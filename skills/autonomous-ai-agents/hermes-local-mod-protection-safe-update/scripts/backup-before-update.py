#!/usr/bin/env python3
"""
保守式更新前的一键备份脚本
用途：在 Hermes Agent context-mode 环境下安全创建备份

使用方法：
    python3 scripts/backup-before-update.py [--patch] [--workflows]

参数：
    --patch      备份所有本地修改（git diff origin/main..HEAD）
    --workflows  备份 .github/workflows 目录
"""

import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path


def backup_patch():
    """创建 Git patch 备份"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path.home() / ".hermes" / "patch-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取本地所有修改
    result = subprocess.run(
        ["git", "diff", "origin/main..HEAD"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Git diff 失败: {result.stderr}")
        return None
    
    patch_file = backup_dir / f"pre-update-{timestamp}.patch"
    patch_file.write_text(result.stdout)
    
    size_mb = len(result.stdout) / 1024 / 1024
    print(f"✅ Patch 备份完成: {patch_file}")
    print(f"   大小: {size_mb:.2f} MB")
    
    return patch_file


def backup_workflows():
    """备份 workflows 目录"""
    workflows_dir = Path(".github/workflows")
    
    if not workflows_dir.exists():
        print("ℹ️  workflows 目录不存在，无需备份")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = Path(f"/tmp/workflows_backup_{timestamp}.tar.gz")
    
    result = subprocess.run(
        ["tar", "-czf", str(backup_file), ".github/workflows"],
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f"❌ workflows 备份失败: {result.stderr.decode()}")
        return None
    
    print(f"✅ workflows 备份完成: {backup_file}")
    return backup_file


def main():
    backup_patch_flag = "--patch" in sys.argv
    backup_workflows_flag = "--workflows" in sys.argv
    
    # 默认：两个都备份
    if not backup_patch_flag and not backup_workflows_flag:
        backup_patch_flag = True
        backup_workflows_flag = True
    
    print("🔒 保守式更新前备份")
    print("=" * 50)
    
    if backup_patch_flag:
        backup_patch()
    
    if backup_workflows_flag:
        backup_workflows()
    
    print("=" * 50)
    print("✅ 备份完成，可以安全执行 rebase")


if __name__ == "__main__":
    main()
