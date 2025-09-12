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

print(f"=== 調試Storage藍圖註冊問題 ===")
print(f"當前工作目錄: {cwd}")

base_dir = 'routes'
if not os.path.isabs(base_dir):
    base_dir = os.path.join(cwd, base_dir)

print(f"基礎目錄: {base_dir}")

# 查找所有Python文件
python_files = glob.glob(os.path.join(base_dir, '**', '*.py'), recursive=True)
print(f"\n找到 {len(python_files)} 個Python文件")

# 過濾storage相關文件
storage_files = [f for f in python_files if 'storage' in f]
print(f"\nStorage相關文件:")
for i, f in enumerate(storage_files, 1):
    rel_path = os.path.relpath(f, cwd)
    module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
    print(f"  {i}. {f}")
    print(f"     模塊路徑: {module_path}")

# 檢查v1目錄下的所有文件
v1_files = [f for f in python_files if 'v1' in f]
print(f"\nV1目錄下的文件 ({len(v1_files)} 個):")
for i, f in enumerate(v1_files, 1):
    rel_path = os.path.relpath(f, cwd)
    module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
    if 'storage' in f:
        print(f"  {i}. ⭐ {f} (STORAGE)")
        print(f"     模塊路徑: {module_path}")
    else:
        print(f"  {i}. {f}")

print(f"\n=== 模擬藍圖發現過程 ===")

# 模擬完整的藍圖發現過程
registered_blueprints = set()
processed_modules = []

for file_path in python_files:
    try:
        # 轉換文件路徑為導入路徑
        rel_path = os.path.relpath(file_path, cwd)
        module_path = os.path.splitext(rel_path)[0]
        module_path = module_path.replace(os.path.sep, '.')
        
        processed_modules.append(module_path)
        
        # 只顯示storage相關的處理過程
        if 'storage' in module_path:
            print(f"\n🔍 處理模塊: {module_path}")
            print(f"   文件路徑: {file_path}")
            
            # 導入模塊
            module = importlib.import_module(module_path)
            print(f"   ✅ 模塊導入成功")
            
            # 查找藍圖實例
            blueprints_found = []
            for name, obj in inspect.getmembers(module):
                if isinstance(obj, Blueprint) and obj not in registered_blueprints:
                    blueprints_found.append((name, obj))
                    registered_blueprints.add(obj)
                    print(f"   📋 找到藍圖: {name} -> {obj}")
                    print(f"      URL前綴: {obj.url_prefix}")
            
            if not blueprints_found:
                print(f"   ⚠️  在模塊中沒有找到新的藍圖")
                
    except Exception as e:
        if 'storage' in file_path:
            print(f"\n❌ 處理 {file_path} 時出錯:")
            print(f"   模塊路徑: {module_path}")
            print(f"   錯誤: {str(e)}")

print(f"\n=== 檢查是否遺漏了storage模塊 ===")
storage_modules = [m for m in processed_modules if 'storage' in m]
print(f"處理的storage模塊: {storage_modules}")

expected_storage_modules = [
    'routes.vidspark_storage',
    'routes.v1.storage.storage_management',
    'routes.v1.storage.__init__'
]

print(f"\n預期的storage模塊: {expected_storage_modules}")

for expected in expected_storage_modules:
    if expected in processed_modules:
        print(f"✅ {expected} - 已處理")
    else:
        print(f"❌ {expected} - 未處理")

print(f"\n=== 總結 ===")
print(f"總共處理了 {len(processed_modules)} 個模塊")
print(f"總共註冊了 {len(registered_blueprints)} 個藍圖")