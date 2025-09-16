#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終字幕生成功能測試
驗證前端修復後的字幕生成功能
"""

import requests
import json
import time

def test_caption_with_correct_font():
    """測試使用正確字體的字幕生成"""
    url = "https://vidsparkback.zeabur.app/v1/video/caption"
    headers = {
        "X-API-Key": "vidspark-production-api-key-2024-secure",
        "Content-Type": "application/json"
    }
    
    # 使用與前端相同的請求格式
    test_data = {
        "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_720x480_1mb.mp4",
        "captions": "Hello World Test Caption",
        "settings": {
            "font_family": "DejaVu Sans",
            "font_size": 24,
            "position": "bottom_center",
            "alignment": "center"
        }
    }
    
    print("=== 測試修復後的字幕生成功能 ===")
    print(f"URL: {url}")
    print(f"請求數據: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    print("\n發送請求...")
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=test_data, timeout=60)
        end_time = time.time()
        
        print(f"\n響應時間: {end_time - start_time:.2f}秒")
        print(f"HTTP狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 字幕生成成功！")
            try:
                result = response.json()
                print(f"響應內容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True
            except:
                print(f"響應內容 (文本): {response.text}")
                return True
        elif response.status_code == 400:
            print(f"❌ 字幕生成失敗 - HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"錯誤詳情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                
                # 檢查是否還是字體錯誤
                if "Font" in str(error_data) and "Arial" in str(error_data):
                    print("\n🔍 仍然存在Arial字體錯誤，前端修復可能未生效")
                    return False
                elif "available_fonts" in error_data:
                    print("\n🔍 字體相關錯誤，但不是Arial問題")
                    print(f"可用字體: {error_data.get('available_fonts', [])}")
                    return False
                else:
                    print("\n🔍 非字體相關錯誤")
                    return False
            except:
                print(f"錯誤響應 (文本): {response.text}")
                return False
        else:
            print(f"❌ 意外的HTTP狀態碼: {response.status_code}")
            print(f"響應內容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 請求超時")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 連接錯誤")
        return False
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        return False

def test_health_check():
    """測試服務健康狀態"""
    url = "https://vidsparkback.zeabur.app/health"
    
    print("\n=== 健康檢查 ===")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ 服務健康狀態正常")
            return True
        else:
            print(f"❌ 服務健康檢查失敗 - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康檢查錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("字幕生成功能最終測試")
    print("=" * 50)
    
    # 健康檢查
    health_ok = test_health_check()
    
    if not health_ok:
        print("\n❌ 服務不可用，無法進行測試")
        exit(1)
    
    # 測試字幕生成
    caption_ok = test_caption_with_correct_font()
    
    print("\n=== 最終測試結果 ===")
    print(f"健康檢查: {'✅ 通過' if health_ok else '❌ 失敗'}")
    print(f"字幕生成: {'✅ 通過' if caption_ok else '❌ 失敗'}")
    
    if health_ok and caption_ok:
        print("\n🎉 所有測試通過！字幕生成功能修復成功！")
        print("\n修復內容總結:")
        print("1. ✅ 後端已安裝matplotlib依賴和DejaVu字體")
        print("2. ✅ 前端測試頁面已更新，使用DejaVu Sans字體")
        print("3. ✅ 字幕生成API正常工作")
        print("\n現在可以正常使用字幕生成功能了！")
    else:
        print("\n❌ 測試失敗，需要進一步檢查")
    
    print("\n=== 測試完成 ===")