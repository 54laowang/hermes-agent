---
name: grid-trading-monitor
description: |
  ETF 网格交易监控系统 - 配置网格参数、实时行情获取、定时监控、微信推送提醒
  
  Use when: 网格交易, grid trading, ETF监控, 量化监控, 恒生科技, 513130, 网格策略, 定投监控, grid, 交易提醒.
  
  Do NOT use for:
  - 实时交易执行（仅监控提醒）
  - 其他策略类型（如定投、趋势跟踪）
  - 个股分析（仅支持 ETF）
  - 高频交易（不适合秒级监控）
  - 资金管理或仓位计算
version: 1.1.0
category: finance
keywords:
  - 网格交易
  - grid trading
  - ETF监控
  - 量化交易
  - 自动化监控
triggers:
  - 网格交易
  - grid trading
  - ETF监控
  - 量化监控
  - 恒生科技
  - 513130
  - 网格策略
  - 定投监控
---

# ETF 网格交易监控助手

## 概述

在 Hermes 中搭建 ETF 网格交易监控系统，实现：
- 网格参数配置（基准价、间距、格数、金额）
- 实时行情获取（东方财富接口）
- 定时监控（Cronjob）
- 触发时微信推送提醒

## 快速搭建

### 1. 创建目录和配置

```bash
mkdir -p ~/.hermes/grid-trading
```

创建 `~/.hermes/grid-trading/config.json`：
```json
{
  "etf_code": "513130",
  "etf_name": "恒生科技ETF",
  "grid_center": 0.625,
  "grid_spacing": 0.025,
  "grid_count_up": 6,
  "grid_count_down": 8,
  "per_grid_amount": 715,
  "initial_grids": 3,
  "total_capital": 10000
}
```

### 2. 配置参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| etf_code | ETF 代码 | 513130 |
| etf_name | ETF 名称 | 恒生科技ETF |
| grid_center | 基准价（元） | 0.625 |
| grid_spacing | 网格间距（元） | 0.025 |
| grid_count_up | 上方卖出格数 | 6 |
| grid_count_down | 下方买入格数 | 8 |
| per_grid_amount | 每格金额（元） | 5000 |
| initial_grids | 初始持仓格数 | 3 |

### 3. 监控脚本

核心脚本 `grid_monitor.py` 应包含：
- 价格获取：东方财富 API（f43 字段 / 1000）
- 网格触发检测
- 状态持久化
- JSON 输出（用于 cronjob 解析）

### 4. 创建 Cronjob

```yaml
name: 网格交易监控-恒生科技ETF
schedule: "*/5 9-11,13-15 * * 1-5"  # 交易时间每5分钟（跳过午休）
prompt: |\n  执行网格交易检查：\n  1. 运行 python ~/.hermes/grid-trading/grid_monitor.py --check\n  2. 如果有 triggered 字段，推送微信提醒\nenabled_toolsets: ["terminal", "send_message"]\n```\n\n**⚠️ Cron 时间表说明：**
- `*/5 9-11,13-15` = 9-11点和13-15点每5分钟\n- 不要用 `*/5 9-15`，这会在 11:30-13:00 午休时也执行

## 常用命令

```bash
# 查看当前状态
python ~/.hermes/grid-trading/grid_monitor.py --status

# 单次检查（JSON 输出）
python ~/.hermes/grid-trading/grid_monitor.py --check

# 启动实时监控
python ~/.hermes/grid-trading/grid_monitor.py --monitor
```

## 行情接口（四重数据源冗余）

**数据源优先级：**
```
1. 新浪财经 API（主） → 最稳定，实时性最好（~129ms）
2. 腾讯财经 API（备） → 港股ETF支持优秀（~121ms）
3. 东方财富 API（备） → 数据全面（~271ms）
4. AkShare（最后） → 响应慢但数据全面（~17秒）
```

**⚠️ 数据源状态（2026-04-30测试）：**
- ✅ 新浪财经：正常（129ms）
- ✅ 腾讯财经：正常（121ms）
- ✅ 东方财富：正常（271ms）
- ✅ AkShare：正常（17秒）
- ❌ 网易财经：已失效（Connection aborted），已从系统移除

### 新浪财经 API（首选）

```python
url = f"https://hq.sinajs.cn/list=sh{etf_code}"
headers = {"Referer": "https://finance.sina.com.cn"}
resp = requests.get(url, headers=headers, timeout=10)
resp.encoding = 'gbk'

# 解析: var hq_str_sh513130="恒生科技ETF,0.613,0.616,0.611,..."
content = data.split('"')[1]
parts = content.split(',')
price = float(parts[3])  # 当前价
```

**优点：** 完全免费、无需注册、实时性最好、稳定性最高

### 腾讯财经 API（备用）

```python
url = f"https://qt.gtimg.cn/q=sh{etf_code}"
resp.encoding = 'gbk'

# 解析: v_sh513130="1~恒生科技ETF~513130~0.611~..."
import re
match = re.search(r'v_sh\d+="([^"]+)"', data)
parts = match.group(1).split('~')
price = float(parts[3])  # 当前价
```

**优点：** 港股ETF支持优秀、实时性好、响应快（~120ms）

**⚠️ 常见错误：**
- ❌ 错误URL：`https://web.sqt.gtimg.cn/q=r_sh{etf_code}`（返回 `v_pv_none_match`）
- ✅ 正确URL：`https://qt.gtimg.cn/q=sh{etf_code}`
- ❌ 错误解析：`parts = data.split('~')`（无法提取引号内容）
- ✅ 正确解析：使用正则提取 `v_sh\d+="([^"]+)"`

### 东方财富 API（第三备用）

```python
url = "https://push2.eastmoney.com/api/qt/stock/get"
params = {"secid": f"1.{etf_code}", "fields": "f43,f44,f45,f46"}
data = requests.get(url, params=params).json()

price = float(data["data"]["f43"]) / 1000  # f43 = 价格 × 1000
```

**缺点：** 连接不稳定，经常超时

### AkShare API（最后兜底）

```python
import akshare as ak

# 获取全市场ETF数据（响应慢，约17秒）
df = ak.fund_etf_spot_em()

# 筛选目标ETF
etf_data = df[df['代码'] == etf_code]
price = float(etf_data['最新价'].values[0])
```

**优点：**
- 完全免费，无需注册和API Key
- 支持A股ETF（恒生科技ETF、沪深300ETF等）
- 数据全面（1446只ETF）
- 开源社区维护

**缺点：**
- 响应较慢（17秒获取全市场数据）
- 不适合高频调用
- 接口稳定性一般

**适用场景：**
- ✅ 低频监控（每5-10分钟一次）
- ✅ 批量获取多只ETF
- ✅ 作为最后兜底数据源
- ❌ 不适合高频交易

**性能优化建议：**
- 批量获取时，一次获取全市场数据，再筛选目标ETF
- 缓存全市场数据，避免重复请求

### 网易财经 API（已失效，已移除）

**状态：** ❌ 已失效
**移除时间：** 2026-04-30
**移除原因：** 连接失败（Connection aborted, RemoteDisconnected）

**历史信息：**
```
接口地址: http://api.money.126.net/data/feed/{code}money.fund
测试结果: 所有测试均失败，API已不可用
```

**替代方案：** AkShare（已添加为数据源4）

**⚠️ 自动切换机制：**
- 单一数据源失败自动切换到下一个
- 所有数据源都失败才返回 None
- 日志记录每次切换（logger.warning）

**完整API文档：** 
- `references/api-datasources.md` — 四重数据源详细调用方式（新浪/腾讯/东方财富/AkShare）
- `references/iTick-api-limitations.md` — iTick API 完整测试报告（⚠️ 股票API不支持ETF，但基金API支持美股ETF）
- `references/api-evaluation-session-20260430.md` — API评估方法论与本次会话完整记录（数据源测试、iTick发现、AkShare集成、网易移除）

### iTick API（补充数据源，用于美股ETF和主板股票）

**⚠️ 关键发现：iTick 有两个不同的 API，ETF支持情况完全不同**

#### 股票 API（`/stock/quote`）

**支持的数据类型：**
- ✅ A股主板股票（贵州茅台 600519、中国平安等）
- ✅ A股指数（上证指数 000001、深证成指等）
- ✅ 港股（腾讯控股 700、美团等）
- ✅ 美股（苹果 AAPL、特斯拉 TSLA等）
- ❌ **任何ETF都不支持**（A股ETF、美股ETF均返回null）

**测试结果：**
| 代码 | 名称 | 价格 | 状态 |
|------|------|------|------|
| 600519 | 贵州茅台 | 1401.17元 | ✅ 成功 |
| 000001 | 上证指数 | 4107.51点 | ✅ 成功 |
| 700 | 腾讯控股 | 478.6港币 | ✅ 成功 |
| 513130 | 恒生科技ETF | - | ❌ 返回null |

#### 基金 API（`/fund/quote`）

**支持的数据类型：**
- ✅ **美股ETF**（纳斯达克100 ETF QQQ、标普500 ETF SPY等）
- ❌ **A股ETF**（恒生科技ETF 513130、沪深300ETF 510300等，免费套餐不支持）

**测试结果：**
| 代码 | 名称 | 价格 | 状态 |
|------|------|------|------|
| QQQ | 纳斯达克100 ETF | $657.55 | ✅ 成功 |
| SPY | 标普500 ETF | $711.69 | ✅ 成功 |
| 513130 | 恒生科技ETF | - | ❌ 返回null |

**使用示例：**
```python
# 获取美股ETF（使用基金API）
url = "https://api.itick.io/fund/quote"
params = {"region": "US", "code": "QQQ"}
headers = {"accept": "application/json", "token": "your_api_key"}
resp = requests.get(url, params=params, headers=headers, timeout=10)
price = resp.json()["data"]["p"]

# 获取主板股票（使用股票API）
url = "https://api.itick.io/stock/quote"
params = {"region": "SH", "code": "600519"}  # 贵州茅台
```

**适用场景：**
- ✅ 监控美股ETF（QQQ、SPY）→ 使用基金API
- ✅ 监控主板股票（贵州茅台、腾讯控股）→ 使用股票API
- ❌ 监控A股ETF（恒生科技ETF、沪深300ETF）→ 免费套餐不支持

**免费套餐限制：**
- 每分钟 5 次调用
- 不支持A股ETF
- 配置文件：`~/.hermes/grid-trading/data_sources/itick_config.json`

## 数据源评估方法论

当需要评估新的数据源API时，采用以下系统性测试方法：

### 1. 基础连接测试

```python
# 测试API是否可达
import requests
import time

def test_api_basic(url, params, headers=None):
    """基础连接测试"""
    start = time.time()
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        elapsed = (time.time() - start) * 1000
        return {
            "success": resp.status_code == 200,
            "status_code": resp.status_code,
            "elapsed_ms": elapsed,
            "data": resp.json() if 'json' in resp.headers.get('content-type', '') else resp.text
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 2. 数据类型支持测试

**测试矩阵：**
| 数据类型 | 测试代码 | 预期结果 |
|---------|---------|---------|
| A股主板 | 600519（贵州茅台） | 成功 |
| A股指数 | 000001（上证指数） | 成功 |
| A股ETF | 513130（恒生科技ETF） | ？待测 |
| 港股 | 700（腾讯控股） | ？待测 |
| 美股ETF | QQQ（纳斯达克100） | ？待测 |

**测试代码：**
```python
test_cases = [
    ("SH", "600519", "A股主板"),
    ("SH", "513130", "A股ETF"),
    ("US", "QQQ", "美股ETF"),
]

for region, code, desc in test_cases:
    result = test_api_basic(url, {"region": region, "code": code})
    print(f"{desc}: {'✅' if result['success'] else '❌'} {result.get('elapsed_ms', 0):.0f}ms")
```

### 3. 响应性能测试

**关键指标：**
- **响应时间**：< 500ms 优秀，< 1000ms 良好，> 5000ms 需考虑备用
- **成功率**：连续10次测试的成功率
- **稳定性**：响应时间标准差

### 4. 价格一致性验证

**测试方法：**
```python
# 对比多个数据源的价格
prices = []
for source_name, source_func in data_sources.items():
    price = source_func(etf_code)
    if price:
        prices.append((source_name, price))

# 计算差异
if len(prices) >= 2:
    max_diff = max(p[1] for p in prices) - min(p[1] for p in prices)
    if max_diff < 0.01:  # 差异小于1分钱
        print("✅ 数据源价格高度一致")
    else:
        print(f"⚠️ 价格差异: {max_diff:.4f}元")
```

### 5. 限制与配额评估

**需要确认：**
- ✅ 是否需要注册/API Key？
- ✅ 免费套餐的调用频率限制？
- ✅ 免费套餐的数据类型限制？
- ✅ 是否需要特定的请求头？

### 6. 文档与记录

**保存测试结果：**
```bash
# 创建测试报告
~/.hermes/grid-trading/data_sources/api_test_report_YYYYMMDD.md

# 记录配置
~/.hermes/grid-trading/data_sources/{api_name}_config.json

# 示例代码
~/.hermes/grid-trading/data_sources/{api_name}_example.py
```

**示例测试报告格式：**
```markdown
# 数据源测试报告

测试时间: 2026-04-30 10:55
ETF代码: 513130 (恒生科技ETF)

## 测试结果

| 数据源 | 价格 | 响应时间 | 状态 |
|--------|------|---------|------|
| 新浪财经 | 0.6110元 | 129ms | ✅ |

## 发现的问题

1. 网易财经API已失效（Connection aborted）
2. iTick免费套餐不支持A股ETF

## 建议

- 移除网易财经
- 添加AkShare作为第四重备用
```

## 交易时间判断

### 交易时段判断

**A股交易时间（监控时段）：**
```
上午: 09:30 - 11:30  ✓
下午: 13:00 - 15:00  ✓

非交易时间（不监控）：
11:30 - 13:00  午休  ✗
15:00 - 09:30  收盘后 ✗
```

### 交易日判断（重要！）

**⚠️ 关键问题：**
- Cron表达式 `*/5 9-11,13-15 * * 1-5` 只排除了周末
- **没有排除法定假期**（五一、国庆、春节等）
- 导致假期也会运行，浪费资源

**解决方案：使用 AkShare 判断交易日**

```python
def is_trading_day(self) -> bool:
    """判断是否是交易日
    
    使用 AkShare 查询交易日历（免费开源）
    排除周末和法定假期
    """
    try:
        import akshare as ak
        today = datetime.now().strftime("%Y%m%d")
        
        # 使用 AkShare 交易日历接口
        df = ak.tool_trade_date_hist_sina()
        
        # 检查今天是否在交易日列表中
        is_open = today in df['trade_date'].astype(str).values
        logger.debug(f"交易日查询: {today} -> {'交易日' if is_open else '非交易日'}")
        return is_open
            
    except Exception as e:
        logger.warning(f"交易日查询失败: {e}，使用简单判断")
        # Fallback: 排除周末
        weekday = datetime.now().weekday()
        return weekday < 5

def is_trading_time(self) -> bool:
    """判断是否交易时间
    
    A股交易时间：
    - 上午: 09:30 - 11:30
    - 下午: 13:00 - 15:00
    
    非交易时间：11:30-13:00 午休
    """
    # 先判断是否交易日
    if not self.is_trading_day():
        return False
    
    # 再判断是否交易时段
    now = datetime.now().strftime("%H:%M")
    morning = "09:25" <= now <= "11:30"
    afternoon = "13:00" <= now <= "15:05"
    return morning or afternoon
```

**在 run_once() 方法中添加交易日判断：**

```python
def run_once(self) -> dict:
    """单次检查（用于 cronjob）"""
    # 先判断是否交易时间（包含交易日判断）
    if not self.is_trading_time():
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"😴 非交易时间，跳过检查: {now}")
        return {
            "error": "非交易时间",
            "is_trading_time": False,
            "timestamp": now
        }
    
    # ... 后续逻辑
```

**测试结果（2026-05-01 五一假期）：**
```
2026-05-01 10:18:38,592 - INFO - 😴 非交易时间，跳过检查: 2026-05-01 10:18:38
{
  "error": "非交易时间",
  "is_trading_time": false,
  "timestamp": "2026-05-01 10:18:38"
}
```

**依赖**：
- AkShare：`pip install akshare`（免费开源）
- 无需API Key，无需注册

**注意事项**：
- AkShare交易日历数据来源于新浪财经
- 包含法定假期的交易日历
- 每次调用会拉取全市场交易日数据，建议缓存

**⚠️ 常见错误：**
- 错误：11:30-13:00 继续监控（午休时间）
- 正确：11:30 截止上午监控，13:00 开始下午监控

## 网格计算

```
买入网格价格 = 基准价 - 间距 × 档位 (档位 1~N)
卖出网格价格 = 基准价 + 间距 × 档位 (档位 1~N)

单格利润率 ≈ 间距 / 基准价
```

## 状态文件

`status.json` 结构：
```json
{
  "holdings": 3,
  "last_price": 0.615,
  "last_trade_grid": null,
  "trade_history": [],
  "grids": [...],
  "updated_at": "2026-04-28T11:36:00"
}
```

## 微信推送格式

触发时发送：
```
📊 恒生科技ETF 网格交易提醒

📉/📈 [买入/卖出] 信号触发

💹 触发价格: X.XXX 元
📊 成交档位: Lv+X
💰 成交金额: 5,000 元
💼 当前持仓: X 格
⏰ 时间: YYYY-MM-DD HH:MM:SS
```

## 风险提示

- 单边上涨会踏空（卖飞）
- 单边下跌会持续补仓
- 需控制总仓位，避免满仓
- 适合震荡市，不适合单边趋势

## 常见问题

### Q: 对话历史丢失怎么办？

如果用户抱怨微信聊天记录不完整，这是 Hermes 的**上下文压缩机制**：
- 默认 `max_context_tokens: 10000`，超过会压缩
- 压缩时移除早期对话，但摘要可能失败导致丢失

**解决方案：**
1. 增大上下文限制（推荐 30000）
2. 重要信息主动保存到 memory/fact_store
3. 临时任务不保存也没关系

### Q: 价格显示异常（如 6.15 而非 0.615）？

这是东方财富API解析错误：
- 东方财富 f43 字段 = 价格 × 1000
- 需要除以 1000，不是 100

**示例：**
```python
# ❌ 错误：除以100
price = f43 / 100  # 得到 6.15（错误）

# ✅ 正确：除以1000
price = f43 / 1000  # 得到 0.615（正确）
```

**推荐：** 优先使用新浪财经API，避免此问题

## 扩展功能

### 多品种监控

复制配置目录，修改 etf_code：
```bash
cp -r ~/.hermes/grid-trading ~/.hermes/grid-trading-512480
# 修改 config.json 中的 etf_code
```

### 动态调整网格

根据波动率自动调整间距：
- 高波动：扩大间距
- 低波动：缩小间距

## 文件结构

```
~/.hermes/grid-trading/
├── config.json          # 网格配置
├── status.json          # 当前状态
├── grid_monitor.py      # 监控脚本
├── grid_trading.log     # 运行日志
└── SKILL.md             # 使用说明
```

---

## Known Gotchas

### 行情数据问题

- **东方财富接口限流**: 频繁请求会被限流
  ```python
  # 添加延时，避免请求过快
  time.sleep(3)  # 每次请求间隔 3 秒
  ```

- **非交易时间无数据**: 盘前盘后可能返回空值
  ```python
  # 检查返回数据有效性
  if not data or 'price' not in data:
      print("非交易时间或数据异常")
      return
  ```

- **数据延迟**: 免费接口有 15 分钟延迟
  ```
  # 不适合实时交易，仅作参考
  ```

### 网格配置陷阱

- **间距过小导致频繁交易**: 手续费吃掉利润
  ```
  ❌ 错误: 间距 0.5%，手续费 0.1%
  ✅ 正确: 间距 ≥ 2%，手续费占比 < 5%
  ```

- **未预留现金**: 下跌时无资金补仓
  ```python
  # 现金比例建议 30-50%
  cash_ratio = total_funds * 0.4  # 预留 40% 现金
  ```

- **格数设置不合理**: 过多或过少都会失效
  ```
  建议: 根据历史波动率设置
  - 低波动 ETF: 10-20 格
  - 高波动 ETF: 20-40 格
  ```

### 监控执行问题

- **Cronjob 未正确设置**: 监控任务未执行
  ```bash
  # 检查 cron 日志
  grep CRON /var/log/syslog | tail -20
  
  # 确保脚本有执行权限
  chmod +x ~/.hermes/grid-trading/grid_monitor.py
  ```

- **微信推送失败**: Token 过期或网络问题
  ```python
  # 添加重试机制
  for i in range(3):
      if send_wechat_message(msg):
          break
      time.sleep(5)
  ```

- **多次触发相同提醒**: 状态未正确更新
  ```python
  # 触发后立即更新状态
  update_status(last_trigger_time=datetime.now())
  ```

### 交易执行风险

- **仅监控不执行**: 仍需人工确认
  ```
  ⚠️ 系统仅推送提醒，不自动下单
  # 避免: 将监控信号直接用于程序化交易
  ```

- **市场剧烈波动**: 网格可能失效
  ```
  # 单边暴涨或暴跌时，网格策略会踏空或套牢
  # 建议: 设置止损线和止盈线
  ```

- **流动性风险**: ETF 成交量不足
  ```
  # 检查 ETF 日成交额
  # 避免: 日成交额 < 1 亿的 ETF
  ```

### 平台限制

- **时区问题**: Cron 使用系统时区
  ```bash
  # 确认系统时区
  timedatectl
  
  # Cron 使用 UTC 时间，需要换算
  # 北京时间 9:30 = UTC 1:30
  ```

- **脚本超时**: 默认 60 秒超时
  ```python
  # 在 Cronjob 配置中增加超时时间
  hermes cron create --timeout 300 ...
  ```
