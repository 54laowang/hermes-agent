---
name: hermes-web-ui-jobs-api-config
description: Hermes Web UI Jobs API 认证配置 — 解决定时任务页面返回 Invalid API key 的问题
version: 1.0.0
category: hermes
tags: [web-ui, jobs, api, authentication, configuration]
---

# Hermes Web UI Jobs API 认证配置

## 问题症状

Web UI 的 Jobs（定时任务）页面返回错误：
```
{"error":{"message":"Invalid API key","type":"invalid_request_error","code":"invalid_api_key"}}
```

## 根本原因

Web UI 的 `gateway-manager.ts` 中的 `getApiKey()` 方法从 `.env` 文件读取 `API_SERVER_KEY`：

```typescript
getApiKey(profileName?: string): string | null {
  const name = profileName || this.activeProfile
  const envPath = join(this.profileDir(name), '.env')
  if (!existsSync(envPath)) return null
  const content = readFileSync(envPath, 'utf-8')
  const match = content.match(/^API_SERVER_KEY\s*=\s*"?([^"\n]+)"?/m)
  return match?.[1]?.trim() || null
}
```

对于 `default` profile，`profileDir('default')` 返回 `~/.hermes`，所以 `.env` 文件必须放在 `~/.hermes/.env`。

## 解决方案

### 步骤 1：获取 API Server Key

从 `~/.hermes/config.yaml` 中读取：

```bash
grep -A 5 "api_server:" ~/.hermes/config.yaml
```

找到 `key` 字段的值。

### 步骤 2：创建 .env 文件

**Default profile**：
```bash
cat > ~/.hermes/.env << 'EOF'
API_SERVER_KEY="your-api-server-key"
EOF
```

**其他 profile**：
```bash
mkdir -p ~/.hermes/profiles/<profile-name>
cat > ~/.hermes/profiles/<profile-name>/.env << 'EOF'
API_SERVER_KEY="your-api-server-key"
EOF
```

### 步骤 3：重启 Web UI

```bash
pkill -f hermes-web-ui
hermes-web-ui
```

### 步骤 4：验证

```bash
# 获取 Web UI token
TOKEN=$(grep -o 'token=[^"]*' ~/.hermes-web-ui/server.log | head -1 | cut -d= -f2)

# 测试 Jobs API
curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8648/api/hermes/jobs" | jq -r '.jobs | length'
```

应该返回定时任务数量（非 0）。

## 文件位置总结

```
~/.hermes/
├── config.yaml           # Hermes 主配置（包含 api_server.key）
├── .env                  # Web UI 读取的 API_SERVER_KEY ⭐ 必须创建
├── state.db              # 会话数据库
└── gateway.pid           # 网关进程 ID

~/.hermes/profiles/<name>/  # 其他 profile
├── config.yaml
└── .env                  # Web UI 读取的 API_SERVER_KEY
```

## 相关文件

- `packages/server/src/services/hermes/gateway-manager.ts` — getApiKey() 方法
- `packages/server/src/controllers/hermes/jobs.ts` — Jobs API 代理控制器

## 常见问题

### Q: 为什么不直接从 config.yaml 读取？

A: Web UI 的设计是多 profile 架构，`.env` 文件用于存储每个 profile 的环境变量。这是一个架构决策，可能是因为 `.env` 文件更适合存储敏感信息（如 API keys）。

### Q: 会话记录正常但定时任务不显示？

A: 这是两个不同的 API：
- Sessions API: 直接读取 `~/.hermes/state.db`（本地数据库）
- Jobs API: 代理到 Hermes Gateway 的 `/api/jobs` 端点（需要认证）

所以会话记录可能正常显示，但定时任务需要正确的 API key 配置。

## 相关 PR

- https://github.com/EKKOLearnAI/hermes-web-ui/pull/369
