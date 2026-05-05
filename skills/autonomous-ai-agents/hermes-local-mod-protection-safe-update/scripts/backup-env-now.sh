#!/bin/bash
# 手动备份 .env 文件
# 用法: backup-env-now.sh [备注]

ENV_FILE="$HOME/.hermes/.env"
BACKUP_DIR="$HOME/.hermes/env-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 检查 .env 文件是否存在
if [[ ! -f "$ENV_FILE" ]]; then
    echo "❌ .env 文件不存在"
    exit 1
fi

# 备份文件名（支持备注）
if [[ -n "$1" ]]; then
    BACKUP_FILE="$BACKUP_DIR/env-$TIMESTAMP-$1.bak"
else
    BACKUP_FILE="$BACKUP_DIR/env-$TIMESTAMP-manual.bak"
fi

# 备份
cp "$ENV_FILE" "$BACKUP_FILE"

# 计算文件大小
SIZE=$(wc -c < "$BACKUP_FILE" | awk '{print $1}')
LINES=$(wc -l < "$BACKUP_FILE" | awk '{print $1}')

echo "✅ .env 手动备份完成"
echo "   文件: $BACKUP_FILE"
echo "   大小: $SIZE bytes"
echo "   行数: $LINES 行"

# 显示配置项
echo ""
echo "📋 已备份的配置项:"
cat "$BACKUP_FILE" | grep -v "^#" | grep -v "^$" | cut -d'=' -f1 | sed 's/^/   - /'
