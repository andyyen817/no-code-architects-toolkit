#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FFmpeg功能测试路由
提供FFmpeg各项功能的测试接口
"""

from flask import Blueprint, request, jsonify, send_file, current_app
import os
import subprocess
import tempfile
import json
import logging
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename

# 创建FFmpeg测试蓝图
ffmpeg_test_bp = Blueprint('ffmpeg_test', __name__, url_prefix='/test/nca/ffmpeg')
logger = logging.getLogger(__name__)

# FFmpeg可执行文件路径
FFMPEG_PATH = os.path.join(os.path.dirname(os.getcwd()), 'ffmpeg-binary', 'bin', 'ffmpeg.exe')
FFPROBE_PATH = os.path.join(os.path.dirname(os.getcwd()), 'ffmpeg-binary', 'bin', 'ffprobe.exe')

# 输出目录配置
OUTPUT_DIR = os.path.join(os.getcwd(), 'output', 'ffmpeg_test')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@ffmpeg_test_bp.route('/')
def ffmpeg_test_page():
    """FFmpeg测试页面"""
    try:
        file_path = os.path.join(current_app.root_path, 'ffmpeg_test.html')
        return send_file(file_path, mimetype='text/html')
    except Exception as e:
        return jsonify({'error': f'页面载入失败: {str(e)}'}), 500

@ffmpeg_test_bp.route('/health', methods=['GET'])
def health_check():
    """FFmpeg健康检查"""
    try:
        # 检查FFmpeg是否可用
        ffmpeg_available = os.path.exists(FFMPEG_PATH)
        ffprobe_available = os.path.exists(FFPROBE_PATH)
        
        # 获取FFmpeg版本信息
        version_info = None
        if ffmpeg_available:
            try:
                result = subprocess.run(
                    [FFMPEG_PATH, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    version_info = result.stdout.split('\n')[0]
            except Exception as e:
                logger.warning(f"获取FFmpeg版本失败: {e}")
        
        return jsonify({
            'status': 'healthy' if ffmpeg_available and ffprobe_available else 'error',
            'ffmpeg_available': ffmpeg_available,
            'ffprobe_available': ffprobe_available,
            'ffmpeg_path': FFMPEG_PATH,
            'ffprobe_path': FFPROBE_PATH,
            'version_info': version_info,
            'output_dir': OUTPUT_DIR,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ffmpeg_test_bp.route('/convert', methods=['POST'])
def format_convert():
    """格式转换测试"""
    try:
        # 获取上传的文件
        if 'file' not in request.files:
            return jsonify({'error': '未提供文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 获取目标格式
        target_format = request.form.get('target_format', 'mp4')
        
        # 保存上传文件
        input_filename = secure_filename(file.filename)
        input_path = os.path.join(OUTPUT_DIR, f"input_{uuid.uuid4().hex}_{input_filename}")
        file.save(input_path)
        
        # 生成输出文件路径
        output_filename = f"converted_{uuid.uuid4().hex}.{target_format}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # 执行FFmpeg转换
        cmd = [
            FFMPEG_PATH,
            '-i', input_path,
            '-y',  # 覆盖输出文件
            output_path
        ]
        
        start_time = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        end_time = datetime.now()
        
        # 清理输入文件
        if os.path.exists(input_path):
            os.remove(input_path)
        
        if result.returncode == 0 and os.path.exists(output_path):
            # 获取文件信息
            file_size = os.path.getsize(output_path)
            processing_time = (end_time - start_time).total_seconds()
            
            return jsonify({
                'success': True,
                'message': '格式转换成功',
                'output_file': output_filename,
                'file_size': file_size,
                'processing_time': processing_time,
                'download_url': f'/test/nca/ffmpeg/download/{output_filename}'
            })
        else:
            return jsonify({
                'success': False,
                'error': '转换失败',
                'ffmpeg_error': result.stderr
            }), 500
            
    except Exception as e:
        logger.error(f"格式转换错误: {e}")
        return jsonify({'error': str(e)}), 500

@ffmpeg_test_bp.route('/metadata', methods=['POST'])
def get_metadata():
    """获取媒体文件元数据"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未提供文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 保存上传文件
        input_filename = secure_filename(file.filename)
        input_path = os.path.join(OUTPUT_DIR, f"metadata_{uuid.uuid4().hex}_{input_filename}")
        file.save(input_path)
        
        try:
            # 使用ffprobe获取元数据
            cmd = [
                FFPROBE_PATH,
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                input_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                
                # 清理输入文件
                if os.path.exists(input_path):
                    os.remove(input_path)
                
                return jsonify({
                    'success': True,
                    'metadata': metadata
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '获取元数据失败',
                    'ffprobe_error': result.stderr
                }), 500
                
        finally:
            # 确保清理临时文件
            if os.path.exists(input_path):
                os.remove(input_path)
                
    except Exception as e:
        logger.error(f"元数据获取错误: {e}")
        return jsonify({'error': str(e)}), 500

@ffmpeg_test_bp.route('/trim', methods=['POST'])
def trim_media():
    """媒体文件剪切测试"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未提供文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 获取剪切参数
        start_time = request.form.get('start_time', '0')
        duration = request.form.get('duration', '10')
        
        # 保存上传文件
        input_filename = secure_filename(file.filename)
        input_path = os.path.join(OUTPUT_DIR, f"trim_input_{uuid.uuid4().hex}_{input_filename}")
        file.save(input_path)
        
        # 生成输出文件路径
        file_ext = os.path.splitext(input_filename)[1]
        output_filename = f"trimmed_{uuid.uuid4().hex}{file_ext}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # 执行FFmpeg剪切
        cmd = [
            FFMPEG_PATH,
            '-i', input_path,
            '-ss', start_time,
            '-t', duration,
            '-c', 'copy',  # 复制编码，快速剪切
            '-y',
            output_path
        ]
        
        start_time_exec = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        end_time_exec = datetime.now()
        
        # 清理输入文件
        if os.path.exists(input_path):
            os.remove(input_path)
        
        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            processing_time = (end_time_exec - start_time_exec).total_seconds()
            
            return jsonify({
                'success': True,
                'message': '剪切成功',
                'output_file': output_filename,
                'file_size': file_size,
                'processing_time': processing_time,
                'download_url': f'/test/nca/ffmpeg/download/{output_filename}'
            })
        else:
            return jsonify({
                'success': False,
                'error': '剪切失败',
                'ffmpeg_error': result.stderr
            }), 500
            
    except Exception as e:
        logger.error(f"剪切错误: {e}")
        return jsonify({'error': str(e)}), 500

@ffmpeg_test_bp.route('/download/<filename>')
def download_file(filename):
    """下载生成的文件"""
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ffmpeg_test_bp.route('/cleanup', methods=['POST'])
def cleanup_files():
    """清理测试文件"""
    try:
        deleted_count = 0
        for filename in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1
        
        return jsonify({
            'success': True,
            'message': f'已清理 {deleted_count} 个文件'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500