#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import importlib
import inspect
from flask import Flask, Blueprint

# Add current directory to path
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

app = Flask(__name__)
base_dir = 'routes'

print(f"=== 模擬藍圖發現過程 ===")
print(f"當前工作目錄: {cwd}")
print(f"基礎目錄: {base_dir}")

# 獲取絕對路徑
if not os.path.isabs(base_dir):
    base_dir = os.path.join(cwd, base_dir)

registered_blueprints = set()

# 查找所有Python文件
python_files = glob.glob(os.path.join(base_dir, '**', '*.py'), recursive=True)
print(f"\n找到 {len(python_files)} 個Python文件")

# 過濾storage相關文件
storage_files = [f for f in python_files if 'storage' in f]
print(f"\nStorage相關文件 ({len(storage_files)} 個):")
for f in storage_files:
    print(f"  {f}")

print(f"\n=== 開始處理所有Python文件 ===")

for file_path in python_files:
    try:
        # 轉換文件路徑為導入路徑
        rel_path = os.path.relpath(file_path, cwd)
        module_path = os.path.splitext(rel_path)[0]
        module_path = module_path.replace(os.path.sep, '.')
        
        # 只顯示storage相關的處理過程
        if 'storage' in module_path:
            print(f"\n處理模塊: {module_path}")
            print(f"  文件路徑: {file_path}")
            
            # 導入模塊
            module = importlib.import_module(module_path)
            print(f"  ✅ 模塊導入成功")
            
            # 查找藍圖實例
            blueprints_found = []
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, Blueprint) and obj not in registered_blueprints:
                    blueprints_found.append((name, obj))
                    registered_blueprints.add(obj)
                    print(f"  📋 註冊藍圖: {name} -> {obj}")
                    print(f"     URL前綴: {obj.url_prefix}")
                    
                    # 模擬註冊到Flask應用
                    try:
                        app.register_blueprint(obj)
                        print(f"     ✅ 成功註冊到Flask應用")
                    except Exception as reg_e:
                        print(f"     ❌ 註冊到Flask應用失敗: {reg_e}")
            
            if not blueprints_found:
                print(f"  ⚠️  在模塊中沒有找到新的藍圖")
                
    except Exception as e:
        if 'storage' in file_path:
            print(f"\n❌ 處理 {file_path} 時出錯:")
            print(f"   模塊路徑: {module_path}")
            print(f"   錯誤: {str(e)}")

print(f"\n=== 總結 ===")
print(f"總共註冊了 {len(registered_blueprints)} 個藍圖")

# 測試路由
print(f"\n=== 測試路由 ===")
with app.test_client() as client:
    test_urls = [
        '/api/v1/storage/status',
        '/storage/status',
        '/vidspark/storage/status'
    ]
    
    for url in test_urls:
        try:
            response = client.get(url)
            print(f"GET {url} -> {response.status_code}")
        except Exception as e:
            print(f"GET {url} -> 錯誤: {e}")

# 顯示所有註冊的路由
print(f"\n=== 所有註冊的路由 ===")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")