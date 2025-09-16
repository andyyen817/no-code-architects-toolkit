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
    
    # 生成作業ID
    job_id = f"test_{id_param}" if id_param else "test_job"

    # 十步法 - 第一步：請求接收與驗證（測試端點）
    logger.info(f"Job {job_id}: [步驟1/8] 請求接收與驗證 - 開始處理測試字幕請求（無需認證）")
    logger.info(f"Job {job_id}: [步驟1/8] 視頻URL: {video_url}")
    logger.info(f"Job {job_id}: [步驟1/8] 字幕內容: {'已提供' if captions else '未提供，將使用自動轉錄'}")
    logger.info(f"Job {job_id}: [步驟1/8] 語言設置: {language}")
    logger.info(f"Job {job_id}: [步驟1/8] 樣式設置: {settings}")
    logger.info(f"Job {job_id}: [步驟1/8] 文本替換規則: {replace}")
    logger.info(f"Job {job_id}: [步驟1/8] 排除時間範圍: {exclude_time_ranges}")
    logger.info(f"Job {job_id}: [步驟1/8] 測試端點請求驗證完成，準備調用核心服務")

    try:
        # 十步法 - 第二步：核心字幕生成服務調用（測試端點）
        logger.info(f"Job {job_id}: [步驟2/8] 核心字幕生成服務調用 - 開始調用generate_ass_captions_v1（測試模式）")
        result = generate_ass_captions_v1(
            video_url=video_url,
            captions=captions,
            settings=settings,
            replace=replace,
            exclude_time_ranges=exclude_time_ranges,
            job_id=job_id,
            language=language
        )
        
        logger.info(f"Job {job_id}: [步驟8/8] 字幕生成完成 - 測試端點處理結果: {result}")
        logger.info(f"Job {job_id}: [測試端點說明] 注意：測試端點僅生成字幕文件，不進行視頻渲染和雲端上傳")
        
        # 十步法 - 測試端點響應返回（步驟1-8完成）
        logger.info(f"Job {job_id}: [測試端點響應] 開始構建測試端點響應")
        response = {
            "job_id": job_id,
            "message": "Video caption generation completed successfully",
            "status": "completed",
            "output_file": result if isinstance(result, str) else result.get('output_file'),
            "processing_info": result,
            "note": "測試端點僅生成字幕文件，如需完整帶字幕視頻請使用 /v1/video/caption"
        }
        
        # 如果有webhook，发送通知
        if webhook_url:
            try:
                logger.info(f"Job {job_id}: [測試端點響應] 發送Webhook通知到: {webhook_url}")
                requests.post(webhook_url, json=response, timeout=10)
                logger.info(f"Job {job_id}: [測試端點響應] Webhook通知發送成功")
            except Exception as webhook_error:
                logger.warning(f"Job {job_id}: [測試端點響應] Webhook發送失敗: {webhook_error}")
        
        logger.info(f"Job {job_id}: [測試端點響應] 測試字幕生成流程完成！")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Job {job_id}: [測試端點錯誤] 測試字幕生成失敗: {e}", exc_info=True)
        error_response = {
            "job_id": job_id,
            "message": f"Video caption generation failed: {str(e)}",
            "status": "failed",
            "error": str(e),
            "note": "測試端點錯誤，請檢查日誌獲取詳細信息"
        }
        
        # 如果有webhook，发送错误通知
        if webhook_url:
            try:
                logger.info(f"Job {job_id}: [測試端點錯誤] 發送錯誤Webhook通知到: {webhook_url}")
                requests.post(webhook_url, json=error_response, timeout=10)
                logger.info(f"Job {job_id}: [測試端點錯誤] 錯誤Webhook通知發送成功")
            except Exception as webhook_error:
                logger.warning(f"Job {job_id}: [測試端點錯誤] 錯誤Webhook發送失敗: {webhook_error}")
        
        return jsonify(error_response), 500