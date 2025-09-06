# Real video cut route with FFmpeg and local storage
import os
import subprocess
import tempfile
import logging
import requests
from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.local_storage import local_storage
from config import LOCAL_STORAGE_PATH

v1_video_cut_real_bp = Blueprint('v1_video_cut_real', __name__)
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

def cut_video_with_ffmpeg(input_path: str, output_path: str, start_time: str, end_time: str) -> bool:
    """使用 FFmpeg 剪輯影片"""
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
            except:
                continue
        
        if not ffmpeg_cmd:
            raise ValueError("FFmpeg not found. Please ensure FFmpeg is installed.")
        
        # FFmpeg 剪輯命令
        cmd = [
            ffmpeg_cmd,
            "-i", input_path,
            "-ss", start_time,
            "-to", end_time,
            "-c", "copy",  # 複製編碼，更快
            "-avoid_negative_ts", "make_zero",
            output_path,
            "-y"  # 覆蓋輸出文件
        ]
        
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        
        # 執行 FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("Video cut successful")
            return True
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error cutting video: {e}")
        return False

@v1_video_cut_real_bp.route('/v1/video/cut', methods=['POST'])
@authenticate
def cut_video_real():
    """真實的影片剪輯功能"""
    logger.info("Real video cut request received")
    
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
            output_filename = f"cut_video_{start_time.replace(':', '')}_to_{end_time.replace(':', '')}.mp4"
            output_path = os.path.join(temp_dir, output_filename)
            
            # 使用 FFmpeg 剪輯
            success = cut_video_with_ffmpeg(input_video, output_path, start_time, end_time)
            
            if success and os.path.exists(output_path):
                # 保存到本地存儲
                saved_path = local_storage.save_file(output_path, 'videos')
                file_url = local_storage.get_file_url(saved_path)
                
                result = {
                    "message": "Video cut completed successfully",
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
                }
                
                return jsonify(result), 200
            else:
                return jsonify({
                    "message": "Video cut failed",
                    "status": "error",
                    "note": "Check if FFmpeg is properly installed"
                }), 500
        
    except Exception as e:
        logger.error(f"Error in video cut - {str(e)}")
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": "error"
        }), 500
