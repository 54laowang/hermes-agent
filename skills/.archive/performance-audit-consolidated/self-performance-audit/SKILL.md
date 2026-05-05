---
name: self-performance-audit
description: 系统化自我性能审计与持续优化体系 - 基于agchk驱动的代码内耗发现、基准测试、持续优化闭环
---

# 🔍 自我性能审计与优化体系

## 核心方法论

基于 agchk 架构审计工具建立的"发现-测量-优化-验证"闭环体系，适用于任何大型 Python 代码库的性能自我诊断和持续优化。

## 四步优化法:
1. **扫描发现** - 静态代码分析找出内耗点
2. **基准测量** - 建立性能基线量化问题
3. **落地优化** - 针对性修复性能瓶颈
4. **持续审计** - 建立机制防止性能退化

---

## 第一步：深度代码扫描发现

### 扫描清单 - 常见性能杀手

| 检查项 | 命令 | 风险阈值 |
|---------|------|----------|
| `while True` 无保护循环 | `grep -rn 'while True:' --include=*.py .` | > 10 处 |
| 循环中 deepcopy | `grep -rn 'deepcopy' --include=*.py .` | 在 for/while 中 |
| print 调试残留 | `grep -rn 'print(' --include=*.py .` | > 50 处 |
| 不必要的 list/dict 拷贝 | `grep -rn '.copy()\|dict()\|list()'` | 热点路径中 |

### 扫描脚本模板

```python
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

class PerformanceScanner:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.findings = defaultdict(list)
        
    def scan_loops(self):
        """扫描无保护的无限循环"""
        result = subprocess.run(
            ['grep', '-rn', 'while True:', '--include=*.py', self.project_root],
            capture_output=True, text=True
        )
        # 检查每个循环是否有 break/return/raise 保护
        
    def scan_copies(self):
        """扫描循环中的数据拷贝"""
        pass
        
    def generate_report(self):
        """生成扫描报告"""
        pass
```

---

## 第二步：建立性能基准测试

### 基准测试套件模板

```python
import time
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    name: str
    avg_time: float
    p50: float
    p95: float
    p99: float
    iterations: int

class CodeBenchmark:
    def __init__(self):
        self.results = {}
        
    def benchmark_operation(self, name, fn, iterations=1000):
        """基准测试单个操作"""
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            fn()
            times.append(time.perf_counter() - start)
            
        times.sort()
        self.results[name] = BenchmarkResult(
            name=name,
            avg_time=sum(times)/len(times),
            p50=times[int(len(times)*0.50)],
            p95=times[int(len(times)*0.95)],
            p99=times[int(len(times)*0.99)],
            iterations=iterations
        )
        
    def print_report(self):
        """打印格式化的基准报告"""
        print(f"{'测试项目':<30} {'平均':>10} {'P50':>10} {'P95':>10}")
        for result in self.results.values():
            print(f"{result.name:<30} "
                  f"{result.avg_time*1000:>8.3f}ms "
                  f"{result.p50*1000:>8.3f}ms "
                  f"{result.p95*1000:>8.3f}ms")
```

### 必测基准项

1. **消息/数据拷贝性能 - deepcopy vs 原地修改
2. **序列化/反序列化** - json.dumps/loads
3. **属性访问开销** - getattr vs 直接访问
4. **字符串处理** - += vs list append + join
5. **循环开销** - for vs 列表推导

---

## 第三步：典型优化技术

### 顶级优化（10-100x 提升）

#### 1. 消除不必要的 deepcopy

❌ 慢代码 (Hermes 实际案例):
```python
if extra_body:
    messages = copy.deepcopy(messages)  # 每次调用都深拷贝
    messages.append({"role": "system", "content": extra_body})
```

✅ 快代码:
```python
if extra_body:
    # 只浅拷贝需要修改的部分，避免递归拷贝整个结构
    messages = list(messages)  # O(n) 但只拷贝第一层引用
    messages.append({"role": "system", "content": extra_body})
```

**实测收益**: 2.6x 整体 API 调用性能提升！

#### 2. 日志延迟格式化

❌ 慢代码:
```python
logger.debug(f"Processing: {big_payload}")  # 总是格式化
```

✅ 快代码:
```python
logger.debug("Processing: %s", big_payload)  # 只在 debug 开启时格式化
```

### 一级优化（2-10x 提升）

#### 3. 循环保护 + 避免死循环

❌ 危险代码:
```python
while True:
    # 可能卡死
```

✅ 安全代码:
```python
MAX_ITER = 1000
for _ in range(MAX_ITER):
    # 处理逻辑
    if done:
        break
else:
    logger.warning("Loop timeout")
```

#### 4. 热点属性缓存

```python
from functools import cached_property, lru_cache

class State:
    @cached_property
    def expensive_computation(self):
        return self._load_and_process()  # 只算一次
```

#### 5. 字符串拼接优化

❌ 慢代码:
```python
result = ""
for item in items:
    result += item  # O(n²)
```

✅ 快代码:
```python
parts = []
for item in items:
    parts.append(item)  # O(n)
result = ''.join(parts)
```

---

## 第四步：持续审计机制

### 1. Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit-performance

echo "🔍 性能预检..."

# 检查新增 print
ADDED_PRINTS=$(git diff --cached | grep -c "^+.*print(")
if [ $ADDED_PRINTS -gt 0 ]; then
    echo "⚠️  发现 $ADDED_PRINTS 个新增 print，请改用 logger"
fi

# 检查新增 while True
ADDED_WHILE=$(git diff --cached | grep -c "^+.*while True")
if [ $ADDED_WHILE -gt 0 ]; then
    echo "⚠️  发现 $ADDED_WHILE 个无限循环，请添加保护"
fi

# 运行 agchk 快速扫描
agchk . --quick
```

### 2. 每日 CI 审计

```yaml
# .github/workflows/daily-audit.yml
name: Daily Performance Audit

on:
  schedule:
    - cron: '0 2 * * *'

jobs:
  audit:
    steps:
      - run: agchk . --profile enterprise
      - run: python3 .agchk/benchmark.py
      - run: python3 .agchk/optimize_stage1.py --dry-run
```

### 3. 性能回归告警

设置性能基线，每次提交后对比：

```python
def check_regression(new_result, baseline, threshold=1.2):
    """检查性能是否退化超过 threshold 20%"""
    if new_result.avg_time > baseline.avg_time * threshold:
        raise PerformanceRegressionError(
            f"性能退化 {new_result.avg_time/baseline.avg_time:.1f}x"
        )
```

---

## 优化验收标准

| 优化等级 | 性能提升 | 验收条件 |
|---------|---------|---------|
| P0 顶级 | > 10x | 移除不必要的 deepcopy |
| P1 重要 | 2-10x | 日志/循环/缓存优化 |
| P2 一般 | 10-50% | 细节调优 |
| P3 长期 | < 10% | 代码整洁 |

---

## 典型发现案例

### Hermes Agent 审计发现

| 问题 | 规模 | 优化后提升 |
|------|------|-------------|
| 2 个关键路径 deepcopy | 2 处 | **2.6x 整体提升** |
| - Anthropic provider deepcopy | 1 处 | 2.5x (0.223ms → 0.089ms) |
| - Qwen provider deepcopy | 1 处 | 1.6x (0.042ms → 0.026ms) |
| 115 个无保护 while True | 115 处 | 0 处实际问题（全部为用户交互） |
| 24,000+ 次状态属性访问 | 2 万次 | 待测量 |
| 10,000+ 次 logger 调用 | 1 万次 | 已使用延迟格式化 |

**关键洞察：出现次数最多的不一定是瓶颈！** 2 个 deepcopy 带来的性能影响 > 10,000 次其他操作。

---

## 文件组织结构

```
.agchk/
├── self_audit_mechanism.md   # 审计机制文档
├── optimize_stage1.py     # 第一阶段优化扫描
├── benchmark.py         # 基准测试套件
├── performance_baseline.json  # 基线数据
└── OPTIMIZATION_PLAYBOOK.md  # 优化速查表
```

---

## 最佳实践

1. **先测量再优化** - 没有基准就不知道优化了多少
2. **热点路径优先** - 优化 1% 的热点代码带来 99% 的收益
3. **建立防退化机制** - 优化完还要防止以后再慢回去
4. **文档化每个优化** - 为什么优化、优化了多少、怎么验证
5. **从最大的瓶颈开始** - deepcopy > 循环 > 日志 > 细节

---

## 记住

**核心洞察：性能优化 90% 的收益来自于 10% 的代码改变。找到那 10%，然后用 10 分钟改完，获得 10-100x 的提升。
