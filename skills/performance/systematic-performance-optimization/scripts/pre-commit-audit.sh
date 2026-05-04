#!/bin/bash
"""
性能审计 pre-commit 钩子
将此文件复制到 .git/hooks/pre-commit 或使用 pre-commit 框架集成

用法:
  chmod +x .agchk/hooks/pre-commit-audit.sh
  ln -s ../../.agchk/hooks/pre-commit-audit.sh .git/hooks/pre-commit
"""

echo "🔍 运行性能审计 (agchk)..."

# 颜色输出
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

WARNINGS=0

# 检查新增的 deepcopy
ADDED_DEEPCOPY=$(git diff --cached | grep -c "^+.*deepcopy")
if [ $ADDED_DEEPCOPY -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $ADDED_DEEPCOPY 个新增 deepcopy 调用${NC}"
    echo "   请确认是否必要 - 考虑使用浅拷贝或不拷贝"
    WARNINGS=$((WARNINGS + ADDED_DEEPCOPY))
fi

# 检查新增的无保护 while True
ADDED_WHILE_TRUE=$(git diff --cached | grep -c "^+.*while True")
if [ $ADDED_WHILE_TRUE -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $ADDED_WHILE_TRUE 个无限循环${NC}"
    echo "   请确认是否有最大迭代次数保护"
    WARNINGS=$((WARNINGS + ADDED_WHILE_TRUE))
fi

# 检查新增的 print 语句
ADDED_PRINT=$(git diff --cached | grep -c "^+.*print(")
if [ $ADDED_PRINT -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $ADDED_PRINT 个新增 print 语句${NC}"
    echo "   请改用 logger.debug/info 以支持日志级别控制"
    WARNINGS=$((WARNINGS + ADDED_PRINT))
fi

# 检查循环内的 f-string 日志
ADDED_FSTRING_LOG=$(git diff --cached | grep -E "^\+.*logger\..*f[\"']" | wc -l)
if [ $ADDED_FSTRING_LOG -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现 $ADDED_FSTRING_LOG 个 f-string 日志${NC}"
    echo "   请改用延迟格式化: logger.debug('msg: %s', var)"
    WARNINGS=$((WARNINGS + ADDED_FSTRING_LOG))
fi

# 检查循环内的字符串拼接
ADDED_STRING_CONCAT=$(git diff --cached | grep -B2 "^+.*+=" | grep -E "^\+.*for|^\+.*while" | wc -l)
if [ $ADDED_STRING_CONCAT -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现潜在的循环内字符串拼接${NC}"
    echo "   请考虑使用列表推导 + ''.join() 替代"
    WARNINGS=$((WARNINGS + ADDED_STRING_CONCAT))
fi

# 输出总结
echo ""
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}📊 发现 $WARNINGS 个潜在性能问题${NC}"
    echo "   以上仅为警告，不阻止提交"
    echo "   请确认改动符合性能最佳实践"
else
    echo -e "${GREEN}✅ 性能审计通过，未发现明显问题${NC}"
fi

echo ""
echo "ℹ️  完整性能审计请运行: python3 .agchk/optimize_stage1.py"
echo "ℹ️  基准测试请运行: python3 .agchk/benchmark.py"

# 不阻止提交，仅作提醒
exit 0
