#!/usr/bin/env python3
"""
每日摘要生成器 v3.0 - LLM 增强版
增强功能：
1. 使用 LLM 提取关键信息（用户偏好、重要决策、学到的东西）
2. 自动升级高价值信息到 L3（fact_store + long-term/）
3. 生成结构化摘要，提升跨会话记忆连贯性
"""

import json
import os
import sys
import sqlite3
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

HERMES_DIR = Path.home() / ".hermes"
SESSIONS_DIR = HERMES_DIR / "sessions"
L2_MEMORY_DIR = HERMES_DIR / "memory" / "short-term"
L3_MEMORY_DIR = HERMES_DIR / "memory" / "long-term"
FACT_STORE_DB = HERMES_DIR / "memory_store.db"

# Hermes Provider API 配置
HERMES_API_URL = os.getenv("HERMES_API_URL", "http://localhost:8642/v1/chat/completions")
HERMES_API_KEY = os.getenv("HERMES_API_KEY", "SV1a9QQO4kPAzHs-Ki-VbUvQJGf4uFZVqC7cBS8AheM")

# 触发关键词（保留原有）
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


def call_llm(messages: List[Dict[str, str]], max_tokens: int = 1000) -> Optional[str]:
    """调用 Hermes Provider API"""
    try:
        headers = {
            "Content-Type": "application/json",
        }
        if HERMES_API_KEY:
            headers["Authorization"] = f"Bearer {HERMES_API_KEY}"
        
        payload = {
            "model": "default",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }
        
        response = requests.post(HERMES_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"⚠️ LLM API 调用失败: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⚠️ LLM API 超时（30s），建议使用手动压缩：python scripts/manual-compress-l2.py")
        return None
    except Exception as e:
        print(f"⚠️ LLM 调用异常: {e}")
        return None


def extract_with_llm(session_content: str) -> Dict[str, Any]:
    """使用 LLM 提取结构化信息"""
    
    prompt = f"""请分析以下对话内容，提取关键信息。要求：
1. 提取用户明确表达的偏好（用户说过的"我喜欢"、"下次"、"记住"等）
2. 提取重要决策和结论
3. 提取学到的知识和技术要点
4. 提取完成的重要任务

对话内容（部分）：
{session_content[:3000]}

请以 JSON 格式返回，结构如下：
{{
  "user_preferences": ["偏好1", "偏好2"],
  "important_decisions": ["决策1", "决策2"],
  "learned_knowledge": ["知识点1", "知识点2"],
  "completed_tasks": ["任务1", "任务2"],
  "key_topics": ["话题1", "话题2"]
}}

注意：
- 只提取用户明确表达的信息，不要推测
- 偏好要具体（如"偏好中文回复"、"喜欢表格形式"）
- 如果某个类别没有内容，返回空数组
- 必须返回有效的 JSON 格式"""

    messages = [
        {"role": "system", "content": "你是专业的对话分析助手，擅长提取结构化信息。"},
        {"role": "user", "content": prompt}
    ]
    
    result = call_llm(messages, max_tokens=800)
    
    if result:
        try:
            # 提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"⚠️ JSON 解析失败: {e}")
    
    # 降级返回空结构
    return {
        "user_preferences": [],
        "important_decisions": [],
        "learned_knowledge": [],
        "completed_tasks": [],
        "key_topics": []
    }


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
            VALUES (?, ?, ?, 0.7, ?, ?)
        """, (content, category, tags, datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        fact_id = cursor.lastrowid
        conn.close()
        return True
    except Exception as e:
        return False


def save_to_long_term(category: str, content: str, date_str: str):
    """保存到 L3 长期记忆"""
    try:
        category_file = L3_MEMORY_DIR / f"{category}.md"
        L3_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        
        # 追加到文件
        with open(category_file, "a", encoding="utf-8") as f:
            f.write(f"\n- [{date_str}] {content}")
        
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


def read_session_content(session_file: Path, max_messages: int = 50) -> str:
    """读取 session 文件内容，提取对话文本"""
    try:
        with open(session_file, "r", encoding="utf-8") as f:
            session = json.load(f)
        
        messages = session.get("messages", [])
        content_lines = []
        
        for msg in messages[:max_messages]:
            role = msg.get("role", "unknown")
            text = msg.get("content", "")
            if isinstance(text, str) and len(text) > 5:
                content_lines.append(f"[{role}]: {text[:200]}")
        
        return "\n".join(content_lines)
        
    except Exception as e:
        return ""


def extract_session_summary(session_file: Path) -> dict:
    """从单个 session 中提取摘要"""
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
        
        # 读取对话内容
        session_content = read_session_content(session_file)
        
        # 使用 LLM 提取
        llm_result = {}
        if session_content and len(session_content) > 100:
            llm_result = extract_with_llm(session_content)
        
        return {
            "session_id": session_file.stem,
            "start_time": datetime.fromtimestamp(session_file.stat().st_mtime).strftime("%H:%M"),
            "turns": len(messages),
            "user_messages": len(user_messages),
            "tool_calls": len(tool_calls),
            "llm_extracted": llm_result,
            "raw_content": session_content[:500],  # 保留部分原始内容用于降级
        }
        
    except Exception as e:
        return None


def generate_daily_summary(today: str = None) -> tuple:
    """生成每日摘要 + 提取事实，返回 (摘要内容, 结构化信息)"""
    if today is None:
        today = datetime.now().strftime("%Y-%m-%d")
    
    sessions = get_today_sessions()
    if not sessions:
        return f"# {today} 记忆摘要\n\n今天没有对话记录。\n", {}
    
    summaries = [extract_session_summary(s) for s in sessions]
    summaries = [s for s in summaries if s]
    
    # 聚合 LLM 提取的信息
    all_preferences = []
    all_decisions = []
    all_knowledge = []
    all_tasks = []
    all_topics = []
    total_turns = 0
    total_tools = 0
    
    for s in summaries:
        llm_data = s.get("llm_extracted", {})
        all_preferences.extend(llm_data.get("user_preferences", []))
        all_decisions.extend(llm_data.get("important_decisions", []))
        all_knowledge.extend(llm_data.get("learned_knowledge", []))
        all_tasks.extend(llm_data.get("completed_tasks", []))
        all_topics.extend(llm_data.get("key_topics", []))
        total_turns += s["turns"]
        total_tools += s["tool_calls"]
    
    # 去重
    all_preferences = list(set(all_preferences))
    all_decisions = list(set(all_decisions))
    all_knowledge = list(set(all_knowledge))
    all_tasks = list(set(all_tasks))
    all_topics = list(set(all_topics))
    
    # 生成 markdown
    content = f"""# {today} 记忆摘要

## 今日概览
- 会话数：{len(sessions)} 个
- 对话轮次：{total_turns} 轮
- 工具调用：{total_tools} 次

"""
    
    # 核心话题
    if all_topics:
        content += "## 核心话题\n\n"
        for i, topic in enumerate(all_topics[:10], 1):
            content += f"{i}. {topic}\n"
        content += "\n"
    
    # 用户偏好记录
    if all_preferences:
        content += "## 用户偏好记录\n\n"
        for pref in all_preferences:
            content += f"- {pref}\n"
        content += "\n"
    else:
        content += """## 用户偏好记录
> （自动提取用户说过的偏好）

（本次未检测到明确偏好）

"""
    
    # 重要决策
    if all_decisions:
        content += "## 重要决策\n\n"
        for decision in all_decisions:
            content += f"- {decision}\n"
        content += "\n"
    
    # 学到的知识
    if all_knowledge:
        content += "## 学到的知识\n\n"
        for knowledge in all_knowledge:
            content += f"- {knowledge}\n"
        content += "\n"
    
    # 已完成任务
    if all_tasks:
        content += "## 已完成任务\n\n"
        for task in all_tasks:
            content += f"- ✅ {task}\n"
        content += "\n"
    else:
        content += """## 已完成任务
> （今天完成的重要工作）

（未检测到明确任务）

"""
    
    # 会话详情
    content += "## 会话详情\n\n"
    for i, s in enumerate(summaries, 1):
        content += f"### 会话 {i} ({s['start_time']})\n"
        content += f"- 对话轮次：{s['turns']} 轮\n"
        content += f"- 工具调用：{s['tool_calls']} 次\n"
        if s.get("llm_extracted", {}).get("key_topics"):
            content += f"- 主要话题：{', '.join(s['llm_extracted']['key_topics'][:2])}\n"
        content += "\n"
    
    # 结构化信息（用于后续处理）
    structured_data = {
        "preferences": all_preferences,
        "decisions": all_decisions,
        "knowledge": all_knowledge,
        "tasks": all_tasks,
        "topics": all_topics
    }
    
    return content, structured_data


def auto_upgrade_to_l3(structured_data: Dict[str, List[str]], today: str):
    """自动升级高价值信息到 L3"""
    
    upgraded = {
        "preferences": 0,
        "decisions": 0,
        "knowledge": 0
    }
    
    # 用户偏好 → user-preference.md + fact_store (user_pref)
    for pref in structured_data.get("preferences", []):
        # 写入 L3 文件
        if save_to_long_term("user-preference", pref, today):
            # 写入 fact_store
            if add_fact_to_store(pref, "user_pref", "auto-upgraded,daily_summarizer_v3"):
                upgraded["preferences"] += 1
    
    # 重要决策 → project-notes.md + fact_store (project)
    for decision in structured_data.get("decisions", []):
        if save_to_long_term("project-notes", decision, today):
            if add_fact_to_store(decision, "project", "auto-upgraded,daily_summarizer_v3"):
                upgraded["decisions"] += 1
    
    # 学到的知识 → technical-knowledge.md + fact_store (general)
    for knowledge in structured_data.get("knowledge", []):
        if save_to_long_term("technical-knowledge", knowledge, today):
            if add_fact_to_store(knowledge, "general", "auto-upgraded,daily_summarizer_v3"):
                upgraded["knowledge"] += 1
    
    return upgraded


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
    
    parser = argparse.ArgumentParser(description="每日摘要生成器 v3.0 - LLM 增强版")
    parser.add_argument("--date", help="指定日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--cleanup", type=int, default=7, help="清理 N 天前的记忆")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不保存")
    parser.add_argument("--no-upgrade", action="store_true", help="不自动升级到 L3")
    parser.add_argument("--no-llm", action="store_true", help="禁用 LLM 提取（降级模式）")
    
    args = parser.parse_args()
    
    print(f"🧠 分层记忆系统 - 每日摘要生成器 v3.0")
    print(f"=" * 50)
    
    # 生成摘要
    summary, structured_data = generate_daily_summary(args.date)
    print(f"\n📝 生成的摘要：\n")
    print(summary)
    
    if structured_data:
        print(f"\n🔍 LLM 提取结果：")
        print(f"  - 用户偏好：{len(structured_data.get('preferences', []))} 条")
        print(f"  - 重要决策：{len(structured_data.get('decisions', []))} 条")
        print(f"  - 学到的知识：{len(structured_data.get('knowledge', []))} 条")
        print(f"  - 已完成任务：{len(structured_data.get('tasks', []))} 条")
    
    if not args.dry_run:
        today = args.date or datetime.now().strftime("%Y-%m-%d")
        saved_file = save_daily_summary(summary, today)
        print(f"\n✅ 已保存到：{saved_file}")
        
        # 自动升级到 L3
        if structured_data and not args.no_upgrade:
            upgraded = auto_upgrade_to_l3(structured_data, today)
            if any(upgraded.values()):
                print(f"\n📊 自动升级到 L3：")
                print(f"  - 偏好 → fact_store: {upgraded['preferences']} 条")
                print(f"  - 决策 → fact_store: {upgraded['decisions']} 条")
                print(f"  - 知识 → fact_store: {upgraded['knowledge']} 条")
        
        # 清理过期
        deleted = cleanup_expired(args.cleanup)
        if deleted > 0:
            print(f"\n🗑️  清理了 {deleted} 个过期的 L2 记忆（超过 {args.cleanup} 天）")
    
    print(f"\n✅ 完成！")


if __name__ == "__main__":
    main()
