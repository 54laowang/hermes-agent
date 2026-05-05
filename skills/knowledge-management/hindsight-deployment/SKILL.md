---
name: hindsight-deployment
description: Hindsight 记忆系统自托管部署与集成 - Docker 部署、OpenRouter/API 配置、三层记忆架构设计、Hermes 集成。当用户需要部署 Hindsight、配置记忆系统、集成到 Hermes 时使用。
version: 1.0.0
triggers:
  - hindsight
  - 记忆系统
  - 自托管部署
  - docker 部署
  - 记忆架构
---

# Hindsight 记忆系统部署指南

## 概述

Hindsight 是一个强大的 AI Agent 记忆系统，专注于**对话学习和语义搜索**。本 Skill 涵盖从零到完整部署的全流程。

## 核心价值

- **自动学习**：从对话中自动提取和存储记忆
- **语义搜索**：基于向量相似度的记忆检索
- **三层架构**：与 MemPalace、fact_store 形成互补记忆系统
- **开源可控**：完全自托管，数据本地存储

## 快速开始

### 前置要求

- Docker Desktop（macOS/Windows/Linux）
- LLM API Key（OpenRouter/OpenAI/Anthropic/Gemini）
- Git

### 一键部署（推荐）

```bash
# 克隆仓库
git clone https://github.com/vectorize-io/hindsight.git ~/hindsight

# 配置 API Key
export OPENROUTER_API_KEY='your-key'

# 启动（OpenRouter 版）
~/hindsight/start-hindsight-openrouter.sh
```

### 访问地址

- **Web UI**: http://localhost:9999
- **API 文档**: http://localhost:8888/docs
- **健康检查**: http://localhost:8888/health

---

## 部署流程

### Phase 1: 环境准备

#### 1.1 Docker Desktop 安装

**macOS (Apple Silicon)**:
```bash
# 方案 A: Homebrew（需要密码授权）
brew install --cask docker

# 方案 B: 手动下载（推荐）
# 下载: https://desktop.docker.com/mac/main/arm64/Docker.dmg
# 双击 DMG → 拖到 Applications → 启动 Docker.app
```

**常见问题**：

**问题 1: 残留文件冲突**
```
Error: It seems there is already a Binary at '/usr/local/bin/hub-tool'
```

**解决方案**:
```bash
# 清理残留文件（需要 sudo）
sudo rm -f /usr/local/bin/hub-tool
sudo rm -f /usr/local/bin/docker*
sudo rm -f /usr/local/bin/docker-compose

# 重新安装
brew install --cask docker
```

**问题 2: Docker Desktop 未启动**
```bash
# 启动 Docker Desktop
open -a Docker

# 等待启动完成（30-60秒）
# 验证
docker info
```

#### 1.2 API Key 配置

**OpenRouter（推荐，免费额度）**:
```bash
# 获取 API Key
open https://openrouter.ai/keys

# 设置环境变量（临时）
export OPENROUTER_API_KEY='sk-or-v1-xxxxx'

# 永久生效（添加到 ~/.zshrc）
echo 'export OPENROUTER_API_KEY="sk-or-v1-xxxxx"' >> ~/.zshrc
source ~/.zshrc

# 添加到 Hermes 配置
echo "OPENROUTER_API_KEY=sk-or-v1-xxxxx" >> ~/.hermes/.env
```

**其他 LLM Provider**:
```bash
# OpenAI
export HINDSIGHT_API_LLM_PROVIDER=openai
export HINDSIGHT_API_LLM_API_KEY='sk-xxxxx'

# Anthropic
export HINDSIGHT_API_LLM_PROVIDER=anthropic
export HINDSIGHT_API_LLM_API_KEY='sk-ant-xxxxx'

# 本地 Ollama
export HINDSIGHT_API_LLM_PROVIDER=ollama
export HINDSIGHT_API_LLM_BASE_URL=http://localhost:11434/v1
```

---

### Phase 2: 部署 Hindsight

#### 2.1 克隆仓库

```bash
cd ~
git clone https://github.com/vectorize-io/hindsight.git
cd hindsight
```

#### 2.2 启动容器

**使用 OpenRouter（推荐）**:
```bash
docker run -d --pull always \
    -p 8888:8888 \
    -p 9999:9999 \
    --name hindsight \
    --restart unless-stopped \
    -e HINDSIGHT_API_LLM_PROVIDER=openai \
    -e HINDSIGHT_API_LLM_API_KEY=$OPENROUTER_API_KEY \
    -e HINDSIGHT_API_LLM_MODEL=openrouter/free \
    -e HINDSIGHT_API_LLM_BASE_URL=https://openrouter.ai/api/v1 \
    -v $HOME/.hindsight-docker:/home/hindsight/.pg0 \
    ghcr.io/vectorize-io/hindsight:latest
```

**使用本地配置文件**:
```bash
# 创建 .env
cp .env.example .env
# 编辑 .env 配置 API Key

# 启动
docker compose up -d
```

#### 2.3 验证部署

```bash
# 等待启动（10-15秒）
sleep 15

# 检查容器状态
docker ps | grep hindsight

# 测试 API
curl http://localhost:8888/health
# 期望: {"status":"healthy","database":"connected"}

# 访问 Web UI
open http://localhost:9999
```

---

### Phase 3: 三层记忆架构集成

#### 3.1 架构设计

```
┌─────────────────────────────────────────────────┐
│              Hermes Agent                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────────┐  ┌──────────────┐          │
│  │  Hindsight    │  │  MemPalace   │          │
│  │  (对话记忆)   │  │  (结构归档)  │          │
│  │  Layer 1      │  │  Layer 2     │          │
│  └───────────────┘  └──────────────┘          │
│        ↓                   ↓                   │
│   自动学习对话        项目文档归档            │
│   语义搜索检索        Wing/Room 导航          │
│                                                 │
│  ┌───────────────┐                            │
│  │  fact_store   │                            │
│  │  (实体图谱)   │                            │
│  │  Layer 3      │                            │
│  └───────────────┘                            │
│        ↓                                       │
│   实体关系推理                                │
│   信任评分系统                                │
└─────────────────────────────────────────────────┘
```

#### 3.2 分工说明

| 记忆层 | 核心能力 | 适用场景 | 存储方式 |
|--------|---------|---------|---------|
| **Hindsight** | 对话学习、语义搜索 | 用户偏好、错误模式 | 自动 |
| **MemPalace** | 结构化归档 | 项目文档、决策记录 | 手动 |
| **fact_store** | 实体关系图谱 | 长期事实、工具配置 | 自动/手动 |

#### 3.3 配置 Hermes 集成

**方式 1: 修改 config.yaml**
```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 5000
  user_char_limit: 2500
  provider: holographic  # 保留 fact_store
  
  # 添加 Hindsight 扩展
  extended_memory:
    hindsight:
      enabled: true
      api_url: http://localhost:8888
      collection: hermes-agent
```

**方式 2: 创建 Hook（高级）**

**⚠️ 已验证可用版本（2026-05-02）**

创建 `~/.hermes/hooks/hindsight_integration.py`:
```python
#!/usr/bin/env python3
"""Hindsight 集成 Hook（已验证版本）"""

import requests
from typing import Dict, Any, List

HINDSIGHT_API = 'http://localhost:8888'
BANK_ID = 'hermes-agent'

def hindsight_retain(content: str, bank_id: str = None) -> bool:
    """存储记忆到 Hindsight"""
    bank_id = bank_id or BANK_ID
    try:
        response = requests.post(
            f"{HINDSIGHT_API}/v1/default/banks/{bank_id}/memories",
            json={"items": [{"content": content}]},
            timeout=60  # LLM 处理需要时间
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[Hindsight] 存储失败: {e}")
        return False

def hindsight_recall(query: str, bank_id: str = None, limit: int = 5) -> List[Dict]:
    """从 Hindsight 检索相关记忆"""
    bank_id = bank_id or BANK_ID
    try:
        response = requests.post(
            f"{HINDSIGHT_API}/v1/default/banks/{bank_id}/memories/recall",
            json={"query": query, "max_tokens": 1000, "budget": "mid"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('results', [])
        return []
    except Exception as e:
        print(f"[Hindsight] 检索失败: {e}")
        return []

def should_store(message: str) -> bool:
    """判断是否应该存储"""
    keywords = ['记住', '记得', '保存', '重要', '以后', 'remember', 'save', 'important']
    return any(kw in message.lower() for kw in keywords)

def pre_llm_call(context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM 调用前的 Hook"""
    user_message = context.get('user_message', '')
    
    if len(user_message) > 10:
        memories = hindsight_recall(user_message, limit=3)
        
        if memories:
            formatted = []
            for m in memories[:3]:
                text = m.get('text', '')
                entities = m.get('entities', [])
                formatted.append(f"{text}" + (f" [实体: {', '.join(entities)}]" if entities else ""))
            
            memory_context = "\n[相关记忆]\n" + "\n".join(f"- {m[:200]}" for m in formatted)
            context['injected_context'] = {
                'hindsight_memories': memories,
                'formatted_context': memory_context
            }
    
    return context

def post_llm_call(context: Dict[str, Any]) -> Dict[str, Any]:
    """LLM 调用后的 Hook"""
    user_message = context.get('user_message', '')
    assistant_response = context.get('assistant_response', '')
    
    if should_store(user_message):
        hindsight_retain(f"User: {user_message}\nAssistant: {assistant_response}")
    
    return context
```

**关键修正点**:
- ✅ 使用正确的 API 端点 `/v1/default/banks/{bank_id}/memories`
- ✅ 请求格式为 `{"items": [{"content": ...}]}`
- ✅ 存储超时设置为 60 秒
- ✅ 检索返回结构化结果（包含实体信息）

**注册 Hook**（`~/.hermes/hooks/hooks.yaml`）:
```yaml
hooks:
  pre_llm_call:
    - hindsight_integration.pre_llm_call
    - supervisor-precheck.main
    
  post_llm_call:
    - hindsight_integration.post_llm_call
```

---

## 管理与维护

### 容器管理

```bash
# 启动
docker start hindsight

# 停止
docker stop hindsight

# 重启
docker restart hindsight

# 查看日志
docker logs hindsight

# 进入容器
docker exec -it hindsight bash

# 查看资源使用
docker stats hindsight
```

### 数据管理

```bash
# 备份数据
tar -czf hindsight-backup-$(date +%Y%m%d).tar.gz ~/.hindsight-docker

# 恢复数据
docker stop hindsight
tar -xzf hindsight-backup-YYYYMMDD.tar.gz -C ~/
docker start hindsight

# 查看数据大小
du -sh ~/.hindsight-docker
```

### ✅ 正确的 API 端点（已验证 2026-05-02）

**重要**: 官方 README 中的简化端点（`/retain`, `/recall`）**不适用于自托管部署**。正确的端点格式如下：

#### 核心 API 端点

| 操作 | 端点 | 方法 | 说明 |
|------|------|------|------|
| **创建 Bank** | `/v1/default/banks/{bank_id}` | PUT | 创建记忆库 |
| **存储记忆** | `/v1/default/banks/{bank_id}/memories` | POST | 批量存储记忆 |
| **检索记忆** | `/v1/default/banks/{bank_id}/memories/recall` | POST | 语义搜索 |
| **查看统计** | `/v1/default/banks/{bank_id}/stats/memories-timeseries` | GET | 记忆时间序列 |
| **列出 Banks** | `/v1/default/banks` | GET | 查看所有记忆库 |

#### 前置条件：创建 Bank

**在存储记忆前，必须先创建 Bank**：
```bash
curl -X PUT "http://localhost:8888/v1/default/banks/hermes-agent" \
  -H "Content-Type: application/json" \
  -d '{"mission":"Hermes Agent 对话记忆系统"}'
```

**返回示例**:
```json
{
  "bank_id": "hermes-agent",
  "name": "hermes-agent",
  "disposition": {
    "skepticism": 3,
    "literalism": 3,
    "empathy": 3
  },
  "mission": "Hermes Agent 对话记忆系统"
}
```

#### 存储记忆（正确格式）

**⚠️ 关键**: 请求体必须包含 `items` 数组，不是直接的 `content` 字段！

```bash
# ✅ 正确格式
curl -X POST "http://localhost:8888/v1/default/banks/hermes-agent/memories" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"content":"用户偏好使用中文，关注 AI 和股票市场"}]}'

# ❌ 错误格式（会返回 422 错误）
curl -X POST "http://localhost:8888/v1/default/banks/hermes-agent/memories" \
  -H "Content-Type: application/json" \
  -d '{"content":"用户偏好使用中文"}'  # 缺少 items 包装
```

**返回示例**:
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

**超时设置**: 存储操作需要 LLM 处理，建议超时 **60 秒**（不是 5 秒）。

#### 检索记忆（正确格式）

```bash
curl -X POST "http://localhost:8888/v1/default/banks/hermes-agent/memories/recall" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "用户偏好",
    "max_tokens": 1000,
    "budget": "mid"
  }'
```

**返回示例**:
```json
{
  "results": [
    {
      "id": "a69bdf28-5059-4de0-b0c2-b3aa193de8e3",
      "text": "用户偏好使用中文，关注 AI 和股票市场 | Involving: 用户",
      "type": "world",
      "entities": ["股票市场", "AI", "用户"],
      "mentioned_at": "2026-05-02T04:38:13.304639+00:00"
    }
  ],
  "entities": {
    "用户": {
      "entity_id": "bc5569d2-9668-48e4-ac63-a5f7e0c1902f",
      "canonical_name": "用户",
      "observations": []
    }
  }
}
```

#### 记忆类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| **world** | 世界事实 | "Alice 在 Google 工作" |
| **experience** | 个人经历 | "我尝试了新方法并失败了" |
| **observation** | 观察结论 | "用户偏好简洁回复" |

类型由 Hindsight **自动判断**，无需手动指定。

#### Python 集成示例（已验证）

```python
#!/usr/bin/env python3
import requests

HINDSIGHT_API = "http://localhost:8888"
BANK_ID = "hermes-agent"

def hindsight_retain(content: str) -> bool:
    """存储记忆到 Hindsight"""
    try:
        response = requests.post(
            f"{HINDSIGHT_API}/v1/default/banks/{BANK_ID}/memories",
            json={"items": [{"content": content}]},
            timeout=60  # ⚠️ 需要足够超时
        )
        return response.status_code == 200
    except Exception as e:
        print(f"存储失败: {e}")
        return False

def hindsight_recall(query: str) -> list:
    """从 Hindsight 检索相关记忆"""
    try:
        response = requests.post(
            f"{HINDSIGHT_API}/v1/default/banks/{BANK_ID}/memories/recall",
            json={"query": query, "max_tokens": 1000, "budget": "mid"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('results', [])
        return []
    except Exception as e:
        print(f"检索失败: {e}")
        return []

# 使用示例
hindsight_retain("用户偏好使用中文，关注 AI 和股票")
memories = hindsight_recall("用户偏好")
for m in memories:
    print(f"- {m['text']}")
```

#### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `{"detail":"Not Found"}` | API 端点错误 | 使用正确的端点格式 |
| `Field required: items` | 请求格式错误 | 添加 `items` 数组包装 |
| 存储超时 | 超时设置过短 | 增加到 60 秒 |
| Bank 不存在 | 未创建 Bank | 先调用 PUT 创建 Bank |

#### API 文档

- **Swagger UI**: http://localhost:8888/docs
- **OpenAPI JSON**: http://localhost:8888/openapi.json

**查看所有可用端点**:
```bash
curl -s http://localhost:8888/openapi.json | \
  python3 -c "import sys, json; data = json.load(sys.stdin); print('\n'.join(sorted(data['paths'].keys())))"
```

---

## 故障排查

### 问题 1: 容器无法启动

**症状**:
```bash
docker ps -a | grep hindsight
# 显示 Exited 状态
```

**解决方案**:
```bash
# 查看日志
docker logs hindsight

# 常见原因:
# 1. 端口被占用
lsof -i:8888
lsof -i:9999

# 2. API Key 未设置
echo $OPENROUTER_API_KEY

# 3. Docker 未运行
docker info
```

### 问题 2: API 无响应

**症状**:
```bash
curl http://localhost:8888/health
# 无响应或超时
```

**解决方案**:
```bash
# 等待服务完全启动（约 10-15 秒）
sleep 15

# 重启容器
docker restart hindsight

# 检查容器资源
docker stats hindsight
```

### 问题 4: API 端点返回 404

**症状**:
```bash
curl http://localhost:8888/retain
# {"detail":"Not Found"}
```

**原因**: 使用了错误的 API 端点

**解决方案**: 参考 [API 端点修正记录](references/api-endpoint-correction-2026-05-02.md)

**正确端点**:
- 存储: `/v1/default/banks/{bank_id}/memories`
- 检索: `/v1/default/banks/{bank_id}/memories/recall`

### 问题 5: 存储操作超时

**症状**:
```python
requests.exceptions.Timeout: HTTPConnectionPool(host='localhost', port=8888): Read timed out
```

**原因**: Hindsight 需要 LLM 处理记忆，默认 5 秒超时太短

**解决方案**: 增加超时到 60 秒
```python
response = requests.post(..., timeout=60)  # 不是 5 秒
```

### 问题 6: 请求格式错误

**症状**:
```json
{"detail":[{"type":"missing","loc":["body","items"],"msg":"Field required"}]}
```

**原因**: 请求体缺少 `items` 数组包装

**解决方案**:
```python
# ❌ 错误
json={"content": "记忆内容"}

# ✅ 正确
json={"items": [{"content": "记忆内容"}]}
```

---

## 最佳实践

### 1. 记忆存储策略

**存储什么**:
- ✅ 用户偏好和习惯
- ✅ 重要决策和理由
- ✅ 错误模式和解决方案
- ✅ 项目关键信息

**不存储什么**:
- ❌ 临时性信息
- ❌ 可从其他系统获取的数据
- ❌ 敏感信息（密码、密钥）

### 2. 记忆检索优化

```python
# 好的 Query
"用户对数据分析的偏好"  # 具体、明确
"上次项目的架构决策"    # 有上下文

# 不好的 Query
"用户"                  # 太泛
"项目"                  # 缺乏上下文
```

### 3. 三层记忆协同

```python
# 工作流示例
1. 用户提问 → Hindsight 检索对话记忆
2. 加载项目文档 → MemPalace 获取结构化知识
3. 验证事实 → fact_store 查询实体关系
4. 生成回答 → 融合三层信息
5. 归档重要信息 → 分发到合适的记忆层
```

---

## 参考资源

- **官方文档**: https://hindsight.vectorize.io
- **GitHub 仓库**: https://github.com/vectorize-io/hindsight
- **Paper**: https://arxiv.org/abs/2512.12818
- **Cookbook**: https://hindsight.vectorize.io/cookbook

---

## 附加资源

### 参考文档
- [Docker Desktop 安装故障排查](references/docker-installation-troubleshooting.md) - 残留文件清理、启动问题等
- [OpenRouter API Key 配置指南](references/openrouter-api-key-setup.md) - 获取、配置、安全最佳实践
- [API 端点探索记录](references/api-endpoint-discovery.md) - ⚠️ API 端点问题、会话导入失败、替代方案
- **[API 端点修正记录（2026-05-02）](references/api-endpoint-correction-2026-05-02.md)** - ✅ 正确端点、请求格式、超时设置、Python 示例

### 脚本工具
- [start-hindsight-openrouter.sh](scripts/start-hindsight-openrouter.sh) - 一键启动脚本
- [stop-hindsight.sh](scripts/stop-hindsight.sh) - 停止脚本

---

## 更新日志

### v1.1.0 (2026-05-02)
- **✅ API 端点修正**: 发现并文档化正确的 REST API 端点格式
- **✅ 请求格式修正**: 明确 `items` 数组包装要求
- **✅ 超时优化**: 存储操作超时从 5 秒增加到 60 秒
- **✅ Hook 示例更新**: 提供已验证可用的 Python Hook 代码
- **✅ 新增参考文档**: `api-endpoint-correction-2026-05-02.md`
- **✅ 故障排查增强**: 新增 API 404、超时、格式错误等问题的解决方案

### v1.0.0 (2026-05-02)
- 初始版本
- Docker Desktop 部署流程
- OpenRouter 集成配置
- 三层记忆架构设计
- Hermes 集成方案
