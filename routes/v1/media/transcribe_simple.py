# 简化版音频转录路由 - 不依赖 Whisper
import os
import logging
from flask import Blueprint, request, jsonify
from services.authentication import authenticate

v1_media_transcribe_simple_bp = Blueprint('v1_media_transcribe_simple', __name__)
logger = logging.getLogger(__name__)

@v1_media_transcribe_simple_bp.route('/v1/media/transcribe', methods=['POST'])
@authenticate
def transcribe_media_simple():
    """简化版音频转录端点 - 模拟响应"""
    logger.info("Simple media transcribe request received")
    
    try:
        data = request.get_json() or {}
        media_url = data.get('media_url')
        include_text = data.get('include_text', True)
        include_srt = data.get('include_srt', False)
        include_segments = data.get('include_segments', False)
        word_timestamps = data.get('word_timestamps', False)
        task = data.get('task', 'transcribe')
        language = data.get('language', 'auto')

        if not media_url:
            return jsonify({"message": "media_url is required"}), 400

        # 模拟转录结果
        response_data = {}
        
        if include_text:
            if task == 'translate':
                response_data['text'] = "This is a simulated translation of the audio content. The actual transcription feature requires Whisper AI model installation."
            else:
                response_data['text'] = "这是音频内容的模拟转录。实际转录功能需要安装 Whisper AI 模型。"
        
        if include_srt:
            response_data['srt'] = """1
00:00:00,000 --> 00:00:05,000
这是音频内容的模拟转录。

2
00:00:05,000 --> 00:00:10,000
实际转录功能需要安装 Whisper AI 模型。"""
        
        if include_segments:
            response_data['segments'] = [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 5.0,
                    "text": "这是音频内容的模拟转录。",
                    "words": [
                        {"start": 0.0, "end": 0.5, "word": "这是"},
                        {"start": 0.5, "end": 1.0, "word": "音频"},
                        {"start": 1.0, "end": 1.5, "word": "内容"},
                        {"start": 1.5, "end": 2.0, "word": "的"},
                        {"start": 2.0, "end": 2.5, "word": "模拟"},
                        {"start": 2.5, "end": 3.0, "word": "转录"}
                    ] if word_timestamps else None
                },
                {
                    "id": 1,
                    "seek": 5000,
                    "start": 5.0,
                    "end": 10.0,
                    "text": "实际转录功能需要安装 Whisper AI 模型。",
                    "words": [
                        {"start": 5.0, "end": 5.5, "word": "实际"},
                        {"start": 5.5, "end": 6.0, "word": "转录"},
                        {"start": 6.0, "end": 6.5, "word": "功能"},
                        {"start": 6.5, "end": 7.0, "word": "需要"},
                        {"start": 7.0, "end": 7.5, "word": "安装"},
                        {"start": 7.5, "end": 8.5, "word": "Whisper"},
                        {"start": 8.5, "end": 9.0, "word": "AI"},
                        {"start": 9.0, "end": 10.0, "word": "模型"}
                    ] if word_timestamps else None
                }
            ]

        logger.info("Simple media transcribe completed")
        
        return jsonify({
            "message": "Transcription simulation completed successfully",
            "status": "simulation_mode",
            "note": "This is a simulation. Full functionality requires Whisper AI model installation.",
            "input": {
                "media_url": media_url,
                "task": task,
                "language": language,
                "include_text": include_text,
                "include_srt": include_srt,
                "include_segments": include_segments,
                "word_timestamps": word_timestamps
            },
            "output": response_data,
            "requirements": {
                "missing_dependency": "openai-whisper",
                "install_command": "pip install openai-whisper",
                "note": "Whisper 模型较大(约1-5GB)，首次使用需下载时间较长"
            }
        }), 200

    except Exception as e:
        logger.error(f"Error in simple media transcribe: {e}")
        return jsonify({"message": f"Transcription simulation failed: {e}", "status": "error"}), 500


