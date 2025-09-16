from flask import Blueprint, jsonify
import sys
import traceback
import importlib
import os

debug_import_bp = Blueprint('debug_import', __name__)

@debug_import_bp.route('/debug/import-errors', methods=['GET'])
def check_import_errors():
    """檢查所有藍圖文件的導入錯誤"""
    results = []
    routes_dir = 'routes'
    
    # 獲取所有Python文件
    for root, dirs, files in os.walk(routes_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py' and not file.endswith('.disabled'):
                file_path = os.path.join(root, file)
                module_path = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                
                try:
                    # 嘗試導入模組
                    module = importlib.import_module(module_path)
                    
                    # 檢查是否有藍圖
                    blueprint_found = False
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if hasattr(attr, 'name') and hasattr(attr, 'url_map'):
                            blueprint_found = True
                            break
                    
                    results.append({
                        'file': file_path,
                        'module': module_path,
                        'status': 'success',
                        'blueprint_found': blueprint_found,
                        'error': None
                    })
                    
                except Exception as e:
                    results.append({
                        'file': file_path,
                        'module': module_path,
                        'status': 'error',
                        'blueprint_found': False,
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    })
    
    # 統計
    total_files = len(results)
    success_count = len([r for r in results if r['status'] == 'success'])
    error_count = len([r for r in results if r['status'] == 'error'])
    blueprint_count = len([r for r in results if r['blueprint_found']])
    
    return jsonify({
        'status': 'success',
        'summary': {
            'total_files': total_files,
            'successful_imports': success_count,
            'failed_imports': error_count,
            'blueprints_found': blueprint_count
        },
        'results': results
    })