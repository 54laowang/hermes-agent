#!/usr/bin/env python3
"""
📊 Hermes Agent 性能基准测试套件
建立性能基线，跟踪优化效果
"""

import time
import json
import copy
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    name: str
    avg_time: float
    p50: float
    p95: float
    p99: float
    iterations: int

class HermesBenchmark:
    def __init__(self):
        self.results: Dict[str, BenchmarkResult] = {}
        
    def benchmark_message_copy(self, iterations=1000):
        """ 基准测试：消息拷贝性能 """
        # 模拟真实的消息结构
        sample_message = {
            "role": "user",
            "content": "Hello, world!",
            "tool_calls": [{"id": "1", "name": "test", "args": {}}],
            "metadata": {"timestamp": time.time()}
        }
        messages = [sample_message.copy() for _ in range(50)]
        
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            # 当前实现：deepcopy
            _ = copy.deepcopy(messages)
            times.append(time.perf_counter() - start)
            
        times.sort()
        self.results['message_copy'] = BenchmarkResult(
            name='消息拷贝 (deepcopy)',
            avg_time=sum(times)/len(times),
            p50=times[int(len(times)*0.50)],
            p95=times[int(len(times)*0.95)],
            p99=times[int(len(times)*0.99)],
            iterations=iterations
        )
        
    def benchmark_message_inplace(self, iterations=1000):
        """ 基准测试：原地修改性能 """
        sample_message = {
            "role": "user",
            "content": "Hello, world!",
        }
        messages = [sample_message.copy() for _ in range(50)]
        
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            # 优化方案：原地修改
            for msg in messages:
                if msg['role'] == 'user':
                    pass  # 原地操作
            times.append(time.perf_counter() - start)
            
        times.sort()
        self.results['message_inplace'] = BenchmarkResult(
            name='消息处理 (原地修改)',
            avg_time=sum(times)/len(times),
            p50=times[int(len(times)*0.50)],
            p95=times[int(len(times)*0.95)],
            p99=times[int(len(times)*0.99)],
            iterations=iterations
        )
        
    def benchmark_json_serialization(self, iterations=1000):
        """ 基准测试：JSON 序列化性能 """
        test_data = {
            "messages": [{"role": "user", "content": "test" * 100} for _ in range(20)],
            "tools": [{"name": f"tool_{i}", "description": "desc" * 50} for i in range(10)],
            "metadata": {"session_id": "test", "timestamp": time.time()}
        }
        
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            serialized = json.dumps(test_data)
            deserialized = json.loads(serialized)
            times.append(time.perf_counter() - start)
            
        times.sort()
        self.results['json_serde'] = BenchmarkResult(
            name='JSON 序列化/反序列化',
            avg_time=sum(times)/len(times),
            p50=times[int(len(times)*0.50)],
            p95=times[int(len(times)*0.95)],
            p99=times[int(len(times)*0.99)],
            iterations=iterations
        )
        
    def benchmark_state_access(self, iterations=10000):
        """ 基准测试：状态访问性能 """
        # 模拟 session.state 访问模式
        class MockState:
            def __init__(self):
                self._data = {f"key_{i}": f"value_{i}" for i in range(100)}
                self.counter = 0
                
            def __getattr__(self, name):
                self.counter += 1
                return self._data.get(name)
        
        state = MockState()
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            # 模拟多次状态访问
            _ = state._data.get(f"key_{i % 100}")
            _ = state._data.get(f"key_{(i+1) % 100}")
            _ = state._data.get(f"key_{(i+2) % 100}")
            times.append(time.perf_counter() - start)
            
        times.sort()
        self.results['state_access'] = BenchmarkResult(
            name='状态属性访问',
            avg_time=sum(times)/len(times),
            p50=times[int(len(times)*0.50)],
            p95=times[int(len(times)*0.95)],
            p99=times[int(len(times)*0.99)],
            iterations=iterations
        )
        
    def print_report(self):
        """ 打印基准测试报告 """
        print("\n" + "="*80)
        print("📊 Hermes Agent 性能基准测试报告")
        print("="*80)
        
        print(f"\n{'测试项目':<35} {'平均耗时':>12} {'P50':>12} {'P95':>12} {'P99':>12}")
        print("-" * 95)
        
        for result in self.results.values():
            print(f"{result.name:<35} "
                  f"{result.avg_time*1000:>10.3f}ms "
                  f"{result.p50*1000:>10.3f}ms "
                  f"{result.p95*1000:>10.3f}ms "
                  f"{result.p99*1000:>10.3f}ms")
        
        print("\n" + "="*80)
        print("💡 优化潜力分析:")
        print("="*80)
        
        # 计算优化潜力
        if 'message_copy' in self.results and 'message_inplace' in self.results:
            speedup = (self.results['message_copy'].avg_time / 
                     self.results['message_inplace'].avg_time)
            print(f"\n🔄 消息拷贝 vs 原地修改: {speedup:.1f}x 加速潜力")
            
        total_per_call = (
            self.results['message_copy'].avg_time +
            self.results['json_serde'].avg_time +
            self.results['state_access'].avg_time * 10  # 每轮 10 次访问
        )
        print(f"⚡ 每轮累计开销: {total_per_call*1000:.2f}ms")
        print(f"💰 优化目标: 降低 50% → {(total_per_call*1000/2):.2f}ms")
        
        return total_per_call

def main():
    print("🚀 运行 Hermes Agent 性能基准测试...")
    print("   建立性能基线，跟踪优化效果")
    
    benchmark = HermesBenchmark()
    
    print("\n📦 测试 1/4: 消息拷贝性能...")
    benchmark.benchmark_message_copy()
    
    print("📦 测试 2/4: 原地修改性能...")
    benchmark.benchmark_message_inplace()
    
    print("📦 测试 3/4: JSON 序列化...")
    benchmark.benchmark_json_serialization()
    
    print("📦 测试 4/4: 状态访问...")
    benchmark.benchmark_state_access()
    
    baseline = benchmark.print_report()
    
    # 保存基线数据
    with open('/Users/me/.hermes/hermes-agent/.agchk/performance_baseline.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'baseline_ms': baseline * 1000,
            'results': {
                k: {
                    'avg_ms': v.avg_time * 1000,
                    'p50_ms': v.p50 * 1000,
                    'p95_ms': v.p95 * 1000,
                }
                for k, v in benchmark.results.items()
            }
        }, f, indent=2)
    
    print(f"\n✅ 基准数据已保存: .agchk/performance_baseline.json")
    print(f"   当前基线: {baseline*1000:.2f}ms/轮")

if __name__ == '__main__':
    main()
