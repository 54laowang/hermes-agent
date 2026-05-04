#!/usr/bin/env python3
"""
Hermes Agent 集成模块
功能：监听任务事件、日程提醒、天气更新
"""

import json
import os
import time
import threading
import logging
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime, timedelta
import sqlite3

logger = logging.getLogger('HermesPet')


class HermesIntegration:
    """Hermes Agent 集成管理器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser(
            "~/.hermes/desktop-pet/hermes_config.json"
        )
        self.config = self._load_config()
        self.running = False
        self.callbacks = {
            'show_message': None,
            'change_state': None,
            'play_animation': None,
        }
        
        # Hermes 数据库路径
        self.hermes_db = os.path.expanduser("~/.hermes/hermes.db")
        self.last_task_check = time.time()
        
    def _load_config(self) -> dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"enabled": False}
    
    def register_callback(self, event: str, callback: Callable):
        """注册回调函数"""
        if event in self.callbacks:
            self.callbacks[event] = callback
        else:
            logger.warning(f"Unknown event: {event}")
    
    def _show_message(self, text: str):
        """显示消息气泡"""
        if self.callbacks['show_message']:
            self.callbacks['show_message'](text)
    
    def _change_state(self, state: str):
        """切换动画状态"""
        if self.callbacks['change_state']:
            self.callbacks['change_state'](state)
    
    def _play_animation(self, animation: str):
        """播放动画"""
        if self.callbacks['play_animation']:
            self.callbacks['play_animation'](animation)
    
    def start(self):
        """启动监听"""
        if not self.config.get('enabled', False):
            logger.info("Hermes integration disabled")
            return
        
        self.running = True
        logger.info("Hermes integration started")
        
        # 启动任务监听线程
        if self.config.get('task_reminder', {}).get('enabled', False):
            threading.Thread(target=self._watch_tasks, daemon=True).start()
            logger.info("Task watcher started")
        
        # 启动日程监听线程
        if self.config.get('schedule_reminder', {}).get('enabled', False):
            threading.Thread(target=self._watch_schedule, daemon=True).start()
            logger.info("Schedule watcher started")
    
    def stop(self):
        """停止监听"""
        self.running = False
        logger.info("Hermes integration stopped")
    
    def _watch_tasks(self):
        """监听任务完成事件"""
        if not os.path.exists(self.hermes_db):
            logger.warning(f"Hermes database not found: {self.hermes_db}")
            return
        
        while self.running:
            try:
                # 检查最近完成的任务
                conn = sqlite3.connect(self.hermes_db)
                cursor = conn.cursor()
                
                # 查询最近 1 分钟内完成的任务
                query = """
                SELECT task_id, status, created_at 
                FROM tasks 
                WHERE status = 'completed' 
                AND created_at > ?
                ORDER BY created_at DESC
                LIMIT 5
                """
                
                cutoff = datetime.now() - timedelta(minutes=1)
                cursor.execute(query, (cutoff.isoformat(),))
                tasks = cursor.fetchall()
                conn.close()
                
                if tasks:
                    for task_id, status, created_at in tasks:
                        msg = f"✅ 任务完成：{task_id[:20]}..."
                        self._show_message(msg)
                        self._change_state(
                            self.config['task_reminder'].get('success_animation', 'idle')
                        )
                        time.sleep(3)  # 避免消息堆叠
                
                time.sleep(30)  # 30 秒检查一次
                
            except Exception as e:
                logger.error(f"Error watching tasks: {e}")
                time.sleep(60)
    
    def _watch_schedule(self):
        """监听日程提醒"""
        while self.running:
            try:
                # TODO: 接入日历 API
                # 这里可以接入 Apple Calendar / Google Calendar
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error watching schedule: {e}")
                time.sleep(60)
    
    def notify_weather(self):
        """天气通知（手动触发）"""
        if not self.config.get('weather', {}).get('enabled', False):
            return
        
        try:
            # TODO: 接入天气 API
            weather_text = "北京 晴 18°C"
            self._show_message(f"🌤️ {weather_text}")
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
    
    def send_custom_message(self, text: str):
        """发送自定义消息"""
        self._show_message(text)


# 示例用法
if __name__ == "__main__":
    hermes = HermesIntegration()
    
    def on_message(text):
        print(f"[Message] {text}")
    
    def on_state(state):
        print(f"[State] {state}")
    
    hermes.register_callback('show_message', on_message)
    hermes.register_callback('change_state', on_state)
    
    # 测试发送消息
    hermes.send_custom_message("测试消息")
