#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from services.database_logger import database_logger
import os

def check_output_files():
    """檢查輸出文件的實際路徑"""
    files = database_logger.get_output_files(limit=10)
    
    print(f"找到 {len(files)} 個輸出文件記錄:")
    print("-" * 80)
    
    for i, file_info in enumerate(files, 1):
        file_id = file_info.get('file_id', 'N/A')
        file_path = file_info.get('file_path', 'N/A')
        file_type = file_info.get('file_type', 'N/A')
        filename = file_info.get('filename', 'N/A')
        
        print(f"{i}. 文件ID: {file_id}")
        print(f"   文件路徑: {file_path}")
        print(f"   文件類型: {file_type}")
        print(f"   文件名: {filename}")
        
        # 檢查文件是否存在
        if file_path != 'N/A' and os.path.exists(file_path):
            print(f"   ✅ 文件存在")
        else:
            print(f"   ❌ 文件不存在")
            
        print()

if __name__ == "__main__":
    check_output_files()