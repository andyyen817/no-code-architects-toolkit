#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import importlib
import glob
from flask import Flask, Blueprint

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# 添加當前目錄到路徑
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

print(f"=== 測試Storage模塊導入問題 ===")
print(f"當前工作目錄: {cwd}")

# 測試直接導入storage_management模塊
print(f"\n=== 測試直接導入 ===")
try:
    from routes.v1.storage.storage_management import storage_management_bp
    print(f"✅ 直接導入成功: {storage_management_bp}")
    print(f"   URL前綴: {storage_management_bp.url_prefix}")
except Exception as e:
    print(f"❌ 直接導入失敗: {str(e)}")

# 測試使用importlib導入
print(f"\n=== 測試importlib導入 ===")
try:
    module = importlib.import_module('routes.v1.storage.storage_management')
    print(f"✅ importlib導入成功: {module}")
    
    # 查找藍圖
    import inspect
    for name, obj in inspect.getmembers(module):
        if isinstance(obj, Blueprint):
            print(f"   找到藍圖: {name} -> {obj}")
            print(f"   URL前綴: {obj.url_prefix}")
except Exception as e:
    print(f"❌ importlib導入失敗: {str(e)}")

# 模擬完整的藍圖發現過程
print(f"\n=== 模擬完整藍圖發現過程 ===")

base_dir = 'routes'
if not os.path.isabs(base_dir):
    base_dir = os.path.join(cwd, base_dir)

python_files = glob.glob(os.path.join(base_dir, '**', '*.py'), recursive=True)
print(f"找到 {len(python_files)} 個Python文件")

# 只處理storage相關文件
storage_files = [f for f in python_files if 'storage' in f]
print(f"\nStorage相關文件: {len(storage_files)} 個")

registered_blueprints = set()
failed_imports = []

for file_path in storage_files:
    try:
        # 轉換文件路徑為導入路徑
        rel_path = os.path.relpath(file_path, cwd)
        module_path = os.path.splitext(rel_path)[0]
        module_path = module_path.replace(os.path.sep, '.')
        
        print(f"\n🔍 處理: {module_path}")
        print(f"   文件: {file_path}")
        
        # 導入模塊
        module = importlib.import_module(module_path)
        print(f"   ✅ 導入成功")
        
        # 查找藍圖
        blueprints_found = 0
        for name, obj in inspect.getmembers(module):
            if isinstance(obj, Blueprint) and obj not in registered_blueprints:
                blueprints_found += 1
                registered_blueprints.add(obj)
                print(f"   📋 藍圖: {name} -> {obj}")
                print(f"      URL前綴: {obj.url_prefix}")
        
        if blueprints_found == 0:
            print(f"   ⚠️  沒有找到新藍圖")
            
    except Exception as e:
        failed_imports.append((module_path, str(e)))
        print(f"   ❌ 導入失敗: {str(e)}")

print(f"\n=== 結果總結 ===")
print(f"成功註冊藍圖: {len(registered_blueprints)} 個")
print(f"失敗導入: {len(failed_imports)} 個")

if failed_imports:
    print(f"\n失敗的導入:")
    for module_path, error in failed_imports:
        print(f"  - {module_path}: {error}")

# 測試Flask應用註冊
print(f"\n=== 測試Flask應用註冊 ===")
app = Flask(__name__)

for bp in registered_blueprints:
    try:
        app.register_blueprint(bp)
        print(f"✅ 註冊成功: {bp.name} ({bp.url_prefix})")
    except Exception as e:
        print(f"❌ 註冊失敗: {bp.name} - {str(e)}")

# 顯示所有註冊的路由
print(f"\n=== 註冊的路由 ===")
for rule in app.url_map.iter_rules():
    print(f"  {rule.methods} {rule.rule} -> {rule.endpoint}")