# GenHuman API 完整調用文檔

## 🎯 **文檔目的**
為後端開發者提供完整的GenHuman API調用指南，包含測試頁面和成功的API調用流程。

---

## 📋 **GenHuman API 測試頁面使用指南**

### **測試頁面訪問地址**
```
雲端測試頁面：https://vidsparkback.zeabur.app/test/genhuman
本地測試頁面：D:\no-code-architects-toolkit\no-code-architects-toolkit\genhuman_cloud_test.html
```

### **成功的API調用流程**
```
步驟1：免費聲音克隆 → 獲取voice_id
步驟2：付費聲音合成 → 獲取數字人音頻URL  
步驟3：免費數字人克隆 → 獲取character_id
步驟4：付費數字人合成 → 數字人音頻URL + character_id = 最終視頻
```

---

## 🔧 **API 端點配置**

### **基礎配置**
```javascript
const GENHUMAN_API_BASE = 'https://api.yidevs.com';
const PRODUCTION_TOKEN = '08D7EE7F91D258F27BD3CA09F72C618F';
const CALLBACK_BASE_URL = 'https://vidsparkback.zeabur.app';
```

### **必要的Header配置**
```javascript
const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${PRODUCTION_TOKEN}`,
    'Accept': 'application/json'
};
```

---

## 🎤 **步驟1：聲音克隆（免費）**

### **API端點**
```
POST https://api.yidevs.com/api/voice-clone
```

### **請求參數**
```javascript
{
    "token": "08D7EE7F91D258F27BD3CA09F72C618F",
    "voice_name": "測試聲音_001",
    "audio_url": "https://your-domain.com/path/to/audio.wav",
    "language": "zh"
}
```

### **成功響應**
```javascript
{
    "success": true,
    "data": {
        "voice_id": "voice_123456",
        "status": "processing",
        "estimated_time": 120
    }
}
```

### **實現代碼示例**
```javascript
async function cloneVoice(audioUrl, voiceName = "測試聲音") {
    try {
        const response = await fetch('https://api.yidevs.com/api/voice-clone', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: '08D7EE7F91D258F27BD3CA09F72C618F',
                voice_name: voiceName,
                audio_url: audioUrl,
                language: 'zh'
            })
        });
        
        const result = await response.json();
        if (result.success) {
            console.log('聲音克隆成功:', result.data.voice_id);
            return result.data.voice_id;
        }
        throw new Error(result.message || '聲音克隆失敗');
    } catch (error) {
        console.error('聲音克隆錯誤:', error);
        throw error;
    }
}
```

---

## 🗣️ **步驟2：聲音合成（付費）**

### **API端點**
```
POST https://api.yidevs.com/api/voice-synthesis
```

### **請求參數**
```javascript
{
    "token": "08D7EE7F91D258F27BD3CA09F72C618F",
    "voice_id": "voice_123456",
    "text": "您要合成的文字內容",
    "language": "zh",
    "speed": 1.0,
    "pitch": 1.0
}
```

### **成功響應**
```javascript
{
    "success": true,
    "data": {
        "task_id": "synthesis_789012",
        "audio_url": "https://api.yidevs.com/storage/audio/synthesis_789012.wav",
        "duration": 15.6,
        "status": "completed"
    }
}
```

### **實現代碼示例**
```javascript
async function synthesizeVoice(voiceId, text) {
    try {
        const response = await fetch('https://api.yidevs.com/api/voice-synthesis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: '08D7EE7F91D258F27BD3CA09F72C618F',
                voice_id: voiceId,
                text: text,
                language: 'zh',
                speed: 1.0,
                pitch: 1.0
            })
        });
        
        const result = await response.json();
        if (result.success) {
            console.log('聲音合成成功:', result.data.audio_url);
            return result.data.audio_url;
        }
        throw new Error(result.message || '聲音合成失敗');
    } catch (error) {
        console.error('聲音合成錯誤:', error);
        throw error;
    }
}
```

---

## 👤 **步驟3：數字人克隆（免費）**

### **API端點**
```
POST https://api.yidevs.com/api/character-clone
```

### **請求參數**
```javascript
{
    "token": "08D7EE7F91D258F27BD3CA09F72C618F",
    "character_name": "測試數字人_001",
    "video_url": "https://your-domain.com/path/to/video.mp4",
    "callback_url": "https://vidsparkback.zeabur.app/genhuman/callback"
}
```

### **成功響應**
```javascript
{
    "success": true,
    "data": {
        "character_id": "char_345678",
        "status": "processing",
        "estimated_time": 300
    }
}
```

### **實現代碼示例**
```javascript
async function cloneCharacter(videoUrl, characterName = "測試數字人") {
    try {
        const response = await fetch('https://api.yidevs.com/api/character-clone', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: '08D7EE7F91D258F27BD3CA09F72C618F',
                character_name: characterName,
                video_url: videoUrl,
                callback_url: 'https://vidsparkback.zeabur.app/genhuman/callback'
            })
        });
        
        const result = await response.json();
        if (result.success) {
            console.log('數字人克隆成功:', result.data.character_id);
            return result.data.character_id;
        }
        throw new Error(result.message || '數字人克隆失敗');
    } catch (error) {
        console.error('數字人克隆錯誤:', error);
        throw error;
    }
}
```

---

## 🎬 **步驟4：數字人合成（付費）**

### **API端點**
```
POST https://api.yidevs.com/api/character-synthesis
```

### **請求參數**
```javascript
{
    "token": "08D7EE7F91D258F27BD3CA09F72C618F",
    "character_id": "char_345678",
    "audio_url": "https://api.yidevs.com/storage/audio/synthesis_789012.wav",
    "callback_url": "https://vidsparkback.zeabur.app/genhuman/callback"
}
```

### **成功響應**
```javascript
{
    "success": true,
    "data": {
        "task_id": "synthesis_456789",
        "video_url": "https://api.yidevs.com/storage/video/synthesis_456789.mp4",
        "status": "completed",
        "duration": 15.6
    }
}
```

### **實現代碼示例**
```javascript
async function synthesizeCharacter(characterId, audioUrl) {
    try {
        const response = await fetch('https://api.yidevs.com/api/character-synthesis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                token: '08D7EE7F91D258F27BD3CA09F72C618F',
                character_id: characterId,
                audio_url: audioUrl,
                callback_url: 'https://vidsparkback.zeabur.app/genhuman/callback'
            })
        });
        
        const result = await response.json();
        if (result.success) {
            console.log('數字人合成成功:', result.data.video_url);
            return result.data.video_url;
        }
        throw new Error(result.message || '數字人合成失敗');
    } catch (error) {
        console.error('數字人合成錯誤:', error);
        throw error;
    }
}
```

---

## 🔄 **完整工作流程實現**

### **主函數示例**
```javascript
async function generateDigitalHumanVideo(audioFile, videoFile, scriptText) {
    try {
        console.log('🚀 開始GenHuman數字人視頻生成流程');
        
        // 步驟1：上傳並獲取文件URL
        const audioUrl = await uploadFile(audioFile);
        const videoUrl = await uploadFile(videoFile);
        
        // 步驟2：聲音克隆
        console.log('🎤 步驟1：聲音克隆...');
        const voiceId = await cloneVoice(audioUrl, '用戶聲音');
        
        // 步驟3：聲音合成
        console.log('🗣️ 步驟2：聲音合成...');
        const synthesizedAudioUrl = await synthesizeVoice(voiceId, scriptText);
        
        // 步驟4：數字人克隆
        console.log('👤 步驟3：數字人克隆...');
        const characterId = await cloneCharacter(videoUrl, '用戶數字人');
        
        // 步驟5：數字人合成
        console.log('🎬 步驟4：數字人合成...');
        const finalVideoUrl = await synthesizeCharacter(characterId, synthesizedAudioUrl);
        
        console.log('✅ 數字人視頻生成完成:', finalVideoUrl);
        return finalVideoUrl;
        
    } catch (error) {
        console.error('❌ 生成過程失敗:', error);
        throw error;
    }
}
```

---

## 📝 **Callback處理**

### **回調端點設置**
```javascript
// 在後端設置回調處理
app.post('/genhuman/callback', (req, res) => {
    const { task_id, status, result_url, error } = req.body;
    
    console.log('收到GenHuman回調:', {
        task_id,
        status,
        result_url,
        error
    });
    
    // 處理回調邏輯
    if (status === 'completed') {
        // 任務完成處理
        console.log('任務完成:', result_url);
    } else if (status === 'failed') {
        // 任務失敗處理
        console.error('任務失敗:', error);
    }
    
    res.json({ success: true });
});
```

---

## 🔍 **錯誤處理和調試**

### **常見錯誤和解決方案**

1. **Token無效**
   ```javascript
   // 錯誤：{"error": "Invalid token"}
   // 解決：檢查token是否正確
   const PRODUCTION_TOKEN = '08D7EE7F91D258F27BD3CA09F72C618F';
   ```

2. **文件URL無法訪問**
   ```javascript
   // 錯誤：{"error": "Unable to download file"}
   // 解決：確保文件URL可以外部訪問
   // 測試：curl -I "your-file-url"
   ```

3. **回調URL設置錯誤**
   ```javascript
   // 錯誤：{"error": "Callback failed"}
   // 解決：確保callback_url可以接收POST請求
   callback_url: 'https://vidsparkback.zeabur.app/genhuman/callback'
   ```

### **調試工具**
```javascript
// 添加詳細日誌
function debugLog(step, data) {
    console.log(`[${new Date().toLocaleTimeString()}] ${step}:`, data);
}

// 使用示例
debugLog('API請求', { url, method, body });
debugLog('API響應', result);
```

---

## 📊 **性能和限制**

### **API限制**
- **聲音克隆**：免費額度 50次/月
- **聲音合成**：付費 ¥0.1/次
- **數字人克隆**：免費額度 10次/月  
- **數字人合成**：付費 ¥1.0/次

### **文件要求**
- **音頻文件**：WAV/MP3格式，≤10MB，≥3秒
- **視頻文件**：MP4格式，≤50MB，720p以上，包含人臉

### **處理時間**
- **聲音克隆**：2-5分鐘
- **聲音合成**：10-30秒
- **數字人克隆**：5-15分鐘
- **數字人合成**：1-3分鐘

---

## 🚀 **部署和使用**

### **後端集成步驟**
1. **複製測試頁面到項目**
   ```bash
   cp genhuman_cloud_test.html your_project/static/
   ```

2. **安裝依賴**
   ```bash
   npm install axios form-data
   ```

3. **配置環境變量**
   ```bash
   GENHUMAN_API_TOKEN=08D7EE7F91D258F27BD3CA09F72C618F
   GENHUMAN_API_BASE=https://api.yidevs.com
   CALLBACK_BASE_URL=https://your-domain.com
   ```

4. **實現回調處理**
   ```javascript
   // 參考上面的回調處理代碼
   ```

---

**📅 創建日期**: 2025-01-09  
**📝 作者**: AI技術顧問  
**🎯 適用項目**: No-Code Architects Toolkit  
**🌐 測試環境**: https://vidsparkback.zeabur.app/test/genhuman  
**📞 技術支援**: 參考 `前端支援后端genhumanapi调用前端技术支援任务执行清单-前端反馈v1v0908.md`
