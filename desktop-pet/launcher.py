#!/usr/bin/env python3
"""
桌面宠物 - 增强版启动器
自动处理 macOS 窮口置顶问题
"""
import sys
import subprocess
import time
from pathlib import Path

def check_window_visible():
    """检查窗口是否可见"""
    try:
        result = subprocess.run(
            ['osascript', '-e', 'tell application "System Events" to get visible of first process whose name contains "Python"'],
            capture_output=True,
            text=True,
            timeout=2
        )
        return 'true' in result.stdout.lower()
    except:
        return True

def force_stay_on_top():
    """macOS 强制窗口置顶"""
    if sys.platform != 'darwin':
        return
    
    script = '''
    tell application "System Events"
        try
            set frontmost of first process whose name contains "Python" to true
            delay 0.1
            set visible of first process whose name contains "Python" to true
        end try
    end tell
    '''
    
    try:
        subprocess.run(['osascript', '-e', script], capture_output=True, timeout=3)
    except:
        pass

def main():
    print("🐱 启动桌面宠物...")
    
    # 启动主程序
    import subprocess
    pet_process = subprocess.Popen(
        [sys.executable, Path(__file__).parent / 'pet_main.py'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print(f"✅ 桌面宠物已启动 (PID: {pet_process.pid})")
    
    # macOS 持续置顶守护
    if sys.platform == 'darwin':
        print("📌 macOS: 启动置顶守护...")
        print("   - 每 10 秒检查窗口状态")
        print("   - 按 Ctrl+C 停止")
        
        try:
            while True:
                time.sleep(10)
                if pet_process.poll() is None:
                    force_stay_on_top()
                else:
                    print("⚠️ 桌面宠物已退出")
                    break
        except KeyboardInterrupt:
            print("\n🛑 停止置顶守护")
            pet_process.terminate()
            pet_process.wait()
    
    print("👋 桌面宠物已退出")

if __name__ == "__main__":
    main()
