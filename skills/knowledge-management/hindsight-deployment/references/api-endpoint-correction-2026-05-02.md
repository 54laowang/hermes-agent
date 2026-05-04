# Hindsight API 端点修正记录

**日期**: 2026-05-02
**问题**: 官方文档中的 API 端点与实际自托管部署不匹配
**状态**: ✅ 已解决

---

## 问题现象

用户报告 Hindsight 本地无法自动导入记忆，所有 API 调用返回 404。

### 测试过的错误端点

```bash
# 以下端点均返回 {"detail":"Not Found"}
curl http://localhost:8888/retain
curl http://localhost:8888/recall
curl http://localhost:8888/memories
curl http://localhost:8888/api/memories
curl http://localhost:8888/v1/memories
```

---

## 调试过程

### Step 1: 检查 OpenAPI 文档

```bash
curl -s http://localhost:8888/openapi.json | \
  python3 -c "import sys, json; data = json.load(sys.stdin); print('\n'.join(sorted(data['paths'].keys())))"
```

**发现**: 实际端点格式为 `/v1/default/banks/{bank_id}/memories`

### Step 2: 测试正确端点

```bash
# 创建 Bank
curl -X PUT "http://localhost:8888/v1/default/banks/hermes-agent" \
  -H "Content-Type: application/json" \
  -d '{"mission":"Hermes Agent 对话记忆系统"}'

# 存储记忆
curl -X POST "http://localhost:8888/v1/default/banks/hermes-agent/memories" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"content":"测试记忆"}]}'

# 检索记忆
curl -X POST "http://localhost:8888/v1/default/banks/hermes-agent/memories/recall" \
  -H "Content-Type: application/json" \
  -d '{"query":"测试","max_tokens":100}'
```

**结果**: ✅ 所有操作成功

---

## 根本原因

1. **文档过时**: 官方 README 使用简化的 LLM Wrapper 示例，但自托管部署需要完整的 REST API 端点
2. **请求格式错误**: 文档示例中直接使用 `content` 字段，但实际需要 `items` 数组包装
3. **超时设置不足**: LLM 处理需要时间，默认 5 秒超时太短

---

## 正确的 API 使用模式

### 1. 创建 Bank（前置条件）

```bash
curl -X PUT "http://localhost:8888/v1/default/banks/{bank_id}" \
  -H "Content-Type: application/json" \
  -d '{"mission":"描述"}'
```

### 2. 存储记忆

```bash
curl -X POST "http://localhost:8888/v1/default/banks/{bank_id}/memories" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"content":"记忆内容"}]}'  # ⚠️ 必须用 items 数组
```

**超时**: 建议 60 秒（LLM 处理需要时间）

### 3. 检索记忆

```bash
curl -X POST "http://localhost:8888/v1/default/banks/{bank_id}/memories/recall" \
  -H "Content-Type: application/json" \
  -d '{"query":"查询内容","max_tokens":1000,"budget":"mid"}'
```

---

## Python Hook 修复示例

**修复前**:
```python
# ❌ 错误的端点和格式
response = requests.post(
    f"{HINDSIGHT_API}/retain",
    json={"bank_id": bank_id, "content": content},
    timeout=5
)
```

**修复后**:
```python
# ✅ 正确的端点和格式
response = requests.post(
    f"{HINDSIGHT_API}/v1/default/banks/{bank_id}/memories",
    json={"items": [{"content": content}]},
    timeout=60  # 增加超时
)
```

---

## 验证结果

### 存储测试

```json
{
  "success": true,
  "bank_id": "hermes-agent",
  "items_count": 1,
  "usage": {
    "input_tokens": 5347,
    "output_tokens": 747,
    "total_tokens": 6094
  }
}
```

### 检索测试

```json
{
  "results": [
    {
      "id": "a69bdf28-5059-4de0-b0c2-b3aa193de8e3",
      "text": "用户偏好使用中文，关注 AI 和股票市场 | Involving: 用户",
      "type": "world",
      "entities": ["股票市场", "AI", "用户"]
    }
  ]
}
```

### 统计数据

```json
{
  "bank_id": "hermes-agent",
  "period": "7d",
  "buckets": [
    {
      "time": "2026-05-02",
      "world": 1,
      "experience": 2,
      "observation": 2
    }
  ]
}
```

---

## 关键学习点

1. **端点格式**: 自托管部署使用完整 REST API 端点 `/v1/default/banks/{bank_id}/...`
2. **请求格式**: 必须用 `items` 数组包装内容
3. **超时设置**: LLM 处理需要时间，存储操作至少 60 秒
4. **Bank 创建**: 存储前必须先创建 Bank
5. **实体提取**: Hindsight 自动提取实体和关系

---

## 相关文件

- **Hook 脚本**: `~/.hermes/hooks/hindsight_integration.py`
- **修复报告**: `~/.hermes/hindsight-fix-report.md`
- **集成指南**: `~/.hermes/hindsight-integration-guide.md`

---

**修复完成时间**: 2026-05-02 12:40
**验证状态**: ✅ 所有测试通过
**生产就绪**: 🟢 可正常使用
