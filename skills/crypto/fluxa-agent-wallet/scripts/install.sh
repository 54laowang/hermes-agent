#!/bin/bash
# FluxA Agent Wallet 快速安装脚本
# 用法: ./install.sh

set -e

echo "🦞 FluxA Agent Wallet 安装脚本"
echo "================================"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo ""

# 安装 CLI
echo "📦 安装 FluxA Wallet CLI..."
npm install -g @fluxa-pay/fluxa-wallet@0.4.5

echo ""
echo "✅ CLI 安装完成"
echo ""

# 检查状态
echo "🔍 检查 Agent 状态..."
fluxa-wallet status

echo ""
echo "================================"
echo "✅ 安装完成！"
echo ""
echo "下一步："
echo "1. 如果未初始化，运行: fluxa-wallet init --name \"您的 Agent 名称\" --client \"客户端信息\""
echo "2. 链接钱包: fluxa-wallet link-wallet"
echo "3. 开始使用 FluxA Agent Wallet 功能"
echo ""
echo "📖 完整文档: ~/.hermes/skills/crypto/fluxa-agent-wallet/SKILL.md"
echo "🌐 官方文档: https://github.com/fluxa-agent-payment/fluxa-ai-wallet-mcp"
