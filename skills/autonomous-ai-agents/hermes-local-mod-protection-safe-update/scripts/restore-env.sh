#!/bin/bash
# .env 一键恢复脚本
# 从备份中恢复 .env 文件

BACKUP_DIR="$HOME/.hermes/env-backups"
ENV_FILE="$HOME/.hermes/.env"

echo "🔧 .env 恢复工具"
echo "================"
echo ""

# 检查备份目录
if [[ ! -d "$BACKUP_DIR" ]]; then
    echo "❌ 备份目录不存在: $BACKUP_DIR"
    exit 1
fi

# 列出可用备份
echo "📋 可用备份列表:"
echo ""
backups=($(ls -t "$BACKUP_DIR"/env-*.bak 2>/dev/null))

if [[ ${#backups[@]} -eq 0 ]]; then
    echo "❌ 没有找到备份文件"
    exit 1
fi

# 显示最近 10 个备份
for i in "${!backups[@]}"; do
    if [[ $i -ge 10 ]]; then break; fi
    backup="${backups[$i]}"
    size=$(wc -c < "$backup" | awk '{print $1}')
    lines=$(wc -l < "$backup" | awk '{print $1}')
    timestamp=$(basename "$backup" | sed 's/env-\([0-9_]*\)\.bak/\1/')
    
    # 格式化时间戳
    year=${timestamp:0:4}
    month=${timestamp:4:2}
    day=${timestamp:6:2}
    hour=${timestamp:9:2}
    min=${timestamp:11:2}
    sec=${timestamp:13:2}
    
    echo "[$i] $year-$month-$day $hour:$min:$sec  ($lines 行, $size bytes)"
done

echo ""
read -p "选择要恢复的备份编号 [0-9，默认 0]: " choice

# 默认选择最新的备份
choice=${choice:-0}

if [[ ! ${backups[$choice]} ]]; then
    echo "❌ 无效的选择"
    exit 1
fi

selected_backup="${backups[$choice]}"
timestamp=$(basename "$selected_backup" | sed 's/env-\([0-9_]*\)\.bak/\1/')

echo ""
echo "📦 即将恢复备份:"
echo "   文件: $selected_backup"
echo "   时间: ${timestamp:0:4}-${timestamp:4:2}-${timestamp:6:2} ${timestamp:9:2}:${timestamp:11:2}:${timestamp:13:2}"
echo ""

read -p "确认恢复？[y/N]: " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "❌ 已取消"
    exit 0
fi

# 备份当前 .env（如果存在）
if [[ -f "$ENV_FILE" ]]; then
    current_backup="$BACKUP_DIR/env-current-$(date +%Y%m%d_%H%M%S).bak"
    cp "$ENV_FILE" "$current_backup"
    echo "✅ 当前 .env 已备份到: $current_backup"
fi

# 恢复选择的备份
cp "$selected_backup" "$ENV_FILE"

echo ""
echo "✅ 恢复完成！"
echo "   恢复文件: $ENV_FILE"
echo "   来源: $selected_backup"
echo ""
echo "⚠️  请重启 Gateway 使配置生效:"
echo "   hermes gateway restart"
