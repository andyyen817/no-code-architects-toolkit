# ZEABUR 部署後測試指南

## 🎯 測試目標
驗證No-Code Architects Toolkit在ZEABUR上的完整功能

## 🌐 測試環境信息
- **外網地址**: https://vidsparkback.zeabur.app
- **內網地址**: vidsparkback.zeabur.internal:8080
- **測試頁面**: zeabur_test_page.html
- **FFMPEG測試**: ffmpeg_test_page.html

## 📋 測試步驟檢查清單

### 階段1: 基礎連接測試 (必須通過)

#### ✅ 步驟1.1: 健康檢查
```bash
測試URL: https://vidsparkback.zeabur.app/health
期望結果: {"status": "healthy", "build": "...", "fix": "..."}
```

**測試方法**:
1. 在瀏覽器中訪問健康檢查URL
2. 確認返回JSON格式的健康狀態
3. ❌ 如果失敗: 檢查ZEABUR部署日誌

#### ✅ 步驟1.2: API認證測試
```bash
測試URL: https://vidsparkback.zeabur.app/v1/toolkit/authenticate
方法: POST
數據: {"api_key": "vidspark-production-api-key-2024-secure"}
```

**測試方法**:
1. 使用Postman或測試頁面測試認證
2. 確認API Key驗證通過
3. ❌ 如果失敗: 檢查環境變量設置

### 階段2: 核心功能測試

#### ✅ 步驟2.1: 音頻轉錄測試 (Whisper)
```bash
測試端點: /v1/media/transcribe_enhanced
測試音頻: https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav
```

**測試參數**:
```json
{
  "media_url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav",
  "language": "auto",
  "task": "transcribe"
}
```

**期望結果**: 返回音頻轉錄文字

#### ✅ 步驟2.2: 視頻處理測試 (FFMPEG)
```bash
測試端點: /v1/video/cut_real
測試視頻: https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4
```

**測試參數**:
```json
{
  "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
  "start_time": "00:00:05",
  "end_time": "00:00:15"
}
```

**期望結果**: 返回剪切後的視頻URL

#### ✅ 步驟2.3: 圖像處理測試
```bash
測試端點: /v1/image/convert/image_to_video_real
測試圖片: https://via.placeholder.com/1280x720/4CAF50/white?text=Test+Image
```

### 階段3: 使用測試頁面

#### ✅ 步驟3.1: 更新測試頁面URL
1. 編輯 `zeabur_test_page.html`
2. 找到這行: `const BASE_URL = 'https://你的zeabur域名.zeabur.app';`
3. 替換為: `const BASE_URL = 'https://vidsparkback.zeabur.app';`
4. 保存文件

#### ✅ 步驟3.2: 在瀏覽器中測試
1. 在瀏覽器中打開 `zeabur_test_page.html`
2. 頁面會自動執行健康檢查
3. 手動測試各項功能
4. 觀察測試結果區域

#### ✅ 步驟3.3: FFMPEG專項測試
1. 在瀏覽器中打開 `ffmpeg_test_page.html`
2. 更新其中的BASE_URL
3. 測試音頻、視頻處理功能
4. 監控性能統計

### 階段4: 性能監控

#### ✅ 步驟4.1: 響應時間測試
- **健康檢查**: < 2秒
- **API認證**: < 3秒
- **音頻轉錄**: < 30秒 (1分鐘音頻)
- **視頻剪切**: < 20秒 (10秒視頻)

#### ✅ 步驟4.2: 並發測試
1. 同時發起3-5個請求
2. 觀察是否有請求超時
3. 檢查ZEABUR資源使用率

## 🚨 常見問題排查

### 問題1: 502 Bad Gateway
**原因**: 應用啟動失敗
**排查**:
1. 檢查ZEABUR部署日誌
2. 確認環境變量設置正確
3. 檢查Docker容器狀態

### 問題2: API認證失敗
**原因**: API_KEY不匹配
**解決方案**:
1. 檢查ZEABUR環境變量中的API_KEY
2. 確認測試代碼中使用相同的API_KEY

### 問題3: 功能測試超時
**原因**: 
- 網絡連接問題
- 服務器資源不足
- 測試文件過大

**解決方案**:
1. 使用更小的測試文件
2. 檢查網絡連接
3. 監控ZEABUR資源使用

### 問題4: Whisper轉錄失敗
**原因**:
- 音頻格式不支持
- faster-whisper模型載入失敗

**解決方案**:
1. 使用支持的音頻格式 (MP3, WAV)
2. 檢查ZEABUR內存使用

## 📊 測試完成標準

### ✅ 必須通過的測試
- [ ] 健康檢查返回正常
- [ ] API認證成功
- [ ] 音頻轉錄功能正常
- [ ] 視頻剪切功能正常
- [ ] 圖像處理功能正常

### ⚡ 性能要求
- [ ] 健康檢查 < 2秒
- [ ] API響應 < 5秒
- [ ] 95%的請求成功率

### 📈 可選測試
- [ ] 長音頻轉錄 (5分鐘+)
- [ ] 大視頻處理 (50MB+)
- [ ] 並發壓力測試

## 🎯 測試完成後的下一步

1. **功能驗證完成**: 開始真實業務測試
2. **性能調優**: 基於測試結果調整配置
3. **監控設置**: 建立長期監控機制
4. **文檔更新**: 更新API文檔和使用指南

## 📝 測試記錄模板

```
測試日期: ____
測試人員: ____
ZEABUR URL: https://vidsparkback.zeabur.app

基礎測試:
[ ] 健康檢查 - 狀態: _____ 響應時間: _____
[ ] API認證 - 狀態: _____ 響應時間: _____

功能測試:
[ ] 音頻轉錄 - 狀態: _____ 處理時間: _____
[ ] 視頻剪切 - 狀態: _____ 處理時間: _____
[ ] 圖像處理 - 狀態: _____ 處理時間: _____

問題記錄:
1. ________________________________
2. ________________________________
3. ________________________________

總結: ________________________________
```




