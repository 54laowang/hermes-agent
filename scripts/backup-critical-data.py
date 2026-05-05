#!/usr/bin/env python3
"""
定期备份关键数据：jobs.json, memory_store.db, .env, config.yaml, memories/
"""
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
BACKUP_DIR = HERMES_HOME / "backups"
MAX_BACKUPS = 7  # 保留最近7天的备份

def backup_critical_data():
    """备份关键数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # 备份文件列表
    critical_files = [
        "cron/jobs.json",
        "memory_store.db",
        ".env",
        "config.yaml",
        "auth.json",
    ]
    
    # 备份目录列表
    critical_dirs = [
        "memories",
        "memory",
    ]
    
    backed_up = []
    
    # 备份文件
    for f in critical_files:
        src = HERMES_HOME / f
        if src.exists():
            dst = backup_path / f
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            backed_up.append(f)
    
    # 备份目录
    for d in critical_dirs:
        src = HERMES_HOME / d
        if src.exists():
            dst = backup_path / d
            shutil.copytree(src, dst, dirs_exist_ok=True)
            backed_up.append(f"{d}/")
    
    # 清理旧备份
    cleanup_old_backups()
    
    # Git commit
    try:
        subprocess.run(["git", "add", "cron/jobs.json"], cwd=HERMES_HOME, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"backup: {timestamp}"], cwd=HERMES_HOME, capture_output=True)
    except:
        pass  # 可能没有变化
    
    return backed_up

def cleanup_old_backups():
    """清理旧备份，保留最近 MAX_BACKUPS 个"""
    if not BACKUP_DIR.exists():
        return
    
    backups = sorted(BACKUP_DIR.iterdir(), key=lambda x: x.name, reverse=True)
    for old in backups[MAX_BACKUPS:]:
        shutil.rmtree(old, ignore_errors=True)
        print(f"清理旧备份: {old.name}")

if __name__ == "__main__":
    backed_up = backup_critical_data()
    print(f"备份完成 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):")
    for f in backed_up:
        print(f"  ✓ {f}")
