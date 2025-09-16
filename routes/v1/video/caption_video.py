# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



from flask import Blueprint, jsonify, request
from app_utils import validate_payload
import logging
from services.ass_toolkit import generate_ass_captions_v1
from services.authentication import authenticate
from services.cloud_storage import upload_file
import os
import requests  # Ensure requests is imported for webhook handling

v1_video_caption_bp = Blueprint('v1_video_caption', __name__)
logger = logging.getLogger(__name__)

@v1_video_caption_bp.route('/v1/video/caption', methods=['POST'])
@authenticate
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
                        "bottom_left", "bottom_center", "bottom_right",
                        "middle_left", "middle_center", "middle_right",
                        "top_left", "top_center", "top_right"
                    ]
                },
                "alignment": {
                    "type": "string",
                    "enum": ["left", "center", "right"]
                },
                "font_family": {"type": "string"},
                "font_size": {"type": "integer"},
                "bold": {"type": "boolean"},
                "italic": {"type": "boolean"},
                "underline": {"type": "boolean"},
                "strikeout": {"type": "boolean"},
                "style": {
                    "type": "string",
                    "enum": ["classic", "karaoke", "highlight", "underline", "word_by_word"]
                },
                "outline_width": {"type": "integer"},
                "spacing": {"type": "integer"},
                "angle": {"type": "integer"},
                "shadow_offset": {"type": "integer"}
            },
            "additionalProperties": False
        },
        "replace": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "find": {"type": "string"},
                    "replace": {"type": "string"}
                },
                "required": ["find", "replace"]
            }
        },
        "exclude_time_ranges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": { "type": "string" },
                    "end": { "type": "string" }
                },
                "required": ["start", "end"],
                "additionalProperties": False
            }
        },
        "webhook_url": {"type": "string", "format": "uri"},
        "id": {"type": "string"},
        "language": {"type": "string"}
    },
    "required": ["video_url"],
    "additionalProperties": False
})
def caption_video_v1():
    data = request.get_json()
    video_url = data['video_url']
    captions = data.get('captions')
    settings = data.get('settings', {})
    replace = data.get('replace', [])
    exclude_time_ranges = data.get('exclude_time_ranges', [])
    webhook_url = data.get('webhook_url')
    id = data.get('id')
    language = data.get('language', 'auto')
    
    # Generate a simple job ID for logging
    import uuid
    job_id = str(uuid.uuid4())[:8]

    # 十步法 - 第一步：請求接收與驗證
    logger.info(f"Job {job_id}: [步驟1/10] 請求接收與驗證 - 開始處理影片字幕請求")
    logger.info(f"Job {job_id}: [步驟1/10] 視頻URL: {video_url}")
    logger.info(f"Job {job_id}: [步驟1/10] 字幕內容: {'已提供' if captions else '未提供，將使用自動轉錄'}")
    logger.info(f"Job {job_id}: [步驟1/10] 語言設置: {language}")
    logger.info(f"Job {job_id}: [步驟1/10] 樣式設置: {settings}")
    logger.info(f"Job {job_id}: [步驟1/10] 文本替換規則: {replace}")
    logger.info(f"Job {job_id}: [步驟1/10] 排除時間範圍: {exclude_time_ranges}")
    logger.info(f"Job {job_id}: [步驟1/10] 請求驗證完成，準備調用核心服務")

    try:
        # Do NOT combine position and alignment. Keep them separate.
        # Just pass settings directly to process_captioning_v1.
        # This ensures position and alignment remain independent keys.
        
        # 十步法 - 第二步：核心字幕生成服務調用
        logger.info(f"Job {job_id}: [步驟2/10] 核心字幕生成服務調用 - 開始調用generate_ass_captions_v1")
        output = generate_ass_captions_v1(video_url, captions, settings, replace, exclude_time_ranges, job_id, language)
        logger.info(f"Job {job_id}: [步驟2/10] 核心服務調用完成")
        
        if isinstance(output, dict) and 'error' in output:
            # Check if this is a font-related error by checking for 'available_fonts' key
            if 'available_fonts' in output:
                # Font error scenario
                return jsonify({"error": output['error'], "available_fonts": output['available_fonts']}), 400
            else:
                # Non-font error scenario, do not return available_fonts
                return jsonify({"error": output['error']}), 400

        # If processing was successful, output is the ASS file path
        ass_path = output
        logger.info(f"Job {job_id}: [步驟8/10] 字幕文件生成完成 - ASS文件路徑: {ass_path}")

        # Prepare output filename and path for the rendered video
        output_filename = f"{job_id}_captioned.mp4"
        output_path = os.path.join(os.path.dirname(ass_path), output_filename)

        # 十步法 - 第三步：視頻文件下載（如果尚未本地化）
        video_path = None
        try:
            logger.info(f"Job {job_id}: [步驟3/10] 視頻文件下載 - 開始下載視頻文件")
            from services.file_management import download_file
            from config import LOCAL_STORAGE_PATH
            video_path = download_file(video_url, LOCAL_STORAGE_PATH)
            logger.info(f"Job {job_id}: [步驟3/10] 視頻下載完成 - 本地路徑: {video_path}")
        except Exception as e:
            logger.error(f"Job {job_id}: [步驟3/10] 視頻下載失敗: {str(e)}")
            return jsonify({"error": str(e)}), 500

        # 十步法 - 第九步：視頻渲染（FFmpeg處理）
        try:
            import ffmpeg
            logger.info(f"Job {job_id}: [步驟9/10] 視頻渲染 - 開始使用FFmpeg處理視頻")
            logger.info(f"Job {job_id}: [步驟9/10] 輸入視頻: {video_path}")
            logger.info(f"Job {job_id}: [步驟9/10] 字幕文件: {ass_path}")
            logger.info(f"Job {job_id}: [步驟9/10] 輸出路徑: {output_path}")
            
            # Get the directory containing the files
            video_dir = os.path.dirname(os.path.abspath(video_path))
            
            # Get relative filenames
            rel_video = os.path.basename(video_path)
            rel_ass = os.path.basename(ass_path)
            rel_output = os.path.basename(output_path)
            
            logger.info(f"Job {job_id}: Working directory: {video_dir}")
            logger.info(f"Job {job_id}: Relative paths - Video: {rel_video}, ASS: {rel_ass}, Output: {rel_output}")
            
            # Change to the directory containing the files and run FFmpeg with relative paths
            original_cwd = os.getcwd()
            try:
                os.chdir(video_dir)
                logger.info(f"Job {job_id}: Changed working directory to: {video_dir}")
                
                ffmpeg.input(rel_video).output(
                    rel_output,
                    vf=f"subtitles={rel_ass}",
                    acodec='copy'
                ).run(overwrite_output=True)
                
            finally:
                # Always restore original working directory
                os.chdir(original_cwd)
                logger.info(f"Job {job_id}: Restored working directory to: {original_cwd}")
            logger.info(f"Job {job_id}: [步驟9/10] FFmpeg處理完成 - 帶字幕視頻已生成: {output_path}")
        except Exception as e:
            logger.error(f"Job {job_id}: [步驟9/10] FFmpeg處理失敗: {str(e)}")
            return jsonify({"error": f"FFmpeg error: {str(e)}"}), 500

        # Clean up the ASS file after use
        os.remove(ass_path)

        # 十步法 - 第十步：響應返回
        logger.info(f"Job {job_id}: [步驟10/10] 響應返回 - 開始上傳到雲端存儲")
        cloud_url = upload_file(output_path)
        logger.info(f"Job {job_id}: [步驟10/10] 雲端上傳完成 - URL: {cloud_url}")

        # Clean up the output file after upload
        os.remove(output_path)
        logger.info(f"Job {job_id}: [步驟10/10] 本地文件清理完成")
        logger.info(f"Job {job_id}: [步驟10/10] 影片字幕處理流程全部完成！")

        return jsonify({
            "job_id": job_id,
            "response": cloud_url,
            "message": "success"
        }), 200

    except Exception as e:
        logger.error(f"Job {job_id}: Error during captioning process - {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
