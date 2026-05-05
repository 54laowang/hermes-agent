---
name: a-share-trading-calendar
description: A股交易日判断 - 判断指定日期是否为A股交易日，排除周末和法定节假日
priority: P0
triggers:
  - 定时任务需要判断交易日
  - 用户询问是否交易日
auto_load: false
---

# A股交易日历

## 核心功能

判断指定日期是否为 A 股交易日，排除周末和法定节假日。

## 交易日判断规则

### 1. 基本规则

```
周一至周五 = 正常交易日
周六、周日 = 休市
```

### 2. 法定节假日（2026年）

| 节日 | 休市日期 | 复市日期 |
|------|---------|---------|
| **元旦** | 1月1日 | 1月2日 |
| **春节** | 1月28日-2月4日 | 2月5日 |
| **清明** | 4月4日-6日 | 4月7日 |
| **劳动节** | 5月1日-5日 | 5月6日 |
| **端午节** | 5月31日-6月2日 | 6月3日 |
| **中秋节** | 10月3日-5日 | 10月6日 |
| **国庆节** | 10月1日-7日 | 10月8日 |

### 3. 调休上班日

**注意**：部分周末可能因调休而成为交易日

例如：
- 春节前后的调休
- 国庆前后的调休

**判断方法**：
- 查询交易所公告
- 检查官方交易日历

## 判断逻辑（伪代码）

```python
def is_trading_day(date):
    # 1. 检查是否为周末
    if date.weekday() in [5, 6]:  # 周六、周日
        # 检查是否为调休上班日
        if is_adjusted_workday(date):
            return True
        return False
    
    # 2. 检查是否为法定节假日
    holidays = get_holidays(date.year)
    if date in holidays:
        return False
    
    # 3. 默认为交易日
    return True
```

## 2026年完整交易日历（重要日期）

### 1月
- 休市：1月1日（元旦）
- 休市：1月28日-2月4日（春节）
- 交易日：约20天

### 2月
- 休市：1日-4日（春节延续）
- 复市：2月5日
- 交易日：约17天

### 4月
- 休市：4月4日-6日（清明）
- 复市：4月7日
- 交易日：约20天

### 5月
- 休市：5月1日-5日（劳动节）⭐ 当前
- 复市：5月6日
- 休市：5月31日（端午节）
- 交易日：约19天

### 6月
- 休市：6月1日-2日（端午延续）
- 复市：6月3日
- 交易日：约21天

### 10月
- 休市：10月1日-7日（国庆+中秋）
- 复市：10月8日
- 交易日：约18天

## 在定时任务中的应用

### 示例1：早盘简报

```
1. 获取当前日期
2. 判断是否为交易日
3. 非交易日 → 输出"今日休市"并结束
4. 交易日 → 继续执行数据收集
```

### 示例2：周一消息面简报

```
1. 获取本周一日期
2. 判断是否为交易日
3. 如本周一休市 → 判断本周是否有其他交易日
4. 如本周全部休市 → 输出"本周休市"并结束
```

## 数据源

**官方交易日历**：
- 上交所：http://www.sse.com.cn/
- 深交所：http://www.szse.cn/

**第三方数据**：
- Tushare：`trade_cal()` 接口
- AkShare：`tool_trade_date_hist_sina()`

## 动态交易日历查询

### 方法 1：Tushare API（推荐）

```python
import tushare as ts

def is_trading_day(date_str):
    """
    判断指定日期是否为交易日
    
    Args:
        date_str: 日期字符串，格式 'YYYY-MM-DD'
    
    Returns:
        bool: True=交易日, False=休市
    """
    pro = ts.pro_api()
    
    # 查询该日期前后的交易日历
    df = pro.trade_cal(
        exchange='SSE',  # 上交所
        start_date=date_str.replace('-', ''),
        end_date=date_str.replace('-', '')
    )
    
    if len(df) == 0:
        return False
    
    return df.iloc[0]['is_open'] == '1'

def get_next_trading_day(date_str):
    """获取下一个交易日"""
    pro = ts.pro_api()
    
    df = pro.trade_cal(
        exchange='SSE',
        start_date=date_str.replace('-', ''),
        end_date=(datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y%m%d'),
        is_open='1'
    )
    
    if len(df) > 0:
        return df.iloc[0]['cal_date']
    return None
```

### 方法 2：AkShare（免费，无需 Token）

```python
import akshare as ak
from datetime import datetime

def is_trading_day_akshare(date_str):
    """
    使用 AkShare 判断交易日
    
    Args:
        date_str: 日期字符串，格式 'YYYY-MM-DD'
    
    Returns:
        bool: True=交易日, False=休市
    """
    # 获取历史交易日历
    df = ak.tool_trade_date_hist_sina()
    
    # 转换日期格式
    trade_dates = df['trade_date'].dt.strftime('%Y-%m-%d').tolist()
    
    return date_str in trade_dates
```

### 在定时任务中的应用

```python
# 步骤 1: 判断交易日
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

if not is_trading_day(today):
    # 输出休市信息
    next_trade = get_next_trading_day(today)
    print(f"今日休市，下一交易日：{next_trade}")
    return

# 步骤 2: 继续执行简报逻辑
print(f"今日为交易日，开始收集数据...")
```

## 已知陷阱

### ⚠️ 调休日判断错误
- **表现**：误将调休上班的周末判断为休市
- **原因**：未检查调休公告
- **解决**：查询交易所官方公告，或使用 AkShare 动态查询

### ⚠️ 节假日日期变化
- **表现**：使用固定日期判断，忽略了节假日变动
- **原因**：每年节假日日期可能不同
- **解决**：动态查询当年节假日安排，或更新硬编码列表

### ⚠️ Tushare Token 失效
- **表现**：调用 `trade_cal()` 返回"您的token不对"
- **原因**：Token 过期或权限不足
- **解决**：使用 AkShare（免费，无需 Token）作为首选方案

### ⚠️ AkShare 数据格式
- **表现**：`df['trade_date'].dt.strftime()` 报错 "Can only use .dt accessor with datetimelike values"
- **原因**：AkShare 返回的是字符串而非 datetime 类型
- **解决**：使用 `.astype(str).tolist()` 直接转换

## 可执行脚本

**`scripts/is_trading_day.py`** - 交易日判断脚本

```bash
# 判断今天是否为交易日
python3 ~/.hermes/skills/finance/a-share-trading-calendar/scripts/is_trading_day.py

# 判断指定日期
python3 ~/.hermes/skills/finance/a-share-trading-calendar/scripts/is_trading_day.py --date 2026-05-06

# 显示下一交易日
python3 ~/.hermes/skills/finance/a-share-trading-calendar/scripts/is_trading_day.py --next
```

**退出码**：0 = 交易日，1 = 休市

**输出**：日期、状态、原因、下一交易日（休市时）

## 相关技能

- `time-anchor-constitution` - 时间锚定宪法
- `daily-market-brief` - 每日市场简报
- `a-share-market-analysis` - A股市场分析
