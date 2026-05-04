# API数据源评估会话记录 - 2026-04-30

## 会话概述

**时间：** 2026-04-30 10:32-10:59
**目标：** 为网格交易监控系统添加备用数据源
**结果：** 发现网易财经API已失效，测试iTick和AkShare，更新数据源架构

---

## iTick API 测试发现

### 关键发现：基金API vs 股票API的区别

**最初问题：**
- 用户提供了iTick API Key
- 文档说支持ETF
- 但股票API测试A股ETF返回null

**深入测试：**
```python
# 测试1：股票API（/stock/quote）
# 结果：A股主板成功，ETF失败
600519 (贵州茅台): ✅ 1401.17元
513130 (恒生科技ETF): ❌ 返回null

# 测试2：基金API（/fund/quote）
# 结果：美股ETF成功，A股ETF失败
QQQ (纳斯达克100 ETF): ✅ $657.55
SPY (标普500 ETF): ✅ $711.69
513130 (恒生科技ETF): ❌ 返回null
```

**结论：**
1. iTick有两个不同的API端点
2. 股票API：支持主板股票，不支持任何ETF
3. 基金API：支持美股ETF，不支持A股ETF（免费套餐限制）
4. 免费套餐对A股ETF完全不支持

**保存价值：**
- 可用于监控美股ETF（QQQ、SPY）
- 可用于监控主板股票（贵州茅台、腾讯控股）
- 不适用于当前恒生科技ETF网格交易

---

## AkShare 测试结果

### 安装与测试

```bash
# 安装
python3 -m pip install akshare

# 测试
python3 -c "import akshare as ak; df = ak.fund_etf_spot_em(); print(len(df))"
# 输出：1446 (全市场ETF数量)
```

### 实时行情测试

```python
import akshare as ak
import time

start = time.time()
df = ak.fund_etf_spot_em()  # 获取全市场ETF
elapsed = (time.time() - start) * 1000

print(f"响应时间: {elapsed:.0f}ms")  # 输出：17137ms
print(f"ETF总数: {len(df)}")  # 输出：1446

# 查找恒生科技ETF
etf_data = df[df['代码'] == '513130']
print(f"价格: {etf_data['最新价'].values[0]}元")  # 输出：0.611元
print(f"涨跌: {etf_data['涨跌幅'].values[0]}%")  # 输出：-0.81%
```

**优点：**
- ✅ 完全免费，无需API Key
- ✅ 支持A股ETF
- ✅ 数据全面（1446只ETF）
- ✅ 开源社区维护

**缺点：**
- ⚠️ 响应慢（17秒获取全市场）
- ⚠️ 不适合高频调用
- ⚠️ 历史K线接口连接失败

**适用场景：**
- ✅ 低频监控（每5-10分钟）
- ✅ 批量获取
- ✅ 最后兜底

---

## 网易财经 API 失效确认

### 测试记录

**第一次测试（10:33）：**
```
状态: ❌ 失败
错误: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**第二次测试（10:55）：**
```
状态: ❌ 失败
错误: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**结论：** 网易财经API已不可用，需要从系统中移除

**历史信息：**
```
接口地址: http://api.money.126.net/data/feed/{code}money.fund
最后可用时间: 未知
失效时间: 2026-04-30之前
```

---

## 系统更新决策

### 数据源架构变更

**变更前：**
```
1. 新浪财经（主）
2. 腾讯财经（备）
3. 东方财富（备）
4. 网易财经（兜底）← 已失效
```

**变更后：**
```
1. 新浪财经（主）— 129ms，最稳定
2. 腾讯财经（备）— 121ms，港股支持好
3. 东方财富（备）— 271ms，数据全面
4. AkShare（兜底）— 17秒，响应慢但数据全面
```

### 移除网易财经的理由

1. **连续测试失败** - 两次测试均连接失败
2. **API已失效** - 可能已停止服务
3. **减少无效请求** - 提升系统性能
4. **代码简化** - 移除无效代码

### 添加AkShare的理由

1. **支持A股ETF** - 与当前监控目标匹配
2. **完全免费** - 无需注册和API Key
3. **数据全面** - 1446只ETF覆盖全市场
4. **开源可靠** - 社区维护，文档齐全

---

## 性能对比分析

### 响应时间对比

| 数据源 | 响应时间 | 相对速度 | 适用场景 |
|--------|---------|---------|---------|
| 腾讯财经 | 121ms | 基准（最快） | 高频监控 |
| 新浪财经 | 129ms | +6.6% | 高频监控 |
| 东方财富 | 271ms | +124% | 中频监控 |
| AkShare | 17,137ms | +140倍 | 低频备用 |

### 价格一致性

**测试结果：**
```
新浪财经: 0.6110元
腾讯财经: 0.6110元
东方财富: 0.6110元

最大差异: 0.0000元
结论: ✅ 高度一致
```

### 成功率

```
测试时间: 2026-04-30 10:55
成功率: 75% (3/4)
失败数据源: 网易财经
```

---

## iTick API 配置保存

### 保存原因

虽然iTick不支持A股ETF，但仍保存配置用于：
1. 未来监控美股ETF（QQQ、SPY）
2. 监控主板股票（贵州茅台、腾讯控股）
3. 数据对比验证

### 配置文件

**位置：** `~/.hermes/grid-trading/data_sources/itick_config.json`

**内容：**
```json
{
  "api_key": "3c7c24590420419b9457...",
  "base_url": {
    "free": "https://api-free.itick.io",
    "production": "https://api.itick.io"
  },
  "api_endpoints": {
    "stock": "/stock/quote",
    "fund": "/fund/quote",
    "kline": "/stock/kline"
  },
  "test_results": {
    "stock_api": {
      "600519": {"name": "贵州茅台", "price": 1401.17, "status": "success"},
      "513130": {"name": "恒生科技ETF", "status": "failed"}
    },
    "fund_api": {
      "QQQ": {"name": "纳斯达克100 ETF", "price": 657.55, "status": "success"},
      "513130": {"name": "恒生科技ETF", "status": "failed"}
    }
  }
}
```

### 示例脚本

**位置：** `~/.hermes/grid-trading/data_sources/itick_example.py`

**功能：**
- 股票API使用示例（主板股票）
- 基金API使用示例（美股ETF）
- 完整的错误处理

---

## 测试方法论总结

### 1. 多数据源对比测试

**方法：**
```python
# 同时测试多个数据源
data_sources = {
    "新浪": get_price_sina,
    "腾讯": get_price_tencent,
    "东方财富": get_price_eastmoney,
}

results = {}
for name, func in data_sources.items():
    start = time.time()
    price = func(etf_code)
    elapsed = (time.time() - start) * 1000
    results[name] = {"price": price, "elapsed_ms": elapsed}

# 对比价格一致性
prices = [r["price"] for r in results.values() if r["price"]]
max_diff = max(prices) - min(prices)
```

### 2. API文档验证

**关键步骤：**
1. 查看官方文档（用户提供的链接）
2. 测试文档中的示例代码
3. 验证返回格式
4. 测试不同的参数组合

**iTick案例：**
- 文档说支持ETF
- 实测发现需要区分股票API和基金API
- 基金API支持美股ETF但不支持A股ETF
- 免费套餐有数据类型限制

### 3. 失败原因排查

**网易财经案例：**
```
第一次失败: 10:33
第二次失败: 10:55
连续失败: 确认API已失效
决策: 从系统中移除
```

### 4. 适用场景判断

**AkShare案例：**
```
响应时间: 17秒
评估: 太慢，不适合高频监控
决策: 作为最后兜底使用
```

---

## 经验教训

### 1. API文档可能不准确或过时

**案例：** iTick文档说支持ETF，但没说明免费套餐的限制
**教训：** 必须实际测试，不能只看文档

### 2. 同一服务商的不同API可能功能完全不同

**案例：** iTick的股票API和基金API支持的数据类型完全不同
**教训：** 需要测试所有相关API端点

### 3. 免费套餐可能有隐藏限制

**案例：** iTick免费套餐不支持A股ETF
**教训：** 测试目标市场的实际数据类型

### 4. 响应时间是重要指标

**案例：** AkShare响应17秒，不适合高频监控
**教训：** 性能测试是评估的重要环节

### 5. 多重冗余的价值

**案例：** 网易财经失效，但系统仍有三个数据源正常工作
**教训：** 多重冗余确保系统稳定性

---

## 文件更新记录

### 更新的文件

1. `~/.hermes/grid-trading/grid_monitor.py`
   - 移除网易财经API
   - 添加AkShare作为数据源4

2. `~/.hermes/grid-trading/API_数据源列表.md`
   - 标记网易财经已失效
   - 更新AkShare测试结果
   - 更新iTick API文档

3. `~/.hermes/grid-trading/data_sources/itick_config.json`
   - 保存API Key
   - 记录测试结果
   - 区分股票API和基金API

4. `~/.hermes/grid-trading/data_sources/itick_example.py`
   - 创建使用示例
   - 包含股票和基金API

5. `~/.hermes/grid-trading/data_sources/akshare_example.py`
   - 创建AkShare使用示例

### 创建的测试报告

- `~/.hermes/grid-trading/测试报告_20260430.md`

---

## 后续行动建议

### 1. 定期数据源健康检查

**建议频率：** 每月一次
**检查内容：**
- 所有数据源的连接状态
- 响应时间变化
- 价格一致性
- API变更通知

### 2. 性能监控

**监控指标：**
- 各数据源响应时间趋势
- 成功率变化
- 错误类型分布

### 3. 新数据源探索

**备选方案：**
- easyquotation（开源库）
- 必盈API（商业方案，有免费额度）
- Tushare（需要积分）

---

**会话总结：** 本次会话成功完成了数据源架构的优化，移除了失效的网易财经API，添加了AkShare作为第四重兜底保障，深入测试了iTick API并发现了股票API与基金API的关键区别，建立了系统化的API评估方法论。系统现在拥有四重冗余（新浪/腾讯/东方财富/AkShare），成功率达75%，价格完全一致，响应时间优秀。
