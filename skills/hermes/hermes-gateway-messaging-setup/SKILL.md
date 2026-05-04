---
name: Hermes Gateway 消息平台配置与故障排查
description: 完整的 Hermes 多平台消息接入指南，包括 QQ Bot、企业微信(WeCom)、多机器人配置方案、进程冲突排查和用户配对批准流程
tags:
  - hermes
  - gateway
  - wecom
  - qqbot
  - 企业微信
  - 多机器人
  - troubleshooting
---

# Hermes Gateway 消息平台配置与故障排查

## 概述
本技能涵盖 Hermes Agent 消息网关的完整配置流程，包括多平台接入、多机器人方案、进程冲突排查和用户配对管理。

---

## 🚀 企业微信 (WeCom) 配置

### 两种接入模式

| 模式 | 说明 | 推荐场景 |
|------|------|----------|
| **WeCom AI Bot** | 官方 AI Bot，WebSocket 直连，无需公网 IP | ⭐ 推荐，最简单 |
| **WeCom Callback** | 自建应用，Webhook 回调，需要公网 | 企业定制开发 |

### 方法一：交互式配置向导
```bash
hermes gateway setup
```
选择 `WeCom (Enterprise WeChat)` 或 `WeCom Callback (Self-Built App)`，按提示填入配置。

### 方法二：手动配置

#### 模式 1：WeCom AI Bot（WebSocket）
1. 企业微信后台创建 AI Bot 应用，启用 "AI 机器人" 能力
2. 获取 Bot ID 和 Secret
3. 通过配置向导或环境变量设置凭证
4. 在 config.yaml 中启用平台并配置访问策略
5. 重启网关生效

```bash
hermes gateway restart
```

#### 模式 2：WeCom Callback（自建应用）
需要公网 IP 和回调地址，适合深度定制场景。

---

## 👥 用户配对管理

### 查看待处理配对请求
```bash
hermes pairing list
```

### 批准配对
```bash
hermes pairing approve <platform> <code>
# 示例: hermes pairing approve wecom CWB5FYKX
```

### 撤销访问
```bash
hermes pairing revoke <platform> <user_id>
```

### 清空待处理请求
```bash
hermes pairing clear-pending
```

---

## 🤖 多 QQ 机器人配置方案

### 现状说明
Hermes 原生网关目前是单 Bot 设计，每个平台类型默认只能配置一个 Bot。

### 方案一：OpenClaw 原生多机器人（推荐）
OpenClaw 是 Hermes 的企业级分支，原生支持多 Bot：

```bash
# 安装插件
openclaw plugins install @tencent-connect/openclaw-qqbot@latest

# 添加多个 Bot
openclaw channels add --channel qqbot --token "APP_ID_1:SECRET_1"
openclaw channels add --channel qqbot --token "APP_ID_2:SECRET_2"

# 创建多 Agent 并绑定
openclaw agents add tech_support --workspace ~/.openclaw/workspace/tech
openclaw agents bind --agent tech_support --bind qqbot:bot1_id
```

### 方案二：Hermes Gateway 多实例部署
每个 Bot 使用独立的配置目录，通过环境变量指定不同的配置路径，启动多个网关进程。

### 方案三：Docker 容器化部署
使用 docker-compose 管理多个容器实例，每个容器一个 Bot。

---

## 🔍 常见故障排查

### 问题 1：平台显示 "fatal"，提示 token 被占用

**症状**:
```
feishu_app_lock: Another local Hermes gateway is already using this Feishu app_id (PID XXXXX)
weixin-bot-token_lock: Weixin bot token already in use (PID XXXXX)
```

**原因**: 存在旧的网关进程没有正常退出，持有了平台 token。

**解决步骤**:
1. 检查旧进程:
```bash
ps aux | grep <PID>
# 示例: ps aux | grep 41520
```

2. 杀掉旧进程:
```bash
kill <PID>
# 示例: kill 41520
```

3. 重启网关:
```bash
hermes gateway restart
```

4. 验证状态（等待 5 秒后）:
```bash
hermes gateway status
```

### 问题 2：WeCom 连接失败，错误码 853000

**原因**: Bot ID 或 Secret 无效，或未正确启用 "AI 机器人" 能力。

**解决步骤**:
1. 确认使用的是 AI Bot 专属的 BotID/Secret（不是普通应用的 AgentID）
2. 确认应用已发布，不在"开发中"状态
3. 确认账号在应用可见范围内
4. 检查企业 IP 白名单配置
5. 重新运行 `hermes gateway setup` 输入正确的凭证

### 问题 3：Bot 不回复消息

**排查清单**:
- ✅ 检查网关状态: `hermes gateway status`
- ✅ 查看网关日志
- ✅ 确认用户已配对批准: `hermes pairing list`
- ✅ 检查平台策略配置
- ✅ 重启网关: `hermes gateway restart`

---

## 📊 状态检查命令

### 查看网关状态
```bash
hermes gateway status
```

### 查看连接详情
检查网关状态文件获取每个平台的详细连接状态和错误信息。

### 查看频道目录
查看已记录的聊天频道列表。

---

## ⚠️ 腾讯官方限制

- 单个 QQ 账号最多可创建 **5 个 QQ Bot**
- 企业微信 AI Bot 需要企业管理员权限创建

---

## 💡 最佳实践

1. **优先使用交互式配置向导**：`hermes gateway setup` 比手动编辑配置文件更不容易出错
2. **定期检查网关状态**：遇到问题先运行 `hermes gateway status`
3. **查看日志定位问题**：日志文件包含详细的错误信息
4. **网关重启后等待**：重启后需要等待 5-10 秒让所有平台完成连接
5. **多实例使用独立目录**：避免配置文件冲突和数据混乱

---

## 🔗 相关技能

- `fix-hermes-wechat-push-timeout` - 解决微信推送异步上下文错误

---

## 更新日志

- 2026-04-23: 初始版本，包含企业微信配置、多机器人方案、进程冲突排查
