#!/usr/bin/env python3
"""
Gateway 进程守护脚本
每5分钟检查一次 Gateway 是否存活，意外停止时自动重启并发送微信通知
"""

import subprocess
import sys
from datetime import datetime

def check_gateway_status():
    """检查 Gateway 进程是否存活"""
    try:
        result = subprocess.run(
            ['launchctl', 'list', 'ai.hermes.gateway'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # 检查是否有 PID（表示进程存活）
        if 'PID' in result.stdout:
            # 提取 PID
            for line in result.stdout.split('\n'):
                if 'PID' in line:
                    pid = line.split('=')[1].strip().strip(';')
                    return True, int(pid)
        return False, None
    except Exception as e:
        return False, None

def restart_gateway():
    """重启 Gateway"""
    try:
        result = subprocess.run(
            ['/Users/me/.local/bin/hermes', 'gateway', 'start'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)

def send_wechat_alert(message):
    """发送微信告警"""
    try:
        # 使用 hermes send 命令发送微信消息
        result = subprocess.run(
            ['/Users/me/.local/bin/hermes', 'send', 'weixin', message],
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.returncode == 0
    except Exception as e:
        print(f"发送告警失败: {e}")
        return False

def main():
    print(f"\n{'='*60}")
    print(f"🕐 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    is_alive, pid = check_gateway_status()
    
    if is_alive:
        print(f"✅ Gateway 正常运行 (PID: {pid})")
        sys.exit(0)
    
    print("❌ Gateway 已停止！尝试重启...")
    
    # 重启 Gateway
    restart_ok, restart_msg = restart_gateway()
    
    if restart_ok:
        print(f"✅ Gateway 重启成功")
        
        # 发送微信告警
        alert_msg = f"""⚠️ Gateway 进程守护告警

【事件】Gateway 意外停止，已自动重启
【时间】{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
【状态】重启成功
【原因】可能是 monitor-token-status.py 误判或其他原因

建议检查日志：
~/.hermes/logs/gateway.log"""
        
        send_wechat_alert(alert_msg)
        print("📱 已发送微信告警")
        sys.exit(0)
    else:
        print(f"❌ Gateway 重启失败: {restart_msg}")
        
        # 发送紧急告警
        alert_msg = f"""🚨 Gateway 进程守护紧急告警

【事件】Gateway 意外停止，重启失败！
【时间】{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
【错误】{restart_msg}

请立即手动处理：
hermes gateway start"""
        
        send_wechat_alert(alert_msg)
        print("📱 已发送紧急微信告警")
        sys.exit(1)

if __name__ == '__main__':
    main()
