# 🚀 ZEABUR 環境變數配置指南

## 📋 必填環境變數

### 🔑 基礎認證配置
```bash
# API認證金鑰（必填）
API_KEY=vidspark-production-api-key-2024-secure

# 本地存儲路徑（必填）
LOCAL_STORAGE_PATH=/app/output

# 調試模式（生產環境必填）
DEBUG=false

# Flask環境
FLASK_ENV=production
```

### 🎵 AI語音處理配置
```bash
# Whisper模型配置（重要）
WHISPER_MODEL=small

# 語音處理線程數
WHISPER_THREADS=2

# VAD過濾
WHISPER_VAD_FILTER=true

# Whisper緩存目錄
WHISPER_CACHE_DIR=/app/whisper_cache
```

### 🎬 FFmpeg視頻處理配置
```bash
# FFmpeg線程數
FFMPEG_THREADS=2

# 視頻編碼預設
FFMPEG_PRESET=fast

# 視頻質量控制
FFMPEG_CRF=23
```

### ⚙️ Gunicorn服務器配置
```bash
# Gunicorn超時設定（重要）
GUNICORN_TIMEOUT=600

# Gunicorn工作進程數
GUNICORN_WORKERS=2

# 最大隊列長度
MAX_QUEUE_LENGTH=5
```

### 🌐 VIDSPARK專用配置
```bash
# VIDSPARK功能啟用
VIDSPARK_ENABLED=true

# 運行環境
VIDSPARK_ENVIRONMENT=production

# 垂直視頻默認格式
VIDSPARK_DEFAULT_ASPECT=9:16

# 默認分辨率
VIDSPARK_DEFAULT_RESOLUTION=1080x1920

# 最大視頻時長（秒）
VIDSPARK_MAX_DURATION=60
```

### 🔧 系統配置
```bash
# Python編碼
PYTHONUNBUFFERED=1
PYTHONIOENCODING=utf-8

# 存儲目錄
VOICE_CLONE_DIR=/app/voice_clone
DIGITAL_HUMAN_DIR=/app/digital_human
```

## 📝 Zeabur部署步驟

### 1. 登入Zeabur
- 訪問：https://zeabur.com
- 使用GitHub帳號登入

### 2. 創建新項目
- 項目名稱：`vidspark-backend`
- 區域選擇：Singapore 或 Hong Kong

### 3. 連接GitHub倉庫
- 選擇：`andyyen817/no-code-architects-toolkit`
- 分支：`main`

### 4. 配置服務設定
- 服務名稱：`vidspark-api`
- 端口：`8080`
- 構建方式：自動檢測Docker

### 5. 設置環境變數
將上述所有環境變數複製到Zeabur的環境變數設置中。

### 6. 部署並測試
- 點擊部署
- 等待部署完成
- 測試API端點：`https://your-app.zeabur.app/health`

## ✅ 部署檢查清單

- [ ] GitHub代碼已推送
- [ ] Zeabur項目已創建
- [ ] GitHub倉庫已連接
- [ ] 環境變數已設置
- [ ] 服務配置已完成
- [ ] 部署已啟動
- [ ] 健康檢查通過
- [ ] API測試成功

## 🎯 測試端點

部署完成後，在以下URL進行測試：
- 健康檢查：`https://vidsparkback.zeabur.app/health`
- NCA測試：`https://vidsparkback.zeabur.app/test/nca`
- 音頻轉錄：`https://vidsparkback.zeabur.app/v1/media/transcribe`
- 影片字幕：`https://vidsparkback.zeabur.app/v1/video/caption`

---

**📅 創建日期**：2025-01-17  
**🎯 目標**：完整部署VIDSPARK到Zeabur  
**✅ 狀態**：準備部署