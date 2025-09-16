#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
import sys
import os
import traceback
import importlib

debug_caption_bp = Blueprint('debug_caption', __name__)

@debug_caption_bp.route('/debug/caption/import', methods=['GET'])
def debug_caption_import():
    """調試caption_video.py導入問題"""
    result = {
        "python_version": sys.version,
        "python_path": sys.path[:5],  # 只顯示前5個路徑
        "current_dir": os.getcwd(),
        "tests": {}
    }
    
    # 測試基本依賴
    try:
        import flask
        result["tests"]["flask"] = {"status": "success", "version": str(flask.__version__)}
    except Exception as e:
        result["tests"]["flask"] = {"status": "error", "error": str(e)}
    
    # 測試app_utils
    try:
        import app_utils
        result["tests"]["app_utils"] = {"status": "success"}
    except Exception as e:
        result["tests"]["app_utils"] = {"status": "error", "error": str(e)}
    
    # 測試services.ass_toolkit
    try:
        from services.ass_toolkit import generate_ass_captions_v1
        result["tests"]["ass_toolkit"] = {"status": "success"}
    except Exception as e:
        result["tests"]["ass_toolkit"] = {"status": "error", "error": str(e)}
    
    # 測試services.authentication
    try:
        from services.authentication import authenticate
        result["tests"]["authentication"] = {"status": "success"}
    except Exception as e:
        result["tests"]["authentication"] = {"status": "error", "error": str(e)}
    
    # 測試services.cloud_storage
    try:
        from services.cloud_storage import upload_file
        result["tests"]["cloud_storage"] = {"status": "success"}
    except Exception as e:
        result["tests"]["cloud_storage"] = {"status": "error", "error": str(e)}
    
    # 測試caption_video模塊導入
    try:
        import routes.v1.video.caption_video as caption_module
        result["tests"]["caption_video_module"] = {"status": "success"}
        
        # 檢查藍圖
        if hasattr(caption_module, 'v1_video_caption_bp'):
            bp = caption_module.v1_video_caption_bp
            result["tests"]["caption_blueprint"] = {
                "status": "success",
                "name": bp.name,
                "url_prefix": bp.url_prefix,
                "type": str(type(bp))
            }
        else:
            result["tests"]["caption_blueprint"] = {
                "status": "error",
                "error": "Blueprint not found in module"
            }
            
    except Exception as e:
        result["tests"]["caption_video_module"] = {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        result["tests"]["caption_blueprint"] = {
            "status": "error",
            "error": "Module import failed"
        }
    
    # 檢查文件是否存在
    caption_file_path = os.path.join(os.getcwd(), 'routes', 'v1', 'video', 'caption_video.py')
    result["file_exists"] = os.path.exists(caption_file_path)
    result["file_path"] = caption_file_path
    
    if result["file_exists"]:
        try:
            with open(caption_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                result["file_size"] = len(content)
                result["file_lines"] = len(content.split('\n'))
        except Exception as e:
            result["file_read_error"] = str(e)
    
    return jsonify(result)

@debug_caption_bp.route('/debug/caption/manual-import', methods=['GET'])
def debug_manual_import():
    """手動測試導入過程"""
    result = {"steps": []}
    
    try:
        # 步驟1: 導入模塊
        result["steps"].append({"step": 1, "action": "Import module", "status": "attempting"})
        module = importlib.import_module('routes.v1.video.caption_video')
        result["steps"][-1]["status"] = "success"
        
        # 步驟2: 檢查藍圖
        result["steps"].append({"step": 2, "action": "Check blueprint", "status": "attempting"})
        if hasattr(module, 'v1_video_caption_bp'):
            bp = module.v1_video_caption_bp
            result["steps"][-1]["status"] = "success"
            result["steps"][-1]["blueprint_info"] = {
                "name": bp.name,
                "url_prefix": bp.url_prefix
            }
        else:
            result["steps"][-1]["status"] = "error"
            result["steps"][-1]["error"] = "Blueprint not found"
        
        # 步驟3: 嘗試註冊到Flask應用
        result["steps"].append({"step": 3, "action": "Register to Flask", "status": "attempting"})
        from flask import Flask
        test_app = Flask(__name__)
        test_app.register_blueprint(bp)
        result["steps"][-1]["status"] = "success"
        
        # 檢查註冊的路由
        routes = []
        for rule in test_app.url_map.iter_rules():
            if 'caption' in rule.rule:
                routes.append({
                    "rule": rule.rule,
                    "methods": list(rule.methods),
                    "endpoint": rule.endpoint
                })
        result["registered_routes"] = routes
        
    except Exception as e:
        if result["steps"]:
            result["steps"][-1]["status"] = "error"
            result["steps"][-1]["error"] = str(e)
            result["steps"][-1]["traceback"] = traceback.format_exc()
        else:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
    
    return jsonify(result)