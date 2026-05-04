#!/usr/bin/env python3
"""
Memory Architecture v1.5.0 - Integration Test
记忆架构完整测试套件

用法:
    python3 ~/.hermes/scripts/test_memory_architecture.py

测试报告保存至: ~/.hermes/logs/test_report_*.json
"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.home() / ".hermes" / "scripts"))


class MemoryArchitectureTest:
    """记忆架构测试套件"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
    
    def log(self, test_name: str, status: str, details: str = ""):
        """记录测试结果"""
        elapsed = time.time() - self.start_time
        entry = {
            "test": test_name,
            "status": status,
            "details": details,
            "elapsed": round(elapsed, 2)
        }
        self.results.append(entry)
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} [{elapsed:.1f}s] {test_name}: {status}")
        if details:
            print(f"   {details}")
    
    def test_1_embedding_similarity(self):
        """测试 1: Embedding 相似度检测"""
        print("\n" + "="*60)
        print("测试 1: Embedding 相似度检测")
        print("="*60)
        
        try:
            from embedding_similarity import EmbeddingSimilarity
            
            es = EmbeddingSimilarity()
            
            # 1.1 统计信息
            stats = es.get_stats()
            print(f"  模型: {stats['model']}")
            print(f"  缓存: {stats['cached_embeddings']}/{stats['total_experiential_memories']}")
            
            # 1.2 相似案例检测
            test_case_id = 131
            similar = es.find_similar_cases_semantic(test_case_id, threshold=0.7, limit=5)
            
            if similar:
                self.log(
                    "1.1 Embedding 统计",
                    "PASS",
                    f"缓存覆盖率 {stats['cache_coverage']}"
                )
                self.log(
                    "1.2 相似案例检测",
                    "PASS",
                    f"找到 {len(similar)} 个相似案例，最高相似度 {similar[0]['similarity']:.0%}"
                )
            else:
                self.log("1.2 相似案例检测", "WARN", "未找到相似案例")
            
            # 1.3 抽象建议
            suggestions = es.suggest_abstractions(threshold=0.7, min_cluster_size=2)
            
            if suggestions:
                self.log(
                    "1.3 抽象建议",
                    "PASS",
                    f"发现 {len(suggestions)} 个抽象机会"
                )
            else:
                self.log("1.3 抽象建议", "WARN", "未发现抽象机会")
            
            return True
        
        except Exception as e:
            self.log("Embedding 测试", "FAIL", str(e))
            return False
    
    def test_2_active_abstraction(self):
        """测试 2: 主动抽象引擎"""
        print("\n" + "="*60)
        print("测试 2: 主动抽象引擎")
        print("="*60)
        
        try:
            from active_abstraction import ActiveAbstractionEngine
            
            aae = ActiveAbstractionEngine()
            
            # 2.1 扫描抽象机会
            suggestions = aae.scan_all_cases(threshold=0.7, min_cluster_size=2)
            
            self.log(
                "2.1 扫描抽象机会",
                "PASS" if suggestions else "WARN",
                f"发现 {len(suggestions)} 个抽象机会"
            )
            
            # 2.2 抽象历史
            history = aae.get_abstraction_history(limit=5)
            
            self.log(
                "2.2 抽象历史",
                "PASS",
                f"历史记录 {len(history)} 条"
            )
            
            return True
        
        except Exception as e:
            self.log("主动抽象测试", "FAIL", str(e))
            return False
    
    def test_3_latent_memory(self):
        """测试 3: Latent Memory"""
        print("\n" + "="*60)
        print("测试 3: Latent Memory")
        print("="*60)
        
        try:
            from latent_memory import LatentMemoryManager
            
            lmm = LatentMemoryManager()
            
            # 3.1 统计信息
            stats = lmm.get_stats()
            print(f"  缓存: {stats['total_caches']}/{stats['max_caches']}")
            print(f"  命中率: {stats['hit_rate']}")
            
            # 3.2 存储测试
            test_context = "测试上下文：用户询问记忆架构优化"
            cache_id = lmm.store_cache(
                session_id="test-session",
                context=test_context,
                cache_data={"test": "data"},
                metadata={"summary": "测试缓存"}
            )
            
            self.log(
                "3.1 存储 KV Cache",
                "PASS",
                f"缓存 ID: {cache_id}"
            )
            
            # 3.3 检索测试
            result = lmm.retrieve_cache(test_context, threshold=0.7)
            
            if result:
                self.log(
                    "3.2 检索 KV Cache",
                    "PASS",
                    f"相似度: {result['similarity']:.0%}"
                )
            else:
                self.log("3.2 检索 KV Cache", "WARN", "未找到相似缓存")
            
            # 3.4 上下文注入
            injection = lmm.get_context_injection(test_context)
            
            if injection:
                self.log(
                    "3.3 上下文注入",
                    "PASS",
                    f"注入内容长度: {len(injection)} 字符"
                )
            else:
                self.log("3.3 上下文注入", "WARN", "无注入内容")
            
            return True
        
        except Exception as e:
            self.log("Latent Memory 测试", "FAIL", str(e))
            return False
    
    def test_4_llm_enhanced_abstraction(self):
        """测试 4: LLM 增强抽象"""
        print("\n" + "="*60)
        print("测试 4: LLM 增强抽象")
        print("="*60)
        
        try:
            from llm_enhanced_abstraction import LLMEnhancedAbstraction
            
            llea = LLMEnhancedAbstraction(provider="modelscope", model="deepseek-ai/DeepSeek-V3.2")
            
            # 4.1 可用模板
            templates = llea.get_available_templates()
            
            self.log(
                "4.1 可用模板",
                "PASS",
                f"{len(templates)} 个模板: {', '.join([t['name'] for t in templates])}"
            )
            
            # 4.2 案例分析
            test_case_ids = [131, 132]
            analysis = llea.analyze_cases(test_case_ids)
            
            self.log(
                "4.2 案例分析",
                "PASS",
                f"案例数: {analysis['case_count']}, 相似度: {analysis['avg_similarity']:.0%}"
            )
            
            # 4.3 规则生成
            result_rule = llea.generate_strategy(test_case_ids, use_llm=False)
            
            self.log(
                "4.3 规则生成",
                "PASS",
                f"生成长度: {len(result_rule['strategy_content'])} 字符"
            )
            
            # 4.4 LLM 生成
            result_llm = llea.generate_strategy(test_case_ids, template="technical", use_llm=True)
            
            if result_llm.get("strategy_source") == "llm":
                self.log(
                    "4.4 LLM 生成",
                    "PASS",
                    f"生成长度: {len(result_llm['strategy_content'])} 字符"
                )
            else:
                self.log("4.4 LLM 生成", "WARN", "回退到规则生成")
            
            return True
        
        except Exception as e:
            self.log("LLM 增强抽象测试", "FAIL", str(e))
            return False
    
    def test_5_memory_evolution(self):
        """测试 5: 记忆演化流程"""
        print("\n" + "="*60)
        print("测试 5: 记忆演化流程")
        print("="*60)
        
        try:
            from memory_evolution import MemoryEvolutionEngine
            
            mee = MemoryEvolutionEngine()
            
            # 5.1 统计信息
            stats = mee.get_evolution_stats()
            
            print(f"  总记忆: {stats['total']}")
            for mtype, count in stats['by_type'].items():
                print(f"    - {mtype}: {count}")
            
            self.log(
                "5.1 记忆统计",
                "PASS",
                f"总计 {stats['total']} 条记忆"
            )
            
            # 5.2 抽象机会检测
            opportunities = mee.detect_abstraction_opportunities()
            
            self.log(
                "5.2 抽象机会检测",
                "PASS" if opportunities else "WARN",
                f"发现 {len(opportunities)} 个抽象机会"
            )
            
            # 5.3 清理弱记忆
            cleaned = mee.cleanup_weak_memories(threshold=0.15)
            
            self.log(
                "5.3 清理弱记忆",
                "PASS",
                f"清理了 {cleaned} 条弱记忆"
            )
            
            return True
        
        except Exception as e:
            self.log("记忆演化测试", "FAIL", str(e))
            return False
    
    def test_6_shell_hook(self):
        """测试 6: Shell Hook 监控"""
        print("\n" + "="*60)
        print("测试 6: Shell Hook 监控")
        print("="*60)
        
        try:
            from memory_evolution_hook import check_new_memories, check_memory_health
            
            # 6.1 新记忆检测
            new_memories = check_new_memories("1970-01-01T00:00:00")
            
            self.log(
                "6.1 新记忆检测",
                "PASS",
                f"检测到 {len(new_memories)} 条记忆"
            )
            
            # 6.2 健康检查
            health = check_memory_health()
            
            self.log(
                "6.2 健康检查",
                "PASS",
                f"总计 {health['total']} 条，低质量 {health['low_quality_count']} 条"
            )
            
            return True
        
        except Exception as e:
            self.log("Shell Hook 测试", "FAIL", str(e))
            return False
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("测试报告")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warned = sum(1 for r in self.results if r["status"] == "WARN")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        
        elapsed = time.time() - self.start_time
        
        print(f"\n📊 总体统计：")
        print(f"  总测试: {total}")
        print(f"  ✅ 通过: {passed}")
        print(f"  ⚠️ 警告: {warned}")
        print(f"  ❌ 失败: {failed}")
        print(f"  通过率: {passed/total:.0%}")
        print(f"  耗时: {elapsed:.1f}s")
        
        print(f"\n📋 详细结果：")
        for r in self.results:
            icon = "✅" if r["status"] == "PASS" else "❌" if r["status"] == "FAIL" else "⚠️"
            print(f"  {icon} {r['test']}: {r['details']}")
        
        # 保存报告
        report_path = Path.home() / ".hermes" / "logs" / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "warned": warned,
                    "failed": failed,
                    "elapsed": elapsed
                },
                "results": self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 报告已保存: {report_path}")
        
        return passed == total or failed == 0


def main():
    """运行完整测试"""
    print("="*60)
    print("Memory Architecture v1.5.0 - Integration Test")
    print("="*60)
    
    test = MemoryArchitectureTest()
    
    # 运行所有测试
    test.test_1_embedding_similarity()
    test.test_2_active_abstraction()
    test.test_3_latent_memory()
    test.test_4_llm_enhanced_abstraction()
    test.test_5_memory_evolution()
    test.test_6_shell_hook()
    
    # 生成报告
    success = test.generate_report()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
