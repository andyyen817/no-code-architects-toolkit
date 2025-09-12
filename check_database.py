#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def check_uploaded_files():
    """檢查上傳文件記錄"""
    print("=== 檢查數據庫中的文件記錄 ===")
    
    try:
        response = requests.get(
            'http://localhost:5000/v1/files/list?limit=50',
            headers={'X-API-Key': 'final-working-2024'}
        )
        
        print(f"API響應狀態: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            print(f"\n找到 {len(files)} 個文件記錄:")
            print("-" * 80)
            
            for i, file in enumerate(files, 1):
                print(f"{i}. 文件名: {file.get('original_filename', 'N/A')}")
                print(f"   類型: {file.get('file_type', 'N/A')}")
                print(f"   大小: {file.get('file_size_mb', 'N/A')} MB")
                print(f"   上傳時間: {file.get('upload_time', 'N/A')}")
                print(f"   文件URL: {file.get('file_url', 'N/A')}")
                print(f"   文件ID: {file.get('file_id', 'N/A')}")
                print("-" * 40)
        else:
            print(f"錯誤: {response.text}")
            
    except Exception as e:
        print(f"檢查失敗: {e}")

def check_output_files():
    """檢查輸出文件記錄"""
    print("\n=== 檢查輸出文件記錄 ===")
    
    try:
        response = requests.get(
            'http://localhost:5000/v1/files/output/list?limit=50',
            headers={'X-API-Key': 'final-working-2024'}
        )
        
        print(f"API響應狀態: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            print(f"\n找到 {len(files)} 個輸出文件記錄:")
            print("-" * 80)
            
            for i, file in enumerate(files, 1):
                print(f"{i}. 文件名: {file.get('filename', 'N/A')}")
                print(f"   操作類型: {file.get('operation_type', 'N/A')}")
                print(f"   大小: {file.get('file_size_mb', 'N/A')} MB")
                print(f"   創建時間: {file.get('created_at', 'N/A')}")
                print(f"   文件URL: {file.get('file_url', 'N/A')}")
                print(f"   文件ID: {file.get('file_id', 'N/A')}")
                print("-" * 40)
        else:
            print(f"錯誤: {response.text}")
            
    except Exception as e:
        print(f"檢查失敗: {e}")

def test_file_urls():
    """測試問題文件URL的可訪問性"""
    print("\n=== 測試問題文件URL ===")
    
    problem_urls = [
        "https://vidsparkback.zeabur.app/nca/files/audio/2025/09/2a8db855-85e8-4109-a46f-c78746c7bfe2.mp3",
        "https://vidsparkback.zeabur.app/nca/files/video/2025/09/43da9e1b-f938-432b-a334-991f16ba41c9.mp4",
        "https://vidsparkback.zeabur.app/nca/files/video/2025/09/43da9e1b-f938-432b-a334-991f16ba41c9_cut_084e20e0-6fea-4b95-b909-d58615868020.mp4"
    ]
    
    for url in problem_urls:
        try:
            response = requests.head(url, timeout=10)
            print(f"URL: {url}")
            print(f"狀態: {response.status_code}")
            if response.status_code != 200:
                # 嘗試GET請求獲取更多信息
                get_response = requests.get(url, timeout=10)
                print(f"GET響應: {get_response.status_code}")
                if get_response.status_code >= 400:
                    print(f"錯誤內容: {get_response.text[:200]}")
            print("-" * 40)
        except Exception as e:
            print(f"URL: {url}")
            print(f"錯誤: {e}")
            print("-" * 40)

if __name__ == "__main__":
    check_uploaded_files()
    check_output_files()
    test_file_urls()