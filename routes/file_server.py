# File server for serving local output files
import os
import logging
from flask import Blueprint, send_file, jsonify
from werkzeug.utils import safe_join

file_server_bp = Blueprint('file_server', __name__)
logger = logging.getLogger(__name__)

@file_server_bp.route('/output/<path:filename>')
def serve_output_file(filename):
    """提供輸出文件的訪問"""
    try:
        # 安全地構建文件路徑
        output_dir = os.path.join(os.getcwd(), 'output')
        file_path = safe_join(output_dir, filename)
        
        if file_path and os.path.exists(file_path):
            logger.info(f"Serving file: {file_path}")
            return send_file(file_path)
        else:
            logger.warning(f"File not found: {filename}")
            return jsonify({"error": "File not found"}), 404
            
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return jsonify({"error": str(e)}), 500

@file_server_bp.route('/output/')
@file_server_bp.route('/files/')
def list_output_files():
    """列出所有輸出文件"""
    try:
        from services.local_storage import local_storage
        files = local_storage.list_files()
        
        return jsonify({
            "message": "Output files list",
            "files": files,
            "count": len(files)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({"error": str(e)}), 500



