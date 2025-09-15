# VidSpark 影片字幕生成解决方案跟执行任务清单 v1.0915

## 问题分析总结

### 1. 核心问题识别

**当前状态**: 系统返回 `simulation_mode`，提示缺少依赖

**根本原因**: 
- 本地开发环境缺少 `openai-whisper` 包
- 本地开发环境缺少 FFmpeg 系统二进制文件
- 系统自动降级到简化模拟模式

### 2. 技术架构分析

#### 2.1 路由实现现状

**发现的路由文件**:
- `routes/v1/video/caption_simple.py` - 简化版模拟实现 ✅ 当前使用
- `routes/v1/video/caption_video.py` - 完整版实现 ❌ 未激活
- `routes/caption_video.py` - 旧版实现

**蓝图注册机制**:
- 使用 `app_utils.py` 中的 `discover_and_register_blueprints()` 自动发现
- 所有符合条件的蓝图都会被注册
- 路由冲突时，后注册的会覆盖先注册的

#### 2.2 依赖状态检查结果

**已安装的包**:
- ✅ `faster-whisper==1.2.0` (ZEABUR生产环境使用)
- ✅ `ffmpeg-python==0.2.0` (Python FFmpeg绑定)

**缺失的包**:
- ❌ `openai-whisper` (本地开发环境)
- ❌ FFmpeg 系统二进制文件 (本地开发环境)

**环境差异**:
- **ZEABUR生产环境**: 使用 `faster-whisper` + 系统FFmpeg
- **本地开发环境**: 缺少关键依赖，降级到模拟模式

### 3. 配置文件分析

#### 3.1 生产环境 (ZEABUR)
```dockerfile
# Dockerfile.zeabur
RUN apt-get install -y ffmpeg  # 系统FFmpeg
COPY requirements_zeabur.txt
# 包含: faster-whisper==1.0.2
```

#### 3.2 本地开发环境
```txt
# requirements.txt
ffmpeg-python==0.2.0
openai-whisper  # 但未安装
```

## 解决方案

### 方案A: 本地开发环境修复 (推荐)

#### A1. 安装缺失依赖
```bash
# 安装 openai-whisper
pip install openai-whisper

# 安装 FFmpeg (Windows)
# 方法1: 使用 chocolatey
choco install ffmpeg

# 方法2: 手动下载
# 1. 下载: https://ffmpeg.org/download.html
# 2. 解压到 C:\ffmpeg
# 3. 添加 C:\ffmpeg\bin 到系统PATH
```

#### A2. 验证安装
```bash
# 验证 FFmpeg
ffmpeg -version

# 验证 Python 包
pip list | Select-String -Pattern "whisper|ffmpeg"
```

### 方案B: 统一使用 faster-whisper (推荐生产)

#### B1. 修改本地环境配置
```bash
# 安装 faster-whisper (与生产环境一致)
pip install faster-whisper==1.2.0

# 安装 FFmpeg (同方案A)
```

#### B2. 更新代码适配
- 修改 `caption_simple.py` 中的依赖检查逻辑
- 统一使用 `faster-whisper` 而非 `openai-whisper`

### 方案C: 容器化开发环境

#### C1. 使用 Docker 开发
```bash
# 构建开发容器
docker build -f Dockerfile.zeabur -t vidspark-dev .

# 运行开发环境
docker run -p 8080:8080 -v $(pwd):/app vidspark-dev
```

## 执行任务清单

### 阶段1: 立即修复 (优先级: 高)

- [ ] **任务1.1**: 安装 FFmpeg 系统二进制文件
  - 时间估计: 15分钟
  - 负责人: 开发者
  - 验证: `ffmpeg -version` 命令成功

- [ ] **任务1.2**: 安装 openai-whisper 或 faster-whisper
  - 时间估计: 10分钟
  - 负责人: 开发者
  - 验证: `pip list` 显示包已安装

- [ ] **任务1.3**: 测试字幕生成功能
  - 时间估计: 10分钟
  - 负责人: 开发者
  - 验证: API返回真实处理结果而非simulation_mode

### 阶段2: 代码优化 (优先级: 中)

- [ ] **任务2.1**: 统一依赖管理
  - 更新 `requirements.txt` 与 `requirements_zeabur.txt` 保持一致
  - 时间估计: 20分钟

- [ ] **任务2.2**: 改进依赖检查逻辑
  - 修改 `caption_simple.py` 中的依赖检测
  - 支持多种 Whisper 实现 (openai-whisper/faster-whisper)
  - 时间估计: 30分钟

- [ ] **任务2.3**: 添加环境检查脚本
  - 创建 `check_dependencies.py` 脚本
  - 自动检测和报告缺失依赖
  - 时间估计: 25分钟

### 阶段3: 长期改进 (优先级: 低)

- [ ] **任务3.1**: 容器化开发环境
  - 创建 `docker-compose.dev.yml`
  - 统一开发和生产环境
  - 时间估计: 60分钟

- [ ] **任务3.2**: 完善错误处理
  - 改进依赖缺失时的错误提示
  - 添加自动降级机制说明
  - 时间估计: 30分钟

- [ ] **任务3.3**: 文档更新
  - 更新开发环境搭建文档
  - 添加依赖安装指南
  - 时间估计: 40分钟

## 技术细节

### 依赖对比表

| 包名 | 本地开发 | ZEABUR生产 | 状态 | 建议 |
|------|----------|------------|------|------|
| openai-whisper | ❌ 缺失 | ❌ 未使用 | 不一致 | 安装或替换 |
| faster-whisper | ✅ 1.2.0 | ✅ 1.0.2 | 版本差异 | 统一版本 |
| ffmpeg-python | ✅ 0.2.0 | ✅ 0.2.0 | 一致 | 保持 |
| FFmpeg (系统) | ❌ 缺失 | ✅ 已安装 | 不一致 | 安装 |

### 路由优先级

1. `/v1/video/caption` → `caption_simple.py` (当前激活)
2. `/v1/video/caption` → `caption_video.py` (完整实现，未激活)

### 环境变量配置

```env
# 推荐配置
WHISPER_MODEL_SIZE=tiny
WHISPER_COMPUTE_TYPE=int8
FFMPEG_BINARY_PATH=auto  # 自动检测
```

## 风险评估

### 高风险
- ❌ 生产环境功能正常，本地开发环境功能受限
- ❌ 开发测试无法验证真实功能

### 中风险
- ⚠️ 依赖版本不一致可能导致行为差异
- ⚠️ FFmpeg 安装可能需要系统管理员权限

### 低风险
- ✅ 现有模拟模式保证基本功能可用
- ✅ 生产环境配置已验证可用

## 验证清单

### 功能验证
- [ ] 本地环境可以处理真实视频文件
- [ ] 字幕生成返回真实结果而非模拟
- [ ] 生成的字幕文件格式正确
- [ ] 视频处理性能符合预期

### 环境验证
- [ ] `ffmpeg -version` 命令成功
- [ ] Python Whisper 包导入成功
- [ ] 临时文件正确清理
- [ ] 错误处理机制正常

---

**创建时间**: 2024-09-15  
**版本**: v1.0915  
**状态**: 待执行  
**预计完成时间**: 2-4小时