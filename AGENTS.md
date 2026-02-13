# AGENTS.md - 伏羲短剧项目

## 项目简介
AI生成短剧制作pipeline，从脚本到成片的全自动化工作流。

## 工作目录
`/home/dz/fuxi`

## 核心文件
- `WORKFLOW.md` — 完整工作流文档
- `WORKFLOW_STATUS.md` — 当前进度状态
- `pipeline/` — 核心代码
- `episodes/` — 剧集输出
- `assets/` — 素材资源

## 技术栈
- Python + Pixi
- ComfyUI (图片/视频生成)
- ElevenLabs (语音)
- FFmpeg (视频处理)

## ⚠️ 环境路径（必读！子agent 每次都要用）
- **Pixi**: `~/.pixi/bin/pixi`（不在默认 PATH 里！）
- **运行命令前必须**: `export PATH="$HOME/.pixi/bin:$PATH"`
- **标准运行方式**: `export PATH="$HOME/.pixi/bin:$PATH" && cd /home/dz/fuxi && pixi run python -m pipeline.<module> <args>`
- **ComfyUI**: `http://127.0.0.1:8188`，输出目录 `/home/dz/ComfyUI/output`
- **creative-toolkit**: `/home/dz/creative-toolkit`（已在 pipeline 代码中 sys.path.insert）
- **长时间任务**: ComfyUI 生成每帧约 5-6 分钟，用 `timeout=1200, yieldMs=120000` 等足够久，**不要因为没输出就 kill 进程！**

## 规则
- 修改代码后必须测试
- 更新 WORKFLOW_STATUS.md 反映当前状态
- 大改动先更新 TODO.md 记录计划
- commit 前确保代码能跑

## GPU
RTX 5070 Ti (16GB) — ComfyUI 图片/视频生成
