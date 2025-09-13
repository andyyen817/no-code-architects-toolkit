#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zeabur 統一配置管理器 v2.0
集中管理所有環境變量和應用配置
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppConfig:
    """應用配置管理器"""
    
    def __init__(self):
        self._load_config()
        self._validate_config()
        
    def _load_config(self):
        """加載配置"""
        # 基礎應用配置
        self.app_config = {
            'name': os.getenv('APP_NAME', 'no-code-architects-toolkit'),
            'version': os.getenv('APP_VERSION', 'v2.0'),
            'environment': os.getenv('ENVIRONMENT', 'production'),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'host': os.getenv('HOST', '0.0.0.0'),
            'port': int(os.getenv('PORT', '8080')),
            'api_key': os.getenv('API_KEY', 'vidspark-production-api-key-2024-secure'),
            'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-here')
        }
        
        # 數據庫配置
        self.database_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'username': os.getenv('DB_USERNAME', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_DATABASE', 'toolkit_db'),
            'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
            'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
            'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
            'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
            'autocommit': os.getenv('DB_AUTOCOMMIT', 'true').lower() == 'true'
        }
        
        # 存儲配置
        self.storage_config = {
            'upload_folder': os.getenv('STORAGE_UPLOAD_FOLDER', './uploads'),
            'max_file_size': int(os.getenv('STORAGE_MAX_FILE_SIZE', '100')) * 1024 * 1024,  # MB to bytes
            'allowed_extensions': os.getenv('STORAGE_ALLOWED_EXTENSIONS', 
                'txt,pdf,png,jpg,jpeg,gif,mp4,mp3,wav,doc,docx,xls,xlsx,ppt,pptx').split(','),
            'cleanup_days': int(os.getenv('STORAGE_CLEANUP_DAYS', '30')),
            'enable_compression': os.getenv('STORAGE_ENABLE_COMPRESSION', 'false').lower() == 'true',
            'compression_quality': int(os.getenv('STORAGE_COMPRESSION_QUALITY', '85'))
        }
        
        # 日誌配置
        self.logging_config = {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'file_path': os.getenv('LOG_FILE_PATH', './logs/app.log'),
            'max_file_size': int(os.getenv('LOG_MAX_FILE_SIZE', '10')) * 1024 * 1024,  # MB to bytes
            'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5'))
        }
        
        # 安全配置
        self.security_config = {
            'cors_enabled': os.getenv('CORS_ENABLED', 'true').lower() == 'true',
            'cors_origins': os.getenv('CORS_ORIGINS', '*').split(','),
            'rate_limit_enabled': os.getenv('RATE_LIMIT_ENABLED', 'false').lower() == 'true',
            'rate_limit_requests': int(os.getenv('RATE_LIMIT_REQUESTS', '100')),
            'rate_limit_window': int(os.getenv('RATE_LIMIT_WINDOW', '3600')),  # seconds
            'jwt_secret': os.getenv('JWT_SECRET', 'jwt-secret-key'),
            'jwt_expiration': int(os.getenv('JWT_EXPIRATION', '86400'))  # seconds
        }
        
        # 第三方服務配置
        self.external_config = {
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'google_api_key': os.getenv('GOOGLE_API_KEY', ''),
            'aws_access_key': os.getenv('AWS_ACCESS_KEY_ID', ''),
            'aws_secret_key': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
            'aws_region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        }
        
        logger.info(f"配置加載完成 - 環境: {self.app_config['environment']}")
    
    def _validate_config(self):
        """驗證配置"""
        # 驗證必需的配置項
        required_configs = {
            'database': ['host', 'username', 'database'],
            'app': ['api_key', 'secret_key']
        }
        
        missing_configs = []
        
        # 檢查數據庫配置
        for key in required_configs['database']:
            if not self.database_config.get(key):
                missing_configs.append(f'DB_{key.upper()}')
        
        # 檢查應用配置
        for key in required_configs['app']:
            if not self.app_config.get(key):
                missing_configs.append(key.upper())
        
        if missing_configs:
            logger.warning(f"缺少配置項: {', '.join(missing_configs)}")
        
        # 創建必要的目錄
        self._ensure_directories()
        
        logger.info("配置驗證完成")
    
    def _ensure_directories(self):
        """確保必要的目錄存在"""
        directories = [
            self.storage_config['upload_folder'],
            os.path.dirname(self.logging_config['file_path'])
        ]
        
        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.debug(f"目錄確認: {directory}")
    
    def get_database_url(self) -> str:
        """獲取數據庫連接URL"""
        config = self.database_config
        return f"mysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"
    
    def get_app_info(self) -> Dict[str, Any]:
        """獲取應用信息"""
        return {
            'name': self.app_config['name'],
            'version': self.app_config['version'],
            'environment': self.app_config['environment'],
            'debug': self.app_config['debug']
        }
    
    def get_flask_config(self) -> Dict[str, Any]:
        """獲取Flask配置"""
        return {
            'DEBUG': self.app_config['debug'],
            'SECRET_KEY': self.app_config['secret_key'],
            'MAX_CONTENT_LENGTH': self.storage_config['max_file_size'],
            'UPLOAD_FOLDER': self.storage_config['upload_folder']
        }
    
    def is_production(self) -> bool:
        """檢查是否為生產環境"""
        return self.app_config['environment'].lower() == 'production'
    
    def is_development(self) -> bool:
        """檢查是否為開發環境"""
        return self.app_config['environment'].lower() in ['development', 'dev']
    
    def get_config_summary(self) -> Dict[str, Any]:
        """獲取配置摘要（隱藏敏感信息）"""
        return {
            'app': {
                'name': self.app_config['name'],
                'version': self.app_config['version'],
                'environment': self.app_config['environment'],
                'host': self.app_config['host'],
                'port': self.app_config['port']
            },
            'database': {
                'host': self.database_config['host'],
                'port': self.database_config['port'],
                'database': self.database_config['database'],
                'pool_size': self.database_config['pool_size']
            },
            'storage': {
                'upload_folder': self.storage_config['upload_folder'],
                'max_file_size_mb': self.storage_config['max_file_size'] // (1024 * 1024),
                'allowed_extensions': len(self.storage_config['allowed_extensions']),
                'cleanup_days': self.storage_config['cleanup_days']
            },
            'security': {
                'cors_enabled': self.security_config['cors_enabled'],
                'rate_limit_enabled': self.security_config['rate_limit_enabled']
            }
        }

# 全局配置實例
_app_config = None

def get_app_config() -> AppConfig:
    """獲取全局配置實例"""
    global _app_config
    if _app_config is None:
        _app_config = AppConfig()
    return _app_config

def get_database_config() -> Dict[str, Any]:
    """獲取數據庫配置"""
    return get_app_config().database_config

def get_storage_config() -> Dict[str, Any]:
    """獲取存儲配置"""
    return get_app_config().storage_config

def get_app_info() -> Dict[str, Any]:
    """獲取應用信息"""
    return get_app_config().get_app_info()

def is_production() -> bool:
    """檢查是否為生產環境"""
    return get_app_config().is_production()

def is_development() -> bool:
    """檢查是否為開發環境"""
    return get_app_config().is_development()

# 向后兼容的常量定义
LOCAL_STORAGE_PATH = get_storage_config()['upload_folder']
API_KEY = get_app_config().app_config['api_key']

if __name__ == '__main__':
    # 測試配置管理器
    config = get_app_config()
    print(f"✅ 配置管理器初始化成功")
    print(f"應用信息: {config.get_app_info()}")
    print(f"數據庫URL: {config.get_database_url()}")
    print(f"配置摘要: {config.get_config_summary()}")
