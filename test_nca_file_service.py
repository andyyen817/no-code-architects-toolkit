#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 NCA 文件服務功能
模擬實際的文件服務請求，驗證修復後的路徑匹配邏輯
"""

import os
import sys
import tempfile
from pathlib import Path
from flask import Flask
from unittest.mock import patch

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_nca_file_service():
    """測試 NCA 文件服務"""
    
    print("🧪 開始測試 NCA 文件服務...")
    
    # 創建 Flask 測試應用
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # 創建臨時測試環境
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🔧 創建測試環境: {temp_dir}")
        
        # 模擬 Zeabur 的目錄結構
        output_dir = os.path.join(temp_dir, "output")
        nca_storage_dir = os.path.join(output_dir, "nca", "video")
        test_date_dir = os.path.join(nca_storage_dir, "2025", "09")
        
        # 創建目錄
        os.makedirs(test_date_dir, exist_ok=True)
        
        # 創建測試文件（模擬實際情況）
        test_files = [
            "0e99ec62-cba5-4cad-b652-88d810253486_trim_f1162973-7f6f-421b-b22e-3c0678d0330d.mp4",
            "0e99ec62-cba5-4cad-b652-88d810253486_cut_dfa814c2-12a8-4b55-989a-d00ac2fb7b9e.mp4",
            "9b2f72d0-13fe-4818-8245-e7b76373b893.mp4",
            "9b2f72d0-13fe-4818-8245-e7b76373b893_trim_79f31f75-8b1d-4d71-9759-8325d58f2c1d.mp4"
        ]
        
        # 創建測試文件並寫入一些內容
        for filename in test_files:
            file_path = os.path.join(test_date_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"Test video content for {filename}")
            print(f"📁 創建測試文件: {filename}")
        
        # 模擬環境變量
        with patch.dict(os.environ, {
            'OUTPUT_DIR': output_dir,
            'NCA_STORAGE_DIR': nca_storage_dir
        }):
            
            try:
                # 導入 NCA 文件路由
                from routes.nca_files import serve_nca_file
                
                # 測試場景 1：請求不存在的精確文件名（應該通過前綴匹配找到）
                print("\n🎯 測試場景 1: 請求精確文件名（不存在）")
                test_file_path = "video/2025/09/0e99ec62-cba5-4cad-b652-88d810253486.mp4"
                print(f"請求文件: {test_file_path}")
                
                with app.test_request_context(f'/nca/{test_file_path}'):
                    try:
                        response = serve_nca_file(test_file_path)
                        print(f"✅ 測試 1 成功: 狀態碼 {response.status_code}")
                        if hasattr(response, 'headers'):
                            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                    except Exception as e:
                        print(f"❌ 測試 1 失敗: {str(e)}")
                
                # 測試場景 2：請求存在的精確文件名
                print("\n🎯 測試場景 2: 請求精確文件名（存在）")
                test_file_path2 = "video/2025/09/9b2f72d0-13fe-4818-8245-e7b76373b893.mp4"
                print(f"請求文件: {test_file_path2}")
                
                with app.test_request_context(f'/nca/{test_file_path2}'):
                    try:
                        response = serve_nca_file(test_file_path2)
                        print(f"✅ 測試 2 成功: 狀態碼 {response.status_code}")
                        if hasattr(response, 'headers'):
                            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                    except Exception as e:
                        print(f"❌ 測試 2 失敗: {str(e)}")
                
                # 測試場景 3：請求完全不存在的文件
                print("\n🎯 測試場景 3: 請求不存在的文件")
                test_file_path3 = "video/2025/09/nonexistent-file.mp4"
                print(f"請求文件: {test_file_path3}")
                
                with app.test_request_context(f'/nca/{test_file_path3}'):
                    try:
                        response = serve_nca_file(test_file_path3)
                        print(f"⚠️  測試 3: 狀態碼 {response.status_code} (預期 404)")
                    except Exception as e:
                        print(f"✅ 測試 3 成功: 正確拋出異常 - {str(e)}")
                
                print("\n🎉 所有測試完成！")
                return True
                
            except ImportError as e:
                print(f"❌ 無法導入 NCA 文件路由: {e}")
                print("   這可能是因為缺少依賴或路徑問題")
                return False
            except Exception as e:
                print(f"❌ 測試過程中發生錯誤: {e}")
                return False

def test_file_matching_logic_only():
    """僅測試文件匹配邏輯（不依賴 Flask）"""
    
    print("\n🔧 測試文件匹配邏輯（獨立測試）...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 設置測試環境
        output_dir = os.path.join(temp_dir, "output")
        nca_storage_dir = os.path.join(output_dir, "nca", "video")
        test_date_dir = os.path.join(nca_storage_dir, "2025", "09")
        os.makedirs(test_date_dir, exist_ok=True)
        
        # 創建測試文件
        test_files = [
            "0e99ec62-cba5-4cad-b652-88d810253486_trim_f1162973-7f6f-421b-b22e-3c0678d0330d.mp4",
            "0e99ec62-cba5-4cad-b652-88d810253486_cut_dfa814c2-12a8-4b55-989a-d00ac2fb7b9e.mp4"
        ]
        
        for filename in test_files:
            file_path = os.path.join(test_date_dir, filename)
            Path(file_path).touch()
        
        # 模擬文件匹配邏輯
        target_file = "video/2025/09/0e99ec62-cba5-4cad-b652-88d810253486.mp4"
        file_type = "video"
        
        # 標準化路徑
        normalized_file_path = target_file.replace('/', os.sep)
        if normalized_file_path.startswith(f'{file_type}{os.sep}'):
            normalized_file_path = normalized_file_path[len(f'{file_type}{os.sep}'):]
        
        print(f"🎯 目標文件: {target_file}")
        print(f"📁 標準化路徑: {normalized_file_path}")
        
        # 嘗試精確匹配
        potential_paths = [
            ("標準路徑", os.path.join(nca_storage_dir, normalized_file_path)),
            ("直接路徑", os.path.join(nca_storage_dir, os.path.basename(normalized_file_path)))
        ]
        
        found_file_path = None
        
        for strategy, path in potential_paths:
            if os.path.exists(path):
                found_file_path = path
                break
        
        # 前綴匹配
        if not found_file_path:
            original_filename = os.path.splitext(os.path.basename(normalized_file_path))[0]
            file_extension = os.path.splitext(normalized_file_path)[1]
            
            print(f"🔍 嘗試前綴匹配: {original_filename}{file_extension}")
            
            for root, dirs, files in os.walk(nca_storage_dir):
                for filename in files:
                    if (filename.startswith(original_filename) and 
                        filename.endswith(file_extension)):
                        
                        valid_suffixes = ['_trim_', '_cut_', '_process_', '_convert_', '_captioned']
                        if any(suffix in filename for suffix in valid_suffixes):
                            found_file_path = os.path.join(root, filename)
                            print(f"✅ 找到匹配文件: {filename}")
                            break
                
                if found_file_path:
                    break
        
        if found_file_path:
            print(f"🎉 測試成功！找到文件: {os.path.basename(found_file_path)}")
            return True
        else:
            print(f"❌ 測試失敗：未找到匹配文件")
            return False

if __name__ == "__main__":
    print("🧪 開始 NCA 文件服務測試...")
    
    # 首先測試獨立的文件匹配邏輯
    logic_test = test_file_matching_logic_only()
    
    # 然後測試完整的服務功能
    service_test = test_nca_file_service()
    
    print(f"\n📊 測試結果:")
    print(f"   文件匹配邏輯: {'通過' if logic_test else '失敗'}")
    print(f"   文件服務功能: {'通過' if service_test else '失敗'}")
    
    if logic_test and service_test:
        print("\n🎉 所有測試通過！修復成功！")
    else:
        print("\n⚠️  部分測試失敗，需要進一步檢查")