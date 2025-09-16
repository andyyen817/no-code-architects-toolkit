#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import traceback

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# 添加當前目錄到路徑
cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

print(f"=== 測試Zeabur環境中caption_video.py導入問題 ===")
print(f"當前工作目錄: {cwd}")
print(f"Python版本: {sys.version}")
print(f"Python路徑: {sys.path[:3]}...")  # 只顯示前3個路徑

# 測試基本依賴
print(f"\n=== 測試基本依賴 ===")
try:
    import flask
    print(f"✅ Flask: {flask.__version__}")
except Exception as e:
    print(f"❌ Flask導入失敗: {e}")

try:
    import logging
    print(f"✅ logging模塊可用")
except Exception as e:
    print(f"❌ logging導入失敗: {e}")

# 測試app_utils
print(f"\n=== 測試app_utils ===")
try:
    import app_utils
    print(f"✅ app_utils導入成功")
except Exception as e:
    print(f"❌ app_utils導入失敗: {e}")
    traceback.print_exc()

# 測試services模塊
print(f"\n=== 測試services模塊 ===")
services_modules = [
    'services.ass_toolkit',
    'services.authentication', 
    'services.cloud_storage',
    'services.file_management'
]

for module_name in services_modules:
    try:
        module = __import__(module_name, fromlist=[''])
        print(f"✅ {module_name}導入成功")
    except Exception as e:
        print(f"❌ {module_name}導入失敗: {e}")

# 測試具體的函數導入
print(f"\n=== 測試具體函數導入 ===")
try:
    from services.ass_toolkit import generate_ass_captions_v1
    print(f"✅ generate_ass_captions_v1導入成功")
except Exception as e:
    print(f"❌ generate_ass_captions_v1導入失敗: {e}")
    traceback.print_exc()

try:
    from services.authentication import require_api_key
    print(f"✅ require_api_key導入成功")
except Exception as e:
    print(f"❌ require_api_key導入失敗: {e}")
    traceback.print_exc()

# 測試caption_video.py導入
print(f"\n=== 測試caption_video.py導入 ===")
try:
    # 先測試模塊導入
    import routes.v1.video.caption_video as caption_module
    print(f"✅ caption_video模塊導入成功")
    
    # 檢查藍圖
    if hasattr(caption_module, 'v1_video_caption_bp'):
        bp = caption_module.v1_video_caption_bp
        print(f"✅ 藍圖存在: {bp.name}")
        print(f"   URL前綴: {bp.url_prefix}")
        print(f"   藍圖類型: {type(bp)}")
    else:
        print(f"❌ 藍圖不存在")
        
except Exception as e:
    print(f"❌ caption_video導入失敗: {e}")
    traceback.print_exc()

# 測試Flask應用註冊
print(f"\n=== 測試Flask應用註冊 ===")
try:
    from flask import Flask
    app = Flask(__name__)
    
    # 嘗試導入並註冊藍圖
    from routes.v1.video.caption_video import v1_video_caption_bp
    app.register_blueprint(v1_video_caption_bp)
    print(f"✅ 藍圖註冊成功")
    
    # 檢查路由
    caption_routes = [rule for rule in app.url_map.iter_rules() if 'caption' in rule.rule]
    print(f"   註冊的caption路由數量: {len(caption_routes)}")
    for rule in caption_routes:
        print(f"   - {rule.rule} [{', '.join(rule.methods)}]")
        
except Exception as e:
    print(f"❌ Flask應用註冊失敗: {e}")
    traceback.print_exc()

print(f"\n=== 測試完成 ===")