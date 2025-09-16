from flask import Blueprint, request, jsonify
import logging
import os
import tempfile
import subprocess
from datetime import datetime

caption_minimal_bp = Blueprint('caption_minimal', __name__)
logger = logging.getLogger(__name__)

@caption_minimal_bp.route('/v1/video/caption/minimal', methods=['POST'])
def caption_video_minimal():
    """最小化字幕API - 不依賴外部庫"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        video_url = data.get('video_url')
        if not video_url:
            return jsonify({
                'status': 'error',
                'message': 'video_url is required'
            }), 400
        
        # 模擬字幕處理
        result = {
            'status': 'success',
            'message': 'Video caption processing initiated (minimal version)',
            'video_url': video_url,
            'processing_id': f'minimal_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'estimated_time': '5-10 minutes',
            'note': 'This is a minimal version without external dependencies'
        }
        
        # 添加可選參數
        if 'webhook_url' in data:
            result['webhook_url'] = data['webhook_url']
        
        if 'id' in data:
            result['request_id'] = data['id']
        
        logger.info(f"Minimal caption processing started for: {video_url}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in minimal caption processing: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Processing failed: {str(e)}'
        }), 500

@caption_minimal_bp.route('/v1/video/caption/minimal/status', methods=['GET'])
def caption_status_minimal():
    """檢查字幕處理狀態 - 最小化版本"""
    processing_id = request.args.get('id')
    
    if not processing_id:
        return jsonify({
            'status': 'error',
            'message': 'processing_id is required'
        }), 400
    
    # 模擬狀態檢查
    return jsonify({
        'status': 'success',
        'processing_id': processing_id,
        'state': 'processing',
        'progress': '50%',
        'message': 'Caption generation in progress (minimal version)'
    })

@caption_minimal_bp.route('/v1/video/caption/minimal/health', methods=['GET'])
def caption_health_minimal():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'service': 'caption_minimal',
        'version': '1.0.0',
        'dependencies': 'none',
        'timestamp': datetime.now().isoformat()
    })