#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
No-Code Architects Toolkit 自動化數據庫設置腳本
目標：直接創建ZEABUR MySQL數據庫表，無需手動操作
"""

import pymysql
import json
import uuid
from datetime import datetime

# ZEABUR MySQL連接配置
DB_CONFIG = {
    'host': 'tpe1.clusters.zeabur.com',
    'port': 30791,
    'user': 'root',
    'password': '248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6',
    'database': 'zeabur',
    'charset': 'utf8mb4'
}

def print_log(message, level="INFO"):
    """打印帶時間戳的日誌"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def connect_database():
    """連接到ZEABUR MySQL數據庫"""
    try:
        print_log("🔗 正在連接ZEABUR MySQL數據庫...")
        connection = pymysql.connect(**DB_CONFIG)
        print_log("✅ 數據庫連接成功！")
        return connection
    except Exception as e:
        print_log(f"❌ 數據庫連接失敗: {str(e)}", "ERROR")
        return None

def execute_sql(connection, sql, description=""):
    """執行SQL語句（可能包含多條語句）"""
    try:
        with connection.cursor() as cursor:
            # 分割SQL語句（按分號分割）
            sql_statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            
            for statement in sql_statements:
                if statement:
                    cursor.execute(statement)
            
            connection.commit()
            print_log(f"✅ {description} - 執行成功")
            return True
    except Exception as e:
        print_log(f"❌ {description} - 執行失敗: {str(e)}", "ERROR")
        return False

def create_tables(connection):
    """創建所有需要的數據表"""
    
    print_log("🚀 開始創建數據表...")
    
    # 1. 用戶表
    users_table_sql = """
    DROP TABLE IF EXISTS nca_users;
    CREATE TABLE nca_users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      uuid VARCHAR(36) NOT NULL UNIQUE,
      username VARCHAR(50) NOT NULL UNIQUE,
      email VARCHAR(100) NOT NULL UNIQUE,
      api_key VARCHAR(64) DEFAULT NULL,
      status TINYINT(1) DEFAULT 1 COMMENT '1-啟用 0-禁用',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用戶表';
    """
    
    # 2. 項目表
    projects_table_sql = """
    DROP TABLE IF EXISTS nca_projects;
    CREATE TABLE nca_projects (
      id INT AUTO_INCREMENT PRIMARY KEY,
      uuid VARCHAR(36) NOT NULL UNIQUE,
      user_id INT NOT NULL,
      project_name VARCHAR(200) NOT NULL,
      project_type ENUM('voice_clone','digital_human','text_to_speech','video_generation') NOT NULL,
      status ENUM('pending','processing','completed','failed','cancelled') DEFAULT 'pending',
      genhuman_task_id VARCHAR(100) DEFAULT NULL,
      config_data JSON,
      result_data JSON,
      progress INT DEFAULT 0 COMMENT '0-100',
      error_message TEXT,
      callback_url VARCHAR(500),
      started_at TIMESTAMP NULL,
      completed_at TIMESTAMP NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_user_id (user_id),
      INDEX idx_status (status),
      INDEX idx_task_id (genhuman_task_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='GenHuman項目表';
    """
    
    # 3. 文件表
    files_table_sql = """
    DROP TABLE IF EXISTS nca_files;
    CREATE TABLE nca_files (
      id INT AUTO_INCREMENT PRIMARY KEY,
      uuid VARCHAR(36) NOT NULL UNIQUE,
      user_id INT NOT NULL,
      project_id INT DEFAULT NULL,
      original_name VARCHAR(255) NOT NULL,
      stored_name VARCHAR(255) NOT NULL,
      file_type ENUM('audio','video','image','document','result') NOT NULL,
      file_size BIGINT NOT NULL,
      file_path VARCHAR(500) NOT NULL,
      file_url VARCHAR(500) NOT NULL,
      upload_method ENUM('form','base64','url') DEFAULT 'form',
      status ENUM('uploading','processing','completed','failed') DEFAULT 'uploading',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_user_id (user_id),
      INDEX idx_project_id (project_id),
      INDEX idx_file_type (file_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文件管理表';
    """
    
    # 4. API日誌表
    api_logs_table_sql = """
    DROP TABLE IF EXISTS nca_api_logs;
    CREATE TABLE nca_api_logs (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT DEFAULT NULL,
      endpoint VARCHAR(200) NOT NULL,
      method ENUM('GET','POST','PUT','DELETE') NOT NULL,
      request_data JSON,
      response_data JSON,
      response_code INT NOT NULL,
      response_time_ms INT DEFAULT NULL,
      success TINYINT(1) NOT NULL,
      error_message TEXT,
      ip_address VARCHAR(45),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_endpoint (endpoint),
      INDEX idx_success (success),
      INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API調用日誌表';
    """
    
    # 5. 配置表
    config_table_sql = """
    DROP TABLE IF EXISTS nca_config;
    CREATE TABLE nca_config (
      id INT AUTO_INCREMENT PRIMARY KEY,
      config_key VARCHAR(100) NOT NULL UNIQUE,
      config_value TEXT NOT NULL,
      config_type ENUM('string','integer','boolean','json') DEFAULT 'string',
      description VARCHAR(255),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系統配置表';
    """
    
    # 執行表創建
    tables = [
        (users_table_sql, "創建用戶表 (nca_users)"),
        (projects_table_sql, "創建項目表 (nca_projects)"),
        (files_table_sql, "創建文件表 (nca_files)"),
        (api_logs_table_sql, "創建API日誌表 (nca_api_logs)"),
        (config_table_sql, "創建配置表 (nca_config)")
    ]
    
    success_count = 0
    for sql, description in tables:
        if execute_sql(connection, sql, description):
            success_count += 1
    
    print_log(f"📊 表創建完成: {success_count}/5 個表成功創建")
    return success_count == 5

def insert_initial_data(connection):
    """插入初始數據"""
    
    print_log("📝 開始插入初始數據...")
    
    # 系統配置數據
    config_data = [
        ('system_version', '1.0.0', 'string', '系統版本'),
        ('max_file_size', '1073741824', 'integer', '最大文件大小(字節)'),
        ('whisper_model_size', 'tiny', 'string', 'Whisper模型大小'),
        ('genhuman_api_enabled', 'true', 'boolean', 'GenHuman API是否啟用'),
        ('supported_file_types', '["audio","video","image","document"]', 'json', '支持的文件類型')
    ]
    
    config_sql = """
    INSERT INTO nca_config (config_key, config_value, config_type, description) VALUES
    (%s, %s, %s, %s)
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.executemany(config_sql, config_data)
            connection.commit()
            print_log("✅ 系統配置數據插入成功")
    except Exception as e:
        print_log(f"❌ 系統配置數據插入失敗: {str(e)}", "ERROR")
        return False
    
    # 創建測試用戶
    users_data = [
        (str(uuid.uuid4()), 'admin', 'admin@nocodearchitects.com', 'admin-api-key-2025', 1),
        (str(uuid.uuid4()), 'testuser', 'test@nocodearchitects.com', 'test-api-key-2025', 1)
    ]
    
    users_sql = """
    INSERT INTO nca_users (uuid, username, email, api_key, status) VALUES
    (%s, %s, %s, %s, %s)
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.executemany(users_sql, users_data)
            connection.commit()
            print_log("✅ 測試用戶數據插入成功")
    except Exception as e:
        print_log(f"❌ 測試用戶數據插入失敗: {str(e)}", "ERROR")
        return False
    
    # 創建測試項目
    projects_data = [
        (str(uuid.uuid4()), 1, '測試語音克隆項目', 'voice_clone', 'pending'),
        (str(uuid.uuid4()), 1, '測試數字人項目', 'digital_human', 'pending')
    ]
    
    projects_sql = """
    INSERT INTO nca_projects (uuid, user_id, project_name, project_type, status) VALUES
    (%s, %s, %s, %s, %s)
    """
    
    try:
        with connection.cursor() as cursor:
            cursor.executemany(projects_sql, projects_data)
            connection.commit()
            print_log("✅ 測試項目數據插入成功")
    except Exception as e:
        print_log(f"❌ 測試項目數據插入失敗: {str(e)}", "ERROR")
        return False
    
    return True

def verify_setup(connection):
    """驗證數據庫設置結果"""
    
    print_log("🔍 開始驗證數據庫設置...")
    
    # 檢查表
    check_tables_sql = "SHOW TABLES LIKE 'nca_%'"
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(check_tables_sql)
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            
            print_log(f"📋 發現 {len(table_names)} 個表:")
            for table_name in table_names:
                print_log(f"   - {table_name}")
            
            expected_tables = ['nca_users', 'nca_projects', 'nca_files', 'nca_api_logs', 'nca_config']
            missing_tables = [table for table in expected_tables if table not in table_names]
            
            if missing_tables:
                print_log(f"❌ 缺少表: {missing_tables}", "ERROR")
                return False
            
            # 檢查數據
            data_checks = [
                ("SELECT COUNT(*) FROM nca_users", "用戶"),
                ("SELECT COUNT(*) FROM nca_projects", "項目"),
                ("SELECT COUNT(*) FROM nca_config", "配置")
            ]
            
            for sql, name in data_checks:
                cursor.execute(sql)
                count = cursor.fetchone()[0]
                print_log(f"📊 {name}數據: {count} 條記錄")
            
            # 顯示用戶信息
            cursor.execute("SELECT id, username, email, status FROM nca_users")
            users = cursor.fetchall()
            print_log("👤 創建的用戶:")
            for user in users:
                print_log(f"   ID:{user[0]} - {user[1]} ({user[2]}) - 狀態:{user[3]}")
            
            # 顯示項目信息
            cursor.execute("SELECT id, project_name, project_type, status FROM nca_projects")
            projects = cursor.fetchall()
            print_log("🎯 創建的項目:")
            for project in projects:
                print_log(f"   ID:{project[0]} - {project[1]} ({project[2]}) - 狀態:{project[3]}")
            
            return True
            
    except Exception as e:
        print_log(f"❌ 驗證過程失敗: {str(e)}", "ERROR")
        return False

def main():
    """主函數"""
    
    print_log("🚀 No-Code Architects Toolkit 自動化數據庫設置開始")
    print_log("🎯 目標: 自動創建ZEABUR MySQL數據庫表")
    
    # 連接數據庫
    connection = connect_database()
    if not connection:
        print_log("💥 無法連接數據庫，設置終止", "ERROR")
        return False
    
    try:
        # 創建表
        if not create_tables(connection):
            print_log("💥 表創建失敗，設置終止", "ERROR")
            return False
        
        # 插入初始數據
        if not insert_initial_data(connection):
            print_log("💥 初始數據插入失敗，設置終止", "ERROR")
            return False
        
        # 驗證設置
        if not verify_setup(connection):
            print_log("💥 設置驗證失敗", "ERROR")
            return False
        
        print_log("🎉 數據庫設置完成！所有表和數據創建成功")
        print_log("📋 下一步: 測試Flask應用的數據庫連接")
        return True
        
    finally:
        connection.close()
        print_log("🔒 數據庫連接已關閉")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n" + "="*50)
        print("✅ 自動化數據庫設置成功完成！")
        print("🚀 現在可以啟動後端應用進行測試")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ 自動化數據庫設置失敗")
        print("🔧 請檢查錯誤信息並重試")
        print("="*50)
