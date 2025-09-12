#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

print("=== Flask應用路由調試 ===")
print(f"應用名稱: {app.name}")
print(f"註冊的藍圖數量: {len(app.blueprints)}")

print("\n=== 所有註冊的藍圖 ===")
for name, blueprint in app.blueprints.items():
    print(f"藍圖: {name} -> {blueprint}")
    if hasattr(blueprint, 'url_prefix'):
        print(f"  URL前綴: {blueprint.url_prefix}")

print("\n=== 所有路由 ===")
for rule in app.url_map.iter_rules():
    print(f"路由: {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")

print("\n=== 存儲相關路由 ===")
storage_routes = [rule for rule in app.url_map.iter_rules() if 'storage' in rule.rule]
for rule in storage_routes:
    print(f"存儲路由: {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")

print("\n=== 測試存儲管理藍圖 ===")
if 'storage_management' in app.blueprints:
    print("✅ 存儲管理藍圖已註冊")
    bp = app.blueprints['storage_management']
    print(f"藍圖URL前綴: {bp.url_prefix}")
else:
    print("❌ 存儲管理藍圖未註冊")

# 測試路由訪問
print("\n=== 測試路由訪問 ===")
with app.test_client() as client:
    # 測試健康檢查
    response = client.get('/health')
    print(f"健康檢查: {response.status_code} - {response.get_json()}")
    
    # 測試存儲狀態
    response = client.get('/api/v1/storage/status')
    print(f"存儲狀態: {response.status_code}")
    if response.status_code == 200:
        print(f"響應: {response.get_json()}")
    else:
        print(f"錯誤: {response.get_data(as_text=True)[:200]}")