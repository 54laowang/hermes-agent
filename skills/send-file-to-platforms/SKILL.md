---
name: send-file-to-platforms
description: 发送文件到企业微信、Telegram、元宝三种平台。支持 PDF、图片、文档等多种格式。
triggers:
  - 发送文件到
  - 发送PDF到
  - 发送文档到
  - 文件发送
  - send file
  - send document
keywords:
  - 文件发送
  - 企业微信
  - Telegram
  - 元宝
  - PDF
  - document
version: 1.0.0
---

# 文件发送到多平台

快速发送文件到企业微信、Telegram、元宝三种平台。

## 使用场景

- 发送 PDF 报告到企业微信
- 发送图片到 Telegram
- 发送文档到元宝

## 平台支持

| 平台 | Chat ID 格式 | 状态 |
|------|-------------|------|
| 企业微信 | 用户名（如 `WangTaoTao`） | ✅ 独立可用 |
| Telegram | 数字 chat_id（如 `7954228359`） | ⚠️ 需停止 Gateway |
| 元宝 | `direct:{user}` 或 `group:{group_code}` | ⚠️ 需停止 Gateway |

## 快速使用

### 企业微信（推荐）

```bash
# 独立可用，无需停止 Gateway
python3 ~/.hermes/scripts/send_file.py wecom WangTaoTao ~/Desktop/report.pdf "文件说明"
```

### Telegram

```bash
# 需要先停止 Gateway
hermes gateway stop
python3 ~/.hermes/scripts/send_file.py telegram 7954228359 ~/Desktop/report.pdf "文件说明"
hermes gateway start
```

### 元宝

```bash
# 需要先停止 Gateway
# chat_id 格式: direct:{user_account} 或 group:{group_code}
hermes gateway stop
python3 ~/.hermes/scripts/send_file.py yuanbao "direct:9jKEQ0JBZqgGUZSXDeUTWjBUULUcsfPHmqrsAbTOM+o=" ~/Desktop/report.pdf "文件说明"
hermes gateway start
```

## Python 代码调用

```python
import os
import asyncio

# 添加脚本路径
import sys
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))

from send_file import send_to_platform

async def main():
    # 企业微信（独立可用）
    result = await send_to_platform(
        platform="wecom",
        chat_id="WangTaoTao",
        file_path="/Users/me/Desktop/report.pdf",
        caption="测试报告"
    )
    print(f"发送结果: {result}")

asyncio.run(main())
```

## 注意事项

1. **Token 锁定问题**
   - Telegram 和元宝的 Token 在 Gateway 运行时会被锁定
   - 独立脚本发送会失败，需停止 Gateway
   - 企业微信没有此限制，可独立使用

2. **Chat ID 格式**
   - 企业微信：用户名（如 `WangTaoTao`）
   - Telegram：数字 chat_id（如 `7954228359`）
   - 元宝：特定格式
     - 私聊：`direct:{user_account}`
     - 群组：`group:{group_code}`
     - **注意**：bot_id 不是 chat_id，不能发送给 bot 自己

3. **文件路径**
   - 必须使用绝对路径
   - 文件必须存在
   - 支持的格式：PDF、图片、文档、视频等

## 配置要求

企业微信 (`~/.hermes/.env`):
```
WECOM_BOT_ID=your_bot_id
WECOM_SECRET=your_secret
```

Telegram (`~/.hermes/.env`):
```
TELEGRAM_BOT_TOKEN=your_token
```

元宝 (`~/.hermes/.env`):
```
YUANBAO_APP_ID=your_app_id
YUANBAO_APP_SECRET=your_secret
YUANBAO_WS_URL=wss://bot-wss.yuanbao.tencent.com/wss/connection
YUANBAO_API_DOMAIN=https://bot.yuanbao.tencent.com
```

## 测试结果

| 平台 | Chat ID | 状态 |
|------|---------|------|
| 企业微信 | `WangTaoTao` | ✅ 已验证 |
| Telegram | `7954228359` | ✅ 已验证 |
| 元宝 | `direct:9jKEQ0JBZqgGUZSXDeUTWjBUULUcsfPHmqrsAbTOM+o=` | ✅ 已验证 |

## 已知问题

### 元宝 chat_id 格式错误

使用 `bot_id`（如 `bot_6b20c1bb882d43069ae3acc5c5ab4121`）发送会返回成功，但消息无处投递。
正确格式：
- 私聊：`direct:{user_account}`
- 群组：`group:{group_code}`

### 跨平台文件转发限制

**不支持直接转发文件实体到其他平台**：
- 飞书 → 元宝：❌ 无法转发文件实体
- 飞书 → 企业微信：❌ 无法转发文件实体
- Telegram → 元宝：❌ 无法转发文件实体

**原因**：每个平台的文件存储系统独立，Token 和上传机制不同。

**解决方案**：
1. 先下载文件到本地
2. 再用 `send_file.py` 发送到目标平台

### 元宝客户端"不支持该消息类型"错误

**症状**：从飞书转发某些消息到元宝时，元宝客户端显示"当前版本暂不支持该消息类型"

**原因**：
- 飞书的某些消息类型（合并转发、分享卡片等）被提取成文本后发送
- 元宝客户端无法正确识别和渲染这些特殊消息格式
- 这是元宝客户端的限制，不是 Hermes 的问题

**解决方案**：
- 复制消息文本内容，重新发送纯文本消息
- 避免转发复杂的合并转发/分享卡片消息

## 相关文件

- 脚本位置: `~/.hermes/scripts/send_file.py`
- 环境变量: `~/.hermes/.env`
- Gateway 配置: `~/.hermes/config.yaml`
