#!/bin/bash

# 伏羲纪元 - Fish Audio 本地服务器启动脚本
# 支持 Docker 和源码两种方式

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🎤 伏羲纪元 - Fish Audio 本地服务启动${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 默认端口
PORT=${FISH_AUDIO_PORT:-8000}
MODE=${FISH_AUDIO_MODE:-auto}

echo -e "\n${YELLOW}可用的启动方式:${NC}"
echo "  1) Docker (推荐)"
echo "  2) 源码安装"
echo "  3) Python 包"
echo ""

# 如果提供了参数，使用参数
if [ -z "$1" ]; then
    read -p "请选择启动方式 [1-3] (默认: 1): " choice
    choice=${choice:-1}
else
    choice=$1
fi

case $choice in
    1)
        echo -e "\n${BLUE}[1/3] 检查 Docker...${NC}"
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}✗ Docker 未安装${NC}"
            echo "  请访问: https://docs.docker.com/get-docker/"
            exit 1
        fi
        echo -e "${GREEN}✓ Docker 可用${NC}"

        echo -e "\n${BLUE}[2/3] 拉取 Fish Audio 镜像...${NC}"
        docker pull fishaudio/fish-speech:latest

        echo -e "\n${BLUE}[3/3] 启动 Fish Audio 服务...${NC}"

        # 检查 GPU 可用性
        if command -v nvidia-smi &> /dev/null; then
            echo -e "${GREEN}✓ 检测到 NVIDIA GPU，使用 GPU 加速${NC}"
            docker run --gpus all \
                -p ${PORT}:8000 \
                -v fish_audio_models:/root/.cache/fish_speech/checkpoints \
                --name fish_audio_server \
                fishaudio/fish-speech:latest
        else
            echo -e "${YELLOW}⚠ 未检测到 GPU，使用 CPU 模式${NC}"
            docker run -p ${PORT}:8000 \
                -v fish_audio_models:/root/.cache/fish_speech/checkpoints \
                --name fish_audio_server \
                fishaudio/fish-speech:latest
        fi
        ;;

    2)
        echo -e "\n${BLUE}[1/4] 克隆仓库...${NC}"
        if [ -d "fish-speech" ]; then
            echo -e "${YELLOW}⚠ fish-speech 目录已存在${NC}"
        else
            git clone https://github.com/fishaudio/fish-speech.git
        fi
        cd fish-speech

        echo -e "\n${BLUE}[2/4] 创建虚拟环境...${NC}"
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate

        echo -e "\n${BLUE}[3/4] 安装依赖...${NC}"
        pip install -e .

        echo -e "\n${BLUE}[4/4] 启动服务器...${NC}"
        python -m fish_speech.server --host 0.0.0.0 --port ${PORT}
        ;;

    3)
        echo -e "\n${BLUE}[1/2] 安装 fish-speech 包...${NC}"
        pip install fish-speech

        echo -e "\n${BLUE}[2/2] 启动服务器...${NC}"
        python -m fish_speech.server --host 0.0.0.0 --port ${PORT}
        ;;

    *)
        echo -e "${RED}✗ 无效的选择${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Fish Audio 服务启动成功!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "服务地址: ${BLUE}http://localhost:${PORT}${NC}"
echo ""
echo "后续步骤:"
echo "  1. 在另一个终端运行配音生成:"
echo -e "     ${YELLOW}export FISH_AUDIO_MODE=local${NC}"
echo -e "     ${YELLOW}python -m pipeline.synth_voice ep002${NC}"
echo ""
echo "环境变量配置:"
echo -e "  ${YELLOW}FISH_AUDIO_LOCAL${NC}  - 本地服务地址 (默认: http://localhost:8000)"
echo -e "  ${YELLOW}FISH_AUDIO_MODE${NC}   - 模式选择 (local / remote / auto)"
echo ""
