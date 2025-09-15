# 🏗️ Zeabur持久化存儲完整解決方案

## 📋 問題分析總結

### 🔍 根本原因確認
通過診斷工具分析，確認問題為：
- ✅ **數據庫記錄完整**：MySQL作為外部服務，記錄保持完整
- ❌ **物理文件丟失**：容器重啟導致非持久化存儲清空
- 🕒 **時間模式**：2025-09-10上傳的文件全部丟失，最近文件正常

### 📊 影響範圍
- 用戶上傳文件：音頻、視頻、圖片
- 處理輸出文件：剪輯、轉換、字幕等
- 數字人素材：聲音克隆、形象素材
- 臨時處理文件：中間步驟文件

## 🎯 Zeabur持久化存儲配置方案

### 1. 核心存儲卷配置

#### 📁 主要存儲目錄結構
```
/app/
├── output/                    # 主要輸出目錄 [需要持久化]
│   ├── nca/                  # NCA文件結構
│   │   ├── audio/           # 音頻文件
│   │   ├── video/           # 視頻文件
│   │   └── image/           # 圖片文件
│   ├── vidspark/            # Vidspark存儲
│   │   └── storage/         # 存儲文件
│   ├── videos/              # 舊版視頻目錄
│   ├── audio/               # 舊版音頻目錄
│   └── images/              # 舊版圖片目錄
├── temp/                     # 臨時文件 [可選持久化]
├── whisper_cache/           # Whisper模型緩存 [需要持久化]
├── voice_clone/             # 聲音克隆文件 [需要持久化]
└── digital_human/           # 數字人素材 [需要持久化]
```

#### 🔧 Zeabur配置更新

**更新 `zeabur.json` 配置：**

```json
{
  "name": "vidspark-backend",
  "services": [
    {
      "name": "vidspark-backend",
      "dockerfile": "Dockerfile.zeabur",
      "port": 8080,
      "env": {
        "API_KEY": "vidspark-backend-2025",
        "LOCAL_STORAGE_PATH": "/app/output",
        "DEBUG": "true",
        "VIDSPARK_ENABLED": "true",
        "VIDSPARK_ENVIRONMENT": "production",
        "PYTHONUNBUFFERED": "1",
        "GUNICORN_WORKERS": "2",
        "GUNICORN_TIMEOUT": "300",
        "WHISPER_CACHE_DIR": "/app/whisper_cache",
        "FFMPEG_THREADS": "2",
        "MAX_VIDEO_SIZE": "100MB",
        "WHISPER_MODEL": "tiny"
      },
      "volumes": [
        {
          "name": "main-storage",
          "mountPath": "/app/output",
          "size": "20GB"
        },
        {
          "name": "whisper-cache",
          "mountPath": "/app/whisper_cache",
          "size": "5GB"
        },
        {
          "name": "voice-clone-storage",
          "mountPath": "/app/voice_clone",
          "size": "10GB"
        },
        {
          "name": "digital-human-storage",
          "mountPath": "/app/digital_human",
          "size": "15GB"
        },
        {
          "name": "temp-storage",
          "mountPath": "/app/temp",
          "size": "5GB"
        }
      ]
    }
  ]
}
```

### 2. MySQL持久化配置

#### 🗄️ 數據庫服務配置
```json
{
  "name": "mysql-database",
  "image": "mysql:8.0",
  "env": {
    "MYSQL_ROOT_PASSWORD": "your-secure-password",
    "MYSQL_DATABASE": "vidspark_db",
    "MYSQL_USER": "vidspark_user",
    "MYSQL_PASSWORD": "your-user-password"
  },
  "volumes": [
    {
      "name": "mysql-data",
      "mountPath": "/var/lib/mysql",
      "size": "10GB"
    }
  ]
}
```

## 🚀 實施步驟

### 階段1：Zeabur控制台配置

1. **登錄Zeabur控制台**
   - 訪問 https://zeabur.com
   - 進入您的項目控制台

2. **配置持久化卷**
   ```bash
   # 主要存儲卷
   名稱: main-storage
   掛載路徑: /app/output
   大小: 20GB
   
   # Whisper緩存卷
   名稱: whisper-cache
   掛載路徑: /app/whisper_cache
   大小: 5GB
   
   # 聲音克隆存儲卷
   名稱: voice-clone-storage
   掛載路徑: /app/voice_clone
   大小: 10GB
   
   # 數字人素材存儲卷
   名稱: digital-human-storage
   掛載路徑: /app/digital_human
   大小: 15GB
   
   # 臨時存儲卷
   名稱: temp-storage
   掛載路徑: /app/temp
   大小: 5GB
   ```

3. **MySQL服務配置**
   ```bash
   # MySQL數據卷
   名稱: mysql-data
   掛載路徑: /var/lib/mysql
   大小: 10GB
   ```

### 階段2：代碼配置更新

1. **更新環境變量**
   ```python
   # 在app.py或配置文件中
   STORAGE_BASE_PATH = os.environ.get('LOCAL_STORAGE_PATH', '/app/output')
   WHISPER_CACHE_DIR = os.environ.get('WHISPER_CACHE_DIR', '/app/whisper_cache')
   VOICE_CLONE_DIR = '/app/voice_clone'
   DIGITAL_HUMAN_DIR = '/app/digital_human'
   ```

2. **確保目錄創建**
   ```python
   # 在應用啟動時創建必要目錄
   def ensure_directories():
       directories = [
           '/app/output/nca/audio',
           '/app/output/nca/video', 
           '/app/output/nca/image',
           '/app/output/vidspark/storage',
           '/app/voice_clone',
           '/app/digital_human',
           '/app/temp',
           '/app/whisper_cache'
       ]
       
       for directory in directories:
           os.makedirs(directory, exist_ok=True)
           print(f"✅ 確保目錄存在: {directory}")
   ```

### 階段3：部署和驗證

1. **部署更新**
   ```bash
   # 推送代碼更新
   git add .
   git commit -m "feat: 添加Zeabur持久化存儲配置"
   git push origin main
   ```

2. **驗證持久化**
   ```bash
   # 測試文件上傳
   curl -X POST https://vidsparkback.zeabur.app/api/file/upload \
        -H "X-API-Key: your-api-key" \
        -F "file=@test.mp4"
   
   # 重啟服務後檢查文件是否仍存在
   curl https://vidsparkback.zeabur.app/nca/files/health \
        -H "X-API-Key: your-api-key"
   ```

## 🔧 數據庫清理和恢復

### 1. 清理無效記錄

```bash
# 檢查無效記錄
curl -X GET https://vidsparkback.zeabur.app/v1/database/file-cleanup/check \
     -H "X-API-Key: your-api-key"

# 試運行清理（不實際刪除）
curl -X POST https://vidsparkback.zeabur.app/v1/database/file-cleanup/cleanup \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"dry_run": true}'

# 實際清理無效記錄
curl -X POST https://vidsparkback.zeabur.app/v1/database/file-cleanup/cleanup \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"dry_run": false}'
```

### 2. 文件統計監控

```bash
# 獲取文件統計
curl -X GET https://vidsparkback.zeabur.app/v1/database/file-cleanup/stats \
     -H "X-API-Key: your-api-key"
```

## 📊 監控和維護

### 1. 存儲使用監控

```python
# 添加存儲監控端點
@app.route('/storage/usage')
@authenticate
def storage_usage():
    """監控存儲使用情況"""
    usage = {}
    
    for path in ['/app/output', '/app/voice_clone', '/app/digital_human']:
        if os.path.exists(path):
            total_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(path)
                for filename in filenames
            )
            usage[path] = {
                'size_bytes': total_size,
                'size_mb': round(total_size / 1024 / 1024, 2)
            }
    
    return jsonify(usage)
```

### 2. 自動備份策略

```python
# 定期備份重要文件
def backup_critical_files():
    """備份關鍵文件到雲存儲"""
    critical_paths = [
        '/app/voice_clone',
        '/app/digital_human'
    ]
    
    for path in critical_paths:
        # 實施備份邏輯
        pass
```

## 🎯 預期效果

### ✅ 解決的問題
1. **文件持久性**：容器重啟後文件不再丟失
2. **數據一致性**：數據庫記錄與物理文件保持同步
3. **用戶體驗**：上傳的文件可以長期訪問
4. **系統穩定性**：減少因文件丟失導致的錯誤

### 📈 性能改進
1. **緩存效率**：Whisper模型緩存持久化
2. **處理速度**：減少重複下載和處理
3. **存儲優化**：合理的目錄結構和大小配置

### 🔒 安全增強
1. **數據保護**：重要文件不會意外丟失
2. **備份策略**：多層次的數據保護
3. **監控告警**：及時發現存儲問題

## 📞 技術支援

如果在實施過程中遇到問題，請：
1. 檢查Zeabur控制台的卷配置
2. 驗證環境變量設置
3. 查看應用日誌中的存儲相關錯誤
4. 使用提供的診斷工具檢查文件狀態

---

**📝 注意事項：**
- 持久化卷配置後需要重新部署應用
- 建議在低峰期進行配置更新
- 定期監控存儲使用情況，避免空間不足
- 保持數據庫記錄與物理文件的一致性
