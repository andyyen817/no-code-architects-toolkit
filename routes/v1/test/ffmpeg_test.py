from flask import Blueprint, render_template, jsonify, request
import os
import subprocess
import logging
from datetime import datetime

# 創建藍圖
ffmpeg_test_bp = Blueprint('v1_test_ffmpeg', __name__, url_prefix='/nca/test')
logger = logging.getLogger(__name__)

@ffmpeg_test_bp.route('/ffmpeg-test', methods=['GET'])
def ffmpeg_test_page():
    """FFmpeg 測試頁面"""
    try:
        return render_template('ffmpeg_test.html')
    except Exception as e:
        logger.error(f"Error loading FFmpeg test page: {str(e)}")
        return jsonify({
            'error': 'Failed to load test page',
            'message': str(e)
        }), 500

@ffmpeg_test_bp.route('/volume-analysis', methods=['POST'])
def volume_analysis():
    """音量分析測試API"""
    try:
        data = request.get_json()
        file_url = data.get('file_url')
        
        if not file_url:
            return jsonify({
                'error': 'Missing file_url parameter'
            }), 400
        
        # 模擬音量分析結果
        # 在實際實現中，這裡會調用FFmpeg進行真實的音量分析
        result = {
            'original_volume': '-18.5 dB',
            'normalized_volume': '-14.0 dB', 
            'volume_gain': '+4.5 dB',
            'analysis_time': datetime.now().isoformat(),
            'status': 'success'
        }
        
        logger.info(f"Volume analysis completed for: {file_url}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Volume analysis error: {str(e)}")
        return jsonify({
            'error': 'Volume analysis failed',
            'message': str(e)
        }), 500

@ffmpeg_test_bp.route('/ffmpeg-status', methods=['GET'])
def ffmpeg_status():
    """FFmpeg 狀態檢查API"""
    try:
        # 檢查FFmpeg是否可用
        ffmpeg_paths = [
            r'D:\no-code-architects-toolkit\no-code-architects-toolkit\ffmpeg-binary\bin\ffmpeg.exe',
            r'D:\no-code-architects-toolkit\ffmpeg-binary\bin\ffmpeg.exe',
            'ffmpeg'  # 系統PATH中的ffmpeg
        ]
        
        ffmpeg_cmd = None
        for path in ffmpeg_paths:
            if os.path.exists(path) or path == 'ffmpeg':
                try:
                    result = subprocess.run([path, '-version'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        ffmpeg_cmd = path
                        break
                except:
                    continue
        
        if ffmpeg_cmd:
            # 獲取FFmpeg版本信息
            version_result = subprocess.run([ffmpeg_cmd, '-version'], 
                                          capture_output=True, text=True)
            version_line = version_result.stdout.split('\n')[0] if version_result.stdout else 'Unknown'
            
            return jsonify({
                'status': 'available',
                'path': ffmpeg_cmd,
                'version': version_line,
                'check_time': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'not_found',
                'message': 'FFmpeg not found in expected locations',
                'checked_paths': ffmpeg_paths,
                'check_time': datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"FFmpeg status check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'check_time': datetime.now().isoformat()
        }), 500

@ffmpeg_test_bp.route('/health', methods=['GET'])
def test_health():
    """測試模塊健康檢查"""
    return jsonify({
        'status': 'healthy',
        'module': 'ffmpeg_test',
        'timestamp': datetime.now().isoformat()
    })