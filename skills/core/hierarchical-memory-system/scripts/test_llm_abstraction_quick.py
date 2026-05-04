#!/usr/bin/env python3
"""
Quick LLM Abstraction Test
快速测试 LLM 增强抽象功能
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".hermes" / "scripts"))

from llm_enhanced_abstraction import LLMEnhancedAbstraction


def main():
    # 使用 modelscope provider（推荐）
    llea = LLMEnhancedAbstraction(
        provider="modelscope",
        model="deepseek-ai/DeepSeek-V3.2"
    )
    
    print("🧪 LLM Enhanced Abstraction Quick Test")
    print("=" * 60)
    
    # 获取测试案例
    test_case_ids = [131, 132]  # 可根据实际情况修改
    
    print(f"\n测试案例: {test_case_ids}")
    
    # 分析案例
    print("\n📊 分析案例...")
    analysis = llea.analyze_cases(test_case_ids)
    
    print(f"  案例数: {analysis['case_count']}")
    print(f"  关键词: {analysis['keywords'][:3]}")
    print(f"  相似度: {analysis['avg_similarity']:.0%}")
    
    # LLM 生成策略
    print("\n🤖 LLM 生成策略...")
    result = llea.generate_strategy(
        test_case_ids,
        template="technical",
        use_llm=True
    )
    
    if result.get("strategy_source") == "llm":
        print("  ✅ LLM 成功")
        print("\n策略内容:")
        for line in result['strategy_content'].split('\n')[:8]:
            print(f"  {line}")
    else:
        print("  ⚠️ 回退到规则生成")
        print(f"  {result['strategy_content'][:100]}...")
    
    llea.emm.close()


if __name__ == "__main__":
    main()
