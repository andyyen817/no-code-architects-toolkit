#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

try:
    from app import app
    
    print("=== Flask應用路由檢查 ===")
    print(f"應用名稱: {app.name}")
    print(f"註冊的藍圖數量: {len(app.blueprints)}")
    
    print("\n=== 註冊的藍圖 ===")
    for bp_name, bp in app.blueprints.items():
        print(f"藍圖: {bp_name} (前綴: {bp.url_prefix})")
    
    print("\n=== 所有路由 ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
    
    print("\n=== 存儲相關路由 ===")
    storage_routes = [rule for rule in app.url_map.iter_rules() if 'storage' in rule.rule]
    for rule in storage_routes:
        print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
    
    # 測試直接訪問
    print("\n=== 測試路由訪問 ===")
    with app.test_client() as client:
        response = client.get('/api/v1/storage/status')
        print(f"狀態碼: {response.status_code}")
        print(f"響應: {response.get_data(as_text=True)[:200]}")
        
except Exception as e:
    print('錯誤:', str(e))
    import traceback
    traceback.print_exc()