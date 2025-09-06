# File upload route for local testing
import os
import tempfile
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from services.authentication import authenticate
from services.local_storage import local_storage

v1_toolkit_upload_bp = Blueprint('v1_toolkit_upload', __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    'audio': {'mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a', 'wma'},
    'video': {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm'},
    'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'}
}

def allowed_file(filename):
    """檢查檔案類型是否允許"""
    if '.' not in filename:
        return False, None
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return True, category
    
    return False, None

@v1_toolkit_upload_bp.route('/v1/toolkit/upload', methods=['POST'])
@authenticate
def upload_file():
    """檔案上傳端點"""
    logger.info("File upload request received")
    
    try:
        # 檢查是否有檔案
        if 'file' not in request.files:
            return jsonify({
                "message": "No file provided",
                "status": "error"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "message": "No file selected",
                "status": "error"
            }), 400
        
        # 檢查檔案類型
        is_allowed, category = allowed_file(file.filename)
        if not is_allowed:
            return jsonify({
                "message": f"File type not allowed. Supported types: {', '.join(sum(ALLOWED_EXTENSIONS.values(), set()))}",
                "status": "error"
            }), 400
        
        # 保存檔案到臨時位置
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]  # 包含微秒，避免重複
        safe_filename = f"{timestamp}_{filename}"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{safe_filename}") as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        # 保存到本地存儲
        if category == 'audio':
            storage_category = 'audio'
        elif category == 'video':
            storage_category = 'videos'
        else:
            storage_category = 'images'
        
        saved_path = local_storage.save_file(temp_path, storage_category)
        file_url = local_storage.get_file_url(saved_path)
        
        # 清理臨時檔案
        os.unlink(temp_path)
        
        logger.info(f"File uploaded and saved: {saved_path}")
        
        return jsonify({
            "message": "File uploaded successfully",
            "status": "completed",
            "file_path": saved_path,
            "file_url": file_url,
            "filename": os.path.basename(saved_path),
            "category": category
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        return jsonify({
            "message": f"File upload failed: {e}",
            "status": "error"
        }), 500
