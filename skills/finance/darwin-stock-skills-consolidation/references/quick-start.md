# 四大核心 Skills 快速入门指南

**创建时间**: 2026-05-02
**适用对象**: 新用户快速上手
**预计用时**: 5 分钟

---

## 🎯 5分钟快速上手

### 第一步：了解四大核心 Skills（1分钟）

| Skill | 核心功能 | 典型使用场景 |
|-------|---------|-------------|
| **stock-data-acquisition** | 数据获取 | 获取股价、查询交易日、管理自选股 |
| **stock-analysis-framework** | 分析研判 | A股分析、技术分析、风险评估 |
| **grid-trading-system** | 交易执行 | 网格交易自动化执行 |
| **market-intelligence-system** | 监控预警 | 市场简报、自动触发、推送通知 |

---

### 第二步：常用命令速查（2分钟）

#### 1. 查询股价

```
用户：查一下恒生科技ETF现在的价格
系统：自动调用 stock-data-acquisition → 返回实时价格
```

**关键词**: `查一下`、`股价`、`行情`、`价格`

---

#### 2. 分析个股

```
用户：分析一下贵州茅台
系统：自动调用 stock-analysis-framework → 返回技术分析 + 风险评估
```

**关键词**: `分析`、`股票名称`、`代码`

---

#### 3. 生成市场简报

```
用户：生成今日市场简报
系统：自动调用 market-intelligence-system → 返回完整简报
```

**关键词**: `简报`、`市场`、`复盘`

---

#### 4. 网格交易监控

```
用户：查看网格交易状态
系统：自动调用 grid-trading-system → 返回持仓 + 触发位
```

**关键词**: `网格`、`持仓`、`交易状态`

---

#### 5. 美股分析

```
用户：美股昨天表现怎么样
系统：自动调用 market-intelligence-system → 时间换算 → 返回美股分析
```

**关键词**: `美股`、`道琼斯`、`纳斯达克`

---

### 第三步：配置定时推送（1分钟）

```bash
# 早盘简报（11:35 推送）
hermes cron create "35 11 * * 1-5" \
  --prompt "生成早盘简报" \
  --target weixin

# 收盘简报（15:05 推送）
hermes cron create "5 15 * * 1-5" \
  --prompt "生成收盘简报" \
  --target weixin

# 网格交易监控（交易时间每5分钟）
hermes cron create "*/5 9-11,13-15 * * 1-5" \
  --prompt "执行网格交易检查" \
  --target weixin
```

---

### 第四步：常用问题速查（1分钟）

#### Q1: 如何判断今天是否交易日？

```
用户：今天开市吗
系统：自动调用 stock-data-acquisition → 返回交易日判断
```

---

#### Q2: 如何添加自选股？

```
用户：把贵州茅台加入自选
系统：自动调用 stock-data-acquisition → 添加到自选股列表
```

---

#### Q3: 如何查看历史K线？

```
用户：查看恒生科技ETF最近一个月的K线
系统：自动调用 stock-data-acquisition → 返回历史数据
```

---

#### Q4: 如何评估ST股票的借壳概率？

```
用户：分析一下ST某某的借壳概率
系统：自动调用 stock-analysis-framework → ST专项分析 → 返回概率评估
```

---

#### Q5: 如何暂停网格交易？

```
用户：暂停网格交易
系统：自动调用 grid-trading-system → 暂停交易执行
```

---

## 🚀 进阶使用

### 自动触发关键词

系统会自动识别以下关键词，无需手动调用 Skill：

**A股关键词**:
- `A股`、`上证指数`、`深证成指`、`创业板`
- `财联社`、`东方财富`
- `A股走势`、`A股行情`、`A股分析`

**美股关键词**:
- `美股`、`道琼斯`、`纳斯达克`、`标普500`
- `Fed`、`美联储`、`利率决议`
- `美股走势`、`美股行情`、`美股分析`

**触发后自动执行**:
1. 建立时间锚点
2. 判断市场状态（盘前/盘中/收盘）
3. 获取实时数据
4. 生成分析报告

---

### 协同使用示例

#### 示例 1: 完整的投资决策流程

```
用户：分析一下恒生科技ETF，并判断是否适合网格交易

系统执行流程：
1. [stock-data-acquisition] 获取实时行情
2. [stock-analysis-framework] 技术分析 + 风险评估
3. [grid-trading-system] 计算网格触发位
4. [market-intelligence-system] 整合结果 → 推送
```

---

#### 示例 2: 异常波动应对

```
用户：今天市场大跌，我的网格交易怎么办？

系统执行流程：
1. [market-intelligence-system] 检测异常波动
2. [stock-analysis-framework] 分析下跌原因
3. [grid-trading-system] 查看当前持仓和触发位
4. [market-intelligence-system] 提供应对建议
```

---

## 📚 深入学习

### 阅读顺序推荐

1. **入门** → 本文档（Quick Start）
2. **实战** → `real-world-scenarios.md`（真实案例）
3. **进阶** → `best-practices.md`（最佳实践）
4. **深入** → 各 Skill 的 `SKILL.md`（完整文档）

---

## 🛠️ 故障排查

### 问题 1: 数据获取失败

**现象**: 返回 `None` 或数据源错误

**排查步骤**:
1. 检查网络连接
2. 检查数据源是否限流
3. 查看日志文件：`~/.hermes/grid-trading/grid_trading.log`

---

### 问题 2: 时间锚点错误

**现象**: 美股日期不正确

**排查步骤**:
1. 检查时区配置
2. 确认夏令时/冬令时
3. 手动指定日期：`美股 05-01 收盘情况`

---

### 问题 3: Cronjob 未执行

**现象**: 定时推送未收到

**排查步骤**:
1. 检查 Cronjob 状态：`hermes cron list`
2. 检查是否交易日
3. 检查推送目标配置

---

## 💡 使用技巧

### 技巧 1: 精确指定日期

```
用户：查看美股 2026-05-01 的收盘情况
系统：精确获取指定日期数据
```

---

### 技巧 2: 多市场对比

```
用户：对比美股和A股最近的表现
系统：自动生成对比分析
```

---

### 技巧 3: 组合使用

```
用户：分析恒生科技ETF的技术面，并计算网格交易的触发位
系统：调用多个 Skills 协同工作
```

---

## 📞 获取帮助

- **查看 Skill 文档**: `hermes skill view {skill-name}`
- **查看案例**: `~/.hermes/skills/{skill-name}/examples/real-world-scenarios.md`
- **查看最佳实践**: `~/.hermes/skills/finance/darwin-stock-skills-consolidation/references/best-practices.md`
- **查看 FAQ**: `~/.hermes/skills/finance/darwin-stock-skills-consolidation/references/faq.md`

---

## 总结

通过本快速入门指南，您已经掌握了：

- ✅ 四大核心 Skills 的基本功能
- ✅ 常用命令和关键词
- ✅ 定时推送配置
- ✅ 常见问题解决
- ✅ 进阶使用技巧

现在可以开始使用四大核心 Skills 进行股票分析和交易了！
