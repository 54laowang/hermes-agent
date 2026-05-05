#!/usr/bin/env python3
"""
Memory 使用率检查（轻量级）
用途：快速返回 Memory 使用率，用于 Shell Hook 或 Cronjob
性能：<50ms
"""

import json
from pathlib import Path

MEMORY_LIMIT = 5000

def main():
    memory_file = Path.home() / ".hermes" / "memory.json"
    
    if not memory_file.exists():
        print("0.00")
        return
    
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = data.get('entries', [])
        total_chars = sum(len(entry) for entry in entries)
        usage = total_chars / MEMORY_LIMIT
        
        print(f"{usage:.2f}")
    
    except Exception:
        print("0.00")

if __name__ == "__main__":
    main()
