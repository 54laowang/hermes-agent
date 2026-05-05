#!/usr/bin/env python3
"""
搜索记忆维护器
在 web_search 完成后自动将结果追加到 search.md
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path


def append_to_search_memory(query: str, results: list, max_results: int = 5):
    """将搜索结果追加到 search.md"""
    
    search_file = Path.home() / ".hermes" / "search.md"
    search_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 初始化文件
    if not search_file.exists():
        search_file.write_text("""# Search Memory - 持续搜索上下文

所有 web_search 结果自动归档，超过 7 天自动摘要压缩。

---
""", encoding="utf-8")
    
    now = datetime.now()
    timestamp = now.strftime("%H:%M")
    today_header = f"## {now.strftime('%Y-%m-%d')}"
    
    content = search_file.read_text(encoding="utf-8")
    
    # 检查今天的日期头是否存在
    if today_header not in content:
        content += f"\n{today_header}\n\n"
    
    # 格式化搜索结果
    entry = f"### {timestamp} - {query}\n\n"
    for i, result in enumerate(results[:max_results], 1):
        title = result.get("title", "")
        description = result.get("description", "")
        url = result.get("url", "")
        
        if title:
            entry += f"- {title}\n"
        if description:
            entry += f"  {description[:100]}...\n" if len(description) > 100 else f"  {description}\n"
        if url:
            entry += f"  🔗 {url}\n"
    
    entry += "\n"
    
    # 追加到今天的条目下
    if today_header in content:
        parts = content.split(today_header)
        content = parts[0] + today_header + "\n" + entry + parts[1]
    else:
        content += today_header + "\n\n" + entry
    
    # 写回文件
    search_file.write_text(content, encoding="utf-8")
    
    return {
        "status": "success",
        "file": str(search_file),
        "results_appended": min(len(results), max_results)
    }


def main():
    if len(sys.argv) > 1:
        # 命令行模式：python search-memory.py "query" results.json
        query = sys.argv[1]
        if len(sys.argv) > 2:
            with open(sys.argv[2], encoding="utf-8") as f:
                results = json.load(f)
        else:
            results = json.loads(sys.stdin.read())
        
        result = append_to_search_memory(query, results)
        print(json.dumps(result, ensure_ascii=False))
    else:
        # Hermes hook 模式
        payload = json.loads(sys.stdin.read())
        query = payload.get("extra", {}).get("search_query", "")
        results = payload.get("extra", {}).get("search_results", [])
        
        if query and results:
            result = append_to_search_memory(query, results)
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("{}")


if __name__ == "__main__":
    main()
