# Real video trim route with FFmpeg and local storage
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

v1_video_trim_real_bp = Blueprint('v1_video_trim_real', __name__)
logger = logging.getLogger(__name__)

def download_video(url: str, temp_dir: str) -> str:
    """下載影片到臨時目錄"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 生成臨時文件名
        temp_filename = os.path.join(temp_dir, "input_video.mp4")
        
        with open(temp_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Video downloaded: {temp_filename}")
        return temp_filename
        
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise

def trim_video_with_ffmpeg(input_path: str, output_path: str, start_time: str, end_time: str) -> bool:
    """使用 FFmpeg 修剪影片"""
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

        # FFmpeg 修剪命令
        command = [
            ffmpeg_cmd,
            "-i", input_path,
            "-ss", start_time,
            "-to", end_time,
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            output_path,
            "-y"
        ]
        
        logger.info(f"Running FFmpeg command: {' '.join(command)}")
        subprocess.run(command, check=True)
        logger.info(f"Video trimmed successfully: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg command failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Error trimming video: {e}")
        return False

@v1_video_trim_real_bp.route('/v1/video/trim', methods=['POST'])
@authenticate
def trim_video_real():
    """Real video trim endpoint using FFmpeg and local storage"""
    logger.info("Real video trim request received")
    
    try:
        data = request.get_json() or {}
        video_url = data.get('video_url', '')
        start_time = data.get('start_time', '00:00:00')
        end_time = data.get('end_time', '00:00:10')

        if not video_url:
            return jsonify({
                "message": "video_url is required",
                "status": "error"
            }), 400

        # 創建臨時目錄
        with tempfile.TemporaryDirectory() as temp_dir:
            # 下載影片
            input_video = download_video(video_url, temp_dir)
            
            # 準備輸出文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"trimmed_video_{timestamp}.mp4"
            output_path = os.path.join(temp_dir, output_filename)
            
            # 執行修剪
            if trim_video_with_ffmpeg(input_video, output_path, start_time, end_time):
                # 保存到本地存儲
                saved_path = local_storage.save_file(output_path, 'videos')
                file_url = local_storage.get_file_url(saved_path)
                
                logger.info(f"Video trimmed and saved: {saved_path}")
                
                return jsonify({
                    "message": "Video trim completed successfully",
                    "status": "completed",
                    "input": {
                        "video_url": video_url,
                        "start_time": start_time,
                        "end_time": end_time
                    },
                    "output": {
                        "file_path": saved_path,
                        "file_url": file_url,
                        "filename": os.path.basename(saved_path)
                    }
                }), 200
            else:
                return jsonify({
                    "message": "Video trim failed: FFmpeg not found",
                    "note": "Check if FFmpeg is properly installed",
                    "status": "error"
                }), 500

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during video download: {e}")
        return jsonify({
            "message": f"Network error downloading video: {e}",
            "status": "error"
        }), 500
    except Exception as e:
        logger.error(f"Error processing video trim: {e}")
        return jsonify({
            "message": f"Video trim failed: {e}",
            "status": "error"
        }), 500
