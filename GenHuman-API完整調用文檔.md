# GenHuman API 完整調用文檔

## 🎯 **文檔目的**
基於前端成功經驗，為後端開發團隊提供完整的GenHuman API調用指南，確保後端能夠100%復制前端的成功實現。

## 📊 **API基礎信息**

### **基礎配置**
```javascript
const API_CONFIG = {
    base: 'https://api.yidevs.com',
    token: '08D7EE7F91D258F27B4ADDF59CDDDEDE.1E95F76130BA23D37CE7BBBD69B19CCF.KYBVDWNR'
};
```

### **通用請求格式**
```javascript
{
    "token": "your_api_token",
    // ... 其他參數
}
```

### **通用響應格式**
```javascript
{
    "code": 200,          // 200=成功，其他=失敗
    "msg": "success",     // 響應消息
    "data": {            // 實際數據
        // ... 具體數據
    }
}
```

---

## 🚀 **完整工作流程**

### **📋 成功流程概覽**
```
1. 免費聲音克隆 → 獲得 voice_id
2. 付費聲音合成 → 獲得 audio_url  
3. 免費數字人克隆 → 獲得 digital_human_id
4. 付費數字人合成 → 獲得 video_task_id
5. 查詢任務狀態 → 獲得最終視頻URL
```

---

## 🎤 **步驟1：免費聲音克隆**

### **API端點**
```
POST https://api.yidevs.com/app/human/human/Voice/clone
```

### **請求參數**
```javascript
{
    "token": "your_api_token",
    "voice_name": "張小明的聲音",      // 自定義聲音名稱
    "voice_url": "https://...",        // 音頻文件URL
    "describe": "男聲，溫和親切"        // 聲音描述
}
```

### **成功響應**
```javascript
{
    "code": 200,
    "msg": "success",
    "data": {
        "voice_id": "f0094de60d1b4a1eae2d985923b89922",  // ⭐ 重要：下一步需要
        "task_id": 55
    }
}
```

### **前端實現範例**
```javascript
async function voiceClone(voiceName, voiceUrl, describe) {
    const response = await fetch('https://api.yidevs.com/app/human/human/Voice/clone', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: API_CONFIG.token,
            voice_name: voiceName,
            voice_url: voiceUrl,
            describe: describe
        })
    });
    
    const result = await response.json();
    if (result.code === 200) {
        return result.data.voice_id;  // 返回voice_id用於下一步
    }
    throw new Error(result.msg);
}
```

### **PHP實現範例**
```php
function voiceClone($voiceName, $voiceUrl, $describe) {
    $url = 'https://api.yidevs.com/app/human/human/Voice/clone';
    $data = [
        'token' => $this->token,
        'voice_name' => $voiceName,
        'voice_url' => $voiceUrl,
        'describe' => $describe
    ];
    
    $response = $this->callAPI($url, $data);
    
    if ($response['code'] === 200) {
        return $response['data']['voice_id'];  // 返回voice_id
    }
    
    throw new Exception($response['msg']);
}
```

---

## 🔊 **步驟2：付費聲音合成**

### **API端點**
```
POST https://api.yidevs.com/app/human/human/Voice/synthesis
```

### **請求參數**
```javascript
{
    "token": "your_api_token",
    "voice_id": "f0094de60d1b4a1eae2d985923b89922",  // 從步驟1獲得
    "text": "大家好，我是數字人助手。"               // 要合成的文字
}
```

### **成功響應**
```javascript
{
    "code": 200,
    "msg": "success",
    "data": {
        "audio_url": "https://example.com/audio.mp3",  // ⭐ 重要：步驟4需要
        "duration": 5.2,
        "file_size": 1024000
    }
}
```

### **前端實現範例**
```javascript
async function voiceSynthesis(voiceId, text) {
    const response = await fetch('https://api.yidevs.com/app/human/human/Voice/synthesis', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: API_CONFIG.token,
            voice_id: voiceId,
            text: text
        })
    });
    
    const result = await response.json();
    if (result.code === 200) {
        return result.data.audio_url;  // 返回音頻URL用於步驟4
    }
    throw new Error(result.msg);
}
```

---

## 👤 **步驟3：免費數字人克隆**

### **API端點**
```
POST https://api.yidevs.com/app/human/human/Index/humanClone
```

### **請求參數**
```javascript
{
    "token": "your_api_token",
    "character_name": "李老師",           // 角色名稱
    "image_url": "https://..."           // 人物照片URL
}
```

### **成功響應**
```javascript
{
    "code": 200,
    "msg": "success",
    "data": {
        "digital_human_id": "1208",          // ⭐ 重要：步驟4需要
        "character_name": "李老師",
        "status": "created"
    }
}
```

### **前端實現範例**
```javascript
async function digitalHumanClone(characterName, imageUrl) {
    const response = await fetch('https://api.yidevs.com/app/human/human/Index/humanClone', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: API_CONFIG.token,
            character_name: characterName,
            image_url: imageUrl
        })
    });
    
    const result = await response.json();
    if (result.code === 200) {
        return result.data.digital_human_id;  // 返回數字人ID用於步驟4
    }
    throw new Error(result.msg);
}
```

---

## 🎬 **步驟4：付費數字人合成（最終步驟）**

### **API端點**
```
POST https://api.yidevs.com/app/human/human/Index/created
```

### **請求參數**
```javascript
{
    "token": "your_api_token",
    "callback_url": "https://your-domain.com/callback",  // 必填：回調地址
    "scene_task_id": "1208",                             // 從步驟3獲得
    "audio_address": "https://example.com/audio.mp3"     // 從步驟2獲得
}
```

### **成功響應**
```javascript
{
    "code": 200,
    "msg": "success",
    "data": {
        "video_task_id": 573,      // ⭐ 重要：查詢狀態需要
        "bill_id": "1102"
    }
}
```

### **前端實現範例**
```javascript
async function digitalHumanSynthesis(callbackUrl, digitalHumanId, audioUrl) {
    const response = await fetch('https://api.yidevs.com/app/human/human/Index/created', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: API_CONFIG.token,
            callback_url: callbackUrl,
            scene_task_id: digitalHumanId,
            audio_address: audioUrl
        })
    });
    
    const result = await response.json();
    if (result.code === 200) {
        return result.data.video_task_id;  // 返回任務ID用於查詢狀態
    }
    throw new Error(result.msg);
}
```

---

## 🔍 **步驟5：查詢任務狀態**

### **API端點**
```
GET https://api.yidevs.com/app/human/human/Musetalk/task
```

### **請求參數**
```javascript
{
    "token": "your_api_token",
    "task_id": "573"           // 從步驟4獲得
}
```

### **成功響應**
```javascript
{
    "code": 200,
    "msg": "success",
    "data": {
        "video_task_id": 561,
        "duration": 97,
        "durationMs": 97000,
        "coverUrl": "https://...",
        "videoUrl": "https://...",    // ⭐ 最終視頻URL
        "videoName": "final_video",
        "tips": "链接地址有效期24H，请及时下载保存",
        "state": 20                   // 10=處理中, 20=完成, 30=失敗
    }
}
```

### **狀態說明**
- `state: 10` - 處理中，需要繼續查詢
- `state: 20` - 已完成，可以獲得videoUrl
- `state: 30` - 處理失敗

### **前端實現範例**
```javascript
async function queryTaskStatus(taskId) {
    const response = await fetch('https://api.yidevs.com/app/human/human/Musetalk/task', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: API_CONFIG.token,
            task_id: taskId
        })
    });
    
    const result = await response.json();
    if (result.code === 200) {
        const data = result.data;
        return {
            status: data.state,
            videoUrl: data.videoUrl,
            isComplete: data.state === 20,
            isFailed: data.state === 30
        };
    }
    throw new Error(result.msg);
}
```

---

## 💼 **完整工作流程實現**

### **JavaScript完整範例**
```javascript
class GenHumanWorkflow {
    constructor(token) {
        this.token = token;
        this.apiBase = 'https://api.yidevs.com';
    }
    
    async executeFullWorkflow(params) {
        try {
            // 步驟1：聲音克隆
            const voiceId = await this.voiceClone(
                params.voiceName, 
                params.voiceUrl, 
                params.voiceDesc
            );
            
            // 步驟2：聲音合成
            const audioUrl = await this.voiceSynthesis(voiceId, params.text);
            
            // 步驟3：數字人克隆
            const digitalHumanId = await this.digitalHumanClone(
                params.characterName, 
                params.imageUrl
            );
            
            // 步驟4：數字人合成
            const taskId = await this.digitalHumanSynthesis(
                params.callbackUrl, 
                digitalHumanId, 
                audioUrl
            );
            
            // 步驟5：查詢狀態（可選，通常通過回調獲得結果）
            return {
                success: true,
                voiceId: voiceId,
                audioUrl: audioUrl,
                digitalHumanId: digitalHumanId,
                taskId: taskId
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// 使用範例
const workflow = new GenHumanWorkflow('your_token');
const result = await workflow.executeFullWorkflow({
    voiceName: '測試聲音',
    voiceUrl: 'https://example.com/audio.mp3',
    voiceDesc: '清晰標準',
    text: '大家好，我是數字人助手。',
    characterName: 'Andy老師',
    imageUrl: 'https://example.com/photo.jpg',
    callbackUrl: 'https://your-domain.com/callback'
});
```

### **PHP完整範例**
```php
<?php
class GenHumanWorkflow {
    private $token;
    private $apiBase = 'https://api.yidevs.com';
    
    public function __construct($token) {
        $this->token = $token;
    }
    
    public function executeFullWorkflow($params) {
        try {
            // 步驟1：聲音克隆
            $voiceId = $this->voiceClone(
                $params['voiceName'], 
                $params['voiceUrl'], 
                $params['voiceDesc']
            );
            
            // 步驟2：聲音合成
            $audioUrl = $this->voiceSynthesis($voiceId, $params['text']);
            
            // 步驟3：數字人克隆
            $digitalHumanId = $this->digitalHumanClone(
                $params['characterName'], 
                $params['imageUrl']
            );
            
            // 步驟4：數字人合成
            $taskId = $this->digitalHumanSynthesis(
                $params['callbackUrl'], 
                $digitalHumanId, 
                $audioUrl
            );
            
            return [
                'success' => true,
                'voiceId' => $voiceId,
                'audioUrl' => $audioUrl,
                'digitalHumanId' => $digitalHumanId,
                'taskId' => $taskId
            ];
            
        } catch (Exception $e) {
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
    
    private function callAPI($endpoint, $data) {
        $url = $this->apiBase . $endpoint;
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json'
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new Exception("HTTP Error: $httpCode");
        }
        
        return json_decode($response, true);
    }
}

// 使用範例
$workflow = new GenHumanWorkflow('your_token');
$result = $workflow->executeFullWorkflow([
    'voiceName' => '測試聲音',
    'voiceUrl' => 'https://example.com/audio.mp3',
    'voiceDesc' => '清晰標準',
    'text' => '大家好，我是數字人助手。',
    'characterName' => 'Andy老師',
    'imageUrl' => 'https://example.com/photo.jpg',
    'callbackUrl' => 'https://your-domain.com/callback'
]);
?>
```

---

## 🚨 **重要注意事項**

### **1. 回調地址要求**
- **必須是外部可訪問的URL**
- **必須支持POST請求**
- **必須返回200狀態碼**

### **2. 文件URL要求**
- **音頻文件必須是外部可訪問的URL**
- **圖片文件必須是外部可訪問的URL**
- **建議檔案大小：音頻<50MB，圖片<10MB**

### **3. 音頻文件格式**
- **支持格式**：MP3, WAV, AAC
- **建議時長**：5-30秒
- **建議品質**：清晰、無雜音

### **4. 圖片文件格式**
- **支持格式**：JPG, PNG
- **建議解析度**：512x512 或更高
- **建議內容**：正面清晰人像照片

### **5. 錯誤處理**
```javascript
// 通用錯誤處理範例
if (response.code !== 200) {
    console.error('API調用失敗:', response.msg);
    throw new Error(`API Error: ${response.msg}`);
}
```

### **6. 調試技巧**
- **記錄所有API請求和響應**
- **驗證URL的外部可訪問性**
- **檢查文件格式和大小**
- **監控回調接收情況**

---

## 📊 **前端成功經驗總結**

### **🏆 關鍵成功因素**
1. **嚴格按照步驟順序執行**
2. **正確傳遞每步的關鍵ID**
3. **確保所有URL外部可訪問**
4. **詳細的錯誤日誌記錄**
5. **完善的異常處理機制**

### **⚠️ 常見錯誤避免**
1. **跳過某個步驟** - 必須完整執行1→2→3→4
2. **URL不可訪問** - 所有文件URL必須外部可訪問
3. **參數名稱錯誤** - 嚴格按照API文檔參數名
4. **Token過期** - 定期檢查Token有效性
5. **回調地址錯誤** - 確保回調地址正確配置

### **📈 性能優化建議**
1. **並行處理非依賴步驟**
2. **合理設置超時時間**
3. **實現重試機制**
4. **緩存中間結果**

---

**📅 創建日期**: 2025-01-09  
**📊 版本**: v1.0  
**👨‍💻 基於**: 前端Vidspark項目成功經驗  
**🎯 目標**: 幫助後端100%復制前端成功  
**⚡ 覆蓋率**: 完整工作流程100%覆蓋
