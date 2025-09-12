#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據庫日誌記錄服務
將API調用記錄保存到Zeabur MySQL數據庫
"""

import logging
import json
import os
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
        # 使用环境变量配置数据库连接
        self.db_config = {
            'host': os.getenv('DB_HOST', 'mysql.zeabur.internal'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USERNAME', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_DATABASE', 'zeabur'),
            'charset': os.getenv('DB_CHARSET', 'utf8mb4')
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
                
                # 🚨 新增：創建文件上傳記錄表
                files_table_sql = """
                CREATE TABLE IF NOT EXISTS `nca_uploaded_files` (
                    `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
                    `file_id` varchar(36) NOT NULL UNIQUE COMMENT 'UUID文件ID',
                    `original_filename` varchar(255) NOT NULL COMMENT '原始文件名',
                    `safe_filename` varchar(255) NOT NULL COMMENT '安全文件名',
                    `file_type` enum('audio','video') NOT NULL COMMENT '文件類型',
                    `file_size` bigint NOT NULL COMMENT '文件大小(字節)',
                    `file_path` varchar(500) NOT NULL COMMENT '本地文件路徑',
                    `file_url` varchar(500) NOT NULL COMMENT '外部訪問URL',
                    `upload_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `idx_file_id` (`file_id`),
                    KEY `idx_file_type` (`file_type`),
                    KEY `idx_upload_time` (`upload_time`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='上傳文件記錄表'
                """
                cursor.execute(files_table_sql)
                connection.commit()
                logger.info("✅ 數據庫表創建成功: nca_uploaded_files")
                
                # 🚨 新增：創建輸出文件記錄表
                output_files_table_sql = """
                CREATE TABLE IF NOT EXISTS `nca_output_files` (
                    `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
                    `file_id` varchar(36) NOT NULL UNIQUE COMMENT 'UUID文件ID',
                    `original_filename` varchar(255) NOT NULL COMMENT '原始文件名',
                    `safe_filename` varchar(255) NOT NULL COMMENT '安全文件名',
                    `file_type` enum('audio','video','image') NOT NULL COMMENT '文件類型',
                    `file_size` bigint NOT NULL COMMENT '文件大小(字節)',
                    `file_path` varchar(500) NOT NULL COMMENT '本地文件路徑',
                    `file_url` varchar(500) NOT NULL COMMENT '外部訪問URL',
                    `operation_type` varchar(50) NOT NULL COMMENT '操作類型(cut/trim/thumbnail/concatenate等)',
                    `metadata` json COMMENT '額外元數據',
                    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `idx_file_id` (`file_id`),
                    KEY `idx_file_type` (`file_type`),
                    KEY `idx_operation_type` (`operation_type`),
                    KEY `idx_created_at` (`created_at`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='輸出文件記錄表'
                """
                cursor.execute(output_files_table_sql)
                connection.commit()
                logger.info("✅ 數據庫表創建成功: nca_output_files")
                
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

# 🚨 新增：文件上傳相關功能
class FileUploadLogger:
    """文件上傳記錄器"""
    
    def log_file_upload(self, file_record):
        """
        記錄文件上傳到數據庫
        
        Args:
            file_record (dict): 文件記錄包含:
                - file_id: UUID文件ID
                - original_filename: 原始文件名
                - safe_filename: 安全文件名
                - file_type: 文件類型 (audio/video)
                - file_size: 文件大小(字節)
                - file_path: 本地文件路徑
                - file_url: 外部訪問URL
                - upload_time: 上傳時間
        """
        if not PYMYSQL_AVAILABLE:
            logger.info(f"📋 文件上傳記錄 (本地): {file_record['original_filename']}")
            return True
        
        # 確保表存在
        if not database_logger.create_table_if_not_exists():
            return False
        
        try:
            connection = database_logger.get_connection()
            if not connection:
                return False
            
            with connection.cursor() as cursor:
                insert_sql = """
                INSERT INTO `nca_uploaded_files` (
                    `file_id`, `original_filename`, `safe_filename`, `file_type`,
                    `file_size`, `file_path`, `file_url`, `upload_time`
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_sql, (
                    file_record['file_id'],
                    file_record['original_filename'],
                    file_record['safe_filename'],
                    file_record['file_type'],
                    file_record['file_size'],
                    file_record['file_path'],
                    file_record['file_url'],
                    file_record['upload_time']
                ))
                connection.commit()
                
                record_id = cursor.lastrowid
                logger.info(f"✅ 文件上傳已記錄到數據庫 (ID: {record_id}): {file_record['original_filename']}")
                return True
                
        except Exception as e:
            logger.error(f"記錄文件上傳失敗: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()
    
    def get_uploaded_files(self, limit=20, file_type=None):
        """
        獲取上傳文件列表
        
        Args:
            limit (int): 返回數量限制
            file_type (str): 文件類型過濾 (audio/video)
            
        Returns:
            list: 文件記錄列表
        """
        if not PYMYSQL_AVAILABLE:
            return []
        
        try:
            connection = database_logger.get_connection()
            if not connection:
                return []
            
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                if file_type:
                    select_sql = """
                    SELECT * FROM `nca_uploaded_files` 
                    WHERE `file_type` = %s
                    ORDER BY `upload_time` DESC 
                    LIMIT %s
                    """
                    cursor.execute(select_sql, (file_type, limit))
                else:
                    select_sql = """
                    SELECT * FROM `nca_uploaded_files` 
                    ORDER BY `upload_time` DESC 
                    LIMIT %s
                    """
                    cursor.execute(select_sql, (limit,))
                
                results = cursor.fetchall()
                
                # 轉換時間為字符串
                for result in results:
                    if 'upload_time' in result:
                        result['upload_time'] = result['upload_time'].strftime('%Y-%m-%d %H:%M:%S')
                    if 'created_at' in result:
                        result['created_at'] = result['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if 'updated_at' in result:
                        result['updated_at'] = result['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                return results
                
        except Exception as e:
            logger.error(f"獲取上傳文件列表失敗: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()

# 將方法添加到主記錄器中
database_logger.log_file_upload = FileUploadLogger().log_file_upload
database_logger.get_uploaded_files = FileUploadLogger().get_uploaded_files

# 🚨 新增：輸出文件相關功能
class OutputFileLogger:
    """輸出文件記錄器"""
    
    def log_output_file(self, file_record):
        """
        記錄輸出文件到數據庫
        
        Args:
            file_record (dict): 文件記錄包含:
                - file_id: UUID文件ID
                - original_filename: 原始文件名
                - safe_filename: 安全文件名
                - file_type: 文件類型 (audio/video/image)
                - file_size: 文件大小(字節)
                - file_path: 本地文件路徑
                - file_url: 外部訪問URL
                - operation_type: 操作類型
                - metadata: 額外元數據
        """
        if not PYMYSQL_AVAILABLE:
            logger.info(f"📋 輸出文件記錄 (本地): {file_record['original_filename']}")
            return True
        
        # 確保表存在
        if not database_logger.create_table_if_not_exists():
            return False
        
        try:
            connection = database_logger.get_connection()
            if not connection:
                return False
            
            with connection.cursor() as cursor:
                insert_sql = """
                INSERT INTO `nca_output_files` (
                    `file_id`, `original_filename`, `safe_filename`, `file_type`,
                    `file_size`, `file_path`, `file_url`, `operation_type`, `metadata`
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # 處理metadata
                metadata_json = None
                if file_record.get('metadata'):
                    metadata_json = json.dumps(file_record['metadata'], ensure_ascii=False)
                
                cursor.execute(insert_sql, (
                    file_record['file_id'],
                    file_record['original_filename'],
                    file_record['safe_filename'],
                    file_record['file_type'],
                    file_record['file_size'],
                    file_record['file_path'],
                    file_record['file_url'],
                    file_record.get('operation_type', 'unknown'),
                    metadata_json
                ))
                connection.commit()
                
                record_id = cursor.lastrowid
                logger.info(f"✅ 輸出文件已記錄到數據庫 (ID: {record_id}): {file_record['original_filename']}")
                return True
                
        except Exception as e:
            logger.error(f"記錄輸出文件失敗: {e}")
            return False
        finally:
            if 'connection' in locals():
                connection.close()
    
    def get_output_files(self, file_type=None, operation_type=None, limit=50):
        """
        獲取輸出文件列表
        
        Args:
            file_type (str): 文件類型過濾 (audio/video/image)
            operation_type (str): 操作類型過濾
            limit (int): 返回數量限制
            
        Returns:
            list: 文件記錄列表
        """
        if not PYMYSQL_AVAILABLE:
            return []
        
        try:
            connection = database_logger.get_connection()
            if not connection:
                return []
            
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                where_conditions = []
                params = []
                
                if file_type:
                    where_conditions.append("`file_type` = %s")
                    params.append(file_type)
                
                if operation_type:
                    where_conditions.append("`operation_type` = %s")
                    params.append(operation_type)
                
                where_clause = " AND ".join(where_conditions)
                if where_clause:
                    where_clause = f"WHERE {where_clause}"
                
                select_sql = f"""
                SELECT * FROM `nca_output_files` 
                {where_clause}
                ORDER BY `created_at` DESC 
                LIMIT %s
                """
                params.append(limit)
                
                cursor.execute(select_sql, params)
                results = cursor.fetchall()
                
                # 轉換時間為字符串
                for result in results:
                    if 'created_at' in result:
                        result['created_at'] = result['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if 'updated_at' in result:
                        result['updated_at'] = result['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                    # 處理metadata
                    if result.get('metadata'):
                        try:
                            result['metadata'] = json.loads(result['metadata'])
                        except:
                            result['metadata'] = {}
                
                return results
                
        except Exception as e:
            logger.error(f"獲取輸出文件列表失敗: {e}")
            return []
        finally:
            if 'connection' in locals():
                connection.close()
    
    def get_output_file_by_id(self, file_id):
        """根據ID獲取輸出文件信息"""
        if not PYMYSQL_AVAILABLE:
            return None
        
        try:
            connection = database_logger.get_connection()
            if not connection:
                return None
            
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                select_sql = "SELECT * FROM `nca_output_files` WHERE `file_id` = %s"
                cursor.execute(select_sql, (file_id,))
                result = cursor.fetchone()
                
                if result:
                    # 轉換時間為字符串
                    if 'created_at' in result:
                        result['created_at'] = result['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if 'updated_at' in result:
                        result['updated_at'] = result['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                    # 處理metadata
                    if result.get('metadata'):
                        try:
                            result['metadata'] = json.loads(result['metadata'])
                        except:
                            result['metadata'] = {}
                
                return result
                
        except Exception as e:
            logger.error(f"獲取輸出文件信息失敗: {e}")
            return None
        finally:
            if 'connection' in locals():
                connection.close()

# 將輸出文件方法添加到主記錄器中
database_logger.log_output_file = OutputFileLogger().log_output_file
database_logger.get_output_files = OutputFileLogger().get_output_files
database_logger.get_output_file_by_id = OutputFileLogger().get_output_file_by_id



