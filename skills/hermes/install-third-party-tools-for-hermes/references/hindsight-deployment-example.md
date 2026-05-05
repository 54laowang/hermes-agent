# Hindsight 记忆系统集成案例

**日期**：2026-05-02  
**状态**：部署准备完成，待 Docker 安装后启动  
**仓库**：vectorize-io/hindsight  
**Stars**：高星项目，LongMemEval benchmark 第一

## 一、项目概述

### 核心能力

Hindsight 是一个 AI Agent 记忆系统，专注于**让 Agent 学习，而不仅仅是记忆**：

- **自动学习对话模式**：无需手动归档
- **语义搜索**：基于向量检索相关记忆
- **时间线记忆**：支持时间窗口查询
- **高性能**：LongMemEval benchmark 第一名

### 与现有记忆系统对比

| 特性 | Hindsight | MemPalace | fact_store |
|------|-----------|-----------|------------|
| 核心能力 | 对话学习 | 结构化归档 | 实体关系 |
| 记忆类型 | 语义记忆 | 情景记忆 | 语义+关系 |
| 存储方式 | 自动 | 手动 | 自动/手动 |
| 检索方式 | 语义搜索 | Wing/Room | 实体查询 |
| 适用场景 | 偏好学习 | 项目文档 | 事实管理 |

**结论**：三层互补，不冲突！

## 二、部署准备

### 环境要求

- **Docker Desktop**：必需（容器化部署）
- **OpenRouter API Key**：用于 LLM 调用
- **端口**：8888（API）、9999（UI）

### 准备状态（2026-05-02）

| 组件 | 状态 | 说明 |
|------|------|------|
| Docker Desktop | ❌ 未安装 | 需手动安装 |
| OPENROUTER_API_KEY | ❌ 未设置 | 需配置环境变量 |
| Hindsight 仓库 | ✅ 已克隆 | ~/hindsight/ |
| 部署脚本 | ✅ 已创建 | 3 个脚本 |
| 集成文档 | ✅ 已创建 | 完整指南 |

## 三、部署流程

### Step 1: 安装 Docker Desktop

```bash
# 下载链接（Apple Silicon）
open https://desktop.docker.com/mac/main/arm64/Docker.dmg

# 或使用 Homebrew（需授权）
brew install --cask docker

# 验证安装
docker --version
docker ps
```

### Step 2: 配置 OpenRouter API Key

```bash
# 获取 API Key
open https://openrouter.ai/keys

# 设置环境变量（临时）
export OPENROUTER_API_KEY='your-key-here'

# 添加到 ~/.zshrc（永久）
echo 'export OPENROUTER_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc

# 验证
echo $OPENROUTER_API_KEY
```

### Step 3: 启动 Hindsight

```bash
# 使用 OpenRouter 启动脚本
~/hindsight/start-hindsight-openrouter.sh

# 或手动启动
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

### Step 4: 验证启动

```bash
# 检查容器状态
docker ps | grep hindsight

# 访问 UI
open http://localhost:9999

# 测试 API
curl http://localhost:8888/v1/health

# 查看日志
docker logs hindsight
```

## 四、Hermes 集成

### 4.1 安装 Python Client

```bash
pip install hindsight-client -U
```

### 4.2 配置 Hermes

编辑 `~/.hermes/config.yaml`：

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 5000
  user_char_limit: 2500
  
  # 主 Provider: holographic (fact_store)
  provider: holographic
  
  # 扩展记忆系统
  extended_memory:
    hindsight:
      enabled: true
      api_url: http://localhost:8888
      auto_store: true           # 自动存储对话
      auto_retrieve: true        # 自动检索相关记忆
      collection: "hermes-agent" # 集合名称
```

### 4.3 创建集成 Hook

创建 `~/.hermes/hooks/hindsight_integration.py`：

```python
#!/usr/bin/env python3
"""
Hindsight 集成 Hook
- 自动存储重要对话到 Hindsight
- 在会话开始时检索相关记忆
- 与 MemPalace 和 fact_store 协同工作
"""

import os
import requests
from datetime import datetime

HINDSIGHT_API = os.getenv('HINDSIGHT_API_URL', 'http://localhost:8888')
COLLECTION = 'hermes-agent'

def store_memory(content: str, metadata: dict = None):
    """存储记忆到 Hindsight"""
    try:
        response = requests.post(
            f"{HINDSIGHT_API}/v1/memories",
            json={
                'content': content,
                'collection': COLLECTION,
                'metadata': metadata or {}
            }
        )
        return response.json()
    except Exception as e:
        print(f"Hindsight 存储失败: {e}")
        return None

def retrieve_memories(query: str, limit: int = 5):
    """从 Hindsight 检索相关记忆"""
    try:
        response = requests.post(
            f"{HINDSIGHT_API}/v1/search",
            json={
                'query': query,
                'collection': COLLECTION,
                'limit': limit
            }
        )
        return response.json().get('memories', [])
    except Exception as e:
        print(f"Hindsight 检索失败: {e}")
        return []

def should_store(message: str) -> bool:
    """判断是否应该存储到 Hindsight"""
    keywords = [
        '记住', '记得', '保存', '重要', '以后',
        'remember', 'save', 'important', 'note'
    ]
    return any(kw in message.lower() for kw in keywords)

# Hook 函数
def pre_llm_call(context: dict) -> dict:
    """LLM 调用前的 Hook"""
    user_message = context.get('user_message', '')
    
    # 检索相关记忆
    if len(user_message) > 10:
        memories = retrieve_memories(user_message)
        if memories:
            context['injected_context'] = {
                'hindsight_memories': memories,
                'source': 'hindsight_integration_hook'
            }
    
    return context

def post_llm_call(context: dict) -> dict:
    """LLM 调用后的 Hook"""
    user_message = context.get('user_message', '')
    assistant_response = context.get('assistant_response', '')
    
    # 存储重要对话
    if should_store(user_message):
        store_memory(
            content=f"User: {user_message}\nAssistant: {assistant_response}",
            metadata={
                'timestamp': datetime.now().isoformat(),
                'type': 'important_conversation'
            }
        )
    
    return context
```

### 4.4 注册 Hook

编辑 `~/.hermes/hooks/hooks.yaml`：

```yaml
hooks:
  pre_llm_call:
    - hindsight_integration.pre_llm_call
    - supervisor-precheck.main  # 保留监察者模式
    
  post_llm_call:
    - hindsight_integration.post_llm_call
```

## 五、测试验证

### 5.1 测试 Hindsight API

```bash
# 存储测试记忆
curl -X POST http://localhost:8888/v1/memories \
  -H "Content-Type: application/json" \
  -d '{
    "content": "用户偏好使用中文，关注 AI 和股票",
    "collection": "hermes-agent"
  }'

# 检索记忆
curl -X POST http://localhost:8888/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "用户偏好",
    "collection": "hermes-agent"
  }'
```

### 5.2 测试三层记忆系统

**Hindsight（对话记忆）**：
```
用户: 我喜欢用中文回复，重点关注 AI 和股票
Hindsight: 自动学习并记住这个偏好
下次对话: 自动注入偏好上下文
```

**MemPalace（结构化存储）**：
```
用户: 把达尔文整合计划归档
MemPalace: 存储到 wing:stock-skills, room:darwin-evolution
下次查询: 通过 Wing/Room 导航检索
```

**fact_store（实体图谱）**：
```
用户: 我的 OpenRouter API Key 是 xxx
fact_store: 提取实体 OPENROUTER_API_KEY，关联到 user
下次验证: 查询实体是否存在
```

## 六、管理命令

### 容器管理

```bash
# 启动
~/hindsight/start-hindsight-openrouter.sh

# 停止
~/hindsight/stop-hindsight.sh

# 查看日志
docker logs hindsight

# 重启
docker restart hindsight

# 查看状态
docker ps | grep hindsight

# 进入容器
docker exec -it hindsight bash
```

### 数据管理

```bash
# 备份数据
tar -czf hindsight-backup-$(date +%Y%m%d).tar.gz ~/.hindsight-docker

# 查看统计
curl http://localhost:8888/v1/stats

# 清理旧记忆（30天前）
curl -X DELETE "http://localhost:8888/v1/memories?older_than=30d"
```

## 七、故障排查

### 问题 1: Docker 未安装

```bash
# 检查
docker --version

# 安装
open https://desktop.docker.com/mac/main/arm64/Docker.dmg
```

### 问题 2: 端口被占用

```bash
# 检查端口
lsof -i:8888
lsof -i:9999

# 停止占用进程或修改脚本中的端口映射
```

### 问题 3: API Key 未设置

```bash
# 检查
echo $OPENROUTER_API_KEY

# 设置
export OPENROUTER_API_KEY='your-key'
```

### 问题 4: 容器启动失败

```bash
# 查看日志
docker logs hindsight

# 重启 Docker Desktop
# 清理容器: docker rm -f hindsight
# 重新启动
```

### 问题 5: Hermes 集成失败

```bash
# 检查 Hook
hermes hooks list

# 检查配置
cat ~/.hermes/config.yaml | grep -A 10 "memory:"

# 测试 Hindsight API
curl http://localhost:8888/v1/health
```

## 八、关键经验总结

### 1. OpenRouter 兼容性

**问题**：Hindsight 官方文档只提到 OpenAI API

**解决方案**：
- Hindsight 使用标准 OpenAI API 格式
- OpenRouter 兼容 OpenAI API
- 只需设置正确的 `BASE_URL` 和 `MODEL`

**配置要点**：
```bash
HINDSIGHT_API_LLM_PROVIDER=openai
HINDSIGHT_API_LLM_API_KEY=$OPENROUTER_API_KEY
HINDSIGHT_API_LLM_MODEL=openrouter/free
HINDSIGHT_API_LLM_BASE_URL=https://openrouter.ai/api/v1
```

### 2. 数据持久化

**问题**：容器重启后数据丢失

**解决方案**：
```bash
-v $HOME/.hindsight-docker:/home/hindsight/.pg0
```

**备份策略**：
- 定期备份 `~/.hindsight-docker` 目录
- 使用 `tar -czf` 压缩归档

### 3. 自动重启

**问题**：系统重启后服务未自动启动

**解决方案**：
```bash
--restart unless-stopped
```

**优点**：
- 系统重启后自动启动
- 容器崩溃后自动重启
- 手动停止后不会自动重启

### 4. 三层记忆协同

**架构设计**：
```
用户输入
    ↓
【Hindsight】检索相关对话记忆
    ↓
【MemPalace】提供项目上下文
    ↓
【fact_store】验证实体事实
    ↓
LLM 生成回复
    ↓
【Hindsight】自动存储重要对话
【MemPalace】归档重要决策
【fact_store】提取新实体关系
```

**分工原则**：
- Hindsight：对话式、自动学习、短期记忆
- MemPalace：文档式、手动归档、长期存储
- fact_store：实体式、自动提取、关系图谱

### 5. 环境变量管理

**最佳实践**：
1. 敏感信息使用环境变量
2. 永久配置写入 `~/.zshrc`
3. 部署脚本检查环境变量是否存在
4. 提供友好的错误提示

## 九、文件清单

### 部署脚本

| 文件 | 路径 | 用途 |
|------|------|------|
| deploy-hindsight.sh | ~/hindsight/ | 通用部署脚本 |
| start-hindsight-openrouter.sh | ~/hindsight/ | OpenRouter 专用启动 |
| stop-hindsight.sh | ~/hindsight/ | 停止脚本 |

### 文档

| 文件 | 路径 | 用途 |
|------|------|------|
| hindsight-integration-guide.md | ~/.hermes/ | 完整集成指南 |
| hindsight-deployment-checklist.md | ~/.hermes/ | 部署清单 |

### 数据目录

| 目录 | 路径 | 用途 |
|------|------|------|
| hindsight-docker | ~/.hindsight-docker/ | Hindsight 数据存储 |
| hindsight | ~/hindsight/ | Hindsight 仓库 |

## 十、下一步优化

1. **智能路由**：根据查询类型选择记忆层
2. **定期归档**：将 Hindsight 短期记忆归档到 MemPalace
3. **冲突解决**：三层记忆数据不一致时的优先级策略
4. **性能优化**：缓存常用记忆，减少 API 调用
5. **可视化**：创建记忆系统 Dashboard

---

**参考链接**：
- [Hindsight 官网](https://hindsight.vectorize.io)
- [Hindsight GitHub](https://github.com/vectorize-io/hindsight)
- [OpenRouter](https://openrouter.ai)
- [LongMemEval Benchmark](https://arxiv.org/abs/2512.12818)
