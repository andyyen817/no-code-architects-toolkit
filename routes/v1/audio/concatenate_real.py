# Real audio concatenate route with FFmpeg and local storage
import os
import subprocess
import tempfile
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.output_file_manager import output_file_manager
from config import LOCAL_STORAGE_PATH

v1_audio_concatenate_real_bp = Blueprint('v1_audio_concatenate_real', __name__)
logger = logging.getLogger(__name__)

def download_audio(url: str, temp_dir: str, index: int) -> str:
    """下載音頻到臨時目錄"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 根據 URL 推斷檔案副檔名
        if url.lower().endswith(('.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a')):
            ext = url.split('.')[-1].lower()
        else:
            ext = 'mp3'  # 預設副檔名
        
        temp_filename = os.path.join(temp_dir, f"audio_{index}.{ext}")
        
        with open(temp_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Audio downloaded: {temp_filename}")
        return temp_filename
        
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        raise

def concatenate_audio_with_ffmpeg(input_files: list, output_path: str) -> bool:
    """使用 FFmpeg 合併音頻，支援混合格式"""
    try:
        # 檢查 FFmpeg 是否可用
        ffmpeg_paths = [
            "ffmpeg",  # 系統 PATH
            r"D:\no-code-architects-toolkit\ffmpeg-binary\bin\ffmpeg.exe",  # 正確的 FFmpeg 位置
            os.path.join(os.path.dirname(os.getcwd()), "ffmpeg-binary", "bin", "ffmpeg.exe")
        ]
        
        ffmpeg_cmd = None
        for path in ffmpeg_paths:
            try:
                result = subprocess.run([path, "-version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    ffmpeg_cmd = path
                    break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        if not ffmpeg_cmd:
            logger.error("FFmpeg not found. Please ensure FFmpeg is installed.")
            return False

        # 使用 filter_complex 來支援混合格式，避免 concat 協議的限制
        # 建構輸入和濾鏡
        input_args = []
        filter_inputs = []
        
        for i, input_file in enumerate(input_files):
            input_args.extend(["-i", input_file])
            filter_inputs.append(f"[{i}:0]")
        
        # 建構 filter_complex 字符串，添加音量正規化
        # 修復：調整I參數從-16到-14，與上傳功能保持一致，提高整體音量
        filter_complex = "".join(filter_inputs) + f"concat=n={len(input_files)}:v=0:a=1[concat];[concat]loudnorm=I=-14:TP=-1.5:LRA=11[out]"
        
        # FFmpeg 音頻合併命令（使用 filter_complex 支援混合格式並進行音量正規化）
        command = [
            ffmpeg_cmd
        ] + input_args + [
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            "-ar", "44100",
            output_path,
            "-y"
        ]
        
        logger.info(f"Running FFmpeg command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Audio concatenated successfully: {output_path}")
            return True
        else:
            logger.error(f"FFmpeg command failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error concatenating audio: {e}")
        return False

@v1_audio_concatenate_real_bp.route('/v1/audio/concatenate', methods=['POST'])
@authenticate
def concatenate_audio_real():
    """Real audio concatenate endpoint using FFmpeg and local storage"""
    logger.info("Real audio concatenate request received")
    
    try:
        data = request.get_json() or {}
        audio_urls = data.get('audio_urls', [])

        if len(audio_urls) < 2:
            return jsonify({
                "message": "At least 2 audio URLs are required",
                "status": "error"
            }), 400

        # 創建臨時目錄
        with tempfile.TemporaryDirectory() as temp_dir:
            # 下載所有音頻檔案
            input_files = []
            for i, url in enumerate(audio_urls):
                try:
                    input_file = download_audio(url, temp_dir, i)
                    input_files.append(input_file)
                except Exception as e:
                    return jsonify({
                        "message": f"Failed to download audio {i+1}: {e}",
                        "status": "error"
                    }), 400
            
            # 準備輸出檔案
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"concatenated_audio_{timestamp}.mp3"
            output_path = os.path.join(temp_dir, output_filename)
            
            # 執行音頻合併
            if concatenate_audio_with_ffmpeg(input_files, output_path):
                # 使用統一的輸出文件管理器保存到MySQL數據庫
                file_info = output_file_manager.save_output_file(
                    source_file_path=output_path,
                    file_type='audio',
                    operation='concatenate',
                    original_filename=f"audio_merge_{len(audio_urls)}_files",
                    metadata={
                        'audio_urls': audio_urls,
                        'total_files': len(audio_urls)
                    }
                )
                
                logger.info(f"Audio concatenated and saved: {file_info['file_path']}")
                
                return jsonify({
                    "message": "Audio concatenation completed successfully",
                    "status": "completed",
                    "input": {
                        "audio_urls": audio_urls,
                        "total_files": len(audio_urls)
                    },
                    "output": {
                        "file_path": file_info['file_path'],
                        "file_url": file_info['file_url'],
                        "filename": file_info['filename']
                    }
                }), 200
            else:
                return jsonify({
                    "message": "Audio concatenation failed: FFmpeg not found",
                    "note": "Check if FFmpeg is properly installed",
                    "status": "error"
                }), 500

    except Exception as e:
        logger.error(f"Error processing audio concatenation: {e}")
        return jsonify({
            "message": f"Audio concatenation failed: {e}",
            "status": "error"
        }), 500
