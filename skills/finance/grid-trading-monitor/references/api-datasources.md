# 免费股票行情API完整参考

> 更新时间：2026-04-30
> 用途：网格交易监控系统数据源

## 当前集成状态

| 数据源 | 优先级 | 状态 | 特点 |
|--------|--------|------|------|
| 新浪财经 API | P0 | ✅ 已集成 | 最稳定，实时性最好 |
| 腾讯财经 API | P1 | ✅ 已集成 | 港股ETF支持优秀 |
| 东方财富 API | P2 | ✅ 已集成 | 数据全面，但连接不稳定 |
| 网易财经 API | P3 | ✅ 已集成 | 最后备用，可靠性一般 |

---

## 详细API调用方式

### 1. 新浪财经 API（首选）

**接口地址：**
```bash
https://hq.sinajs.cn/list=sh{code}
```

**示例请求：**
```bash
curl "https://hq.sinajs.cn/list=sh513130" \
  -H "Referer: https://finance.sina.com.cn"
```

**返回格式：**
```javascript
var hq_str_sh513130="恒生科技ETF,0.613,0.616,0.611,0.610,0.612,0.611,0.612,2345678,12345678,..."
```

**Python解析：**
```python
def parse_sina(data: str, etf_code: str) -> float:
    """解析新浪财经API返回数据"""
    resp.encoding = 'gbk'
    
    if '=' in data and '"' in data:
        content = data.split('"')[1]
        parts = content.split(',')
        
        if len(parts) > 3:
            # parts[0]=名称, [1]=开盘, [2]=昨收, [3]=当前价
            price = float(parts[3])
            if 0.1 < price < 10:  # ETF价格范围验证
                return round(price, 4)
    return None
```

**字段说明：**
- `parts[0]` = 名称
- `parts[1]` = 开盘价
- `parts[2]` = 昨收价
- `parts[3]` = 当前价 ⭐
- `parts[4]` = 最高价
- `parts[5]` = 最低价

**注意事项：**
- ⚠️ 必须添加 `Referer: https://finance.sina.com.cn` 头
- ⚠️ 返回编码为 GBK，需要 `resp.encoding = 'gbk'`
- ✅ 完全免费，无需注册
- ✅ 实时性最好（盘中实时）

---

### 2. 腾讯财经 API（港股支持优秀）

**接口地址：**
```bash
https://qt.gtimg.cn/q=sh{code}
```

**示例请求：**
```bash
curl "https://qt.gtimg.cn/q=sh513130"
```

**返回格式：**
```javascript
v_sh513130="1~恒生科技ETF~513130~0.611~0.613~0.616~0.610~..."
```

**Python解析：**
```python
import re

def parse_tencent(data: str) -> float:
    """解析腾讯财经API返回数据"""
    resp.encoding = 'gbk'
    
    # 使用正则提取引号内的内容
    if 'v_sh' in data and '~' in data:
        match = re.search(r'v_sh\d+="([^"]+)"', data)
        if match:
            parts = match.group(1).split('~')
            if len(parts) > 3:
                price = float(parts[3])  # 当前价
                if 0.1 < price < 10:
                    return round(price, 4)
    return None
```

**字段说明（按 `~` 分隔）：**
- `parts[1]` = 名称
- `parts[2]` = 代码
- `parts[3]` = 当前价 ⭐
- `parts[4]` = 昨收价
- `parts[5]` = 最高价
- `parts[6]` = 最低价

**优点：**
- ✅ 港股ETF支持优秀
- ✅ 完全免费，无需注册
- ✅ 实时性好，响应快（~120ms）

**⚠️ 常见错误：**
- ❌ 错误URL：`https://web.sqt.gtimg.cn/q=r_sh{etf_code}`（返回 `v_pv_none_match`）
- ✅ 正确URL：`https://qt.gtimg.cn/q=sh{etf_code}`
- ❌ 错误解析：`parts = data.split('~')`（无法提取引号内容）
- ✅ 正确解析：使用正则提取 `v_sh\d+="([^"]+)"`

---

### 3. 东方财富 API（第三备用）

**接口地址：**
```bash
https://push2.eastmoney.com/api/qt/stock/get?secid=1.{code}&fields=f43,f44,f45,f46
```

**示例请求：**
```bash
curl "https://push2.eastmoney.com/api/qt/stock/get?secid=1.513130&fields=f43,f44,f45,f46"
```

**返回格式：**
```json
{
  "data": {
    "f43": 611,  // 当前价 * 1000
    "f44": 613,  // 最高价 * 1000
    "f45": 610,  // 最低价 * 1000
    "f46": 612   // 昨收价 * 1000
  }
}
```

**Python解析：**
```python
def parse_eastmoney(data: dict) -> float:
    """解析东方财富API返回数据"""
    if data.get("data") and data["data"].get("f43"):
        # f43 是价格 * 1000，不是 * 100
        price = float(data["data"]["f43"]) / 1000
        if 0.1 < price < 10:
            return round(price, 4)
    return None
```

**注意事项：**
- ⚠️ **f43 字段 = 价格 × 1000**，不是 × 100
- ⚠️ 连接不稳定，经常超时（timeout建议10秒）
- ✅ JSON格式，易于解析
- ✅ 支持多市场（A股、港股、美股）

**常见错误：**
```python
# ❌ 错误：除以100
price = f43 / 100  # 得到 6.15（错误）

# ✅ 正确：除以1000
price = f43 / 1000  # 得到 0.615（正确）
```

---

### 4. 网易财经 API（最后兜底）

**接口地址：**
```bash
http://api.money.126.net/data/feed/{code}money.fund
```

**示例请求：**
```bash
curl "http://api.money.126.net/data/feed/513130money.fund"
```

**返回格式：**
```javascript
_ntes_quote_callback({"513130":{"price":0.611,"percent":0.0049,...}})
```

**Python解析：**
```python
import re

def parse_netease(data: str) -> float:
    """解析网易财经API返回数据（JSONP格式）"""
    # 正则提取price字段
    match = re.search(r'"price"\s*:\s*([0-9.]+)', data)
    if match:
        price = float(match.group(1))
        if 0.1 < price < 10:
            return round(price, 4)
    return None
```

**优点：**
- ✅ 完全免费
- ✅ JSONP格式，前端可用

**缺点：**
- ⚠️ 可靠性一般
- ⚠️ 需要正则提取

---

## 多数据源自动切换实现

```python
def get_price_api(self) -> float:
    """从多个数据源获取实时价格（按优先级依次尝试）"""
    etf_code = self.config["etf_code"]
    
    # 数据源1：新浪财经 API（最稳定）
    try:
        url = f"https://hq.sinajs.cn/list=sh{etf_code}"
        headers = {"Referer": "https://finance.sina.com.cn"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'gbk'
        data = resp.text
        
        if '=' in data and '"' in data:
            content = data.split('"')[1]
            parts = content.split(',')
            
            if len(parts) > 3:
                price = float(parts[3])
                if 0.1 < price < 10:
                    logger.debug(f"新浪API获取成功: {price}")
                    return round(price, 4)
                    
    except Exception as e:
        logger.warning(f"新浪API获取价格失败: {e}")
    
    # 数据源2：腾讯财经 API
    try:
        url = f"https://web.sqt.gtimg.cn/q=r_sh{etf_code}"
        resp = requests.get(url, timeout=10)
        resp.encoding = 'gbk'
        data = resp.text
        
        if '~' in data:
            parts = data.split('~')
            if len(parts) > 4:
                price = float(parts[3])
                if 0.1 < price < 10:
                    logger.debug(f"腾讯API获取成功: {price}")
                    return round(price, 4)
                    
    except Exception as e:
        logger.warning(f"腾讯API获取价格失败: {e}")
    
    # 数据源3：东方财富 API
    try:
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "secid": f"1.{etf_code}",
            "ut": "fa5fd1943c73445f94f2bfe8de5bf8e4",
            "fields": "f43,f44,f45,f46,f47,f48,f169,f170"
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get("data") and data["data"].get("f43"):
            price = float(data["data"]["f43"]) / 1000
            if 0.1 < price < 10:
                logger.debug(f"东方财富API获取成功: {price}")
                return round(price, 4)
                
    except Exception as e:
        logger.warning(f"东方财富API获取价格失败: {e}")
    
    # 数据源4：网易财经 API
    try:
        url = f"http://api.money.126.net/data/feed/{etf_code}money.fund"
        resp = requests.get(url, timeout=10)
        data = resp.text
        
        import re
        match = re.search(r'"price"\s*:\s*([0-9.]+)', data)
        if match:
            price = float(match.group(1))
            if 0.1 < price < 10:
                logger.debug(f"网易API获取成功: {price}")
                return round(price, 4)
                
    except Exception as e:
        logger.warning(f"网易API获取价格失败: {e}")
    
    return None
```

---

## 注意事项

### 1. 时间锚定原则

**A股交易时间：**
```
上午: 09:30 - 11:30  ✓
下午: 13:00 - 15:00  ✓

午休: 11:30 - 13:00  ✗（不监控）
收盘: 15:00 - 09:30  ✗（不监控）
```

**获取数据前必须确认：**
- 当前是否在交易时段
- 获取的是实时价格还是收盘价
- 数据的时间戳是否正确

### 2. 价格验证

**必须验证：**
- 价格范围合理（ETF一般在 0.1-10 元之间）
- 不为 0 或负数
- 与昨收价偏差不超过 10%（防止异常数据）

```python
def validate_price(price: float, yesterday_close: float) -> bool:
    """验证价格合理性"""
    if not (0.1 < price < 10):
        return False
    
    # 涨跌幅不超过10%（ETF涨跌停限制）
    change_pct = abs(price - yesterday_close) / yesterday_close
    if change_pct > 0.10:
        return False
    
    return True
```

### 3. 错误处理

**必须处理：**
- 网络超时（设置 `timeout=10`）
- 数据解析失败（try-except）
- 数据源切换（多数据源冗余）
- 日志记录（logger.warning/debug）

### 4. 调用频率

**建议：**
- 网格交易监控：每 5 分钟一次
- 实时盯盘：每 1 分钟一次
- ⚠️ 避免高频调用（可能被限流）

---

## 其他可选API（未集成）

### 5. AkShare（开源库）

**GitHub：** https://github.com/akfamily/akshare

**安装：**
```bash
pip install akshare
```

**示例：**
```python
import akshare as ak

# 获取实时行情
df = ak.stock_zh_a_spot_em()
price = df[df['代码'] == '513130']['最新价'].values[0]
```

**优点：**
- ✅ 开源免费
- ✅ 支持A股/港股/美股/期货/加密货币
- ✅ 数据源聚合（新浪、东方财富、腾讯）

**缺点：**
- ⚠️ 需要安装Python库
- ⚠️ 依赖第三方数据源
- ⚠️ 可能在高频率调用时被限流

---

### 6. easyquotation（开源项目）

**GitHub：** https://github.com/shidenggui/easyquotation

**安装：**
```bash
pip install easyquotation
```

**示例：**
```python
import easyquotation

# 新浪数据源
quotation = easyquotation.use('sina')
data = quotation.real(['513130'], prefix=True)
price = data['513130']['now']
```

**优点：**
- ✅ 开源免费
- ✅ 支持新浪/腾讯/集思录
- ✅ 简单易用
- ✅ 社区活跃

---

## 数据源选择建议

### 个人使用场景（网格交易监控）

**推荐组合：**
```
新浪财经（主） → 腾讯财经（备） → 东方财富（备） → 网易财经（最后）
```

**理由：**
1. **实时性**：新浪、腾讯都是盘中实时数据
2. **稳定性**：大厂维护，可靠性高
3. **免费**：无需注册，无调用限制
4. **简单**：HTTP接口，无需安装SDK

### 量化研究场景

**推荐：** AkShare + Tushare

**理由：**
- 数据全面（历史数据、财务数据、技术指标）
- 开源免费
- 社区活跃，文档齐全

### 高频交易场景

**推荐：** 券商Level-2 API 或 必盈API

**理由：**
- 毫秒级延迟
- 盘口深度数据
- 稳定性保证

---

## 参考链接

- [新浪财经](https://finance.sina.com.cn/)
- [腾讯财经](https://finance.qq.com/)
- [东方财富](https://www.eastmoney.com/)
- [AkShare GitHub](https://github.com/akfamily/akshare)
- [easyquotation GitHub](https://github.com/shidenggui/easyquotation)

---

## 更新日志

- **2026-04-30**：新增腾讯财经、网易财经API，形成四重数据源冗余
- **2026-04-29**：修正东方财富API获取净值问题，改用新浪财经API
- **2026-04-28**：初始版本，使用东方财富API
