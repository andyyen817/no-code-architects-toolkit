# Enhanced audio transcription with both global and fallback support
import os
import tempfile
import logging
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from services.local_storage import local_storage

v1_media_transcribe_enhanced_bp = Blueprint('v1_media_transcribe_enhanced', __name__)
logger = logging.getLogger(__name__)

# Try to import faster-whisper (should be available in global environment)
WHISPER_AVAILABLE = False
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
    logger.info("faster-whisper is available (global environment)")
except ImportError:
    logger.warning("faster-whisper not available, using simulation mode")

def download_media(url: str, temp_dir: str) -> str:
    """Download media file to temporary directory"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file extension
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
    """Transcribe audio using faster-whisper (CPU optimized)"""
    try:
        # Use small model (balance between accuracy and performance)
        logger.info("Loading faster-whisper small model...")
        model = WhisperModel("small", device="cpu", compute_type="int8", num_workers=1)
        logger.info("Model loaded successfully")
        
        # Check audio file size and duration
        import os
        file_size = os.path.getsize(audio_path) / (1024 * 1024)  # MB
        logger.info(f"Audio file size: {file_size:.2f} MB")
        
        # Perform transcription
        logger.info("Starting transcription process...")
        segments, info = model.transcribe(
            audio_path, 
            task=task,
            language=language if language and language != "auto" else None,
            word_timestamps=True,
            vad_filter=True,  # Voice activity detection for better accuracy
            beam_size=1,      # Reduce beam size for faster processing
            patience=1.0      # Reduce patience for faster processing
        )
        logger.info("Transcription process completed")
        
        # Process results
        result = {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": [],
            "text": ""
        }
        
        full_text = []
        
        logger.info("Processing transcription segments...")
        segment_count = 0
        for i, segment in enumerate(segments):
            segment_count += 1
            segment_data = {
                "id": i,
                "seek": int(segment.start * 1000),  # milliseconds
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": []
            }
            
            # Add word-level timestamps
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
            
            # Log progress every 10 segments
            if segment_count % 10 == 0:
                logger.info(f"Processed {segment_count} segments...")
        
        result["text"] = " ".join(full_text)
        logger.info(f"Successfully processed {segment_count} segments")
        return result
        
    except Exception as e:
        logger.error(f"Error in faster-whisper transcription: {e}")
        raise

def generate_srt(segments: list, max_words_per_line: int = 10) -> str:
    """Generate SRT subtitle format"""
    srt_content = []
    
    for i, segment in enumerate(segments, 1):
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]
        
        # Format time
        start_srt = f"{int(start_time//3600):02d}:{int((start_time%3600)//60):02d}:{int(start_time%60):02d},{int((start_time%1)*1000):03d}"
        end_srt = f"{int(end_time//3600):02d}:{int((end_time%3600)//60):02d}:{int(end_time%60):02d},{int((end_time%1)*1000):03d}"
        
        # Split long text
        words = text.split()
        if len(words) > max_words_per_line:
            lines = []
            for j in range(0, len(words), max_words_per_line):
                lines.append(" ".join(words[j:j+max_words_per_line]))
            text = "\n".join(lines)
        
        srt_content.append(f"{i}\n{start_srt} --> {end_srt}\n{text}\n")
    
    return "\n".join(srt_content)

def create_simulation_response(data: dict) -> dict:
    """Create simulation response when Whisper is not available"""
    media_url = data.get('media_url')
    include_text = data.get('include_text', True)
    include_srt = data.get('include_srt', False)
    include_segments = data.get('include_segments', False)
    word_timestamps = data.get('word_timestamps', False)
    task = data.get('task', 'transcribe')
    language = data.get('language', 'auto')

    response_data = {}
    
    if include_text:
        if task == 'translate':
            response_data['text'] = "This is a simulated English translation of the audio content. Install faster-whisper for real transcription: pip install faster-whisper"
        else:
            response_data['text'] = "这是音频内容的模拟转录。安装 faster-whisper 获得真实转录功能: pip install faster-whisper"
    
    if include_srt:
        response_data['srt'] = """1
00:00:00,000 --> 00:00:05,000
这是音频内容的模拟转录。

2
00:00:05,000 --> 00:00:10,000
安装 faster-whisper 获得真实转录功能。"""
    
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
            }
        ]

    return {
        "message": "Transcription simulation completed successfully",
        "status": "simulation_mode",
        "note": "This is a simulation. Install faster-whisper for real functionality: pip install faster-whisper",
        "input": {
            "media_url": media_url,
            "task": task,
            "language": language
        },
        "output": response_data,
        "requirements": {
            "missing_dependency": "faster-whisper",
            "install_command": "pip install faster-whisper",
            "note": "Whisper model is large (1-5GB), first use requires download time"
        }
    }

@v1_media_transcribe_enhanced_bp.route('/v1/media/transcribe', methods=['POST'])
@authenticate
def transcribe_media_enhanced():
    """Enhanced audio transcription endpoint with global environment support"""
    logger.info("Enhanced media transcribe request received")
    
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

        # If Whisper is not available, return simulation
        if not WHISPER_AVAILABLE:
            return jsonify(create_simulation_response(data)), 200

        # Real transcription with faster-whisper
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download media file
            input_media_path = download_media(media_url, temp_dir)
            
            # Perform transcription
            logger.info(f"Starting transcription for: {media_url}")
            start_time = datetime.now()
            transcription_result = transcribe_with_faster_whisper(
                input_media_path, 
                task=task, 
                language=language if language != "auto" else None
            )
            process_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Transcription completed in {process_time:.2f} seconds")
            
            # Build response
            response_data = {}
            
            if include_text:
                response_data['text'] = transcription_result['text']
            
            if include_srt:
                srt_content = generate_srt(transcription_result['segments'], max_words_per_line)
                response_data['srt'] = srt_content
                
                # Save SRT file to local storage
                if srt_content:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    srt_filename = f"transcription_{timestamp}.srt"
                    srt_path = os.path.join(temp_dir, srt_filename)
                    
                    with open(srt_path, 'w', encoding='utf-8') as f:
                        f.write(srt_content)
                    
                    saved_srt_path = local_storage.save_file(srt_path, 'subtitles')
                    response_data['srt_url'] = local_storage.get_file_url(saved_srt_path)
            
            if include_segments:
                if word_timestamps:
                    response_data['segments'] = transcription_result['segments']
                else:
                    # Remove word-level timestamps
                    segments_no_words = []
                    for segment in transcription_result['segments']:
                        segment_copy = segment.copy()
                        segment_copy.pop('words', None)
                        segments_no_words.append(segment_copy)
                    response_data['segments'] = segments_no_words

            logger.info(f"Real transcription completed in {process_time:.2f}s")
            
            return jsonify({
                "message": "Real transcription completed successfully",
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
                    "device": "cpu",
                    "environment": "global_python"
                }
            }), 200

    except Exception as e:
        logger.error(f"Error in enhanced transcription: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Return a more informative error response
        return jsonify({
            "message": f"Transcription failed: {str(e)}", 
            "status": "error",
            "error_type": type(e).__name__,
            "input": {
                "media_url": data.get('media_url', 'Unknown'),
                "task": data.get('task', 'transcribe'),
                "language": data.get('language', 'auto')
            },
            "troubleshooting": {
                "possible_causes": [
                    "Audio file too large (try smaller files first)",
                    "Insufficient memory (close other applications)",
                    "Corrupted audio file",
                    "Network timeout during download"
                ],
                "solutions": [
                    "Try with a shorter audio file (< 1 minute)",
                    "Restart the server",
                    "Check audio file accessibility",
                    "Ensure stable internet connection"
                ]
            },
            "note": "Check server logs for detailed error information"
        }), 500
