---
name: fix-hermes-message-rate-limit
description: Hermes Agent 长消息完整解决方案 - 修复平台限流、输出截断、API 超时三大类问题
tags: [hermes, gateway, wechat, rate-limit, max-tokens, timeout, troubleshooting]
version: "1.2"
created: "2026-04-26"
updated: "2026-04-28"
author: "Hermes Agent"
---

# Hermes 长消息完整解决方案（限流 + 截断 + 超时）

## 🔍 快速诊断：你的问题属于哪一类？

| 错误现象 | 问题类型 | 对应章节 |
|---------|---------|---------|
| `finish_reason='length'` / 回复输出到一半突然停止 | 输出截断 (max_tokens 限制) | 🚀 配套2：输出截断防护 |
| 长消息分块发送失败 / 看起来"卡死" / 消息不完整 | 平台限流 (发送频率限制) | 🔧 修复步骤 |
| 推理中途中断 / `HERMES_STREAM_STALE_TIMEOUT` 错误 | API 超时 (推理时间太长) | 🚀 配套1：长上下文超时防护 |

---

## 问题描述

当 Hermes Agent 输出长消息时，会自动拆分成多条消息发送。如果发送频率超过平台限制，会触发限流，表现为：
- ❌ 消息发送失败
- ⏸️ 看起来像是"卡死"
- 🤫 没有明显错误提示但消息无法送达

## 平台限流阈值

| 平台 | 限流阈值 | 状态 |
|------|----------|------|
| 微信/企业微信 | ~5 条/秒 | ⚠️ 容易触发 |
| Telegram | 内置限流 | ✓ 自动处理 |
| Discord | 内置重试 | ✓ 自动处理 |
| Feishu/Lark | Webhook 限流检测 | ✓ 内置 |
| Slack | rate_limited 重试 | ✓ 内置 |

## 🔧 修复步骤

### 步骤 1: 定位配置位置

```bash
# 查看当前微信平台配置
cd ~/.hermes && grep -A5 "weixin" config.yaml

# 查看代码中的默认配置
cd ~/.hermes/hermes-agent && grep -n "send_chunk_delay" gateway/platforms/weixin.py
```

### 步骤 2: 修改 config.yaml 增加延迟

⚠️ **重要**: 数值必须用引号包裹，否则会被 YAML 解析为数字类型导致后续读取失败。

```yaml
platforms:
  weixin:
    extra:
      # 分块发送间隔（秒）- 原默认 0.35
      send_chunk_delay_seconds: "0.8"
      # 重试次数 - 原默认 2
      send_chunk_retries: "3"
```

### 步骤 2 备选: 使用 Python 脚本自动化修改（推荐）

避免手动编辑出错，使用脚本安全修改：

```python
import yaml

with open('/Users/me/.hermes/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

if 'weixin' in config.get('platforms', {}):
    if 'extra' not in config['platforms']['weixin']:
        config['platforms']['weixin']['extra'] = {}
    config['platforms']['weixin']['extra']['send_chunk_delay_seconds'] = "0.8"
    config['platforms']['weixin']['extra']['send_chunk_retries'] = "3"

with open('/Users/me/.hermes/config.yaml', 'w') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

print("✅ 限流配置已更新")
```

### 步骤 3: 重启网关

```bash
hermes gateway restart

# 验证状态
hermes gateway status
```

## 📊 配置效果对比

| 配置项 | 修改前 | 修改后 | 变化 |
|--------|--------|--------|------|
| 分块间隔 | 0.35s | 0.8s | +128% |
| 发送频率 | ~2.8 条/秒 | ~1.25 条/秒 | -55% |
| 重试次数 | 2 次 | 3 次 | +50% |

> **说明**: 1.25 条/秒远低于 5 条/秒的限流阈值。

## 🔍 排查 Checklist

- [ ] 确认网关已重启
- [ ] 检查 config.yaml 配置是否正确
- [ ] 发送长消息测试（让 Agent 输出 1000+ 字）
- [ ] 查看 gateway.log 是否有错误
- [ ] 如仍有问题，继续增大延迟

## 🚨 进阶方案

### 方案 A: 更保守的延迟设置

如果 0.8s 仍然触发限流，继续增加：

```yaml
send_chunk_delay_seconds: "1.2"    # 约 0.8 条/秒，最保守设置
```

### 方案 B: 使用环境变量

```bash
# 在 ~/.zshrc 或 ~/.bashrc 中添加
export WEIXIN_SEND_CHUNK_DELAY_SECONDS="1.0"
export WEIXIN_SEND_CHUNK_RETRIES="3"
```

### 方案 C: 减少分块大小（需修改源码）

修改 `gateway/platforms/weixin.py` 中的 `max_length` 参数（默认 800），
使每块更小、发送时间更长。

## 📝 验证方法

### 方法 1: 日志检查
```bash
tail -50 ~/.hermes/logs/gateway.log
tail -20 ~/.hermes/logs/gateway.error.log
```

### 方法 2: 功能测试
向 Agent 发送指令："写一篇 1000 字的关于人工智能的文章"

观察：
- ✓ 消息能否完整送达
- ✓ 是否有明显卡顿
- ✓ 所有分块是否按顺序到达

### 方法 3: 查看当前配置
```bash
cd ~/.hermes && grep -A3 "send_chunk" config.yaml
```

## 📂 相关代码位置

| 文件 | 行号 | 说明 |
|------|------|------|
| `gateway/platforms/weixin.py` | 1140-1141 | 延迟配置读取 |
| `gateway/platforms/weixin.py` | 1616-1617 | 分块发送间隔逻辑 |
| `~/.hermes/config.yaml` | 微信 extra 节点 | 用户自定义配置 |

## ⚠️ 常见误区

1. ❌ **以为是网络问题** - 限流是平台侧的限制，不是网络问题
2. ❌ **以为是 Agent 卡死** - Agent 正常运行，只是消息发送被拦截
3. ❌ **重启就好了** - 不修改配置，重启后发送长消息仍会触发限流

## ✅ 修复成功标准

- 1000+ 字的长消息能够完整送达
- 所有分块按顺序到达，没有丢失
- 网关日志中没有 `rate_limit` 或发送失败相关错误

---

## 🚀 配套1：长上下文超时防护

### 问题背景

大型模型（GLM-4, Doubao, DeepSeek 等）处理长上下文时需要较长推理时间：
- 13K 上下文: 约 8-10 分钟
- 128K 上下文: 约 20-30 分钟
- 流式输出按字符/令牌增量输出，整体耗时更长

默认配置（180 秒/3 分钟）远远不够，会导致：
- ❌ 任务中途中断
- 📋 错误日志被 `HERMES_STREAM_STALE_TIMEOUT` 污染
- 😞 用户体验差（回复不完整）

### 修复方案：全局 + 分层超时配置

#### 步骤 1: 添加全局 env 超时配置

在 `config.yaml` 顶层添加：
```yaml
env:
  # 流式输出超时（秒）- 长上下文推理需要更多时间
  HERMES_STREAM_STALE_TIMEOUT: "600"      # 10 分钟
  # 非流式输出超时
  HERMES_NON_STREAM_TIMEOUT: "900"        # 15 分钟
  # OpenAI 兼容 API 超时
  OPENAI_TIMEOUT: "600"                    # 10 分钟
```

#### 步骤 2: Provider 级独立配置（按需）

对特别慢的模型 Provider，单独设置更长超时：
```yaml
providers:
  edgefn:  # 例如：GLM-4 / Doubao 等需要特别长的推理时间
    base_url: "https://api.example.com/v1"
    api_key: "${EDGEFN_API_KEY}"
    timeout: 600    # 独立设置 10 分钟超时
```

#### 步骤 3: 验证配置生效

```bash
# 检查配置
cd ~/.hermes && grep -A5 "env:" config.yaml

# 重启网关
hermes gateway restart

# 测试长上下文任务
# 让 Agent 处理 >10K tokens 的任务，观察是否能完整输出
```

### 超时配置效果对比

| 配置项 | 默认值 | 推荐值 | 提升幅度 |
|--------|--------|--------|----------|
| 流式超时 | 180s | 600s | +233% |
| 非流式超时 | 300s | 900s | +200% |
| OpenAI API 超时 | 120s | 600s | +400% |

> **说明**: 600 秒（10 分钟）可以覆盖绝大多数 128K 以内的长上下文推理场景。

---

## 🚀 配套2：输出截断（max_tokens）防护

### 问题背景

Hermes Agent 默认的 `max_tokens`（模型单次输出 token 限制）只有 2000，这个限制对于长回复场景（代码生成、深度分析、长文档写作、多步骤推理）来说很容易被触发，导致：
- ❌ 错误：`Response truncated due to output length limit`
- 📋 错误日志：`finish_reason='length'`
- 😞 回复不完整、代码被截断、分析中途停止

### 修复方案：增加输出 token 限制

#### 步骤 1: 修改 model 节点配置

在 `config.yaml` 的 `model` 节点下添加：
```yaml
model:
  # 输出 cap - 单次 API 调用最大输出 tokens（默认仅 2000）
  max_tokens: 16384
```

#### 步骤 2: Python 脚本自动化修改

```python
import yaml

with open('/Users/me/.hermes/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

if 'model' not in config:
    config['model'] = {}

# 设置为 16384 tokens - 足够长的输出长度
config['model']['max_tokens'] = 16384

with open('/Users/me/.hermes/config.yaml', 'w') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

print("✅ 已添加 max_tokens 配置: 16384")
```

#### 步骤 3: 验证配置并重启

```bash
# 检查配置
cd ~/.hermes && grep -A5 "model:" config.yaml | grep max_tokens

# 重启网关
hermes gateway restart
```

### 输出配置效果对比

| 配置项 | 默认值 | 推荐值 | 最大可选 | 提升幅度 |
|--------|--------|--------|----------|----------|
| max_tokens | 2,000 | 16,384 | 65,536 | **+719%** |

> **说明**: 
> - 16384 足够应对绝大多数长回复场景
> - 对于 DeepSeek 等支持超长输出的模型，可以设置为 32768 或 65536
> - 上限取决于具体模型的最大输出能力

### 排查 Checklist

- [ ] 确认 `model.max_tokens` 已正确配置
- [ ] 确认源代码已修复（关键！）
- [ ] 确认网关已重启
- [ ] 生成长回复测试（让 Agent 写 1000 字文章或 200 行代码）
- [ ] 查看是否还有 `finish_reason='length'` 错误
- [ ] 如仍有截断，继续增大 `max_tokens` 值

---

## 🚀 配套3：源代码修复（关键！）

### 问题背景

**配置文件中的 `model.max_tokens` 不会自动生效！**

Hermes Agent 的代码中没有读取这个配置，也没有在创建 Agent 实例时传递 `max_tokens` 参数。这是一个架构层面的 bug。

影响文件：
1. `cli.py` - CLI 模式下创建 Agent
2. `tui_gateway/server.py` - 网关模式下创建 Agent

### 修复方案：添加配置读取和参数传递

#### 修复 1: CLI 模式 (`cli.py`)

**位置**: `~/.hermes/hermes-agent/cli.py`

##### 第一步: 在 `__init__` 中读取配置（约 2050 行）

在 `max_turns` 配置读取之后添加：

```python
# Max tokens (output length limit): config file > default (None = let adapter use model default)
_model_config = CLI_CONFIG.get("model", {})
if isinstance(_model_config, dict) and _model_config.get("max_tokens"):
    self.max_tokens = int(_model_config["max_tokens"])
elif CLI_CONFIG.get("max_tokens"):
    self.max_tokens = int(CLI_CONFIG["max_tokens"])
else:
    self.max_tokens = None  # None = let adapter use model default
```

##### 第二步: 创建 Agent 时传递参数（约 3500 行）

在 `AIAgent(` 调用中添加：

```python
self.agent = AIAgent(
    model=effective_model,
    api_key=runtime.get("api_key"),
    base_url=runtime.get("base_url"),
    provider=runtime.get("provider"),
    max_tokens=self.max_tokens,  # ← 添加这一行
    # ... 其他参数
)
```

#### 修复 2: 网关模式 (`tui_gateway/server.py`)

**位置**: `~/.hermes/hermes-agent/tui_gateway/server.py`

在 `_make_agent` 函数中（约 1403 行）添加：

```python
def _make_agent(sid: str, key: str, session_id: str | None = None):
    from run_agent import AIAgent
    from hermes_cli.runtime_provider import resolve_runtime_provider

    cfg = _load_cfg()
    system_prompt = ((cfg.get("agent") or {}).get("system_prompt", "") or "").strip()
    
    # Load max_tokens from config ← 添加这部分
    _model_config = cfg.get("model", {})
    max_tokens = None
    if isinstance(_model_config, dict) and _model_config.get("max_tokens"):
        max_tokens = int(_model_config["max_tokens"])
    elif cfg.get("max_tokens"):
        max_tokens = int(cfg["max_tokens"])
    
    model, requested_provider = _resolve_startup_runtime()
    runtime = resolve_runtime_provider(
        requested=requested_provider,
        target_model=model or None,
    )
    return AIAgent(
        model=model,
        provider=runtime.get("provider"),
        base_url=runtime.get("base_url"),
        api_key=runtime.get("api_key"),
        max_tokens=max_tokens,  # ← 添加这一行
        # ... 其他参数
    )
```

### 验证修复是否生效

```bash
# 检查代码修改是否正确
cd ~/.hermes/hermes-agent
grep -n "max_tokens=self.max_tokens" cli.py
grep -n "max_tokens=max_tokens" tui_gateway/server.py

# 应该能看到匹配结果
```

---

## ⚠️ 重要提醒：上游更新风险

当 Hermes Agent 发布新版本并执行 `hermes update` 时，本地的源代码修改会被覆盖！

建议：
1. 记录修复步骤，更新后重新应用
2. 或者使用 `hermes-local-mod-protection-safe-update` 技能保护本地修改

---

## 📚 相关文档

- `MESSAGE-RATE-LIMIT-FIX.md` - 详细修复记录
- `~/hermes-agent/gateway/platforms/ADDING_A_PLATFORM.md` - 平台开发指南
