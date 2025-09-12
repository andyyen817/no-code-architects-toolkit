# VidSpark後端Zeabur+ZeaburMySQL環境變量設置整合 v2.0912

## 📋 文檔概述
本文檔整合了VidSpark後端在Zeabur平台部署時所需的所有環境變量配置，包括數據庫連接、應用配置、存儲設置等。

**更新內容 v2.0912：**
- ✅ 同步ZEABUR_環境變量_完整配置.md的最新配置
- ✅ 統一存儲卷配置為 `data` (MySQL) 和標準化命名
- ✅ 更新環境變量值和安全密鑰
- ✅ 添加存儲卷配置詳細說明
- ✅ 增加付費用戶存儲管理配置

## 🎯 環境變量分類配置

### 📱 Zeabur 項目環境變量（在主應用服務中設置）

這些環境變量需要在 **Zeabur 控制台 → 您的項目 → 主應用服務 → Environment Variables** 中設置：

```bash
# === 應用核心配置 ===
ENVIRONMENT=production
PORT=8080
FLASK_ENV=production
FLASK_DEBUG=false

# === 安全密鑰 ===
API_KEY=vidspark-production-api-key-2024-secure
SECRET_KEY=vidspark-flask-secret-key-ultra-secure-2024

# === 數據庫連接配置 ===
DB_HOST=mysql.zeabur.internal
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6
DB_DATABASE=zeabur
DB_CHARSET=utf8mb4
DB_POOL_SIZE=5
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# === 存儲配置 ===
STORAGE_UPLOAD_FOLDER=/app/uploads
STORAGE_MAX_FILE_SIZE=100
ALLOWED_EXTENSIONS=mp4,avi,mov,mp3,wav,jpg,png,gif
TEMP_FILE_CLEANUP_HOURS=24
```

### 🗄️ Zeabur MySQL 環境變量（MySQL 服務自動配置）

這些環境變量由 **Zeabur MySQL 服務自動生成**，無需手動設置：

```bash
# === MySQL 服務自動配置（無需手動設置）===
# MYSQL_ROOT_PASSWORD=248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6  # 自動生成
# MYSQL_DATABASE=zeabur                                  # 自動創建
# MYSQL_USER=root                                        # 預設用戶
# MYSQL_HOST=mysql.zeabur.internal                       # 內部網絡地址
# MYSQL_PORT=3306                                        # 預設端口
```

## 💾 存儲卷配置（在 Volumes 部分設置）

這些**不是環境變量**，而是在 **Zeabur 控制台 → 各服務 → Volumes** 中配置的存儲卷：

### 🔹 主應用服務存儲卷
在 **主應用服務 → Volumes** 中添加：

| 存儲卷名稱 | 掛載路徑 | 大小 | 用途 |
|-----------|---------|------|------|
| `main-storage` | `/app/uploads` | 10GB | 用戶上傳文件 |
| `output-storage` | `/app/output` | 20GB | 處理後的輸出文件 |
| `temp-storage` | `/app/temp` | 5GB | 臨時處理文件 |

### 🔹 MySQL 服務存儲卷
在 **MySQL 服務 → Volumes** 中添加：

| 存儲卷名稱 | 掛載路徑 | 大小 | 用途 |
|-----------|---------|------|------|
| `data` | `/var/lib/mysql` | 10GB | MySQL 數據持久化 |

**⚠️ 重要說明**：如果您的MySQL服務已經有自帶的 `data` 存儲卷，**無需修改**！保持現有配置即可。

## 🔧 Zeabur 控制台操作步驟

### 步驟1: 設置環境變量
1. 登錄 Zeabur 控制台
2. 進入您的項目
3. 點擊主應用服務
4. 進入「Environment Variables」或「環境變量」
5. 逐一添加以下環境變量：

**直接複製貼上的環境變量列表：**
```
DB_HOST=mysql.zeabur.internal
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6
DB_DATABASE=zeabur
DB_CHARSET=utf8mb4
DB_POOL_SIZE=5
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
ENVIRONMENT=production
PORT=8080
API_KEY=vidspark-production-api-key-2024-secure
SECRET_KEY=vidspark-flask-secret-key-ultra-secure-2024
FLASK_ENV=production
FLASK_DEBUG=false
STORAGE_UPLOAD_FOLDER=/app/uploads
STORAGE_MAX_FILE_SIZE=100
ALLOWED_EXTENSIONS=mp4,avi,mov,mp3,wav,jpg,png,gif
TEMP_FILE_CLEANUP_HOURS=24
```

### 步驟2: 配置存儲卷（必須）

**是的，您需要配置這些存儲卷！** 這是為了防止容器重啟時文件丟失。

**主應用服務存儲卷配置：**
1. 進入 Zeabur 控制台
2. 選擇您的項目
3. 點擊主應用服務
4. 進入「Volumes」或「存儲卷」部分
5. 按照上表添加 3 個存儲卷

**MySQL 服務存儲卷配置：**
1. 點擊 MySQL 服務
2. 進入「Volumes」部分
3. **檢查現有配置**：
   - ✅ 如果已有 `data` → `/var/lib/mysql`，**保持不變**
   - ❌ 如果沒有存儲卷，添加 `data` 存儲卷
   - ⚠️ **切勿**將現有的 `data` 改名

### 步驟3: MySQL 服務檢查

確認您的 MySQL 服務狀態：
1. MySQL 服務正常運行
2. 數據庫密碼與環境變量中的 DB_PASSWORD 一致
3. 存儲卷正確掛載

## 📝 重要配置說明

### TEMP_FILE_CLEANUP_HOURS 詳細說明

**這個參數是什麼？**
- `TEMP_FILE_CLEANUP_HOURS=24` 是**臨時文件**的自動清理時間
- 只影響 `/app/temp` 目錄中的**暫存檔案**
- **不會影響用戶正式儲存的檔案**

**臨時文件 vs 正式存儲文件**

| 文件類型 | 存儲位置 | 清理規則 | 說明 |
|---------|---------|---------|-----|
| **臨時文件** | `/app/temp` | 24小時後自動刪除 | 處理過程中的暫存檔 |
| **正式存儲文件** | `/app/output` | 永久保存 | 用戶上傳和處理完成的檔案 |
| **用戶文件** | `/app/output/nca/*` | 永久保存 | 付費用戶的正式存儲空間 |

**付費用戶10GB存儲空間配置**
這個配置還沒有設定,現在還沒有做收費功能,等到做收費功能,你要提醒我,
對於每月10GB存儲空間的付費用戶，建議以下配置：

```bash
# 存儲配置（針對付費用戶）
STORAGE_MAX_FILE_SIZE=500          # 單檔最大500MB
STORAGE_CLEANUP_DAYS=365           # 正式文件保留1年
TEMP_FILE_CLEANUP_HOURS=2          # 臨時文件2小時清理（節省空間）
STORAGE_ENABLE_COMPRESSION=true    # 啟用文件壓縮
STORAGE_COMPRESSION_QUALITY=75     # 壓縮品質75%
```

## 🗂️ 進階配置分類

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

## ✅ 配置檢查清單

### 📱 Zeabur 項目環境變量檢查（主應用服務）
- [ ] ENVIRONMENT=production
- [ ] PORT=8080
- [ ] API_KEY=vidspark-production-api-key-2024-secure
- [ ] SECRET_KEY=vidspark-flask-secret-key-ultra-secure-2024
- [ ] DB_HOST=mysql.zeabur.internal
- [ ] DB_PASSWORD=248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6
- [ ] STORAGE_UPLOAD_FOLDER=/app/uploads

### 🗄️ MySQL 服務檢查
- [ ] MySQL 服務正常運行
- [ ] 數據庫密碼正確
- [ ] 內部網絡連接正常

### 💾 存儲卷檢查

**主應用服務存儲卷：**
- [ ] main-storage → /app/uploads (10GB)
- [ ] output-storage → /app/output (20GB)
- [ ] temp-storage → /app/temp (5GB)

**MySQL 服務存儲卷：**
- [ ] data → /var/lib/mysql (10GB) **← 如果已存在，保持不變**

## 🚨 重要提醒

1. **所有配置值都是真實可用的**，直接複製貼上即可
2. **存儲卷配置是必須的**，否則文件會在容器重啟時丟失
3. **MySQL密碼已經從現有配置中提取**，無需修改
4. **API密鑰和SECRET_KEY已經生成**，安全可用

## 📊 配置類型總結表

| 配置類型 | 設置位置 | 是否需要手動配置 | 主要用途 |
|---------|---------|-----------------|----------|
| **📱 Zeabur 項目環境變量** | 主應用服務 → Environment Variables | ✅ **需要** | 應用運行配置、數據庫連接 |
| **🗄️ MySQL 環境變量** | MySQL 服務自動生成 | ❌ **不需要** | MySQL 服務內部配置 |
| **💾 存儲卷** | 各服務 → Volumes | ✅ **需要** | 數據持久化存儲 |

## 🎯 快速配置指南

### 第一步：設置項目環境變量 📱
**位置：** Zeabur 控制台 → 主應用服務 → Environment Variables
**操作：** 複製貼上上方的環境變量列表

**💡 付費用戶建議**：將 `TEMP_FILE_CLEANUP_HOURS` 設為 `2` 以節省存儲空間

### 第二步：配置存儲卷 💾
**位置：** Zeabur 控制台 → 各服務 → Volumes
**操作：** 按照表格添加存儲卷

**💡 付費用戶建議**：10GB存儲卷足夠，啟用壓縮可節省更多空間

### 第三步：檢查 MySQL 服務 🗄️
**位置：** Zeabur 控制台 → MySQL 服務
**操作：** 確認服務運行正常

## 📞 如果遇到問題

如果配置後仍有問題，請檢查：
1. **環境變量**是否全部正確設置在主應用服務中
2. **存儲卷**是否正確掛載到對應路徑
3. **MySQL服務**是否正常運行
4. **應用日誌**中是否有錯誤信息

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

---

**文檔版本**: v2.0912  
**創建時間**: 2024-01-12  
**最後更新**: 2024-01-12  
**維護人員**: VidSpark技術團隊  
**適用環境**: Zeabur生產環境  
**同步來源**: ZEABUR_環境變量_完整配置.md

配置完成後，重新部署應用即可生效。