# Real image to video conversion - CPU optimized, no AI required
import os
import subprocess
import tempfile
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.local_storage import local_storage

v1_image_convert_video_real_bp = Blueprint('v1_image_convert_video_real', __name__)
logger = logging.getLogger(__name__)

# Check if Pillow is available
PIL_AVAILABLE = False
try:
    from PIL import Image
    PIL_AVAILABLE = True
    logger.info("PIL/Pillow is available")
except ImportError:
    logger.warning("PIL/Pillow not available, using simulation mode")

def download_image(url: str, temp_dir: str) -> str:
    """Download image file to temporary directory"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file extension
        original_filename = url.split('/')[-1].split('?')[0]
        file_extension = os.path.splitext(original_filename)[1] if '.' in original_filename else '.jpg'
        
        temp_filename = os.path.join(temp_dir, f"input_image{file_extension}")
        
        with open(temp_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Image downloaded: {temp_filename}")
        return temp_filename
        
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {e}")
        raise

def convert_image_to_video_with_ffmpeg(image_path: str, output_path: str, 
                                     length: float = 5.0, frame_rate: int = 30, 
                                     zoom_speed: float = 0.03) -> bool:
    """Convert image to video using FFmpeg with simple zoom effect"""
    try:
        # Get image dimensions using Pillow
        if PIL_AVAILABLE:
            with Image.open(image_path) as img:
                width, height = img.size
            logger.info(f"Original image dimensions: {width}x{height}")
        else:
            # Default dimensions if Pillow not available
            width, height = 1920, 1080
            logger.warning("Using default dimensions (Pillow not available)")
        
        # Check FFmpeg availability
        ffmpeg_paths = [
            "ffmpeg",  # System PATH
            r"D:\no-code-architects-toolkit\ffmpeg-binary\bin\ffmpeg.exe",
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

        # Simplified approach for better compatibility
        if width > height:
            # Landscape - scale to 1080p
            output_width, output_height = 1920, 1080
        else:
            # Portrait - scale to vertical HD
            output_width, output_height = 1080, 1920
        
        # Calculate zoom parameters (simplified)
        zoom_start = 1.0
        zoom_end = 1.0 + (zoom_speed * length)
        
        logger.info(f"Video parameters: {length}s, {frame_rate}fps, zoom: {zoom_start} to {zoom_end}")
        logger.info(f"Output resolution: {output_width}x{output_height}")
        
        # Simplified FFmpeg command - more compatible
        command = [
            ffmpeg_cmd,
            "-loop", "1",
            "-i", image_path,
            "-vf", f"scale={output_width*2}:{output_height*2},zoompan=z='1+({zoom_speed})*on/{int(length*frame_rate)}':d={int(length*frame_rate)}:s={output_width}x{output_height}",
            "-r", str(frame_rate),
            "-c:v", "libx264",
            "-t", str(length),
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            output_path,
            "-y"
        ]
        
        logger.info(f"Running simplified FFmpeg command: {' '.join(command)}")
        
        # Execute FFmpeg with timeout
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info(f"Image to video conversion successful: {output_path}")
            return True
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            
            # Fallback: Try even simpler command without zoom
            logger.info("Trying fallback method without zoom effect...")
            fallback_command = [
                ffmpeg_cmd,
                "-loop", "1",
                "-i", image_path,
                "-vf", f"scale={output_width}:{output_height}",
                "-r", str(frame_rate),
                "-c:v", "libx264",
                "-t", str(length),
                "-pix_fmt", "yuv420p",
                "-preset", "fast",
                output_path,
                "-y"
            ]
            
            logger.info(f"Running fallback command: {' '.join(fallback_command)}")
            fallback_result = subprocess.run(fallback_command, capture_output=True, text=True, timeout=60)
            
            if fallback_result.returncode == 0:
                logger.info(f"Fallback conversion successful: {output_path}")
                return True
            else:
                logger.error(f"Fallback also failed: {fallback_result.stderr}")
                return False
            
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg command timed out")
        return False
    except Exception as e:
        logger.error(f"Error converting image to video: {e}")
        return False

def create_simulation_response(data: dict) -> dict:
    """Create simulation response when dependencies are not available"""
    image_url = data.get('image_url')
    length = data.get('length', 5.0)
    frame_rate = data.get('frame_rate', 30)
    zoom_speed = data.get('zoom_speed', 3.0)

    return {
        "message": "Image to video conversion simulation completed",
        "status": "simulation_mode",
        "note": "This is a simulation. Install Pillow for real functionality: pip install Pillow",
        "input": {
            "image_url": image_url,
            "length": length,
            "frame_rate": frame_rate,
            "zoom_speed": zoom_speed
        },
        "output": {
            "video_url": "http://localhost:8080/output/videos/simulated_image_to_video.mp4",
            "filename": "simulated_image_to_video.mp4",
            "duration": length,
            "resolution": "1920x1080",
            "format": "mp4"
        },
        "requirements": {
            "missing_dependency": "PIL/Pillow",
            "install_command": "pip install Pillow",
            "note": "FFmpeg is also required for video processing"
        }
    }

@v1_image_convert_video_real_bp.route('/v1/image/convert/video', methods=['POST'])
@authenticate
def image_to_video_real():
    """Real image to video conversion - CPU optimized"""
    logger.info("Real image to video conversion request received")
    
    try:
        data = request.get_json() or {}
        image_url = data.get('image_url')
        length = float(data.get('length', 5.0))
        frame_rate = int(data.get('frame_rate', 30))
        zoom_speed = float(data.get('zoom_speed', 3.0)) / 100  # Convert percentage to decimal

        if not image_url:
            return jsonify({"message": "image_url is required"}), 400

        # Validate parameters
        if not (0.1 <= length <= 60):
            return jsonify({"message": "Length must be between 0.1 and 60 seconds"}), 400
        
        if not (15 <= frame_rate <= 60):
            return jsonify({"message": "Frame rate must be between 15 and 60 fps"}), 400
        
        if not (0 <= zoom_speed <= 1):
            return jsonify({"message": "Zoom speed must be between 0 and 100"}), 400

        # If Pillow is not available, return simulation
        if not PIL_AVAILABLE:
            return jsonify(create_simulation_response(data)), 200

        # Real conversion with FFmpeg
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download image file
            logger.info(f"Starting conversion for: {image_url}")
            input_image_path = download_image(image_url, temp_dir)
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"image_to_video_{timestamp}.mp4"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Convert image to video
            start_time = datetime.now()
            success = convert_image_to_video_with_ffmpeg(
                input_image_path, output_path, length, frame_rate, zoom_speed
            )
            process_time = (datetime.now() - start_time).total_seconds()
            
            if not success:
                return jsonify({
                    "message": "Image to video conversion failed",
                    "status": "error",
                    "input": data,
                    "note": "Check FFmpeg installation and image file accessibility"
                }), 500
            
            # Save to local storage
            saved_file_path = local_storage.save_file(output_path, 'videos')
            file_url = local_storage.get_file_url(saved_file_path)
            
            logger.info(f"Image to video conversion completed in {process_time:.2f}s")
            
            return jsonify({
                "message": "Image to video conversion completed successfully",
                "status": "completed",
                "input": {
                    "image_url": image_url,
                    "length": length,
                    "frame_rate": frame_rate,
                    "zoom_speed": zoom_speed * 100  # Convert back to percentage
                },
                "output": {
                    "video_url": file_url,
                    "file_path": saved_file_path,
                    "filename": output_filename,
                    "duration": length,
                    "frame_rate": frame_rate,
                    "format": "mp4"
                },
                "performance": {
                    "processing_time_seconds": process_time,
                    "method": "ffmpeg_zoompan",
                    "device": "cpu"
                }
            }), 200

    except Exception as e:
        logger.error(f"Error in image to video conversion: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            "message": f"Image to video conversion failed: {str(e)}",
            "status": "error",
            "error_type": type(e).__name__,
            "input": data.get('image_url', 'Unknown') if 'data' in locals() else 'Unknown',
            "troubleshooting": {
                "possible_causes": [
                    "Image file too large or invalid format",
                    "FFmpeg not installed or accessible",
                    "Pillow (PIL) not installed",
                    "Network timeout during image download"
                ],
                "solutions": [
                    "Install Pillow: pip install Pillow",
                    "Ensure FFmpeg is properly installed",
                    "Try with a smaller image file",
                    "Check image URL accessibility"
                ]
            },
            "note": "Check server logs for detailed error information"
        }), 500
