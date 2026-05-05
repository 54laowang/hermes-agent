#!/usr/bin/env python3
"""
手动压缩 L2 短期记忆 - 当 daily-summarizer-v3.py 超时时使用
用法：python manual-compress-l2.py [YYYY-MM-DD]
"""

import sys
from pathlib import Path
from datetime import datetime

def compress_l2(date_str: str = None):
    """压缩指定日期的 L2 记忆"""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    l2_file = Path.home() / f".hermes/memory/short-term/{date_str}.md"
    
    if not l2_file.exists():
        print(f"❌ 文件不存在：{l2_file}")
        return False
    
    content = l2_file.read_text()
    lines = content.split('\n')
    
    # 提取会话和话题
    sessions = []
    current_session = None
    
    for line in lines:
        if line.startswith('### 会话'):
            if current_session:
                sessions.append(current_session)
            current_session = {'title': line, 'topics': []}
        elif current_session and line.startswith('- 主要话题：'):
            topic = line.replace('- 主要话题：', '').strip()
            current_session['topics'].append(topic)
    
    if current_session:
        sessions.append(current_session)
    
    # 提取核心话题（去重）
    core_topics = []
    seen = set()
    for s in sessions:
        for t in s['topics']:
            if t and t not in seen and len(t) > 3:
                core_topics.append(t)
                seen.add(t)
    
    # 生成压缩摘要
    summary = f"""# {date_str} 记忆摘要

## 今日概览
- 会话数：{len(sessions)} 个
- 核心话题：{len(core_topics)} 个
- 主要工作：（请手动补充）

## 核心话题（前10个）
{chr(10).join(f'{i+1}. {t}' for i, t in enumerate(core_topics[:10]))}

## 重要成果
- （请手动补充）

## 用户偏好更新
- 无新增偏好

## 技术知识沉淀
- （请手动补充）

## 归档记录
- fact_store: （请手动补充）
- MemPalace: （请手动补充）
- Git提交: （请手动补充）
"""
    
    # 备份原文件
    backup_file = l2_file.with_suffix('.md.bak')
    backup_file.write_text(content)
    
    # 保存压缩文件
    l2_file.write_text(summary)
    
    print(f"✅ 压缩完成！")
    print(f"原文：{len(content)} 字符 → {len(content)//1024} KB")
    print(f"压缩后：{len(summary)} 字符")
    print(f"压缩率：{(1 - len(summary)/len(content))*100:.1f}%")
    print(f"备份：{backup_file}")
    
    return True

if __name__ == "__main__":
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    compress_l2(date_str)
