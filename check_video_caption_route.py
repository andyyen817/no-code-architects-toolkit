#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

print("=== 檢查影片字幕路由 ===\n")

# 創建Flask應用
app = create_app()

print(f"應用名稱: {app.name}")
print(f"註冊的藍圖數量: {len(app.blueprints)}\n")

# 查找所有路由
all_routes = []
for rule in app.url_map.iter_rules():
    all_routes.append({
        'path': rule.rule,
        'methods': [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']],
        'endpoint': rule.endpoint
    })

print(f"總路由數量: {len(all_routes)}\n")

# 查找影片相關路由
video_routes = [r for r in all_routes if 'video' in r['path'].lower()]
print(f"=== 影片相關路由 ({len(video_routes)} 個) ===")
for route in sorted(video_routes, key=lambda x: x['path']):
    methods_str = ', '.join(route['methods'])
    print(f"{route['path']} [{methods_str}] -> {route['endpoint']}")

# 查找字幕相關路由
caption_routes = [r for r in all_routes if 'caption' in r['path'].lower()]
print(f"\n=== 字幕相關路由 ({len(caption_routes)} 個) ===")
for route in sorted(caption_routes, key=lambda x: x['path']):
    methods_str = ', '.join(route['methods'])
    print(f"{route['path']} [{methods_str}] -> {route['endpoint']}")

# 特別檢查 /v1/video/caption
target_route = '/v1/video/caption'
found_target = False
for route in all_routes:
    if route['path'] == target_route:
        found_target = True
        methods_str = ', '.join(route['methods'])
        print(f"\n✅ 找到目標路由: {route['path']} [{methods_str}] -> {route['endpoint']}")
        break

if not found_target:
    print(f"\n❌ 未找到目標路由: {target_route}")
    
    # 查找相似路由
    similar_routes = [r for r in all_routes if 'caption' in r['path'] and 'video' in r['path']]
    if similar_routes:
        print("\n相似路由:")
        for route in similar_routes:
            methods_str = ', '.join(route['methods'])
            print(f"  {route['path']} [{methods_str}] -> {route['endpoint']}")

# 檢查藍圖註冊
print(f"\n=== 藍圖註冊情況 ===")
for bp_name, bp in app.blueprints.items():
    if 'video' in bp_name.lower() or 'caption' in bp_name.lower():
        print(f"藍圖: {bp_name} (前綴: {bp.url_prefix})")

print("\n=== 檢查完成 ===")