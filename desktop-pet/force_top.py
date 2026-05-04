#!/usr/bin/env python3
"""
桌面宠物 - 一键置顶工具
快速解决 macOS 窗口置顶问题
"""
import subprocess
import sys

def force_front():
    """强制 Python 窗口置顶"""
    script = '''
    tell application "System Events"
        try
            set frontmost of first process whose name contains "Python" to true
            set visible of first process whose name contains "Python" to true
        end try
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', script], check=True)
        print("✅ 已强制置顶！宠物应该在所有窗口最前面了")
        print("   如果还是看不到，请检查：")
        print("   1. 宠物是否在其他桌面空间")
        print("   2. 是否有全屏应用遮挡")
        return True
    except Exception as e:
        print(f"❌ 置顶失败: {e}")
        return False

if __name__ == "__main__":
    print("📌 强制置顶桌面宠物...")
    force_front()
