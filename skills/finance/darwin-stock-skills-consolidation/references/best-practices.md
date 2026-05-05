# 四大核心 Skills 协同使用最佳实践

**创建时间**: 2026-05-02
**适用对象**: 已完成达尔文整合的四大核心 Skills
**目标用户**: 希望系统化使用股票分析交易生态的用户

---

## 📋 目录

1. [协同架构总览](#协同架构总览)
2. [数据流向与协作关系](#数据流向与协作关系)
3. [典型工作流](#典型工作流)
4. [最佳实践案例](#最佳实践案例)
5. [常见陷阱与避坑指南](#常见陷阱与避坑指南)
6. [配置参考](#配置参考)

---

## 协同架构总览

### 四层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    监控预警层                                │
│              market-intelligence-system                      │
│   (市场监控、自动触发、简报生成、推送通知)                    │
└───────────────────┬─────────────────────────────────────────┘
                    │ 市场预警信号
                    │ 交易日历更新
                    │ 数据源健康度
                    ↓
┌─────────────────────────────────────────────────────────────┐
│                    交易执行层                                │
│                 grid-trading-system                          │
│   (配置管理、行情获取、触发检测、交易执行、状态管理)          │
└───────────────────┬─────────────────────────────────────────┘
                    │ 交易信号
                    │ 持仓状态
                    │ 异常事件
                    ↓
┌─────────────────────────────────────────────────────────────┐
│                    分析研判层                                │
│              stock-analysis-framework                        │
│   (A股分析、ST专项、技术分析、量化回测、地缘政治、风险管理)   │
└───────────────────┬─────────────────────────────────────────┘
                    │ 分析结果
                    │ 风险评估
                    │ 投资建议
                    ↓
┌─────────────────────────────────────────────────────────────┐
│                    数据获取层                                │
│              stock-data-acquisition                          │
│   (多数据源切换、智能缓存、交易日历、自选股管理)              │
└─────────────────────────────────────────────────────────────┘
```

### 核心协作关系

| 层级 | Skill | 职责 | 与其他层协作 |
|------|-------|------|-------------|
| **监控预警** | market-intelligence-system | 全局监控、自动触发 | → 交易执行层（预警信号）<br>→ 所有层（数据源健康度） |
| **交易执行** | grid-trading-system | 自动交易 | → 监控预警层（交易信号）<br>→ 数据获取层（行情请求） |
| **分析研判** | stock-analysis-framework | 深度分析 | → 数据获取层（数据请求）<br>→ 监控预警层（分析结果） |
| **数据获取** | stock-data-acquisition | 数据基础设施 | → 所有层（数据服务） |

---

## 数据流向与协作关系

### 1. 自上而下：监控预警驱动

```
用户消息/定时触发
    ↓
AutoTrigger 检测关键词
    ↓
TimeAnchor 建立时间锚点
    ↓
MarketMonitor 获取市场数据（依赖 stock-data-acquisition）
    ↓
BriefGenerator 生成简报
    ↓
PushNotifier 推送通知
```

### 2. 自下而上：交易执行反馈

```
grid-trading-system 触发交易
    ↓
TradeExecutor 执行交易
    ↓
StateManager 更新持仓
    ↓
market-intelligence-system 接收交易信号
    ↓
BriefGenerator 在简报中展示
```

### 3. 双向协同：异常处理

```
market-intelligence-system 检测异常波动
    ↓
发送预警信号给 grid-trading-system
    ↓
grid-trading-system 暂停交易
    ↓
grid-trading-system 发送异常事件
    ↓
market-intelligence-system 推送错误通知
```

---

## 典型工作流

### 工作流 1: 日常监控与交易

**触发方式**: Cronjob 定时（每5分钟）

```
[Cron 触发] 交易时间每5分钟
    ↓
[market-intelligence-system]
    1. 判断交易日（TimeAnchor）
    2. 获取市场数据（MarketMonitor）
    3. 检测异常波动（MarketMonitor）
    4. 如有异常 → 发送预警信号
    ↓
[grid-trading-system]
    1. 接收预警信号（如有）
    2. 获取 ETF 行情（MarketDataFetcher）
    3. 检测网格触发（TriggerDetector）
    4. 执行交易（TradeExecutor）
    5. 更新状态（StateManager）
    6. 发送交易信号
    ↓
[market-intelligence-system]
    1. 接收交易信号
    2. 在下一期简报中展示
```

### 工作流 2: 用户主动分析

**触发方式**: 用户提问（"分析一下恒生科技ETF"）

```
[用户提问] "分析一下恒生科技ETF"
    ↓
[market-intelligence-system]
    1. AutoTrigger 检测关键词
    2. TimeAnchor 建立时间锚点
    3. MarketMonitor 获取市场概况
    ↓
[stock-data-acquisition]
    1. 获取恒生科技ETF实时行情
    2. 获取历史K线数据
    3. 智能缓存结果
    ↓
[stock-analysis-framework]
    1. 技术分析（趋势、支撑压力）
    2. 风险评估（波动率、回撤）
    3. 投资建议（买入/卖出/持有）
    ↓
[grid-trading-system]
    1. 获取当前持仓状态
    2. 计算网格触发位
    3. 提供交易参考
    ↓
[market-intelligence-system]
    1. 整合所有分析结果
    2. 生成综合简报
    3. PushNotifier 推送给用户
```

### 工作流 3: 异常事件处理

**触发方式**: 数据源故障 / 市场熔断 / 异常波动

```
[异常检测] 数据源故障 / 熔断 / 异常波动
    ↓
[stock-data-acquisition]
    1. 检测数据源故障
    2. 自动切换备用数据源
    3. 记录切换日志
    4. 如所有数据源失败 → 返回错误
    ↓
[market-intelligence-system]
    1. 接收数据源健康度报告
    2. 判断异常严重程度
    3. 如严重异常 → 发送预警信号
    ↓
[grid-trading-system]
    1. 接收预警信号
    2. 暂停交易执行
    3. 记录暂停原因
    4. 发送异常事件
    ↓
[market-intelligence-system]
    1. 接收异常事件
    2. PushNotifier 推送错误通知
    3. 等待系统恢复
```

---

## 最佳实践案例

### 案例 1: 完整的交易日监控体系

**目标**: 建立从开盘到收盘的完整监控体系

**配置步骤**:

```bash
# 1. 配置 Cronjob（market-intelligence-system）
# 早盘简报（11:35）
hermes cron create "35 11 * * 1-5" \
  --skill market-intelligence-system \
  --prompt "生成早盘简报" \
  --target weixin

# 收盘简报（15:05）
hermes cron create "5 15 * * 1-5" \
  --skill market-intelligence-system \
  --prompt "生成收盘简报" \
  --target weixin

# 晚间复盘（20:00）
hermes cron create "0 20 * * 1-5" \
  --skill market-intelligence-system \
  --prompt "生成晚间复盘简报" \
  --target weixin

# 2. 配置网格交易监控（grid-trading-system）
# 交易时间每5分钟检查
hermes cron create "*/5 9-11,13-15 * * 1-5" \
  --skill grid-trading-system \
  --prompt "执行网格交易检查" \
  --target weixin

# 3. 配置 Shell Hook（自动触发）
# 编辑 ~/.hermes/config.yaml
hooks:
  pre_llm_call:
  - command: /Users/me/.hermes/hooks/supervisor-precheck.py
    timeout: 5
```

**预期效果**:

- 早盘收盘自动推送简报
- 交易时间每5分钟检查网格触发
- 用户提问自动注入市场上下文
- 异常事件实时推送

---

### 案例 2: ST股票风险监控与交易暂停

**目标**: 当市场出现异常波动时，自动暂停网格交易

**配置步骤**:

```python
# grid-trading-system/config.json 添加异常处理
{
  "symbol": "513130",
  "name": "恒生科技ETF",
  "pause_on_warning": true,  # 接收到预警时暂停
  "resume_after_minutes": 30  # 30分钟后自动恢复
}
```

**执行流程**:

```
[market-intelligence-system]
检测到异常波动（跌停家数>50）
    ↓
发送预警信号给 grid-trading-system
    ↓
[grid-trading-system]
暂停交易执行
记录暂停原因：异常波动
等待30分钟后恢复
    ↓
发送异常事件给 market-intelligence-system
    ↓
[market-intelligence-system]
推送微信通知：
"⚠️ 异常波动预警
跌停家数达到 50 家，网格交易已暂停
预计 30 分钟后恢复"
```

---

### 案例 3: 多市场对比分析

**目标**: 对比美股和A股走势，寻找投资机会

**用户请求**: "对比一下美股和A股最近的表现"

**执行流程**:

```
[market-intelligence-system]
AutoTrigger 检测到多市场关键词
    ↓
TimeAnchor 分别建立两个时间锚点：
  - 美股：美东时间 2026-05-01 16:00（收盘）
  - A股：北京时间 2026-05-02 15:00（收盘）
    ↓
MarketMonitor 分别获取数据：
  - 美股：道琼斯、纳斯达克、标普500
  - A股：上证指数、深证成指、创业板指
    ↓
[stock-data-acquisition]
获取美股和A股的历史数据
智能缓存结果
    ↓
[stock-analysis-framework]
对比分析：
  - 走势对比（相关性分析）
  - 资金流向（北向资金 vs 美股资金）
  - 情绪对比（VIX vs A股涨跌停）
  - 投资启示（背离机会、联动效应）
    ↓
[market-intelligence-system]
生成对比简报
PushNotifier 推送给用户
```

**输出示例**:

```
📊 美股 vs A股 对比分析

【美股】（美东时间 05-01 收盘）
道琼斯：38,750 (+0.8%)
纳斯达克：16,230 (+1.2%)
标普500：5,150 (+0.9%)

【A股】（北京时间 05-02 收盘）
上证指数：3,150 (-0.5%)
深证成指：9,850 (-0.8%)
创业板指：1,850 (-1.2%)

【相关性】
30日相关系数：0.42（中等正相关）
背离程度：美股强于A股 1.7%

【资金流向】
北向资金：-45亿（连续3日流出）
美股资金：+120亿（持续流入）

【投资启示】
1. 美股强于A股，存在背离机会
2. 北向资金持续流出，需等待企稳
3. 关注美股科技股对A股科技板块的传导效应
```

---

## 常见陷阱与避坑指南

### 陷阱 1: 时间锚点混乱

**错误场景**:

```
用户（北京时间 09:00）："看看美股昨天表现"
系统错误地获取了美股 05-02 的数据（实际应为 05-01）
```

**避坑方法**:

1. 强制使用 TimeAnchor 建立时间锚点
2. 美股日期换算规则：
   - 北京时间 09:00 = 美东时间 前日 21:00
   - 美股"昨天" = 美东日期 - 1
3. 在输出中明确标注日期

**正确流程**:

```python
# TimeAnchor 模块
北京时间 = "2026-05-02 09:00"
美东时间 = 北京时间 - 12小时 = "2026-05-01 21:00"
目标美股日期 = "2026-05-01"（美东时间）
```

---

### 陷阱 2: 数据源切换导致数据不一致

**错误场景**:

```
第一次请求：使用新浪数据源，价格 = 0.625
第二次请求：新浪故障，切换腾讯，价格 = 0.626
用户质疑："为什么价格变了？"
```

**避坑方法**:

1. 在输出中标注数据源和时间戳
2. 使用缓存减少数据源切换
3. 多源价格差异>0.1%时记录警告

**正确流程**:

```
[输出]
恒生科技ETF（513130）
价格：0.625 元
数据源：新浪财经
时间：2026-05-02 14:35:12
```

---

### 陷阱 3: 网格交易在非交易时段触发

**错误场景**:

```
Cronjob 在 11:30-13:00 午休时段执行
检测到价格触发，但实际无法交易
```

**避坑方法**:

1. 使用 TradingCalendar 判断交易时段
2. Cronjob 配置排除午休时段：`*/5 9-11,13-15 * * 1-5`
3. 执行前再次检查交易时段

**正确配置**:

```bash
# 正确：排除午休时段
hermes cron create "*/5 9-11,13-15 * * 1-5" ...

# 错误：包含午休时段
hermes cron create "*/5 9-15 * * 1-5" ...
```

---

### 陷阱 4: 异常事件导致系统卡死

**错误场景**:

```
所有数据源故障 → 无限重试 → 系统卡死
```

**避坑方法**:

1. 设置重试上限（最多3次）
2. 失败后返回错误，不阻塞
3. 推送错误通知，人工介入

**正确流程**:

```python
# stock-data-acquisition
max_retries = 3
for retry in range(max_retries):
    try:
        data = fetch_from_source()
        return data
    except Exception as e:
        log_error(e)
        if retry == max_retries - 1:
            return None  # 返回错误，不阻塞
```

---

## 配置参考

### 完整的 Cronjob 配置

```yaml
# ~/.hermes/config.yaml

cron_jobs:
  # 早盘简报
  - name: 早盘简报
    schedule: "35 11 * * 1-5"
    skill: market-intelligence-system
    prompt: "生成早盘简报"
    target: weixin

  # 收盘简报
  - name: 收盘简报
    schedule: "5 15 * * 1-5"
    skill: market-intelligence-system
    prompt: "生成收盘简报"
    target: weixin

  # 晚间复盘
  - name: 晚间复盘
    schedule: "0 20 * * 1-5"
    skill: market-intelligence-system
    prompt: "生成晚间复盘简报"
    target: weixin

  # 网格交易监控
  - name: 网格交易监控
    schedule: "*/5 9-11,13-15 * * 1-5"
    skill: grid-trading-system
    prompt: "执行网格交易检查"
    target: weixin
```

### Shell Hook 配置

```yaml
# ~/.hermes/config.yaml

hooks:
  pre_llm_call:
  - command: /Users/me/.hermes/hooks/time-sense-injector.py
    timeout: 5
  - command: /Users/me/.hermes/hooks/smart-skill-loader.py
    timeout: 5
  - command: /Users/me/.hermes/hooks/supervisor-precheck.py
    timeout: 5
```

### 网格交易配置

```json
// ~/.hermes/grid-trading/config.json
{
  "symbol": "513130",
  "name": "恒生科技ETF",
  "base_price": 0.625,
  "grid_spacing": 0.025,
  "grid_spacing_pct": 0.04,
  "upper_grids": 6,
  "lower_grids": 8,
  "amount_per_grid": 715,
  "initial_position": 3,
  "total_capital": 10000,
  "pause_on_warning": true,
  "resume_after_minutes": 30,
  "last_updated": "2026-05-02T10:00:00Z"
}
```

---

## 总结

四大核心 Skills 通过清晰的分层架构和双向数据流，实现了完整的股票分析交易生态：

- **数据获取层**：提供可靠的数据基础设施
- **分析研判层**：提供深度分析和投资建议
- **交易执行层**：自动化网格交易执行
- **监控预警层**：全局监控和智能推送

通过合理的配置和协作，可以构建一个自动化、智能化的投资决策系统。
