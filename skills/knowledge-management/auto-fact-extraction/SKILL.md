---
name: Auto Fact Extraction
description: Hermes 双层自动事实提取系统 - 结合 Shell Hooks + fact_store 实现跨会话持久化记忆，彻底解决上下文压缩导致的信息丢失问题
category: knowledge-management
---

# 双层自动事实提取系统

## 🎯 核心问题

Hermes 对话经常因上下文压缩（context compaction）丢失早期会话的关键信息，导致：
- 用户需求被遗忘
- 项目进度需要重复确认
- 技术决策无法追溯

## 💡 解决方案：双层记忆架构

```
┌─────────────────────────────────────────────────┐
│  Layer 1: 助手主动提取 (智能结构化)            │
│  - 识别用户偏好、决策记录、项目里程碑            │
│  - 分类存储: user_pref / project / tool / general│
│  - 标签系统 + 信任分机制                        │
└───────────────────────┬─────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────┐
│  Layer 2: Shell Hook 自动提取 (静默兜底)         │
│  - post_llm_call 事件触发                       │
│  - 每次 LLM 响应后自动执行                      │
│  - 记录对话元数据（时间戳、会话ID、平台等）     │
└─────────────────────────────────────────────────┘
```

---

## 📋 实施步骤

### Step 1: 配置 Shell Hook

创建文件 `~/.hermes/agent-hooks/auto-fact-extract.py`:

```python
#!/usr/bin/env python3
"""
Hermes Shell Hook - post_llm_call 事件触发
自动提取对话中的关键事实并持久化
"""
import json
import os
import sys
from datetime import datetime

LOG_FILE = os.path.expanduser("~/.hermes/logs/auto-facts.log")

def main():
    # 确保日志目录存在
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # 读取 Hermes 传入的环境变量
    event_data = {
        "timestamp": datetime.now().isoformat(),
        "session_id": os.environ.get("HERMES_SESSION_ID", "unknown"),
        "platform": os.environ.get("HERMES_PLATFORM", "unknown"),
        "model": os.environ.get("HERMES_MODEL", "unknown"),
        "prompt_length": os.environ.get("HERMES_PROMPT_LENGTH", "0"),
        "response_length": os.environ.get("HERMES_RESPONSE_LENGTH", "0"),
        "event": os.environ.get("HERMES_HOOK_EVENT", "unknown"),
    }
    
    # 追加日志
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event_data, ensure_ascii=False) + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

设置可执行权限:
```bash
chmod +x ~/.hermes/agent-hooks/auto-fact-extract.py
```

### Step 2: 配置 Hermes Hooks

更新 `~/.hermes/config.yaml`:

```yaml
hooks:
  enabled: true
  shell_hooks:
    post_llm_call:
      - path: ~/.hermes/agent-hooks/auto-fact-extract.py
        timeout: 10  # 避免阻塞会话流程
```

### Step 3: 验证配置

```bash
# 列出所有钩子
hermes hooks list

# 测试钩子
hermes hooks test post_llm_call
```

---

## 🛠️ fact_store 使用规范

### 四大分类标准

| Category | 使用场景 | 示例 |
|----------|----------|------|
| `user_pref` | 用户偏好、习惯、禁忌 | 偏好中文回复、不喜欢过长输出 |
| `project` | 项目相关、进度、决策 | 正在开发 NPC 分支自动提取功能 |
| `tool` | 工具知识、配置信息 | fact_store 支持 4 种分类 |
| `general` | 通用信息、时间戳 | 当前时间 2026年4月27日 |

### 最佳实践

1. **及时添加**: 发现关键信息立即保存，不要等上下文丢失
2. **精准分类**: 正确选择 category 提升后续召回率
3. **丰富标签**: 使用逗号分隔的多标签系统 `tags: "npc,memory,hermes"`
4. **反馈校准**: 调用后标记 `fact_feedback(action="helpful")` 提升信任分
5. **定期更新**: 信息变更时使用 `action="update"` 保持时效性

---

## ⚡ 常用命令速查

```bash
# 添加事实
fact_store action=add category=user_pref content="..." tags="..."

# 搜索事实
fact_store action=search query="关键词"

# 列出所有事实
fact_store action=list limit=10

# 实体探测（召回所有相关事实）
fact_store action=probe entity="NPC"

# 更新事实
fact_store action=update fact_id=1 content="..."

# 标记有用（提升信任分）
fact_feedback action=helpful fact_id=1
```

---

## 🧠 智能提取触发点

助手应当主动调用 fact_store 的场景：

1. ✅ 用户表达明确偏好（语言、风格、工具选择）
2. ✅ 做出重要技术决策（架构选型、方案取舍）
3. ✅ 项目里程碑达成（功能完成、Bug 修复）
4. ✅ 发现工具/环境的特殊行为
5. ✅ 重复出现的模式或需求

---

## 📊 信任分机制

- 新事实默认信任分: **0.5**
- 标记 `helpful`: **+0.05**
- 标记 `unhelpful`: **-0.05**
- 检索时自动按信任分排序

高信任分的事实会优先被召回，形成正反馈循环。

---

## ⚠️ 注意事项

1. **不要过度保存**: 只保存真正跨会话有价值的信息
2. **避免重复**: 添加前先搜索确认，同一事实不要多次存储
3. **简洁明了**: 内容控制在 1-2 句话，便于检索和理解
4. **去敏感化**: 不要保存 API Key、密码等敏感信息

---

## 🔄 与其他记忆系统对比

| 机制 | 持久性 | 结构化 | 自动化 | 上下文占用 |
|------|--------|--------|--------|------------|
| memory tool | ✅ 永久 | ❌ 无结构 | ❌ 手动 | ✅ 低 |
| session_search | ✅ 永久 | ❌ 全文搜索 | ❌ 手动 | ❌ 高 |
| **fact_store** | ✅ 永久 | ✅ 分类+标签+信任分 | ⚡ 半自动 | ✅ 极低 |
| MemPalace | ✅ 永久 | ✅ 知识图谱 | ❌ 手动 | ✅ 低 |

---

**设计哲学**: 记忆不是存储越多越好，而是在正确的时间能召回正确的信息。
