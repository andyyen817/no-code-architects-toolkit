-- =====================================================
-- No-Code Architects Toolkit 數據庫快速設置腳本
-- =====================================================
-- 執行環境: ZEABUR MySQL Terminal
-- 數據庫: zeabur
-- 執行方式: 直接在Terminal中逐條執行

-- 確保使用正確的數據庫
USE zeabur;

-- =====================================================
-- 1. 核心用戶表 (簡化版)
-- =====================================================
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

-- =====================================================
-- 2. GenHuman項目表 (核心功能)
-- =====================================================
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

-- =====================================================
-- 3. 文件管理表 (重要)
-- =====================================================
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

-- =====================================================
-- 4. API調用日誌表 (開發階段重要)
-- =====================================================
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

-- =====================================================
-- 5. 系統配置表 (必需)
-- =====================================================
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

-- =====================================================
-- 插入初始配置數據
-- =====================================================
INSERT INTO nca_config (config_key, config_value, config_type, description) VALUES
('system_version', '1.0.0', 'string', '系統版本'),
('max_file_size', '1073741824', 'integer', '最大文件大小(字節)'),
('whisper_model_size', 'tiny', 'string', 'Whisper模型大小'),
('genhuman_api_enabled', 'true', 'boolean', 'GenHuman API是否啟用'),
('supported_file_types', '["audio","video","image","document"]', 'json', '支持的文件類型');

-- =====================================================
-- 創建測試用戶
-- =====================================================
INSERT INTO nca_users (uuid, username, email, api_key, status) VALUES
(UUID(), 'admin', 'admin@nocodearchitects.com', 'admin-api-key-2025', 1),
(UUID(), 'testuser', 'test@nocodearchitects.com', 'test-api-key-2025', 1);

-- =====================================================
-- 創建測試項目
-- =====================================================
INSERT INTO nca_projects (uuid, user_id, project_name, project_type, status) VALUES
(UUID(), 1, '測試語音克隆項目', 'voice_clone', 'pending'),
(UUID(), 1, '測試數字人項目', 'digital_human', 'pending');

-- =====================================================
-- 驗證創建結果
-- =====================================================
SELECT '=== 數據庫表創建完成 ===' AS message;

SELECT TABLE_NAME as '已創建的表' 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'zeabur' AND TABLE_NAME LIKE 'nca_%';

SELECT '=== 用戶數據 ===' AS message;
SELECT id, username, email, status FROM nca_users;

SELECT '=== 項目數據 ===' AS message;
SELECT id, project_name, project_type, status FROM nca_projects;

SELECT '=== 系統配置 ===' AS message;
SELECT config_key, config_value FROM nca_config;

SELECT 'No-Code Architects Toolkit 數據庫初始化完成！' AS 完成狀態;
