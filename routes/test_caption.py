# 临时测试字幕功能 - 无需认证
from flask import Blueprint, jsonify, request
from app_utils import validate_payload
import logging
from services.ass_toolkit import generate_ass_captions_v1
from services.cloud_storage import upload_file
import os
import requests

test_caption_bp = Blueprint('test_caption', __name__)
logger = logging.getLogger(__name__)

@test_caption_bp.route('/test/caption', methods=['POST'])
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
                "font_family": {"type": "string"},
                "font_size": {"type": "integer"},
                "bold": {"type": "boolean"},
                "italic": {"type": "boolean"},
                "style": {
                    "type": "string",
                    "enum": ["classic", "karaoke", "highlight", "underline", "word_by_word"]
                }
            },
            "additionalProperties": False
        },
        "language": {"type": "string"},
        "replace": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "find": {"type": "string"},
                    "replace": {"type": "string"}
                },
                "required": ["find", "replace"],
                "additionalProperties": False
            }
        },
        "exclude_time_ranges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "number"},
                    "end": {"type": "number"}
                },
                "required": ["start", "end"],
                "additionalProperties": False
            }
        },
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"}
    },
    "required": ["video_url"],
    "additionalProperties": False
})
def test_caption_video():
    data = request.get_json() or {}
    """测试字幕生成功能 - 无需认证"""
    video_url = data['video_url']
    captions = data.get('captions', None)  # None means auto-generate transcription
    settings = data.get('settings', {})
    language = data.get('language', 'auto')
    replace = data.get('replace', [])
    exclude_time_ranges = data.get('exclude_time_ranges', [])
    webhook_url = data.get('webhook_url')
    id_param = data.get('id')

    logger.info(f"Test caption request for {video_url}")
    logger.info(f"Settings: {settings}")

    try:
        # 调用字幕生成服务
        job_id = f"test_{id_param}" if id_param else "test_job"
        result = generate_ass_captions_v1(
            video_url=video_url,
            captions=captions,
            settings=settings,
            replace=replace,
            exclude_time_ranges=exclude_time_ranges,
            job_id=job_id,
            language=language
        )
        
        logger.info(f"Caption generation completed: {result}")
        
        # 构建响应
        response = {
            "job_id": f"test_{id_param}" if id_param else "test_job",
            "message": "Video caption generation completed successfully",
            "status": "completed",
            "output_file": result.get('output_file'),
            "processing_info": result
        }
        
        # 如果有webhook，发送通知
        if webhook_url:
            try:
                requests.post(webhook_url, json=response, timeout=10)
                logger.info(f"Webhook notification sent to {webhook_url}")
            except Exception as webhook_error:
                logger.warning(f"Failed to send webhook: {webhook_error}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in test caption generation: {e}")
        error_response = {
            "job_id": f"test_{id_param}" if id_param else "test_job",
            "message": f"Video caption generation failed: {str(e)}",
            "status": "failed",
            "error": str(e)
        }
        
        # 如果有webhook，发送错误通知
        if webhook_url:
            try:
                requests.post(webhook_url, json=error_response, timeout=10)
                logger.info(f"Error webhook notification sent to {webhook_url}")
            except Exception as webhook_error:
                logger.warning(f"Failed to send error webhook: {webhook_error}")
        
        return jsonify(error_response), 500