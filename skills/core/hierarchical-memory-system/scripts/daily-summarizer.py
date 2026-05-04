#!/usr/bin/env python3
"""
每日摘要生成器 - L1 → L2
每天 23:55 自动运行，将当天的对话提取成核心要点摘要
v2.0: 增加批量事实提取到 fact_store
"""

import json
import os
import sys
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"
SESSIONS_DIR = HERMES_DIR / "sessions"
L2_MEMORY_DIR = HERMES_DIR / "memory" / "short-term"
FACT_STORE_DB = HERMES_DIR / "memory_store.db"

# 触发关键词
TRIGGER_KEYWORDS = [
    "记住", "记得", "别忘了", "下次", "以后",
    "偏好", "喜欢", "不喜欢", "不要",
    "我习惯", "我一般", "我总是",
    "设置为", "默认为",
    "路径是", "地址是", "在哪个目录", "位置是",
    "核心是", "本质是", "关键是",
    "这个项目", "这个仓库", "这个系统",
    "工作时间", "夜班", "早班",
]

# 否定关键词
NEGATIVE_KEYWORDS = [
    "?", "？", "吗", "呢", "吧", "嘛",
    "你记住", "你记得",
]


def contains_trigger(text: str) -> bool:
    """检测文本是否包含记忆触发词"""
    for neg in NEGATIVE_KEYWORDS:
        if neg in text:
            return False
    for kw in TRIGGER_KEYWORDS:
        if kw in text:
            return True
    return False


def classify_fact(text: str) -> str:
    """分类事实"""
    if any(kw in text for kw in ["喜欢", "偏好", "不喜欢", "不要", "习惯"]):
        return "user_pref"
    elif any(kw in text for kw in ["项目", "仓库", "代码", "系统"]):
        return "project"
    elif any(kw in text for kw in ["命令", "工具", "路径", "配置"]):
        return "tool"
    else:
        return "general"


def add_fact_to_store(content: str, category: str, tags: str = "") -> bool:
    """添加事实到 fact_store"""
    try:
        conn = sqlite3.connect(str(FACT_STORE_DB))
        cursor = conn.cursor()
        
        # 检查重复
        cursor.execute(
            "SELECT id FROM facts WHERE content = ? AND category = ?",
            (content, category)
        )
        if cursor.fetchone():
            conn.close()
            return False
        
        # 插入新事实
        cursor.execute("""
            INSERT INTO facts (content, category, tags, trust_score, created_at, updated_at)
            VALUES (?, ?, ?, 0.5, ?, ?)
        """, (content, category, tags, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        fact_id = cursor.lastrowid
        conn.close()
        return True
    except Exception as e:
        return False


def get_today_sessions() -> list:
    """获取今天所有的 session 文件"""
    today = datetime.now().strftime("%Y-%m-%d")
    sessions = []
    
    for session_file in SESSIONS_DIR.glob("*.json"):
        try:
            mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
            if mtime.strftime("%Y-%m-%d") == today:
                sessions.append(session_file)
        except:
            pass
    
    return sorted(sessions, key=lambda f: f.stat().st_mtime)


def extract_session_summary(session_file: Path, max_chars: int = 2000) -> dict:
    """从单个 session 中提取摘要和潜在事实"""
    try:
        with open(session_file, "r", encoding="utf-8") as f:
            session = json.load(f)
        
        messages = session.get("messages", [])
        if not messages:
            return None
        
        # 统计基本信息
        user_messages = [m for m in messages if m.get("role") == "user"]
        assistant_messages = [m for m in messages if m.get("role") == "assistant"]
        tool_calls = [m for m in messages if m.get("role") == "tool"]
        
        # 提取核心话题
        topics = []
        potential_facts = []
        
        for msg in user_messages:
            content = msg.get("content", "")
            if isinstance(content, str) and len(content) > 5:
                # 话题
                if len(topics) < 5:
                    topics.append(content[:50] + ("..." if len(content) > 50 else ""))
                
                # 潜在事实
                if contains_trigger(content):
                    potential_facts.append(content)
        
        return {
            "session_id": session_file.stem,
            "start_time": datetime.fromtimestamp(session_file.stat().st_mtime).strftime("%H:%M"),
            "turns": len(messages),
            "user_messages": len(user_messages),
            "tool_calls": len(tool_calls),
            "topics": topics[:3],
            "potential_facts": potential_facts,
        }
        
    except Exception as e:
        return None


def generate_daily_summary(today: str = None) -> tuple:
    """生成每日摘要 + 提取事实，返回 (摘要内容, 提取的事实列表)"""
    if today is None:
        today = datetime.now().strftime("%Y-%m-%d")
    
    sessions = get_today_sessions()
    if not sessions:
        return f"# {today} 记忆摘要\n\n今天没有对话记录。\n", []
    
    summaries = [extract_session_summary(s) for s in sessions]
    summaries = [s for s in summaries if s]
    
    # 聚合所有话题和事实
    all_topics = []
    all_facts = []
    total_turns = 0
    total_tools = 0
    
    for s in summaries:
        all_topics.extend(s["topics"])
        all_facts.extend(s.get("potential_facts", []))
        total_turns += s["turns"]
        total_tools += s["tool_calls"]
    
    # 去重事实
    unique_facts = list(set(all_facts))
    
    # 生成 markdown
    content = f"""# {today} 记忆摘要

## 今日概览
- 会话数：{len(sessions)} 个
- 对话轮次：{total_turns} 轮
- 工具调用：{total_tools} 次

## 核心话题
"""
    
    for i, topic in enumerate(all_topics[:10], 1):
        content += f"{i}. {topic}\n"
    
    if not all_topics:
        content += "（无记录）\n"
    
    content += "\n## 会话详情\n\n"
    for i, s in enumerate(summaries, 1):
        content += f"### 会话 {i} ({s['start_time']})\n"
        content += f"- 对话轮次：{s['turns']} 轮\n"
        content += f"- 工具调用：{s['tool_calls']} 次\n"
        if s["topics"]:
            content += f"- 主要话题：{s['topics'][0]}\n"
        content += "\n"
    
    # 自动提取的事实
    if unique_facts:
        content += "## 自动提取的事实\n\n"
        for fact in unique_facts:
            content += f"- {fact}\n"
        content += "\n"
    else:
        content += """## 用户偏好记录
> （自动提取用户说过的偏好）

（本次未检测到明确偏好）

## 重要事实
> （用户提到的需要长期记住的事实）

（本次未检测到重要事实）

"""
    
    content += """## 已完成任务
> （今天完成的重要工作）

- 

"""
    
    return content, unique_facts


def save_facts_to_store(facts: list) -> int:
    """批量保存事实到 fact_store"""
    saved = 0
    for fact in facts:
        category = classify_fact(fact)
        tags = "auto-extracted,daily_summarizer"
        if add_fact_to_store(fact, category, tags):
            saved += 1
    return saved


def save_daily_summary(content: str, today: str = None):
    """保存每日摘要到 L2 记忆"""
    if today is None:
        today = datetime.now().strftime("%Y-%m-%d")
    
    L2_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    summary_file = L2_MEMORY_DIR / f"{today}.md"
    
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    return summary_file


def cleanup_expired(days: int = 7):
    """清理超过 N 天的 L2 记忆"""
    cutoff = datetime.now() - timedelta(days=days)
    
    deleted = 0
    for md_file in L2_MEMORY_DIR.glob("*.md"):
        try:
            file_date = datetime.strptime(md_file.stem, "%Y-%m-%d")
            if file_date < cutoff:
                md_file.unlink()
                deleted += 1
        except:
            pass
    
    return deleted


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="每日摘要生成器 v2.0")
    parser.add_argument("--date", help="指定日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--cleanup", type=int, default=7, help="清理 N 天前的记忆")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不保存")
    parser.add_argument("--no-fact-store", action="store_true", help="不保存到 fact_store")
    
    args = parser.parse_args()
    
    print(f"🧠 分层记忆系统 - 每日摘要生成器 v2.0")
    print(f"=" * 50)
    
    # 生成摘要
    summary, facts = generate_daily_summary(args.date)
    print(f"\n📝 生成的摘要：\n")
    print(summary)
    
    if facts:
        print(f"\n🔍 检测到 {len(facts)} 条潜在事实")
    
    if not args.dry_run:
        today = args.date or datetime.now().strftime("%Y-%m-%d")
        saved_file = save_daily_summary(summary, today)
        print(f"\n✅ 已保存到：{saved_file}")
        
        # 批量保存事实
        if facts and not args.no_fact_store:
            saved_facts = save_facts_to_store(facts)
            if saved_facts > 0:
                print(f"📊 已保存 {saved_facts} 条事实到 fact_store")
        
        # 清理过期
        deleted = cleanup_expired(args.cleanup)
        if deleted > 0:
            print(f"🗑️  清理了 {deleted} 个过期的 L2 记忆（超过 {args.cleanup} 天）")
    
    print(f"\n✅ 完成！")


if __name__ == "__main__":
    main()
