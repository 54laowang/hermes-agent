#!/usr/bin/env python3
"""
Hermes API Key 环境变量一键迁移脚本
自动提取 config.yaml 中的硬编码 Key → 替换为环境变量引用 → 验证结果

使用方法:
    python3 migrate-secrets-to-env.py
"""

import yaml
import os
import sys
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path.home() / ".hermes" / "config.yaml"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "ai.hermes.gateway.plist"
GITIGNORE_PATH = Path.home() / ".hermes" / ".gitignore"
ZSHRC_PATH = Path.home() / ".zshrc"

BACKUP_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = Path.home() / f".hermes/config.yaml.backup.{BACKUP_TIMESTAMP}"


def banner(text):
    """打印分隔标题"""
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")


def step(step_num, text):
    """打印步骤"""
    print(f"\n📌 步骤 {step_num}: {text}")


def backup_config():
    """备份当前配置"""
    if not CONFIG_PATH.exists():
        print(f"❌ 配置文件不存在: {CONFIG_PATH}")
        sys.exit(1)
    
    import shutil
    shutil.copy2(CONFIG_PATH, BACKUP_PATH)
    print(f"✅ 已备份到: {BACKUP_PATH.name}")
    return BACKUP_PATH


def extract_unique_keys(config):
    """从配置中提取所有唯一的 API Key"""
    all_keys = {}
    
    def collect_keys(obj, prefix=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "api_key" and isinstance(v, str) and len(v) > 10:
                    if v not in all_keys:
                        all_keys[v] = []
                    all_keys[v].append(f"{prefix}.{k}" if prefix else k)
                else:
                    collect_keys(v, f"{prefix}.{k}" if prefix else k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                collect_keys(item, f"{prefix}[{i}]" if prefix else f"[{i}]")
    
    collect_keys(config)
    
    # 分类
    categorized = {"ark": [], "modelscope": [], "edgefn": [], "other": []}
    for key, paths in all_keys.items():
        if key.startswith("ark-") or key.startswith("d4ce") or len(key) == 36:
            categorized["ark"].append((key, paths))
        elif key.startswith("ms-"):
            categorized["modelscope"].append((key, paths))
        elif key.startswith("sk-"):
            categorized["edgefn"].append((key, paths))
        else:
            categorized["other"].append((key, paths))
    
    return all_keys, categorized


def get_key_map(categorized):
    """获取 key -> env_var 映射"""
    key_map = {}
    env_vars = {}
    
    # 取每个分类的第一个作为代表值
    for cat_name, items in categorized.items():
        if items:
            if cat_name == "ark":
                env_var = "ARK_API_KEY"
            elif cat_name == "modelscope":
                env_var = "MODELSCOPE_API_KEY"
            elif cat_name == "edgefn":
                env_var = "EDGEFN_API_KEY"
            else:
                env_var = f"{cat_name.upper()}_API_KEY"
            
            # 使用出现次数最多的 key 作为代表
            all_keys_for_cat = [k for k, paths in items]
            representative_key = max(all_keys_for_cat, key=lambda k: sum(len(p) for _, p in items if _ == k))
            
            key_map[representative_key] = env_var
            env_vars[env_var] = representative_key
            
            # 为同类中的其他 key 也建立映射
            for key, _ in items:
                if key not in key_map:
                    key_map[key] = env_var
    
    return key_map, env_vars


def replace_with_env_vars(config, key_map):
    """递归替换配置中的 API Key 为环境变量引用"""
    
    def replace_obj(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "api_key" and isinstance(v, str):
                    if v in key_map:
                        obj[k] = f"${{{key_map[v]}}}"
                else:
                    replace_obj(v)
        elif isinstance(obj, list):
            for item in obj:
                replace_obj(item)
    
    replace_obj(config)
    return config


def verify_migration(original_config, migrated_config):
    """验证迁移结果"""
    banner("迁移验证")
    
    # 统计原配置中的硬编码
    original_keys = set()
    def count_keys(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "api_key" and isinstance(v, str) and len(v) > 10:
                    original_keys.add(v)
                else:
                    count_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                count_keys(item)
    count_keys(original_config)
    
    # 统计迁移后的环境变量引用
    env_refs = set()
    def count_env_refs(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "api_key" and isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                    env_refs.add(v)
                else:
                    count_env_refs(v)
        elif isinstance(obj, list):
            for item in obj:
                count_env_refs(item)
    count_env_refs(migrated_config)
    
    # 统计残留的硬编码
    remaining_hardcoded = set()
    def count_remaining(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "api_key" and isinstance(v, str) and len(v) > 10 and not (v.startswith("${") and v.endswith("}")):
                    remaining_hardcoded.add(v)
                else:
                    count_remaining(v)
        elif isinstance(obj, list):
            for item in obj:
                count_remaining(item)
    count_remaining(migrated_config)
    
    print(f"原配置中唯一 API Key: {len(original_keys)} 个")
    print(f"迁移后环境变量引用: {len(env_refs)} 个 ({', '.join(env_refs)})")
    print(f"残留硬编码 Key: {len(remaining_hardcoded)} 个")
    
    if remaining_hardcoded:
        print("\n⚠️  残留的硬编码 Key（可能在注释中）:")
        for key in remaining_hardcoded:
            print(f"  - {key[:20]}...")
    
    success = len(env_refs) >= len(original_keys) - len(remaining_hardcoded)
    if success:
        print("\n✅ 迁移验证通过！")
    else:
        print("\n❌ 迁移验证不完整")
    
    return success, env_refs


def update_gitignore():
    """更新 .gitignore 添加敏感文件规则"""
    rules = [
        "config.yaml",
        "*.key",
        "*.pem",
        "secrets/",
        ".env*",
        "certs/"
    ]
    
    existing_rules = set()
    if GITIGNORE_PATH.exists():
        with open(GITIGNORE_PATH, 'r') as f:
            existing_rules = set(line.strip() for line in f if line.strip())
    
    new_rules = [r for r in rules if r not in existing_rules]
    
    if new_rules:
        with open(GITIGNORE_PATH, 'a') as f:
            f.write("\n# Sensitive Files - Added by secrets migration\n")
            for r in new_rules:
                f.write(f"{r}\n")
        print(f"✅ .gitignore 已添加 {len(new_rules)} 条新规则")
    else:
        print("ℹ️  .gitignore 已有敏感文件规则，跳过")


def update_zshrc(env_vars):
    """更新 ~/.zshrc 添加环境变量"""
    env_block_lines = ["\n# Hermes Agent API Keys (auto-added by secrets migration)"]
    for var, value in env_vars.items():
        env_block_lines.append(f"export {var}='{value}'")
    env_block = "\n".join(env_block_lines) + "\n"
    
    if ZSHRC_PATH.exists():
        with open(ZSHRC_PATH, 'r') as f:
            content = f.read()
        
        if "# Hermes Agent API Keys" in content:
            print("ℹ️  ~/.zshrc 已有 Hermes API Key 配置，跳过")
        else:
            with open(ZSHRC_PATH, 'a') as f:
                f.write(env_block)
            print("✅ ~/.zshrc 已添加环境变量")


def update_launchd_plist(env_vars):
    """更新 launchd plist 添加环境变量"""
    if not PLIST_PATH.exists():
        print("ℹ️  launchd plist 不存在，跳过")
        return
    
    try:
        import plistlib
        
        with open(PLIST_PATH, 'rb') as f:
            plist = plistlib.load(f)
        
        plist['EnvironmentVariables'] = {k: v for k, v in env_vars.items()}
        
        with open(PLIST_PATH, 'wb') as f:
            plistlib.dump(plist, f, sort_keys=False)
        
        print("✅ launchd plist 已更新环境变量")
        print("\n🔄 需要重新加载 plist 才能生效:")
        print("  launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway.plist")
        print("  launchctl load ~/Library/LaunchAgents/ai.hermes.gateway.plist")
    except Exception as e:
        print(f"⚠️  更新 plist 失败: {e}")


def save_migrated_config(config):
    """保存迁移后的配置"""
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print("✅ 迁移后的配置已保存")


def main():
    banner("Hermes API Key 环境变量一键迁移")
    
    # 步骤 1: 备份
    step(1, "备份当前配置")
    backup_path = backup_config()
    
    # 步骤 2: 读取并提取 Key
    step(2, "分析配置文件，提取唯一 API Key")
    with open(CONFIG_PATH, 'r') as f:
        original_config = yaml.safe_load(f)
    
    all_keys, categorized = extract_unique_keys(original_config)
    
    print(f"\n找到 {len(all_keys)} 个唯一 API Key:")
    for cat, items in categorized.items():
        if items:
            print(f"  {cat.upper()}: {len(items)} 个 Key, 出现在 {sum(len(p) for _, p in items)} 处")
            for key, paths in items[:2]:  # 只显示前2个位置
                print(f"    - {key[:20]}... @ {paths[0]}")
            if len(items) > 2:
                print(f"    - ... 还有 {len(items) - 2} 个")
    
    # 步骤 3: 建立映射
    step(3, "建立 Key → 环境变量映射")
    key_map, env_vars = get_key_map(categorized)
    
    print(f"\n映射关系:")
    for key, env_var in key_map.items():
        print(f"  {key[:20]}... -> {env_var}")
    
    # 步骤 4: 执行替换
    step(4, "替换所有 API Key 为环境变量引用")
    migrated_config = replace_with_env_vars(original_config, key_map)
    
    # 步骤 5: 验证
    success, env_refs = verify_migration(original_config, migrated_config)
    
    if not success:
        print("\n⚠️  迁移不完整，请检查后重试")
        response = input("是否继续保存？(y/N): ").strip().lower()
        if response != 'y':
            print("❌ 已取消，配置未修改")
            return
    
    # 步骤 6: 保存
    step(5, "保存迁移后的配置")
    save_migrated_config(migrated_config)
    
    # 步骤 7: 更新配套文件
    step(6, "更新配套文件 (.gitignore, .zshrc, plist)")
    update_gitignore()
    update_zshrc(env_vars)
    update_launchd_plist(env_vars)
    
    # 完成
    banner("迁移完成！")
    print("\n📋 后续操作:")
    print("  1. 重新加载 shell 环境（新开终端或 source ~/.zshrc）")
    print("  2. 重启网关: hermes gateway restart")
    print("  3. 验证服务: python3 ~/.hermes/scripts/health-check.py")
    print("\n🔄 如需回滚:")
    print(f"  cp {BACKUP_PATH} ~/.hermes/config.yaml && hermes gateway restart")


if __name__ == "__main__":
    main()
