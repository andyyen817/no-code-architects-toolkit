#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據庫管理端點
提供數據庫連接測試、API日誌查詢等功能
"""

from flask import Blueprint, jsonify, request
import logging
from functools import wraps
import os
from flask import request, jsonify

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

# 創建數據庫管理藍圖
v1_database_manage_bp = Blueprint('v1_database_manage', __name__)
logger = logging.getLogger(__name__)

@v1_database_manage_bp.route('/v1/database/test', methods=['GET'])
@authenticate
def test_database():
    """測試數據庫連接"""
    try:
        from services.database_logger import database_logger
        
        result = database_logger.test_database_connection()
        
        if result['status'] == 'success':
            return jsonify({
                "message": "數據庫連接測試成功",
                "status": "success",
                "database_info": result['config']
            }), 200
        else:
            return jsonify({
                "message": result['message'],
                "status": result['status'],
                "available": result['available']
            }), 400
            
    except Exception as e:
        error_msg = f"數據庫測試失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "message": error_msg,
            "status": "error"
        }), 500

@v1_database_manage_bp.route('/v1/database/logs', methods=['GET'])
@authenticate
def get_api_logs():
    """獲取API調用日誌"""
    try:
        from services.database_logger import database_logger
        
        # 獲取查詢參數
        limit = request.args.get('limit', 50, type=int)
        if limit > 200:  # 限制最大查詢數量
            limit = 200
        
        logs = database_logger.get_recent_logs(limit)
        
        return jsonify({
            "message": f"成功獲取 {len(logs)} 條API調用記錄",
            "status": "success",
            "count": len(logs),
            "logs": logs
        }), 200
        
    except Exception as e:
        error_msg = f"獲取API日誌失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "message": error_msg,
            "status": "error"
        }), 500

@v1_database_manage_bp.route('/v1/database/init', methods=['POST'])
@authenticate
def init_database():
    """初始化數據庫表"""
    try:
        from services.database_logger import database_logger
        
        success = database_logger.create_table_if_not_exists()
        
        if success:
            return jsonify({
                "message": "數據庫表初始化成功",
                "status": "success",
                "table_created": True
            }), 200
        else:
            return jsonify({
                "message": "數據庫表初始化失敗",
                "status": "error",
                "table_created": False
            }), 400
            
    except Exception as e:
        error_msg = f"數據庫初始化失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "message": error_msg,
            "status": "error"
        }), 500

@v1_database_manage_bp.route('/v1/database/stats', methods=['GET'])
@authenticate
def get_database_stats():
    """獲取數據庫統計信息"""
    try:
        from services.database_logger import database_logger
        
        # 測試連接
        connection_test = database_logger.test_database_connection()
        
        if not connection_test['available']:
            return jsonify({
                "message": "數據庫不可用",
                "status": "error",
                "available": False
            }), 400
        
        # 獲取最近的日誌統計
        recent_logs = database_logger.get_recent_logs(100)
        
        # 計算統計信息
        total_calls = len(recent_logs)
        success_calls = len([log for log in recent_logs if log.get('response_status', 0) < 400])
        error_calls = total_calls - success_calls
        
        endpoints = {}
        for log in recent_logs:
            endpoint = log.get('endpoint', 'unknown')
            if endpoint not in endpoints:
                endpoints[endpoint] = 0
            endpoints[endpoint] += 1
        
        return jsonify({
            "message": "數據庫統計信息獲取成功",
            "status": "success",
            "stats": {
                "total_api_calls": total_calls,
                "success_calls": success_calls,
                "error_calls": error_calls,
                "success_rate": round(success_calls / total_calls * 100, 2) if total_calls > 0 else 0,
                "top_endpoints": dict(sorted(endpoints.items(), key=lambda x: x[1], reverse=True)[:10])
            },
            "database_info": connection_test['config']
        }), 200
        
    except Exception as e:
        error_msg = f"獲取數據庫統計失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "message": error_msg,
            "status": "error"
        }), 500



