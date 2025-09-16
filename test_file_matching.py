#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試文件路徑匹配邏輯
模擬 nca_files.py 中的文件匹配功能
"""

import os
import tempfile
import shutil
from pathlib import Path

def test_file_matching():
    """測試文件匹配邏輯"""
    
    # 創建臨時測試目錄結構
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
        
        for filename in test_files:
            file_path = os.path.join(test_date_dir, filename)
            Path(file_path).touch()
            print(f"📁 創建測試文件: {filename}")
        
        # 測試場景：尋找不存在的精確文件名
        target_file = "2025/09/0e99ec62-cba5-4cad-b652-88d810253486.mp4"
        print(f"\n🎯 測試目標: {target_file}")
        
        # 模擬文件匹配邏輯
        normalized_file_path = target_file.replace('/', os.sep)
        
        # 1. 嘗試精確匹配
        potential_paths = [
            ("標準路徑", os.path.join(nca_storage_dir, normalized_file_path)),
            ("直接路徑", os.path.join(nca_storage_dir, os.path.basename(normalized_file_path))),
            ("舊版路徑", os.path.join(output_dir, "video", normalized_file_path)),
            ("根目錄路徑", os.path.join(output_dir, normalized_file_path))
        ]
        
        found_file_path = None
        found_strategy = None
        
        print("\n🔍 嘗試精確匹配:")
        for strategy, path in potential_paths:
            print(f"  檢查{strategy}: {path}")
            if os.path.exists(path):
                found_file_path = path
                found_strategy = strategy
                print(f"  ✅ 找到文件 - {strategy}")
                break
            else:
                print(f"  ❌ 文件不存在 - {strategy}")
        
        # 2. 如果精確匹配失敗，嘗試前綴匹配
        if not found_file_path:
            print("\n🔍 精確匹配失敗，嘗試前綴匹配...")
            
            # 提取原始文件名
            original_filename = os.path.splitext(os.path.basename(normalized_file_path))[0]
            file_extension = os.path.splitext(normalized_file_path)[1]
            
            print(f"  原始文件名: {original_filename}")
            print(f"  擴展名: {file_extension}")
            
            # 搜索目錄
            search_directories = [
                nca_storage_dir,
                os.path.join(output_dir, "video"),
                output_dir
            ]
            
            for search_dir in search_directories:
                if not os.path.exists(search_dir):
                    continue
                    
                print(f"  🔍 搜索目錄: {search_dir}")
                
                # 檢查目錄及其子目錄
                for root, dirs, files in os.walk(search_dir):
                    for filename in files:
                        # 檢查文件是否以原始文件名開頭且有相同擴展名
                        if (filename.startswith(original_filename) and 
                            filename.endswith(file_extension) and 
                            filename != os.path.basename(normalized_file_path)):
                            
                            candidate_path = os.path.join(root, filename)
                            print(f"    🔍 找到前綴匹配文件: {filename}")
                            
                            # 驗證這是一個有效的變體
                            valid_suffixes = ['_trim_', '_cut_', '_process_', '_convert_', '_captioned']
                            if any(suffix in filename for suffix in valid_suffixes):
                                found_file_path = candidate_path
                                found_strategy = f"前綴匹配 ({os.path.relpath(search_dir, output_dir)})"
                                print(f"    ✅ 前綴匹配成功 - {found_strategy}")
                                print(f"    📁 文件路徑: {found_file_path}")
                                break
                    
                    if found_file_path:
                        break
                
                if found_file_path:
                    break
        
        # 結果
        if found_file_path:
            print(f"\n🎉 測試成功！")
            print(f"策略: {found_strategy}")
            print(f"找到文件: {found_file_path}")
            return True
        else:
            print(f"\n❌ 測試失敗：未找到匹配文件")
            return False

if __name__ == "__main__":
    print("🧪 開始測試文件匹配邏輯...")
    success = test_file_matching()
    print(f"\n📊 測試結果: {'通過' if success else '失敗'}")