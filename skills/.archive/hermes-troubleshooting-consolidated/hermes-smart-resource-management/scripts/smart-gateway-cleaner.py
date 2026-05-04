#!/usr/bin/env python3
"""
智能网关清理器 - 只在闲置时清理，避免打断用户对话

功能：
1. 检测活跃会话数量和最后活动时间
2. 超过 60 分钟无会话时自动关闭网关
3. 清理孤儿 MCP 进程
4. 记录清理日志便于追溯

每 15 分钟运行一次，只有真正闲置才行动
"""

import os
import json
import time
import glob
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 配置
HERMES_HOME = Path.home() / ".hermes"
LOG_DIR = HERMES_HOME / "logs"
SESSION_TIMEOUT_MINUTES = 60  # 超过 60 分钟无会话才清理
LOG_FILE = LOG_DIR / "smart-cleaner.log"

def log(msg):
    """写日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {msg}\n"
    print(log_line.strip())
    with open(LOG_FILE, 'a') as f:
        f.write(log_line)

def get_running_processes():
    """获取所有 hermes 进程"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'hermes'],
            capture_output=True, text=True
        )
        pids = [int(p) for p in result.stdout.strip().split('\n') if p]
        return pids
    except:
        return []

def count_active_sessions():
    """
    检测活跃会话数量
    返回: (活跃会话数, 最近活动时间分钟数)
    """
    try:
        # 方法 1: 检查 gateway.log 中最近的消息活动
        gateway_log = LOG_DIR / "gateway.log"
        if gateway_log.exists():
            result = subprocess.run(
                ['tail', '-100', str(gateway_log)],
                capture_output=True, text=True
            )
            
            # 统计最近 1 小时内的会话活动
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_activity = []
            
            for line in result.stdout.split('\n'):
                if not line.strip():
                    continue
                try:
                    # 解析日志时间戳格式: 2026-04-27 23:10:20,100
                    time_str = line[:19]
                    log_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    
                    # 检查是否有消息处理、用户输入等活动
                    # 包括平台连接、消息收发等关键活动
                    activity_keywords = [
                        'received message', 'sending message', 
                        'tool call', 'session', 'user input',
                        '平台消息', '处理消息',
                        # 平台连接活动（Telegram/微信/QQ等）
                        'Connected to Telegram', 'Telegram polling',
                        'Connected to wss://', 'weixin', 'wecom',
                        'QQBot', 'discord', 'slack',
                        # 消息处理
                        'message received', 'message sent',
                        # 网络活动
                        'network error', 'reconnect'
                    ]
                    
                    if any(k in line for k in activity_keywords):
                        if log_time > one_hour_ago:
                            recent_activity.append(log_time)
                except:
                    pass
            
            if recent_activity:
                last_activity = max(recent_activity)
                minutes_since = (datetime.now() - last_activity).total_seconds() // 60
                return len(recent_activity), int(minutes_since)
        
        # 方法 2: 检查 sessions 目录的修改时间
        sessions_dir = HERMES_HOME / "sessions"
        if sessions_dir.exists():
            session_files = list(sessions_dir.glob("*.json"))
            if session_files:
                latest_mtime = max(f.stat().st_mtime for f in session_files)
                minutes_since = (time.time() - latest_mtime) // 60
                return len(session_files), int(minutes_since)
        
        return 0, 999  # 无法检测到活动，默认闲置
        
    except Exception as e:
        log(f"⚠️  检测会话时出错: {e}")
        return 0, 999

def kill_orphan_processes():
    """清理孤儿进程"""
    try:
        # 查找所有 hermes mcp serve 进程
        subprocess.run(
            ['pkill', '-f', 'hermes mcp serve'],
            capture_output=True
        )
        log("   ✅ 已清理 MCP 孤儿进程")
        time.sleep(2)
    except:
        pass

def stop_gateway():
    """停止网关"""
    try:
        log("🔄 执行网关停止...")
        
        # 先停止网关服务
        subprocess.run(
            ['/Users/me/.hermes/hermes-agent/venv/bin/python', 
             '/Users/me/.local/bin/hermes', 'gateway', 'stop'],
            capture_output=True, timeout=30
        )
        time.sleep(3)
        
        # 清理残留进程
        kill_orphan_processes()
        
        pids = get_running_processes()
        if pids:
            log(f"   ⚠️  仍有 {len(pids)} 个进程残留，强制清理")
            for pid in pids:
                try:
                    os.kill(pid, 15)  # SIGTERM
                except:
                    pass
            time.sleep(2)
            
        log("   ✅ 网关已停止")
        return True
        
    except Exception as e:
        log(f"   ❌ 停止网关失败: {e}")
        return False

def main():
    """主逻辑"""
    log(f"{'='*50}")
    log("🔍 开始智能网关状态检测")
    
    # 1. 获取当前进程情况
    pids = get_running_processes()
    log(f"📊 当前 hermes 进程数: {len(pids)}")
    
    if len(pids) == 0:
        log("   ✅ 网关未运行，无需处理")
        return
    
    # 2. 检测会话活跃度
    active_count, minutes_since = count_active_sessions()
    log(f"💬 最近 1 小时会话活动: {active_count} 次")
    log(f"⏱️  距最后活动: {minutes_since} 分钟")
    
    # 3. 决策
    if minutes_since < SESSION_TIMEOUT_MINUTES:
        log(f"✅ 系统活跃（{minutes_since} 分钟内有活动），跳过清理")
        log(f"   ⏭️  距自动清理还有: {SESSION_TIMEOUT_MINUTES - minutes_since} 分钟")
        return
    
    # 4. 超时，执行清理
    log(f"⚠️  已超过 {SESSION_TIMEOUT_MINUTES} 分钟无会话活动，执行智能清理")
    
    # 5. 停止网关
    stop_gateway()
    
    # 6. 最终确认
    final_pids = get_running_processes()
    if len(final_pids) == 0:
        log("✅ 清理完成，所有进程已安全关闭")
    else:
        log(f"⚠️  仍有 {len(final_pids)} 个进程未关闭")
    
    log(f"{'='*50}\n")

if __name__ == '__main__':
    main()
