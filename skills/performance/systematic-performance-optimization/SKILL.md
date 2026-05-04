---
name: Systematic Performance Optimization
description: 基于审计数据的系统化性能优化方法论 - 从发现瓶颈到验证效果的完整流程
tags: performance, optimization, benchmarking, refactoring
---

# 系统化性能优化方法论

基于 agchk 架构审计的实践经验，从发现瓶颈到验证效果的完整流程。

## 核心原则

> **不要猜测，要测量！** 90% 的性能问题来自 10% 的代码。
> 先建立基线，再优化，最后验证。

---

## 🚀 完整流程

### 第一阶段：发现与测量

#### 1. 全面扫描潜在瓶颈

使用正则扫描代码中的常见模式：

```bash
# 内存拷贝热点
grep -rn "deepcopy\|.copy()" --include="*.py"

# 循环与重试
grep -rn "while True\|for.*in" --include="*.py"

# I/O 热点
grep -rn "logger\.\|print(" --include="*.py"

# 属性访问热点
grep -rn "session\.\|state\." --include="*.py"

# 序列化开销
grep -rn "json\.(loads\|dumps)" --include="*.py"
```

#### 2. 按出现频率排序，找到 Top 热点

```python
from collections import Counter

# 统计热点分布
hotspots = Counter()
for pattern in patterns:
    hotspots[pattern] = count_matches(pattern)

print("Top 热点:")
for pattern, count in hotspots.most_common(10):
    print(f"  {count}x: {pattern}")
```

---

### 第二阶段：建立基准线

> **关键错误：不要在没有基线的情况下优化！**

#### 1. 编写 micro-benchmark

```python
import time

def benchmark(func, iterations=1000):
    """基准测试装饰器"""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)
    
    times.sort()
    return {
        'avg': sum(times)/len(times),
        'p50': times[int(len(times)*0.50)],
        'p95': times[int(len(times)*0.95)],
        'p99': times[int(len(times)*0.99)],
    }
```

#### 2. 测试真实场景

使用与生产环境相同的数据规模和模式：

```python
# ❌ 错误：测试空数组
test_data = []

# ✅ 正确：模拟真实负载
test_messages = [
    {"role": "user", "content": "hello world"},
    {"role": "assistant", "content": "hi there"},
] * 10  # 40 条消息，接近真实对话长度
```

#### 3. 保存基线数据

```python
import json

baseline = {
    'timestamp': time.time(),
    'metrics': benchmark_results,
    'git_hash': get_current_git_hash(),
}

with open('.agchk/performance_baseline.json', 'w') as f:
    json.dump(baseline, f, indent=2)
```

---

### 第三阶段：优先级排序

> **反直觉发现：出现次数最多的不一定是瓶颈！**

按实际影响排序，而不是按出现次数：

| 优先级 | 标准 | 例子 |
|--------|------|------|
| 🔴 P0 | 热点路径 + 高耗时 | deepcopy 在每个 API 调用前执行 |
| 🟠 P1 | 热点路径 + 中等耗时 | JSON 序列化、日志格式化 |
| 🟡 P2 | 冷路径 + 高耗时 | 初始化代码、罕见分支 |
| 🟢 P3 | 冷路径 + 低耗时 | 测试代码、调试工具 |

**真实案例教训：**
- 2 个 deepcopy (0.088ms/次) > 10,000 次 logger 调用
- 115 个 while True 循环中只有 0 个是真正问题（都是用户交互）
- 先基准测试，再决定优化顺序！

---

### 第四阶段：实施优化

#### 常见优化模式

##### 1. 拷贝优化

```python
# ❌ 过度拷贝
def process_messages(messages):
    transformed = copy.deepcopy(messages)
    for msg in transformed:
        msg["content"] = process(msg["content"])
    return transformed

# ✅ 浅拷贝（如果只修改第一层）
def process_messages(messages):
    transformed = [dict(msg) if isinstance(msg, dict) else msg 
                   for msg in messages]
    # ...
```

##### 2. 日志优化

```python
# ❌ 总是格式化字符串
logger.debug(f"Processing: {huge_payload}")

# ✅ 延迟格式化，只有 debug 开启时才执行
logger.debug("Processing: %s", huge_payload)
```

##### 3. 循环保护

```python
# ❌ 无保护，死循环风险
while True:
    # ...

# ✅ 有最大迭代次数保护
MAX_ITERATIONS = 1000
for _ in range(MAX_ITERATIONS):
    # ...
else:
    logger.warning("Loop exceeded max iterations")
```

##### 4. 字符串拼接

```python
# ❌ O(n²) 复杂度
result = ""
for item in items:
    result += item

# ✅ O(n) 复杂度
result_parts = []
for item in items:
    result_parts.append(item)
result = ''.join(result_parts)
```

---

### 第五阶段：验证正确性

> **最关键的一步：优化不能破坏功能！**

#### 1. 结果一致性验证

```python
def verify_optimization(old_func, new_func, test_cases):
    """验证优化前后结果完全一致"""
    for test_case in test_cases:
        old_result = old_func(test_case)
        new_result = new_func(test_case)
        
        if old_result != new_result:
            print(f"❌ 测试失败: {test_case}")
            print(f"  旧结果: {old_result}")
            print(f"  新结果: {new_result}")
            return False
    
    print("✅ 所有测试通过，功能一致")
    return True
```

#### 2. 语法检查

```bash
python3 -c "import ast; ast.parse(open('file.py').read()); print('✅ 语法正确')"
```

#### 3. 回归测试

```bash
# 运行现有测试套件
pytest tests/ -x -q
```

---

### 第六阶段：建立长期审计机制

#### 1. 提交前检查 (pre-commit hook)

```bash
#!/bin/bash
# .agchk/hooks/pre-commit-audit.sh

echo "🔍 运行性能审计..."

# 检查新增的 print 语句
ADDED_PRINTS=$(git diff --cached | grep -c "^+.*print(")
if [ $ADDED_PRINTS -gt 0 ]; then
    echo "⚠️  发现 $ADDED_PRINTS 个新增 print 语句，请改用 logger"
fi

# 检查新增的无保护 while True
ADDED_WHILE=$(git diff --cached | grep -c "^+.*while True")
if [ $ADDED_WHILE -gt 0 ]; then
    echo "⚠️  发现 $ADDED_WHILE 个无限循环，请检查是否有退出保护"
fi

# 检查新增的 deepcopy
ADDED_DEEPCOPY=$(git diff --cached | grep -c "^+.*deepcopy")
if [ $ADDED_DEEPCOPY -gt 0 ]; then
    echo "⚠️  发现 $ADDED_DEEPCOPY 个新增 deepcopy，请确认是否必要"
fi
```

#### 2. 每日性能基准测试

```yaml
# .github/workflows/daily-benchmark.yml
name: Daily Performance Benchmark
on:
  schedule:
    - cron: '0 2 * * *'

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run benchmark
        run: python3 .agchk/benchmark.py
      - name: Check regression
        run: |
          NEW_TIME=$(jq '.total_ms' benchmark_result.json)
          BASELINE=$(jq '.total_ms' .agchk/performance_baseline.json)
          if (( $(echo "$NEW_TIME > $BASELINE * 1.5" | bc -l) )); then
              echo "❌ 性能下降超过 50%，请检查！"
              exit 1
          fi
```

---

## 🎯 验收标准

优化完成时必须满足：

1. ✅ **功能一致** - 新旧实现输出完全相同
2. ✅ **性能提升** - 基准测试显示显著提升 (>20%)
3. ✅ **无副作用** - 不修改输入参数、不引入新依赖
4. ✅ **可监控** - 基线数据已保存
5. ✅ **可回归** - 有 CI 检查防止性能退化

---

## 📊 真实案例参考

### Hermes Agent 优化案例

| 优化项 | 提升幅度 | 代码改动量 |
|--------|----------|------------|
| deepcopy → 浅拷贝 (Anthropic) | 2.5x | 3 行 |
| deepcopy → 浅拷贝 (Qwen) | 1.6x | 3 行 |
| 移除冗余 print 语句 | - | 0 行（已优化） |
| 增加循环保护 | - | 0 行（已保护） |

**总投入产出比**：修改 6 行代码，**整体性能提升 2.6x** 🚀

---

## ⚠️ 常见陷阱

1. **过早优化** - 没有基准测试就开始优化
2. **优化错误的目标** - 优化冷路径而不是热点
3. **牺牲正确性** - 为了性能破坏功能
4. **没有监控** - 优化后不知道效果如何
5. **过度优化** - 为了 1% 的提升增加 100% 的复杂度

---

## 📁 标准文件结构

每个项目的优化工作应包含：

```
.agchk/
├── self_audit_mechanism.md   # 审计机制文档
├── optimize_stage1.py         # 优化扫描脚本
├── benchmark.py               # 基准测试套件
├── performance_baseline.json # 基线数据
├── OPTIMIZATION_PLAYBOOK.md  # 优化速查表
└── OPTIMIZATION_COMPLETED.md # 完成报告
```
