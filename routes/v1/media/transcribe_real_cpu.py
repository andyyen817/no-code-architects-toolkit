# CPU优化版音频转录路由 - 使用 faster-whisper
import os
import tempfile
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.output_file_manager import output_file_manager

v1_media_transcribe_real_cpu_bp = Blueprint('v1_media_transcribe_real_cpu', __name__)
logger = logging.getLogger(__name__)

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
    logger.info("faster-whisper is available")
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("faster-whisper not available, using simulation mode")

def download_media(url: str, temp_dir: str) -> str:
    """下載媒體文件到臨時目錄"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 獲取文件擴展名
        original_filename = url.split('/')[-1].split('?')[0]
        file_extension = os.path.splitext(original_filename)[1] if '.' in original_filename else '.mp3'
        
        temp_filename = os.path.join(temp_dir, f"input_media{file_extension}")
        
        with open(temp_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Media downloaded: {temp_filename}")
        return temp_filename
        
    except Exception as e:
        logger.error(f"Error downloading media from {url}: {e}")
        raise

def transcribe_with_faster_whisper(audio_path: str, task: str = "transcribe", language: str = None) -> dict:
    """使用 faster-whisper 進行轉錄 (CPU優化)"""
    try:
        # 使用 small 模型 (平衡準確性和性能)
        model = WhisperModel("small", device="cpu", compute_type="int8")
        
        # 進行轉錄
        segments, info = model.transcribe(
            audio_path, 
            task=task,
            language=language if language and language != "auto" else None,
            word_timestamps=True,
            vad_filter=True  # 語音活動檢測，提高準確性
        )
        
        # 處理結果
        result = {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": [],
            "text": ""
        }
        
        full_text = []
        
        for i, segment in enumerate(segments):
            segment_data = {
                "id": i,
                "seek": int(segment.start * 1000),  # 毫秒
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": []
            }
            
            # 添加詞級時間戳
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    segment_data["words"].append({
                        "start": word.start,
                        "end": word.end,
                        "word": word.word.strip(),
                        "probability": getattr(word, 'probability', 0.0)
                    })
            
            result["segments"].append(segment_data)
            full_text.append(segment.text.strip())
        
        result["text"] = " ".join(full_text)
        return result
        
    except Exception as e:
        logger.error(f"Error in faster-whisper transcription: {e}")
        raise

def generate_srt(segments: list, max_words_per_line: int = 10) -> str:
    """生成SRT字幕格式"""
    srt_content = []
    
    for i, segment in enumerate(segments, 1):
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]
        
        # 格式化時間
        start_srt = f"{int(start_time//3600):02d}:{int((start_time%3600)//60):02d}:{int(start_time%60):02d},{int((start_time%1)*1000):03d}"
        end_srt = f"{int(end_time//3600):02d}:{int((end_time%3600)//60):02d}:{int(end_time%60):02d},{int((end_time%1)*1000):03d}"
        
        # 分割長文本
        words = text.split()
        if len(words) > max_words_per_line:
            lines = []
            for j in range(0, len(words), max_words_per_line):
                lines.append(" ".join(words[j:j+max_words_per_line]))
            text = "\n".join(lines)
        
        srt_content.append(f"{i}\n{start_srt} --> {end_srt}\n{text}\n")
    
    return "\n".join(srt_content)

@v1_media_transcribe_real_cpu_bp.route('/v1/media/transcribe', methods=['POST'])
@authenticate
def transcribe_media_real_cpu():
    """CPU優化版音頻轉錄端點"""
    logger.info("CPU-optimized media transcribe request received")
    
    if not WHISPER_AVAILABLE:
        # 回退到模擬模式
        return jsonify({
            "message": "faster-whisper not installed, using simulation mode",
            "status": "simulation_mode",
            "note": "Install faster-whisper for real functionality: pip install faster-whisper",
            "simulation_data": "模擬轉錄結果..."
        }), 200
    
    try:
        data = request.get_json() or {}
        media_url = data.get('media_url')
        include_text = data.get('include_text', True)
        include_srt = data.get('include_srt', False)
        include_segments = data.get('include_segments', False)
        word_timestamps = data.get('word_timestamps', False)
        task = data.get('task', 'transcribe')
        language = data.get('language', 'auto')
        max_words_per_line = data.get('max_words_per_line', 10)

        if not media_url:
            return jsonify({"message": "media_url is required"}), 400

        with tempfile.TemporaryDirectory() as temp_dir:
            # 下載媒體文件
            input_media_path = download_media(media_url, temp_dir)
            
            # 使用 faster-whisper 進行轉錄
            start_time = datetime.now()
            transcription_result = transcribe_with_faster_whisper(
                input_media_path, 
                task=task, 
                language=language if language != "auto" else None
            )
            process_time = (datetime.now() - start_time).total_seconds()
            
            # 構建響應
            response_data = {}
            
            if include_text:
                response_data['text'] = transcription_result['text']
            
            if include_srt:
                srt_content = generate_srt(transcription_result['segments'], max_words_per_line)
                response_data['srt'] = srt_content
                
                # 保存SRT文件到本地存储
                if srt_content:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    srt_filename = f"transcription_{timestamp}.srt"
                    srt_path = os.path.join(temp_dir, srt_filename)
                    
                    with open(srt_path, 'w', encoding='utf-8') as f:
                        f.write(srt_content)
                    
                    # 使用統一的輸出文件管理器保存到MySQL數據庫
                    srt_file_info = output_file_manager.save_output_file(
                        source_file_path=srt_path,
                        file_type='audio',  # SRT可以當作音頻相關文件
                        operation='transcribe_srt',
                        original_filename=os.path.basename(media_url),
                        metadata={
                            'source_url': media_url,
                            'task': task,
                            'language': language,
                            'detected_language': transcription_result.get('language', 'unknown')
                        }
                    )
                    response_data['srt_url'] = srt_file_info['file_url']
            
            if include_segments:
                if word_timestamps:
                    response_data['segments'] = transcription_result['segments']
                else:
                    # 移除詞級時間戳
                    segments_no_words = []
                    for segment in transcription_result['segments']:
                        segment_copy = segment.copy()
                        segment_copy.pop('words', None)
                        segments_no_words.append(segment_copy)
                    response_data['segments'] = segments_no_words

            logger.info(f"CPU transcription completed in {process_time:.2f}s")
            
            return jsonify({
                "message": "Transcription completed successfully",
                "status": "completed",
                "input": {
                    "media_url": media_url,
                    "task": task,
                    "language": language,
                    "detected_language": transcription_result.get('language', 'unknown'),
                    "language_probability": transcription_result.get('language_probability', 0.0),
                    "duration": transcription_result.get('duration', 0.0)
                },
                "output": response_data,
                "performance": {
                    "processing_time_seconds": process_time,
                    "model_used": "faster-whisper-tiny-cpu",
                    "compute_type": "int8",
                    "device": "cpu"
                }
            }), 200

    except Exception as e:
        logger.error(f"Error in CPU transcription: {e}")
        return jsonify({
            "message": f"Transcription failed: {e}", 
            "status": "error",
            "note": "Check audio file format and accessibility"
        }), 500






