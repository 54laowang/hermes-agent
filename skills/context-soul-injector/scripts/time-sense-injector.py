#!/usr/bin/env python3
"""
灵魂注入器 - 时间感知模块
在每轮对话前注入时间上下文，让 Agent 真正"活在时间里"
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path


def get_time_context():
    """生成时间感知上下文"""
    now = datetime.now()
    
    # 判断时间段
    hour = now.hour
    if 5 <= hour < 9:
        time_of_day = "清晨"
    elif 9 <= hour < 12:
        time_of_day = "上午"
    elif 12 <= hour < 14:
        time_of_day = "中午"
    elif 14 <= hour < 18:
        time_of_day = "下午"
    elif 18 <= hour < 22:
        time_of_day = "晚上"
    else:
        time_of_day = "深夜"
    
    # 判断是否周末
    is_weekend = now.weekday() >= 5
    
    # 判断A股市场状态
    if is_weekend:
        market_status = "休市（周末）"
    elif hour < 9 or (hour == 9 and now.minute < 30):
        market_status = "盘前"
    elif hour == 11 and now.minute >= 30:
        market_status = "午盘"
    elif hour >= 15:
        market_status = "收盘后"
    else:
        market_status = "交易中"
    
    # 判断美股市场状态（美东时间 = 北京时间 - 12小时）
    us_hour = (hour - 12) % 24
    us_date = now - timedelta(days=1) if hour < 4 else now
    if us_hour < 9 or (us_hour == 9 and now.minute < 30):
        us_market_status = "盘前"
    elif us_hour >= 16:
        us_market_status = "收盘后"
    else:
        us_market_status = "交易中"
    
    context = f"""
【当前时间感知】
现在是：{now.strftime('%Y-%m-%d %H:%M:%S')}
星期：{"星期一" if now.weekday() == 0 else "星期二" if now.weekday() == 1 else "星期三" if now.weekday() == 2 else "星期四" if now.weekday() == 3 else "星期五" if now.weekday() == 4 else "星期六" if now.weekday() == 5 else "星期日"}
时间段：{time_of_day}
是否周末：{"是" if is_weekend else "否"}

【市场状态】
A股：{market_status}
美股：{us_market_status}（美东日期：{us_date.strftime('%Y-%m-%d')}）

【时间锚定原则 - 最高优先级】
⚠️ 任何数据分析前，必须先建立时间锚点：
1. 搜索关键词必须包含精确日期 + 时间节点
2. 验证数据时间戳是否匹配当前市场状态
3. 不匹配 = 拒绝使用，重新搜索
4. 禁止用过时数据凑数

行为准则：
1. 如果当前是凌晨（0:00-5:00）或深夜（22:00 以后），主动提醒用户注意休息
2. 如果是周末，理解用户可能不想聊严肃的工作话题（除非用户明确要求）
3. 感知时间流逝，长时间间隔后的对话可以自然地"重新接上话题"
"""
    
    return context


def get_search_context(days: int = 7, max_entries: int = 10):
    """从 search.md 读取近期搜索上下文"""
    search_file = Path.home() / ".hermes" / "search.md"
    
    if not search_file.exists():
        return ""
    
    try:
        content = search_file.read_text(encoding="utf-8")
        lines = content.split("\n")
        
        # 简单提取最近的搜索条目
        recent_searches = []
        in_entry = False
        current_entry = []
        
        for line in lines[-200:]:  # 只看最近的
            if line.startswith("### ") and len(recent_searches) < max_entries:
                if current_entry:
                    recent_searches.append("\n".join(current_entry))
                current_entry = [line]
                in_entry = True
            elif in_entry and line.strip():
                current_entry.append(line)
        
        if current_entry and len(recent_searches) < max_entries:
            recent_searches.append("\n".join(current_entry))
        
        if recent_searches:
            return f"""
【近期搜索记忆】
{chr(10).join(recent_searches[-5:])}
"""
        
    except Exception as e:
        pass
    
    return ""


def extract_topic_from_session(session_file: str) -> str:
    """从 JSONL 会话文件中提取关键话题
    
    使用启发式规则：
    1. 提取第一个用户消息的前50字
    2. 或提取包含关键词的消息
    """
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            # 只读取前20行（避免加载整个大文件）
            for i, line in enumerate(f):
                if i >= 20:
                    break
                
                try:
                    msg = json.loads(line.strip())
                    
                    # 找第一个用户消息
                    if msg.get('role') == 'user':
                        content = msg.get('content', '')
                        if isinstance(content, str) and len(content) > 5:
                            # 提取话题（前50字）
                            topic = content[:50]
                            if len(content) > 50:
                                topic += "..."
                            return topic
                except:
                    continue
        
        return ""
    except:
        return ""


def get_recent_session_context(hours: int = 24, max_sessions: int = 5):
    """从 Hermes 会话文件提取最近会话的关键话题
    
    解决跨平台/跨会话上下文断裂问题
    
    v2.0 优化：
    - 提取实际话题内容（而非仅 session_id）
    - 支持多平台识别（企业微信/飞书/微信/Telegram/元宝/CLI）
    - 智能摘要：提取第一个用户消息作为话题代表
    """
    import glob
    import os
    
    try:
        sessions_dir = Path.home() / ".hermes" / "sessions"
        if not sessions_dir.exists():
            return ""
        
        # 获取所有 .jsonl 会话文件，按修改时间排序
        session_files = glob.glob(str(sessions_dir / "*.jsonl"))
        if not session_files:
            return ""
        
        # 按修改时间排序（最新的在前）
        session_files.sort(key=os.path.getmtime, reverse=True)
        
        topics = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for filepath in session_files[:max_sessions * 3]:
            if len(topics) >= max_sessions:
                break
            
            filename = os.path.basename(filepath)
            
            # 解析文件名格式: YYYYMMDD_HHMMSS_<id>.jsonl
            if not filename.endswith('.jsonl'):
                continue
            
            parts = filename.replace('.jsonl', '').split('_')
            if len(parts) < 3:
                continue
            
            date_str, time_str, session_id = parts[0], parts[1], parts[2]
            
            # 解析时间
            try:
                file_time = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
                
                # 过滤太久远的会话
                if file_time < cutoff_time:
                    continue
                
                time_str_fmt = file_time.strftime("%m-%d %H:%M")
            except:
                continue
            
            # 从文件内容推断平台（读取第一行）
            platform = "未知"
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if '"source"' in first_line:
                        if '"wecom"' in first_line:
                            platform = "企业微信"
                        elif '"feishu"' in first_line:
                            platform = "飞书"
                        elif '"weixin"' in first_line:
                            platform = "微信"
                        elif '"telegram"' in first_line:
                            platform = "Telegram"
                        elif '"yuanbao"' in first_line:
                            platform = "元宝"
                        elif '"cli"' in first_line:
                            platform = "CLI"
            except:
                pass
            
            # 提取实际话题内容
            topic_content = extract_topic_from_session(filepath)
            
            if topic_content:
                topics.append(f"{time_str_fmt} [{platform}]: {topic_content}")
        
        if topics:
            return f"""
【近期对话话题】（跨会话上下文）
{chr(10).join(topics)}

⚠️ 如果用户提起之前聊过的话题，用 session_search 搜索历史会话
💡 关键词示例：跨会话记忆、昨天聊过、之前讨论、上次说
"""
        
    except Exception as e:
        pass
    
    return ""


def main():
    # 读取 payload（如果是 hook 模式）
    if not sys.stdin.isatty():
        try:
            payload = json.loads(sys.stdin.read())
        except:
            payload = {}
    else:
        payload = {}
    
    # 生成上下文
    time_ctx = get_time_context()
    search_ctx = get_search_context()
    session_ctx = get_recent_session_context()  # 新增：跨会话话题追踪
    
    full_context = time_ctx + search_ctx + session_ctx
    
    # 返回为 Hermes hook 格式
    result = {
        "context_injection": full_context.strip(),
        "injection_position": "before_system_prompt",
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "time_injected": True,
            "search_injected": len(search_ctx) > 0,
            "session_injected": len(session_ctx) > 0  # 新增标记
        }
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
