#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的Flask應用測試字幕功能
"""

from flask import Flask, request, jsonify, send_from_directory
import whisper
import tempfile
import os
import traceback

app = Flask(__name__)

# 全局變量存儲模型
model = None

def load_whisper_model():
    """加載Whisper模型"""
    global model
    if model is None:
        print("正在加載Whisper模型...")
        model = whisper.load_model("base")
        print("✓ Whisper模型加載成功")
    return model

@app.route('/', methods=['GET'])
def index():
    """主頁 - 返回測試頁面"""
    return send_from_directory('.', 'test_subtitle.html')

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({
        'status': 'ok',
        'message': '服務運行正常',
        'whisper_loaded': model is not None
    })

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """音頻轉錄接口"""
    try:
        # 檢查是否有文件上傳
        if 'audio' not in request.files:
            return jsonify({'error': '沒有上傳音頻文件'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': '沒有選擇文件'}), 400
        
        # 加載模型
        whisper_model = load_whisper_model()
        
        # 保存臨時文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # 進行轉錄
            print(f"正在轉錄文件: {temp_path}")
            result = whisper_model.transcribe(temp_path)
            
            # 提取文本和時間戳
            transcription = {
                'text': result['text'],
                'language': result['language'],
                'segments': []
            }
            
            # 處理分段信息
            for segment in result['segments']:
                transcription['segments'].append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text']
                })
            
            print(f"✓ 轉錄完成，語言: {result['language']}")
            return jsonify({
                'success': True,
                'transcription': transcription
            })
            
        finally:
            # 清理臨時文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        print(f"轉錄錯誤: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate_srt', methods=['POST'])
def generate_srt():
    """生成SRT字幕文件"""
    try:
        data = request.get_json()
        if not data or 'segments' not in data:
            return jsonify({'error': '缺少segments數據'}), 400
        
        segments = data['segments']
        srt_content = ""
        
        for i, segment in enumerate(segments, 1):
            start_time = format_time(segment['start'])
            end_time = format_time(segment['end'])
            text = segment['text'].strip()
            
            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{text}\n\n"
        
        return jsonify({
            'success': True,
            'srt_content': srt_content
        })
        
    except Exception as e:
        print(f"生成SRT錯誤: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def format_time(seconds):
    """將秒數轉換為SRT時間格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

if __name__ == '__main__':
    print("正在啟動測試服務器...")
    print("可用接口:")
    print("  GET  /health - 健康檢查")
    print("  POST /transcribe - 音頻轉錄")
    print("  POST /generate_srt - 生成SRT字幕")
    
    app.run(host='0.0.0.0', port=5001, debug=True)