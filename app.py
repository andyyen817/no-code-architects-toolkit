#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zeabur 主應用程序 v2.0
統一的Flask應用啟動和路由管理
"""

# 首先加载.env文件，在任何其他导入之前
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)  # 使用override=True覆盖现有环境变量
except ImportError:
    pass

import os
import sys
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("环境变量文件加载成功")

# 導入配置和管理器
from config import get_app_config, get_app_info
from database_manager import get_database_manager, reset_database_manager
from storage_management import register_storage_routes
from app_utils import discover_and_register_blueprints

# 重置数据库管理器以使用新的环境变量
reset_database_manager()
logger.info("数据库管理器已重置，将使用新的环境变量")

def create_app():
    """創建Flask應用實例"""
    app = Flask(__name__)
    
    # 加載配置
    config = get_app_config()
    app.config.update(config.get_flask_config())
    
    # 配置CORS
    if config.security_config['cors_enabled']:
        CORS(app, origins=config.security_config['cors_origins'])
        logger.info(f"CORS已啟用 - 允許來源: {config.security_config['cors_origins']}")
    
    # 註冊路由
    register_routes(app)
    
    # 註冊存儲路由
    try:
        register_storage_routes(app)
        logger.info("存儲路由註冊成功")
    except Exception as e:
        logger.error(f"存儲路由註冊失敗: {e}")
    
    # 動態發現和註冊藍圖
    try:
        blueprints = discover_and_register_blueprints(app)
        logger.info(f"動態註冊了 {len(blueprints)} 個藍圖")
    except Exception as e:
        logger.error(f"動態藍圖註冊失敗: {e}")
    
    # 初始化數據庫（可選）
    try:
        from database_manager import get_database_manager, init_database_tables
        db_manager = get_database_manager()
        if db_manager.initialize_pool():
            if init_database_tables(db_manager):
                logger.info("數據庫初始化成功")
            else:
                logger.warning("數據庫表初始化失敗，但連接池正常")
        else:
            logger.warning("數據庫連接池初始化失敗，應用將在無數據庫模式下運行")
    except Exception as e:
        logger.warning(f"數據庫初始化失敗，應用將在無數據庫模式下運行: {e}")
        # 在開發環境下不退出，允許無數據庫運行
        pass
    
    logger.info(f"Flask應用創建成功 - 環境: {config.app_config['environment']}")
    return app

def register_routes(app):
    """註冊基礎路由"""
    
    @app.route('/', methods=['GET'])
    def index():
        """首頁"""
        app_info = get_app_info()
        return jsonify({
            'message': 'No-Code Architects Toolkit API',
            'version': app_info['version'],
            'environment': app_info['environment'],
            'status': 'running',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康檢查端點"""
        try:
            # 檢查數據庫連接
            db_manager = get_database_manager()
            db_status = db_manager.health_check()
            
            app_info = get_app_info()
            
            is_healthy = db_status.get('connected', False)
            
            health_data = {
                'status': 'healthy' if is_healthy else 'unhealthy',
                'build': 200,
                'fix': 'zeabur-deployment-v2.0',
                'timestamp': datetime.now().isoformat(),
                'app': {
                    'name': app_info['name'],
                    'version': app_info['version'],
                    'environment': app_info['environment']
                },
                'database': db_status,
                'uptime': 'running'
            }
            
            # 在無數據庫模式下仍返回200，因為應用本身是健康的
            return jsonify(health_data), 200
            
        except Exception as e:
            logger.error(f"健康檢查失敗: {e}")
            return jsonify({
                'status': 'unhealthy',
                'build': 500,
                'fix': 'zeabur-deployment-v2.0',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/v1/info', methods=['GET'])
    def api_info():
        """API信息端點"""
        config = get_app_config()
        return jsonify({
            'api': {
                'version': 'v1',
                'name': 'No-Code Architects Toolkit API',
                'description': 'Unified API for no-code development tools'
            },
            'app': get_app_info(),
            'config_summary': config.get_config_summary(),
            'endpoints': {
                'health': '/health',
                'storage': '/api/v1/storage',
                'info': '/api/v1/info'
            },
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/v1/status', methods=['GET'])
    def api_status():
        """API狀態端點"""
        try:
            db_manager = get_database_manager()
            db_status = db_manager.check_health()
            
            return jsonify({
                'api_status': 'operational',
                'database': db_status,
                'storage': 'operational',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"狀態檢查失敗: {e}")
            return jsonify({
                'api_status': 'degraded',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 503
    
    @app.errorhandler(404)
    def not_found(error):
        """404錯誤處理"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404,
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500錯誤處理"""
        logger.error(f"內部服務器錯誤: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal server error occurred',
            'status_code': 500,
            'timestamp': datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        """文件過大錯誤處理"""
        return jsonify({
            'error': 'File Too Large',
            'message': 'The uploaded file exceeds the maximum allowed size',
            'status_code': 413,
            'timestamp': datetime.now().isoformat()
        }), 413
    
    logger.info("基礎路由註冊完成")

def main():
    """主函數"""
    try:
        # 創建應用
        app = create_app()
        config = get_app_config()
        
        # 顯示啟動信息
        app_info = get_app_info()
        logger.info(f"="*50)
        logger.info(f"🚀 {app_info['name']} {app_info['version']}")
        logger.info(f"環境: {app_info['environment']}")
        logger.info(f"調試模式: {app_info['debug']}")
        logger.info(f"服務器: {config.app_config['host']}:{config.app_config['port']}")
        logger.info(f"="*50)
        
        # 啟動應用
        app.run(
            host=config.app_config['host'],
            port=config.app_config['port'],
            debug=config.app_config['debug'],
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("應用被用戶中斷")
    except Exception as e:
        logger.error(f"應用啟動失敗: {e}")
        sys.exit(1)
    finally:
        # 清理資源
        try:
            db_manager = get_database_manager()
            db_manager.close_all_connections()
            logger.info("數據庫連接已關閉")
        except Exception as e:
            logger.error(f"清理資源時出錯: {e}")

if __name__ == '__main__':
    main()