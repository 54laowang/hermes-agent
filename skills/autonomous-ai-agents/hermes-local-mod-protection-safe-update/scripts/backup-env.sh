#!/bin/bash
# .env 自动备份脚本
# 每次保守式更新前自动调用，备份所有环境变量配置

ENV_FILE="$HOME/.hermes/.env"
BACKUP_DIR="$HOME/.hermes/env-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 检查 .env 文件是否存在
if [[ ! -f "$ENV_FILE" ]]; then
    echo "⚠️  .env 文件不存在，跳过备份"
    exit 0
fi

# 备份 .env
BACKUP_FILE="$BACKUP_DIR/env-$TIMESTAMP.bak"
cp "$ENV_FILE" "$BACKUP_FILE"

# 计算文件大小
SIZE=$(wc -c < "$BACKUP_FILE" | awk '{print $1}')
LINES=$(wc -l < "$BACKUP_FILE" | awk '{print $1}')

echo "✅ .env 备份完成"
echo "   文件: $BACKUP_FILE"
echo "   大小: $SIZE bytes"
echo "   行数: $LINES 行"

# 保留最近 30 天的备份，自动清理旧备份
find "$BACKUP_DIR" -name "env-*.bak" -mtime +30 -delete 2>/dev/null
if [[ $? -eq 0 ]]; then
    echo "🧹 已清理 30 天前的旧备份"
fi

# 列出最近的备份
echo ""
echo "📋 最近备份列表:"
ls -lt "$BACKUP_DIR"/env-*.bak 2>/dev/null | head -5 | awk '{print "   "$9" ("$6" "$7" "$8")"}'

exit 0
