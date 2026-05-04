---
name: Hermes Timeout & Rate Limit Optimization
description: 系统性修复 Hermes Agent 长消息限流和 API 超时问题的标准化流程
author: Hermes Assistant
created: 2026-04-26
tags: [hermes, timeout, rate-limit, glm-5, api, configuration]
---

# Hermes 超时与限流优化技能

## 适用场景

当出现以下问题时使用此技能：
- ⚠️ `No response from provider for XXXs` - API 超时
- 📨 长消息拆块发送时触发平台限流（看起来像卡死）
- 🔄 `Interrupting current task` - 超时后发送新消息导致中断
- GLM-5 / 智谱 / 其他处理较慢的模型

---

## 问题一：消息频率限流修复

### 问题表现
- 长消息拆分成多条发送时
- 发送频率超过平台限制（微信 ~5 条/秒）
- 表现为"卡死"，无错误提示但消息无法送达

### 修复步骤

#### 1. 修改微信分块发送延迟
**文件**: `~/.hermes/config.yaml`

```yaml
platforms:
  weixin:
    extra:
      send_chunk_delay_seconds: "0.8"    # 原默认 0.35
      send_chunk_retries: "3"             # 原默认 2
```

**效果对比**：
| 指标 | 修改前 | 修改后 |
|------|--------|--------|
| 分块间隔 | 0.35s | 0.8s |
| 发送频率 | ~2.8 条/秒 | ~1.25 条/秒 |
| 重试次数 | 2 次 | 3 次 |

#### 2. 验证配置生效
```bash
cd ~/.hermes && grep -A5 "send_chunk_delay" config.yaml
hermes gateway restart
```

#### 3. 如仍有问题，继续增大延迟
```yaml
send_chunk_delay_seconds: "1.2"    # 更保守的设置 (~0.8 条/秒)
```

---

## 问题二：API 超时修复（GLM-5 等慢模型）

### 问题表现
```
⚠️ No response from provider for 515s (model: GLM-5, context: ~13,330 tokens). Reconnecting...
```

### 三层保护机制

#### 第一层：全局环境变量配置
**文件**: `~/.hermes/config.yaml`

```yaml
env:
  # 流式请求超时: 10 分钟 (原默认 3 分钟)
  HERMES_STREAM_STALE_TIMEOUT: '600'
  # 非流式请求超时: 15 分钟
  HERMES_NON_STREAM_TIMEOUT: '900'
  # OpenAI 兼容 API 超时
  OPENAI_TIMEOUT: '600'
```

#### 第二层：优化上下文超时缩放逻辑
**文件**: `hermes-agent/run_agent.py` （约第 6578 行）

修改超时梯度逻辑，降低阈值：
```python
# 原逻辑（阈值太高）
if _est_tokens > 100_000:          # 300s
elif _est_tokens > 50_000:        # 240s
else:                             # 180s ❌ 13K 不够

# 新逻辑（多梯度，覆盖更全面）
if _est_tokens > 100_000:
    _stream_stale_timeout = max(_stream_stale_timeout_base, 600.0)   # 10 分钟
elif _est_tokens > 50_000:
    _stream_stale_timeout = max(_stream_stale_timeout_base, 480.0)   # 8 分钟
elif _est_tokens > 20_000:
    _stream_stale_timeout = max(_stream_stale_timeout_base, 360.0)   # 6 分钟
elif _est_tokens > 10_000:
    _stream_stale_timeout = max(_stream_stale_timeout_base, 300.0)   # 5 分钟
elif _est_tokens > 5_000:
    _stream_stale_timeout = max(_stream_stale_timeout_base, 240.0)   # 4 分钟
else:
    _stream_stale_timeout = _stream_stale_timeout_base
```

**13K token 场景效果**: 180s → 300s (+67%)

#### 第三层：每个 Provider 单独配置
**文件**: `~/.hermes/config.yaml`

根据模型处理速度分级配置：

```yaml
providers:
  # 处理较快的模型 - Ark / 火山引擎
  ark:
    extra:
      timeout: 480           # 8 分钟
      stream_timeout: 480
      max_retries: 3
      retry_delay: 2

  # 中等速度 - ModelScope / DeepSeek
  modelscope:
    extra:
      timeout: 540           # 9 分钟
      stream_timeout: 540
      max_retries: 3
      retry_delay: 2

  # 处理较慢 - GLM-5 / edgefn / openrouter
  edgefn:
    extra:
      timeout: 600           # 10 分钟
      stream_timeout: 600
      max_retries: 3
      retry_delay: 2

  openrouter:
    extra:
      timeout: 600
      stream_timeout: 600
      max_retries: 3
      retry_delay: 2
```

#### Fallback Provider 也需要配置
```yaml
fallback_providers:
  - provider: ark.cn-beijing.volces.com
    timeout: 600
    stream_timeout: 600
    max_retries: 3
  # ... 其他 fallback 同理
```

---

## 验证修复效果

### 1. 检查配置是否生效
```bash
# 查看环境变量配置
grep -A5 "env:" ~/.hermes/config.yaml

# 查看 provider 配置
grep -A5 "extra:" ~/.hermes/config.yaml | grep -E "timeout|provider"
```

### 2. 重启网关
```bash
hermes gateway restart
sleep 3
hermes gateway status
```

### 3. 长上下文测试
让 Agent 处理一个长任务，验证不再超时：
```
"请分析以下 5000 字的文章并写一篇详细的总结..."
```

### 4. 监控日志
```bash
# 查看是否还有超时
grep "No response from provider\|stale for" ~/.hermes/logs/gateway.log

# 查看限流相关
grep "rate limit\|chunk" ~/.hermes/logs/gateway.log
```

---

## 进阶优化（如仍有问题）

### 方案 A: 继续增大全局超时
```yaml
env:
  HERMES_STREAM_STALE_TIMEOUT: '900'    # 15 分钟
  HERMES_NON_STREAM_TIMEOUT: '1200'     # 20 分钟
```

### 方案 B: 添加 Shell 环境变量
编辑 `~/.zshrc` 或 `~/.bashrc`:
```bash
export HERMES_STREAM_STALE_TIMEOUT=600
export HERMES_NON_STREAM_TIMEOUT=900
export OPENAI_TIMEOUT=600
```

### 方案 C: 切换到更快的模型
对于需要快速响应的场景，考虑使用：
- DeepSeek V3.2 (ModelScope)
- Ark Code (火山引擎)

---

## 常见问题 FAQ

### Q1: 为什么 GLM-5 这么慢？
A: GLM-5 是推理增强模型，长上下文需要进行深度思考（类似 DeepSeek R1），处理时间确实比普通模型长很多。13K token 需要 8-10 分钟是正常的。

### Q2: "Interrupting current task" 是什么原因？
A: 这是超时的连锁反应 - API 调用超时后，你又发了新消息，Hermes 会自动中断当前等待的任务。

### Q3: 所有模型都需要 10 分钟吗？
A: 不需要。根据模型处理速度配置不同的超时即可：
- 快模型 (Ark): 480s
- 中等 (DeepSeek): 540s
- 慢模型 (GLM-5): 600s+

### Q4: 改完代码后 Hermes 更新会覆盖吗？
A: 是的。如果 Hermes 升级覆盖了 `run_agent.py`，需要重新修改。建议保留这个技能以便重新应用。

---

## 修复 Checklist

- [ ] 消息限流：调整 `send_chunk_delay_seconds` 到 0.8s
- [ ] 全局超时：设置 `HERMES_STREAM_STALE_TIMEOUT=600`
- [ ] 代码修改：优化 `run_agent.py` 中的上下文缩放逻辑
- [ ] Provider 配置：每个 provider 添加 `extra.timeout`
- [ ] Fallback 配置：fallback providers 也添加超时
- [ ] 重启网关：`hermes gateway restart`
- [ ] 验证测试：发送长消息测试效果
- [ ] 文档记录：保存配置到修复说明文档

---

## 相关文件位置

| 文件 | 说明 |
|------|------|
| `~/.hermes/config.yaml` | 全局配置 + Provider 配置 |
| `hermes-agent/run_agent.py` | 上下文超时缩放逻辑 |
| `hermes-agent/gateway/platforms/weixin.py` | 微信分块发送延迟 |
| `~/.hermes/logs/gateway.log` | 网关日志 |
| `~/.hermes/GLM5-TIMEOUT-FIX.md` | 修复记录文档 |
| `~/.hermes/MESSAGE-RATE-LIMIT-FIX.md` | 限流修复文档 |

---

*Last updated: 2026-04-26*
