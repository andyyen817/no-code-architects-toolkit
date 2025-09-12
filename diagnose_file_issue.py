#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件訪問問題診斷工具
分析數據庫記錄與物理文件的對應關係

作者：AI助手
創建日期：2025-01-09
目的：診斷Zeabur生產環境文件訪問問題
"""

import os
import sys
import logging
from datetime import datetime

# 添加項目根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.database_logger import database_logger
except ImportError:
    print("❌ 無法導入database_logger，請確保數據庫服務可用")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose_file_access_issue():
    """
    診斷文件訪問問題
    """
    print("🔍 開始診斷文件訪問問題...")
    print("=" * 60)
    
    # 1. 檢查數據庫連接
    print("\n1️⃣ 檢查數據庫連接...")
    connection_test = database_logger.test_database_connection()
    if connection_test['available']:
        print("✅ 數據庫連接正常")
        print(f"   數據庫信息: {connection_test.get('info', 'N/A')}")
    else:
        print("❌ 數據庫連接失敗")
        print(f"   錯誤信息: {connection_test.get('error', 'N/A')}")
        return
    
    # 2. 檢查問題文件的數據庫記錄
    print("\n2️⃣ 檢查問題文件的數據庫記錄...")
    problem_files = [
        "2a8db855-85e8-4109-a46f-c78746c7bfe2.mp3",
        "289d6dc4-b2b2-42ed-a879-97a66f647130.mp4", 
        "5e04c8b3-401f-46f3-8c3f-64d657ee2ba4.mp4"
    ]
    
    working_files = [
        "43da9e1b-f938-432b-a334-991f16ba41c9.mp4",
        "43da9e1b-f938-432b-a334-991f16ba41c9_cut_084e20e0-6fea-4b95-b909-d58615868020.mp4"
    ]
    
    print("\n🔴 問題文件檢查:")
    for filename in problem_files:
        check_file_in_database(filename)
    
    print("\n🟢 正常文件檢查:")
    for filename in working_files:
        check_file_in_database(filename)
    
    # 3. 獲取最近的文件記錄
    print("\n3️⃣ 獲取最近的文件記錄...")
    try:
        uploaded_files = database_logger.get_uploaded_files(limit=10)
        output_files = database_logger.get_output_files(limit=10)
        
        print(f"\n📤 最近上傳文件 ({len(uploaded_files)} 條記錄):")
        for i, file_record in enumerate(uploaded_files[:5], 1):
            print(f"   {i}. {file_record.get('original_filename', 'N/A')}")
            print(f"      文件路徑: {file_record.get('file_path', 'N/A')}")
            print(f"      文件URL: {file_record.get('file_url', 'N/A')}")
            print(f"      上傳時間: {file_record.get('upload_time', 'N/A')}")
            print(f"      物理文件存在: {'✅' if os.path.exists(file_record.get('file_path', '')) else '❌'}")
            print()
        
        print(f"\n📥 最近輸出文件 ({len(output_files)} 條記錄):")
        for i, file_record in enumerate(output_files[:5], 1):
            print(f"   {i}. {file_record.get('original_filename', 'N/A')}")
            print(f"      文件路徑: {file_record.get('file_path', 'N/A')}")
            print(f"      文件URL: {file_record.get('file_url', 'N/A')}")
            print(f"      創建時間: {file_record.get('created_at', 'N/A')}")
            print(f"      操作類型: {file_record.get('operation_type', 'N/A')}")
            print(f"      物理文件存在: {'✅' if os.path.exists(file_record.get('file_path', '')) else '❌'}")
            print()
            
    except Exception as e:
        print(f"❌ 獲取文件記錄失敗: {str(e)}")
    
    # 4. 檢查存儲目錄結構
    print("\n4️⃣ 檢查存儲目錄結構...")
    check_storage_structure()
    
    # 5. 生成診斷報告
    print("\n5️⃣ 診斷總結...")
    generate_diagnosis_summary()

def check_file_in_database(filename):
    """
    檢查特定文件在數據庫中的記錄
    """
    try:
        # 檢查上傳文件表
        uploaded_files = database_logger.get_uploaded_files(limit=1000)
        output_files = database_logger.get_output_files(limit=1000)
        
        found_in_uploaded = False
        found_in_output = False
        
        # 在上傳文件中查找
        for file_record in uploaded_files:
            if filename in file_record.get('original_filename', '') or filename in file_record.get('file_path', ''):
                found_in_uploaded = True
                print(f"   📤 在上傳文件表中找到: {filename}")
                print(f"      文件ID: {file_record.get('file_id')}")
                print(f"      文件路徑: {file_record.get('file_path')}")
                print(f"      文件URL: {file_record.get('file_url')}")
                print(f"      上傳時間: {file_record.get('upload_time')}")
                print(f"      物理文件存在: {'✅' if os.path.exists(file_record.get('file_path', '')) else '❌'}")
                break
        
        # 在輸出文件中查找
        for file_record in output_files:
            if filename in file_record.get('original_filename', '') or filename in file_record.get('file_path', ''):
                found_in_output = True
                print(f"   📥 在輸出文件表中找到: {filename}")
                print(f"      文件ID: {file_record.get('file_id')}")
                print(f"      文件路徑: {file_record.get('file_path')}")
                print(f"      文件URL: {file_record.get('file_url')}")
                print(f"      創建時間: {file_record.get('created_at')}")
                print(f"      操作類型: {file_record.get('operation_type')}")
                print(f"      物理文件存在: {'✅' if os.path.exists(file_record.get('file_path', '')) else '❌'}")
                break
        
        if not found_in_uploaded and not found_in_output:
            print(f"   ❌ 未在數據庫中找到文件記錄: {filename}")
            
    except Exception as e:
        print(f"   ❌ 檢查文件記錄時出錯: {str(e)}")

def check_storage_structure():
    """
    檢查存儲目錄結構
    """
    base_paths = [
        './output',
        './output/nca',
        './output/nca/audio',
        './output/nca/video', 
        './output/nca/image',
        './temp'
    ]
    
    for path in base_paths:
        abs_path = os.path.abspath(path)
        exists = os.path.exists(abs_path)
        print(f"   {'✅' if exists else '❌'} {path} -> {abs_path}")
        
        if exists and os.path.isdir(abs_path):
            try:
                files = os.listdir(abs_path)
                print(f"      包含 {len(files)} 個項目")
                if len(files) > 0 and len(files) <= 5:
                    for file in files[:5]:
                        print(f"        - {file}")
                elif len(files) > 5:
                    for file in files[:3]:
                        print(f"        - {file}")
                    print(f"        ... 還有 {len(files) - 3} 個項目")
            except Exception as e:
                print(f"      ❌ 無法讀取目錄內容: {str(e)}")

def generate_diagnosis_summary():
    """
    生成診斷總結
    """
    print("\n📋 診斷總結:")
    print("   根據以上檢查結果，可能的問題原因包括:")
    print("   1. 🗄️ 數據庫記錄存在但物理文件丟失")
    print("   2. 🔄 Zeabur容器重啟導致臨時存儲清空")
    print("   3. 📁 文件存儲路徑配置不一致")
    print("   4. 🕒 文件自動清理機制觸發")
    print("   5. 💾 存儲空間不足導致文件丟失")
    
    print("\n🔧 建議解決方案:")
    print("   1. 檢查Zeabur持久化存儲配置")
    print("   2. 實施數據庫記錄與物理文件的一致性檢查")
    print("   3. 建立文件備份和恢復機制")
    print("   4. 配置適當的文件清理策略")
    print("   5. 監控存儲使用情況")

if __name__ == "__main__":
    try:
        diagnose_file_access_issue()
    except KeyboardInterrupt:
        print("\n\n⏹️ 診斷被用戶中斷")
    except Exception as e:
        print(f"\n\n❌ 診斷過程中發生錯誤: {str(e)}")
        logger.error(f"診斷錯誤: {str(e)}", exc_info=True)
    finally:
        print("\n" + "=" * 60)
        print(f"🏁 診斷完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")