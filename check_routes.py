#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import sys
import os

# 添加當前目錄到Python路徑
sys.path.insert(0, os.getcwd())

from flask import Flask
from app_utils import discover_and_register_blueprints

print("=== 檢查Flask應用路由 ===")

# 創建Flask應用並註冊藍圖
app = Flask(__name__)
blueprints = discover_and_register_blueprints(app)

print(f"\n註冊的藍圖數量: {len(blueprints)}")

# 獲取所有路由
with app.app_context():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': rule.rule
        })
    
    print(f"\n總路由數量: {len(routes)}")
    
    # 查找storage相關路由
    storage_routes = [r for r in routes if 'storage' in r['path'].lower() or 'storage' in r['endpoint'].lower()]
    print(f"\nStorage相關路由: {len(storage_routes)} 個")
    
    for route in storage_routes:
        methods_str = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
        print(f"  {route['path']} [{methods_str}] -> {route['endpoint']}")
    
    # 查找所有API路由
    api_routes = [r for r in routes if '/api/' in r['path']]
    print(f"\nAPI路由: {len(api_routes)} 個")
    
    for route in sorted(api_routes, key=lambda x: x['path']):
        methods_str = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
        print(f"  {route['path']} [{methods_str}] -> {route['endpoint']}")

print("\n=== 測試storage端點 ===")

# 測試storage端點
storage_endpoints = [
    'http://localhost:8080/api/v1/storage/usage',
    'http://localhost:8080/api/v1/storage/initialize',
    'http://localhost:8080/api/v1/storage/status'
]

for endpoint in storage_endpoints:
    try:
        response = requests.get(endpoint, timeout=5)
        print(f"✅ {endpoint} -> {response.status_code}")
        if response.status_code == 200:
            print(f"   響應: {response.text[:100]}...")
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint} -> 錯誤: {str(e)}")