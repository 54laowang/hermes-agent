#!/usr/bin/env python3
"""
桌面宠物控制脚本 - 快捷命令行工具

Usage:
    python3 pet_control.py msg "你好世界"
    python3 pet_control.py state walk
    python3 pet_control.py health
"""

import sys
import requests
import json

PORT = 51983
BASE_URL = f"http://127.0.0.1:{PORT}"


def send_message(text: str):
    """发送消息"""
    url = f"{BASE_URL}/msg"
    resp = requests.get(url, params={"text": text})
    print(f"📤 消息已发送: {text}")
    print(f"✅ 响应: {resp.json()}")


def change_state(state: str):
    """切换状态"""
    url = f"{BASE_URL}/state"
    resp = requests.get(url, params={"name": state})
    print(f"🎭 状态已切换: {state}")
    print(f"✅ 响应: {resp.json()}")


def health_check():
    """健康检查"""
    url = f"{BASE_URL}/health"
    resp = requests.get(url)
    data = resp.json()
    print("🏥 健康检查:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    try:
        if command == "msg" and len(sys.argv) >= 3:
            send_message(sys.argv[2])
        elif command == "state" and len(sys.argv) >= 3:
            change_state(sys.argv[2])
        elif command == "health":
            health_check()
        else:
            print(__doc__)
    except requests.exceptions.ConnectionError:
        print("❌ 宠物未运行或端口被占用")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
