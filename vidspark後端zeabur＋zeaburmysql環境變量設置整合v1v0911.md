# VidSpark後端Zeabur+ZeaburMySQL環境變量設置整合 v1.0911

## 📋 文檔概述
本文檔整合了VidSpark後端在Zeabur平台部署時所需的所有環境變量配置，包括數據庫連接、應用配置、存儲設置等。

## 🗂️ 配置分類

### 1. 數據庫連接配置 🗄️

#### MySQL基礎連接
```bash
# 數據庫類型
DB_CONNECTION=mysql

# 數據庫服務器配置
DB_HOST=mysql.zeabur.internal
DB_PORT=3306
DB_DATABASE=zeabur
DB_USERNAME=root
DB_PASSWORD=248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6

# 字符集配置
DB_CHARSET=utf8mb4
DB_COLLATION=utf8mb4_unicode_ci
```

#### 連接池配置
```bash
# 連接池大小設置
DB_POOL_SIZE=5
DB_POOL_MAX=10
DB_POOL_MIN=2

# 超時設置
DB_POOL_TIMEOUT=30
DB_TIMEOUT=30000

# 連接回收時間
DB_POOL_RECYCLE=3600
DB_MAX_OVERFLOW=20
```

#### SQLAlchemy配置
```bash
# SQLAlchemy URI (自動生成，無需手動設置)
# SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:fhlkzgNuRQL79C5eFb4036vX2T18YdAn@mysql.zeabur.internal:3306/zeabur?charset=utf8mb4

# SQLAlchemy選項
SQLALCHEMY_TRACK_MODIFICATIONS=false
SQLALCHEMY_ECHO=false
```

### 2. 應用核心配置 🚀

#### Flask應用配置
```bash
# 應用環境
FLASK_ENV=production
FLASK_DEBUG=false

# 應用密鑰
API_KEY=production-api-key-2024
SECRET_KEY=your-secret-key-here

# 應用端口
PORT=5000
```

#### 安全配置
```bash
# CORS配置
CORS_ORIGINS=*
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=Content-Type,Authorization

# JWT配置（如果使用）
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
```

### 3. 文件存儲配置 📁

#### 基礎存儲設置
```bash
# 存儲路徑
STORAGE_PATH=/app/output
UPLOAD_PATH=/app/uploads
TEMP_PATH=/app/temp

# 文件大小限制
MAX_FILE_SIZE=100
MAX_CONTENT_LENGTH=104857600

# 允許的文件類型
ALLOWED_EXTENSIONS=mp4,avi,mov,mp3,wav,jpg,png,gif
```

#### 臨時文件管理
```bash
# 臨時文件清理
TEMP_FILE_CLEANUP_HOURS=24
AUTO_CLEANUP_ENABLED=true

# 文件處理超時
FILE_PROCESSING_TIMEOUT=300
```

### 4. GenHuman API配置 🤖

#### API連接設置
```bash
# GenHuman API基礎配置
GENHUMAN_API_BASE_URL=https://api.yidevs.com
GENHUMAN_API_KEY=your-genhuman-api-key
GENHUMAN_API_TIMEOUT=300

# API重試配置
API_RETRY_COUNT=3
API_RETRY_DELAY=5
```

#### 功能開關
```bash
# 功能啟用開關
VOICE_CLONE_ENABLED=true
DIGITAL_HUMAN_ENABLED=true
TEXT_TO_SPEECH_ENABLED=true
```

### 5. 日誌和監控配置 📊

#### 日誌配置
```bash
# 日誌級別
LOG_LEVEL=INFO
DEBUG_MODE=false

# 日誌文件
LOG_FILE=/app/logs/app.log
ERROR_LOG_FILE=/app/logs/error.log
```

#### 監控配置
```bash
# 健康檢查
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=60

# 性能監控
PERFORMANCE_MONITORING=true
METRICS_ENABLED=true
```

### 6. 緩存配置 ⚡

#### Redis配置（如果使用）
```bash
# Redis連接
REDIS_URL=redis://redis.zeabur.internal:6379
REDIS_DB=0
REDIS_PASSWORD=

# 緩存設置
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=300
```

## 🔧 完整環境變量清單

### Zeabur環境變量設置（複製貼上版本）

```bash
# === 數據庫配置 ===
DB_CONNECTION=mysql
DB_HOST=mysql.zeabur.internal
DB_PORT=3306
DB_DATABASE=zeabur
DB_USERNAME=root
DB_PASSWORD=fhlkzgNuRQL79C5eFb4036vX2T18YdAn
DB_CHARSET=utf8mb4
DB_POOL_SIZE=5
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# === 應用配置 ===
FLASK_ENV=production
API_KEY=production-api-key-2024
PORT=5000

# === 存儲配置 ===
STORAGE_PATH=/app/output
MAX_FILE_SIZE=100
TEMP_FILE_CLEANUP_HOURS=24

# === GenHuman API ===
GENHUMAN_API_BASE_URL=https://api.yidevs.com
GENHUMAN_API_TIMEOUT=300

# === 日誌配置 ===
LOG_LEVEL=INFO
DEBUG_MODE=false
```

## 📝 環境變量設置步驟

### 方法1：通過Zeabur控制台設置
1. 登入Zeabur控制台
2. 進入VidSpark後端項目
3. 點擊應用服務
4. 進入「環境變量」頁面
5. 逐一添加上述環境變量
6. 保存並重啟服務

### 方法2：通過.env文件（本地開發）
```bash
# 創建.env文件
cp .env.example .env

# 編輯.env文件，添加上述配置
vim .env
```

### 方法3：通過Zeabur CLI
```bash
# 安裝Zeabur CLI
npm install -g @zeabur/cli

# 登入
zeabur auth login

# 設置環境變量
zeabur env set DB_HOST=mysql.zeabur.internal
zeabur env set DB_PASSWORD=fhlkzgNuRQL79C5eFb4036vX2T18YdAn
# ... 其他變量
```

## 🔍 配置驗證清單

### 必須檢查項目 ✅
- [ ] DB_HOST設置為 `mysql.zeabur.internal`
- [ ] DB_PASSWORD正確無誤
- [ ] API_KEY已設置
- [ ] STORAGE_PATH路徑正確
- [ ] 所有必需的環境變量都已設置

### 可選檢查項目 ⚙️
- [ ] 連接池配置合理
- [ ] 日誌級別適當
- [ ] 文件大小限制合理
- [ ] 緩存配置（如果使用）

## 🚨 安全注意事項

### 敏感信息保護
1. **數據庫密碼**：絕不在代碼中硬編碼
2. **API密鑰**：使用環境變量管理
3. **JWT密鑰**：定期更換
4. **訪問控制**：限制環境變量訪問權限

### 最佳實踐
1. 定期備份環境變量配置
2. 使用不同環境的不同配置
3. 監控敏感變量的使用情況
4. 實施配置變更審計

## 🔄 配置更新流程

### 更新步驟
1. 備份當前配置
2. 更新環境變量
3. 測試配置有效性
4. 重啟應用服務
5. 驗證功能正常

### 回滾計劃
1. 保留舊配置備份
2. 準備快速回滾腳本
3. 監控服務狀態
4. 必要時執行回滾

## 📊 配置模板

### 開發環境模板
```bash
FLASK_ENV=development
DEBUG_MODE=true
LOG_LEVEL=DEBUG
DB_DATABASE=zeabur_dev
```

### 測試環境模板
```bash
FLASK_ENV=testing
DEBUG_MODE=false
LOG_LEVEL=INFO
DB_DATABASE=zeabur_test
```

### 生產環境模板
```bash
FLASK_ENV=production
DEBUG_MODE=false
LOG_LEVEL=WARNING
DB_DATABASE=zeabur
```

## 📞 技術支持

### 常見問題
1. **數據庫連接失敗**：檢查DB_HOST和密碼
2. **文件上傳失敗**：檢查STORAGE_PATH權限
3. **API調用超時**：調整TIMEOUT設置
4. **內存不足**：調整連接池大小

### 聯繫方式
- 技術文檔：參考相關MD文件
- 錯誤排除：查看日誌文件
- 緊急支持：聯繫開發團隊

---

**文檔版本**: v1.0911  
**創建時間**: 2024-01-11  
**最後更新**: 2024-01-11  
**維護人員**: VidSpark技術團隊  
**適用環境**: Zeabur生產環境