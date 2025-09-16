#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to check the status of optional dependencies
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

print("=== Testing Optional Dependencies Import Status ===")

# Test whisper
try:
    import whisper
    print("✅ whisper: Available")
except ImportError as e:
    print(f"❌ whisper: Not available - {e}")

# Test playwright
try:
    import playwright
    print("✅ playwright: Available")
except ImportError as e:
    print(f"❌ playwright: Not available - {e}")

# Test yt_dlp
try:
    import yt_dlp
    print("✅ yt_dlp: Available")
except ImportError as e:
    print(f"❌ yt_dlp: Not available - {e}")

# Test boto3
try:
    import boto3
    print("✅ boto3: Available")
except ImportError as e:
    print(f"❌ boto3: Not available - {e}")

print("\n=== Testing Service Modules with Conditional Imports ===")

# Test transcription service
try:
    from services.transcription import WHISPER_AVAILABLE
    print(f"✅ services.transcription: WHISPER_AVAILABLE = {WHISPER_AVAILABLE}")
except ImportError as e:
    print(f"❌ services.transcription: Import failed - {e}")

# Test screenshot service
try:
    from routes.v1.image.screenshot_webpage import PLAYWRIGHT_AVAILABLE
    print(f"✅ routes.v1.image.screenshot_webpage: PLAYWRIGHT_AVAILABLE = {PLAYWRIGHT_AVAILABLE}")
except ImportError as e:
    print(f"❌ routes.v1.image.screenshot_webpage: Import failed - {e}")

# Test download service
try:
    from routes.v1.media.download import YT_DLP_AVAILABLE
    print(f"✅ routes.v1.media.download: YT_DLP_AVAILABLE = {YT_DLP_AVAILABLE}")
except ImportError as e:
    print(f"❌ routes.v1.media.download: Import failed - {e}")

# Test S3 upload service
try:
    from services.v1.s3.upload import BOTO3_AVAILABLE
    print(f"✅ services.v1.s3.upload: BOTO3_AVAILABLE = {BOTO3_AVAILABLE}")
except ImportError as e:
    print(f"❌ services.v1.s3.upload: Import failed - {e}")

print("\n=== Summary ===")
print("All modules with conditional imports should load successfully even if optional dependencies are missing.")
print("The *_AVAILABLE flags indicate whether the optional functionality is enabled.")