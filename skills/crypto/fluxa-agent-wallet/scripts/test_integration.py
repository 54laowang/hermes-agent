#!/usr/bin/env python3
"""
FluxA Agent Wallet 集成测试
验证 Smart Skill Router 是否正确识别并加载此技能
"""

import json
import sys
import os
from pathlib import Path

# 添加 hooks 目录到路径
hooks_dir = Path.home() / ".hermes" / "hooks"
sys.path.insert(0, str(hooks_dir))

# 动态导入
import importlib.util
spec = importlib.util.spec_from_file_location("skill_router", hooks_dir / "skill-router.py")
skill_router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(skill_router)

SkillRouter = skill_router.SkillRouter


def test_crypto_triggers():
    """测试加密货币相关触发词"""
    router = SkillRouter()
    
    test_cases = [
        ("我想转账USDC", ["fluxa-agent-wallet"]),
        ("帮我支付这个API", ["fluxa-agent-wallet"]),
        ("打开钱包", ["fluxa-agent-wallet"]),
        ("加入龙虾朋友圈", ["fluxa-agent-wallet"]),
        ("领取红包", ["fluxa-agent-wallet"]),
        ("创建x402支付", ["fluxa-agent-wallet"]),
    ]
    
    print("🧪 测试 FluxA Agent Wallet 触发词识别\n")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for message, expected_skills in test_cases:
        recommended = router.recommend_skills(message)
        
        # 检查期望的技能是否在推荐列表中
        matched = all(skill in recommended for skill in expected_skills)
        
        status = "✅" if matched else "❌"
        print(f"{status} 消息: \"{message}\"")
        print(f"   期望: {expected_skills}")
        print(f"   实际: {recommended}")
        print()
        
        if matched:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    
    return failed == 0


def test_skill_structure():
    """测试技能文件结构"""
    print("\n🧪 测试技能文件结构\n")
    print("=" * 60)
    
    skill_dir = Path.home() / ".hermes" / "skills" / "crypto" / "fluxa-agent-wallet"
    
    required_files = [
        "SKILL.md",
        "README.md",
        "scripts/install.sh",
        "references/CLAWPI.md",
        "references/PAYOUT.md",
        "references/X402-PAYMENT.md",
        "references/PAYMENT-LINK.md",
        "references/MANDATE-PLANNING.md",
    ]
    
    passed = 0
    failed = 0
    
    for file_path in required_files:
        full_path = skill_dir / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        
        if exists:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"文件检查: {passed}/{len(required_files)} 存在")
    
    return failed == 0


def test_skill_metadata():
    """测试 SKILL.md 元数据"""
    print("\n🧪 测试 SKILL.md 元数据\n")
    print("=" * 60)
    
    skill_file = Path.home() / ".hermes" / "skills" / "crypto" / "fluxa-agent-wallet" / "SKILL.md"
    
    if not skill_file.exists():
        print("❌ SKILL.md 不存在")
        return False
    
    content = skill_file.read_text()
    
    # 检查必需的 frontmatter 字段
    required_fields = [
        "name:",
        "description:",
        "version:",
        "cli_version:",
        "network:",
        "category:",
    ]
    
    passed = 0
    failed = 0
    
    for field in required_fields:
        if field in content:
            print(f"✅ 找到字段: {field}")
            passed += 1
        else:
            print(f"❌ 缺少字段: {field}")
            failed += 1
    
    # 检查关键内容
    key_sections = [
        "快速开始",
        "能力矩阵",
        "安全注意事项",
        "Hermes 集成特性",
    ]
    
    print()
    for section in key_sections:
        if section in content:
            print(f"✅ 包含章节: {section}")
            passed += 1
        else:
            print(f"❌ 缺少章节: {section}")
            failed += 1
    
    print("=" * 60)
    print(f"元数据检查: {passed} 通过, {failed} 失败")
    
    return failed == 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🦞 FluxA Agent Wallet 集成测试")
    print("=" * 60)
    
    results = {
        "触发词识别": test_crypto_triggers(),
        "文件结构": test_skill_structure(),
        "元数据检查": test_skill_metadata(),
    }
    
    print("\n" + "=" * 60)
    print("📊 最终测试结果")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print()
    if all_passed:
        print("🎉 所有测试通过！FluxA Agent Wallet 已成功集成到 Hermes")
        print()
        print("📖 快速开始:")
        print("   1. 运行安装脚本: ~/.hermes/skills/crypto/fluxa-agent-wallet/scripts/install.sh")
        print("   2. 或手动安装: npm install -g @fluxa-pay/fluxa-wallet@0.4.5")
        print("   3. 查看文档: ~/.hermes/skills/crypto/fluxa-agent-wallet/SKILL.md")
        print()
        print("💬 使用示例:")
        print("   \"帮我转账USDC给朋友\"")
        print("   \"加入龙虾朋友圈\"")
        print("   \"支付这个API\"")
    else:
        print("⚠️ 部分测试失败，请检查上述输出")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
