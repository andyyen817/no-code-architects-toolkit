#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存儲管理API端點
提供存儲初始化、監控和維護的HTTP接口

作者：AI助手
創建日期：2025-01-09
目的：為Zeabur持久化存儲提供管理接口
"""

import logging
from datetime import datetime
from flask import Blueprint, jsonify, request
from functools import wraps
import os
import sys

# 添加項目根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from services.storage_manager import storage_manager

logger = logging.getLogger(__name__)

# 創建存儲管理藍圖
storage_management_bp = Blueprint('storage_management', __name__, url_prefix='/api/v1/storage')

def require_auth(f):
    """
    認證裝飾器
    檢查API密鑰或管理員權限
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 檢查API密鑰
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        expected_key = os.environ.get('API_KEY', 'default-api-key')
        
        if api_key != expected_key:
            return jsonify({
                'error': '未授權訪問',
                'message': '需要有效的API密鑰',
                'timestamp': datetime.now().isoformat()
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

@storage_management_bp.route('/initialize', methods=['POST'])
@require_auth
def initialize_storage():
    """
    初始化存儲目錄
    
    POST /api/v1/storage/initialize
    
    Returns:
        JSON: 初始化結果
    """
    try:
        logger.info("📡 收到存儲初始化請求")
        
        # 執行存儲初始化
        result = storage_manager.initialize_storage()
        
        # 添加響應元數據
        response_data = {
            'success': result['success'],
            'message': '存儲初始化完成' if result['success'] else '存儲初始化失敗',
            'timestamp': datetime.now().isoformat(),
            'data': result
        }
        
        status_code = 200 if result['success'] else 500
        
        logger.info(f"✅ 存儲初始化響應: {result['success']}")
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"存儲初始化API異常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服務器內部錯誤',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_management_bp.route('/usage', methods=['GET'])
@require_auth
def get_storage_usage():
    """
    獲取存儲使用情況
    
    GET /api/v1/storage/usage
    
    Returns:
        JSON: 存儲使用統計
    """
    try:
        logger.info("📊 收到存儲使用情況查詢請求")
        
        # 獲取存儲使用情況
        usage_stats = storage_manager.get_storage_usage()
        
        response_data = {
            'success': True,
            'message': '存儲使用情況查詢成功',
            'timestamp': datetime.now().isoformat(),
            'data': usage_stats
        }
        
        logger.info(f"📈 存儲使用情況: {usage_stats['total_size_gb']}GB")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"存儲使用情況查詢API異常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服務器內部錯誤',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_management_bp.route('/health', methods=['GET'])
def storage_health_check():
    """
    存儲健康檢查（無需認證）
    
    GET /api/v1/storage/health
    
    Returns:
        JSON: 健康檢查結果
    """
    try:
        logger.info("🏥 收到存儲健康檢查請求")
        
        # 執行健康檢查
        health_status = storage_manager.health_check()
        
        response_data = {
            'success': health_status['healthy'],
            'message': '存儲系統健康' if health_status['healthy'] else '存儲系統存在問題',
            'timestamp': datetime.now().isoformat(),
            'data': health_status
        }
        
        status_code = 200 if health_status['healthy'] else 503
        
        logger.info(f"💚 存儲健康狀態: {'健康' if health_status['healthy'] else '異常'}")
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"存儲健康檢查API異常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服務器內部錯誤',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_management_bp.route('/cleanup', methods=['POST'])
@require_auth
def cleanup_temp_files():
    """
    清理臨時文件
    
    POST /api/v1/storage/cleanup
    
    Request Body (optional):
        {
            "max_age_hours": 24  // 文件最大保留時間（小時）
        }
    
    Returns:
        JSON: 清理結果
    """
    try:
        logger.info("🧹 收到臨時文件清理請求")
        
        # 獲取請求參數
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        # 驗證參數
        if not isinstance(max_age_hours, (int, float)) or max_age_hours <= 0:
            return jsonify({
                'success': False,
                'error': '參數錯誤',
                'message': 'max_age_hours必須是正數',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 執行清理
        cleanup_result = storage_manager.cleanup_temp_files(max_age_hours)
        
        response_data = {
            'success': True,
            'message': f'臨時文件清理完成，清理了{cleanup_result["cleaned_files"]}個文件',
            'timestamp': datetime.now().isoformat(),
            'data': cleanup_result
        }
        
        logger.info(f"🗑️ 清理完成: {cleanup_result['cleaned_files']}個文件，{cleanup_result['freed_mb']}MB")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"臨時文件清理API異常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服務器內部錯誤',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_management_bp.route('/directories/create', methods=['POST'])
@require_auth
def create_year_month_directories():
    """
    創建年月目錄結構
    
    POST /api/v1/storage/directories/create
    
    Request Body (optional):
        {
            "year": 2025,   // 年份，默認當前年
            "month": 1      // 月份，默認當前月
        }
    
    Returns:
        JSON: 創建結果
    """
    try:
        logger.info("📅 收到年月目錄創建請求")
        
        # 獲取請求參數
        data = request.get_json() or {}
        year = data.get('year')
        month = data.get('month')
        
        # 驗證參數
        if year is not None and (not isinstance(year, int) or year < 2020 or year > 2030):
            return jsonify({
                'success': False,
                'error': '參數錯誤',
                'message': '年份必須在2020-2030之間',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        if month is not None and (not isinstance(month, int) or month < 1 or month > 12):
            return jsonify({
                'success': False,
                'error': '參數錯誤',
                'message': '月份必須在1-12之間',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 創建目錄
        result = storage_manager.create_year_month_directories(year, month)
        
        response_data = {
            'success': True,
            'message': f'年月目錄創建完成，創建了{len(result["created"])}個新目錄',
            'timestamp': datetime.now().isoformat(),
            'data': result
        }
        
        logger.info(f"📁 年月目錄創建完成: {len(result['created'])}個新目錄")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"年月目錄創建API異常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服務器內部錯誤',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@storage_management_bp.route('/status', methods=['GET'])
def get_storage_status():
    """
    獲取存儲系統綜合狀態（無需認證）
    
    GET /api/v1/storage/status
    
    Returns:
        JSON: 存儲系統綜合狀態
    """
    try:
        logger.info("📋 收到存儲狀態查詢請求")
        
        # 獲取健康狀態
        health_status = storage_manager.health_check()
        
        # 獲取使用情況（簡化版）
        try:
            usage_stats = storage_manager.get_storage_usage()
            usage_summary = {
                'total_size_gb': usage_stats['total_size_gb'],
                'total_size_mb': usage_stats['total_size_mb'],
                'paths_count': len([p for p in usage_stats['paths'].values() if p.get('exists', False)])
            }
        except Exception as e:
            logger.warning(f"獲取使用情況失敗: {str(e)}")
            usage_summary = {'error': '無法獲取使用情況'}
        
        # 檢查關鍵目錄
        critical_paths_status = {}
        for path in storage_manager.critical_paths:
            critical_paths_status[path] = {
                'exists': os.path.exists(path),
                'writable': os.access(path, os.W_OK) if os.path.exists(path) else False
            }
        
        response_data = {
            'success': True,
            'message': '存儲狀態查詢成功',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'health': health_status,
                'usage': usage_summary,
                'critical_paths': critical_paths_status,
                'environment': {
                    'LOCAL_STORAGE_PATH': os.environ.get('LOCAL_STORAGE_PATH', '未設置'),
                    'VOICE_CLONE_DIR': os.environ.get('VOICE_CLONE_DIR', '未設置'),
                    'DIGITAL_HUMAN_DIR': os.environ.get('DIGITAL_HUMAN_DIR', '未設置'),
                    'WHISPER_CACHE_DIR': os.environ.get('WHISPER_CACHE_DIR', '未設置')
                }
            }
        }
        
        logger.info("📊 存儲狀態查詢完成")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"存儲狀態查詢API異常: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服務器內部錯誤',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 錯誤處理
@storage_management_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '端點不存在',
        'message': '請檢查API路徑是否正確',
        'timestamp': datetime.now().isoformat()
    }), 404

@storage_management_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': '方法不允許',
        'message': '請檢查HTTP方法是否正確',
        'timestamp': datetime.now().isoformat()
    }), 405

@storage_management_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"存儲管理API內部錯誤: {str(error)}", exc_info=True)
    return jsonify({
        'success': False,
        'error': '服務器內部錯誤',
        'message': '請聯繫管理員',
        'timestamp': datetime.now().isoformat()
    }), 500

# 藍圖信息
@storage_management_bp.route('/', methods=['GET'])
def storage_management_info():
    """
    存儲管理API信息
    
    GET /api/v1/storage/
    
    Returns:
        JSON: API信息
    """
    return jsonify({
        'service': '存儲管理API',
        'version': '1.0.0',
        'description': '提供存儲初始化、監控和維護功能',
        'endpoints': {
            'GET /': '獲取API信息',
            'GET /status': '獲取存儲系統綜合狀態（無需認證）',
            'GET /health': '存儲健康檢查（無需認證）',
            'GET /usage': '獲取存儲使用情況（需要認證）',
            'POST /initialize': '初始化存儲目錄（需要認證）',
            'POST /cleanup': '清理臨時文件（需要認證）',
            'POST /directories/create': '創建年月目錄結構（需要認證）'
        },
        'authentication': {
            'method': 'API Key',
            'header': 'X-API-Key',
            'query_param': 'api_key'
        },
        'timestamp': datetime.now().isoformat()
    }), 200