# Whisper 音頻轉錄和視頻字幕測試指南

## 🎯 測試目標
驗證ZEABUR上faster-whisper引擎的轉錄能力和字幕生成功能

## ✅ 可用的轉錄功能

### 1. 音頻轉錄 (Enhanced)
**端點**: `/v1/media/transcribe_enhanced`
**狀態**: ✅ 可用 (faster-whisper)

**測試參數**:
```json
{
  "media_url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav",
  "language": "auto",
  "task": "transcribe"
}
```

### 2. 簡單轉錄
**端點**: `/v1/media/transcribe_simple`
**狀態**: ✅ 可用 (faster-whisper)

**測試參數**:
```json
{
  "media_url": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav"
}
```

### 3. CPU優化轉錄
**端點**: `/v1/media/transcribe_real_cpu`
**狀態**: ✅ 可用 (faster-whisper)

## 🎬 視頻字幕功能

### 1. 簡單視頻字幕
**端點**: `/v1/video/caption_simple`
**狀態**: ✅ 可用

**測試參數**:
```json
{
  "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
  "language": "auto"
}
```

### 2. 不可用的功能
**端點**: `/v1/video/caption_video` 和 `/v1/media/transcribe_media`
**狀態**: ❌ 不可用 (需要原版whisper)

## 🧪 建議測試方案

### 階段1: 基礎轉錄測試
1. 使用短音頻文件測試基本轉錄功能
2. 測試不同語言的識別能力
3. 驗證faster-whisper的處理速度

### 階段2: 視頻字幕測試
1. 使用短視頻文件測試字幕生成
2. 驗證字幕時間軸的準確性
3. 測試不同視頻格式的兼容性

### 階段3: 性能測試
1. 測試較長音頻/視頻的處理能力
2. 並發處理測試
3. CPU和內存使用監控

## 🎯 推薦測試媒體

### 音頻測試文件
1. **短音頻**: https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav
2. **英文語音**: https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav
3. **音樂**: https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand60.wav

### 視頻測試文件
1. **示例視頻**: https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4
2. **短片**: https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4

## 📊 期望結果
- **轉錄準確率**: 85%+ (英文)
- **處理速度**: 1分鐘音頻 < 30秒處理
- **支持格式**: MP3, WAV, MP4, AVI
- **最大文件**: 100MB (基於ZEABUR限制)

## ⚠️ 注意事項
1. faster-whisper使用CPU處理，速度較GPU版本慢但更穩定
2. 長文件可能需要較長處理時間
3. 中文識別能力可能不如英文
4. 建議先用短文件測試功能可用性




