#!/bin/bash
# TuriX Status Checker
# 检查 TuriX 任务运行状态

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$HOME/.hermes/TuriX-CUA"
LOG_FILE="$PROJECT_DIR/.turix_tmp/logging.log"

# 检查进程
PID=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}')

if [[ -z "$PID" ]]; then
    echo -e "${BLUE}状态: 未运行${NC}"
    exit 0
fi

echo -e "${GREEN}进程ID: $PID${NC}"

# 检查日志文件
if [[ ! -f "$LOG_FILE" ]]; then
    echo -e "${YELLOW}状态: 启动中（日志未创建）${NC}"
    exit 0
fi

# 获取最新日志
LAST_LOG=$(tail -1 "$LOG_FILE" 2>/dev/null)
STEP_COUNT=$(ls "$PROJECT_DIR/examples/.turix_tmp"/brain_llm_interactions.log_brain_*.txt 2>/dev/null | wc -l | tr -d ' ')

# 判断状态
if echo "$LAST_LOG" | grep -qi "completed"; then
    echo -e "${GREEN}状态: 已完成${NC}"
elif echo "$LAST_LOG" | grep -qi "failed"; then
    echo -e "${RED}状态: 失败${NC}"
elif echo "$LAST_LOG" | grep -qi "step"; then
    echo -e "${GREEN}状态: 运行中（步骤数: $STEP_COUNT）${NC}"
    echo -e "${BLUE}最新日志: $LAST_LOG${NC}"
else
    echo -e "${YELLOW}状态: 未知（步骤数: $STEP_COUNT）${NC}"
fi

# 显示内存使用
MEM_MB=$(ps -p "$PID" -o rss= | awk '{printf "%.0f", $1/1024}')
echo -e "${BLUE}内存使用: ${MEM_MB}MB${NC}"

# 显示最近错误（如果有）
if tail -50 "$LOG_FILE" | grep -qi "error\|exception\|failed"; then
    echo -e "${YELLOW}⚠️ 发现错误日志，请检查:${NC}"
    tail -50 "$LOG_FILE" | grep -i "error\|exception\|failed" | tail -3
fi
