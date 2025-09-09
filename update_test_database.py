#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZEABUR雲端測試數據庫結構更新腳本
目標：為雲端測試功能添加專用數據表
"""

import pymysql
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
    """執行SQL語句"""
    try:
        with connection.cursor() as cursor:
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

def add_test_tables(connection):
    """添加測試專用數據表"""
    
    print_log("🚀 開始添加測試數據表...")
    
    # 1. 測試記錄表
    test_records_sql = """
    CREATE TABLE IF NOT EXISTS nca_test_records (
      id INT AUTO_INCREMENT PRIMARY KEY,
      test_type ENUM('nca_toolkit','ffmpeg','whisper','genhuman') NOT NULL,
      test_function VARCHAR(100) NOT NULL COMMENT '測試的具體功能',
      test_endpoint VARCHAR(200) NOT NULL COMMENT 'API端點',
      input_data JSON COMMENT '輸入參數',
      output_data JSON COMMENT '輸出結果',
      test_status ENUM('running','success','failed','timeout') DEFAULT 'running',
      error_message TEXT COMMENT '錯誤信息',
      execution_time_ms INT DEFAULT NULL COMMENT '執行時間(毫秒)',
      file_urls JSON COMMENT '相關文件URL列表',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_test_type (test_type),
      INDEX idx_test_status (test_status),
      INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='雲端測試記錄表';
    """
    
    # 2. Whisper轉錄結果表
    whisper_results_sql = """
    CREATE TABLE IF NOT EXISTS nca_whisper_results (
      id INT AUTO_INCREMENT PRIMARY KEY,
      test_record_id INT NOT NULL,
      media_type ENUM('audio','video') NOT NULL,
      media_url VARCHAR(500) NOT NULL,
      transcribed_text TEXT,
      srt_content TEXT COMMENT 'SRT字幕內容',
      language VARCHAR(10) DEFAULT 'zh',
      model_used VARCHAR(50) DEFAULT 'tiny',
      processing_time_seconds FLOAT,
      confidence_score FLOAT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_test_record_id (test_record_id),
      INDEX idx_media_type (media_type),
      FOREIGN KEY (test_record_id) REFERENCES nca_test_records(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Whisper轉錄結果表';
    """
    
    # 3. FFMPEG處理結果表
    ffmpeg_results_sql = """
    CREATE TABLE IF NOT EXISTS nca_ffmpeg_results (
      id INT AUTO_INCREMENT PRIMARY KEY,
      test_record_id INT NOT NULL,
      operation_type VARCHAR(50) NOT NULL COMMENT '操作類型：convert,extract,resize等',
      input_file_url VARCHAR(500) NOT NULL,
      output_file_url VARCHAR(500),
      ffmpeg_command TEXT COMMENT '執行的FFmpeg命令',
      processing_time_seconds FLOAT,
      file_size_before BIGINT COMMENT '處理前文件大小',
      file_size_after BIGINT COMMENT '處理後文件大小',
      resolution_before VARCHAR(20) COMMENT '處理前分辨率',
      resolution_after VARCHAR(20) COMMENT '處理後分辨率',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_test_record_id (test_record_id),
      INDEX idx_operation_type (operation_type),
      FOREIGN KEY (test_record_id) REFERENCES nca_test_records(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='FFMPEG處理結果表';
    """
    
    # 4. GenHuman API調用結果表
    genhuman_results_sql = """
    CREATE TABLE IF NOT EXISTS nca_genhuman_results (
      id INT AUTO_INCREMENT PRIMARY KEY,
      test_record_id INT NOT NULL,
      api_type VARCHAR(50) NOT NULL COMMENT 'API類型：voice_clone,digital_human等',
      task_id VARCHAR(100) COMMENT 'GenHuman任務ID',
      request_data JSON COMMENT '請求數據',
      callback_data JSON COMMENT '回調數據',
      status ENUM('pending','processing','completed','failed') DEFAULT 'pending',
      result_url VARCHAR(500) COMMENT '結果文件URL',
      processing_time_minutes FLOAT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_test_record_id (test_record_id),
      INDEX idx_api_type (api_type),
      INDEX idx_task_id (task_id),
      FOREIGN KEY (test_record_id) REFERENCES nca_test_records(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='GenHuman API結果表';
    """
    
    # 5. 測試會話表
    test_sessions_sql = """
    CREATE TABLE IF NOT EXISTS nca_test_sessions (
      id INT AUTO_INCREMENT PRIMARY KEY,
      session_name VARCHAR(200) NOT NULL,
      description TEXT,
      test_count INT DEFAULT 0,
      success_count INT DEFAULT 0,
      failed_count INT DEFAULT 0,
      total_execution_time_ms BIGINT DEFAULT 0,
      started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      completed_at TIMESTAMP NULL,
      INDEX idx_started_at (started_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='測試會話表';
    """
    
    # 執行表創建
    tables = [
        (test_records_sql, "創建測試記錄表 (nca_test_records)"),
        (whisper_results_sql, "創建Whisper結果表 (nca_whisper_results)"),
        (ffmpeg_results_sql, "創建FFMPEG結果表 (nca_ffmpeg_results)"),
        (genhuman_results_sql, "創建GenHuman結果表 (nca_genhuman_results)"),
        (test_sessions_sql, "創建測試會話表 (nca_test_sessions)")
    ]
    
    success_count = 0
    for sql, description in tables:
        if execute_sql(connection, sql, description):
            success_count += 1
    
    print_log(f"📊 測試表創建完成: {success_count}/5 個表成功創建")
    return success_count == 5

def verify_test_tables(connection):
    """驗證測試表創建結果"""
    
    print_log("🔍 開始驗證測試表...")
    
    try:
        with connection.cursor() as cursor:
            # 檢查所有表
            cursor.execute("SHOW TABLES LIKE 'nca_%'")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            
            print_log(f"📋 發現 {len(table_names)} 個NCA表:")
            for table_name in table_names:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print_log(f"   - {table_name}: {count} 條記錄")
            
            # 檢查新增的測試表
            test_tables = [
                'nca_test_records', 'nca_whisper_results', 
                'nca_ffmpeg_results', 'nca_genhuman_results', 'nca_test_sessions'
            ]
            
            missing_tables = [table for table in test_tables if table not in table_names]
            
            if missing_tables:
                print_log(f"❌ 缺少測試表: {missing_tables}", "ERROR")
                return False
            
            print_log("✅ 所有測試表創建成功！")
            return True
            
    except Exception as e:
        print_log(f"❌ 驗證過程失敗: {str(e)}", "ERROR")
        return False

def main():
    """主函數"""
    
    print_log("🚀 ZEABUR雲端測試數據庫更新開始")
    print_log("🎯 目標: 添加測試專用數據表")
    
    connection = connect_database()
    if not connection:
        print_log("💥 無法連接數據庫，更新終止", "ERROR")
        return False
    
    try:
        # 添加測試表
        if not add_test_tables(connection):
            print_log("💥 測試表創建失敗", "ERROR")
            return False
        
        # 驗證創建結果
        if not verify_test_tables(connection):
            print_log("💥 測試表驗證失敗", "ERROR")
            return False
        
        print_log("🎉 數據庫更新完成！所有測試表創建成功")
        print_log("📋 下一步: 創建雲端測試頁面")
        return True
        
    finally:
        connection.close()
        print_log("🔒 數據庫連接已關閉")

if __name__ == "__main__":
    success = main()
    if success:
        print("\n" + "="*50)
        print("✅ 測試數據庫更新成功完成！")
        print("🚀 現在可以創建雲端測試頁面")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ 測試數據庫更新失敗")
        print("🔧 請檢查錯誤信息並重試")
        print("="*50)




