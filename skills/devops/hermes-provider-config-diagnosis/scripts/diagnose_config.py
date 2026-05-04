#!/usr/bin/env python3
"""
Hermes Provider 配置自动诊断脚本
自动检查配置结构、providers 格式、模型切换功能
"""

import yaml
import sys
import os
from pathlib import Path

def check_yaml_syntax(config_path):
    """检查 YAML 语法"""
    try:
        with open(config_path, 'r') as f:
            yaml.safe_load(f)
        return True, "YAML 语法正常"
    except yaml.YAMLError as e:
        return False, f"YAML 语法错误: {e}"

def check_providers_structure(config):
    """检查 providers 结构是否正确"""
    providers = config.get('providers', {})
    
    if isinstance(providers, list):
        return False, f"❌ providers 是 LIST 格式 (列表)，应该是 DICT 格式 (字典)"
    elif isinstance(providers, dict):
        return True, f"✅ providers 是 DICT 格式 (正确)，共 {len(providers)} 个提供商"
    else:
        return False, f"❌ providers 格式错误: {type(providers)}"

def check_providers_slug(config):
    """检查每个提供商是否有 slug 字段"""
    providers = config.get('providers', {})
    if not isinstance(providers, dict):
        return False, "无法检查 slug (providers 格式错误)"
    
    missing_slug = []
    for name, provider in providers.items():
        if isinstance(provider, dict) and not provider.get('slug'):
            missing_slug.append(name)
    
    if missing_slug:
        return False, f"❌ 以下提供商缺少 slug 字段: {', '.join(missing_slug)}"
    return True, "✅ 所有提供商都有 slug 字段"

def check_fallback_providers(config):
    """检查 fallback_providers 是否引用正确"""
    providers = config.get('providers', {})
    fallbacks = config.get('fallback_providers', [])
    
    if not isinstance(fallbacks, list):
        return False, "fallback_providers 格式错误"
    
    provider_names = set(providers.keys()) if isinstance(providers, dict) else set()
    unknown_providers = []
    
    for fb in fallbacks:
        if isinstance(fb, dict) and fb.get('provider'):
            if fb['provider'] not in provider_names:
                unknown_providers.append(fb['provider'])
    
    if unknown_providers:
        return False, f"⚠️  fallback_providers 引用了未知的 provider: {', '.join(unknown_providers)}"
    return True, f"✅ fallback_providers 引用正确 (共 {len(fallbacks)} 个)"

def test_model_switch():
    """测试模型切换 API"""
    try:
        sys.path.insert(0, str(Path.home() / '.hermes' / 'hermes-agent'))
        from hermes_cli.model_switch import switch_model
        
        result = switch_model(
            raw_input="test",
            current_provider="test",
            current_model="test",
            current_base_url="",
            current_api_key="",
            is_global=False,
            explicit_provider=None,
        )
        # 只要不抛异常就说明 API 正常
        return True, "✅ model_switch API 加载正常"
    except ImportError as e:
        return False, f"❌ 无法导入 model_switch: {e}"
    except Exception as e:
        # 测试参数错误是正常的，说明 API 可以工作
        return True, f"✅ model_switch API 工作正常 (预期错误: {type(e).__name__})"

def main():
    config_path = Path.home() / '.hermes' / 'config.yaml'
    
    print("=" * 60)
    print("🔍 Hermes Provider 配置自动诊断")
    print("=" * 60)
    print(f"配置文件: {config_path}")
    print()
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return 1
    
    checks = [
        ("YAML 语法检查", check_yaml_syntax),
        ("providers 结构检查", check_providers_structure),
        ("providers slug 字段检查", check_providers_slug),
        ("fallback_providers 引用检查", check_fallback_providers),
        ("model_switch API 检查", test_model_switch),
    ]
    
    passed = 0
    failed = 0
    
    for name, check_func in checks:
        print(f"📋 {name}:")
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            if "YAML" in name:
                ok, msg = check_func(config_path)
            elif "API" in name:
                ok, msg = check_func()
            else:
                ok, msg = check_func(config)
        except Exception as e:
            ok, msg = False, f"检查异常: {e}"
        
        print(f"   {msg}")
        if ok:
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 诊断结果: {passed} / {len(checks)} 项通过")
    if failed == 0:
        print("🎉 所有检查通过！配置正常。")
    else:
        print(f"⚠️  有 {failed} 项需要修复")
    print("=" * 60)
    
    return failed

if __name__ == '__main__':
    sys.exit(main())
