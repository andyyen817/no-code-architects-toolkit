# 🚀 ZEABUR Terminal 數據庫快速設置

## 🎯 目標
直接在ZEABUR Terminal中快速創建所需的數據庫表

## ⏰ 預計時間
5-10分鐘完成所有設置

---

## 📋 **執行步驟**

### **步驟1: 連接MySQL**
在你當前的ZEABUR Terminal中執行：

```bash
mysql -h tpe1.clusters.zeabur.com -P 30791 -u root -p248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6 zeabur
```

**如果連接成功，你會看到：**
```
mysql>
```

### **步驟2: 確認當前數據庫**
```sql
SELECT DATABASE();
SHOW TABLES;
```

### **步驟3: 執行表創建語句**
**請逐條複製粘貼以下SQL語句：**

#### **3.1 創建用戶表**
```sql
USE zeabur;

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
```

#### **3.2 創建項目表**
```sql
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
```

#### **3.3 創建文件表**
```sql
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
```

#### **3.4 創建API日誌表**
```sql
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
```

#### **3.5 創建配置表**
```sql
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
```

### **步驟4: 插入初始數據**

#### **4.1 插入系統配置**
```sql
INSERT INTO nca_config (config_key, config_value, config_type, description) VALUES
('system_version', '1.0.0', 'string', '系統版本'),
('max_file_size', '1073741824', 'integer', '最大文件大小(字節)'),
('whisper_model_size', 'tiny', 'string', 'Whisper模型大小'),
('genhuman_api_enabled', 'true', 'boolean', 'GenHuman API是否啟用'),
('supported_file_types', '["audio","video","image","document"]', 'json', '支持的文件類型');
```

#### **4.2 插入測試用戶**
```sql
INSERT INTO nca_users (uuid, username, email, api_key, status) VALUES
(UUID(), 'admin', 'admin@nocodearchitects.com', 'admin-api-key-2025', 1),
(UUID(), 'testuser', 'test@nocodearchitects.com', 'test-api-key-2025', 1);
```

#### **4.3 插入測試項目**
```sql
INSERT INTO nca_projects (uuid, user_id, project_name, project_type, status) VALUES
(UUID(), 1, '測試語音克隆項目', 'voice_clone', 'pending'),
(UUID(), 1, '測試數字人項目', 'digital_human', 'pending');
```

### **步驟5: 驗證創建結果**

#### **5.1 檢查表**
```sql
SHOW TABLES LIKE 'nca_%';
```
**期望結果：**
```
+-------------------+
| Tables_in_zeabur  |
+-------------------+
| nca_api_logs      |
| nca_config        |
| nca_files         |
| nca_projects      |
| nca_users         |
+-------------------+
```

#### **5.2 檢查數據**
```sql
SELECT COUNT(*) as user_count FROM nca_users;
SELECT COUNT(*) as project_count FROM nca_projects;
SELECT COUNT(*) as config_count FROM nca_config;
```

#### **5.3 查看創建的用戶**
```sql
SELECT id, username, email, status FROM nca_users;
```

#### **5.4 查看創建的項目**
```sql
SELECT id, project_name, project_type, status FROM nca_projects;
```

### **步驟6: 退出MySQL**
```sql
EXIT;
```

---

## ✅ **成功標準**

如果你看到：
- ✅ 5個表成功創建
- ✅ 2個用戶記錄
- ✅ 2個項目記錄
- ✅ 5個配置記錄

**恭喜！數據庫設置完成！**

---

## 🔧 **常見問題**

### **問題1: 連接失敗**
```bash
# 嘗試不同的連接方式
mysql -h tpe1.clusters.zeabur.com -P 30791 -u root -p
# 然後手動輸入密碼: 248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6
```

### **問題2: 權限錯誤**
確保：
1. 使用root用戶
2. 密碼正確
3. 數據庫名稱是 `zeabur`

### **問題3: 表已存在**
SQL中使用了 `DROP TABLE IF EXISTS`，會自動處理。

---

## 🎯 **下一步**

數據庫設置完成後：
1. **測試後端應用連接**
2. **訪問健康檢查端點**
3. **開始GenHuman API開發**

**準備好了嗎？讓我們開始執行！** 🚀
