#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地音頻轉錄測試腳本
"""

import requests
import json
import os

def test_transcribe_with_local_file():
    """使用本地音頻文件測試轉錄功能"""
    
    # 查找本地可用的音頻文件
    test_files = [
        "d:/no-code-architects-toolkit/ffmpeg/tests/data/asynth-44100-2.wav",
        "d:/no-code-architects-toolkit/ffmpeg/tests/data/lavf/mp3/mp3-conformance/he_32khz.bit",
        "d:/no-code-architects-toolkit/ffmpeg/tests/data/lavf/mp3/mp3-conformance/he_44khz.bit",
    ]
    
    # 檢查文件是否存在
    available_file = None
    for file_path in test_files:
        if os.path.exists(file_path):
            available_file = file_path
            print(f"找到可用的測試文件: {file_path}")
            break
    
    if not available_file:
        print("未找到可用的測試音頻文件")
        return
    
    # 準備請求數據
    url = "http://localhost:5000/v1/media/transcribe"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "vidspark-production-api-key-2024-secure"
    }
    
    # 使用file://協議
    data = {
        "media_url": f"file:///{available_file.replace(os.sep, '/')}",
        "language": "auto",
        "include_text": True,
        "include_srt": False
    }
    
    print(f"測試URL: {data['media_url']}")
    print("發送轉錄請求...")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        print(f"響應狀態碼: {response.status_code}")
        print(f"響應內容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n=== 轉錄成功 ===")
            if 'text' in result:
                print(f"轉錄文本: {result['text']}")
            if 'status' in result:
                print(f"狀態: {result['status']}")
        else:
            print(f"\n=== 轉錄失敗 ===")
            print(f"錯誤: {response.text}")
            
    except Exception as e:
        print(f"請求失敗: {e}")

if __name__ == "__main__":
    test_transcribe_with_local_file()