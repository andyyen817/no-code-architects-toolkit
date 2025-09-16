#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

print("=== 檢查本地路由註冊情況 ===\n")

# 創建Flask應用
app = create_app()

print(f"應用名稱: {app.name}")
print(f"註冊的藍圖數量: {len(app.blueprints)}\n")

# 顯示所有註冊的藍圖
print("=== 註冊的藍圖 ===")
for name, blueprint in app.blueprints.items():
    print(f"藍圖: {name} -> {blueprint}")
    if hasattr(blueprint, 'url_prefix'):
        print(f"  URL前綴: {blueprint.url_prefix}")
print()

# 查找所有路由
all_routes = []
for rule in app.url_map.iter_rules():
    all_routes.append({
        'path': rule.rule,
        'methods': [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']],
        'endpoint': rule.endpoint
    })

print(f"總路由數量: {len(all_routes)}\n")

# 查找影片字幕相關路由
video_caption_routes = [r for r in all_routes if 'video' in r['path'].lower() and 'caption' in r['path'].lower()]
print(f"=== 影片字幕相關路由 ({len(video_caption_routes)} 個) ===")
for route in sorted(video_caption_routes, key=lambda x: x['path']):
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

# 檢查v1_video_caption藍圖
if 'v1_video_caption' in app.blueprints:
    print(f"\n✅ v1_video_caption藍圖已註冊")
    bp = app.blueprints['v1_video_caption']
    print(f"藍圖URL前綴: {bp.url_prefix}")
else:
    print(f"\n❌ v1_video_caption藍圖未註冊")

print("\n=== 所有路由列表 ===")
for route in sorted(all_routes, key=lambda x: x['path']):
    methods_str = ', '.join(route['methods'])
    print(f"{route['path']} [{methods_str}] -> {route['endpoint']}")