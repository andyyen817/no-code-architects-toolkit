#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試導入調試腳本
用於檢查Zeabur環境中caption_video.py的導入問題
"""

import sys
import traceback
import importlib
from flask import Flask, Blueprint, jsonify

# 創建測試藍圖
test_import_bp = Blueprint('test_import', __name__, url_prefix='/test')

@test_import_bp.route('/import/caption', methods=['GET'])
def test_caption_import():
    """測試caption_video模組的導入"""
    results = {
        'test_timestamp': '2025-01-27',
        'python_version': sys.version,
        'import_tests': {}
    }
    
    # 測試基本依賴
    test_modules = [
        'flask',
        'os',
        'requests',
        'logging',
        'app_utils',
        'services.ass_toolkit',
        'services.authentication', 
        'services.cloud_storage'
    ]
    
    for module_name in test_modules:
        try:
            importlib.import_module(module_name)
            results['import_tests'][module_name] = {
                'status': 'success',
                'error': None
            }
        except Exception as e:
            results['import_tests'][module_name] = {
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    # 測試caption_video模組導入
    try:
        caption_module = importlib.import_module('routes.v1.video.caption_video')
        results['caption_video_import'] = {
            'status': 'success',
            'blueprint_name': getattr(caption_module, 'v1_video_caption_bp', None),
            'module_attributes': [attr for attr in dir(caption_module) if not attr.startswith('_')]
        }
    except Exception as e:
        results['caption_video_import'] = {
            'status': 'failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    
    # 測試簡化版caption模組導入
    try:
        simple_module = importlib.import_module('routes.v1.video.caption_video_simple')
        results['caption_video_simple_import'] = {
            'status': 'success',
            'blueprint_name': getattr(simple_module, 'v1_video_caption_simple_bp', None),
            'module_attributes': [attr for attr in dir(simple_module) if not attr.startswith('_')]
        }
    except Exception as e:
        results['caption_video_simple_import'] = {
            'status': 'failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    
    return jsonify(results)

if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(test_import_bp)
    app.run(debug=True)