# 跨会话上下文追踪实现细节

> 2026-05-03: 解决用户反馈"跨会话不调取记忆"问题

## 问题背景

用户在企业微信聊过"五粮液年报问题"，切换到飞书后 Agent 没有自动调取上下文，需要手动搜索。

## 根因分析

### 错误假设

```python
# ❌ 错误：假设会话存储在 SQLite 数据库
db_path = Path.home() / ".hermes" / "sessions" / "sessions.db"
result = subprocess.run(["sqlite3", str(db_path), "SELECT ..."])
```

### 实际机制

```
~/.hermes/sessions/
├── 20260503_165919_da55f264.jsonl  ← 企业微信会话 (190KB)
├── 20260503_104113_ffe74ca7.jsonl  ← 飞书会话 (147KB)
├── sessions.db                      ← 空文件 (0 字节)
└── sessions.json                    ← 索引文件
```

**会话文件格式**: JSONL（每行一个 JSON 对象）

**文件命名**: `YYYYMMDD_HHMMSS_<session_id>.jsonl`

## 解决方案

### 实现代码

```python
def get_recent_session_context(hours: int = 24, max_sessions: int = 3):
    """从 Hermes 会话文件提取最近会话的关键话题"""
    import glob
    import os
    
    sessions_dir = Path.home() / ".hermes" / "sessions"
    session_files = glob.glob(str(sessions_dir / "*.jsonl"))
    
    # 按修改时间排序（最新的在前）
    session_files.sort(key=os.path.getmtime, reverse=True)
    
    topics = []
    for filepath in session_files[:max_sessions]:
        filename = os.path.basename(filepath)
        parts = filename.replace('.jsonl', '').split('_')
        
        if len(parts) >= 3:
            date_str, time_str, session_id = parts[0], parts[1], parts[2]
            
            # 解析时间
            file_time = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
            time_str_fmt = file_time.strftime("%m-%d %H:%M")
            
            # 从文件内容推断平台
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                platform = "未知"
                if '"source"' in first_line:
                    if '"wecom"' in first_line:
                        platform = "[企业微信]"
                    elif '"feishu"' in first_line:
                        platform = "[飞书]"
                    # ... 其他平台
            
            topics.append(f"{time_str_fmt} {platform}: {session_id[:12]}...")
    
    return topics
```

### 注入效果

```
【近期对话话题】（跨会话上下文）
05-03 16:59 [企业微信]: da55f264...  ← 刚才聊的五粮液年报
05-03 10:41 [飞书]: ffe74ca7...
05-03 10:17 未知: 327ccd26...

⚠️ 如果用户提起之前聊过的话题，用 session_search 搜索历史会话
```

## 未来优化方向

1. **话题摘要提取**: 当前只显示 session_id，可改为从会话摘要中提取关键词
2. **智能去重**: 排除当前会话本身
3. **时间范围过滤**: 只显示 24 小时内的会话

## 相关文件

- 主脚本: `scripts/time-sense-injector.py`
- 会话存储: `~/.hermes/sessions/*.jsonl`
