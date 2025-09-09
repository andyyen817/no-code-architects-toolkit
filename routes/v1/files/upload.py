#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件上傳端點 - 為NCA測試中心提供文件上傳功能
保存到本地存儲並記錄到Zeabur MySQL數據庫
"""

from flask import Blueprint, request, jsonify
import logging
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from auth.auth import authenticate

# 創建文件上傳藍圖
v1_files_upload_bp = Blueprint('v1_files_upload', __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    'audio': {'mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a', 'wma'},
    'video': {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm'}
}

def allowed_file(filename, file_type):
    """檢查文件類型是否允許"""
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS.get(file_type, set())

def get_file_size_mb(size_bytes):
    """轉換文件大小為MB"""
    return round(size_bytes / 1024 / 1024, 2)

@v1_files_upload_bp.route('/v1/files/upload/audio', methods=['POST'])
@authenticate
def upload_audio():
    """音頻文件上傳"""
    return handle_file_upload('audio')

@v1_files_upload_bp.route('/v1/files/upload/video', methods=['POST'])
@authenticate
def upload_video():
    """視頻文件上傳"""
    return handle_file_upload('video')

def handle_file_upload(file_type):
    """通用文件上傳處理"""
    try:
        # 檢查文件
        if 'file' not in request.files:
            return jsonify({
                "message": "沒有文件被上傳",
                "status": "error"
            }), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "message": "沒有選擇文件",
                "status": "error"
            }), 400

        # 檢查文件類型
        if not allowed_file(file.filename, file_type):
            return jsonify({
                "message": f"不支持的{file_type}文件格式。支持的格式: {', '.join(ALLOWED_EXTENSIONS[file_type])}",
                "status": "error"
            }), 400

        # 生成安全的文件名
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1].lower()
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{file_extension}"
        
        # 創建存儲目錄（按日期分類）
        current_date = datetime.now()
        year_month = current_date.strftime("%Y/%m")
        storage_dir = os.path.join(os.getcwd(), 'output', 'nca', file_type, year_month)
        os.makedirs(storage_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(storage_dir, safe_filename)
        file.save(file_path)
        
        # 獲取文件信息
        file_size = os.path.getsize(file_path)
        file_size_mb = get_file_size_mb(file_size)
        
        # 生成文件URL（外部可訪問）
        file_url = f"https://vidsparkback.zeabur.app/nca/files/{file_type}/{year_month}/{safe_filename}"
        
        # 保存到數據庫
        file_record = {
            'file_id': file_id,
            'original_filename': original_filename,
            'safe_filename': safe_filename,
            'file_type': file_type,
            'file_size': file_size,
            'file_path': file_path,
            'file_url': file_url,
            'upload_time': current_date
        }
        
        # 記錄到數據庫
        from services.database_logger import database_logger
        database_logger.log_file_upload(file_record)
        
        logger.info(f"{file_type.capitalize()}文件上傳成功: {original_filename} -> {safe_filename} ({file_size_mb}MB)")
        
        return jsonify({
            "message": f"{file_type.capitalize()}文件上傳成功",
            "status": "success",
            "file_id": file_id,
            "original_filename": original_filename,
            "file_url": file_url,
            "file_size": file_size,
            "file_size_mb": file_size_mb,
            "file_type": file_type,
            "upload_time": current_date.isoformat()
        }), 200
        
    except Exception as e:
        error_msg = f"{file_type.capitalize()}文件上傳失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "message": error_msg,
            "status": "error"
        }), 500

@v1_files_upload_bp.route('/v1/files/list', methods=['GET'])
@authenticate
def list_uploaded_files():
    """獲取上傳文件列表"""
    try:
        from services.database_logger import database_logger
        
        # 獲取查詢參數
        limit = request.args.get('limit', 20, type=int)
        file_type = request.args.get('type', None)  # 可選：audio 或 video
        
        if limit > 100:  # 限制最大查詢數量
            limit = 100
        
        files = database_logger.get_uploaded_files(limit, file_type)
        
        return jsonify({
            "message": f"成功獲取 {len(files)} 個文件記錄",
            "status": "success",
            "count": len(files),
            "files": files
        }), 200
        
    except Exception as e:
        error_msg = f"獲取文件列表失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "message": error_msg,
            "status": "error"
        }), 500