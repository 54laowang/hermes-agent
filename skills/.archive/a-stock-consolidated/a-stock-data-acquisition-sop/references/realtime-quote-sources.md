# A股实时行情数据源

## 个股实时行情（推荐方案）

### P0级（首选 - API接口）

**腾讯财经API**
```
URL: https://qt.gtimg.cn/q=sz{股票代码}
示例: https://qt.gtimg.cn/q=sz300586
返回: v_sz300586="51~美联新材~300586~当前价~昨收~今开~..."
解析: 用~分隔，第4字段=当前价，第31字段=涨跌额，第32字段=涨跌幅
```
**优势**：API接口、数据完整、可程序化调用、延迟低

### P1级（次选 - 网页访问）

**新浪财经实时行情**
```
URL: https://finance.sina.com.cn/realstock/company/sz{股票代码}/nc.shtml
示例: https://finance.sina.com.cn/realstock/company/sz300586/nc.shtml
```
**优势**：明确显示11:30午盘收盘时间

**腾讯财经网页**
```
URL: https://gu.qq.com/sz{股票代码}
示例: https://gu.qq.com/sz300586
```
**优势**：界面清晰、五档盘口详细

**同花顺**
```
URL: https://stockpage.10jqka.com.cn/{股票代码}/
示例: https://stockpage.10jqka.com.cn/300586/
```
**优势**：成交明细显示11:30收盘价

## 大盘行情

**P0级（首选）：**
- 财联社盘面直播：https://www.cls.cn/subject/1103
- 东方财富网：https://stock.eastmoney.com/

## 注意事项

1. 东方财富个股页午间休盘时显示"-"，无法获取实时价
2. 新浪API（hq.sinajs.cn）可能返回Forbidden，建议使用腾讯API
3. 网易财经可能返回502错误，不推荐使用
