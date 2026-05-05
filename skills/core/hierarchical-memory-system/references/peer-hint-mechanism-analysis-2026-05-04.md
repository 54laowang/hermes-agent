# Peer Hint 机制深度分析 - 2026-05-04

## 概述

Peer Hint（同伴提示）是 Agent 间轻量级协作机制，让 Agent A 能"提示" Agent B 某些信息，而非直接控制。核心特点：非阻塞、异步、可选采纳。

**比喻**：像同事间的"友情提醒"，而非上司的"指令"。

## 三种主流实现路径

### 1️⃣ 共享状态模式（LangGraph 风格）

**核心思想**：所有 Agent 共享一个状态对象

**实现代码**：

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    messages: Annotated[list, "reducer"]  # 消息历史
    peer_hints: Annotated[dict, "reducer"]  # Agent 间提示

def reducer(left: dict, right: dict) -> dict:
    """合并多个 Agent 的提示"""
    return {**left, **right}

# Agent A 写入提示
state["peer_hints"]["agent_b"] = {
    "hint": "用户偏好简短回复",
    "confidence": 0.8,
    "timestamp": "2026-05-04T02:20:00"
}

# Agent B 读取提示
hint = state["peer_hints"].get("agent_a", {})
```

**优点**：
- ✅ 强一致性，所有 Agent 看到相同状态
- ✅ 适合流水线式任务（Agent A → B → C）

**缺点**：
- ❌ 需要中心化存储
- ❌ 扩展性受限（Agent 数量多时性能下降）

**适用场景**：
- 单 Gateway 多 Agent
- 流水线式任务
- 强一致性要求

### 2️⃣ 统一记忆模式（CrewAI 风格）

**核心思想**：多层记忆系统，Agent 自动共享

**实现代码**：

```python
from crewai import Agent, Task, Crew
from crewai.memory import LongTermMemory

# Agent 自动共享记忆
researcher = Agent(
    role="Researcher",
    memory=True,  # 启用记忆
    allow_delegation=True  # 允许委托任务
)

writer = Agent(
    role="Writer",
    memory=True,  # 共享同一记忆系统
)

# Agent A 的发现自动进入共享记忆
# Agent B 可通过语义检索获取
crew = Crew(
    agents=[researcher, writer],
    memory=True,  # 启用全局记忆
    process=Process.sequential
)

# Peer Hint 自动传递
# Researcher 完成研究后，Writer 能看到所有发现
```

**优点**：
- ✅ 长期记忆，跨会话持久化
- ✅ 语义检索，智能匹配相关提示

**缺点**：
- ❌ 需要向量数据库
- ❌ 成本较高（embedding 计算）

**适用场景**：
- 多 Gateway 多 Agent
- 长期协作任务
- 知识积累型应用

### 3️⃣ 消息传播模式（Gossip Protocol）

**核心思想**：去中心化传播

**实现代码**：

```python
import random
import asyncio

class GossipAgent:
    def __init__(self, agent_id: str, peers: list):
        self.id = agent_id
        self.peers = peers
        self.hints = {}  # 本地提示存储
    
    async def spread_hint(self, hint: dict, ttl: int = 3):
        """传播提示到随机选择的 peer"""
        if ttl <= 0:
            return
        
        # 随机选择 k 个 peer
        k = min(3, len(self.peers))
        selected = random.sample(self.peers, k)
        
        for peer in selected:
            await peer.receive_hint(hint, ttl - 1)
    
    async def receive_hint(self, hint: dict, ttl: int):
        """接收并传播提示"""
        hint_id = hint.get("id")
        
        # 去重：避免重复传播
        if hint_id in self.hints:
            return
        
        # 存储提示
        self.hints[hint_id] = hint
        
        # 继续传播
        await self.spread_hint(hint, ttl)
```

**优点**：
- ✅ 去中心化，无单点故障
- ✅ 动态 peer 发现
- ✅ 适合大规模分布式场景

**缺点**：
- ❌ 最终一致性（可能有延迟）
- ❌ 网络开销大

**适用场景**：
- 多 Gateway 分布式
- 大规模 Agent 网络
- 高可用性要求

## 新兴协议：A2A (Agent-to-Agent)

Google 2025 年提出的标准化协议。

**消息格式**：

```json
{
  "protocol": "a2a/1.0",
  "from": "agent_researcher_01",
  "to": "agent_writer_02",
  "type": "hint",
  "payload": {
    "hint": "用户偏好中文回复",
    "confidence": 0.85,
    "metadata": {
      "source": "user_interaction_history",
      "timestamp": "2026-05-04T02:20:00Z"
    }
  },
  "ttl": 300,
  "priority": 5
}
```

**核心特性**：
- ✅ 标准化消息格式
- ✅ 支持优先级和 TTL
- ✅ 可扩展的 metadata

## 值得学习的设计模式

### 1. 提示去重机制

```python
from pybloom_live import ScalableBloomFilter

class HintManager:
    def __init__(self):
        self.seen = ScalableBloomFilter()
    
    def is_duplicate(self, hint_id: str) -> bool:
        if hint_id in self.seen:
            return True
        self.seen.add(hint_id)
        return False
```

**效果**：内存节省 90%

### 2. 优先级队列

```python
import heapq

class PriorityHintQueue:
    def __init__(self):
        self.queue = []
    
    def add_hint(self, hint: dict, priority: int):
        """高优先级提示先处理"""
        heapq.heappush(self.queue, (-priority, hint))
    
    def get_next_hint(self):
        if self.queue:
            return heapq.heappop(self.queue)[1]
        return None
```

### 3. TTL 过期机制

```python
from datetime import datetime, timedelta

class TimeBasedHint:
    def __init__(self, content: str, ttl_seconds: int = 300):
        self.content = content
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at
```

### 4. 信任评分机制

```python
class TrustBasedHint:
    def __init__(self, content: str, source: str, confidence: float):
        self.content = content
        self.source = source
        self.confidence = confidence
        self.retrieval_count = 0
        self.helpful_count = 0
    
    def get_trust_score(self) -> float:
        """动态信任评分"""
        if self.retrieval_count == 0:
            return self.confidence
        
        accuracy = self.helpful_count / self.retrieval_count
        return 0.7 * self.confidence + 0.3 * accuracy
```

## 性能优化策略

| 策略 | 效果 | 实现难度 |
|------|------|---------|
| **本地缓存** | 减少 70% 网络请求 | ⭐ |
| **Bloom Filter 去重** | 内存节省 90% | ⭐⭐ |
| **分层传播** | 网络流量减少 60% | ⭐⭐⭐ |
| **压缩传输** | 带宽节省 50% | ⭐⭐ |

## 单 Gateway vs 多 Gateway

### 单 Gateway + 多 Agent

```
┌─────────────────────────────────┐
│      Gateway (单一入口)          │
└─────────────────────────────────┘
         ↓           ↓           ↓
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Agent A│  │ Agent B│  │ Agent C│
    └────────┘  └────────┘  └────────┘
         ↓           ↓           ↓
    ┌─────────────────────────────────┐
    │   共享 Peer Hint（内存）          │
    └─────────────────────────────────┘
```

**优点**：
- ✅ 部署简单
- ✅ Peer Hint 高效（内存共享）
- ✅ 调试方便
- ✅ 成本低

**缺点**：
- ❌ 单点故障
- ❌ 扩展性受限
- ❌ 隔离性差

**适用场景**：
- 个人使用 / 小团队（<10 人）
- Agent 数量较少（<20 个）
- 任务相对独立

### 多 Gateway + 多 Agent

```
┌──────────────┐     ┌──────────────┐
│  Gateway A   │     │  Gateway B   │
└──────────────┘     └──────────────┘
      ↓       ↓             ↓       ↓
  ┌─────┐  ┌─────┐     ┌─────┐  ┌─────┐
  │Agent│  │Agent│     │Agent│  │Agent│
  │ A1  │  │ A2  │     │ B1  │  │ B2  │
  └─────┘  └─────┘     └─────┘  └─────┘
      ↓           ↓             ↓
  ┌──────────────────────────────────┐
  │   分布式 Peer Hint（Redis/MQ）     │
  └──────────────────────────────────┘
```

**优点**：
- ✅ 高可用
- ✅ 水平扩展
- ✅ 隔离性强
- ✅ 灵活部署

**缺点**：
- ❌ 运维复杂
- ❌ Peer Hint 跨进程（需要 Redis）
- ❌ 成本高

**适用场景**：
- 多租户 SaaS 平台
- Agent 数量多（>20 个）
- 不同业务域隔离要求高

## 与 Hermes 集成建议

### 基于现有架构的实现

```python
# ~/.hermes/core/peer_hint.py

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class PeerHint:
    """Agent 间提示"""
    from_agent: str
    to_agent: str
    hint_type: str  # "preference", "context", "warning"
    content: str
    confidence: float = 0.8
    ttl: int = 300  # 5 分钟过期
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_json(self) -> str:
        return json.dumps({
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.hint_type,
            "content": self.content,
            "confidence": self.confidence,
            "ttl": self.ttl,
            "created_at": self.created_at.isoformat()
        })


class PeerHintManager:
    """Peer Hint 管理器"""
    
    def __init__(self, storage_backend: str = "sqlite"):
        self.hints: Dict[str, PeerHint] = {}
        self.storage_backend = storage_backend
    
    def send_hint(self, hint: PeerHint):
        """发送提示"""
        hint_id = f"{hint.from_agent}_{hint.created_at.timestamp()}"
        self.hints[hint_id] = hint
        
        # 持久化到数据库
        self._persist_hint(hint)
        
        # 如果是实时模式，推送消息
        self._push_to_recipient(hint)
    
    def get_hints_for_agent(self, agent_id: str) -> list:
        """获取给某 Agent 的所有有效提示"""
        now = datetime.now()
        valid_hints = []
        
        for hint_id, hint in self.hints.items():
            # 检查是否过期
            if (now - hint.created_at).seconds > hint.ttl:
                continue
            
            # 检查是否是给该 Agent 的
            if hint.to_agent == agent_id or hint.to_agent == "*":
                valid_hints.append(hint)
        
        return valid_hints
    
    def _persist_hint(self, hint: PeerHint):
        """持久化提示"""
        # TODO: 存储到 SQLite 或 Redis
        pass
    
    def _push_to_recipient(self, hint: PeerHint):
        """实时推送提示"""
        # TODO: 通过 WebSocket 或消息队列推送
        pass
```

### 与 fact_store 集成

```python
# 事实提取到 fact_store
fact_store(
    action="add",
    content=f"Agent {from_agent} 提示：{hint.content}",
    entity=to_agent,
    category="peer_hint",
    tags=f"hint,{hint_type}"
)

# 查询相关提示
hints = fact_store(
    action="probe",
    entity=agent_id
)
```

## 应用场景

### 场景1：跨 Agent 偏好传递

```python
# Agent A（财经分析）发现用户偏好
hint = PeerHint(
    from_agent="finance_analyst",
    to_agent="*",  # 广播给所有 Agent
    hint_type="preference",
    content="用户偏好简洁的中文回复",
    confidence=0.9
)

# Agent B（科技新闻）自动收到提示
# 调整回复风格
```

### 场景2：上下文共享

```python
# Agent A（数据采集）完成工作
hint = PeerHint(
    from_agent="data_collector",
    to_agent="data_analyst",
    hint_type="context",
    content="已获取 A 股 2026-05-04 收盘数据",
    confidence=1.0
)

# Agent B（数据分析）收到提示
# 避免重复获取数据
```

### 场景3：风险警告

```python
# Agent A 检测到异常
hint = PeerHint(
    from_agent="risk_monitor",
    to_agent="*",
    hint_type="warning",
    content="检测到 API 限流，建议降级",
    confidence=0.85,
    ttl=60  # 1 分钟有效
)

# 其他 Agent 收到警告
# 自动切换到降级模式
```

## 总结

Peer Hint 机制的核心价值：

**1. 提升协作效率**
- Agent 间无需重复沟通
- 直接传递关键信息

**2. 降低 Token 消耗**
- 避免重复查询
- 避免上下文膨胀

**3. 增强可扩展性**
- 新 Agent 加入后能快速获取必要上下文
- 动态发现和协作

**实现建议**：

| 场景 | 推荐方案 | 存储后端 |
|------|---------|---------|
| 单 Gateway | 共享状态 | 内存/SQLite |
| 多 Gateway | 统一记忆 | Redis/MemPalace |
| 分布式 | Gossip Protocol | Redis Pub/Sub |

**Hermes 最佳实践**：
- ✅ 结合 fact_store（结构化存储）
- ✅ 结合 MemPalace（语义检索）
- ✅ 结合 L5 Context Memory（任务追踪）
- ✅ 支持信任评分（质量过滤）
