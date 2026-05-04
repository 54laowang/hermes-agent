---
name: vibe-trading-integration
description: Vibe-Trading 金融 AI 平台集成 - HKUDS 出品的多智能体量化交易系统。72 个金融技能、29 个智能体团队预设、7 个回测引擎、跨会话记忆。支持通过 MCP 集成到 Hermes。
author: Hermes
tags: [finance, trading, multi-agent, backtest, mcp, integration]
---

# Vibe-Trading 集成

**项目来源**: 香港大学数据科学学院 (HKUDS)  
**仓库**: https://github.com/HKUDS/Vibe-Trading  
**版本**: v0.1.6 (2026-04-28)  
**最后更新**: 2026-05-01

---

## 🎯 项目定位

**Vibe-Trading 是一个 AI 驱动的多智能体金融工作空间**：

```
自然语言 → 可执行交易策略 + 研究洞察 + 投资组合分析
```

**核心优势**：
- 🚀 **零门槛启动**: 一行命令 `pip install vibe-trading-ai`
- 🌐 **全市场覆盖**: A股、港股/美股、加密货币、期货、外汇
- 🤖 **多智能体协作**: 29 个预设交易团队（投资委员会、全球配置委员会等）
- 🧠 **持续学习**: 跨会话记忆 + 自进化技能
- 📊 **专业回测**: 7 个市场引擎 + 统计验证（蒙特卡洛、自助法、滚动前向）

---

## 📊 核心能力矩阵

| 模块 | 数量 | 详情 |
|------|------|------|
| **专业技能** | 72 个 | 7 大类别（数据源、策略、分析、资产类别、加密货币、资金流向、工具） |
| **智能体团队** | 29 个 | 预配置的投资、交易、风险管理团队 |
| **数据源** | 6 个 | AKShare、Tushare、yfinance、OKX、CCXT、Futu |
| **回测引擎** | 7 个 | A股、港股/美股、加密货币、期货、外汇、期权、跨市场组合 |
| **工具集** | 27 个 | 回测、因子分析、期权定价、形态识别等 |
| **LLM 提供商** | 12+ | OpenRouter、OpenAI、DeepSeek、Gemini、Kimi 等 |

---

## 🚀 快速开始

### 方法 1: PyPI 安装（推荐）

```bash
pip install vibe-trading-ai
vibe-trading init              # 交互式配置 .env
vibe-trading                   # 启动 CLI
vibe-trading serve --port 8899 # 启动 Web UI
```

### 方法 2: MCP 插件（集成到 Hermes）

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  vibe-trading:
    command: vibe-trading-mcp
    transport: stdio
    env:
      LANGCHAIN_PROVIDER: deepseek
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
```

**然后可以在 Hermes 中直接使用**：
```
用户: 用 Vibe-Trading 分析一下比亚迪的投资价值
Hermes: 自动调用 vibe-trading-mcp 工具进行分析
```

### 方法 3: Docker（零配置）

```bash
git clone https://github.com/HKUDS/Vibe-Trading.git
cd Vibe-Trading
cp agent/.env.example agent/.env
# 编辑 .env 设置 LLM API Key
docker compose up --build
```

访问 `http://localhost:8899`

---

## 🐝 多智能体协作示例

### Investment Committee（投资委员会）

**工作流**: 多空辩论 → 风险审查 → 投资经理最终决策

**智能体角色**：
- `bull_advocate` - 多方研究员（构建看多逻辑）
- `bear_advocate` - 空方研究员（识别风险）
- `risk_reviewer` - 风险审查官（评估风险）
- `portfolio_manager` - 投资经理（最终决策）

**DAG 执行流程**：
```
bull_advocate ──┐
                 ├─→ risk_reviewer ─→ portfolio_manager
bear_advocate ──┘
```

### 其他预设团队

- `global_allocation_committee` - 全球配置委员会
- `crypto_trading_desk` - 加密货币交易台
- `earnings_research_desk` - 盈利研究台
- `quant_strategy_desk` - 量化策略台
- `risk_committee` - 风险委员会
- `geopolitical_war_room` - 地缘政治作战室

查看完整列表：`vibe-trading --swarm-presets`

---

## 💡 典型应用场景

### 场景 1: 快速策略验证

```bash
# 自然语言描述策略
"帮我测试一个 A 股策略：
- 选股：ROE > 15%，PE < 20
- 买入：MACD 金叉
- 卖出：跌破 MA20
- 回测期：2023-2025"

# Vibe-Trading 自动：
# 1. 调用 akshare 获取数据
# 2. 编写策略代码
# 3. 运行回测引擎
# 4. 生成统计报告
# 5. 导出 Pine Script（TradingView）
```

### 场景 2: 多空辩论决策

```bash
# 启动投资委员会
vibe-trading --swarm-preset investment_committee

# 输入目标：
"分析贵州茅台（600519.SH）当前投资价值"

# 自动执行：
# 1. Bull Advocate 构建看多逻辑
# 2. Bear Advocate 识别风险
# 3. Risk Reviewer 评估风险
# 4. PM 最终决策（买/卖/观望）
```

### 场景 3: 跨市场组合回测

```bash
"测试一个跨市场组合：
- 60% A 股（沪深300 ETF）
- 30% 加密货币（BTC/USDT）
- 10% 黄金期货

回测 2024-2025，月度再平衡"

# Composite Engine 自动：
# - 共享资金池
# - 每个市场独立规则
# - 组合绩效分析
```

---

## 📦 数据源支持

| 数据源 | 市场 | 是否免费 | 说明 |
|--------|------|---------|------|
| **AKShare** | A股、港股、美股、期货、外汇 | ✅ 免费 | 主力数据源，覆盖全市场 |
| **yfinance** | 港股、美股 | ✅ 免费 | 雅虎财经数据 |
| **OKX** | 加密货币 | ✅ 免费 | 行情数据 |
| **CCXT** | 加密货币 | ✅ 免费 | 统一交易所接口 |
| **Tushare** | A股 | ⚠️ 需 Token | 高级数据（可选） |
| **Futu** | 港股、A股 | ⚠️ 需开户 | 实时行情（可选） |

**自动降级策略**: Tushare 失败 → AKShare 作为备用

---

## 🎨 72 个技能分类

### 1. 数据源 (6)
- `data-routing` - 智能数据源路由
- `tushare` / `yfinance` / `akshare` / `okx-market` / `ccxt`

### 2. 策略生成 (17)
- `strategy-generate` - 通用策略生成
- `cross-market-strategy` - 跨市场策略
- `technical-basic` - 基础技术分析
- `candlestick` / `ichimoku` / `elliott-wave` / `smc`
- `multi-factor` - 多因子策略
- `ml-strategy` - 机器学习策略

### 3. 分析研究 (15)
- `factor-research` - 因子研究
- `macro-analysis` / `global-macro` - 宏观分析
- `valuation-model` - 估值模型
- `earnings-forecast` - 盈利预测

### 4. 资产类别 (9)
- `options-strategy` / `options-advanced`
- `convertible-bond` / `etf-analysis`
- `asset-allocation` / `sector-rotation`

### 5. 加密货币 (7)
- `perp-funding-basis` / `liquidation-heatmap`
- `stablecoin-flow` / `defi-yield`
- `onchain-analysis`

### 6. 资金流向 (7)
- `hk-connect-flow` / `us-etf-flow`
- `edgar-sec-filings` / `financial-statement`

### 7. 工具 (8)
- `backtest-diagnose` / `report-generate`
- `pine-script` / `doc-reader` / `web-reader`

---

## 📊 回测引擎能力

### 7 大引擎

| 引擎 | 市场 | 特性 |
|------|------|------|
| `ChinaAEngine` | A股 | 涨跌停限制、T+1、停牌处理 |
| `GlobalEquityEngine` | 港股/美股 | 分红、拆股、货币转换 |
| `CryptoEngine` | 加密货币 | 7x24 交易、资金费率、滑点 |
| `ChinaFuturesEngine` | 商品期货 | 夜盘、保证金、杠杆 |
| `GlobalFuturesEngine` | 全球期货 | 跨时区、保证金 |
| `ForexEngine` | 外汇 | 点差、隔夜利息 |
| `CompositeEngine` | 跨市场组合 | 共享资金池、市场间再平衡 |

### 统计验证

- **Monte Carlo** - 蒙特卡洛模拟
- **Bootstrap CI** - 自助法置信区间
- **Walk-Forward** - 滚动前向验证
- **4 种优化器** - 参数优化

### 15+ 绩效指标

```
收益率指标: Total Return, CAGR, Monthly/Annual Return
风险指标: Max DD, Sharpe, Sortino, Calmar
交易统计: Win Rate, Profit Factor, Avg Hold Days
组合指标: Information Ratio, Tracking Error, Beta
```

---

## 🔧 高级特性

### 1. 跨会话记忆

```python
# 会话 1
用户: "我偏好价值投资，关注 ROE 和 FCF"
Vibe: 记住用户偏好 → 创建 skill "user-value-style"

# 会话 2（几天后）
用户: "帮我筛选 A 股"
Vibe: 自动应用 "user-value-style" → 筛选高 ROE、高 FCF 个股
```

### 2. 自进化技能

```python
# Agent 创建新技能
user: "我发现北向资金流入后，股票通常上涨"
Vibe: 创建技能 "northbound-inflow-signal"

# 后续使用中自动优化
- 记录使用次数
- 分析有效性
- 更新参数（流入阈值、持仓天数等）
```

### 3. 5 层上下文压缩

```
Layer 1: 最近 N 条消息（完整保留）
Layer 2: 工具调用摘要
Layer 3: 关键决策点
Layer 4: 用户偏好和约束
Layer 5: 会话元数据
```

---

## 🔗 与 Hermes Agent 集成

### 集成方案对比

| 方案 | 优势 | 适用场景 |
|------|------|---------|
| **MCP 插件** | 无缝集成、复用记忆 | 推荐，日常使用 |
| **独立部署** | 功能完整、Web UI | 深度研究 |
| **Skill 封装** | 灵活定制 | 特定需求 |

### MCP 集成步骤

1. **安装 Vibe-Trading**
   ```bash
   pip install vibe-trading-ai
   vibe-trading init
   ```

2. **配置 Hermes**
   ```yaml
   # ~/.hermes/config.yaml
   mcp_servers:
     vibe-trading:
       command: vibe-trading-mcp
       transport: stdio
   ```

3. **重启 Hermes**
   ```bash
   hermes gateway restart
   ```

4. **使用示例**
   ```
   用户: 用 Vibe-Trading 回测一个均线策略
   Hermes: [自动调用 vibe-trading-mcp 工具]
   ```

---

## 🎯 适用人群

| 用户类型 | 核心价值 |
|---------|---------|
| **量化研究员** | 快速策略验证 + 因子研究 + 统计验证 |
| **个人投资者** | 自然语言 → 策略代码，零编程门槛 |
| **投资顾问** | 自动生成投资报告 + 多空辩论 |
| **金融学生** | 学习策略开发 + 回测方法论 |
| **加密货币交易者** | 链上分析 + 资金流向 + 7x24 回测 |
| **AI 研究者** | 多智能体协作框架 + MCP 集成 |

---

## 📌 最新更新（2026-05-01）

- **相关性热力图** - 滚动收益相关性 + ECharts 可视化
- **OpenAI Codex OAuth** - 无需 API Key，使用 ChatGPT OAuth
- **A股 ST 预警过滤** - `ashare-pre-st-filter` 技能

---

## 🔍 相关资源

- **官方仓库**: https://github.com/HKUDS/Vibe-Trading
- **PyPI 包**: https://pypi.org/project/vibe-trading-ai/
- **文档**: https://github.com/HKUDS/Vibe-Trading#readme
- **Discord**: https://discord.gg/2vDYc2w5

---

## 📝 注意事项

1. **数据源选择**
   - 优先使用 AKShare（免费、覆盖全）
   - Tushare 仅在需要高级数据时使用（需 Token）
   - 加密货币数据 OKX/CCXT 均可

2. **LLM 提供商**
   - OpenRouter 推荐用于多模型切换
   - DeepSeek 性价比高（适合中文）
   - 本地可用 Ollama（无需 API Key）

3. **回测注意事项**
   - A股需考虑涨跌停限制
   - 加密货币 7x24 交易，注意滑点
   - 跨市场组合需设置再平衡规则

4. **与 Hermes 协同**
   - MCP 插件方式最简单
   - 可复用 Hermes 的记忆系统
   - 建议固定高频使用的技能

---

**集成价值**: Vibe-Trading 提供专业的金融分析能力，Hermes 提供通用 Agent 框架和记忆系统，两者结合可实现 1+1>2 的效果。
