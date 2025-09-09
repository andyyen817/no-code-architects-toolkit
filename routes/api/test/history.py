#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試歷史API端點
為NCA測試中心提供測試歷史查詢功能
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

# 創建測試歷史藍圖
api_test_history_bp = Blueprint('api_test_history', __name__)
logger = logging.getLogger(__name__)

@api_test_history_bp.route('/api/test/history', methods=['GET'])
def get_test_history():
    """
    獲取測試歷史記錄
    
    Returns:
        JSON響應包含測試歷史數據
    """
    try:
        # 目前返回模擬的測試歷史數據
        # 在實際實現中，這裡會從數據庫查詢真實數據
        test_history = {
            "status": "success",
            "total_tests": 15,
            "success_rate": 0.73,
            "last_updated": datetime.now().isoformat(),
            "tests": [
                {
                    "id": "test_001",
                    "type": "audio_convert",
                    "operation": "mp3",
                    "status": "success",
                    "duration_ms": 2340,
                    "timestamp": "2025-01-09T18:45:00Z",
                    "file_size": 1024000
                },
                {
                    "id": "test_002", 
                    "type": "audio_convert",
                    "operation": "wav",
                    "status": "failed",
                    "error": "轉換超時",
                    "duration_ms": 30000,
                    "timestamp": "2025-01-09T18:46:00Z",
                    "file_size": 2048000
                },
                {
                    "id": "test_003",
                    "type": "video_process",
                    "operation": "thumbnail",
                    "status": "success", 
                    "duration_ms": 1200,
                    "timestamp": "2025-01-09T18:47:00Z",
                    "file_size": 5120000
                },
                {
                    "id": "test_004",
                    "type": "video_process",
                    "operation": "convert",
                    "status": "success",
                    "duration_ms": 8900,
                    "timestamp": "2025-01-09T18:48:00Z", 
                    "file_size": 10240000
                },
                {
                    "id": "test_005",
                    "type": "video_process",
                    "operation": "trim",
                    "status": "failed",
                    "error": "參數錯誤",
                    "duration_ms": 500,
                    "timestamp": "2025-01-09T18:49:00Z",
                    "file_size": 7680000
                }
            ],
            "statistics": {
                "audio_tests": {
                    "total": 8,
                    "success": 5,
                    "failed": 3,
                    "success_rate": 0.625
                },
                "video_tests": {
                    "total": 7,
                    "success": 6,
                    "failed": 1, 
                    "success_rate": 0.857
                },
                "average_duration_ms": 4200,
                "total_data_processed": "156 MB"
            }
        }
        
        logger.info("測試歷史查詢成功")
        return jsonify(test_history), 200
        
    except Exception as e:
        error_msg = f"獲取測試歷史失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500

@api_test_history_bp.route('/api/test/history', methods=['POST'])
def add_test_record():
    """
    添加測試記錄
    
    Returns:
        JSON響應確認記錄已添加
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "沒有提供測試數據"}), 400
        
        # 驗證必需字段
        required_fields = ['type', 'operation', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必需字段: {field}"}), 400
        
        # 在實際實現中，這裡會將數據保存到數據庫
        test_record = {
            "id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": data['type'],
            "operation": data['operation'], 
            "status": data['status'],
            "duration_ms": data.get('duration_ms', 0),
            "error": data.get('error'),
            "file_size": data.get('file_size', 0),
            "timestamp": datetime.now().isoformat(),
            "created": True
        }
        
        logger.info(f"測試記錄已添加: {test_record['id']}")
        return jsonify({
            "status": "success",
            "message": "測試記錄已添加",
            "record": test_record
        }), 201
        
    except Exception as e:
        error_msg = f"添加測試記錄失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({"error": error_msg}), 500




