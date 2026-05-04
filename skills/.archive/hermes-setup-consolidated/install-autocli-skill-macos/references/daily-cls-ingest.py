#!/usr/bin/env python3
"""
每日财联社热门新闻自动抓取入库脚本
适配 Hermes + AutoCLI + Obsidian 工作流
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 配置
VAULT_PATH = Path(os.path.expanduser("~/Documents/Obsidian/AI-NEWS-HUB"))
RAW_DIR = VAULT_PATH / "raw" / "daily-finance"
DAILY_DIR = VAULT_PATH / "daily"

def fetch_cls_hot() -> list:
    """使用autocli抓取财联社热门新闻，然后解析"""
    print("🔍 正在抓取财联社热门新闻...")
    result = subprocess.run(['autocli', 'cls', 'hot'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 抓取失败: {result.stderr}")
        return []
    
    # 解析表格输出
    lines = result.stdout.strip().split('\n')
    data = []
    # 跳过表头分隔线，找到实际数据行
    in_table = False
    header_passed = False
    for line in lines:
        if '+-' in line:  # 分隔线
            in_table = not in_table
            if in_table:
                header_passed = True  # 下一行就是数据了
            continue
        if in_table and line.startswith('|') and header_passed:
            # 拆分列 | rank | title | reading_num | author |
            cols = [col.strip() for col in line.split('|')[1:-1]]
            if len(cols) >= 4:
                rank, title, reading, author = cols[:4]
                if title != 'title':  # 跳过表头行
                    data.append({
                        'rank': rank,
                        'title': title,
                        'reading_num': reading,
                        'author': author
                    })
    print(f"✅ 抓取到 {len(data)} 条热门主题")
    return data

def save_raw(data: list) -> Path:
    """保存原始数据"""
    today = datetime.now().strftime("%Y-%m-%d")
    raw_file = RAW_DIR / f"{today}.json"
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 原始数据已保存: {raw_file}")
    return raw_file

def generate_daily_page(data: list, raw_file: Path) -> Path:
    """生成每日汇总Wiki页面"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = DAILY_DIR / f"{today}.md"
    
    # 生成内容
    content = f"""---
title: 每日财经热点 {today}
created: {today}
updated: {today}
type: daily
tags: [每日汇总]
sources: [{str(raw_file.relative_to(VAULT_PATH))}]
---

# 每日财经热点 {today}

## Top 热门主题

| # | 标题 | 阅读量 | 来源 |
|---|------|--------|------|
"""
    
    for i, item in enumerate(data[:20], 1):
        title = item.get('title', '').strip()
        reading = item.get('reading_num', '')
        author = item.get('author', '-')
        content += f"| {i} | {title} | {reading} | {author} |\n"
    
    content += """

## 热点分析

> （人工补充分析，或AI生成分析）

## 相关链接

<!-- 链接到相关实体/概念页面 -->

"""
    
    with open(daily_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📄 每日汇总页面已生成: {daily_file}")
    return daily_file

def update_index():
    """更新index.md"""
    index_path = VAULT_PATH / "index.md"
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 统计页面数量
    def count_md(directory):
        return len(list(Path(directory).glob('*.md')))
    
    total = sum([
        count_md(VAULT_PATH / "entities"),
        count_md(VAULT_PATH / "concepts"),
        count_md(VAULT_PATH / "comparisons"),
        count_md(VAULT_PATH / "queries"),
        count_md(VAULT_PATH / "daily")
    ])
    
    # 读取现有内容
    with open(index_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新表头的最新更新和总页数
    new_lines = []
    for line in lines:
        if line.startswith('> 最新更新：'):
            new_lines.append(f'> 最新更新：{today} | 总页数：{total}\n')
        elif '## 每日汇总' in line:
            new_lines.append(line)
            # 添加今日链接
            new_lines.append(f"- [[{today}]] 每日财经热点汇总\n")
        else:
            new_lines.append(line)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"🔄 index.md 已更新")

def update_log():
    """更新log.md"""
    log_path = VAULT_PATH / "log.md"
    today = datetime.now().strftime("%Y-%m-%d")
    
    entry = f"\n## [{today}] daily-ingest | 财联社每日热门新闻自动抓取\n- 原始数据保存到 raw/daily-finance/{today}.json\n- 生成每日汇总页面 daily/{today}.md\n- 更新 index.md\n"
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    print(f"📝 log.md 已更新")

def main():
    # 确保目录存在
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    
    # 抓取
    data = fetch_cls_hot()
    if not data:
        print("❌ 没有获取到数据")
        return 1
    
    # 保存原始
    raw_file = save_raw(data)
    
    # 生成页面
    daily_file = generate_daily_page(data, raw_file)
    
    # 更新索引
    update_index()
    
    # 更新日志
    update_log()
    
    print(f"\n✅ 完成！今日热点已入库")
    print(f"   原始数据: {raw_file}")
    print(f"   每日页面: {daily_file}")
    print(f"   在Obsidian中打开即可查看")
    
    return 0

if __name__ == "__main__":
    exit(main())