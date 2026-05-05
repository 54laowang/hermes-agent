#!/usr/bin/env python3
"""
macOS 窗口置顶增强工具
使用 AppleScript 强制窗口置顶
"""
import subprocess
import sys
import time

def set_window_stay_on_top(window_title="pet_main.py"):
    """使用 AppleScript 设置窗口置顶"""
    script = f'''
    tell application "System Events"
        set frontmost of process "Python" to true
        tell process "Python"
            set visible to true
        end tell
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
        print("✅ 窗口已置顶")
        return True
    except Exception as e:
        print(f"❌ 置顶失败: {e}")
        return False

def keep_window_on_top(interval=5):
    """持续保持窗口置顶"""
    print(f"🔄 开始持续置顶（每{interval}秒检查一次）")
    print("按 Ctrl+C 停止")
    
    while True:
        set_window_stay_on_top()
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--keep":
        # 持续置顶模式
        keep_window_on_top()
    else:
        # 单次置顶
        set_window_stay_on_top()
