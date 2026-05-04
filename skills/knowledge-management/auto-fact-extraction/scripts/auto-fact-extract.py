#!/usr/bin/env python3
"""
Hermes Shell Hook - post_llm_call 事件触发
自动提取对话中的关键事实并持久化

安装:
1. 复制到 ~/.hermes/agent-hooks/auto-fact-extract.py
2. chmod +x ~/.hermes/agent-hooks/auto-fact-extract.py
3. 在 config.yaml 中配置钩子
"""
import json
import os
import sys
from datetime import datetime

LOG_FILE = os.path.expanduser("~/.hermes/logs/auto-facts.log")

def main():
    # 确保日志目录存在
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # 读取 Hermes 传入的环境变量
    event_data = {
        "timestamp": datetime.now().isoformat(),
        "session_id": os.environ.get("HERMES_SESSION_ID", "unknown"),
        "platform": os.environ.get("HERMES_PLATFORM", "unknown"),
        "model": os.environ.get("HERMES_MODEL", "unknown"),
        "prompt_length": os.environ.get("HERMES_PROMPT_LENGTH", "0"),
        "response_length": os.environ.get("HERMES_RESPONSE_LENGTH", "0"),
        "event": os.environ.get("HERMES_HOOK_EVENT", "unknown"),
    }
    
    # 追加日志
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event_data, ensure_ascii=False) + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
