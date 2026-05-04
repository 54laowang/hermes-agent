#!/bin/bash
# Hindsight 快速启动脚本（OpenRouter 版）
# 用途: 一键启动 Hindsight 记忆系统

set -e

echo "=== 启动 Hindsight 记忆系统 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查环境变量
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo -e "${RED}❌ 未找到 OPENROUTER_API_KEY 环境变量${NC}"
    echo ""
    echo "请先设置 API Key:"
    echo "  export OPENROUTER_API_KEY='your-key'"
    echo ""
    echo "获取地址: https://openrouter.ai/keys"
    exit 1
fi

echo -e "${GREEN}✅ API Key 已设置: ${OPENROUTER_API_KEY:0:10}...${OPENROUTER_API_KEY: -6}${NC}"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    echo "请先安装 Docker Desktop: https://desktop.docker.com/mac/main/arm64/Docker.dmg"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &>/dev/null; then
    echo -e "${YELLOW}⚠️  Docker 未运行，正在启动...${NC}"
    open -a Docker
    echo "等待 Docker 启动（30-60秒）..."
    sleep 30
fi

echo -e "${GREEN}✅ Docker 运行正常${NC}"

# 检查是否已运行
if docker ps | grep -q hindsight; then
    echo -e "${GREEN}✅ Hindsight 已在运行${NC}"
    echo ""
    echo "访问地址:"
    echo "  API: http://localhost:8888"
    echo "  UI:  http://localhost:9999"
    exit 0
fi

# 检查已停止的容器
if docker ps -a | grep -q hindsight; then
    echo -e "${YELLOW}⚠️  发现已停止的容器，正在启动...${NC}"
    docker start hindsight
    sleep 5
    
    echo -e "${GREEN}✅ Hindsight 已启动${NC}"
    echo ""
    echo "访问地址:"
    echo "  API: http://localhost:8888"
    echo "  UI:  http://localhost:9999"
    exit 0
fi

# 创建数据目录
mkdir -p ~/.hindsight-docker

echo ""
echo -e "${YELLOW}🚀 启动 Hindsight 容器...${NC}"

# Docker 运行命令
docker run -d --pull always \
    -p 8888:8888 \
    -p 9999:9999 \
    --name hindsight \
    --restart unless-stopped \
    -e HINDSIGHT_API_LLM_PROVIDER=openai \
    -e HINDSIGHT_API_LLM_API_KEY=$OPENROUTER_API_KEY \
    -e HINDSIGHT_API_LLM_MODEL=openrouter/free \
    -e HINDSIGHT_API_LLM_BASE_URL=https://openrouter.ai/api/v1 \
    -v $HOME/.hindsight-docker:/home/hindsight/.pg0 \
    ghcr.io/vectorize-io/hindsight:latest

echo ""
echo "⏳ 等待服务就绪（约 10-15 秒）..."
sleep 15

# 验证启动
if docker ps | grep -q hindsight; then
    echo ""
    echo -e "${GREEN}✅ Hindsight 启动成功！${NC}"
    echo ""
    echo "访问地址:"
    echo "  API: http://localhost:8888"
    echo "  UI:  http://localhost:9999"
    echo "  数据: ~/.hindsight-docker"
    echo ""
    echo "管理命令:"
    echo "  停止: docker stop hindsight"
    echo "  日志: docker logs hindsight"
    echo "  重启: docker restart hindsight"
else
    echo ""
    echo -e "${RED}❌ 启动失败，查看日志:${NC}"
    docker logs hindsight
    exit 1
fi
