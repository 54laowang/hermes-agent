#!/usr/bin/env python3
"""
Skills 完整度自动验证脚本
用途：统计 Skill 的检查点、异常处理、边界条件数量，验证完整度是否达标

使用方法：
    python scripts/verify_skill_completeness.py <skill_path>
    
示例：
    python scripts/verify_skill_completeness.py stock-data-acquisition/SKILL.md
"""

import re
import sys
from pathlib import Path


def analyze_skill(skill_path):
    """分析 Skill 完整度"""
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计检查点（格式：**CP-MODULE-01**）
    checkpoints = len(re.findall(r'\*\*CP-[A-Z]+-\d+\*\*', content))
    
    # 统计边界条件（格式：**BC-MODULE-01**）
    boundaries = len(re.findall(r'\*\*BC-[A-Z]+-\d+\*\*', content))
    
    # 统计异常处理（查找"异常场景"表格行数）
    exceptions = len(re.findall(r'异常场景', content))
    
    # 统计模块
    modules = len(re.findall(r'## 模块', content))
    
    # 统计代码行数
    lines = len(content.split('\n'))
    
    return {
        'checkpoints': checkpoints,
        'exceptions': exceptions,
        'boundaries': boundaries,
        'modules': modules,
        'lines': lines
    }


def verify_completeness(skill_name, result, targets):
    """验证完整度是否达标"""
    print(f"\n📊 {skill_name}")
    print(f"   检查点: {result['checkpoints']} 个")
    print(f"   异常处理: {result['exceptions']} 处")
    print(f"   边界条件: {result['boundaries']} 项")
    print(f"   核心模块: {result['modules']} 个")
    print(f"   代码行数: {result['lines']} 行")
    
    # 验证达标情况
    target = targets.get(skill_name, {'checkpoints': 15, 'exceptions': 10, 'boundaries': 15})
    
    cp_ok = result['checkpoints'] >= target['checkpoints']
    ex_ok = result['exceptions'] >= target['exceptions']
    bc_ok = result['boundaries'] >= target['boundaries']
    
    print(f"\n   ✅ 检查点: {result['checkpoints']} >= {target['checkpoints']} {'✅' if cp_ok else '❌'}")
    print(f"   ✅ 异常处理: {result['exceptions']} >= {target['exceptions']} {'✅' if ex_ok else '❌'}")
    print(f"   ✅ 边界条件: {result['boundaries']} >= {target['boundaries']} {'✅' if bc_ok else '❌'}")
    
    completeness = 100 if (cp_ok and ex_ok and bc_ok) else 0
    print(f"   ✅ 完整度: {completeness}% {'✅' if completeness == 100 else '❌'}")
    
    return completeness == 100


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python scripts/verify_skill_completeness.py <skill_path>")
        print("示例: python scripts/verify_skill_completeness.py stock-data-acquisition/SKILL.md")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    if not skill_path.exists():
        print(f"❌ 文件不存在: {skill_path}")
        sys.exit(1)
    
    # 定义各 Skill 的达标标准
    targets = {
        'stock-data-acquisition': {'checkpoints': 20, 'exceptions': 15, 'boundaries': 20},
        'stock-analysis-framework': {'checkpoints': 25, 'exceptions': 20, 'boundaries': 25},
        'grid-trading-system': {'checkpoints': 15, 'exceptions': 10, 'boundaries': 15},
        'market-intelligence-system': {'checkpoints': 18, 'exceptions': 12, 'boundaries': 18}
    }
    
    print("=" * 60)
    print("Skills 完整度验证")
    print("=" * 60)
    
    result = analyze_skill(skill_path)
    skill_name = skill_path.parent.name if skill_path.name == 'SKILL.md' else skill_path.stem
    
    success = verify_completeness(skill_name, result, targets)
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ 验证通过！完整度达到 100%")
        sys.exit(0)
    else:
        print("❌ 验证失败！完整度未达标")
        sys.exit(1)


if __name__ == '__main__':
    main()
