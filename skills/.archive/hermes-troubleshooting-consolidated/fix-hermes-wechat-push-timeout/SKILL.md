---
name: fix-hermes-wechat-push-timeout
description: 解决 Hermes cronjob 微信推送 "Timeout context manager should be used inside a task" 异步错误
author: Hermes
tags: [hermes, wechat, bugfix, cronjob]
---

# Fix Hermes WeChat Push: Timeout context manager should be used inside a task

## 问题描述
在 Hermes 中使用 cronjob 配置微信推送时，遇到错误：
```
delivery error: Weixin send failed: Timeout context manager should be used inside a task
```

这是 Hermes v0.10.0 的已知 bug，当直接使用 `deliver` 字段推送微信时，会出现异步上下文错误。

## 问题根源
错误发生在交互式会话中主动调用 `send_message` 时：
```
Error: send_message: Timeout context manager should be used inside a task
```

这是因为当前 Weixin 网关已经在运行中，再次调用推送会导致异步上下文冲突。

## 两种解决方案（根据使用场景选择）

### 方案一：cronjob 自动化推送（推荐）
**不要在任务内调用 `send_message`**，而是让 cronjob 自动投递最终响应，这样避开了异步上下文问题。

#### 具体步骤

1. **在自动化脚本中输出推送内容**，用标记包裹：
```python
print("\n--- WECHAT PUSH ---\n")
# 输出推送内容
print(push_content)
print("\n--- END ---\n")
```

2. **配置 cronjob**：
   - `deliver` 字段填写完整目标：`deliver: platform:chat_id`，例如 `weixin:o9cq80znDxnUb_ojFoc-8kBCdqdE@im.wechat`
   - prompt：要求提取内容后作为最终响应输出

```
运行脚本 `/path/to/script.py`，这会自动抓取数据并更新 Obsidian。

请捕获完整的脚本输出，找到 `--- WECHAT PUSH ---` 和 `--- END ---` 之间的内容。

**直接把这段内容作为你的最终响应**。系统会自动将响应投递到配置的微信频道。

你不需要调用 send_message 工具。
```

3. **为什么有效**：
   - 最终响应由系统在正确的上下文中投递，避开异步冲突
   - 不需要在任务内主动调用 `send_message`

---

### 方案二：cronjob 任务内主动推送（经实践验证可工作）
如果你需要在任务内进行更复杂的逻辑处理，可以让任务主动调用 `send_message`。

#### 具体步骤

1. **同样用标记输出内容**（同上）

2. **修改 cronjob prompt**：
```
运行脚本 `/path/to/your/script.py`，抓取数据并存入 Obsidian。

请捕获完整的脚本输出，找到 `--- WECHAT PUSH ---` 和 `--- END ---` 之间的内容，然后使用 send_message 工具将这段内容推送到微信目标频道。推送完成后报告结果。

你需要提取内容并主动推送。
```

⚠️ **重要说明**：
- 在当前交互式会话中直接测试 `send_message` 仍然会报 `Timeout context manager` 错误，这是正常现象
- 该错误只在交互式环境中发生，**cronjob 后台任务环境中推送是成功的**

3. **关键修复：iLink ret=-2 错误**
如果推送后仍然收不到，且错误日志显示：
```
iLink sendmessage error: ret=-2 errcode=None errmsg=unknown error
```
这通常是因为 Token 过期/失效，需要：
1. 用户重新扫码配置 iLink 机器人
2. **重启 Hermes Gateway** 让新配置生效：
```bash
launchctl stop ai.hermes.gateway && sleep 2 && launchctl start ai.hermes.gateway
```

### 完整的自动化脚本模板 (Python)

```python
#!/usr/bin/env python3
"""
每日自动抓取脚本模板
输出格式适配 Hermes cronjob 微信推送修复方案
"""

import os
from datetime import datetime
from pathlib import Path

# 配置
VAULT_PATH = Path(os.path.expanduser("~/Documents/Obsidian/AI-NEWS-HUB"))
... 你的抓取逻辑 ...

# 生成推送内容
push_content = f"""📊 **标题 | {today}**

{你的推送内容}

📍 完整内容已自动入库到 {output_file}
"""

# 按标记格式输出，供cronjob提取
print("\n--- WECHAT PUSH ---\n")
print(push_content)
print("\n--- END ---\n")

# 返回退出码
exit(0)
```

## 验证修复
修复后，cronjob 列表应该显示 `last_delivery_error: null`，说明推送成功。如果 Token 有效，iLink 推送会在几分钟内到达（有延迟是正常现象）。

## 适用场景
- Hermes cronjob 微信推送遇到 `Timeout context manager` 错误
- 需要在自动化脚本生成内容后推送到微信
- iLink 机器人推送 ret=-2 错误排查

## 附加：AutoCLI 常见问题修复

### 问题 1：财联社热点抓取标题为空
**现象**：运行 `autocli cls hot` 输出中 `title` 字段为空
**原因**：自动生成的 CSS selector 错误，误识别为 `item.ad.title`
**解决**：编辑配置文件，修正选择器：

```bash
vi ~/.autocli/adapters/cls/hot.yaml
```

找到 `title` 行，改成：
```yaml
title: item.title
```

### 问题 2：编译后被 `Killed: 9` 杀死
**现象**：`autocli --version` 直接输出 `Killed: 9`
**原因**：macOS Gatekeeper 阻止未公证的二进制运行
**解决**：
```bash
xattr -d com.apple.provenance $(which autocli)
xattr -d com.apple.quarantine $(which autocli)
```

验证：
```bash
autocli --version
```

## 验证修复

修复后，检查 cronjob 状态：
```bash
cronjob list
```
如果 `last_delivery_error` 显示 `null`，说明推送成功。

## 经验总结
1. **交互式会话 vs 后台任务**：`Timeout context manager` 错误只发生在交互式会话调用 `send_message` 时，cronjob 后台任务不受影响
2. **两种推送方式**：
   - 简单场景：`deliver: weixin:channel_id` + 提取内容作为最终响应（推荐）
   - 复杂逻辑：任务内主动调用 `send_message`（后台可用）
3. **iLink ret=-2 必查**：90% 的情况是 Token 过期，需要重启 Gateway
4. **AutoCLI macOS 编译后必做**：移除 quarantine 扩展属性，否则 Gatekeeper 会杀死进程
