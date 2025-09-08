-- =================================================
-- No-Code Architects Toolkit 後端數據庫表結構
-- =================================================
-- 創建日期: 2025-01-09
-- 目標數據庫: zeabur (你的ZEABUR MySQL實例)
-- 表前綴: nca_ (No-Code Architects的縮寫)

-- 確保使用正確的數據庫
USE zeabur;

-- =================================================
-- 1. 用戶表 (nca_users)
-- =================================================
CREATE TABLE IF NOT EXISTS `nca_users` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主鍵ID',
  `uuid` varchar(36) NOT NULL COMMENT '用戶唯一標識',
  `username` varchar(50) NOT NULL COMMENT '用戶名',
  `email` varchar(100) NOT NULL COMMENT '郵箱',
  `password_hash` varchar(255) NOT NULL COMMENT '密碼哈希',
  `status` tinyint(1) DEFAULT 1 COMMENT '狀態 1-正常 0-禁用',
  `api_key` varchar(64) DEFAULT NULL COMMENT '用戶API密鑰',
  `last_login_at` timestamp NULL DEFAULT NULL COMMENT '最後登錄時間',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '創建時間',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  UNIQUE KEY `uk_email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用戶信息表';

-- =================================================
-- 2. GenHuman項目表 (nca_genhuman_projects)
-- =================================================
CREATE TABLE IF NOT EXISTS `nca_genhuman_projects` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主鍵ID',
  `uuid` varchar(36) NOT NULL COMMENT '項目唯一標識',
  `user_id` bigint(20) UNSIGNED NOT NULL COMMENT '用戶ID',
  `project_name` varchar(200) NOT NULL COMMENT '項目名稱',
  `project_type` enum('voice_clone','digital_human','text_to_speech','video_generation') NOT NULL COMMENT '項目類型',
  `status` enum('pending','processing','completed','failed','cancelled') DEFAULT 'pending' COMMENT '項目狀態',
  `genhuman_task_id` varchar(100) DEFAULT NULL COMMENT 'GenHuman API任務ID',
  `config_json` json COMMENT '項目配置JSON',
  `result_data` json COMMENT '結果數據JSON',
  `progress` int(3) DEFAULT 0 COMMENT '進度百分比 0-100',
  `error_message` text COMMENT '錯誤信息',
  `callback_url` varchar(500) COMMENT '回調URL',
  `webhook_secret` varchar(100) COMMENT 'Webhook密鑰',
  `started_at` timestamp NULL DEFAULT NULL COMMENT '開始處理時間',
  `completed_at` timestamp NULL DEFAULT NULL COMMENT '完成時間',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '創建時間',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_project_type` (`project_type`),
  KEY `idx_status` (`status`),
  KEY `idx_genhuman_task_id` (`genhuman_task_id`),
  FOREIGN KEY (`user_id`) REFERENCES `nca_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='GenHuman項目表';

-- =================================================
-- 3. 文件管理表 (nca_files)
-- =================================================
CREATE TABLE IF NOT EXISTS `nca_files` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主鍵ID',
  `uuid` varchar(36) NOT NULL COMMENT '文件唯一標識',
  `user_id` bigint(20) UNSIGNED NOT NULL COMMENT '用戶ID',
  `project_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT '關聯項目ID',
  `file_name` varchar(255) NOT NULL COMMENT '原始文件名',
  `stored_name` varchar(255) NOT NULL COMMENT '存儲文件名',
  `file_type` enum('audio','video','image','text','document','result') NOT NULL COMMENT '文件類型',
  `mime_type` varchar(100) NOT NULL COMMENT 'MIME類型',
  `file_size` bigint(20) NOT NULL COMMENT '文件大小(字節)',
  `file_path` varchar(500) NOT NULL COMMENT '文件存儲路徑',
  `file_url` varchar(500) NOT NULL COMMENT '文件訪問URL',
  `status` enum('uploading','processing','completed','failed') DEFAULT 'uploading' COMMENT '處理狀態',
  `upload_method` enum('form','base64','url') DEFAULT 'form' COMMENT '上傳方式',
  `checksum` varchar(64) COMMENT '文件校驗和',
  `metadata_json` json COMMENT '文件元數據JSON',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '創建時間',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_project_id` (`project_id`),
  KEY `idx_file_type` (`file_type`),
  KEY `idx_status` (`status`),
  FOREIGN KEY (`user_id`) REFERENCES `nca_users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`project_id`) REFERENCES `nca_genhuman_projects` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件管理表';

-- =================================================
-- 4. API調用記錄表 (nca_api_calls)
-- =================================================
CREATE TABLE IF NOT EXISTS `nca_api_calls` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主鍵ID',
  `uuid` varchar(36) NOT NULL COMMENT '調用唯一標識',
  `user_id` bigint(20) UNSIGNED NOT NULL COMMENT '用戶ID',
  `project_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT '關聯項目ID',
  `api_endpoint` varchar(200) NOT NULL COMMENT 'API端點',
  `api_method` enum('GET','POST','PUT','DELETE','PATCH') NOT NULL COMMENT 'HTTP方法',
  `request_data` json COMMENT '請求數據',
  `response_data` json COMMENT '響應數據',
  `response_code` int(3) NOT NULL COMMENT 'HTTP狀態碼',
  `response_time_ms` int(11) DEFAULT NULL COMMENT '響應時間(毫秒)',
  `success` tinyint(1) NOT NULL COMMENT '是否成功',
  `error_message` text COMMENT '錯誤信息',
  `ip_address` varchar(45) COMMENT '請求IP地址',
  `user_agent` varchar(500) COMMENT 'User-Agent',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '創建時間',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_project_id` (`project_id`),
  KEY `idx_api_endpoint` (`api_endpoint`),
  KEY `idx_success` (`success`),
  KEY `idx_created_at` (`created_at`),
  FOREIGN KEY (`user_id`) REFERENCES `nca_users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`project_id`) REFERENCES `nca_genhuman_projects` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API調用記錄表';

-- =================================================
-- 5. 系統配置表 (nca_system_config)
-- =================================================
CREATE TABLE IF NOT EXISTS `nca_system_config` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主鍵ID',
  `config_key` varchar(100) NOT NULL COMMENT '配置鍵',
  `config_value` text NOT NULL COMMENT '配置值',
  `config_type` enum('string','integer','float','boolean','json') DEFAULT 'string' COMMENT '配置類型',
  `description` varchar(500) COMMENT '配置描述',
  `is_public` tinyint(1) DEFAULT 0 COMMENT '是否公開 0-私有 1-公開',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '創建時間',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系統配置表';

-- =================================================
-- 6. 操作日誌表 (nca_operation_logs)
-- =================================================
CREATE TABLE IF NOT EXISTS `nca_operation_logs` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主鍵ID',
  `user_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT '用戶ID',
  `operation_type` varchar(50) NOT NULL COMMENT '操作類型',
  `operation_description` varchar(500) NOT NULL COMMENT '操作描述',
  `target_type` varchar(50) COMMENT '操作目標類型',
  `target_id` bigint(20) UNSIGNED COMMENT '操作目標ID',
  `ip_address` varchar(45) COMMENT 'IP地址',
  `user_agent` varchar(500) COMMENT 'User-Agent',
  `extra_data` json COMMENT '額外數據',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '創建時間',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_operation_type` (`operation_type`),
  KEY `idx_target_type_id` (`target_type`, `target_id`),
  KEY `idx_created_at` (`created_at`),
  FOREIGN KEY (`user_id`) REFERENCES `nca_users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日誌表';

-- =================================================
-- 插入初始系統配置
-- =================================================
INSERT INTO `nca_system_config` (`config_key`, `config_value`, `config_type`, `description`, `is_public`) VALUES
('system_version', '1.0.0', 'string', '系統版本號', 1),
('max_file_size', '1073741824', 'integer', '最大文件上傳大小(字節)', 1),
('supported_file_types', '["audio", "video", "image", "text", "document"]', 'json', '支持的文件類型', 1),
('genhuman_api_enabled', 'true', 'boolean', 'GenHuman API是否啟用', 0),
('whisper_model_size', 'tiny', 'string', 'Whisper模型大小', 0),
('default_language', 'zh-CN', 'string', '默認語言', 1),
('system_timezone', 'Asia/Taipei', 'string', '系統時區', 1);

-- =================================================
-- 創建初始管理員用戶 (可選)
-- =================================================
INSERT INTO `nca_users` (`uuid`, `username`, `email`, `password_hash`, `status`, `api_key`) VALUES
(UUID(), 'admin', 'admin@nocodearchitects.com', SHA2('admin123456', 256), 1, 'admin-api-key-2025');

-- =================================================
-- 顯示創建結果
-- =================================================
SELECT '=== 數據庫表創建完成 ===' AS message;
SHOW TABLES LIKE 'nca_%';

SELECT '=== 用戶表記錄數 ===' AS message;
SELECT COUNT(*) AS user_count FROM nca_users;

SELECT '=== 系統配置記錄數 ===' AS message;
SELECT COUNT(*) AS config_count FROM nca_system_config;

SELECT 'No-Code Architects Toolkit 後端數據庫初始化完成！' AS status;
