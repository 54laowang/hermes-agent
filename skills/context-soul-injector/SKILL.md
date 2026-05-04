---
name: context-soul-injector
version: 2.0.0
description: |
  给 Agent 注入灵魂：时间感知 + 持续搜索上下文 + 对话状态感知
  通过 Hermes Shell Hook 自动注入，让 Agent 真正"活在时间里"。
category: core
author: hermes
triggers:
  - 对话开始
  - 时间相关查询
  - 上下文检索
dependencies:
  - ~/.hermes/hooks/time-sense-injector.py
  - ~/.hermes/search.md
  - ~/.hermes/config.yaml
---

# 灵魂注入器 - Context Soul Injector

## 概述

本 Skill 通过三阶段工作流，为 Agent 注入时间感知、上下文记忆和对话状态感知能力。

---

## 工作流程（三阶段）

### Phase 0: 环境预检 ⚙️

**目标**: 确认所有依赖就绪，避免运行时错误。

**检查清单**:

| 检查项 | 路径 | 失败处理 |
|--------|------|----------|
| Hook 脚本存在 | `~/.hermes/hooks/time-sense-injector.py` | 执行安装流程 |
| 配置文件存在 | `~/.hermes/config.yaml` | 创建默认配置 |
| Hook 已注册 | `config.yaml` 中 `hooks.pre_llm_call` | 添加注册项 |
| 搜索归档存在 | `~/.hermes/search.md` | 创建空文件 |

**执行命令**:
```bash
# 一键预检
test -f ~/.hermes/hooks/time-sense-injector.py && \
test -f ~/.hermes/config.yaml && \
test -f ~/.hermes/search.md && \
echo "✅ 环境预检通过" || echo "❌ 缺少依赖，执行安装"
```

**异常处理**:
- 如果 hook 脚本缺失 → 提示用户运行 `hermes skills install context-soul-injector`
- 如果配置损坏 → 备份后重新生成默认配置
- 如果权限不足 → 提示执行 `chmod +x ~/.hermes/hooks/*.py`

---

### Phase 1: 时间感知注入 🕐

**触发时机**: 每次 LLM 调用前（通过 `pre_llm_call` hook 自动执行）

**注入内容**:

```yaml
时间上下文:
  - 当前精确时间: YYYY-MM-DD HH:MM:SS
  - 星期: 星期X
  - 时间段: 清晨/上午/中午/下午/晚上/深夜
  - 周末标识: 是/否

行为准则:
  凌晨(00:00-05:00):
    - 主动提醒用户注意休息
    - 避免发起复杂任务
  深夜(22:00-24:00):
    - 询问是否继续工作
    - 提供简化建议
  周末:
    - 理解用户可能不想聊严肃工作
    - 优先轻松话题（除非用户明确要求）
  长时间间隔:
    - 自然地"重新接上话题"
    - 简要回顾上次对话要点
```

**验证方式**:
```bash
# 测试时间感知是否生效
# 在对话中询问"现在几点"，Agent 应返回精确时间
```

**检查点**: 
- ✅ 用户确认时间显示正确
- ✅ Agent 表现出符合时间段的行为（如深夜提醒休息）

---

### Phase 2: 持续搜索上下文 🔍

**目标**: 避免重复搜索，保持信息连续性。

**文件位置**: `~/.hermes/search.md`

**写入规则**:

```markdown
## YYYY-MM-DD

### HH:MM - [搜索主题]
- 关键发现 1
- 关键发现 2
- 来源：[媒体名]（P0/P1/P2/P3）
- 链接：[URL]

---
```

**读取规则**:
1. 新搜索前，先在 `search.md` 中检索相关关键词
2. 如果已存在且时间戳 < 7 天，直接复用
3. 如果已存在但时间戳 > 7 天，标记"需更新"

**维护策略**:

| 时间范围 | 操作 |
|----------|------|
| 0-7 天 | 保留完整内容 |
| 7-30 天 | 自动摘要为 3-5 条要点 |
| > 30 天 | 归档到 `search.archive.md` 或删除 |

**检查点**:
- ✅ 用户确认搜索结果已归档
- ✅ 用户确认没有重复搜索

---

### Phase 3: 跨会话话题追踪 💬

**目标**: 解决跨平台/跨会话上下文断裂问题

**触发时机**: 每次 LLM 调用前（与时间感知同步注入）

**实现方式**: 从 `~/.hermes/sessions/*.jsonl` 文件提取最近会话

**注入内容示例**:

```
【近期对话话题】（跨会话上下文）
05-03 16:59 [企业微信]: da55f264...
05-03 10:41 [飞书]: ffe74ca7...
05-03 10:17 未知: 327ccd26...

⚠️ 如果用户提起之前聊过的话题，用 session_search 搜索历史会话
```

**平台识别规则**:

| 文件内容特征 | 平台标注 |
|-------------|---------|
| `"source": "wecom"` | [企业微信] |
| `"source": "feishu"` | [飞书] |
| `"source": "weixin"` | [微信] |
| `"source": "telegram"` | [Telegram] |
| `"source": "yuanbao"` | [元宝] |
| `"source": "cli"` | [CLI] |

**文件名解析格式**: `YYYYMMDD_HHMMSS_<session_id>.jsonl`

**检查点**:
- ✅ 用户提起之前话题时，Agent 能识别需要搜索历史会话
- ✅ 跨平台对话时，Agent 显示平台来源

---

## 异常处理手册

### 错误 1: Hook 未触发

**症状**: Agent 没有时间感知，回答"我不知道现在几点"

**诊断**:
```bash
# 检查 hook 是否注册
grep -A 5 "pre_llm_call" ~/.hermes/config.yaml
```

**解决**:
```yaml
# 在 config.yaml 中添加
hooks:
  pre_llm_call:
    - ~/.hermes/hooks/time-sense-injector.py
```

---

### 错误 2: 搜索归档损坏

**症状**: `search.md` 格式混乱，无法解析

**解决**:
```bash
# 备份损坏文件
cp ~/.hermes/search.md ~/.hermes/search.md.bak

# 创建新的归档文件
cat > ~/.hermes/search.md << 'EOF'
# 搜索归档

> 记录重要搜索结果，避免重复劳动

---
EOF
```

---

### 错误 3: 时间注入延迟

**症状**: 时间信息显示为几秒前，而非当前

**原因**: Hook 执行耗时过长

**解决**: 
- 优化 hook 脚本，避免复杂计算
- 使用缓存机制（TTL 60 秒）

---

## 测试验证

### 功能测试清单

| 测试项 | 验证方法 | 预期结果 |
|--------|----------|----------|
| 时间注入 | 问"现在几点" | 返回精确时间 + 星期 + 时间段 |
| 周末感知 | 周末对话 | Agent 表现轻松，不主动推工作 |
| 深夜提醒 | 23:00 后对话 | Agent 提醒休息 |
| 搜索归档 | 执行 web_search | 结果自动追加到 search.md |
| 搜索复用 | 重复搜索相同主题 | Agent 提示"已在 X 天前搜索过" |

---

## 配置参考

**config.yaml 示例**:
```yaml
hooks:
  pre_llm_call:
    - ~/.hermes/hooks/time-sense-injector.py

context_soul:
  time_sense:
    enabled: true
    timezone: "Asia/Shanghai"
  search_archive:
    enabled: true
    max_age_days: 30
    auto_summary: true
```

---

## 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 时间感知注入 | ✅ 完成 | 每轮对话前自动注入当前时间、市场状态 |
| 搜索记忆归档 | ✅ 完成 | 从 `search.md` 读取近期搜索 |
| 跨会话话题追踪 | ✅ 完成 | 从 `.jsonl` 会话文件提取近期对话（2026-05-03 新增） |

---

## 下一步规划

| 优先级 | 功能 | 预估工作量 |
|--------|------|-----------|
| 🟢 中 | 自动过期策略（7 天以上自动摘要） | 半天 |
| 🟢 中 | 话题摘要提取（从 session summary 而非 session_id） | 半天 |

---

## 重要技术发现

### Hermes 会话存储机制

**错误假设**: 会话存储在 SQLite 数据库 (`sessions.db`)

**实际机制**: 会话存储在 `.jsonl` 文件中

```
~/.hermes/sessions/
├── 20260503_165919_da55f264.jsonl  ← 企业微信会话
├── 20260503_104113_ffe74ca7.jsonl  ← 飞书会话
└── sessions.db                      ← 空文件（0 字节）
```

**文件命名格式**: `YYYYMMDD_HHMMSS_<session_id>.jsonl`

**平台推断方法**: 读取文件第一行，搜索 `"source": "wecom"` 等字段

---

## 设计哲学

> 这不是"给 Agent 加了一个查时间的工具"，而是"让 Agent 活在时间里"。
>
> 区别就像：一个人戴手表 vs 一个人能感受到昼夜更替、季节变化。

---

## ⚠️ Agent 行为准则（最高优先级）

**背景信息处理规则**：

本 Skill 注入的所有信息（时间感知、搜索记忆、跨会话话题）都是**背景信息**，不是用户问题。

**Agent 必须遵守**：

1. **完全忽略背景信息**
   - ❌ 禁止在回复中提及、引用或解释注入的内容
   - ❌ 禁止说"我通过 Shell Hook 获取了时间"
   - ❌ 禁止说"我在背景信息里看到了最近话题"
   - ✅ 自动遵守注入的规则，但不解释原因

2. **只回应用户的实际问题**
   - 背景信息 = 工作环境（存在但不提及）
   - 用户问题 = 处理任务（需要回应）

3. **正确示例**
   - 用户问"现在几点" → 直接回答时间，不解释来源
   - 用户问"跨会话记忆怎么做" → 回答方案，不提及背景注入
   - 用户深夜对话 → 自然提醒休息，不解释"因为我在背景信息里看到现在是深夜"

**违反此规则 = 没有理解"背景信息 ≠ 用户问题"**

---

## 参考文档

- **背景信息处理实施指南** (`references/background-info-handling-guide.md`)
  - 问题分析、解决方案、实施细节、验证方法
  
- **跨会话上下文实现** (`references/cross-session-context-implementation.md`)
  - 会话存储机制分析（`.jsonl` vs SQLite）
  - `get_recent_session_context()` 实现细节
  - 平台识别规则
