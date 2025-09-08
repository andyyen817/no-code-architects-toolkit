# ZEABUR 環境變量設置完整指南

## 🎯 目標
為No-Code Architects Toolkit後端配置完整的ZEABUR環境變量，結合前端成功經驗和後端技術需求

## 📊 信息來源
- ✅ **前端成功經驗**：來自`前端支援后端genhumanapi调用前端技术支援任务执行清单-前端反馈v1v0908.md`
- ✅ **後端技術需求**：基於Flask + Python架構
- ✅ **數據庫配置**：ZEABUR MySQL內網連接

---

## 🚀 **ZEABUR環境變量完整清單**

### **1. 基礎Flask應用配置**
```bash
# Flask應用基礎設置
API_KEY=production-api-key-2024
LOCAL_STORAGE_PATH=/app/output
DEBUG=false
FLASK_ENV=production
SECRET_KEY=nCa2025$K8mQ9#xR7vL3@pY6wE4tU1zA9sN5bM2dF8cH6jG

# Python運行環境
PYTHONUNBUFFERED=1
PYTHONIOENCODING=utf-8
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=/app
```

### **2. Whisper AI 語音處理配置**
```bash
# Whisper模型配置（基於成功運行經驗）
WHISPER_MODEL_SIZE=tiny
WHISPER_COMPUTE_TYPE=int8
WHISPER_CACHE_DIR=/app/whisper_cache
WHISPER_DEVICE=cpu
WHISPER_LANGUAGE=auto
```

### **3. 服務地址配置**
```bash
# ZEABUR服務地址
SERVICE_BASE_URL=https://vidsparkback.zeabur.app
ZEABUR_INTERNAL_URL=http://vidsparkback.zeabur.internal:8080
ZEABUR_EXTERNAL_URL=https://vidsparkback.zeabur.app
SERVER_PORT=8080
```

### **4. 文件處理配置**
```bash
# 文件上傳和處理限制（基於前端成功經驗）
MAX_CONTENT_LENGTH=1073741824
FILE_UPLOAD_MAX_SIZE=1000M
FILE_PROCESSING_TIMEOUT=1800
TEMP_FILE_CLEANUP_HOURS=24

# 文件存儲路徑
UPLOAD_FOLDER=/app/output
TEMP_FOLDER=/app/temp
STATIC_FOLDER=/app/static
```

### **5. GenHuman API配置（來自前端成功經驗）**
```bash
# GenHuman API基礎配置
GENHUMAN_API_BASE=https://api.yidevs.com
GENHUMAN_PRODUCTION_TOKEN=08D7EE7F91D258F27B4ADDF59CDDDEDE.1E95F76130BA23D37CE7BBBD69B19CCF.KYBVDWNR
GENHUMAN_CALLBACK_BASE_URL=https://vidsparkback.zeabur.app
GENHUMAN_WEBHOOK_SECRET=vidspark_webhook_2025
GENHUMAN_API_TIMEOUT=300
GENHUMAN_MAX_RETRIES=3
```

---

## 🗃️ **ZEABUR MySQL數據庫配置**

### **1. 數據庫連接配置**
```bash
# MySQL連接配置（使用獨立ZEABUR MySQL實例）
DB_CONNECTION=mysql
DB_HOST=tpe1.clusters.zeabur.com
DB_PORT=30791
DB_DATABASE=zeabur
DB_USERNAME=root
DB_PASSWORD=248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6
DB_CHARSET=utf8mb4
DB_COLLATION=utf8mb4_unicode_ci
```

### **2. 數據庫連接池配置**
```bash
# SQLAlchemy連接池配置
DB_POOL_SIZE=5
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_MAX_OVERFLOW=10
DB_POOL_PRE_PING=true
```

### **3. 數據庫安全配置**
```bash
# 數據庫安全設置
DB_SSL_MODE=disabled
DB_CONNECT_TIMEOUT=60
DB_READ_TIMEOUT=60
DB_WRITE_TIMEOUT=60
DB_AUTO_RECONNECT=true
```

---

## ⚙️ **ZEABUR控制台設置步驟**

### **步驟1: 進入項目設置**
1. 登錄 https://zeabur.com
2. 找到你的 No-Code Architects Toolkit 項目
3. 點擊項目進入詳情頁面
4. 找到 "Environment Variables" 標籤

### **步驟2: 添加基礎環境變量**
**🚨 重要**：一個一個添加，確保每個都正確設置

#### **基礎Flask配置（必需）**
```
變量名: API_KEY
變量值: production-api-key-2024

變量名: LOCAL_STORAGE_PATH
變量值: /app/output

變量名: DEBUG
變量值: false

變量名: FLASK_ENV
變量值: production

變量名: SECRET_KEY
變量值: nCa2025$K8mQ9#xR7vL3@pY6wE4tU1zA9sN5bM2dF8cH6jG
說明: Flask安全密鑰，用於Session加密和CSRF保護，請使用強隨機字符串

變量名: PYTHONUNBUFFERED
變量值: 1

變量名: PYTHONIOENCODING
變量值: utf-8
```

#### **Whisper AI配置（必需）**
```
變量名: WHISPER_MODEL_SIZE
變量值: tiny

變量名: WHISPER_COMPUTE_TYPE
變量值: int8

變量名: WHISPER_CACHE_DIR
變量值: /app/whisper_cache
```

#### **服務地址配置（必需）**
```
變量名: SERVICE_BASE_URL
變量值: https://vidsparkback.zeabur.app

變量名: SERVER_PORT
變量值: 8080
```

### **步驟3: 添加數據庫環境變量**
#### **數據庫連接（必需）**
```
變量名: DB_CONNECTION
變量值: mysql

變量名: DB_HOST
變量值: tpe1.clusters.zeabur.com

變量名: DB_PORT
變量值: 30791

變量名: DB_DATABASE
變量值: zeabur

變量名: DB_USERNAME
變量值: root

變量名: DB_PASSWORD
變量值: 248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6

變量名: DB_CHARSET
變量值: utf8mb4
```

#### **連接池配置（推薦）**
```
變量名: DB_POOL_SIZE
變量值: 5

變量名: DB_POOL_TIMEOUT
變量值: 30

變量名: DB_POOL_RECYCLE
變量值: 3600
```

### **步驟4: 添加GenHuman API配置**
#### **API基礎配置（如需GenHuman功能）**
```
變量名: GENHUMAN_API_BASE
變量值: https://api.yidevs.com

變量名: GENHUMAN_PRODUCTION_TOKEN
變量值: 08D7EE7F91D258F27B4ADDF59CDDDEDE.1E95F76130BA23D37CE7BBBD69B19CCF.KYBVDWNR

變量名: GENHUMAN_CALLBACK_BASE_URL
變量值: https://vidsparkback.zeabur.app

變量名: GENHUMAN_WEBHOOK_SECRET
變量值: vidspark_webhook_2025
```

### **步驟5: 添加文件處理配置**
#### **文件上傳配置（推薦）**
```
變量名: MAX_CONTENT_LENGTH
變量值: 1073741824

變量名: FILE_UPLOAD_MAX_SIZE
變量值: 1000M

變量名: FILE_PROCESSING_TIMEOUT
變量值: 1800
```

---

## 🗄️ **MySQL數據庫設置步驟**

### **方案1: 使用現有數據庫（推薦）**
使用前端已經配置成功的MySQL實例，創建新的數據庫：

#### **步驟1: 連接測試**
```bash
# 使用你的ZEABUR MySQL連接信息
mysqlsh --sql --host=tpe1.clusters.zeabur.com --port=30791 --user=root --password=248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6 --schema=zeabur
```

#### **步驟2: 確認數據庫**
```sql
-- 確認當前數據庫
SHOW DATABASES;
USE zeabur;

-- 檢查當前表格
SHOW TABLES;
```

#### **步驟3: 創建數據表**
```sql
-- 用戶表
CREATE TABLE `nca_users` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) NOT NULL COMMENT '用戶唯一標識',
  `username` varchar(50) NOT NULL COMMENT '用戶名',
  `email` varchar(100) NOT NULL COMMENT '郵箱',
  `password_hash` varchar(255) NOT NULL COMMENT '密碼哈希',
  `status` tinyint(1) DEFAULT 1 COMMENT '狀態 1-正常 0-禁用',
  `api_key` varchar(64) DEFAULT NULL COMMENT '用戶API密鑰',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用戶表';

-- GenHuman項目表
CREATE TABLE `nca_genhuman_projects` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) NOT NULL COMMENT '項目唯一標識',
  `user_id` bigint(20) UNSIGNED NOT NULL COMMENT '用戶ID',
  `project_name` varchar(200) NOT NULL COMMENT '項目名稱',
  `project_type` enum('voice_clone','digital_human','text_to_speech') NOT NULL COMMENT '項目類型',
  `status` enum('pending','processing','completed','failed','cancelled') DEFAULT 'pending' COMMENT '項目狀態',
  `config_json` json COMMENT '項目配置JSON',
  `result_data` json COMMENT '結果數據JSON',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  KEY `idx_user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `nca_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='GenHuman項目表';

-- 文件管理表
CREATE TABLE `nca_files` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) NOT NULL COMMENT '文件唯一標識',
  `user_id` bigint(20) UNSIGNED NOT NULL COMMENT '用戶ID',
  `project_id` bigint(20) UNSIGNED DEFAULT NULL COMMENT '關聯項目ID',
  `file_name` varchar(255) NOT NULL COMMENT '原始文件名',
  `file_type` enum('audio','video','image','text','result') NOT NULL COMMENT '文件類型',
  `file_size` bigint(20) NOT NULL COMMENT '文件大小(字節)',
  `file_path` varchar(500) NOT NULL COMMENT '文件存儲路徑',
  `file_url` varchar(500) NOT NULL COMMENT '文件訪問URL',
  `status` enum('uploading','processing','completed','failed') DEFAULT 'uploading' COMMENT '處理狀態',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  KEY `idx_user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `nca_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文件管理表';

-- API調用記錄表
CREATE TABLE `nca_api_calls` (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) NOT NULL COMMENT '調用唯一標識',
  `user_id` bigint(20) UNSIGNED NOT NULL COMMENT '用戶ID',
  `api_endpoint` varchar(200) NOT NULL COMMENT 'API端點',
  `request_data` json COMMENT '請求數據',
  `response_data` json COMMENT '響應數據',
  `response_code` int(3) NOT NULL COMMENT 'HTTP狀態碼',
  `success` tinyint(1) NOT NULL COMMENT '是否成功',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_uuid` (`uuid`),
  KEY `idx_user_id` (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `nca_users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API調用記錄表';
```

### **方案2: 創建獨立數據庫（備選）**
如果需要完全獨立的數據庫實例：

1. 在ZEABUR控制台創建新的MySQL服務
2. 獲取新的連接信息
3. 更新環境變量中的數據庫配置

---

## ✅ **設置完成驗證**

### **步驟1: 應用重啟**
設置完環境變量後，ZEABUR會自動重新部署應用。等待2-5分鐘。

### **步驟2: 健康檢查**
訪問：`https://vidsparkback.zeabur.app/health`

期望響應：
```json
{
  "status": "healthy",
  "build": "BUILD_NUMBER",
  "environment": "production",
  "database": "connected"
}
```

### **步驟3: 數據庫連接測試**
訪問：`https://vidsparkback.zeabur.app/v1/toolkit/test`

確認應用能正常連接數據庫。

### **步驟4: 功能測試**
使用之前創建的測試頁面測試基礎功能：
- 文件上傳功能
- API認證功能
- 數據庫讀寫功能

---

## 🚨 **常見問題解決**

### **問題1: 應用啟動失敗**
**症狀**：環境變量設置後應用無法啟動

**檢查清單**：
- [ ] 確認所有必需環境變量都已設置
- [ ] 檢查變量名稱拼寫是否正確
- [ ] 確認變量值格式是否正確
- [ ] 查看ZEABUR部署日誌錯誤信息

### **問題2: 數據庫連接失敗**
**症狀**：應用啟動但無法連接數據庫

**解決步驟**：
1. 確認數據庫環境變量設置正確
2. 檢查數據庫名稱是否存在
3. 驗證數據庫用戶權限
4. 測試網絡連通性

### **問題3: GenHuman API調用失敗**
**症狀**：GenHuman相關功能無法使用

**解決步驟**：
1. 確認GENHUMAN_PRODUCTION_TOKEN正確
2. 檢查GENHUMAN_API_BASE地址
3. 驗證回調URL可訪問性
4. 查看API調用錯誤日誌

---

## 📋 **設置檢查清單**

### **基礎配置檢查**
- [ ] API_KEY已設置
- [ ] LOCAL_STORAGE_PATH已配置
- [ ] FLASK_ENV設為production
- [ ] PYTHONUNBUFFERED設為1
- [ ] SERVICE_BASE_URL正確

### **Whisper配置檢查**
- [ ] WHISPER_MODEL_SIZE設為tiny
- [ ] WHISPER_COMPUTE_TYPE設為int8
- [ ] WHISPER_CACHE_DIR已設置

### **數據庫配置檢查**
- [ ] DB_HOST設為mysql.zeabur.internal
- [ ] DB_DATABASE設為nocode_architects_backend
- [ ] DB_USERNAME和DB_PASSWORD正確
- [ ] DB_CHARSET設為utf8mb4
- [ ] 數據庫連接池配置已設置

### **GenHuman API配置檢查**
- [ ] GENHUMAN_API_BASE正確
- [ ] GENHUMAN_PRODUCTION_TOKEN已設置
- [ ] GENHUMAN_CALLBACK_BASE_URL正確
- [ ] GENHUMAN_WEBHOOK_SECRET已設置

### **驗證檢查**
- [ ] 應用重新部署完成
- [ ] 健康檢查通過
- [ ] 數據庫連接成功
- [ ] 基礎功能測試通過

---

## 🎯 **下一步行動**

### **立即執行**
1. **設置環境變量**：按照本指南在ZEABUR控制台設置所有環境變量
2. **創建數據庫**：創建`nocode_architects_backend`數據庫和表結構
3. **驗證配置**：運行健康檢查和基礎功能測試

### **後續開發**
1. **開發GenHuman API接口**：基於前端成功經驗開發後端API
2. **數據遷移**：如需要，將前端數據遷移到後端數據庫
3. **前後端聯調**：完成前後端API對接

---

**📅 創建日期**: 2025-01-09  
**📊 版本**: v1.0908  
**🎯 目標**: 統合前端成功經驗，提供完整的ZEABUR環境配置指南  
**📋 基於**: 前端反饋 + 後端技術需求 + ZEABUR平台特性  
**⚡ 期望效果**: 一次性正確配置，避免反覆調試環境問題