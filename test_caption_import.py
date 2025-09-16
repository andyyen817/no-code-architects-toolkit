#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 測試caption_video.py模塊導入 ===\n")

try:
    print("1. 測試導入Flask相關模塊...")
    from flask import Blueprint, jsonify, request
    print("   ✅ Flask模塊導入成功")
except Exception as e:
    print(f"   ❌ Flask模塊導入失敗: {e}")
    sys.exit(1)

try:
    print("2. 測試導入app_utils...")
    from app_utils import validate_payload
    print("   ✅ app_utils導入成功")
except Exception as e:
    print(f"   ❌ app_utils導入失敗: {e}")

try:
    print("3. 測試導入services.ass_toolkit...")
    from services.ass_toolkit import generate_ass_captions_v1
    print("   ✅ services.ass_toolkit導入成功")
except Exception as e:
    print(f"   ❌ services.ass_toolkit導入失敗: {e}")

try:
    print("4. 測試導入services.authentication...")
    from services.authentication import authenticate
    print("   ✅ services.authentication導入成功")
except Exception as e:
    print(f"   ❌ services.authentication導入失敗: {e}")

try:
    print("5. 測試導入services.cloud_storage...")
    from services.cloud_storage import upload_file
    print("   ✅ services.cloud_storage導入成功")
except Exception as e:
    print(f"   ❌ services.cloud_storage導入失敗: {e}")

try:
    print("6. 測試導入caption_video.py模塊...")
    from routes.v1.video.caption_video import v1_video_caption_bp
    print(f"   ✅ caption_video.py模塊導入成功")
    print(f"   藍圖名稱: {v1_video_caption_bp.name}")
    print(f"   藍圖URL前綴: {v1_video_caption_bp.url_prefix}")
except Exception as e:
    print(f"   ❌ caption_video.py模塊導入失敗: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 測試完成 ===")