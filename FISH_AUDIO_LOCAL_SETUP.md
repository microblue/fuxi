# 🎤 Fish Audio 本地部署指南

在本地运行 Fish Audio 服务，无需 API Key，支持离线使用和 GPU 加速。

---

## 快速开始（3 步）

### 1️⃣ 启动 Fish Audio 服务

**Linux / Mac:**
```bash
chmod +x scripts/start_fish_audio.sh
./scripts/start_fish_audio.sh
# 选择 1 (Docker) 或 2 (源码) 或 3 (pip)
```

**Windows:**
```bash
scripts/start_fish_audio.bat
# 选择 1 (Docker) 或 2 (源码) 或 3 (pip)
```

### 2️⃣ 设置环境变量

```bash
# 指定本地模式
export FISH_AUDIO_MODE=local
# 或在 Windows 中：
set FISH_AUDIO_MODE=local
```

### 3️⃣ 生成配音

```bash
# 自动连接本地服务器
python -m pipeline.synth_voice ep002

# 输出示例：
# ✓ Generated via Fish Audio (local)
```

---

## 详细安装步骤

### 方案 A: Docker（推荐）

最简单，自动处理所有依赖和模型。

#### 安装 Docker

- **Mac**: https://docs.docker.com/desktop/install/mac-install/
- **Linux**: https://docs.docker.com/engine/install/
- **Windows**: https://docs.docker.com/desktop/install/windows-install/

#### 启动服务

```bash
# 1. 拉取镜像
docker pull fishaudio/fish-speech:latest

# 2. 启动服务（GPU 加速，如果有 GPU）
docker run --gpus all \
    -p 8000:8000 \
    -v fish_audio_models:/root/.cache/fish_speech/checkpoints \
    --name fish_audio_server \
    fishaudio/fish-speech:latest

# 或使用 CPU（无需 NVIDIA GPU）
docker run -p 8000:8000 \
    -v fish_audio_models:/root/.cache/fish_speech/checkpoints \
    --name fish_audio_server \
    fishaudio/fish-speech:latest
```

#### 停止服务

```bash
docker stop fish_audio_server
docker remove fish_audio_server
```

---

### 方案 B: 源码安装

更新快，便于开发。

```bash
# 1. 克隆仓库
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate (Windows)

# 3. 安装依赖
pip install -e .

# 4. 启动服务
python -m fish_speech.server --host 0.0.0.0 --port 8000
```

---

### 方案 C: Pip 包安装

最快速。

```bash
# 1. 安装
pip install fish-speech

# 2. 启动
python -m fish_speech.server --host 0.0.0.0 --port 8000
```

---

## 配置和使用

### 环境变量

```bash
# 本地服务地址（默认: http://localhost:8000）
export FISH_AUDIO_LOCAL="http://localhost:8000"

# 模式选择：local / remote / auto （默认: auto）
export FISH_AUDIO_MODE="local"

# 远程 API Key（如果使用远程服务）
export FISH_AUDIO_API_KEY="your_key_here"
```

### 模式说明

| 模式 | 说明 | 用途 |
|------|------|------|
| `local` | 强制使用本地服务器 | 完全离线 |
| `remote` | 强制使用远程 API | 需要 API Key |
| `auto` | 自动选择（优先本地） | 推荐（最灵活） |

### 自动模式工作流

```
本地服务器运行？
  ├─ YES → 使用本地服务器
  └─ NO  → 检查 API Key
          ├─ YES → 使用远程 API
          └─ NO  → 使用占位符（静音）
```

---

## 完整工作流示例

### 终端 1: 启动 Fish Audio

```bash
# Mac/Linux
./scripts/start_fish_audio.sh
# 选择 1 (Docker)

# 或 Windows
scripts/start_fish_audio.bat
# 选择 1 (Docker)

# 输出：
# Fish Audio service started!
# Service address: http://localhost:8000
```

### 终端 2: 生成配音

```bash
# 设置本地模式
export FISH_AUDIO_MODE=local

# 生成配音
python -m pipeline.synth_voice ep002

# 输出：
# ============================================================
# 语音合成 — ep002
# ============================================================
#   [TTS] S01.wav: "邪灵之眼......他被雷泽的恶灵附身了!"
#         character=elder_woman, emotion=terror, 3.0s
#     ✓ Generated via Fish Audio (local)
#   [TTS] S02.wav: "..."
#     ✓ Generated via Fish Audio (local)
# ...
```

### 终端 3: 生成最终视频

```bash
# 生成视频（自动使用已生成的配音）
python -m pipeline.render_video ep002

# 输出：
# episodes/ep002/video/final.mp4
```

---

## 系统要求

### Docker 方案

| 要求 | 最低 | 推荐 |
|------|------|------|
| RAM | 4GB | 8GB+ |
| 磁盘 | 5GB | 10GB+ |
| 网络 | 100 Mbps | 200+ Mbps |
| GPU | 否（CPU 可用） | NVIDIA GPU (6GB+) |

### 源码方案

| 要求 | 最低 | 推荐 |
|------|------|------|
| Python | 3.8 | 3.10+ |
| 虚拟环境 | 推荐 | 必需 |
| RAM | 8GB | 16GB+ |
| 磁盘 | 10GB | 20GB+ |
| GPU | 否 | NVIDIA GPU (6GB+) |

---

## GPU 加速

### 检查 GPU

```bash
# NVIDIA GPU
nvidia-smi

# 输出示例：
# NVIDIA-SMI 530.41.03  Driver Version: 530.41.03  CUDA Version: 12.1
```

### 启用 GPU（Docker）

```bash
# 确保已安装 nvidia-docker
docker --gpus all run ... fishaudio/fish-speech:latest
```

### 启用 GPU（源码）

```bash
# PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 或使用 conda
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

---

## 故障排除

### ❌ Docker 启动失败

```bash
# 检查 Docker 是否运行
docker ps

# 查看日志
docker logs fish_audio_server

# 重启 Docker
docker restart fish_audio_server

# 删除并重新创建
docker rm fish_audio_server
docker run -p 8000:8000 fishaudio/fish-speech:latest
```

### ❌ 连接超时

```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 如果无响应，检查防火墙
# Windows: 允许 8000 端口通过防火墙
# Mac/Linux: sudo ufw allow 8000
```

### ❌ 模型下载缓慢

```bash
# 预先下载模型（可选）
# 首次运行会自动下载，约 2-3GB

# 如果下载中断，重新启动服务
docker restart fish_audio_server
```

### ❌ 生成语音失败

```bash
# 检查本地服务是否可用
export FISH_AUDIO_MODE=auto
python -m pipeline.synth_voice ep002

# 如果仍失败，检查：
# 1. 服务是否在运行
# 2. 端口是否正确 (8000)
# 3. 是否设置了正确的 FISH_AUDIO_LOCAL
```

---

## 性能对比

### 速度

| 模式 | 文本长度 | CPU | GPU |
|------|---------|-----|-----|
| 本地 (Docker) | 100字 | ~2-3s | ~0.5s |
| 本地 (源码) | 100字 | ~2-3s | ~0.5s |
| 远程 API | 100字 | ~1-2s* | - |

*远程 API 包括网络延迟

### 成本

| 模式 | 成本 |
|------|------|
| 本地 Docker | ✅ 免费 |
| 本地 源码 | ✅ 免费 |
| 远程 API | 💰 按次计费 |

---

## 高级配置

### 自定义端口

```bash
# 启动脚本中指定
export FISH_AUDIO_PORT=9000
./scripts/start_fish_audio.sh

# 或 Docker 命令中
docker run -p 9000:8000 fishaudio/fish-speech:latest
```

### 自定义服务地址

```bash
# 远程服务器
export FISH_AUDIO_LOCAL="http://192.168.1.100:8000"
export FISH_AUDIO_MODE="local"

python -m pipeline.synth_voice ep002
```

### 保存生成的音频

```bash
# 音频自动保存在
episodes/{ep}/audio/S01.wav
episodes/{ep}/audio/S02.wav
# ...
```

---

## 常见问题

### Q: 能在远程服务器上运行吗？

A: 可以。在远程服务器上启动 Fish Audio，然后设置：
```bash
export FISH_AUDIO_LOCAL="http://remote_server:8000"
export FISH_AUDIO_MODE="local"
```

### Q: 能同时使用本地和远程吗？

A: 支持自动降级：
- 优先使用本地服务
- 本地不可用时，使用远程 API
- 都不可用时，使用占位符

```bash
export FISH_AUDIO_MODE="auto"
```

### Q: 能改变生成的语音质量吗？

A: Fish Audio 支持多种模型和参数。查看官方文档：
https://github.com/fishaudio/fish-speech

### Q: 能用其他 TTS 替代 Fish Audio 吗？

A: 可以。在 `synth_voice.py` 中编辑 `CHARACTER_VOICES` 改用 Edge TTS 或其他提供商。

---

## 下一步

- ✅ 本地部署 Fish Audio
- ✅ 设置环境变量
- ✅ 生成第一批配音
- ⏭️  配置 shots.json（对话、角色、情感）
- ⏭️  生成最终视频

---

## 参考资源

- **Fish Audio 官方**: https://github.com/fishaudio/fish-speech
- **Docker 文档**: https://docs.docker.com
- **伏羲项目**: `/home/dz/fuxi`

---

## 支持

如有问题，参考：
- `AUDIO_SYSTEM_GUIDE.md` - 完整音频系统教程
- `AUDIO_QUICK_START.md` - 快速参考
- `pipeline/synth_voice.py` - 源代码注释

