---
name: hermes-gateway-platform-config
title: Hermes Gateway 多平台配置与排错指南
description: 企业微信 (WeCom)、QQ Bot 等消息平台接入、错误码排查、网关状态验证
---

# Hermes Gateway 多平台配置与排错指南

## 核心概念

Hermes Gateway 支持 14+ 消息平台接入，每个平台通过独立的适配器连接。

⚠️ **当前限制**：原生网关每个平台类型默认只能配置一个 Bot 实例。如需多机器人，可使用多实例部署或 OpenClaw 企业版。

---

## 企业微信 (WeCom) 配置

### 两种接入模式

| 模式 | 说明 | 推荐场景 |
|------|------|----------|
| **WeCom AI Bot** | WebSocket 直连，无需公网 IP | ⭐ 推荐，最简单 |
| **WeCom Callback** | 自建应用，Webhook 回调 | 企业深度定制 |

---

### 模式 1：WeCom AI Bot（WebSocket 模式）⭐ 推荐

**企业微信后台准备**：
1. 登录 [企业微信管理后台](https://work.weixin.qq.com/)
2. 应用管理 → 自建 → 创建应用
3. **必须启用「AI 机器人」功能**（在功能标签页）
4. 在 AI 机器人页面获取 **BotID** 和 **Secret**

> ❗ 关键：不要使用普通应用的 AgentID/Secret，必须用 AI 机器人专属凭证！

**配置步骤**：

1. 运行交互式向导：
```bash
hermes gateway setup
```
选择 `WeCom (Enterprise WeChat)`，按提示输入 BotID 和 Secret。

2. 或者直接编辑环境变量文件，添加：
```
WECOM_BOT_ID=your_bot_id_here
WECOM_SECRET=your_bot_secret_here
WECOM_GROUP_POLICY=open
WECOM_DM_POLICY=open
```

3. 在主配置文件中启用平台：
```yaml
platforms:
  wecom:
    enabled: true
    allowed_users: []  # 用户白名单，空=全部允许
    allowed_groups: [] # 群组白名单
```

4. 重启网关：
```bash
hermes gateway restart
```

---

### 模式 2：WeCom Callback（自建应用）

适合需要深度定制的企业场景，需要公网可访问的服务器。

需配置的环境变量：
- `WECOM_CORP_ID` - 企业 ID
- `WECOM_AGENT_ID` - 应用 AgentID
- `WECOM_SECRET` - 应用 Secret
- `WECOM_TOKEN` - 回调令牌（自定义）
- `WECOM_AES_KEY` - 消息加密密钥

---

## QQ Bot 配置

**腾讯限制**：单个 QQ 账号最多可创建 **5 个 QQ Bot**。

### 单 Bot 配置

1. 运行配置向导：`hermes gateway setup`
2. 选择 `QQ Bot`
3. 输入从 QQ 开放平台获取的 `AppID` 和 `Secret`

环境变量：
```
QQ_APP_ID=your_app_id
QQ_CLIENT_SECRET=your_client_secret
QQ_ALLOW_ALL_USERS=true
```

### 多 Bot 部署方案

| 方案 | 说明 |
|------|------|
| **OpenClaw 原生** | 企业级分支，原生 accounts 对象支持多 Bot，数据隔离 |
| **多实例部署** | 每个 Bot 使用独立配置目录，分别启动网关进程 |
| **Docker 容器化** | 每个容器一个 Bot，完全隔离 |

OpenClaw 多 Bot 配置示例：
```bash
# 添加多个 Bot
openclaw channels add --channel qqbot --token "APP_ID_1:SECRET_1"
openclaw channels add --channel qqbot --token "APP_ID_2:SECRET_2"

# 创建并绑定多 Agent
openclaw agents add tech_support --workspace ~/.openclaw/workspace/tech
openclaw agents bind --agent tech_support --bind qqbot:bot1_id
```

---

## ✅ 连接状态验证

### 快速检查命令

```bash
# 查看网关服务状态
hermes gateway status

# 查看详细连接状态（JSON格式）
cat ~/.hermes/gateway_state.json
```

### 状态字段解读

| 状态值 | 说明 |
|--------|------|
| `connected` | ✅ 正常连接 |
| `retrying` | 🔄 连接失败，正在重试 |
| `fatal` | ❌ 致命错误，无法自动恢复 |

### 查看日志排查问题

```bash
# 实时查看网关日志
tail -f ~/.hermes/logs/gateway.log

# 查看最近 50 行错误日志
tail -50 ~/.hermes/logs/gateway.error.log
```

---

## 🔧 常见错误码排查

### 企业微信错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| **853000** | invalid bot_id or secret | 1. 检查 BotID/Secret 复制是否正确<br>2. 确认启用了「AI 机器人」能力<br>3. 确认应用已发布<br>4. 检查服务器 IP 是否在企业白名单 |
| `wecom_connect_error` | WebSocket 连接失败 | 检查网络、防火墙、凭证有效性 |

### 微信 (Weixin/iLink) 错误

| 错误现象 | 可能原因 | 解决方案 |
|----------|----------|----------|
| **send_message 报 "No home channel set"** | 1. 微信平台未连接<br>2. Token 过期<br>3. 配置格式错误 | 1. 检查 `WEIXIN_HOME_CHANNEL` 不含 `@im.wechat` 后缀<br>2. 查看网关日志确认微信连接状态<br>3. 重新扫码获取新 Token |
| **网关日志无微信连接记录** | Token 失效/过期 | 运行 `hermes gateway setup` 选择 Weixin 扫码重新登录 |
| **iLink sendmessage ret=-2** | Token 无效或过期 | 同上，重新扫码 + 重启网关 |
| **微信平台 enabled: true 但未连接** | 缺少 `WEIXIN_TOKEN` 或 `WEIXIN_ACCOUNT_ID` | 检查 `.env` 文件是否包含有效凭证 |
| **平台静默失败，无任何错误日志** | Token 格式问题或平台初始化异常 | 见下方「微信平台静默失败诊断」 |

#### 微信平台静默失败诊断

**症状**：
- `hermes status` 显示微信 `configured`
- `platforms.weixin.enabled: true` 配置正确
- 网关日志中**完全没有**微信连接/断开记录（飞书/Telegram 正常）
- `send_message` 工具报 "No home channel set"
- `~/.hermes/logs/gateway.error.log` 无任何微信错误

**诊断步骤**：

1. **检查 Token 是否完整保存**：
```bash
grep -i "WEIXIN" ~/.hermes/.env
# 应包含完整的 WEIXIN_ACCOUNT_ID 和 WEIXIN_TOKEN
# 如果 Token 显示为 "xxx...xxx" 截断格式，说明可能保存不完整
```

2. **强制清理并重新扫码**：
```bash
# 1. 停止网关
pkill -f "hermes.*gateway"

# 2. 清理旧 Token（可选，谨慎）
# rm ~/.hermes/weixin/accounts/*

# 3. 重新扫码
hermes gateway setup
# 选择 Weixin / WeChat → 扫码登录

# 4. 强制重启网关
hermes gateway restart

# 5. 等待并检查日志
sleep 8 && tail -50 ~/.hermes/logs/gateway.log | grep -i weixin
```

3. **对比其他平台**：
```bash
# 检查飞书连接日志（作为参考）
tail -100 ~/.hermes/logs/gateway.log | grep -i "feishu\|lark"
# 如果飞书正常而微信无日志，说明微信平台初始化有问题
```

4. **检查网关进程**：
```bash
# 确认只有一个网关进程
ps aux | grep -i "hermes.*gateway" | grep -v grep
# 多个网关进程可能导致配置冲突
```

**可能原因**：
- Token 扫码成功但保存不完整
- 多个网关进程竞争资源
- 微信平台适配器内部异常（无外显错误）
- 旧 Token 缓存问题

**解决方案优先级**：
1. 强制杀掉所有网关进程后重启
2. 重新扫码获取新 Token
3. 检查 `.env` 文件 Token 完整性
4. 查看 Hermes 源码 `gateway/platforms/weixin.py` 排查

#### 微信 Token 过期诊断流程

1. **检查网关日志**：
```bash
tail -100 ~/.hermes/logs/gateway.log | grep -i "weixin"
```
如果没有任何微信连接日志，说明平台未初始化。

2. **检查 Token 配置**：
```bash
grep -i "WEIXIN" ~/.hermes/.env
```
应包含：`WEIXIN_ACCOUNT_ID`、`WEIXIN_TOKEN`、`WEIXIN_BASE_URL`

3. **检查 HOME_CHANNEL 配置**：
```bash
grep "WEIXIN_HOME_CHANNEL" ~/.hermes/config.yaml
```
⚠️ **注意**：`WEIXIN_HOME_CHANNEL` 应该只包含用户 ID，**不要**包含 `@im.wechat` 后缀！

```yaml
# ❌ 错误格式
WEIXIN_HOME_CHANNEL: o9cq80znDxnUb_ojFoc-8kBCdqdE@im.wechat

# ✅ 正确格式
WEIXIN_HOME_CHANNEL: o9cq80znDxnUb_ojFoc-8kBCdqdE
```

4. **重新扫码获取 Token**：
```bash
hermes gateway setup
# 选择 Weixin / WeChat
# 按提示扫码登录
```

5. **重启网关使配置生效**：
```bash
hermes gateway restart
```

### 通用错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `*_lock` | Token 已被占用 | 停止使用同一凭证的其他网关进程 `kill <PID>` |
| 无错误但收不到消息 | 权限/可见范围问题 | 检查应用可见范围、群聊是否添加机器人 |

### 万能修复：重启网关

90% 的连接问题可通过重启解决：
```bash
hermes gateway restart

# 等待5秒后检查状态
sleep 5 && cat ~/.hermes/gateway_state.json
```

---

## API Server 配置

API Server 提供 OpenAI 兼容的 HTTP API，允许外部应用通过 REST API 与 Hermes 交互。

### 配置步骤

1. **编辑配置文件** `~/.hermes/config.yaml`：
```yaml
platforms:
  api_server:
    enabled: true
    cors_origins: "*"  # 或指定域名列表
    extra:
      host: 127.0.0.1
      port: 8642
      key: "your-secure-api-key-here"  # ⚠️ 必须放在 extra 内部！
```

2. **生成安全的 API Key**：
```bash
# 方法1: 使用 openssl
openssl rand -base64 32

# 方法2: 使用 Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. **重启 Gateway**：
```bash
hermes gateway restart
```

### ⚠️ 常见配置错误

**错误示例**（key 在错误位置）：
```yaml
platforms:
  api_server:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8642
    key: "your-key"  # ❌ 错误！不会被读取
```

**正确示例**（key 在 extra 内部）：
```yaml
platforms:
  api_server:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8642
      key: "your-key"  # ✅ 正确位置
```

> **原因**：API Server 适配器从 `extra.get("key")` 读取配置，而不是从 `platforms.api_server.key`。

### 验证配置

```bash
# 测试健康检查
curl http://127.0.0.1:8642/health

# 测试认证（无 key 应返回错误）
curl http://127.0.0.1:8642/v1/models

# 测试认证（正确 key 应返回数据）
curl -H "Authorization: Bearer your-key" http://127.0.0.1:8642/v1/models
```

### 可用端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查（无需认证） |
| `/health/detailed` | GET | 详细状态（无需认证） |
| `/v1/models` | GET | 列出可用模型（需认证） |
| `/v1/chat/completions` | POST | OpenAI 兼容聊天接口（需认证） |
| `/v1/responses` | POST | OpenAI Responses API（需认证） |

### 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 启动警告 "No API key configured" | key 未在 extra 内部 | 将 key 移到 `platforms.api_server.extra.key` |
| 端口被占用 | 其他进程使用 8642 | `lsof -i :8642` 查找并停止进程 |
| 认证失败返回 401 | API key 不正确 | 检查 Authorization header 格式 |
| 端点返回 404 | 路径错误 | 使用正确的端点路径（如 /v1/models 不是 /api/v1/models） |

---

## Yuanbao (元宝) 配置

元宝是腾讯的企业消息平台，支持群聊和私信，通过 WebSocket 连接。

### 配置步骤

1. **获取凭证**：
   - 下载元宝 APP：https://yuanbao.tencent.com/
   - 在 APP 中：PAI → My Bot → 创建新机器人
   - 创建后复制 **App ID** 和 **App Secret**

2. **运行配置向导**：
```bash
hermes gateway setup
```
选择 `Yuanbao`，输入 App ID 和 App Secret。

3. **配置环境变量**（`.env` 文件）：
```bash
YUANBAO_APP_ID=your_app_id
YUANBAO_APP_SECRET=your_app_secret
YUANBAO_WS_URL=wss://bot-wss.yuanbao.tencent.com/wss/connection
YUANBAO_API_DOMAIN=https://bot.yuanbao.tencent.com
```

4. **启用平台**（`config.yaml`）：
```yaml
platforms:
  yuanbao:
    enabled: true
    extra:
      app_id: ${YUANBAO_APP_ID}
      app_secret: ${YUANBAO_APP_SECRET}
      ws_url: ${YUANBAO_WS_URL}
      api_domain: ${YUANBAO_API_DOMAIN}
```

5. **重启网关**：
```bash
hermes gateway restart
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| HTTP 404 错误 | WebSocket URL 错误 | 使用正确的 URL：`wss://bot-wss.yuanbao.tencent.com/wss/connection` |
| 连接超时 | 网络问题或防火墙 | 检查网络连接和防火墙设置 |
| 认证失败 | App ID/Secret 错误 | 确认凭证正确且机器人已激活 |

### 相关技能

- `yuanbao` - 元宝群组 @mention 和成员查询

---

## 支持的平台列表

通过 `hermes gateway setup` 可配置：

- Telegram、Discord、Slack、Matrix、Mattermost
- WhatsApp、Signal、Email、SMS (Twilio)
- DingTalk (钉钉)、Feishu/Lark (飞书)
- **WeCom (企业微信)** - AI Bot / Callback 双模式
- Weixin / WeChat (个人微信)
- BlueBubbles (iMessage)
- **QQ Bot** - 官方 API v2
- **Yuanbao (元宝)** - 腾讯企业消息平台 ⭐ 新增
- **API Server** - OpenAI 兼容 REST API

---

## 配置文件位置

| 文件 | 用途 |
|------|------|
| 主配置文件 | 平台开关、白名单、功能选项 |
| 环境变量文件 | API 密钥、Bot Token、Secret 等敏感信息 |
| 状态文件 | 网关运行状态、各平台实时连接状态 |
| 日志目录 | 运行日志和错误日志 |

---

## 最佳实践

1. **先测试后生产**：先用测试账号验证连接，再正式发布
2. **白名单控制**：生产环境建议配置 `allowed_users` 和 `allowed_groups`
3. **定期重启**：网关长时间运行可能出现连接断开，建议定期重启
4. **日志监控**：监控错误日志及时发现连接问题

---

## 相关技能

- `setup-daily-ai-tech-hackernews-autopush` - 微信消息推送自动化
- `fix-autocli-cls-hot-empty` - AutoCLI 常见问题修复
