#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雲端測試頁面路由配置
為Flask應用添加測試頁面路由
"""

from flask import Blueprint, send_file, jsonify, request, current_app
import os
import json
import sys
import traceback
import importlib
import importlib.util
from datetime import datetime

# Try to import pymysql with fallback
try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False
    print("Warning: PyMySQL not available - database features disabled")

# 創建測試藍圖
test_bp = Blueprint('test', __name__, url_prefix='/test')

# 數據庫配置
DB_CONFIG = {
    'host': 'tpe1.clusters.zeabur.com',
    'port': 30791,
    'user': 'root',
    'password': '248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6',
    'database': 'zeabur',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """獲取數據庫連接"""
    if not PYMYSQL_AVAILABLE:
        return None
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        current_app.logger.error(f"數據庫連接失敗: {str(e)}")
        return None

# 測試頁面路由
@test_bp.route('/nca')
def nca_test_page():
    """No-Code Architects Toolkit 測試頁面 - 修復版"""
    try:
        file_path = os.path.join(current_app.root_path, 'test-pages', 'nca_cloud_test_fixed.html')
        return send_file(file_path, mimetype='text/html')
    except Exception as e:
        return jsonify({'error': f'頁面載入失敗: {str(e)}'}), 500

@test_bp.route('/nca-original')
def nca_test_page_original():
    """No-Code Architects Toolkit 測試頁面 - 原版（有問題）"""
    try:
        file_path = os.path.join(current_app.root_path, 'test-pages', 'nca_cloud_test.html')
        return send_file(file_path, mimetype='text/html')
    except Exception as e:
        return jsonify({'error': f'頁面載入失敗: {str(e)}'}), 500

@test_bp.route('/ffmpeg')
def ffmpeg_test_page():
    """FFMPEG 測試頁面"""
    try:
        file_path = os.path.join(current_app.root_path, 'test-pages', 'ffmpeg_cloud_test.html')
        return send_file(file_path, mimetype='text/html')
    except Exception as e:
        return jsonify({'error': f'頁面載入失敗: {str(e)}'}), 500

@test_bp.route('/genhuman')
def genhuman_test_page():
    """GenHuman API 測試頁面"""
    try:
        file_path = os.path.join(current_app.root_path, 'test-pages', 'genhuman_cloud_test.html')
        return send_file(file_path, mimetype='text/html')
    except Exception as e:
        return jsonify({'error': f'頁面載入失敗: {str(e)}'}), 500

# 路由檢查API
@test_bp.route('/routes')
def list_all_routes():
    """顯示所有註冊的路由"""
    try:
        routes = []
        for rule in current_app.url_map.iter_rules():
            routes.append({
                'path': rule.rule,
                'methods': [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']],
                'endpoint': rule.endpoint
            })
        
        # 按路徑排序
        routes.sort(key=lambda x: x['path'])
        
        return jsonify({
            'success': True,
            'total_routes': len(routes),
            'routes': routes,
            'blueprints': list(current_app.blueprints.keys())
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 測試數據API路由
@test_bp.route('/api/record', methods=['POST'])
def record_test_result():
    """記錄測試結果到數據庫"""
    try:
        data = request.get_json()
        
        required_fields = ['test_type', 'test_function', 'test_endpoint', 'test_status', 'execution_time_ms']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必需字段: {field}'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': '數據庫連接失敗'}), 500
        
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO nca_test_records 
                (test_type, test_function, test_endpoint, input_data, output_data, 
                 test_status, error_message, execution_time_ms, file_urls, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data['test_type'],
                    data['test_function'],
                    data['test_endpoint'],
                    json.dumps(data.get('input_data')),
                    json.dumps(data.get('output_data')),
                    data['test_status'],
                    data.get('error_message'),
                    data['execution_time_ms'],
                    json.dumps(data.get('file_urls', [])),
                    datetime.now()
                )
                
                cursor.execute(sql, values)
                connection.commit()
                record_id = cursor.lastrowid
                
                return jsonify({
                    'success': True,
                    'record_id': record_id,
                    'message': '測試結果記錄成功'
                })
                
        finally:
            connection.close()
            
    except Exception as e:
        current_app.logger.error(f"測試結果記錄失敗: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@test_bp.route('/api/whisper/record', methods=['POST'])
def record_whisper_result():
    """記錄Whisper測試結果到專用表"""
    try:
        data = request.get_json()
        
        required_fields = ['media_type', 'media_url', 'transcribed_text', 'processing_time_seconds']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必需字段: {field}'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': '數據庫連接失敗'}), 500
        
        try:
            with connection.cursor() as cursor:
                # 先創建測試記錄
                test_record_sql = """
                INSERT INTO nca_test_records 
                (test_type, test_function, test_endpoint, test_status, execution_time_ms, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(test_record_sql, (
                    'whisper',
                    f"whisper_{data['media_type']}_transcribe",
                    f"/v1/{'media' if data['media_type'] == 'audio' else 'video'}/{'transcribe' if data['media_type'] == 'audio' else 'caption'}",
                    'success',
                    int(data['processing_time_seconds'] * 1000),
                    datetime.now()
                ))
                
                test_record_id = cursor.lastrowid
                
                # 再創建Whisper專用記錄
                whisper_sql = """
                INSERT INTO nca_whisper_results 
                (test_record_id, media_type, media_url, transcribed_text, srt_content, 
                 language, model_used, processing_time_seconds, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(whisper_sql, (
                    test_record_id,
                    data['media_type'],
                    data['media_url'],
                    data['transcribed_text'],
                    data.get('srt_content'),
                    data.get('language', 'zh'),
                    data.get('model_used', 'tiny'),
                    data['processing_time_seconds'],
                    datetime.now()
                ))
                
                connection.commit()
                whisper_record_id = cursor.lastrowid
                
                return jsonify({
                    'success': True,
                    'record_id': whisper_record_id,
                    'test_record_id': test_record_id,
                    'message': 'Whisper測試結果記錄成功'
                })
                
        finally:
            connection.close()
            
    except Exception as e:
        current_app.logger.error(f"Whisper測試結果記錄失敗: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@test_bp.route('/api/ffmpeg/record', methods=['POST'])
def record_ffmpeg_result():
    """記錄FFMPEG測試結果到專用表"""
    try:
        data = request.get_json()
        
        required_fields = ['operation_type', 'input_file_url', 'processing_time_seconds', 'test_status']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必需字段: {field}'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': '數據庫連接失敗'}), 500
        
        try:
            with connection.cursor() as cursor:
                # 創建測試記錄
                test_record_sql = """
                INSERT INTO nca_test_records 
                (test_type, test_function, test_endpoint, test_status, execution_time_ms, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(test_record_sql, (
                    'ffmpeg',
                    f"ffmpeg_{data['operation_type']}",
                    f"/api/ffmpeg/{data['operation_type']}",
                    data['test_status'],
                    int(data['processing_time_seconds'] * 1000),
                    datetime.now()
                ))
                
                test_record_id = cursor.lastrowid
                
                # 創建FFMPEG專用記錄
                ffmpeg_sql = """
                INSERT INTO nca_ffmpeg_results 
                (test_record_id, operation_type, input_file_url, output_file_url, 
                 ffmpeg_command, processing_time_seconds, file_size_before, file_size_after, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(ffmpeg_sql, (
                    test_record_id,
                    data['operation_type'],
                    data['input_file_url'],
                    data.get('output_file_url'),
                    data.get('ffmpeg_command'),
                    data['processing_time_seconds'],
                    data.get('file_size_before', 0),
                    data.get('file_size_after', 0),
                    datetime.now()
                ))
                
                connection.commit()
                ffmpeg_record_id = cursor.lastrowid
                
                return jsonify({
                    'success': True,
                    'record_id': ffmpeg_record_id,
                    'test_record_id': test_record_id,
                    'message': 'FFMPEG測試結果記錄成功'
                })
                
        finally:
            connection.close()
            
    except Exception as e:
        current_app.logger.error(f"FFMPEG測試結果記錄失敗: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@test_bp.route('/api/genhuman/record', methods=['POST'])
def record_genhuman_result():
    """記錄GenHuman測試結果到專用表"""
    try:
        data = request.get_json()
        
        required_fields = ['api_type', 'task_id', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必需字段: {field}'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': '數據庫連接失敗'}), 500
        
        try:
            with connection.cursor() as cursor:
                # 創建測試記錄
                test_record_sql = """
                INSERT INTO nca_test_records 
                (test_type, test_function, test_endpoint, test_status, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                cursor.execute(test_record_sql, (
                    'genhuman',
                    f"genhuman_{data['api_type']}",
                    f"/api/genhuman/{data['api_type']}",
                    'success' if data['status'] in ['processing', 'completed'] else 'failed',
                    datetime.now()
                ))
                
                test_record_id = cursor.lastrowid
                
                # 創建GenHuman專用記錄
                genhuman_sql = """
                INSERT INTO nca_genhuman_results 
                (test_record_id, api_type, task_id, request_data, callback_data, 
                 status, result_url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(genhuman_sql, (
                    test_record_id,
                    data['api_type'],
                    data['task_id'],
                    json.dumps(data.get('request_data')),
                    json.dumps(data.get('callback_data')),
                    data['status'],
                    data.get('result_url'),
                    datetime.now()
                ))
                
                connection.commit()
                genhuman_record_id = cursor.lastrowid
                
                return jsonify({
                    'success': True,
                    'record_id': genhuman_record_id,
                    'test_record_id': test_record_id,
                    'message': 'GenHuman測試結果記錄成功'
                })
                
        finally:
            connection.close()
            
    except Exception as e:
        current_app.logger.error(f"GenHuman測試結果記錄失敗: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@test_bp.route('/api/history')
def get_test_history():
    """獲取測試歷史統計"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': '數據庫連接失敗'}), 500
        
        try:
            with connection.cursor() as cursor:
                # 獲取總體統計
                stats_sql = """
                SELECT 
                    test_type,
                    COUNT(*) as total,
                    SUM(CASE WHEN test_status = 'success' THEN 1 ELSE 0 END) as success,
                    AVG(execution_time_ms) as avg_time
                FROM nca_test_records 
                GROUP BY test_type
                """
                
                cursor.execute(stats_sql)
                stats = cursor.fetchall()
                
                # 獲取最近的測試記錄
                recent_sql = """
                SELECT test_type, test_function, test_status, execution_time_ms, created_at
                FROM nca_test_records 
                ORDER BY created_at DESC 
                LIMIT 10
                """
                
                cursor.execute(recent_sql)
                recent_tests = cursor.fetchall()
                
                return jsonify({
                    'success': True,
                    'stats': [
                        {
                            'test_type': stat[0],
                            'total': stat[1],
                            'success': stat[2],
                            'success_rate': (stat[2] / stat[1] * 100) if stat[1] > 0 else 0,
                            'avg_time': float(stat[3]) if stat[3] else 0
                        }
                        for stat in stats
                    ],
                    'recent_tests': [
                        {
                            'test_type': test[0],
                            'test_function': test[1],
                            'test_status': test[2],
                            'execution_time_ms': test[3],
                            'created_at': test[4].strftime('%Y-%m-%d %H:%M:%S')
                        }
                        for test in recent_tests
                    ],
                    'total_tests': sum(stat[1] for stat in stats)
                })
                
        finally:
            connection.close()
            
    except Exception as e:
        current_app.logger.error(f"測試歷史獲取失敗: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@test_bp.route('/api/status')
def get_test_status():
    """獲取測試系統狀態"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'error': '數據庫連接失敗'}), 500
        
        try:
            with connection.cursor() as cursor:
                # 檢查今日測試統計
                today_sql = """
                SELECT 
                    COUNT(*) as total_today,
                    SUM(CASE WHEN test_status = 'success' THEN 1 ELSE 0 END) as success_today
                FROM nca_test_records 
                WHERE DATE(created_at) = CURDATE()
                """
                
                cursor.execute(today_sql)
                today_stats = cursor.fetchone()
                
                # 檢查各個測試模塊狀態
                module_sql = """
                SELECT 
                    test_type,
                    COUNT(*) as count,
                    MAX(created_at) as last_test
                FROM nca_test_records 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
                GROUP BY test_type
                """
                
                cursor.execute(module_sql)
                module_stats = cursor.fetchall()
                
                return jsonify({
                    'success': True,
                    'status': 'healthy',
                    'today_tests': today_stats[0] if today_stats else 0,
                    'today_success': today_stats[1] if today_stats else 0,
                    'today_success_rate': (today_stats[1] / today_stats[0] * 100) if today_stats and today_stats[0] > 0 else 0,
                    'active_modules': [
                        {
                            'module': module[0],
                            'tests_last_hour': module[1],
                            'last_test': module[2].strftime('%Y-%m-%d %H:%M:%S')
                        }
                        for module in module_stats
                    ],
                    'database_connected': True,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
        finally:
            connection.close()
            
    except Exception as e:
        current_app.logger.error(f"測試狀態獲取失敗: {str(e)}")
        return jsonify({
            'success': False, 
            'status': 'error',
            'error': str(e),
            'database_connected': False,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500

# 註冊測試藍圖到Flask應用的函數
def register_test_routes(app):
    """註冊測試路由到Flask應用"""
    app.register_blueprint(test_bp)
    app.logger.info("測試路由已註冊")
    
    # 添加測試頁面主入口
    @app.route('/test')
    def test_index():
        """測試中心主頁"""
        html_content = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>No-Code Architects Toolkit 測試中心</title>
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 40px 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                .container {
                    background: rgba(255,255,255,0.95);
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }
                h1 {
                    text-align: center;
                    color: #2c3e50;
                    margin-bottom: 30px;
                    font-size: 2.5em;
                }
                .test-cards {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 30px;
                    margin-top: 40px;
                }
                .test-card {
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    text-align: center;
                    transition: transform 0.3s ease;
                }
                .test-card:hover {
                    transform: translateY(-5px);
                }
                .test-card h3 {
                    color: #2c3e50;
                    margin-bottom: 15px;
                }
                .test-card p {
                    color: #7f8c8d;
                    margin-bottom: 20px;
                }
                .test-btn {
                    display: inline-block;
                    padding: 12px 25px;
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    transition: all 0.3s ease;
                    font-weight: 600;
                }
                .test-btn:hover {
                    background: linear-gradient(135deg, #2980b9, #1abc9c);
                    transform: translateY(-2px);
                }
                .status-indicator {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #27ae60;
                    margin-right: 8px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛠️ No-Code Architects Toolkit 測試中心</h1>
                <p style="text-align: center; font-size: 1.2em; color: #7f8c8d;">
                    <span class="status-indicator"></span>
                    ZEABUR雲端環境 | 完整功能測試 | MySQL數據持久化
                </p>
                
                <div class="test-cards">
                    <div class="test-card">
                        <h3>🛠️ NCA Toolkit 測試</h3>
                        <p>音頻處理、視頻處理、圖像處理、文件管理等核心功能測試</p>
                        <a href="/test/nca" class="test-btn">開始測試</a>
                    </div>
                    
                    <div class="test-card">
                        <h3>🎬 FFMPEG 測試</h3>
                        <p>音視頻格式轉換、剪切、壓縮、縮略圖生成等專業功能測試</p>
                        <a href="/test/ffmpeg" class="test-btn">開始測試</a>
                    </div>
                    
                    <div class="test-card">
                        <h3>🤖 GenHuman API 測試</h3>
                        <p>聲音克隆、數字人克隆、語音合成、視頻生成等AI功能測試</p>
                        <a href="/test/genhuman" class="test-btn">開始測試</a>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                    <h4>🔗 快速連結</h4>
                    <p>
                        <a href="/health" style="margin: 0 15px;">健康檢查</a> |
                        <a href="/test/api/status" style="margin: 0 15px;">測試狀態</a> |
                        <a href="/test/api/history" style="margin: 0 15px;">測試歷史</a>
                    </p>
                </div>
            </div>
            
            <script>
                // 檢查服務狀態
                fetch('/test/api/status')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            console.log('測試系統狀態正常:', data);
                        }
                    })
                    .catch(error => console.error('測試系統狀態檢查失敗:', error));
            </script>
        </body>
        </html>
        """
        return html_content

@test_bp.route('/import/caption', methods=['GET'])
def test_caption_import():
    """測試caption_video模組的導入"""
    results = {
        'test_timestamp': datetime.now().isoformat(),
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
            'blueprint_name': str(getattr(caption_module, 'v1_video_caption_bp', None)),
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
            'blueprint_name': str(getattr(simple_module, 'v1_video_caption_simple_bp', None)),
            'module_attributes': [attr for attr in dir(simple_module) if not attr.startswith('_')]
        }
    except Exception as e:
        results['caption_video_simple_import'] = {
            'status': 'failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    
    return jsonify(results)

@test_bp.route('/original/caption/debug', methods=['GET'])
def debug_original_caption():
    """詳細測試原始caption_video模組的導入問題"""
    results = {
        'test_timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'step_by_step_import': {}
    }
    
    # 逐步測試導入
    import_steps = [
        ('flask', 'from flask import Blueprint, jsonify, request'),
        ('app_utils', 'from app_utils import validate_payload'),
        ('logging', 'import logging'),
        ('services.ass_toolkit', 'from services.ass_toolkit import generate_ass_file'),
        ('services.authentication', 'from services.authentication import authenticate'),
        ('services.cloud_storage', 'from services.cloud_storage import upload_to_cloud, download_from_cloud'),
        ('os', 'import os'),
        ('requests', 'import requests')
    ]
    
    for step_name, import_statement in import_steps:
        try:
            exec(import_statement)
            results['step_by_step_import'][step_name] = {
                'status': 'success',
                'import_statement': import_statement,
                'error': None
            }
        except Exception as e:
            results['step_by_step_import'][step_name] = {
                'status': 'failed',
                'import_statement': import_statement,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    # 嘗試導入整個模組
    try:
        # 先嘗試導入模組但不執行
        import importlib.util
        import os as os_module
        file_path = os_module.path.join(os_module.getcwd(), 'routes', 'v1', 'video', 'caption_video.py')
        spec = importlib.util.spec_from_file_location(
            "caption_video", 
            file_path
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            results['full_module_import'] = {
                'status': 'success',
                'blueprint_found': hasattr(module, 'v1_video_caption_bp'),
                'module_attributes': [attr for attr in dir(module) if not attr.startswith('_')]
            }
        else:
            results['full_module_import'] = {
                'status': 'failed',
                'error': 'Could not create module spec',
                'file_path': file_path
            }
    except Exception as e:
        results['full_module_import'] = {
            'status': 'failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    
    # 檢查services模組的具體問題
    services_tests = [
        'services.ass_toolkit',
        'services.authentication',
        'services.cloud_storage'
    ]
    
    results['services_detailed'] = {}
    for service in services_tests:
        try:
            module = importlib.import_module(service)
            results['services_detailed'][service] = {
                'status': 'success',
                'attributes': [attr for attr in dir(module) if not attr.startswith('_')][:10]  # 限制輸出
            }
        except Exception as e:
            results['services_detailed'][service] = {
                'status': 'failed',
                'error': str(e)
            }
    
    return jsonify(results)
