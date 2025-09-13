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
from services.authentication import authenticate  # 🚨 修復：使用正確的導入路徑
from services.database_logger import database_logger  # 🚨 新增：導入數據庫記錄器

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
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        storage_dir = os.path.join(os.getcwd(), 'output', 'nca', file_type, year, month)
        os.makedirs(storage_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(storage_dir, safe_filename)
        file.save(file_path)
        
        # 如果是音頻文件，使用FFmpeg進行音量正規化處理
        if file_type == 'audio':
            try:
                import subprocess
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
                
                if ffmpeg_cmd:
                    # 創建臨時文件用於處理
                    temp_path = file_path + ".temp"
                    
                    # 🚨 改進：使用更有效的音量處理策略
                    # 1. 先分析音頻音量
                    analyze_command = [
                        ffmpeg_cmd,
                        "-i", file_path,
                        "-af", "volumedetect",
                        "-f", "null",
                        "-"
                    ]
                    
                    analyze_result = subprocess.run(analyze_command, capture_output=True, text=True)
                    
                    # 2. 根據原始格式選擇合適的編碼器和參數
                    if file_extension.lower() == '.m4a':
                        codec_params = ["-codec:a", "aac", "-b:a", "256k"]
                        output_ext = file_extension
                    elif file_extension.lower() == '.mp3':
                        codec_params = ["-codec:a", "libmp3lame", "-b:a", "192k"]
                        output_ext = file_extension
                    else:
                        # 對於其他格式，轉換為高質量MP3
                        codec_params = ["-codec:a", "libmp3lame", "-b:a", "192k"]
                        output_ext = '.mp3'
                        # 更新文件路徑和文件名
                        new_safe_filename = f"{file_id}{output_ext}"
                        new_file_path = os.path.join(storage_dir, new_safe_filename)
                        temp_path = new_file_path + ".temp"
                    
                    # 3. 使用音量正規化濾鏡，保持較高音量
                    # 修復：調整I參數從-16到-14，提高整體音量
                    audio_filter = "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=summary"
                    
                    # FFmpeg 命令：音量正規化 + 增益處理
                    command = [
                        ffmpeg_cmd,
                        "-i", file_path,
                        "-af", audio_filter,
                    ] + codec_params + [
                        "-ar", "44100",
                        temp_path,
                        "-y"
                    ]
                    
                    result = subprocess.run(command, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # 如果格式改變了，更新相關變量
                        if output_ext != file_extension:
                            # 刪除原文件
                            os.remove(file_path)
                            # 更新文件路徑和名稱
                            file_path = new_file_path
                            safe_filename = new_safe_filename
                            file_extension = output_ext
                        
                        # 替換原文件
                        os.replace(temp_path, file_path)
                        logger.info(f"Audio volume enhanced and normalized: {safe_filename}")
                    else:
                        # 如果處理失敗，刪除臨時文件並保留原文件
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        logger.warning(f"Audio normalization failed for {safe_filename}: {result.stderr}")
                else:
                    logger.warning("FFmpeg not found, skipping audio normalization")
            except Exception as e:
                logger.warning(f"Audio normalization error for {safe_filename}: {e}")
        
        # 獲取文件信息
        file_size = os.path.getsize(file_path)
        file_size_mb = get_file_size_mb(file_size)
        
        # 生成文件URL（外部可訪問）- 使用最終的safe_filename
        final_filename = os.path.basename(file_path)
        file_url = f"https://vidsparkback.zeabur.app/nca/files/{file_type}/{year}/{month}/{final_filename}"
        
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

@v1_files_upload_bp.route('/v1/files/output/list', methods=['GET'])
@authenticate
def get_output_files():
    """
    獲取輸出文件列表
    支持查詢參數：
    - limit: 返回數量限制 (默認50)
    - file_type: 文件類型過濾 (audio/video/image)
    - operation_type: 操作類型過濾 (cut/trim/thumbnail等)
    """
    try:
        # 獲取查詢參數
        limit = request.args.get('limit', 50, type=int)
        file_type = request.args.get('file_type')
        operation_type = request.args.get('operation_type')
        
        # 限制最大返回數量
        limit = min(limit, 100)
        
        # 從數據庫獲取輸出文件列表
        files = database_logger.get_output_files(
            file_type=file_type,
            operation_type=operation_type,
            limit=limit
        )
        
        # 格式化文件信息
        formatted_files = []
        for file_record in files:
            file_info = {
                'file_id': file_record.get('file_id'),
                'filename': file_record.get('safe_filename'),
                'original_filename': file_record.get('original_filename'),
                'file_type': file_record.get('file_type'),
                'file_size': file_record.get('file_size'),
                'file_size_mb': round(file_record.get('file_size', 0) / (1024 * 1024), 2) if file_record.get('file_size') else 0,
                'file_url': file_record.get('file_url'),
                'operation_type': file_record.get('operation_type'),
                'metadata': file_record.get('metadata', {}),
                'created_at': file_record.get('created_at')
            }
            formatted_files.append(file_info)
        
        return jsonify({
            "message": "輸出文件列表獲取成功",
            "status": "success",
            "files": formatted_files,
            "total": len(formatted_files),
            "filters": {
                "file_type": file_type,
                "operation_type": operation_type,
                "limit": limit
            }
        }), 200
        
    except Exception as e:
        error_msg = f"獲取輸出文件列表失敗: {str(e)}"
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