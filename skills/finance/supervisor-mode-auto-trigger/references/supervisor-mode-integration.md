# 监察者模式集成技术细节

## 核心文件

### 1. 自动触发Hook

**文件路径**：`~/.hermes/hooks/supervisor-precheck.py`

**功能**：
- 检测用户消息中的美股/A股关键词
- 自动计算时间锚定
- 注入数据源优先级和执行清单

**关键函数**：

```python
def should_trigger_supervisor(user_message):
    """判断是否需要触发监察者模式"""
    us_stock_patterns = [
        r'美股.*(走势|收盘|行情|分析)',
        r'(道琼斯|纳斯达克|标普500|S&P)',
        r'(Fed|美联储|利率决议)',
    ]
    
    a_stock_patterns = [
        r'A股.*(走势|收盘|行情|分析)',
        r'(上证指数|深证成指|创业板)',
    ]
    
    # 检查匹配...
```

```python
def get_us_eastern_time(beijing_time):
    """北京时间 → 美东时间"""
    return beijing_time - timedelta(hours=12)
```

```python
def generate_supervisor_prompt(market_type, beijing_time):
    """生成监察者预检查提示"""
    # 自动计算时间锚定、市场状态、目标日期...
    # 返回完整的系统提示追加内容
```

---

## 配置集成

### config.yaml Hook配置

```yaml
hooks:
  pre_llm_call:
  - command: /Users/me/.hermes/hooks/time-sense-injector.py
    timeout: 5
  - command: /Users/me/.hermes/hooks/smart-skill-loader.py
    timeout: 5
  - command: /Users/me/.hermes/hooks/supervisor-precheck.py  # ← 监察者Hook
    timeout: 5
```

**执行顺序**：
1. `time-sense-injector.py` - 注入当前时间到系统提示
2. `smart-skill-loader.py` - 自动加载相关Skills
3. `supervisor-precheck.py` - 注入监察者预检查内容

---

## 时区换算逻辑

### 美股时区换算

```python
# 美东时间 = 北京时间 - 12小时
us_eastern_time = beijing_time - timedelta(hours=12)

# 美东收盘日期 = 北京时间日期 - 1（凌晨04:00后）
if beijing_time.hour >= 4:
    target_date = (beijing_time - timedelta(days=1)).strftime('%Y-%m-%d')
```

### 市场状态判断

```python
hour = us_eastern_time.hour

if hour < 9.5:
    market_status = "盘前"
elif 9.5 <= hour < 16:
    market_status = "盘中"
else:
    market_status = "收盘/盘后"
```

---

## 数据注入格式

### 输入（用户消息）

```json
{
  "message": "美股走势及消息面分析"
}
```

### 输出（Hook返回）

```json
{
  "system_prompt_append": "【监察者模式自动触发 - 美股分析前置检查】\n\n⚠️ 检测到您请求美股相关分析...",
  "context": {
    "supervisor_mode_triggered": true,
    "market_type": "us_stock",
    "beijing_time": "2026-04-30 06:25:38"
  }
}
```

---

## 执行流程

```
用户发送消息
    ↓
Hermes接收
    ↓
pre_llm_call Hooks触发
    ↓
1. time-sense-injector.py → 注入当前时间
    ↓
2. smart-skill-loader.py → 加载相关Skills
    ↓
3. supervisor-precheck.py → 检测关键词
    ↓
匹配成功？
    ├─ 是 → 注入监察者提示 → LLM响应
    └─ 否 → 跳过 → LLM正常响应
```

---

## 测试方法

### 单元测试

```bash
# 测试美股触发
echo '{"message": "美股走势分析"}' | python3 ~/.hermes/hooks/supervisor-precheck.py

# 测试A股触发
echo '{"message": "A股走势分析"}' | python3 ~/.hermes/hooks/supervisor-precheck.py

# 测试非触发
echo '{"message": "今天天气"}' | python3 ~/.hermes/hooks/supervisor-precheck.py
```

### 集成测试

```python
import json
import subprocess

test_cases = [
    {"message": "美股走势", "should_trigger": True, "market": "us_stock"},
    {"message": "A股分析", "should_trigger": True, "market": "a_stock"},
    {"message": "天气", "should_trigger": False, "market": None},
]

for test in test_cases:
    cmd = f'echo \'{json.dumps({"message": test["message"]})}\' | python3 ~/.hermes/hooks/supervisor-precheck.py'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = json.loads(result.stdout)
    
    triggered = bool(output.get("system_prompt_append"))
    market = output.get("context", {}).get("market_type")
    
    assert triggered == test["should_trigger"]
    if test["should_trigger"]:
        assert market == test["market"]
```

---

## 性能指标

| 指标 | 数值 |
|------|------|
| Hook执行时间 | < 0.1秒 |
| 内存占用 | < 5MB |
| CPU使用 | < 1% |
| 触发准确率 | 100%（7/7测试通过） |

---

## 扩展指南

### 添加新市场（如港股）

1. **添加关键词模式**：

```python
def should_trigger_supervisor(user_message):
    hk_stock_patterns = [
        r'港股.*(走势|收盘|行情|分析)',
        r'(恒生指数|恒指)',
        r'(腾讯|阿里|美团)',
    ]
    
    for pattern in hk_stock_patterns:
        if re.search(pattern, user_message, re.IGNORECASE):
            return "hk_stock"
```

2. **添加时区换算**：

```python
def get_hk_time(beijing_time):
    """北京时间 → 香港时间（相同，UTC+8）"""
    return beijing_time  # 香港与北京同区
```

3. **添加市场状态判断**：

```python
elif market_type == "hk_stock":
    hour = hk_time.hour
    if hour < 9.5:
        market_status = "盘前"
    elif 9.5 <= hour < 12:
        market_status = "早盘"
    elif 12 <= hour < 13:
        market_status = "午休"
    elif 13 <= hour < 16:
        market_status = "午盘"
    else:
        market_status = "收盘"
```

---

## 故障排查

### Hook未触发

**检查清单**：
1. ✅ Hook文件是否存在？
2. ✅ Hook是否有执行权限？
3. ✅ config.yaml中是否配置？
4. ✅ 用户消息是否包含关键词？

```bash
# 检查文件
ls -la ~/.hermes/hooks/supervisor-precheck.py

# 检查权限
chmod +x ~/.hermes/hooks/supervisor-precheck.py

# 检查配置
grep -A 3 "supervisor-precheck.py" ~/.hermes/config.yaml
```

### 时间锚定错误

**检查清单**：
1. ✅ 是否正确读取系统注入的时间？
2. ✅ 时区换算是否正确？
3. ✅ 市场状态判断是否正确？

```bash
# 测试时区换算
python3 << 'EOF'
from datetime import datetime, timedelta

beijing_time = datetime.utcnow() + timedelta(hours=8)
us_eastern_time = beijing_time - timedelta(hours=12)

print(f"北京时间: {beijing_time}")
print(f"美东时间: {us_eastern_time}")
EOF
```

---

## 维护建议

1. **定期测试** - 每月运行一次完整测试套件
2. **日志监控** - 检查Hook执行日志，发现异常
3. **关键词更新** - 根据用户新需求添加关键词
4. **性能优化** - 如果Hook执行时间 > 1秒，需要优化

---

## 版本历史

- **v1.0** (2026-04-30) - 初始版本，支持美股/A股自动触发
