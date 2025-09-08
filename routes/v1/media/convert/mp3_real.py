# Real MP3 convert route with FFmpeg and local storage
import os
import subprocess
import tempfile
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.local_storage import local_storage
from config import LOCAL_STORAGE_PATH

v1_media_convert_mp3_real_bp = Blueprint('v1_media_convert_mp3_real', __name__)
logger = logging.getLogger(__name__)

def download_media(url: str, temp_dir: str) -> str:
    """下載媒體到臨時目錄"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 根據 URL 推斷檔案副檔名
        if '.' in url.split('/')[-1]:
            ext = url.split('.')[-1].lower()[:4]  # 限制副檔名長度
        else:
            ext = 'tmp'
        
        temp_filename = os.path.join(temp_dir, f"input_media.{ext}")
        
        with open(temp_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Media downloaded: {temp_filename}")
        return temp_filename
        
    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        raise

def convert_to_mp3_with_ffmpeg(input_path: str, output_path: str) -> bool:
    """使用 FFmpeg 轉換為 MP3"""
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

        # FFmpeg MP3 轉換命令
        command = [
            ffmpeg_cmd,
            "-i", input_path,
            "-codec:a", "libmp3lame",
            "-b:a", "192k",
            "-ar", "44100",
            output_path,
            "-y"
        ]
        
        logger.info(f"Running FFmpeg command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Media converted to MP3 successfully: {output_path}")
            return True
        else:
            logger.error(f"FFmpeg command failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error converting to MP3: {e}")
        return False

@v1_media_convert_mp3_real_bp.route('/v1/media/convert/mp3', methods=['POST'])
@authenticate
def convert_to_mp3_real():
    """Real MP3 convert endpoint using FFmpeg and local storage"""
    logger.info("Real MP3 convert request received")
    
    try:
        data = request.get_json() or {}
        media_url = data.get('media_url', '')

        if not media_url:
            return jsonify({
                "message": "media_url is required",
                "status": "error"
            }), 400

        # 創建臨時目錄
        with tempfile.TemporaryDirectory() as temp_dir:
            # 下載媒體檔案
            input_file = download_media(media_url, temp_dir)
            
            # 準備輸出檔案
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"converted_audio_{timestamp}.mp3"
            output_path = os.path.join(temp_dir, output_filename)
            
            # 執行 MP3 轉換
            if convert_to_mp3_with_ffmpeg(input_file, output_path):
                # 保存到本地存儲
                saved_path = local_storage.save_file(output_path, 'audio')
                file_url = local_storage.get_file_url(saved_path)
                
                logger.info(f"Media converted to MP3 and saved: {saved_path}")
                
                return jsonify({
                    "message": "MP3 conversion completed successfully",
                    "status": "completed",
                    "input": {
                        "media_url": media_url
                    },
                    "output": {
                        "file_path": saved_path,
                        "file_url": file_url,
                        "filename": os.path.basename(saved_path)
                    }
                }), 200
            else:
                return jsonify({
                    "message": "MP3 conversion failed: FFmpeg not found",
                    "note": "Check if FFmpeg is properly installed",
                    "status": "error"
                }), 500

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during media download: {e}")
        return jsonify({
            "message": f"Network error downloading media: {e}",
            "status": "error"
        }), 500
    except Exception as e:
        logger.error(f"Error processing MP3 conversion: {e}")
        return jsonify({
            "message": f"MP3 conversion failed: {e}",
            "status": "error"
        }), 500



