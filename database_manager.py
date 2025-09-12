#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zeabur MySQL 持久化存儲數據庫管理器 v2.0
統一MySQL連接管理、連接池和健康檢查機制
"""

import os
import logging
import pymysql
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import time
from threading import Lock

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """統一的MySQL數據庫管理器"""
    
    def __init__(self):
        self.connection_pool = []
        self.pool_size = 5
        self.pool_lock = Lock()
        self.config = self._load_config()
        self.is_connected = False
        
    def _load_config(self) -> Dict[str, Any]:
        """加載數據庫配置"""
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USERNAME', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_DATABASE', 'zeabur_storage'),
            'charset': 'utf8mb4',
            'autocommit': True,
            'connect_timeout': 10,
            'read_timeout': 10,
            'write_timeout': 10
        }
        
        # 驗證必要配置（密碼可以為空）
        required_fields = ['host', 'user', 'database']
        missing_fields = [field for field in required_fields if not config[field]]
        
        # 檢查密碼是否存在（可以為空字符串）
        if 'password' not in config:
            missing_fields.append('password')
        
        if missing_fields:
            logger.error(f"缺少必要的數據庫配置: {', '.join(missing_fields)}")
            raise ValueError(f"Missing required database config: {', '.join(missing_fields)}")
            
        logger.info(f"數據庫配置加載成功: {config['host']}:{config['port']}/{config['database']}")
        return config
    
    def _create_connection(self) -> pymysql.Connection:
        """創建新的數據庫連接"""
        try:
            connection = pymysql.connect(**self.config)
            logger.info("MySQL連接創建成功")
            return connection
        except Exception as e:
            logger.error(f"創建MySQL連接失敗: {e}")
            raise
    
    def initialize_pool(self) -> bool:
        """初始化連接池"""
        try:
            with self.pool_lock:
                # 清空現有連接池
                for conn in self.connection_pool:
                    try:
                        conn.close()
                    except:
                        pass
                self.connection_pool.clear()
                
                # 創建新連接池
                for i in range(self.pool_size):
                    conn = self._create_connection()
                    self.connection_pool.append(conn)
                    
                self.is_connected = True
                logger.info(f"連接池初始化成功，大小: {self.pool_size}")
                return True
                
        except Exception as e:
            logger.error(f"連接池初始化失敗: {e}")
            self.is_connected = False
            return False
    
    @contextmanager
    def get_connection(self):
        """獲取數據庫連接（上下文管理器）"""
        connection = None
        try:
            with self.pool_lock:
                if not self.connection_pool:
                    # 如果連接池為空，創建新連接
                    connection = self._create_connection()
                else:
                    connection = self.connection_pool.pop()
                    
                # 檢查連接是否有效
                if not self._is_connection_alive(connection):
                    connection = self._create_connection()
                    
            yield connection
            
        except Exception as e:
            logger.error(f"數據庫操作錯誤: {e}")
            raise
        finally:
            # 歸還連接到池中
            if connection:
                with self.pool_lock:
                    if len(self.connection_pool) < self.pool_size:
                        self.connection_pool.append(connection)
                    else:
                        connection.close()
    
    def _is_connection_alive(self, connection) -> bool:
        """檢查連接是否存活"""
        try:
            connection.ping(reconnect=False)
            return True
        except:
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                
                return {
                    'status': 'healthy',
                    'connected': True,
                    'pool_size': len(self.connection_pool),
                    'config': {
                        'host': self.config['host'],
                        'port': self.config['port'],
                        'database': self.config['database']
                    }
                }
        except Exception as e:
            logger.error(f"健康檢查失敗: {e}")
            return {
                'status': 'unhealthy',
                'connected': False,
                'error': str(e),
                'pool_size': len(self.connection_pool)
            }
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """執行查詢並返回結果"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute(query, params)
                result = cursor.fetchall()
                cursor.close()
                return result
        except Exception as e:
            logger.error(f"查詢執行失敗: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """執行更新操作並返回影響行數"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                affected_rows = cursor.execute(query, params)
                conn.commit()
                cursor.close()
                return affected_rows
        except Exception as e:
            logger.error(f"更新執行失敗: {e}")
            raise
    
    def close_all_connections(self):
        """關閉所有連接"""
        with self.pool_lock:
            for conn in self.connection_pool:
                try:
                    conn.close()
                except:
                    pass
            self.connection_pool.clear()
            self.is_connected = False
            logger.info("所有數據庫連接已關閉")

def init_database_tables(db_manager: DatabaseManager) -> bool:
    """初始化數據庫表結構"""
    try:
        # 文件存儲表
        create_files_table = """
        CREATE TABLE IF NOT EXISTS files (
            id VARCHAR(36) PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size BIGINT NOT NULL,
            file_hash VARCHAR(64) NOT NULL,
            mime_type VARCHAR(100),
            user_id VARCHAR(36),
            metadata JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_id (user_id),
            INDEX idx_file_hash (file_hash),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        # 執行表創建
        db_manager.execute_update(create_files_table)
        logger.info("數據庫表初始化成功")
        return True
        
    except Exception as e:
        logger.error(f"數據庫表初始化失敗: {e}")
        return False

# 全局數據庫管理器實例
_db_manager = None
_db_lock = Lock()

def get_database_manager() -> DatabaseManager:
    """獲取全局數據庫管理器實例（單例模式）"""
    global _db_manager
    
    if _db_manager is None:
        with _db_lock:
            if _db_manager is None:
                _db_manager = DatabaseManager()
                
    return _db_manager

def reset_database_manager():
    """重置數據庫管理器實例（用於重新加載配置）"""
    global _db_manager
    with _db_lock:
        if _db_manager:
            _db_manager.close_all_connections()
        _db_manager = None

if __name__ == '__main__':
    # 測試數據庫管理器
    db = get_database_manager()
    
    # 初始化連接池
    if db.initialize_pool():
        print("✅ 連接池初始化成功")
        
        # 健康檢查
        health = db.health_check()
        print(f"健康檢查結果: {health}")
        
        # 初始化表
        if init_database_tables(db):
            print("✅ 數據庫表初始化成功")
        else:
            print("❌ 數據庫表初始化失敗")
            
        # 關閉連接
        db.close_all_connections()
    else:
        print("❌ 連接池初始化失敗")