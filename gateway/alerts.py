"""
Gateway Alerts Module

Provides alerting functionality for gateway conflicts and issues.
Alerts are sent to configured channels (Feishu, Telegram, etc.) when
gateway problems are detected.
"""

import os
import logging
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Alert configuration is read from environment or config.yaml
# GATEWAY_ALERT_PLATFORM: "feishu" | "telegram" | "yuanbao" | None
# GATEWAY_ALERT_CHAT_ID: target chat/group ID
# GATEWAY_ALERT_MIN_LEVEL: "error" | "warning" | "info" (default: "warning")


def get_alert_config() -> dict:
    """Load alert configuration from environment or config.yaml."""
    config = {
        "platform": os.environ.get("GATEWAY_ALERT_PLATFORM"),
        "chat_id": os.environ.get("GATEWAY_ALERT_CHAT_ID"),
        "min_level": os.environ.get("GATEWAY_ALERT_MIN_LEVEL", "warning"),
        "enabled": False,
    }

    if config["platform"] and config["chat_id"]:
        config["enabled"] = True
    else:
        # Try to read from config.yaml
        try:
            from hermes_constants import get_hermes_home
            import yaml

            config_path = get_hermes_home() / "config.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    cfg = yaml.safe_load(f) or {}
                alert_cfg = cfg.get("gateway", {}).get("alerts", {})
                if alert_cfg.get("enabled"):
                    config["platform"] = alert_cfg.get("platform", config["platform"])
                    config["chat_id"] = alert_cfg.get("chat_id", config["chat_id"])
                    config["min_level"] = alert_cfg.get("min_level", config["min_level"])
                    config["enabled"] = bool(config["platform"] and config["chat_id"])
        except Exception as e:
            logger.debug("Could not load alert config from config.yaml: %s", e)

    return config


_LEVEL_PRIORITY = {"info": 0, "warning": 1, "error": 2}


def should_send_alert(level: str, config: dict) -> bool:
    """Check if alert should be sent based on level threshold."""
    if not config.get("enabled"):
        return False

    min_level = config.get("min_level", "warning")
    return _LEVEL_PRIORITY.get(level, 0) >= _LEVEL_PRIORITY.get(min_level, 0)


def send_gateway_alert(
    level: str,
    title: str,
    message: str,
    platform: Optional[str] = None,
    chat_id: Optional[str] = None,
) -> bool:
    """
    Send a gateway alert to the configured channel.

    Args:
        level: Alert level - "info", "warning", or "error"
        title: Alert title/subject
        message: Detailed message body
        platform: Override platform (defaults to config)
        chat_id: Override chat ID (defaults to config)

    Returns:
        True if alert was sent successfully, False otherwise
    """
    config = get_alert_config()

    # Override with explicit args if provided
    platform = platform or config.get("platform")
    chat_id = chat_id or config.get("chat_id")

    if not should_send_alert(level, config):
        logger.debug("Alert suppressed (level=%s, min_level=%s)", level, config.get("min_level"))
        return False

    if not platform or not chat_id:
        logger.debug("Alert not configured (platform=%s, chat_id=%s)", platform, chat_id)
        return False

    # Format message
    level_emoji = {"info": "ℹ️", "warning": "⚠️", "error": "🚨"}.get(level, "📢")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    full_message = f"{level_emoji} **{title}**\n\n{message}\n\n_时间: {timestamp}_"

    # Send via appropriate platform
    try:
        if platform == "feishu":
            return _send_feishu_alert(chat_id, full_message)
        elif platform == "telegram":
            return _send_telegram_alert(chat_id, full_message)
        elif platform == "yuanbao":
            return _send_yuanbao_alert(chat_id, full_message)
        else:
            logger.warning("Unknown alert platform: %s", platform)
            return False
    except Exception as e:
        logger.error("Failed to send gateway alert: %s", e)
        return False


def _send_feishu_alert(chat_id: str, message: str) -> bool:
    """Send alert via Feishu API."""
    try:
        import httpx
        import json

        # Get Feishu credentials from environment
        app_id = os.environ.get("FEISHU_APP_ID")
        app_secret = os.environ.get("FEISHU_APP_SECRET")

        if not app_id or not app_secret:
            logger.debug("Feishu credentials not configured for alerts")
            return False

        # Get tenant access token
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                json={"app_id": app_id, "app_secret": app_secret},
            )
            resp.raise_for_status()
            token = resp.json().get("tenant_access_token")

            if not token:
                return False

            # Send message with proper JSON encoding
            resp = client.post(
                "https://open.feishu.cn/open-apis/im/v1/messages",
                params={"receive_id_type": "chat_id"},
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "receive_id": chat_id,
                    "msg_type": "text",
                    "content": json.dumps({"text": message}, ensure_ascii=False),
                },
            )
            resp.raise_for_status()
            return resp.json().get("code") == 0

    except Exception as e:
        logger.error("Feishu alert failed: %s", e)
        return False


def _send_telegram_alert(chat_id: str, message: str) -> bool:
    """Send alert via Telegram Bot API."""
    try:
        import httpx

        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            logger.debug("Telegram bot token not configured for alerts")
            return False

        with httpx.Client(timeout=10) as client:
            resp = client.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                },
            )
            resp.raise_for_status()
            return resp.json().get("ok", False)

    except Exception as e:
        logger.error("Telegram alert failed: %s", e)
        return False


def _send_yuanbao_alert(chat_id: str, message: str) -> bool:
    """Send alert via Yuanbao (腾讯元宝)."""
    # Yuanbao uses WebSocket and is more complex
    # For now, log and return False
    logger.info("Yuanbao alert not implemented yet: %s", message[:100])
    return False


def check_gateway_conflict() -> Optional[dict]:
    """
    Check if there are multiple gateway processes running.

    Returns:
        Conflict info dict if conflict detected, None otherwise
    """
    import subprocess

    try:
        # Find all gateway processes
        result = subprocess.run(
            ["pgrep", "-fl", "gateway run"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        lines = [l for l in result.stdout.strip().split("\n") if l]
        if len(lines) <= 1:
            return None

        # Multiple gateways found
        pids = []
        for line in lines:
            parts = line.split(None, 1)
            if parts:
                pids.append(int(parts[0]))

        return {
            "count": len(pids),
            "pids": pids,
            "message": f"检测到 {len(pids)} 个 gateway 进程同时运行: {pids}",
        }

    except Exception as e:
        logger.debug("Gateway conflict check failed: %s", e)
        return None


def monitor_gateway_health() -> None:
    """
    Periodic health check for gateway conflicts.

    This function is intended to be called from a cron job or
    scheduled task.
    """
    conflict = check_gateway_conflict()

    if conflict:
        send_gateway_alert(
            level="warning",
            title="Gateway 进程冲突",
            message=conflict["message"],
        )
        logger.warning("Gateway conflict detected: %s", conflict)
