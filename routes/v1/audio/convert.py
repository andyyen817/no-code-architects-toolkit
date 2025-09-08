#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音頻轉換API端點
為NCA測試中心提供音頻格式轉換功能
"""

from flask import Blueprint, request, jsonify
import logging
import os
import tempfile
from app_utils import validate_payload, queue_task_wrapper
from services.authentication import authenticate
import ffmpeg

# 創建音頻轉換藍圖
v1_audio_convert_bp = Blueprint('v1_audio_convert', __name__)
logger = logging.getLogger(__name__)

@v1_audio_convert_bp.route('/v1/audio/convert', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "audio_file": {"type": "string"},  # Base64編碼的音頻文件
        "target_format": {"type": "string", "enum": ["mp3", "wav", "aac", "flac", "ogg"]},
        "bitrate": {"type": "string", "pattern": "^[0-9]+k$"},
        "sample_rate": {"type": "number"},
        "id": {"type": "string"}
    },
    "required": ["audio_file", "target_format"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def convert_audio_format(job_id, data):
    """
    音頻格式轉換
    
    Args:
        job_id (str): 作業ID
        data (dict): 包含音頻文件和轉換參數的數據
    
    Returns:
        Tuple of (response_data, endpoint_string, status_code)
    """
    audio_file = data['audio_file']
    target_format = data['target_format']
    bitrate = data.get('bitrate', '128k')
    sample_rate = data.get('sample_rate', 44100)
    id = data.get('id')
    
    logger.info(f"Job {job_id}: 開始音頻轉換 - 目標格式: {target_format}")
    
    try:
        # 創建臨時目錄
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解碼Base64音頻文件
            import base64
            audio_data = base64.b64decode(audio_file.split(',')[1] if ',' in audio_file else audio_file)
            
            # 保存輸入文件
            input_path = os.path.join(temp_dir, f"input_audio_{job_id}")
            with open(input_path, 'wb') as f:
                f.write(audio_data)
            
            # 設置輸出文件路徑
            output_path = os.path.join(temp_dir, f"output_audio_{job_id}.{target_format}")
            
            # 使用FFmpeg進行轉換
            try:
                stream = ffmpeg.input(input_path)
                stream = ffmpeg.output(
                    stream, 
                    output_path,
                    acodec=_get_codec_for_format(target_format),
                    audio_bitrate=bitrate,
                    ar=sample_rate
                )
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
                
                logger.info(f"Job {job_id}: FFmpeg轉換完成")
                
            except ffmpeg.Error as e:
                error_msg = f"FFmpeg轉換失敗: {str(e)}"
                logger.error(f"Job {job_id}: {error_msg}")
                return {"error": error_msg}, "/v1/audio/convert", 500
            
            # 讀取輸出文件並編碼為Base64
            if os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    output_data = f.read()
                
                output_base64 = base64.b64encode(output_data).decode('utf-8')
                
                # 獲取文件大小
                file_size = len(output_data)
                
                logger.info(f"Job {job_id}: 音頻轉換成功 - 輸出大小: {file_size} bytes")
                
                return {
                    "status": "success",
                    "job_id": job_id,
                    "target_format": target_format,
                    "bitrate": bitrate,
                    "sample_rate": sample_rate,
                    "file_size": file_size,
                    "audio_data": f"data:audio/{target_format};base64,{output_base64}",
                    "download_filename": f"converted_audio_{job_id}.{target_format}"
                }, "/v1/audio/convert", 200
                
            else:
                error_msg = "轉換完成但找不到輸出文件"
                logger.error(f"Job {job_id}: {error_msg}")
                return {"error": error_msg}, "/v1/audio/convert", 500
                
    except Exception as e:
        error_msg = f"音頻轉換過程中發生錯誤: {str(e)}"
        logger.error(f"Job {job_id}: {error_msg}", exc_info=True)
        return {"error": error_msg}, "/v1/audio/convert", 500

def _get_codec_for_format(format_name):
    """根據格式返回適當的編解碼器"""
    codec_map = {
        'mp3': 'mp3',
        'wav': 'pcm_s16le',
        'aac': 'aac',
        'flac': 'flac',
        'ogg': 'libvorbis'
    }
    return codec_map.get(format_name, 'mp3')

