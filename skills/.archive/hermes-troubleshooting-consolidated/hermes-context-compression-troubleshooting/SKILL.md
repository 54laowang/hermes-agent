---
name: hermes-context-compression-troubleshooting
description: 诊断和修复 Hermes 上下文压缩导致对话历史丢失的问题 - 配置摘要模型、增大上下文限制、持久化重要信息
version: 1.0.0
category: hermes
triggers:
  - 对话历史丢失
  - 聊天记录不完整
  - context compaction
  - 摘要生成失败
  - Summary generation was unavailable
  - conversation turns were removed
  - 微信聊天记录丢失
---

# Hermes 上下文压缩问题诊断与修复

## 问题现象

用户反馈：**微信/其他平台的聊天记录不完整，之前讨论的内容消失了**

典型错误信息：
```
Summary generation was unavailable. 
157 conversation turns were removed to free context space 
but could not be summarized.
```

---

## 根因分析

### 问题机制

Hermes 在对话历史超过 `max_context_tokens` 时会触发自动压缩：
1. 移除早期对话轮次
2. 尝试生成摘要保留关键信息
3. 如果摘要生成失败 → 早期对话直接丢失

### 常见原因

| 原因 | 症状 |
|------|------|
| 摘要模型未配置 | `compression.model` 指向未配置的 provider |
| 摘要模型不可用 | Gemini 等模型没有 API key |
| 上下文限制过小 | 默认 10000 tokens 太容易触发压缩 |

---

## 诊断步骤

### 1. 检查会话文件

```bash
# 查看最近的会话文件
ls -la ~/.hermes/sessions/*.jsonl | tail -5

# 搜索压缩标记
grep "CONTEXT COMPACTION\|removed\|Summary generation" ~/.hermes/sessions/*.jsonl
```

### 2. 检查压缩配置

```bash
cat ~/.hermes/config.yaml | grep -A10 "compression:"
```

关键配置项：
- `compression.model` - 摘要生成使用的模型
- `compression.provider` - 模型提供者
- `max_context_tokens` - 上下文窗口大小
- `max_history_tokens` - 历史记录限制

### 3. 检查摘要模型可用性

```bash
# 查看主模型配置
cat ~/.hermes/config.yaml | grep -A3 "^model:"

# 查看所有 providers
cat ~/.hermes/config.yaml | grep -A10 "providers:"
```

**问题标志**：`compression.model` 使用了未配置 API key 的 provider（如 `google/gemini`）

---

## 解决方案

### 方案 1：增大上下文限制（推荐）

```yaml
agents:
  default:
    max_context_tokens: 30000    # 从 10000 增大到 30000
    max_history_tokens: 25000    # 相应增大
    auto_summarize_threshold: 10000  # 触发阈值
```

**效果**：减少压缩触发频率，3 倍容量

### 方案 2：修复摘要模型配置

使用与主模型相同的配置：

```yaml
auxiliary:
  compression:
    model: GLM-5              # 与主模型一致
    provider: custom:jd       # 与主模型一致
    timeout: 120
```

**原则**：摘要模型应该使用已验证可用的 provider

### 方案 3：关闭压缩（不推荐）

```yaml
compression:
  enabled: false
```

**风险**：长对话可能导致 token 溢出

---

## 最佳实践

### 重要信息持久化

**不要依赖对话历史保存重要信息！**

上下文压缩会删除早期对话，重要信息应该主动保存：

```python
# 用户偏好 → memory
memory(action='add', target='user', content='用户四五月上夜班，20:00-08:00')

# 结构化事实 → fact_store
fact_store(action='add', entities=['网格交易'], content='恒生科技ETF网格计划，总资金1万')
```

**持久化优先级**：
1. 用户偏好、习惯 → `memory(target='user')`
2. 项目配置、环境事实 → `memory(target='memory')`
3. 结构化实体关系 → `fact_store`
4. 可复用流程 → `skill_manage`

### 验证配置生效

修改配置后必须重启 Hermes：

```bash
# 停止网关
pkill -f "hermes.*gateway"

# 重启网关
hermes gateway run --replace
```

---

## 配置模板

### 推荐配置

```yaml
# 上下文限制
agents:
  default:
    max_context_tokens: 30000
    max_history_tokens: 25000
    auto_summarize_threshold: 10000

# 摘要生成（与主模型一致）
auxiliary:
  compression:
    model: GLM-5
    provider: custom:jd
    timeout: 120

# 压缩行为
compression:
  enabled: true
  protect_last_n: 20        # 保护最近 20 轮
  target_ratio: 0.2         # 压缩目标比例
  threshold: 0.5            # 50% 时触发
```

---

## 问题排查清单

- [ ] 检查会话文件是否有 "Summary generation was unavailable"
- [ ] 检查 `compression.model` 是否使用未配置的 provider
- [ ] 检查 `max_context_tokens` 是否过小
- [ ] 验证摘要模型 provider 是否有有效 API key
- [ ] 确认重要信息已保存到 memory/fact_store
- [ ] 重启 Hermes 使新配置生效

---

## 相关技能

- [hermes-architecture-optimization](../hermes-architecture-optimization) - 记忆架构优化
- [Auto Fact Extraction](../knowledge-management/Auto%20Fact%20Extraction) - 自动事实提取
