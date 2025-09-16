#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request
from app_utils import validate_payload
import logging
from services.authentication import authenticate
import os

v1_video_caption_simple_bp = Blueprint('v1_video_caption_simple', __name__)
logger = logging.getLogger(__name__)

@v1_video_caption_simple_bp.route('/v1/video/caption/simple', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_url": {"type": "string", "format": "uri"},
        "captions": {"type": "string"},
        "settings": {
            "type": "object",
            "properties": {
                "line_color": {"type": "string"},
                "word_color": {"type": "string"},
                "outline_color": {"type": "string"},
                "all_caps": {"type": "boolean"},
                "max_words_per_line": {"type": "integer"},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "position": {
                    "type": "string",
                    "enum": [
                        "top_left", "top_center", "top_right",
                        "middle_left", "middle_center", "middle_right",
                        "bottom_left", "bottom_center", "bottom_right"
                    ]
                },
                "font_size": {"type": "integer"},
                "font_family": {"type": "string"}
            },
            "additionalProperties": False
        },
        "webhook_url": {"type": "string", "format": "uri"}
    },
    "required": ["video_url", "captions"],
    "additionalProperties": False
})
def generate_video_captions_simple():
    """
    簡化版影片字幕生成端點
    用於測試Zeabur環境中的基本功能
    """
    try:
        data = request.get_json()
        video_url = data['video_url']
        captions = data['captions']
        settings = data.get('settings', {})
        webhook_url = data.get('webhook_url')
        
        logger.info(f"收到簡化版字幕生成請求: {video_url}")
        
        # 返回模擬響應
        response = {
            "message": "簡化版字幕生成請求已接收",
            "status": "processing",
            "video_url": video_url,
            "captions_length": len(captions),
            "settings": settings,
            "webhook_url": webhook_url,
            "note": "這是簡化版端點，用於測試Zeabur環境"
        }
        
        logger.info(f"簡化版字幕生成響應: {response}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"簡化版字幕生成錯誤: {str(e)}")
        return jsonify({
            "error": "簡化版字幕生成失敗",
            "details": str(e)
        }), 500

@v1_video_caption_simple_bp.route('/v1/video/caption/simple/test', methods=['GET'])
def test_simple_caption():
    """
    測試端點，檢查簡化版字幕功能是否正常
    """
    return jsonify({
        "message": "簡化版字幕端點正常運行",
        "status": "ok",
        "endpoint": "/v1/video/caption/simple",
        "methods": ["POST"],
        "environment": "zeabur" if os.getenv('ZEABUR') else "local"
    }), 200