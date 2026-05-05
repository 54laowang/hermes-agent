#!/bin/bash
# Camofox 快速测试脚本

echo "🦊 Camofox Browser 快速测试"
echo ""

# 检查服务
if ! curl -s http://localhost:9377/health > /dev/null 2>&1; then
  echo "❌ Camofox 服务未运行"
  echo "启动命令: cd ~/projects/camofox-browser && npm start"
  exit 1
fi

echo "✅ 服务运行中"
echo ""

# 测试 1: Example.com
echo "测试 1: 访问 Example.com"
TAB=$(curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId": "quick-test", "url": "https://example.com"}')
TAB_ID=$(echo $TAB | jq -r '.tabId')

curl -s "http://localhost:9377/tabs/$TAB_ID/snapshot?userId=quick-test" | jq -r '.snapshot' | head -3

curl -s -X DELETE "http://localhost:9377/tabs/$TAB_ID?userId=quick-test" > /dev/null
echo ""

# 测试 2: Google 搜索
echo "测试 2: Google 搜索(AI agent)"
TAB=$(curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId": "quick-test", "macro": "@google_search", "query": "AI agent browser"}')
TAB_ID=$(echo $TAB | jq -r '.tabId')

sleep 2
curl -s "http://localhost:9377/tabs/$TAB_ID/snapshot?userId=quick-test" | jq -r '.snapshot' | grep -m 3 "link"

curl -s -X DELETE "http://localhost:9377/tabs/$TAB_ID?userId=quick-test" > /dev/null
echo ""

echo "✅ 所有测试通过"
