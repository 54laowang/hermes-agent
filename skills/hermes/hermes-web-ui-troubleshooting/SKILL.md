---
name: hermes-web-ui-troubleshooting
description: Hermes Web UI 问题诊断与修复指南 - 涵盖会话同步、数据库架构、API 路由、运行时补丁等常见问题的系统性排查流程
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, web-ui, troubleshooting, database, sync, patch]
    homepage: https://github.com/EKKOLearnAI/hermes-web-ui
    related_skills: [hermes-agent]
---

# Hermes Web UI 问题诊断与修复

Hermes Web UI 是 Hermes Agent 的 Web 仪表盘，提供会话管理、使用统计、平台配置、定时任务等功能。本技能涵盖常见问题的诊断和修复方法。

## 架构概览

```
hermes-web-ui/
├── dist/server/index.js          # 打包后的服务器代码（可运行时修补）
├── packages/
│   ├── client/src/               # Vue 3 前端
│   └── server/src/               # Koa BFF 服务器
│       ├── db/hermes/            # 数据库层
│       │   ├── session-store.ts  # 会话存储
│       │   ├── sessions-db.ts    # 会话查询逻辑
│       │   └── schemas.ts        # 表结构定义
│       └── services/hermes/      # 业务逻辑
│           ├── session-sync.ts   # 会话同步
│           └── hermes-cli.ts     # CLI 包装
└── ~/.hermes-web-ui/
    ├── hermes-web-ui.db          # Web UI 本地数据库
    ├── server.log                # 服务器日志
    └── .token                    # 认证令牌
```

**关键数据源：**
- Web UI 数据库：`~/.hermes-web-ui/hermes-web-ui.db`
- Hermes 会话数据库：`~/.hermes/state.db`（或 profile 目录下）
- 配置文件：`~/.hermes/config.yaml` 中的 `platforms.api_server`

## 常见问题诊断流程

### 1. 会话不显示问题

**症状：** Web UI 启动正常，但会话列表为空

**诊断步骤：**

```bash
# 1. 检查源数据库是否有数据
sqlite3 ~/.hermes/state.db "SELECT source, COUNT(*) FROM sessions GROUP BY source;"

# 2. 检查 Web UI 数据库
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "SELECT COUNT(*) FROM sessions;"

# 3. 检查同步日志
grep -i "session-sync" ~/.hermes-web-ui/server.log

# 4. 检查 Web UI 版本
hermes-web-ui --version
```

**常见原因：**
- 同步逻辑过滤条件过严（如只同步 `api_server` 来源）
- 数据库路径不匹配
- Node.js 版本不满足要求（需要 >= 22.5 才有 `node:sqlite`）

**修复方法：**
参见 `references/session-sync-fix.md`

### 1.5. 定时任务不显示问题

**症状：** 会话列表正常，但定时任务（Cron Jobs）列表为空或返回 `Invalid API key`

**诊断步骤：**

```bash
# 1. 检查 Hermes Agent 是否有定时任务
hermes cron list

# 2. 直接测试 Hermes Gateway API
curl -H "Authorization: Bearer <hermes-api-key>" http://127.0.0.1:8642/api/jobs

# 3. 测试 Web UI 代理
curl -H "Authorization: Bearer <web-ui-token>" http://127.0.0.1:8648/api/hermes/jobs

# 4. 检查 .env 文件是否存在
ls -la ~/.hermes/.env
```

**根本原因：**

Web UI 的 `gateway-manager.ts` 从 `~/.hermes/.env` 文件读取 `API_SERVER_KEY`：

```typescript
// packages/server/src/services/hermes/gateway-manager.ts
getApiKey(profileName?: string): string | null {
  const name = profileName || this.activeProfile
  const envPath = join(this.profileDir(name), '.env')
  if (!existsSync(envPath)) return null
  // ...
}
```

对于 `default` profile，`profileDir('default')` 返回 `~/.hermes`（不是 `~/.hermes/profiles/default`）。

**修复方法：**

```bash
# 从 config.yaml 提取 API key
API_KEY=$(grep -A 5 "api_server:" ~/.hermes/config.yaml | grep "key:" | awk '{print $2}')

# 创建 .env 文件
cat > ~/.hermes/.env << EOF
API_SERVER_KEY="$API_KEY"
EOF

# 重启 Web UI
hermes-web-ui restart
```

**验证：**
```bash
# 应该返回任务数量
curl -H "Authorization: Bearer <token>" http://127.0.0.1:8648/api/hermes/jobs | jq '.jobs | length'
```

### 2. API 404 错误

**症状：** 前端请求返回 404

**诊断步骤：**

```bash
# 检查 Web UI 端口（默认 8648，不是 3000）
netstat -an | grep -E "8648|8642"

# 检查路由定义
grep -o "router\.[a-z]*('[^']*'" ~/.nvm/versions/node/*/lib/node_modules/hermes-web-ui/dist/server/index.js | head -30

# 测试 API
curl -H "Authorization: Bearer <token>" http://127.0.0.1:8648/api/<endpoint>
```

**常见原因：**
- 访问了错误的端口（Web UI 在 8648，Hermes Gateway API 在 8642）
- 路由不存在或未注册

### 3. 认证失败

**症状：** API 返回 401 Unauthorized

**诊断步骤：**

```bash
# 获取当前 token
cat ~/.hermes-web-ui/.token

# 或从日志中查找
grep "Auth enabled" ~/.hermes-web-ui/server.log
```

**修复：**
```bash
# URL 格式
http://localhost:8648/#/?token=<your-token>

# API 请求格式
curl -H "Authorization: Bearer <token>" http://127.0.0.1:8648/api/...
```

### 4. 运行时代码修补

当需要快速修复 bug 而不想重新构建时，可以直接修改打包后的代码：

**步骤：**
```bash
# 1. 定位问题代码
grep -n "problematic-pattern" ~/.nvm/versions/node/*/lib/node_modules/hermes-web-ui/dist/server/index.js

# 2. 备份原文件
cp ~/.nvm/versions/node/*/lib/node_modules/hermes-web-ui/dist/server/index.js{,.backup}

# 3. 应用补丁
sed -i '' 's/old-pattern/new-pattern/g' ~/.nvm/versions/node/*/lib/node_modules/hermes-web-ui/dist/server/index.js

# 4. 验证修改
grep "new-pattern" ~/.nvm/versions/node/*/lib/node_modules/hermes-web-ui/dist/server/index.js

# 5. 重启服务
hermes-web-ui restart
```

**注意事项：**
- 这是临时方案，应该向官方仓库提交 PR
- 每次更新 Web UI 都会覆盖修改
- 保留备份文件以便回滚

## 数据库架构

### Web UI 数据库（hermes-web-ui.db）

**核心表：**
- `sessions` - 会话元数据
- `messages` - 会话消息
- `session_usage` - 使用统计
- `gc_*` - 群聊相关表

**关键字段：**
```sql
-- sessions 表
id TEXT PRIMARY KEY
profile TEXT NOT NULL DEFAULT 'default'
source TEXT NOT NULL DEFAULT 'api_server'  -- ⚠️ 默认值可能导致过滤问题
model TEXT NOT NULL DEFAULT ''
title TEXT
started_at INTEGER NOT NULL
ended_at INTEGER
last_active INTEGER NOT NULL
```

### Hermes 源数据库（state.db）

**查询示例：**
```bash
# 按来源统计
sqlite3 ~/.hermes/state.db "SELECT source, COUNT(*) FROM sessions GROUP BY source;"

# 最近会话
sqlite3 ~/.hermes/state.db "SELECT id, title, source FROM sessions ORDER BY started_at DESC LIMIT 5;"
```

## 关键源码位置

### 会话同步逻辑

**文件：** `packages/server/src/services/hermes/session-sync.ts`

**关键函数：**
- `syncAllHermesSessionsOnStartup()` - 启动时同步入口
- `syncProfileSessions(profile)` - 单个 profile 同步

**常见 bug：**
- 硬编码 source 过滤：`listHermesSessionSummaries('api_server', ...)`
- 应改为：`listHermesSessionSummaries(undefined, ...)` 同步所有来源

### 会话查询逻辑

**文件：** `packages/server/src/db/hermes/sessions-db.ts`

**关键函数：**
- `listSessionSummaries(source, limit, profile)` - 列出会话摘要
- `getSessionDetailFromDbWithProfile(sessionId, profile)` - 获取完整会话

**SQL 查询要点：**
- 过滤条件：`s.source != 'tool'`、`s.parent_session_id IS NULL`
- 排序：按 `last_active` 降序

## 数据验证清单

修复后必须验证以下指标：

```bash
# 1. 检查会话数量
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "SELECT COUNT(*) FROM sessions; SELECT COUNT(*) FROM messages;"

# 2. 检查来源分布（修复后应保留真实来源）
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "SELECT source, COUNT(*) as count FROM sessions GROUP BY source ORDER BY count DESC;"

# 3. 与源数据库对比（数量应接近）
sqlite3 ~/.hermes/state.db "SELECT COUNT(*) FROM sessions WHERE source != 'tool';"

# 4. 检查最新会话是否有正确的来源
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "SELECT id, title, source FROM sessions ORDER BY last_active DESC LIMIT 5;"
```

**预期结果：**
- 会话来源应该包含 `cli`、`telegram`、`weixin`、`feishu`、`cron` 等（而不是全部 `api_server`）
- 会话总数应与源数据库接近（允许有小幅差异）
- 消息数量应为会话数量的数倍

## 数据重新同步流程

如果 Web UI 数据库损坏或需要完全重新同步：

```bash
# 1. 停止 Web UI
hermes-web-ui stop

# 2. 备份现有数据库（可选）
cp ~/.hermes-web-ui/hermes-web-ui.db ~/.hermes-web-ui/hermes-web-ui.db.backup

# 3. 清空数据
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "DELETE FROM sessions; DELETE FROM messages; DELETE FROM session_usage;"

# 4. 启动 Web UI（自动触发同步）
hermes-web-ui start

# 5. 等待同步完成（约 5-10 秒）
sleep 10

# 6. 验证结果
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "SELECT source, COUNT(*) FROM sessions GROUP BY source;"
```

**注意：** Web UI 只在 `sessions` 表为空时自动同步。如果需要增量同步，需要修改同步逻辑。

## 调试技巧

### 1. 查看详细日志

```bash
# 实时日志
tail -f ~/.hermes-web-ui/server.log

# 只看同步相关
tail -f ~/.hermes-web-ui/server.log | grep -i "sync\\|session"
```

### 2. 手动触发同步

Web UI 只在数据库为空时自动同步。如果需要重新同步：

```bash
# 清空本地数据库
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "DELETE FROM sessions; DELETE FROM messages;"

# 重启 Web UI
hermes-web-ui restart
```

### 3. 数据库直接查询

```bash
# 检查数据完整性
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "
  SELECT 
    (SELECT COUNT(*) FROM sessions) as sessions,
    (SELECT COUNT(*) FROM messages) as messages;
"

# 查看会话来源分布
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "
  SELECT source, COUNT(*) FROM sessions GROUP BY source;
"
```

## 向上游贡献

发现 bug 后应该：

### 快速修复流程（推荐）

**完整案例参考：** `references/session-sync-fix.md`

1. **确认问题：**
   - 检查源数据库 vs Web UI 数据库
   - 确认是代码 bug 而非配置问题

2. **运行时补丁验证：**
```bash
# 先用 sed 修改打包后的代码验证修复有效
FILE=~/.nvm/versions/node/*/lib/node_modules/hermes-web-ui/dist/server/index.js
cp "$FILE" "${FILE}.backup"
sed -i '' 's/old-pattern/new-pattern/g' "$FILE"
hermes-web-ui restart

# 验证修复效果后再提交 PR
```

3. **克隆仓库并修复源码：**
```bash
cd /tmp
git clone --depth 1 https://github.com/EKKOLearnAI/hermes-web-ui.git
cd hermes-web-ui

# 定位源码
grep -rn "problematic-pattern" packages/server/src/

# 创建分支
git checkout -b fix/descriptive-name

# 修复源码
vim packages/server/src/path/to/file.ts

# 提交
git add -A
git commit -m "fix: clear description of the problem and solution"
```

4. **提交 PR：**
```bash
# Fork 仓库（如果还没有）
gh repo fork EKKOLearnAI/hermes-web-ui --clone=false

# 推送到 fork
git remote add myfork https://github.com/<your-username>/hermes-web-ui.git
git push myfork fix/descriptive-name -u

# 创建 PR
gh pr create --repo EKKOLearnAI/hermes-web-ui \
  --title "fix: clear title" \
  --body "## Problem
Describe the problem clearly

## Root Cause
Explain what's wrong in the code

## Solution
Show the fix with code diff

## Testing
Show before/after data or screenshots

## Impact
Explain what this fixes for users"
```

### PR 最佳实践

**标题格式：** `fix: brief description` / `feat: brief description`

**正文结构：**
1. **Problem** - 用户遇到的症状
2. **Root Cause** - 代码层面的问题
3. **Solution** - 修复方案和代码变更
4. **Testing** - 修复前后的数据对比或截图
5. **Impact** - 对用户的影响

**示例：** https://github.com/EKKOLearnAI/hermes-web-ui/pull/369

## 参考文件

- **`references/session-sync-fix.md`** - v0.5.4 会话同步过滤 bug 和定时任务认证问题的完整修复案例，包括根本原因分析、诊断流程、修复步骤和数据验证。涵盖：
  - 会话同步过滤问题（硬编码 `source='api_server'`）
  - 定时任务认证问题（缺少 `~/.hermes/.env` 文件）
  - 运行时补丁方案和源码修复
  - 完整诊断路径示例
- **`scripts/diagnose.sh`** - 快速诊断脚本，检查服务状态、数据库、认证和常见问题

## 相关资源

- **官方仓库：** https://github.com/EKKOLearnAI/hermes-web-ui
- **Hermes Agent：** https://github.com/NousResearch/hermes-agent
- **Node SQLite 要求：** Node.js >= 22.5.0
- **日志文件：** `~/.hermes-web-ui/logs/server.log`（详细日志）
- **服务日志：** `~/.hermes-web-ui/server.log`（启动日志）
