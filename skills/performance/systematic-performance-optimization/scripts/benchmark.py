#!/usr/bin/env python3
"""
性能基准测试套件 - 可直接复用
将此脚本复制到项目的 .agchk/benchmark.py 使用
"""

import time
import json
import copy
from typing import Dict, List, Any, Callable


class Benchmarker:
    """基准测试工具类"""
    
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations
        self.results = {}
    
    def benchmark(self, name: str, func: Callable, *args, **kwargs) -> Dict:
        """运行基准测试并返回统计数据"""
        times = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            times.append(time.perf_counter() - start)
        
        times.sort()
        result = {
            'avg_ms': (sum(times) / len(times)) * 1000,
            'p50_ms': times[int(len(times) * 0.50)] * 1000,
            'p95_ms': times[int(len(times) * 0.95)] * 1000,
            'p99_ms': times[int(len(times) * 0.99)] * 1000,
            'total_ms': sum(times) * 1000,
            'iterations': self.iterations,
        }
        self.results[name] = result
        return result
    
    def compare(self, name: str, old_func: Callable, new_func: Callable, 
                *args, **kwargs) -> Dict:
        """对比两个实现的性能"""
        old_result = self.benchmark(f"{name}_old", old_func, *args, **kwargs)
        new_result = self.benchmark(f"{name}_new", new_func, *args, **kwargs)
        
        speedup = old_result['avg_ms'] / new_result['avg_ms']
        self.results[f"{name}_speedup"] = {
            'speedup_x': speedup,
            'improvement_pct': (speedup - 1) * 100,
            'old_avg_ms': old_result['avg_ms'],
            'new_avg_ms': new_result['avg_ms'],
        }
        return self.results[f"{name}_speedup"]
    
    def verify_equivalence(self, old_func: Callable, new_func: Callable,
                          test_cases: List) -> bool:
        """验证两个实现结果完全一致"""
        for i, test_case in enumerate(test_cases):
            old_result = old_func(test_case)
            new_result = new_func(test_case)
            
            if old_result != new_result:
                print(f"❌ 测试用例 {i} 失败:")
                print(f"   输入: {repr(test_case)[:100]}")
                print(f"   旧输出: {repr(old_result)[:100]}")
                print(f"   新输出: {repr(new_result)[:100]}")
                return False
        
        print("✅ 所有测试用例通过，功能完全一致")
        return True
    
    def save_results(self, path: str = ".agchk/benchmark_results.json"):
        """保存基准测试结果"""
        data = {
            'timestamp': time.time(),
            'results': self.results,
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"📊 基准测试结果已保存到: {path}")
    
    def print_summary(self):
        """打印基准测试摘要"""
        print("\n" + "="*60)
        print("📊 性能基准测试结果")
        print("="*60)
        
        for name, result in self.results.items():
            if 'speedup_x' in result:
                speedup = result['speedup_x']
                emoji = "🚀" if speedup >= 1.5 else "✅" if speedup >= 1.1 else "⚠️"
                print(f"{emoji} {name}: {speedup:.2f}x 提升")
                print(f"   {result['old_avg_ms']:.3f}ms → {result['new_avg_ms']:.3f}ms")
            else:
                print(f"📌 {name}:")
                print(f"   avg: {result['avg_ms']:.3f}ms, p99: {result['p99_ms']:.3f}ms")
        
        print("="*60)


# ========== 示例使用 ==========
if __name__ == "__main__":
    # 示例：测试 deepcopy vs 浅拷贝
    benchmarker = Benchmarker(iterations=1000)
    
    test_data = {
        'messages': [{'role': 'user', 'content': 'hello'}] * 10,
        'tools': None,
        'model': 'gpt-4',
    }
    
    def old_implementation(data):
        return copy.deepcopy(data)
    
    def new_implementation(data):
        return {k: v for k, v in data.items()}
    
    # 验证一致性
    print("🔍 验证功能一致性...")
    benchmarker.verify_equivalence(
        old_implementation, new_implementation, [test_data]
    )
    
    # 运行基准测试
    print("\n⚡ 运行基准测试...")
    benchmarker.compare(
        "copy_operation", old_implementation, new_implementation, test_data
    )
    
    # 打印并保存
    benchmarker.print_summary()
    benchmarker.save_results()
