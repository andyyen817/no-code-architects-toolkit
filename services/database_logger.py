#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據庫日誌記錄服務
將API調用記錄保存到Zeabur MySQL數據庫
"""

import logging
import json
from datetime import datetime

# 條件導入
try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

logger = logging.getLogger(__name__)

class DatabaseLogger:
    def __init__(self):
        self.db_config = {
            'host': 'tpe1.clusters.zeabur.com',
            'port': 30791,
            'user': 'root',
            'password': '248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6',
            'database': 'zeabur',
            'charset': 'utf8mb4'
        }
        self.table_created = False
    
    def get_connection(self):
        """獲取數據庫連接"""
        if not PYMYSQL_AVAILABLE:
            return None
        try:
            return pymysql.connect(**self.db_config)
        except Exception as e:
            logger.warning(f"數據庫連接失敗: {e}")
            return None
    
    def create_table_if_not_exists(self):
        """創建API調用記錄表（如果不存在）"""
        if self.table_created or not PYMYSQL_AVAILABLE:
            return True
            
        try:
            connection = self.get_connection()
            if not connection:
                return False
                
            with connection.cursor() as cursor:
                # 創建API調用記錄表
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS `nca_api_logs` (
                    `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
                    `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `endpoint` varchar(255) NOT NULL,
                    `method` varchar(10) NOT NULL,
                    `request_data` text,
                    `response_status` int,
                    `response_time_ms` int,
                    `file_url` varchar(500),
                    `file_size` bigint,
                    `error_message` text,
                    `user_ip` varchar(45),
                    `api_key_used` varchar(50),
                    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`),
                    KEY `idx_timestamp` (`timestamp`),
                    KEY `idx_endpoint` (`endpoint`),
                    KEY `idx_status` (`response_status`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(create_table_sql)
                connection.commit()
                self.table_created = True
                logger.info("✅ 數據庫表創建成功: nca_api_logs")
                return True
                
        except Exception as e:
            logger.error(f"創建數據庫表失敗: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()
    
    def log_api_call(self, endpoint, method, request_data=None, response_status=None, 
                     response_time_ms=None, file_url=None, file_size=None, 
                     error_message=None, user_ip=None, api_key_used=None):
        """
        記錄API調用到數據庫
        
        Args:
            endpoint: API端點路徑
            method: HTTP方法
            request_data: 請求數據（dict或str）
            response_status: HTTP響應狀態碼
            response_time_ms: 響應時間（毫秒）
            file_url: 生成的文件URL
            file_size: 文件大小（字節）
            error_message: 錯誤信息
            user_ip: 用戶IP地址
            api_key_used: 使用的API Key
        """
        if not PYMYSQL_AVAILABLE:
            logger.info(f"📝 API調用記錄 (本地): {method} {endpoint} -> {response_status}")
            return True
        
        # 確保表存在
        if not self.create_table_if_not_exists():
            return False
        
        try:
            connection = self.get_connection()
            if not connection:
                return False
            
            with connection.cursor() as cursor:
                # 準備數據
                request_data_str = None
                if request_data:
                    if isinstance(request_data, dict):
                        request_data_str = json.dumps(request_data, ensure_ascii=False)
                    else:
                        request_data_str = str(request_data)
                
                # 插入記錄
                insert_sql = """
                INSERT INTO `nca_api_logs` (
                    `endpoint`, `method`, `request_data`, `response_status`, 
                    `response_time_ms`, `file_url`, `file_size`, `error_message`,
                    `user_ip`, `api_key_used`
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_sql, (
                    endpoint, method, request_data_str, response_status,
                    response_time_ms, file_url, file_size, error_message,
                    user_ip, api_key_used
                ))
                connection.commit()
                
                log_id = cursor.lastrowid
                logger.info(f"✅ API調用已記錄到數據庫 (ID: {log_id}): {method} {endpoint}")
                return True
                
        except Exception as e:
            logger.error(f"記錄API調用失敗: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()
    
    def get_recent_logs(self, limit=50):
        """獲取最近的API調用記錄"""
        if not PYMYSQL_AVAILABLE:
            return []
        
        try:
            connection = self.get_connection()
            if not connection:
                return []
            
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                select_sql = """
                SELECT * FROM `nca_api_logs` 
                ORDER BY `timestamp` DESC 
                LIMIT %s
                """
                cursor.execute(select_sql, (limit,))
                results = cursor.fetchall()
                
                # 轉換datetime為字符串
                for result in results:
                    if 'timestamp' in result:
                        result['timestamp'] = result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    if 'created_at' in result:
                        result['created_at'] = result['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if 'updated_at' in result:
                        result['updated_at'] = result['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                return results
                
        except Exception as e:
            logger.error(f"獲取API調用記錄失敗: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()
    
    def test_database_connection(self):
        """測試數據庫連接"""
        if not PYMYSQL_AVAILABLE:
            return {
                "status": "warning",
                "message": "PyMySQL not available",
                "available": False
            }
        
        try:
            connection = self.get_connection()
            if not connection:
                return {
                    "status": "error",
                    "message": "無法連接到數據庫",
                    "available": False
                }
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            return {
                "status": "success",
                "message": "數據庫連接成功",
                "available": True,
                "config": {
                    "host": self.db_config['host'],
                    "port": self.db_config['port'],
                    "database": self.db_config['database'],
                    "charset": self.db_config['charset']
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"數據庫連接測試失敗: {str(e)}",
                "available": False
            }
        finally:
            if 'connection' in locals():
                connection.close()

# 創建全局實例
database_logger = DatabaseLogger()
