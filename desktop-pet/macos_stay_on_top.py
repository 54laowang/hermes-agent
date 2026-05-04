"""
macOS 窗口置顶增强版
使用 NSApplication API 强制置顶
"""
import sys
from pathlib import Path

def set_stay_on_top_macos():
    """macOS 强制置顶窗口"""
    if sys.platform != 'darwin':
        return
    
    try:
        # 导入 macOS 框架
        from Cocoa import NSApp, NSFloatingWindowLevel, NSWindowCollectionBehaviorCanJoinAllSpaces
        
        # 获取当前窗口
        window = NSApp.keyWindow()
        if window:
            # 设置窗口层级为浮动
            window.setLevel_(NSFloatingWindowLevel)
            # 允许在所有桌面空间显示
            window.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
            print("✅ macOS 窗口已强制置顶")
        else:
            print("⚠️ 未找到窗口")
            
    except ImportError:
        print("⚠️ 未安装 Cocoa，使用备用方案")
        # 备用方案：AppleScript
        import subprocess
        script = '''
        tell application "System Events"
            try
                set frontmost of first process whose name contains "Python" to true
            end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], capture_output=True)

if __name__ == "__main__":
    set_stay_on_top_macos()
