#!/usr/bin/env python3
"""
Desktop Pet System - 桌面宠物主程序
跨平台透明窗口宠物，支持动画、消息气泡、HTTP控制

Usage:
    python3 pet_main.py
"""
import sys
import os
from pathlib import Path

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from pet_window import PetWindow
from pet_server import PetServer
from pet_hermes import HermesIntegration
import threading
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('DesktopPet')

# 配置
PORT = 51983
DEFAULT_SKIN = "default"


def check_singleton():
    """检测是否已有实例运行"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', PORT))
        s.close()
        print(f'⚠️  宠物已在运行 (端口 {PORT})')
        return False
    except ConnectionRefusedError:
        return True
    finally:
        s.close()


def main():
    """主函数"""
    # 检测单例
    if not check_singleton():
        sys.exit(0)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Desktop Pet")
    
    # 创建宠物窗口
    pet = PetWindow(skin_name=DEFAULT_SKIN)
    pet.show()
    
    # 启动 HTTP 服务器（后台线程）
    server = PetServer(pet, port=PORT)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    # 启动 Hermes 集成
    hermes = HermesIntegration()
    hermes.register_callback('show_message', pet.show_message)
    hermes.register_callback('change_state', pet.change_state)
    hermes.start()
    
    logger.info(f"🐱 桌面宠物已启动 (端口 {PORT})")
    logger.info("💡 单击拖动 | 双击关闭 | 右键菜单")
    logger.info("🔗 Hermes 集成已启用")
    
    # 运行主循环
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
