#!/bin/bash
# Camofox Cookie 导入工具
# 将 Cookie 文件导入到 Camofox 的指定用户会话

set -e

CAMOFOX_URL="${CAMOFOX_URL:-http://localhost:9377}"
USER_ID="${1:-hermes}"
COOKIE_FILE="${2:-cookies.txt}"

echo "🍪 Camofox Cookie 导入工具"
echo ""

# 检查 Camofox 服务
echo "1. 检查 Camofox 服务..."
if ! curl -s "$CAMOFOX_URL/health" > /dev/null 2>&1; then
    echo "❌ Camofox 服务未运行"
    echo ""
    echo "启动命令:"
    echo "   cd ~/projects/camofox-browser && npm start"
    echo ""
    echo "或设置环境变量:"
    echo "   export CAMOFOX_URL=http://your-server:9377"
    exit 1
fi

echo "✅ Camofox 服务运行中"
echo ""

# 检查 Cookie 文件
echo "2. 检查 Cookie 文件..."
if [[ ! -f "$COOKIE_FILE" ]]; then
    echo "❌ Cookie 文件不存在: $COOKIE_FILE"
    echo ""
    echo "请先导出 Cookie:"
    echo "   ./scripts/export-cookies.sh"
    echo ""
    echo "或手动创建 Netscape 格式的 Cookie 文件:"
    echo "   .example.com\tTRUE\t/\tFALSE\t0\tcookie_name\tcookie_value"
    exit 1
fi

echo "✅ 找到 Cookie 文件: $COOKIE_FILE"
echo "   大小: $(wc -c < "$COOKIE_FILE") 字节"
echo "   行数: $(wc -l < "$COOKIE_FILE") 行"
echo ""

# 显示前几行 Cookie
if command -v jq &> /dev/null; then
    echo "3. Cookie 预览(前 3 行):"
    head -3 "$COOKIE_FILE" | grep -v "^#" | grep -v "^$"
    echo ""
fi

# 确认导入
echo "4. 准备导入..."
echo "   用户 ID: $USER_ID"
echo "   目标端点: $CAMOFOX_URL/sessions/$USER_ID/cookies"
echo ""

read -p "确认导入? (y/N): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "已取消"
    exit 0
fi

# 导入 Cookie
echo ""
echo "5. 导入 Cookie..."

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$CAMOFOX_URL/sessions/$USER_ID/cookies" \
  -H "Content-Type: text/plain" \
  --data-binary @"$COOKIE_FILE")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [[ "$HTTP_CODE" == "200" ]]; then
    echo "✅ Cookie 导入成功"
    echo ""
    if command -v jq &> /dev/null; then
        echo "响应:"
        echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    fi
else
    echo "❌ Cookie 导入失败"
    echo "HTTP 状态码: $HTTP_CODE"
    echo "响应:"
    echo "$BODY"
    exit 1
fi

echo ""
echo "6. 验证导入结果..."

# 创建测试标签页验证
TEST_TAB=$(curl -s -X POST "$CAMOFOX_URL/tabs" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"$USER_ID\", \"sessionKey\": \"cookie-test\", \"url\": \"https://example.com\"}")

TAB_ID=$(echo "$TEST_TAB" | grep -o '"tabId":"[^"]*"' | cut -d'"' -f4)

if [[ -n "$TAB_ID" ]]; then
    echo "✅ 创建测试标签页: $TAB_ID"
    # 清理测试标签页
    curl -s -X DELETE "$CAMOFOX_URL/tabs/$TAB_ID?userId=$USER_ID" > /dev/null
else
    echo "⚠️  无法创建测试标签页"
fi

echo ""
echo "✅ Cookie 导入完成!"
echo ""
echo "📖 使用说明:"
echo "   1. Cookie 已绑定到用户 ID: $USER_ID"
echo "   2. 后续使用相同 userId 的请求会自动携带这些 Cookie"
echo "   3. 测试访问:"
echo "      curl -X POST $CAMOFOX_URL/tabs \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d '{\"userId\": \"$USER_ID\", \"url\": \"https://target-site.com\"}'"
echo ""
echo "⚠️  安全提醒:"
echo "   - Cookie 包含敏感登录信息"
echo "   - 请勿分享 $COOKIE_FILE 文件"
echo "   - 使用后建议删除: rm $COOKIE_FILE"
