# 性能优化速查表

基于 Hermes Agent 架构审计的实践经验，快速识别并修复常见性能问题。

---

## 🔍 快速扫描清单

### 1. 拷贝热点
```bash
# 搜索 deepcopy 和 .copy()
grep -rn "copy.deepcopy\|deepcopy\|.copy()" --include="*.py"
```

**问题代码：**
```python
# ❌ 不必要的深拷贝
transformed = copy.deepcopy(messages)
for msg in transformed:
    msg["content"] = process(msg["content"])
```

**修复方案：**
```python
# ✅ 浅拷贝（只修改第一层）
transformed = [dict(msg) if isinstance(msg, dict) else msg 
               for msg in messages]

# ✅ 如果完全不修改输入，直接返回！
return messages  # 如果不需要修改，不要拷贝！
```

---

### 2. 日志优化
```bash
# 搜索 f-string 在日志中
grep -rn "logger\..*f\"" --include="*.py"
grep -rn "logger\..*f'" --include="*.py"
```

**问题代码：**
```python
# ❌ 总是格式化字符串，即使日志级别关闭
logger.debug(f"Processing: {huge_payload}")
logger.debug(f"State: {json.dumps(large_state)}")
```

**修复方案：**
```python
# ✅ 延迟格式化，只有 debug 开启时才执行
logger.debug("Processing: %s", huge_payload)
logger.debug("State: %s", json.dumps(large_state))

# ✅ 对于昂贵操作，先检查日志级别
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("State: %s", expensive_computation())
```

---

### 3. 无保护循环
```bash
# 搜索无限循环
grep -rn "while True" --include="*.py"
```

**问题代码：**
```python
# ❌ 无保护，死循环风险
while True:
    if condition:
        break
```

**修复方案：**
```python
# ✅ 有最大迭代次数保护
MAX_ITERATIONS = 1000
for _ in range(MAX_ITERATIONS):
    if condition:
        break
else:
    logger.warning("Loop exceeded max iterations")
```

---

### 4. 字符串拼接
```bash
# 搜索循环内的 += 字符串操作
grep -rn "+=" --include="*.py" | grep -B2 "for\|while"
```

**问题代码：**
```python
# ❌ O(n²) 复杂度
result = ""
for item in items:
    result += item  # 每次创建新字符串！
```

**修复方案：**
```python
# ✅ O(n) 复杂度
result_parts = []
for item in items:
    result_parts.append(item)
result = ''.join(result_parts)
```

---

### 5. 冗余 print 语句
```bash
# 搜索 print 语句
grep -rn "print(" --include="*.py" | grep -v "#.*print"
```

**问题代码：**
```python
# ❌ 生产环境中的 print 语句（同步 I/O）
print(f"Processing {len(messages)} messages")
```

**修复方案：**
```python
# ✅ 使用 logger，支持异步和级别控制
logger.debug("Processing %d messages", len(messages))
```

---

## 📊 优先排序矩阵

| 出现次数 | 单次耗时 | 优先级 | 行动 |
|----------|----------|--------|------|
| 高 (>10) | 高 (>1ms) | 🔴 P0 | 立即修复 |
| 高 (>10) | 中 (0.1-1ms) | 🟠 P1 | 计划修复 |
| 低 (<10) | 高 (>1ms) | 🟡 P2 | 评估影响 |
| 低 (<10) | 低 (<0.1ms) | 🟢 P3 | 可以忽略 |

**关键教训：** 2 个 deepcopy (0.088ms) > 10,000 次 logger 调用！
永远先基准测试，再排序！

---

## ✅ 修复验证清单

修复完成后必须验证：

1. **语法检查**
   ```bash
   python3 -c "import ast; ast.parse(open('file.py').read()); print('OK')"
   ```

2. **功能一致** - 新旧实现输出完全相同
   ```python
   assert old_func(input) == new_func(input)
   ```

3. **性能提升** - 基准测试显示 >20% 提升

4. **无副作用** - 不修改输入参数
   ```python
   original = copy.deepcopy(input)
   result = new_func(input)
   assert input == original  # 输入未被修改
   ```

5. **回归测试** - 现有测试套件全部通过

---

## 🚀 验收标准

| 指标 | 优秀 | 良好 | 可接受 | 不可接受 |
|------|------|------|--------|----------|
| 性能提升 | >2x | >1.5x | >1.1x | <1.1x |
| 代码改动 | <10 行 | <50 行 | <200 行 | >500 行 |
| 测试覆盖率 | 100% | >90% | >70% | <50% |
| 引入复杂度 | 0 | 低 | 中 | 高 |

---

## 💡 设计模式

### 防御性拷贝模式
```python
def process_data(data, copy_strategy='auto'):
    """
    智能拷贝：根据输入决定拷贝策略
    
    copy_strategy: 'deep'|'shallow'|'auto'|'none'
    """
    if copy_strategy == 'none':
        return data
    
    if copy_strategy == 'auto':
        # 检查是否需要深拷贝
        has_nested = any(isinstance(v, (dict, list)) 
                         for v in data.values())
        copy_strategy = 'deep' if has_nested else 'shallow'
    
    if copy_strategy == 'deep':
        return copy.deepcopy(data)
    else:
        return dict(data)
```

### 惰性求值模式
```python
class LazyState:
    """只在真正需要时才拷贝或计算"""
    
    def __init__(self, state):
        self._state = state
        self._copy = None
    
    @property
    def state(self):
        if self._copy is None:
            self._copy = self._make_copy()
        return self._copy
    
    def _make_copy(self):
        # 根据实际需要选择拷贝策略
        return dict(self._state)
```

---

## 📝 提交前检查

每次提交代码前运行：

```bash
#!/bin/bash
echo "🔍 性能审计检查..."

ADDED_DEEPCOPY=$(git diff --cached | grep -c "^+.*deepcopy")
ADDED_WHILE_TRUE=$(git diff --cached | grep -c "^+.*while True")
ADDED_PRINT=$(git diff --cached | grep -c "^+.*print(")

echo "   新增 deepcopy: $ADDED_DEEPCOPY"
echo "   新增 while True: $ADDED_WHILE_TRUE"
echo "   新增 print: $ADDED_PRINT"

if [ $((ADDED_DEEPCOPY + ADDED_WHILE_TRUE + ADDED_PRINT)) -gt 0 ]; then
    echo "⚠️  上述代码可能存在性能问题，请确认是否必要"
fi
```

---

## 📚 参考资源

- [Python 性能分析指南](https://docs.python.org/3/library/profile.html)
- [高性能 Python](https://github.com/mynameisfiber/high_performance_python)
- [Real Python: 性能优化](https://realpython.com/python-performance/)

---

*最后更新: 基于 Hermes Agent v2 架构审计实践*
