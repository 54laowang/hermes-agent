#!/bin/bash
# 桌面宠物启动脚本

cd ~/.hermes/desktop-pet

echo "🐱 启动桌面宠物..."
echo "📍 端口: 51983"
echo "💡 单击拖动 | 双击关闭 | 右键菜单"
echo ""

python3 pet_main.py
