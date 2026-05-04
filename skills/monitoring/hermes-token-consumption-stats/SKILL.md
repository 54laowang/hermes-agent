---
name: Hermes Token Consumption Statistics
description: 查询 Hermes Agent 今日各平台 Token 消耗统计和成本估算，支持按日/按时段/按模型精确分析
author: Hermes Agent
created: 2026-04-24
updated: 2026-04-29
tags: monitoring, tokens, cost, statistics, sqlite
---

# Hermes Token 消耗统计

查询 Hermes Agent 的 Token 使用情况和成本估算。

## 触发条件

当用户问以下问题时使用：
- "今天消耗了多少 token"
- "统计我的 token 使用"
- "计算 API 成本"
- "token 消耗报告"
- "查看 token 统计"

---

## 方法一：SQLite 精确查询（推荐）

### 数据源

Hermes 的 session 数据存储在 SQLite 数据库：`~/.hermes/state.db`

关键表：`sessions`

| 字段 | 类型 | 说明 |
|------|------|------|
| `started_at` | REAL | Unix timestamp，会话开始时间 |
| `model` | TEXT | 使用的模型 |
| `input_tokens` | INTEGER | 输入 tokens |
| `output_tokens` | INTEGER | 输出 tokens |
| `cache_read_tokens` | INTEGER | 缓存读取 tokens |
| `cache_write_tokens` | INTEGER | 缓存写入 tokens |
| `reasoning_tokens` | INTEGER | 推理 tokens |

### 查询模板

#### 1. 今日总览

```sql
SELECT 
  date(started_at, 'unixepoch', 'localtime') as date,
  model,
  COUNT(*) as session_count,
  SUM(input_tokens) as total_input_tokens,
  SUM(output_tokens) as total_output_tokens,
  SUM(input_tokens + output_tokens) as total_tokens,
  SUM(cache_read_tokens) as cache_read_tokens,
  SUM(reasoning_tokens) as reasoning_tokens
FROM sessions
WHERE date(started_at, 'unixepoch', 'localtime') = date('now', 'localtime')
GROUP BY date, model
ORDER BY total_tokens DESC;
```

#### 2. 按时段分布

```sql
SELECT 
  strftime('%H', started_at, 'unixepoch', 'localtime') as hour,
  COUNT(*) as sessions,
  SUM(input_tokens) as input,
  SUM(output_tokens) as output,
  SUM(input_tokens + output_tokens) as total
FROM sessions
WHERE date(started_at, 'unixepoch', 'localtime') = date('now', 'localtime')
GROUP BY hour
ORDER BY hour;
```

#### 3. 指定日期查询

将 `date('now', 'localtime')` 替换为目标日期，如 `'2026-04-29'`。

### 执行方法

```bash
# 直接查询
sqlite3 ~/.hermes/state.db "SQL查询语句"

# 或者通过 hermes CLI
hermes insights --days 1
```

---

## 方法二：日志文件估算（备用）

当 SQLite 数据不可用时，通过日志估算。

### 数据源

`~/.hermes/logs/agent.log` 中 "response ready" 记录

### 提取字段

- platform (平台)
- api_calls (API 调用次数)
- response chars (输出字符数)

### 估算公式

- 输出 Tokens ≈ 字符数 × 0.75 (1 token ≈ 1.33 个字符)
- 输入 Tokens ≈ 输出 Tokens × 1.5 (包含问题和上下文)
- 总计 = 输入 + 输出

### Python 实现

```python
import os
import re
from datetime import datetime

home = os.path.expanduser("~")
agent_log = os.path.join(home, ".hermes/logs/agent.log")
today = datetime.now().strftime("%Y-%m-%d")

platform_stats = {}

with open(agent_log, 'r') as f:
    for line in f:
        if today not in line:
            continue
        match = re.search(r'response ready: platform=(\w+) chat=.*? time=[\d.]+s api_calls=(\d+) response=(\d+) chars', line)
        if match:
            platform = match.group(1)
            api_calls = int(match.group(2))
            chars = int(match.group(3))
            if platform not in platform_stats:
                platform_stats[platform] = {'count': 0, 'api_calls': 0, 'chars': 0}
            platform_stats[platform]['count'] += 1
            platform_stats[platform]['api_calls'] += api_calls
            platform_stats[platform]['chars'] += chars

# 计算汇总
total_responses = sum(s['count'] for s in platform_stats.values())
total_api_calls = sum(s['api_calls'] for s in platform_stats.values())
total_chars = sum(s['chars'] for s in platform_stats.values())
output_tokens = int(total_chars * 0.75)
input_tokens = int(output_tokens * 1.5)
grand_total = output_tokens + input_tokens
```

---

## 常见模型价格（2026年4月）

### DeepSeek V4 Pro（优惠期至2026年5月31日）

| 项目 | 原价 | 优惠价（2.5折） |
|------|------|----------------|
| 输入（缓存命中） | ¥0.1/M | **¥0.025/M** |
| 输入（缓存未命中） | ¥12/M | **¥3/M** |
| 输出 | ¥24/M | **¥6/M** |

**新闻来源**：搜索"DeepSeek V4 Pro 优惠 2026"

### DeepSeek V4 Flash

| 项目 | 价格 |
|------|------|
| 输入 | ¥0.14/M |
| 输出 | ¥0.28/M |

### DeepSeek V3.2

| 项目 | 价格 |
|------|------|
| 输入（缓存命中） | $0.028/M |
| 输入（缓存未命中） | $0.28/M |
| 输出 | $0.42/M |

### 其他模型

| 模型 | 输入 $/M | 输出 $/M |
|------|---------|---------|
| GPT-4o | $2.50 | $10.00 |
| Claude Sonnet 4 | $3.00 | $15.00 |
| Gemini Pro | $1.25 | $5.00 |

---

## 费用计算公式

```
输入费用 = input_tokens × 输入单价 ÷ 1,000,000
输出费用 = output_tokens × 输出单价 ÷ 1,000,000
总费用 = 输入费用 + 输出费用
```

**缓存优化**：
- 如果有缓存命中，输入费用分开计算
- 缓存命中的价格通常是未命中的 1/10 到 1/120

**示例计算**（DeepSeek V4 Pro，48M tokens）：

```
输入费用 = 48,127,761 × ¥3/M ÷ 1,000,000 = ¥144.38
输出费用 = 223,645 × ¥6/M ÷ 1,000,000 = ¥1.34
总费用 = ¥145.72

如果 80% 缓存命中：
输入（缓存命中）= 38,502,209 × ¥0.025/M = ¥0.96
输入（缓存未命中）= 9,625,552 × ¥3/M = ¥28.88
总费用 = ¥0.96 + ¥28.88 + ¥1.34 = ¥31.18（节省 78%）
```

---

## 报告模板

```markdown
## 📊 YYYY-MM-DD Token 消耗统计报告

### 一、总体消耗

| 指标 | 数值 |
|------|------|
| **会话总数** | X 次 |
| **输入 Tokens** | X (X.XX M) |
| **输出 Tokens** | X (X.XX M) |
| **总 Tokens** | X (X.XX M) |
| **缓存读取 Tokens** | X |
| **使用模型** | XXX |

### 二、时段分布

| 时段 | 会话数 | 输入 Tokens | 输出 Tokens | 总 Tokens |
|------|--------|------------|------------|----------|
| HH:00 | X | X | X | X |

**峰值时段：** HH:00-HH:00（X tokens）

### 三、费用计算（按 X 模型计算）

| 场景 | 输入费用 | 输出费用 | 总费用 |
|------|---------|---------|--------|
| **全缓存未命中** | ¥X.XX | ¥X.XX | **¥X.XX** |
| **80%缓存命中** | ¥X.XX | ¥X.XX | **¥X.XX** |

### 四、关键发现

1. 输入占 X%（原因：长上下文加载）
2. 峰值时段消耗占 X%
3. 启用缓存可节省 X%

### 五、优化建议

1. 启用缓存：`hermes config set cache.enabled true`
2. 减少不必要的长上下文加载
3. 合并多个小会话
```

---

## 关键发现

1. **输入占主导** - 通常占 95%+ tokens（Memory + Skills + 系统提示词）
2. **时段集中** - 高峰时段消耗远超其他时段
3. **缓存策略关键** - 缓存命中可节省 70-90% 输入费用
4. **缓存命中价格优势** - 是未命中价格的 **1/120**（DeepSeek V4 Pro）

---

## 注意事项

1. **时区问题** - 确保查询时使用 `localtime` 参数，否则时间会显示为 UTC
2. **价格变化** - 模型价格会变化，查询前先搜索最新价格
3. **优惠截止** - 优惠活动有截止日期，注意检查是否过期
4. **提供商差异** - 不同提供商的价格可能不同（官方 vs 第三方）
5. **估算 vs 精确** - 优先使用 SQLite 方法，日志估算仅作备用
