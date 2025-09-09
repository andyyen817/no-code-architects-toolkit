#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vidspark存儲文件訪問路由
解決GenHuman API無法訪問上傳文件的404錯誤問題

根據genhuman开发错误.md中的成功案例創建
"""

from flask import Blueprint, send_file, jsonify, abort
import os
import logging
import mimetypes
from werkzeug.utils import safe_join

# 創建存儲訪問藍圖
vidspark_storage_bp = Blueprint('vidspark_storage', __name__)
logger = logging.getLogger(__name__)

@vidspark_storage_bp.route('/vidspark/storage/<path:file_path>')
def serve_storage_file(file_path):
    """
    提供vidspark存儲文件的外部訪問
    
    重要：確保GenHuman API能夠訪問上傳的文件
    
    URL格式: https://domain.com/vidspark/storage/video/2025/09/filename.mp4
    本地路徑: ./output/vidspark/storage/video/2025/09/filename.mp4
    
    Args:
        file_path: 文件相對路徑，如 video/2025/09/filename.mp4
        
    Returns:
        文件內容或404錯誤
    """
    try:
        # 構建安全的文件路徑
        output_dir = os.path.join(os.getcwd(), 'output')
        vidspark_storage_dir = os.path.join(output_dir, 'vidspark', 'storage')
        
        # 使用safe_join防止路徑遍歷攻擊
        full_file_path = safe_join(vidspark_storage_dir, file_path)
        
        if not full_file_path:
            logger.warning(f"Invalid file path: {file_path}")
            return jsonify({"error": "Invalid file path"}), 400
        
        # 檢查文件是否存在
        if not os.path.exists(full_file_path):
            logger.warning(f"File not found: {full_file_path}")
            return jsonify({
                "error": "File not found",
                "path": file_path,
                "full_path": full_file_path
            }), 404
        
        # 獲取MIME類型
        mime_type, _ = mimetypes.guess_type(full_file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        logger.info(f"✅ Serving vidspark storage file: {file_path}")
        logger.info(f"📁 Full path: {full_file_path}")
        logger.info(f"📊 MIME type: {mime_type}")
        logger.info(f"📦 File size: {os.path.getsize(full_file_path)} bytes")
        
        # 返回文件，設置正確的CORS頭
        response = send_file(
            full_file_path,
            mimetype=mime_type,
            as_attachment=False
        )
        
        # 🚨 關鍵：設置CORS頭，允許GenHuman API訪問
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Cache-Control'] = 'public, max-age=86400'
        
        return response
        
    except Exception as e:
        error_msg = f"Error serving storage file: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500

@vidspark_storage_bp.route('/vidspark/files/<path:file_path>')
def serve_files_alias(file_path):
    """
    提供 /vidspark/files/ 路徑的別名支持
    
    某些情況下文件URL可能使用 files 而不是 storage
    """
    return serve_storage_file(file_path)

@vidspark_storage_bp.route('/vidspark/storage/health')
def storage_health():
    """
    存儲系統健康檢查
    """
    try:
        output_dir = os.path.join(os.getcwd(), 'output')
        vidspark_storage_dir = os.path.join(output_dir, 'vidspark', 'storage')
        
        # 檢查存儲目錄是否存在
        storage_exists = os.path.exists(vidspark_storage_dir)
        
        # 如果不存在，創建目錄
        if not storage_exists:
            os.makedirs(vidspark_storage_dir, exist_ok=True)
            logger.info(f"Created vidspark storage directory: {vidspark_storage_dir}")
        
        # 檢查目錄結構
        subdirs = ['video', 'audio', 'images']
        for subdir in subdirs:
            subdir_path = os.path.join(vidspark_storage_dir, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path, exist_ok=True)
                logger.info(f"Created subdirectory: {subdir_path}")
        
        return jsonify({
            "status": "healthy",
            "storage_directory": vidspark_storage_dir,
            "storage_exists": True,
            "subdirectories": subdirs,
            "message": "Vidspark storage system is ready"
        }), 200
        
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
