# Hindsight API 端点探索记录

**日期**: 2026-05-02  
**状态**: ⚠️ API 端点与文档不匹配

## 问题发现

在部署 Hindsight 后，尝试使用文档中描述的 API 端点进行会话历史导入，发现所有端点均返回 "Not Found"。

## 测试过的端点

### 记忆存储端点

| 端点 | 方法 | 状态 | 备注 |
|------|------|------|------|
| `/retain` | POST | ❌ Not Found | 官方文档推荐 |
| `/memories` | POST | ❌ Not Found | 常见 RESTful 端点 |
| `/api/memories` | POST | ❌ Not Found | 带 API 前缀 |
| `/v1/memories` | POST | ❌ Not Found | 带 API 版本 |

### 记忆检索端点

| 端点 | 方法 | 状态 | 备注 |
|------|------|------|------|
| `/recall` | POST | ❌ Not Found | 官方文档推荐 |
| `/search` | POST | ❌ Not Found | 常见检索端点 |
| `/api/search` | POST | ❌ Not Found | 带 API 前缀 |

### 健康检查端点

| 端点 | 方法 | 状态 | 备注 |
|------|------|------|------|
| `/health` | GET | ✅ 正常 | 返回 `{"status":"healthy","database":"connected"}` |
| `/docs` | GET | ✅ 正常 | Swagger UI |
| `/openapi.json` | GET | ✅ 正常 | OpenAPI 规范 |

## 会话历史导入失败

### 提取统计
- 会话文件: 107 个 JSONL 文件
- 时间跨度: 2026-04-15 至 2026-05-02
- 提取消息: 1,624 条对话
- 导入成功: 0 条（API 端点问题）

### 导入脚本

已创建导入脚本: `~/.hermes/scripts/import_sessions_to_hindsight.py`

但受限于 API 端点问题，无法自动导入。

## 替代方案

### 方案 A: 使用 Web UI（推荐）

1. 访问 http://localhost:9999
2. 创建 Bank（如 `hermes-agent-history`）
3. 手动添加关键记忆

**建议添加的关键信息**:
- 用户偏好: 使用中文，关注 AI 和股票投资
- 重要项目: 达尔文 Skills 整合（已完成）
- 工作配置: 4-5 月夜班（20:00-08:00）
- 记忆架构: 三层记忆系统（Hindsight + MemPalace + fact_store）

### 方案 B: 查看 API 文档

访问 http://localhost:8888/docs 通过 Swagger UI 探索正确的端点。

### 方案 C: 使用 LLM Wrapper

```python
from hindsight_client import Hindsight

client = Hindsight(base_url="http://localhost:8888")

# 自动记忆（无需关心具体端点）
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "记住：用户偏好使用中文"}
    ]
)
```

## 可能原因

1. **版本不匹配**: Hindsight 版本与文档版本不一致
2. **Bank 依赖**: 需要先创建 Bank 才能使用端点
3. **API 认证**: 可能需要 API Key 认证
4. **部署方式**: Docker 部署与云端部署端点不同

## 下一步行动

1. 通过 Web UI 熟悉功能
2. 查看 Swagger UI 文档确认正确端点
3. 尝试 LLM Wrapper 集成方式
4. 等待官方修复或更新文档

## 相关文档

- 部署报告: `~/.hermes/hindsight-deployment-complete.md`
- 导入报告: `~/.hermes/hindsight-import-report.md`
- 集成指南: `~/.hermes/hindsight-integration-guide.md`
