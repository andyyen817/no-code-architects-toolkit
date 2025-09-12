# 技術小白設置Zeabur MySQL操作指南

## 📋 操作概述
本指南將幫助您在Zeabur平台上正確設置MySQL數據庫環境變量，確保VidSpark後端應用能夠正常連接和使用數據庫。

## 🎯 前置條件
- 已有Zeabur帳號並登入
- 已創建VidSpark後端項目
- 已在Zeabur上創建MySQL服務

## 📊 當前MySQL數據庫信息
根據 `后端数据库配置方案v1v0908.md`，您的MySQL數據庫配置如下：
```
主機地址: mysql.zeabur.internal
數據庫名: zeabur
用戶名: root
密碼: fhlkzgNuRQL79C5eFb4036vX2T18YdAn
端口: 3306
字符集: utf8mb4
```

## 🔧 步驟一：登入Zeabur控制台

1. 打開瀏覽器，前往 [https://zeabur.com](https://zeabur.com)
2. 點擊右上角「登入」按鈕
3. 使用您的帳號密碼登入
4. 進入項目控制台

## 🗂️ 步驟二：找到您的VidSpark後端項目

1. 在控制台首頁，找到您的VidSpark後端項目
2. 點擊項目名稱進入項目詳情頁面
3. 確認項目中已有MySQL服務正在運行

## ⚙️ 步驟三：設置環境變量

### 3.1 進入環境變量設置頁面
1. 在項目頁面中，找到您的後端應用服務
2. 點擊應用服務名稱
3. 在左側菜單中找到「環境變量」或「Environment Variables」
4. 點擊進入環境變量設置頁面

### 3.2 添加數據庫相關環境變量
請按照以下順序，逐一添加環境變量：

#### 基礎數據庫配置
```
變量名: DB_CONNECTION
變量值: mysql
說明: 指定數據庫類型為MySQL
```

```
變量名: DB_HOST
變量值: mysql.zeabur.internal
說明: MySQL服務器地址
```

```
變量名: DB_PORT
變量值: 3306
說明: MySQL服務端口
```

```
變量名: DB_DATABASE
變量值: zeabur
說明: 數據庫名稱
```

```
變量名: DB_USERNAME
變量值: root
說明: 數據庫用戶名
```

```
變量名: DB_PASSWORD
變量值: 248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6
說明: 數據庫密碼
```

```
變量名: DB_CHARSET
變量值: utf8mb4
說明: 數據庫字符集
```

#### 連接池配置
```
變量名: DB_POOL_SIZE
變量值: 5
說明: 數據庫連接池大小
```

```
變量名: DB_POOL_TIMEOUT
變量值: 30
說明: 連接超時時間(秒)
```

```
變量名: DB_POOL_RECYCLE
變量值: 3600
說明: 連接回收時間(秒)
```

#### 應用配置
```
變量名: API_KEY
變數值: production-api-key-2024
說明: 應用API密鑰
```

```
變量名: FLASK_ENV
變量值: production
說明: Flask運行環境
```

```
變量名: STORAGE_PATH
變量值: /app/output
說明: 文件存儲路徑
```

```
變量名: MAX_FILE_SIZE
變量值: 1000
說明: 最大文件大小(MB)
```

### 3.3 保存環境變量
1. 確認所有環境變量都已正確輸入
2. 點擊「保存」或「Save」按鈕
3. 等待系統保存完成

## 🔄 步驟四：重啟應用服務

1. 回到項目主頁面
2. 找到您的後端應用服務
3. 點擊服務右側的「重啟」或「Restart」按鈕
4. 等待服務重啟完成（通常需要1-3分鐘）

## ✅ 步驟五：驗證配置

### 5.1 檢查服務狀態
1. 確認後端應用服務狀態為「運行中」或「Running」
2. 確認MySQL服務狀態為「運行中」或「Running」

### 5.2 檢查日誌
1. 點擊後端應用服務
2. 查看「日誌」或「Logs」頁面
3. 確認沒有數據庫連接錯誤
4. 尋找類似以下的成功信息：
   - "Database connected successfully"
   - "MySQL connection established"
   - "Storage system initialized"

### 5.3 測試API端點
1. 獲取您的應用訪問URL
2. 在瀏覽器中訪問：`https://your-app-url/api/v1/storage/status`
3. 如果返回JSON格式的狀態信息，說明配置成功

## 🚨 常見問題排除

### 問題1：連接被拒絕
**症狀**：日誌顯示 "Connection refused" 或 "Access denied"
**解決方案**：
1. 檢查DB_HOST是否為 `mysql.zeabur.internal`
2. 確認MySQL服務正在運行
3. 驗證用戶名和密碼是否正確

### 問題2：數據庫不存在
**症狀**：日誌顯示 "Database does not exist"
**解決方案**：
1. 確認DB_DATABASE設置為 `zeabur`
2. 檢查MySQL服務中是否已創建該數據庫

### 問題3：字符集問題
**症狀**：中文數據顯示亂碼
**解決方案**：
1. 確認DB_CHARSET設置為 `utf8mb4`
2. 重啟應用服務

### 問題4：連接超時
**症狀**：日誌顯示 "Connection timeout"
**解決方案**：
1. 增加DB_POOL_TIMEOUT值（如60）
2. 檢查網絡連接狀況

## 📞 獲取幫助

如果遇到問題無法解決：
1. 截圖錯誤日誌
2. 記錄具體的錯誤信息
3. 聯繫技術支持團隊
4. 提供您的項目名稱和錯誤時間

## ✨ 成功標準

配置成功後，您應該能夠：
- ✅ 後端應用正常啟動
- ✅ 數據庫連接成功
- ✅ API端點正常響應
- ✅ 文件上傳功能正常
- ✅ 數據持久化保存

---

**創建時間**: 2024-01-11  
**適用版本**: VidSpark v1.0  
**維護人員**: 技術支持團隊  
**難度等級**: 初級 ⭐⭐☆☆☆