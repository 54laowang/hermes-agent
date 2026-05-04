#!/bin/bash
# 启动桌面宠物并强制置顶

cd ~/.hermes/desktop-pet

# 启动宠物
python3 pet_main.py &
PET_PID=$!

# 等待启动
sleep 2

# macOS 强制置顶
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS: 设置窗口置顶..."
    
    # 方法1: AppleScript
    osascript -e 'tell application "System Events" to set frontmost of first process whose name contains "Python" to true'
    
    # 方法2: 使用 yabai（如果安装了）
    if command -v yabai &> /dev/null; then
        yabai -m window --layer above
    fi
fi

echo "✅ 桌面宠物已启动 (PID: $PET_PID)"
echo "📌 如果置顶不生效，请尝试："
echo "   1. 右键宠物 → 📌 始终置顶"
echo "   2. 双击宠物切换置顶状态"

wait $PET_PID
