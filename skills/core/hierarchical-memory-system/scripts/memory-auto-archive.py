#!/usr/bin/env python3
"""
Memory 自动精简归档脚本
功能：
1. 读取 Memory 条目
2. 识别可归档内容（Phase报告、进度条目、技术细节）
3. 迁移到 fact_store
4. 从 Memory 删除
5. 生成精简报告
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# 配置
MEMORY_LIMIT = 5000
AUTO_CLEAN_THRESHOLD = 0.85

HERMES_DIR = Path.home() / ".hermes"
MEMORY_DB = HERMES_DIR / "memory_store.db"

# 需要归档的关键词模式
ARCHIVE_PATTERNS = [
    ("Phase", "项目进度报告"),
    ("完成（", "完成报告"),
    ("修复完成", "修复报告"),
    ("已安装（", "安装通知"),
    ("已完全移除", "移除通知"),
    ("Skill Library 更新完成", "Skill更新"),
    ("检查点", "技术细节"),
]

# 必须保留的关键词
KEEP_PATTERNS = [
    "时间锚定宪法",
    "数据交叉验证原则",
    "网格交易",
    "记忆架构",
    "用户偏好",
    "零容忍",
    "Tushare API",
    "Vibe-Trading",
]


def should_archive(entry):
    """判断条目是否应该归档"""
    for pattern in KEEP_PATTERNS:
        if pattern in entry:
            return False, None
    
    for pattern, reason in ARCHIVE_PATTERNS:
        if pattern in entry:
            return True, reason
    
    return False, None


def archive_to_factstore(entry, reason):
    """将条目归档到 fact_store"""
    try:
        conn = sqlite3.connect(str(MEMORY_DB))
        cursor = conn.cursor()
        
        content = entry[:500]
        category = "project" if "darwin" in entry.lower() else "general"
        
        cursor.execute("""
            INSERT INTO facts (content, category, trust, created_at, tags)
            VALUES (?, ?, 0.8, ?, ?)
        """, (content, category, datetime.now().isoformat(), f"auto-archive,{reason}"))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Error] 归档失败: {e}", file=sys.stderr)
        return False


def main():
    """主函数"""
    memory_file = HERMES_DIR / "memory.json"
    
    if not memory_file.exists():
        print("Memory file not found")
        return
    
    with open(memory_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entries = data.get('entries', [])
    archived_count = 0
    
    for entry in entries[:]:
        should_remove, reason = should_archive(entry)
        if should_remove:
            if archive_to_factstore(entry, reason):
                entries.remove(entry)
                archived_count += 1
    
    if archived_count > 0:
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 归档完成：{archived_count} 条")
    else:
        print("未找到可归档的条目")


if __name__ == "__main__":
    main()
