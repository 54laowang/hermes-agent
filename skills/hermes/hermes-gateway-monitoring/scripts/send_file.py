#!/usr/bin/env python3
"""
文件发送工具 - 支持企业微信、Telegram、元宝三种平台

使用方法（独立运行，仅企业微信）:
    python3 send_file.py wecom WangTaoTao /path/to/file.pdf "文件说明"

在 Gateway 停止时（Telegram/元宝）:
    hermes gateway stop
    python3 send_file.py telegram 7954228359 /path/to/file.pdf "文件说明"
    hermes gateway start
"""

import os
import asyncio
from pathlib import Path
from typing import Optional

# 加载环境变量
def load_env():
    env_path = os.path.expanduser('~/.hermes/.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()


async def send_to_wecom(chat_id: str, file_path: str, caption: Optional[str] = None) -> dict:
    """发送文件到企业微信"""
    from gateway.config import PlatformConfig
    from gateway.platforms.wecom import WeComAdapter
    
    config = PlatformConfig()
    config.enabled = True
    
    adapter = WeComAdapter(config)
    connected = await adapter.connect()
    
    if not connected:
        return {"success": False, "error": "企业微信连接失败"}
    
    try:
        result = await adapter.send_document(
            chat_id=chat_id,
            file_path=file_path,
            caption=caption
        )
        return {
            "success": result.success,
            "message_id": result.message_id,
            "error": result.error
        }
    finally:
        await adapter.disconnect()


async def send_to_telegram(chat_id: str, file_path: str, caption: Optional[str] = None) -> dict:
    """发送文件到 Telegram（需要 Gateway 未运行）"""
    from gateway.config import PlatformConfig
    from gateway.platforms.telegram import TelegramAdapter
    
    config = PlatformConfig()
    config.enabled = True
    config.token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    adapter = TelegramAdapter(config)
    connected = await adapter.connect()
    
    if not connected:
        return {"success": False, "error": "Telegram 连接失败（Token 可能被 Gateway 锁定）"}
    
    try:
        result = await adapter.send_document(
            chat_id=chat_id,
            file_path=file_path,
            caption=caption
        )
        return {
            "success": result.success,
            "message_id": result.message_id,
            "error": result.error
        }
    finally:
        await adapter.disconnect()


async def send_to_yuanbao(chat_id: str, file_path: str, caption: Optional[str] = None) -> dict:
    """发送文件到元宝（需要 Gateway 未运行）"""
    from gateway.config import PlatformConfig
    from gateway.platforms.yuanbao import YuanbaoAdapter
    
    config = PlatformConfig()
    config.enabled = True
    config.extra = {
        "app_id": os.environ.get("YUANBAO_APP_ID"),
        "app_secret": os.environ.get("YUANBAO_APP_SECRET"),
        "ws_url": os.environ.get("YUANBAO_WS_URL"),
        "api_domain": os.environ.get("YUANBAO_API_DOMAIN"),
    }
    
    adapter = YuanbaoAdapter(config)
    connected = await adapter.connect()
    
    if not connected:
        return {"success": False, "error": "元宝连接失败（连接可能被 Gateway 锁定）"}
    
    try:
        result = await adapter.send_document(
            chat_id=chat_id,
            file_path=file_path,
            caption=caption
        )
        return {
            "success": result.success,
            "message_id": result.message_id,
            "error": result.error
        }
    finally:
        await adapter.disconnect()


async def send_to_platform(
    platform: str,
    chat_id: str,
    file_path: str,
    caption: Optional[str] = None
) -> dict:
    """统一发送接口"""
    if not os.path.exists(file_path):
        return {"success": False, "error": f"文件不存在: {file_path}"}
    
    platform = platform.lower()
    
    if platform == "wecom":
        return await send_to_wecom(chat_id, file_path, caption)
    elif platform == "telegram":
        return await send_to_telegram(chat_id, file_path, caption)
    elif platform == "yuanbao":
        return await send_to_yuanbao(chat_id, file_path, caption)
    else:
        return {"success": False, "error": f"不支持的平台: {platform}"}


def main():
    import sys
    
    if len(sys.argv) < 4:
        print("用法: python3 send_file.py <platform> <chat_id> <file_path> [caption]")
        print("平台: wecom | telegram | yuanbao")
        print("\n注意: Telegram 和元宝需要先停止 Gateway（Token 锁定问题）")
        print("  hermes gateway stop")
        print("  python3 send_file.py telegram 7954228359 /path/to/file.pdf")
        print("  hermes gateway start")
        sys.exit(1)
    
    platform = sys.argv[1]
    chat_id = sys.argv[2]
    file_path = os.path.abspath(sys.argv[3])
    caption = sys.argv[4] if len(sys.argv) > 4 else None
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    print(f"发送文件到 {platform}...")
    print(f"  chat_id: {chat_id}")
    print(f"  file: {file_path}")
    
    result = asyncio.run(send_to_platform(platform, chat_id, file_path, caption))
    
    if result["success"]:
        print(f"✓ 发送成功! message_id: {result.get('message_id')}")
    else:
        print(f"✗ 发送失败: {result.get('error')}")


if __name__ == "__main__":
    main()
