#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
視頻處理API端點
為NCA測試中心提供視頻處理功能
"""

from flask import Blueprint, request, jsonify
import logging
import os
import tempfile
from app_utils import validate_payload, queue_task_wrapper
from services.authentication import authenticate
import ffmpeg
import base64

# 創建視頻處理藍圖
v1_video_process_bp = Blueprint('v1_video_process', __name__)
logger = logging.getLogger(__name__)

@v1_video_process_bp.route('/v1/video/process', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "video_file": {"type": "string"},  # Base64編碼的視頻文件
        "operation": {"type": "string", "enum": ["convert", "resize", "trim", "extract_audio", "thumbnail"]},
        "target_format": {"type": "string"},
        "width": {"type": "number"},
        "height": {"type": "number"},
        "start_time": {"type": "number"},
        "duration": {"type": "number"},
        "quality": {"type": "string", "enum": ["high", "medium", "low"]},
        "id": {"type": "string"}
    },
    "required": ["video_file", "operation"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def process_video(job_id, data):
    """
    視頻處理
    
    Args:
        job_id (str): 作業ID
        data (dict): 包含視頻文件和處理參數的數據
    
    Returns:
        Tuple of (response_data, endpoint_string, status_code)
    """
    video_file = data['video_file']
    operation = data['operation']
    target_format = data.get('target_format', 'mp4')
    width = data.get('width')
    height = data.get('height')
    start_time = data.get('start_time', 0)
    duration = data.get('duration')
    quality = data.get('quality', 'medium')
    id = data.get('id')
    
    logger.info(f"Job {job_id}: 開始視頻處理 - 操作: {operation}")
    
    try:
        # 創建臨時目錄
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解碼Base64視頻文件
            video_data = base64.b64decode(video_file.split(',')[1] if ',' in video_file else video_file)
            
            # 保存輸入文件
            input_path = os.path.join(temp_dir, f"input_video_{job_id}.mp4")
            with open(input_path, 'wb') as f:
                f.write(video_data)
            
            # 根據操作類型處理視頻
            if operation == "convert":
                return _convert_video(job_id, input_path, temp_dir, target_format, quality)
            elif operation == "resize":
                return _resize_video(job_id, input_path, temp_dir, width, height, quality)
            elif operation == "trim":
                return _trim_video(job_id, input_path, temp_dir, start_time, duration, quality)
            elif operation == "extract_audio":
                return _extract_audio(job_id, input_path, temp_dir)
            elif operation == "thumbnail":
                return _generate_thumbnail(job_id, input_path, temp_dir, start_time)
            else:
                return {"error": f"不支持的操作: {operation}"}, "/v1/video/process", 400
                
    except Exception as e:
        error_msg = f"視頻處理過程中發生錯誤: {str(e)}"
        logger.error(f"Job {job_id}: {error_msg}", exc_info=True)
        return {"error": error_msg}, "/v1/video/process", 500

def _convert_video(job_id, input_path, temp_dir, target_format, quality):
    """轉換視頻格式"""
    output_path = os.path.join(temp_dir, f"converted_{job_id}.{target_format}")
    
    try:
        # 設置質量參數
        crf = _get_crf_for_quality(quality)
        
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(
            stream, 
            output_path,
            vcodec='libx264',
            crf=crf,
            preset='medium'
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return _create_video_response(job_id, output_path, "convert", target_format)
        
    except ffmpeg.Error as e:
        return {"error": f"視頻轉換失敗: {str(e)}"}, "/v1/video/process", 500

def _resize_video(job_id, input_path, temp_dir, width, height, quality):
    """調整視頻尺寸"""
    output_path = os.path.join(temp_dir, f"resized_{job_id}.mp4")
    
    try:
        if not width or not height:
            return {"error": "調整尺寸需要指定寬度和高度"}, "/v1/video/process", 400
        
        crf = _get_crf_for_quality(quality)
        
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.filter(stream, 'scale', width, height)
        stream = ffmpeg.output(stream, output_path, vcodec='libx264', crf=crf)
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return _create_video_response(job_id, output_path, "resize", "mp4")
        
    except ffmpeg.Error as e:
        return {"error": f"視頻尺寸調整失敗: {str(e)}"}, "/v1/video/process", 500

def _trim_video(job_id, input_path, temp_dir, start_time, duration, quality):
    """裁剪視頻"""
    output_path = os.path.join(temp_dir, f"trimmed_{job_id}.mp4")
    
    try:
        crf = _get_crf_for_quality(quality)
        
        stream = ffmpeg.input(input_path, ss=start_time)
        if duration:
            stream = ffmpeg.output(stream, output_path, t=duration, vcodec='libx264', crf=crf)
        else:
            stream = ffmpeg.output(stream, output_path, vcodec='libx264', crf=crf)
        
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return _create_video_response(job_id, output_path, "trim", "mp4")
        
    except ffmpeg.Error as e:
        return {"error": f"視頻裁剪失敗: {str(e)}"}, "/v1/video/process", 500

def _extract_audio(job_id, input_path, temp_dir):
    """提取音頻"""
    output_path = os.path.join(temp_dir, f"audio_{job_id}.mp3")
    
    try:
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, acodec='mp3', audio_bitrate='128k')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return _create_audio_response(job_id, output_path, "extract_audio")
        
    except ffmpeg.Error as e:
        return {"error": f"音頻提取失敗: {str(e)}"}, "/v1/video/process", 500

def _generate_thumbnail(job_id, input_path, temp_dir, start_time=0):
    """生成縮略圖"""
    output_path = os.path.join(temp_dir, f"thumbnail_{job_id}.jpg")
    
    try:
        stream = ffmpeg.input(input_path, ss=start_time)
        stream = ffmpeg.output(stream, output_path, vframes=1, format='image2')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        return _create_image_response(job_id, output_path, "thumbnail")
        
    except ffmpeg.Error as e:
        return {"error": f"縮略圖生成失敗: {str(e)}"}, "/v1/video/process", 500

def _create_video_response(job_id, output_path, operation, format_name):
    """創建視頻響應"""
    if os.path.exists(output_path):
        with open(output_path, 'rb') as f:
            output_data = f.read()
        
        output_base64 = base64.b64encode(output_data).decode('utf-8')
        file_size = len(output_data)
        
        logger.info(f"Job {job_id}: 視頻{operation}成功 - 輸出大小: {file_size} bytes")
        
        return {
            "status": "success",
            "job_id": job_id,
            "operation": operation,
            "format": format_name,
            "file_size": file_size,
            "video_data": f"data:video/{format_name};base64,{output_base64}",
            "download_filename": f"{operation}_{job_id}.{format_name}"
        }, "/v1/video/process", 200
    else:
        return {"error": f"{operation}完成但找不到輸出文件"}, "/v1/video/process", 500

def _create_audio_response(job_id, output_path, operation):
    """創建音頻響應"""
    if os.path.exists(output_path):
        with open(output_path, 'rb') as f:
            output_data = f.read()
        
        output_base64 = base64.b64encode(output_data).decode('utf-8')
        file_size = len(output_data)
        
        logger.info(f"Job {job_id}: 音頻{operation}成功 - 輸出大小: {file_size} bytes")
        
        return {
            "status": "success",
            "job_id": job_id,
            "operation": operation,
            "format": "mp3",
            "file_size": file_size,
            "audio_data": f"data:audio/mp3;base64,{output_base64}",
            "download_filename": f"{operation}_{job_id}.mp3"
        }, "/v1/video/process", 200
    else:
        return {"error": f"{operation}完成但找不到輸出文件"}, "/v1/video/process", 500

def _create_image_response(job_id, output_path, operation):
    """創建圖像響應"""
    if os.path.exists(output_path):
        with open(output_path, 'rb') as f:
            output_data = f.read()
        
        output_base64 = base64.b64encode(output_data).decode('utf-8')
        file_size = len(output_data)
        
        logger.info(f"Job {job_id}: 圖像{operation}成功 - 輸出大小: {file_size} bytes")
        
        return {
            "status": "success",
            "job_id": job_id,
            "operation": operation,
            "format": "jpg",
            "file_size": file_size,
            "image_data": f"data:image/jpeg;base64,{output_base64}",
            "download_filename": f"{operation}_{job_id}.jpg"
        }, "/v1/video/process", 200
    else:
        return {"error": f"{operation}完成但找不到輸出文件"}, "/v1/video/process", 500

def _get_crf_for_quality(quality):
    """根據質量設置獲取CRF值"""
    quality_map = {
        'high': 18,
        'medium': 23,
        'low': 28
    }
    return quality_map.get(quality, 23)

