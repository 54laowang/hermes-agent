#!/usr/bin/env python3
"""
重要事实自动提取器
在每轮对话后检测用户是否说了需要记住的内容，自动提取到 L3 长期记忆
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"
L3_MEMORY_DIR = HERMES_DIR / "memory" / "long-term"

# 触发关键词（用户说这些词时，说明这句话可能需要记住）
TRIGGER_KEYWORDS = [
    "记住", "记得", "别忘了", "下次", "以后",
    "偏好", "喜欢", "不喜欢", "不要",
    "我习惯", "我一般", "我总是",
    "设置为", "默认为",
    "路径是", "地址是", "在哪个目录", "位置是",
    "核心是", "本质是", "关键是",
    "这个项目", "这个仓库", "这个系统",
]

# 否定关键词（命中时跳过）
NEGATIVE_KEYWORDS = [
    "?", "吗", "呢", "吧",  # 疑问句
    "你记住", "你记得",  # 反问
]


def contains_trigger(text: str) -> bool:
    """检测文本是否包含记忆触发词"""
    text_lower = text.lower()
    
    # 检查否定关键词（如疑问句）
    for neg in NEGATIVE_KEYWORDS:
        if neg in text_lower:
            return False
    
    # 检查触发关键词
    for kw in TRIGGER_KEYWORDS:
        if kw in text_lower:
            return True
    
    return False


def extract_fact(user_message: str, assistant_response: str = "") -> dict:
    """从用户消息中提取事实"""
    
    if not contains_trigger(user_message):
        return None
    
    # 简单分类
    category = "general"
    
    if any(kw in user_message for kw in ["喜欢", "偏好", "不喜欢", "不要"]):
        category = "user-preference"
    elif any(kw in user_message for kw in ["项目", "仓库", "代码"]):
        category = "project-notes"
    elif any(kw in user_message for kw in ["命令", "工具", "路径"]):
        category = "environment-facts"
    elif any(kw in user_message for kw in ["技术", "架构", "模型"]):
        category = "technical-knowledge"
    
    return {
        "fact": user_message.strip(),
        "category": category,
        "timestamp": datetime.now().isoformat(),
        "context": assistant_response[:100] if assistant_response else "",
        "confidence": 0.8 if contains_trigger(user_message) else 0.5,
    }


def save_fact(fact: dict) -> Path:
    """保存事实到 L3 长期记忆"""
    category = fact["category"]
    fact_file = L3_MEMORY_DIR / f"{category}.md"
    
    L3_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    # 初始化文件
    if not fact_file.exists():
        header = {
            "user-preference": "# 用户偏好 User Preferences\n\n用户明确表达的喜好、习惯、禁忌。\n\n---\n\n",
            "environment-facts": "# 环境事实 Environment Facts\n\n系统、工具、路径等客观事实。\n\n---\n\n",
            "project-notes": "# 项目记录 Project Notes\n\n项目相关的重要信息、决策记录。\n\n---\n\n",
            "technical-knowledge": "# 技术知识 Technical Knowledge\n\n学到的重要技术知识、架构、方法论。\n\n---\n\n",
            "general": "# 通用记忆 General\n\n其他需要长期记住的信息。\n\n---\n\n",
        }
        fact_file.write_text(header.get(category, f"# {category}\n\n"), encoding="utf-8")
    
    # 追加事实
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{timestamp}] {fact['fact']}\n"
    
    content = fact_file.read_text(encoding="utf-8")
    content += entry
    fact_file.write_text(content, encoding="utf-8")
    
    return fact_file


def main():
    """Hermes hook 入口"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 测试模式
        test_messages = [
            "记住，我喜欢用表格来呈现对比信息",
            "以后生成代码时，记得先写注释再写实现",
            "这个项目的路径是 ~/work/ai-project",
            "OpenClaw 的核心是分层记忆系统",
        ]
        for msg in test_messages:
            fact = extract_fact(msg)
            if fact:
                print(f"✅ 检测到事实 [{fact['category']}]: {msg}")
            else:
                print(f"❌ 未检测到: {msg}")
        return
    
    # Hermes hook 模式
    payload = json.loads(sys.stdin.read())
    
    user_message = payload.get("extra", {}).get("user_message", "")
    assistant_response = payload.get("extra", {}).get("assistant_response", "")
    
    if not user_message:
        print("{}")
        return
    
    fact = extract_fact(user_message, assistant_response)
    
    if fact and fact["confidence"] >= 0.7:
        saved_file = save_fact(fact)
        result = {
            "status": "fact_extracted",
            "category": fact["category"],
            "fact": fact["fact"],
            "saved_to": str(saved_file),
        }
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("{}")


if __name__ == "__main__":
    main()
