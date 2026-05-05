#!/bin/bash
# 本地修改验证脚本
# 用于合并后验证本地自定义内容是否保留

set -e

echo "🔍 验证本地修改保留情况..."
echo ""

# 定义关键内容检查
declare -A checks=(
    ["README 达尔文进化"]="达尔文进化方法论"
    ["README 记忆系统"]="记忆系统优化"
)

all_passed=true

for name in "${!checks[@]}"; do
    keyword="${checks[$name]}"
    if grep -q "$keyword" ~/.hermes/hermes-agent/README.md; then
        echo "✅ $name：保留"
    else
        echo "❌ $name：丢失"
        all_passed=false
    fi
done

echo ""

# 检查本地增强文件
files=(
    "$HOME/.hermes/context_triggers.yaml"
    "$HOME/.hermes/hooks/context_discovery.py"
    "$HOME/.hermes/memory/darwin-evolution/"
)

echo "📁 检查本地增强文件..."
for file in "${files[@]}"; do
    if [ -e "$file" ]; then
        echo "✅ $(basename $file)：存在"
    else
        echo "⚠️  $(basename $file)：不存在"
    fi
done

echo ""

if [ "$all_passed" = true ]; then
    echo "✅ 所有本地修改验证通过"
    exit 0
else
    echo "❌ 部分本地修改丢失，请检查合并过程"
    exit 1
fi
