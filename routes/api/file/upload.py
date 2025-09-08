#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件上傳API端點
為NCA測試中心提供文件上傳功能
"""

from flask import Blueprint, request, jsonify
import logging
import os
import tempfile
import uuid
import base64
from datetime import datetime

# 創建文件上傳藍圖
api_file_upload_bp = Blueprint('api_file_upload', __name__)
logger = logging.getLogger(__name__)

@api_file_upload_bp.route('/api/file/upload', methods=['POST'])
def upload_file():
    """
    文件上傳端點
    
    支持兩種上傳方式：
    1. FormData文件上傳
    2. Base64編碼文件上傳
    
    Returns:
        JSON響應包含文件URL和相關信息
    """
    try:
        # 檢查是否是FormData上傳
        if 'file' in request.files:
            return _handle_formdata_upload()
        
        # 檢查是否是JSON/Base64上傳
        elif request.is_json:
            return _handle_base64_upload()
        
        else:
            return jsonify({
                "error": "沒有找到文件數據。請使用FormData或Base64格式上傳"
            }), 400
            
    except Exception as e:
        error_msg = f"文件上傳失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500

def _handle_formdata_upload():
    """處理FormData格式的文件上傳"""
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "沒有選擇文件"}), 400
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1].lower()
    safe_filename = f"{file_id}{file_extension}"
    
    # 確保輸出目錄存在
    output_dir = os.path.join(os.getcwd(), 'output', 'uploads')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(output_dir, safe_filename)
    file.save(file_path)
    
    # 獲取文件信息
    file_size = os.path.getsize(file_path)
    file_type = _get_file_type(file_extension)
    
    logger.info(f"FormData文件上傳成功: {original_filename} -> {safe_filename} ({file_size} bytes)")
    
    return jsonify({
        "status": "success",
        "file_id": file_id,
        "original_filename": original_filename,
        "filename": safe_filename,
        "file_path": file_path,
        "file_url": f"/uploads/{safe_filename}",
        "file_size": file_size,
        "file_type": file_type,
        "upload_time": datetime.now().isoformat(),
        "upload_method": "formdata"
    }), 200

def _handle_base64_upload():
    """處理Base64格式的文件上傳"""
    data = request.get_json()
    
    if not data or 'file_data' not in data:
        return jsonify({"error": "Base64文件數據缺失"}), 400
    
    file_data = data['file_data']
    filename = data.get('filename', 'uploaded_file')
    
    # 解析Base64數據
    if ',' in file_data:
        # 移除data:type;base64,前綴
        header, base64_data = file_data.split(',', 1)
        
        # 從header中提取文件類型
        if 'data:' in header and ';base64' in header:
            mime_type = header.replace('data:', '').replace(';base64', '')
            file_extension = _get_extension_from_mime_type(mime_type)
        else:
            file_extension = os.path.splitext(filename)[1].lower() or '.bin'
    else:
        base64_data = file_data
        file_extension = os.path.splitext(filename)[1].lower() or '.bin'
    
    try:
        # 解碼Base64數據
        file_bytes = base64.b64decode(base64_data)
    except Exception as e:
        return jsonify({"error": f"Base64解碼失敗: {str(e)}"}), 400
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{file_extension}"
    
    # 確保輸出目錄存在
    output_dir = os.path.join(os.getcwd(), 'output', 'uploads')
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(output_dir, safe_filename)
    with open(file_path, 'wb') as f:
        f.write(file_bytes)
    
    # 獲取文件信息
    file_size = len(file_bytes)
    file_type = _get_file_type(file_extension)
    
    logger.info(f"Base64文件上傳成功: {filename} -> {safe_filename} ({file_size} bytes)")
    
    return jsonify({
        "status": "success",
        "file_id": file_id,
        "original_filename": filename,
        "filename": safe_filename,
        "file_path": file_path,
        "file_url": f"/uploads/{safe_filename}",
        "file_size": file_size,
        "file_type": file_type,
        "upload_time": datetime.now().isoformat(),
        "upload_method": "base64"
    }), 200

def _get_file_type(file_extension):
    """根據文件擴展名確定文件類型"""
    audio_extensions = ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a']
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv']
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    if file_extension in audio_extensions:
        return 'audio'
    elif file_extension in video_extensions:
        return 'video'
    elif file_extension in image_extensions:
        return 'image'
    else:
        return 'other'

def _get_extension_from_mime_type(mime_type):
    """根據MIME類型返回文件擴展名"""
    mime_map = {
        'audio/mp3': '.mp3',
        'audio/mpeg': '.mp3',
        'audio/wav': '.wav',
        'audio/wave': '.wav',
        'audio/aac': '.aac',
        'audio/flac': '.flac',
        'audio/ogg': '.ogg',
        'audio/mp4': '.m4a',
        'video/mp4': '.mp4',
        'video/avi': '.avi',
        'video/quicktime': '.mov',
        'video/webm': '.webm',
        'video/x-msvideo': '.avi',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/bmp': '.bmp',
        'image/webp': '.webp',
        'application/octet-stream': '.bin'
    }
    return mime_map.get(mime_type, '.bin')

