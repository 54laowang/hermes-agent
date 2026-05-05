#!/bin/bash
# Hermes Web UI 快速诊断脚本
# 用法：bash diagnose.sh

set -e

echo "=== Hermes Web UI 诊断 ==="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查服务状态
echo -e "${YELLOW}[1/6] 检查服务状态${NC}"
if pgrep -f "hermes-web-ui" > /dev/null; then
    PID=$(pgrep -f "hermes-web-ui" | head -1)
    echo -e "  ${GREEN}✓${NC} Web UI 运行中 (PID: $PID)"
else
    echo -e "  ${RED}✗${NC} Web UI 未运行"
    echo "  启动命令: hermes-web-ui start"
fi
echo ""

# 2. 检查端口
echo -e "${YELLOW}[2/6] 检查端口${NC}"
if lsof -i :8648 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} 端口 8648 (Web UI) 已监听"
else
    echo -e "  ${RED}✗${NC} 端口 8648 未监听"
fi

if lsof -i :8642 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} 端口 8642 (Hermes API) 已监听"
else
    echo -e "  ${YELLOW}!${NC} 端口 8642 未监听（Gateway 可能未运行）"
fi
echo ""

# 3. 检查版本
echo -e "${YELLOW}[3/6] 检查版本${NC}"
VERSION=$(hermes-web-ui --version 2>&1 || echo "未知")
echo "  Web UI 版本: $VERSION"
NODE_VERSION=$(node --version 2>&1 || echo "未知")
echo "  Node.js 版本: $NODE_VERSION"

# Node.js 版本检查
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | tr -d 'v')
if [ "$NODE_MAJOR" -lt 22 ]; then
    echo -e "  ${YELLOW}!${NC} Node.js < 22，可能缺少 node:sqlite 支持"
fi
echo ""

# 4. 检查数据库
echo -e "${YELLOW}[4/6] 检查数据库${NC}"

# Web UI 数据库
WEBUI_DB="$HOME/.hermes-web-ui/hermes-web-ui.db"
if [ -f "$WEBUI_DB" ]; then
    SESSIONS=$(sqlite3 "$WEBUI_DB" "SELECT COUNT(*) FROM sessions;" 2>/dev/null || echo "错误")
    MESSAGES=$(sqlite3 "$WEBUI_DB" "SELECT COUNT(*) FROM messages;" 2>/dev/null || echo "错误")
    echo -e "  ${GREEN}✓${NC} Web UI 数据库存在"
    echo "    会话数: $SESSIONS"
    echo "    消息数: $MESSAGES"
else
    echo -e "  ${RED}✗${NC} Web UI 数据库不存在: $WEBUI_DB"
fi

# Hermes 源数据库
HERMES_DB="$HOME/.hermes/state.db"
if [ -f "$HERMES_DB" ]; then
    SOURCE_COUNT=$(sqlite3 "$HERMES_DB" "SELECT COUNT(*) FROM sessions;" 2>/dev/null || echo "错误")
    echo -e "  ${GREEN}✓${NC} Hermes 数据库存在"
    echo "    会话数: $SOURCE_COUNT"
    
    # 按来源统计
    echo "    来源分布:"
    sqlite3 "$HERMES_DB" "SELECT source, COUNT(*) as count FROM sessions GROUP BY source ORDER BY count DESC LIMIT 5;" 2>/dev/null | while IFS='|' read source count; do
        echo "      - $source: $count"
    done
else
    echo -e "  ${RED}✗${NC} Hermes 数据库不存在: $HERMES_DB"
fi
echo ""

# 5. 检查认证
echo -e "${YELLOW}[5/6] 检查认证${NC}"
TOKEN_FILE="$HOME/.hermes-web-ui/.token"
if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat "$TOKEN_FILE")
    echo -e "  ${GREEN}✓${NC} Token 文件存在"
    echo "  Token: ${TOKEN:0:20}..."
    echo "  访问 URL: http://localhost:8648/#/?token=$TOKEN"
else
    echo -e "  ${YELLOW}!${NC} Token 文件不存在（认证可能未启用）"
fi
echo ""

# 6. 检查最近日志
echo -e "${YELLOW}[6/6] 最近日志（最后 10 行）${NC}"
LOG_FILE="$HOME/.hermes-web-ui/server.log"
if [ -f "$LOG_FILE" ]; then
    tail -10 "$LOG_FILE" | sed 's/^/  /'
else
    echo -e "  ${YELLOW}!${NC} 日志文件不存在"
fi
echo ""

# 问题诊断
echo -e "${YELLOW}=== 诊断结果 ===${NC}"
ISSUES=0

# 检查会话同步问题
if [ -f "$HERMES_DB" ] && [ -f "$WEBUI_DB" ]; then
    SOURCE_COUNT=$(sqlite3 "$HERMES_DB" "SELECT COUNT(*) FROM sessions;" 2>/dev/null || echo "0")
    WEBUI_COUNT=$(sqlite3 "$WEBUI_DB" "SELECT COUNT(*) FROM sessions;" 2>/dev/null || echo "0")
    
    if [ "$SOURCE_COUNT" -gt 0 ] && [ "$WEBUI_COUNT" -eq 0 ]; then
        echo -e "  ${RED}✗${NC} 源数据库有会话但 Web UI 无数据 - 同步问题"
        echo "    可能原因：v0.5.4 的同步 bug（只同步 api_server 来源）"
        echo "    解决方案：参考 hermes-web-ui-troubleshooting skill"
        ISSUES=$((ISSUES + 1))
    fi
fi

# 检查 Node.js 版本
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | tr -d 'v')
if [ "$NODE_MAJOR" -lt 22 ]; then
    echo -e "  ${YELLOW}!${NC} Node.js 版本过低，可能缺少 node:sqlite"
    echo "    建议升级到 Node.js >= 22.5.0"
    ISSUES=$((ISSUES + 1))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} 未发现明显问题"
fi

echo ""
echo "详细文档：使用 skill_view('hermes-web-ui-troubleshooting') 查看"
