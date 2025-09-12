# Zeabur 部署和持久化存儲配置指南

## 📋 概述

本指南詳細說明如何在 Zeabur 平台上配置持久化存儲，解決容器重啟導致文件丟失的問題，並提供完整的部署流程。

## 🎯 解決的問題

### 問題描述
- **根本原因**: Zeabur 容器重啟時，非持久化存儲的數據會被清空
- **影響範圍**: 用戶上傳的文件、生成的內容、緩存數據等
- **具體表現**: 數據庫記錄存在，但物理文件丟失，導致 404 錯誤

### 解決方案
- 配置 Zeabur 持久化存儲卷
- 更新應用存儲路徑配置
- 實施自動存儲初始化
- 添加存儲監控和管理功能

## 🔧 Zeabur 控制台配置

### 1. 登錄 Zeabur 控制台

1. 訪問 [Zeabur Dashboard](https://dash.zeabur.com)
2. 登錄您的帳戶
3. 選擇您的項目

### 2. 配置持久化存儲卷

#### 主應用服務配置

1. **進入服務設置**
   - 點擊您的主應用服務
   - 進入「Settings」或「設置」頁面
   - 找到「Volumes」或「存儲卷」部分

2. **添加存儲卷**
   
   **主輸出存儲卷**
   ```
   名稱: main-storage
   掛載路徑: /app/output
   大小: 20GB (建議初始大小)
   ```
   
   **Whisper 緩存存儲卷**
   ```
   名稱: whisper-cache
   掛載路徑: /app/whisper_cache
   大小: 5GB
   ```
   
   **聲音克隆存儲卷**
   ```
   名稱: voice-clone-storage
   掛載路徑: /app/voice_clone
   大小: 10GB
   ```
   
   **數字人素材存儲卷**
   ```
   名稱: digital-human-storage
   掛載路徑: /app/digital_human
   大小: 15GB
   ```
   
   **臨時文件存儲卷**
   ```
   名稱: temp-storage
   掛載路徑: /app/temp
   大小: 5GB
   ```

#### MySQL 服務配置

1. **進入 MySQL 服務設置**
   - 點擊您的 MySQL 服務
   - 進入「Settings」頁面

2. **添加數據庫存儲卷**
   ```
   名稱: mysql-data
   掛載路徑: /var/lib/mysql
   大小: 10GB (根據數據量調整)
   ```

### 3. 環境變量配置

在主應用服務的環境變量中添加或更新：

```bash
# 存儲路徑配置
LOCAL_STORAGE_PATH=/app/output
WHISPER_CACHE_DIR=/app/whisper_cache
VOICE_CLONE_DIR=/app/voice_clone
DIGITAL_HUMAN_DIR=/app/digital_human

# 數據庫配置 (如果需要)
DATABASE_URL=mysql://username:password@mysql-service:3306/database_name

# API 配置
API_KEY=your-production-api-key-here
```

## 📁 代碼配置更新

### 1. zeabur.json 配置文件

項目中的 `zeabur.json` 已更新為：

```json
{
  "name": "no-code-architects-toolkit",
  "dockerfile": "Dockerfile",
  "ports": [8080],
  "env": {
    "LOCAL_STORAGE_PATH": "/app/output",
    "VOICE_CLONE_DIR": "/app/voice_clone",
    "DIGITAL_HUMAN_DIR": "/app/digital_human",
    "WHISPER_CACHE_DIR": "/app/whisper_cache"
  },
  "volumes": {
    "main-storage": {
      "mount": "/app/output",
      "size": "20GB"
    },
    "whisper-cache": {
      "mount": "/app/whisper_cache",
      "size": "5GB"
    },
    "voice-clone-storage": {
      "mount": "/app/voice_clone",
      "size": "10GB"
    },
    "digital-human-storage": {
      "mount": "/app/digital_human",
      "size": "15GB"
    },
    "temp-storage": {
      "mount": "/app/temp",
      "size": "5GB"
    }
  }
}
```

### 2. 存儲管理系統

項目已添加完整的存儲管理系統：

- **存儲管理器**: `services/storage_manager.py`
- **API 端點**: `routes/v1/storage/storage_management.py`
- **自動初始化**: 應用啟動時自動創建目錄結構

## 🚀 部署流程

### 1. 準備部署

1. **確認代碼更新**
   ```bash
   git add .
   git commit -m "feat: 添加 Zeabur 持久化存儲配置和存儲管理系統"
   git push origin main
   ```

2. **檢查配置文件**
   - 確認 `zeabur.json` 配置正確
   - 檢查環境變量設置

### 2. Zeabur 部署

1. **觸發部署**
   - Zeabur 會自動檢測到 Git 推送
   - 或在控制台手動觸發部署

2. **監控部署過程**
   - 查看構建日誌
   - 確認存儲卷正確掛載
   - 檢查應用啟動日誌

3. **驗證部署**
   - 訪問健康檢查端點: `GET /health`
   - 檢查存儲狀態: `GET /api/v1/storage/status`
   - 測試文件上傳功能

## 🔍 驗證和測試

### 1. 存儲系統驗證

**檢查存儲狀態**
```bash
curl -X GET "https://your-app.zeabur.app/api/v1/storage/status"
```

**檢查存儲健康**
```bash
curl -X GET "https://your-app.zeabur.app/api/v1/storage/health"
```

**查看存儲使用情況** (需要 API 密鑰)
```bash
curl -X GET "https://your-app.zeabur.app/api/v1/storage/usage" \
  -H "X-API-Key: your-api-key"
```

### 2. 功能測試

1. **文件上傳測試**
   - 上傳測試文件
   - 確認文件正確保存
   - 檢查數據庫記錄

2. **容器重啟測試**
   - 在 Zeabur 控制台重啟應用
   - 確認文件仍然存在
   - 驗證功能正常

3. **存儲管理測試**
   - 測試存儲初始化 API
   - 測試臨時文件清理
   - 驗證監控功能

## 📊 監控和維護

### 1. 存儲監控

**定期檢查存儲使用情況**
```bash
# 每日檢查腳本
curl -X GET "https://your-app.zeabur.app/api/v1/storage/usage" \
  -H "X-API-Key: your-api-key" | jq '.data.total_size_gb'
```

**設置告警閾值**
- 存儲使用量 > 30GB: 警告
- 存儲使用量 > 40GB: 緊急

### 2. 定期維護

**清理臨時文件** (建議每日執行)
```bash
curl -X POST "https://your-app.zeabur.app/api/v1/storage/cleanup" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"max_age_hours": 24}'
```

**數據庫清理** (建議每週執行)
```bash
curl -X POST "https://your-app.zeabur.app/api/v1/database/cleanup_invalid_records" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

### 3. 備份策略

1. **Zeabur 自動備份**
   - 啟用 Zeabur 的自動備份功能
   - 設置備份頻率和保留期

2. **手動備份**
   - 定期下載重要文件
   - 導出數據庫數據

## 🚨 故障排除

### 1. 常見問題

**問題**: 存儲卷未正確掛載
```bash
# 檢查掛載點
ls -la /app/output
df -h | grep /app
```

**問題**: 權限錯誤
```bash
# 檢查目錄權限
ls -la /app/
whoami
```

**問題**: 存儲空間不足
```bash
# 檢查磁盤使用情況
du -sh /app/output/*
df -h /app/output
```

### 2. 日誌檢查

**應用日誌**
- 在 Zeabur 控制台查看應用日誌
- 搜索存儲相關的錯誤信息

**存儲初始化日誌**
```
🚀 正在初始化存儲系統...
✅ 存儲系統初始化成功
```

## 📈 性能優化

### 1. 存儲優化

- **定期清理**: 自動清理過期的臨時文件
- **壓縮存儲**: 對大文件進行壓縮
- **分層存儲**: 將不同類型的文件存儲在不同的卷中

### 2. 監控優化

- **實時監控**: 設置存儲使用量告警
- **性能監控**: 監控文件讀寫性能
- **容量規劃**: 根據使用趨勢調整存儲容量

## 🔮 未來改進

### 1. 自動擴容
- 實施存儲使用量監控
- 自動申請額外存儲空間
- 智能文件歸檔

### 2. 多區域備份
- 實施跨區域數據備份
- 災難恢復計劃
- 數據同步機制

### 3. 高級功能
- CDN 集成
- 文件版本控制
- 智能緩存策略

## 📞 技術支援

如果在配置過程中遇到問題，請：

1. 檢查 Zeabur 控制台的部署日誌
2. 使用存儲管理 API 進行診斷
3. 查看應用健康檢查端點
4. 聯繫技術支援團隊

---

**配置完成後，您的應用將具備完整的持久化存儲能力，確保數據在容器重啟後仍然保留。**