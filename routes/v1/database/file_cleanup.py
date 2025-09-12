#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據庫文件記錄清理工具
解決數據庫記錄與物理文件不匹配的問題
"""

import os
import logging
from flask import Blueprint, jsonify, request
from routes.authenticate import auth_bp
from functools import wraps
import os

# 創建認證裝飾器
def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_api_key = os.environ.get('API_KEY')
        if api_key == expected_api_key:
            return f(*args, **kwargs)
        else:
            return jsonify({"message": "Unauthorized", "status": "error"}), 401
    return decorated_function

from services.database_logger import database_logger

# 創建文件清理藍圖
v1_database_file_cleanup_bp = Blueprint('v1_database_file_cleanup', __name__)
logger = logging.getLogger(__name__)

@v1_database_file_cleanup_bp.route('/v1/database/file-cleanup/check', methods=['GET'])
@authenticate
def check_file_records():
    """檢查數據庫文件記錄與物理文件的對應關係"""
    try:
        # 檢查數據庫連接
        connection_test = database_logger.test_database_connection()
        if not connection_test['available']:
            return jsonify({
                "message": "數據庫不可用，無法檢查文件記錄",
                "status": "error",
                "available": False
            }), 400
        
        # 獲取所有上傳文件記錄
        uploaded_files = database_logger.get_uploaded_files(limit=1000)
        output_files = database_logger.get_output_files(limit=1000)
        
        # 檢查結果統計
        check_results = {
            "uploaded_files": {
                "total": len(uploaded_files),
                "valid": 0,
                "invalid": 0,
                "invalid_records": []
            },
            "output_files": {
                "total": len(output_files),
                "valid": 0,
                "invalid": 0,
                "invalid_records": []
            }
        }
        
        # 檢查上傳文件
        for file_record in uploaded_files:
            file_path = file_record.get('file_path', '')
            if file_path and os.path.exists(file_path):
                check_results["uploaded_files"]["valid"] += 1
            else:
                check_results["uploaded_files"]["invalid"] += 1
                check_results["uploaded_files"]["invalid_records"].append({
                    "file_id": file_record.get('file_id'),
                    "filename": file_record.get('original_filename'),
                    "file_path": file_path,
                    "file_url": file_record.get('file_url'),
                    "upload_time": str(file_record.get('upload_time', ''))
                })
        
        # 檢查輸出文件
        for file_record in output_files:
            file_path = file_record.get('file_path', '')
            if file_path and os.path.exists(file_path):
                check_results["output_files"]["valid"] += 1
            else:
                check_results["output_files"]["invalid"] += 1
                check_results["output_files"]["invalid_records"].append({
                    "file_id": file_record.get('file_id'),
                    "filename": file_record.get('original_filename'),
                    "file_path": file_path,
                    "file_url": file_record.get('file_url'),
                    "operation_type": file_record.get('operation_type'),
                    "created_at": str(file_record.get('created_at', ''))
                })
        
        return jsonify({
            "message": "文件記錄檢查完成",
            "status": "success",
            "check_results": check_results
        }), 200
        
    except Exception as e:
        error_msg = f"文件記錄檢查失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "message": error_msg,
            "status": "error"
        }), 500

@v1_database_file_cleanup_bp.route('/v1/database/file-cleanup/cleanup', methods=['POST'])
@authenticate
def cleanup_invalid_records():
    """清理無效的文件記錄"""
    try:
        data = request.get_json() or {}
        dry_run = data.get('dry_run', True)  # 默認為試運行模式
        
        # 檢查數據庫連接
        connection_test = database_logger.test_database_connection()
        if not connection_test['available']:
            return jsonify({
                "message": "數據庫不可用，無法清理文件記錄",
                "status": "error",
                "available": False
            }), 400
        
        cleanup_results = {
            "dry_run": dry_run,
            "uploaded_files_deleted": 0,
            "output_files_deleted": 0,
            "deleted_records": []
        }
        
        if not dry_run:
            # 實際清理模式
            connection = database_logger.get_connection()
            if not connection:
                return jsonify({
                    "message": "無法獲取數據庫連接",
                    "status": "error"
                }), 500
            
            try:
                with connection.cursor() as cursor:
                    # 清理上傳文件表中的無效記錄
                    uploaded_files = database_logger.get_uploaded_files(limit=1000)
                    for file_record in uploaded_files:
                        file_path = file_record.get('file_path', '')
                        if not file_path or not os.path.exists(file_path):
                            delete_sql = "DELETE FROM `nca_uploaded_files` WHERE `file_id` = %s"
                            cursor.execute(delete_sql, (file_record.get('file_id'),))
                            cleanup_results["uploaded_files_deleted"] += 1
                            cleanup_results["deleted_records"].append({
                                "table": "nca_uploaded_files",
                                "file_id": file_record.get('file_id'),
                                "filename": file_record.get('original_filename')
                            })
                    
                    # 清理輸出文件表中的無效記錄
                    output_files = database_logger.get_output_files(limit=1000)
                    for file_record in output_files:
                        file_path = file_record.get('file_path', '')
                        if not file_path or not os.path.exists(file_path):
                            delete_sql = "DELETE FROM `nca_output_files` WHERE `file_id` = %s"
                            cursor.execute(delete_sql, (file_record.get('file_id'),))
                            cleanup_results["output_files_deleted"] += 1
                            cleanup_results["deleted_records"].append({
                                "table": "nca_output_files",
                                "file_id": file_record.get('file_id'),
                                "filename": file_record.get('original_filename')
                            })
                    
                    connection.commit()
                    logger.info(f"清理完成：刪除了 {cleanup_results['uploaded_files_deleted']} 個上傳文件記錄，{cleanup_results['output_files_deleted']} 個輸出文件記錄")
                    
            finally:
                connection.close()
        else:
            # 試運行模式，只統計不實際刪除
            uploaded_files = database_logger.get_uploaded_files(limit=1000)
            for file_record in uploaded_files:
                file_path = file_record.get('file_path', '')
                if not file_path or not os.path.exists(file_path):
                    cleanup_results["uploaded_files_deleted"] += 1
                    cleanup_results["deleted_records"].append({
                        "table": "nca_uploaded_files",
                        "file_id": file_record.get('file_id'),
                        "filename": file_record.get('original_filename')
                    })
            
            output_files = database_logger.get_output_files(limit=1000)
            for file_record in output_files:
                file_path = file_record.get('file_path', '')
                if not file_path or not os.path.exists(file_path):
                    cleanup_results["output_files_deleted"] += 1
                    cleanup_results["deleted_records"].append({
                        "table": "nca_output_files",
                        "file_id": file_record.get('file_id'),
                        "filename": file_record.get('original_filename')
                    })
        
        return jsonify({
            "message": f"文件記錄清理{'模擬' if dry_run else '實際'}完成",
            "status": "success",
            "cleanup_results": cleanup_results
        }), 200
        
    except Exception as e:
        error_msg = f"文件記錄清理失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "message": error_msg,
            "status": "error"
        }), 500

@v1_database_file_cleanup_bp.route('/v1/database/file-cleanup/stats', methods=['GET'])
@authenticate
def get_file_stats():
    """獲取文件記錄統計信息"""
    try:
        # 檢查數據庫連接
        connection_test = database_logger.test_database_connection()
        if not connection_test['available']:
            return jsonify({
                "message": "數據庫不可用，無法獲取文件統計",
                "status": "error",
                "available": False
            }), 400
        
        # 獲取文件記錄
        uploaded_files = database_logger.get_uploaded_files(limit=1000)
        output_files = database_logger.get_output_files(limit=1000)
        
        # 統計信息
        stats = {
            "uploaded_files": {
                "total": len(uploaded_files),
                "by_type": {},
                "recent_uploads": []
            },
            "output_files": {
                "total": len(output_files),
                "by_type": {},
                "by_operation": {},
                "recent_outputs": []
            }
        }
        
        # 統計上傳文件
        for file_record in uploaded_files:
            file_type = file_record.get('file_type', 'unknown')
            stats["uploaded_files"]["by_type"][file_type] = stats["uploaded_files"]["by_type"].get(file_type, 0) + 1
        
        # 最近的上傳文件（前5個）
        stats["uploaded_files"]["recent_uploads"] = [
            {
                "filename": f.get('original_filename'),
                "file_type": f.get('file_type'),
                "upload_time": str(f.get('upload_time', '')),
                "file_size": f.get('file_size')
            }
            for f in uploaded_files[:5]
        ]
        
        # 統計輸出文件
        for file_record in output_files:
            file_type = file_record.get('file_type', 'unknown')
            operation_type = file_record.get('operation_type', 'unknown')
            
            stats["output_files"]["by_type"][file_type] = stats["output_files"]["by_type"].get(file_type, 0) + 1
            stats["output_files"]["by_operation"][operation_type] = stats["output_files"]["by_operation"].get(operation_type, 0) + 1
        
        # 最近的輸出文件（前5個）
        stats["output_files"]["recent_outputs"] = [
            {
                "filename": f.get('original_filename'),
                "file_type": f.get('file_type'),
                "operation_type": f.get('operation_type'),
                "created_at": str(f.get('created_at', '')),
                "file_size": f.get('file_size')
            }
            for f in output_files[:5]
        ]
        
        return jsonify({
            "message": "文件統計信息獲取成功",
            "status": "success",
            "stats": stats
        }), 200
        
    except Exception as e:
        error_msg = f"獲取文件統計失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "message": error_msg,
            "status": "error"
        }), 500