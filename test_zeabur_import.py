#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 測試Zeabur環境導入問題 ===\n")

# 測試基本模塊
try:
    print("1. 測試基本Python模塊...")
    import logging
    import os
    import requests
    import uuid
    print("   ✅ 基本模塊導入成功")
except Exception as e:
    print(f"   ❌ 基本模塊導入失敗: {e}")

# 測試Flask
try:
    print("2. 測試Flask模塊...")
    from flask import Blueprint, jsonify, request
    print("   ✅ Flask模塊導入成功")
except Exception as e:
    print(f"   ❌ Flask模塊導入失敗: {e}")

# 測試app_utils
try:
    print("3. 測試app_utils...")
    from app_utils import validate_payload
    print("   ✅ app_utils導入成功")
except Exception as e:
    print(f"   ❌ app_utils導入失敗: {e}")

# 測試services模塊
services_modules = [
    ('services.ass_toolkit', 'generate_ass_captions_v1'),
    ('services.authentication', 'authenticate'),
    ('services.cloud_storage', 'upload_file'),
    ('services.file_management', 'download_file'),
    ('services.video_toolkit', None),
    ('services.font_toolkit', None)
]

for i, (module_name, function_name) in enumerate(services_modules, 4):
    try:
        print(f"{i}. 測試{module_name}...")
        if function_name:
            exec(f"from {module_name} import {function_name}")
        else:
            exec(f"import {module_name}")
        print(f"   ✅ {module_name}導入成功")
    except Exception as e:
        print(f"   ❌ {module_name}導入失敗: {e}")

# 測試FFmpeg相關
try:
    print("10. 測試ffmpeg-python...")
    import ffmpeg
    print("   ✅ ffmpeg-python導入成功")
except Exception as e:
    print(f"   ❌ ffmpeg-python導入失敗: {e}")

# 最後測試caption_video.py
try:
    print("11. 測試caption_video.py完整導入...")
    from routes.v1.video.caption_video import v1_video_caption_bp
    print(f"   ✅ caption_video.py導入成功")
    print(f"   藍圖名稱: {v1_video_caption_bp.name}")
    print(f"   藍圖URL前綴: {v1_video_caption_bp.url_prefix}")
except Exception as e:
    print(f"   ❌ caption_video.py導入失敗: {e}")
    import traceback
    print(f"   詳細錯誤: {traceback.format_exc()}")

print("\n=== 測試完成 ===")