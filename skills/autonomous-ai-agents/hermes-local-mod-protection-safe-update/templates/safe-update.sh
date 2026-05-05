#!/bin/bash
# Hermes 安全更新脚本 - 自动保护本地修改后再更新
# 来源: hermes-local-mod-protection-safe-update skill

HERMES_DIR="/Users/me/.hermes/hermes-agent"
PATCH_BACKUP_DIR="/Users/me/.hermes/patch-backups"

echo "🔒 Hermes 安全更新启动..."
cd "$HERMES_DIR"

# 创建备份目录
mkdir -p "$PATCH_BACKUP_DIR"

# 检查是否有未提交的修改
if [[ -n $(git status --porcelain) ]]; then
    echo "📦 检测到未提交的修改，正在自动备份..."
    
    # 备份当前时间戳
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    # 生成 patch 备份
    git diff > "$PATCH_BACKUP_DIR/pre-update-$TIMESTAMP.patch"
    echo "✅ 已备份到: $PATCH_BACKUP_DIR/pre-update-$TIMESTAMP.patch"
    
    # 特别备份 split-brain 修复
    if git diff --name-only | grep -q "gateway/platforms/base.py"; then
        git diff gateway/platforms/base.py > ~/hermes-split-brain-fix.patch
        echo "✅ split-brain 修复已单独备份"
    fi
fi

echo ""
echo "🚀 开始拉取更新..."
git pull --rebase origin main

echo ""
echo "✅ 更新完成！"
echo "📋 如果有冲突，请手动解决后提交"
echo ""
git status
