# 🗄️ No-Code Architects Toolkit 數據庫設置指南

## 🎯 目標
在你的ZEABUR MySQL實例中創建後端所需的所有數據表

## 📋 前置條件
- ✅ 你已經創建了ZEABUR MySQL服務
- ✅ 你已經獲得了連接信息
- ✅ 你已經在ZEABUR後端設置了數據庫環境變量

## 🚀 **執行步驟**

### **步驟1: 連接到你的ZEABUR MySQL**
```bash
# 使用mysqlsh連接（推薦）
mysqlsh --sql --host=tpe1.clusters.zeabur.com --port=30791 --user=root --password=248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6 --schema=zeabur
```

**或者使用傳統mysql客戶端：**
```bash
mysql -h tpe1.clusters.zeabur.com -P 30791 -u root -p248s1xp5zOiwdLe0MqGQ3W7nTE9YZVh6 zeabur
```

### **步驟2: 執行數據庫表創建腳本**

**方法1: 直接在MySQL Shell中執行**
```sql
# 確認當前數據庫
SELECT DATABASE();

# 加載並執行創建腳本
source create_backend_database_tables.sql;
```

**方法2: 複製粘貼執行**
1. 打開 `create_backend_database_tables.sql` 文件
2. 複製所有SQL語句
3. 在MySQL Shell中粘貼並執行

### **步驟3: 驗證創建結果**

#### **檢查表是否創建成功**
```sql
-- 查看所有nca_開頭的表
SHOW TABLES LIKE 'nca_%';

-- 期望看到6個表：
-- nca_users
-- nca_genhuman_projects  
-- nca_files
-- nca_api_calls
-- nca_system_config
-- nca_operation_logs
```

#### **檢查表結構**
```sql
-- 查看用戶表結構
DESCRIBE nca_users;

-- 查看項目表結構  
DESCRIBE nca_genhuman_projects;

-- 查看文件表結構
DESCRIBE nca_files;
```

#### **檢查初始數據**
```sql
-- 查看系統配置
SELECT * FROM nca_system_config;

-- 查看管理員用戶
SELECT id, username, email, status FROM nca_users;
```

### **步驟4: 測試數據庫連接**

創建一個測試項目記錄：
```sql
-- 插入測試項目
INSERT INTO nca_genhuman_projects (
    uuid, 
    user_id, 
    project_name, 
    project_type, 
    status
) VALUES (
    UUID(),
    (SELECT id FROM nca_users WHERE username = 'admin'),
    '測試項目',
    'voice_clone',
    'pending'
);

-- 查看插入結果
SELECT * FROM nca_genhuman_projects ORDER BY created_at DESC LIMIT 1;
```

## ✅ **驗證成功標準**

如果你看到以下結果，說明設置成功：

1. **表創建成功**：
   ```
   +-------------------------+
   | Tables_in_zeabur (nca_%) |
   +-------------------------+
   | nca_api_calls           |
   | nca_files               |
   | nca_genhuman_projects   |
   | nca_operation_logs      |
   | nca_system_config       |
   | nca_users               |
   +-------------------------+
   ```

2. **系統配置存在**：
   ```sql
   SELECT COUNT(*) FROM nca_system_config;
   -- 應該返回 7 條記錄
   ```

3. **管理員用戶存在**：
   ```sql
   SELECT username FROM nca_users WHERE username = 'admin';
   -- 應該返回 'admin'
   ```

## 🔧 **常見問題解決**

### **問題1: 連接失敗**
**症狀**: `ERROR 2003 (HY000): Can't connect to MySQL server`

**解決方案**:
1. 確認主機地址和端口正確
2. 檢查密碼是否包含特殊字符需要轉義
3. 嘗試使用不同的MySQL客戶端工具

### **問題2: 權限不足**
**症狀**: `ERROR 1044 (42000): Access denied for user`

**解決方案**:
1. 確認使用root用戶連接
2. 檢查數據庫名稱是否正確
3. 聯繫ZEABUR支持檢查用戶權限

### **問題3: 表已存在錯誤**
**症狀**: `ERROR 1050 (42S01): Table 'xxx' already exists`

**解決方案**:
這是正常的，腳本使用了`CREATE TABLE IF NOT EXISTS`，可以安全忽略。

## 🎯 **下一步**

數據庫設置完成後：

1. **更新後端應用配置**：確保Flask應用能連接到數據庫
2. **測試API端點**：使用測試頁面驗證數據庫操作
3. **開始開發GenHuman API接口**：基於這些表結構開發功能

---

**📅 創建日期**: 2025-01-09  
**🎯 目標**: 技術小白友好的數據庫設置指南  
**⚡ 預期時間**: 10-15分鐘完成所有設置
