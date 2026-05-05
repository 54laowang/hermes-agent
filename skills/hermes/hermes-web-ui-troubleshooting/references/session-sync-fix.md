# 会话同步过滤 Bug 修复案例

## 问题描述

**症状：** Hermes Web UI v0.5.4 更新后会话记录和定时任务不显示

**影响版本：** v0.5.0 - v0.5.4

**发现时间：** 2026-05-01

## 问题一：会话记录不显示

### 根本原因

**源码位置：** `packages/server/src/services/hermes/session-sync.ts:59`

```typescript
// 错误代码 - 硬编码只同步 api_server 来源
const summaries = await listHermesSessionSummaries('api_server', 10000, profile)
```

**问题分析：**

1. Hermes Agent 的会话来源多样：
   - `cli` - 命令行会话（186 个）
   - `telegram` - Telegram 平台（23 个）
   - `weixin` - 微信平台（107 个）
   - `feishu` - 飞书平台（24 个）
   - `cron` - 定时任务（262 个）
   - `qqbot`、`wecom` 等

2. **没有 `api_server` 来源的会话**，因为 `api_server` 只是一个 API 端点，不是会话来源

3. Web UI 同步逻辑错误地假设主要会话来自 `api_server`，导致所有实际会话被过滤掉

### 修复方案

**文件：** `packages/server/src/services/hermes/session-sync.ts`

```diff
- const summaries = await listHermesSessionSummaries('api_server', 10000, profile)
+ const summaries = await listHermesSessionSummaries(undefined, 10000, profile)
```

**原因：** 传递 `undefined` 移除 source 过滤，同步所有来源的会话

## 问题二：定时任务不显示

### 症状

会话列表正常，但定时任务列表为空或 API 返回 `Invalid API key`

### 根本原因

**源码位置：** `packages/server/src/services/hermes/gateway-manager.ts:127`

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

**问题分析：**

1. Web UI 的 jobs API 是代理到 Hermes Gateway 的 `/api/jobs` 端点
2. 代理请求需要 Hermes Gateway 的 API key 认证
3. `getApiKey()` 从 `~/.hermes/.env` 文件读取 `API_SERVER_KEY`
4. 对于 `default` profile，`profileDir('default')` 返回 `~/.hermes`（不是 `~/.hermes/profiles/default`）
5. 用户配置在 `~/.hermes/config.yaml` 的 `platforms.api_server.key` 字段，但 Web UI 不会读取这个位置

### 修复方案

**创建 `~/.hermes/.env` 文件：**

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

### 验证

```bash
# 检查定时任务数量
curl -H "Authorization: Bearer <web-ui-token>" \
  http://127.0.0.1:8648/api/hermes/jobs | jq '.jobs | length'

# 应该返回实际任务数量（如 6）
```

### 架构说明

```
Web UI Jobs API 流程：

浏览器 → Web UI (8648) → Gateway Manager → ~/.hermes/.env → API_SERVER_KEY
                                ↓
                           Hermes Gateway (8642) → /api/jobs → 定时任务数据
```

**关键点：**
- Web UI 不直接存储定时任务数据
- 定时任务数据在 Hermes Agent 的内存和 `~/.hermes/state.db` 中
- Web UI 只是一个代理层，需要正确配置认证才能访问 Hermes Gateway API

## 诊断流程

### 步骤 1：确认会话问题

```bash
# 检查源数据库是否有数据
sqlite3 ~/.hermes/state.db "SELECT source, COUNT(*) FROM sessions GROUP BY source;"

# 输出示例：
# cli|186
# cron|262
# feishu|24
# qqbot|2
# telegram|23
# wecom|2
# weixin|107

# 检查 Web UI 数据库
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "SELECT COUNT(*) FROM sessions;"

# 输出：0（问题确认）
```

### 步骤 2：确认定时任务问题

```bash
# 检查 Hermes Agent 是否有定时任务
hermes cron list

# 直接测试 Hermes Gateway API
curl -H "Authorization: Bearer <hermes-api-key>" \
  http://127.0.0.1:8642/api/jobs | jq '.jobs | length'

# 输出：6（Gateway 有数据）

# 测试 Web UI 代理
curl -H "Authorization: Bearer <web-ui-token>" \
  http://127.0.0.1:8648/api/hermes/jobs

# 输出：{"error":{"message":"Invalid API key"}}（问题确认）
```

### 步骤 3：检查配置文件

```bash
# 检查 .env 文件是否存在
ls -la ~/.hermes/.env

# 输出：No such file or directory（问题确认）

# 检查 config.yaml 中的 API key
grep -A 5 "api_server:" ~/.hermes/config.yaml

# 输出：
# api_server:
#   cors_origins: '*'
#   enabled: true
#   extra:
#     host: 127.0.0.1
#     key: SV1a9QQO4kPAzHs-Ki-VbUvQJGf4uFZVqC7cBS8AheM
```

### 步骤 4：应用修复

```bash
# 1. 修复会话同步（修改源码或运行时补丁）
# 详见上文

# 2. 修复定时任务认证
API_KEY=$(grep -A 5 "api_server:" ~/.hermes/config.yaml | grep "key:" | awk '{print $2}')
cat > ~/.hermes/.env << EOF
API_SERVER_KEY="$API_KEY"
EOF

# 3. 清空数据库重新同步
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "DELETE FROM sessions; DELETE FROM messages;"

# 4. 重启 Web UI
hermes-web-ui restart

# 5. 等待同步完成
sleep 5
```

### 步骤 5：验证结果

```bash
# 验证会话
sqlite3 ~/.hermes-web-ui/hermes-web-ui.db "
  SELECT source, COUNT(*) as count 
  FROM sessions 
  GROUP BY source 
  ORDER BY count DESC;
"

# 输出示例：
# cron|263
# cli|71
# weixin|39
# telegram|12
# feishu|12
# wecom|2
# qqbot|2

# 验证定时任务
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8648/api/hermes/jobs | jq '.jobs | length'

# 输出：6 ✓
```

## 运行时补丁（临时方案）

如果无法重新构建，可以修改打包后的代码：

```bash
FILE=~/.nvm/versions/node/v25.9.0/lib/node_modules/hermes-web-ui/dist/server/index.js

# 备份
cp "$FILE" "${FILE}.backup"

# Python 脚本应用多处修改
python3 << 'PYTHON_SCRIPT'
import re

file_path = "$FILE"
with open(file_path, 'r') as f:
    content = f.read()

# 1. 修复会话同步过滤
content = re.sub(
    r'await GW\("api_server",',
    'await GW(undefined,',
    content
)

# 2. 修复 createSession 的 source 参数
content = re.sub(
    r'source:\s*"api_server"',
    'source: e.source || "api_server"',
    content
)

with open(file_path, 'w') as f:
    f.write(content)

print("Patch applied successfully")
PYTHON_SCRIPT

# 重启服务
hermes-web-ui restart
```

**注意：** 这是临时方案，每次更新 Web UI 都会覆盖修改。应该向官方仓库提交 PR。

## 相关代码

### session-sync.ts

**文件：** `packages/server/src/services/hermes/session-sync.ts`

```typescript
export async function syncProfileSessions(profile: string): Promise<void> {
  // 修复前：只同步 api_server 来源
  // const summaries = await listHermesSessionSummaries('api_server', 10000, profile)
  
  // 修复后：同步所有来源
  const summaries = await listHermesSessionSummaries(undefined, 10000, profile)
  
  for (const summary of summaries) {
    // ...
    const sessionId = await createSession(
      {
        id: hermesSession.id,
        source: hermesSession.source,  // 保留原始来源
        // ...
      },
      profile,
      hermesSession.source  // 显式传递来源
    )
    // ...
  }
}
```

### session-store.ts

**文件：** `packages/server/src/db/hermes/session-store.ts`

```typescript
// 修复前：硬编码默认值
export async function createSession(
  data: CreateSessionData,
  profile: string = 'default'
): Promise<string> {
  // source 默认 'api_server'，覆盖真实来源
}

// 修复后：保留真实来源
interface CreateSessionData {
  id: string
  model?: string
  title?: string
  source?: string  // 添加可选参数
  started_at: number
  ended_at?: number
  last_active: number
}

export async function createSession(
  data: CreateSessionData,
  profile: string = 'default'
): Promise<string> {
  const stmt = db.prepare(`
    INSERT INTO sessions (id, profile, source, model, title, started_at, ended_at, last_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `)
  
  stmt.run(
    data.id,
    profile,
    data.source || 'api_server',  // 使用传入的 source，回退到 'api_server'
    data.model || '',
    data.title || '',
    data.started_at,
    data.ended_at,
    data.last_active
  )
  
  return data.id
}
```

### gateway-manager.ts

**文件：** `packages/server/src/services/hermes/gateway-manager.ts`

```typescript
class GatewayManager {
  // 读取 profile 的 API_SERVER_KEY
  getApiKey(profileName?: string): string | null {
    const name = profileName || this.activeProfile
    try {
      const envPath = join(this.profileDir(name), '.env')
      if (!existsSync(envPath)) return null
      const content = readFileSync(envPath, 'utf-8')
      const match = content.match(/^API_SERVER_KEY\s*=\s*"?([^"\n]+)"?/m)
      return match?.[1]?.trim() || null
    } catch {
      return null
    }
  }
  
  // 对于 default profile，返回 ~/.hermes
  private profileDir(name: string): string {
    if (name === 'default') return HERMES_BASE  // ~/.hermes
    return join(HERMES_BASE, 'profiles', name)
  }
}
```

**问题：** 只从 `.env` 文件读取，不从 `config.yaml` 读取，导致配置不匹配。

**建议改进：**

```typescript
getApiKey(profileName?: string): string | null {
  const name = profileName || this.activeProfile
  
  // 1. 先尝试从 .env 读取（优先级高）
  const envPath = join(this.profileDir(name), '.env')
  if (existsSync(envPath)) {
    const content = readFileSync(envPath, 'utf-8')
    const match = content.match(/^API_SERVER_KEY\s*=\s*"?([^"\n]+)"?/m)
    if (match?.[1]?.trim()) return match[1].trim()
  }
  
  // 2. 回退到 config.yaml（兼容旧配置）
  const configPath = join(this.profileDir(name), 'config.yaml')
  if (existsSync(configPath)) {
    try {
      const content = readFileSync(configPath, 'utf-8')
      const cfg = yaml.load(content) as any
      const key = cfg?.platforms?.api_server?.extra?.key
      if (key) return key
    } catch {}
  }
  
  return null
}
```

### jobs.ts（代理层）

**文件：** `packages/server/src/controllers/hermes/jobs.ts`

```typescript
export async function list(ctx: Context) {
  await proxyRequest(ctx, '/api/jobs')
}

async function proxyRequest(ctx: Context, upstreamPath: string, method?: string): Promise<void> {
  const profile = resolveProfile(ctx)
  const upstream = getUpstream(profile)  // http://127.0.0.1:8642
  const headers = buildHeaders(profile)  // 包含 Authorization: Bearer <API_SERVER_KEY>
  
  const url = `${upstream}${upstreamPath}`  // http://127.0.0.1:8642/api/jobs
  
  const res = await fetch(url, { headers, ... })
  ctx.body = await res.json()
}
```

**关键点：** `buildHeaders()` 调用 `getApiKey()`，如果返回 null，请求就缺少认证头。

## 上游贡献

**PR 已提交：** https://github.com/EKKOLearnAI/hermes-web-ui/pull/369

**修复内容：**
1. 移除硬编码的 source 过滤，同步所有来源的会话
2. 修改 `createSession` 接受并使用传入的 source 参数
3. Web UI 已有完整的会话来源显示功能：
   - 会话按来源分组（可折叠/展开）
   - 每个来源有对应的标签（CLI、Telegram、WeChat 等）
   - 来源徽章显示在会话标题旁
   - 来源排序：`api_server` 优先，`cron` 最后，其他按字母排序

**未包含在 PR 中的改进：**
- `getApiKey()` 应该回退读取 `config.yaml`（需要单独 PR）

## 完整诊断路径示例

**用户报告：** "更新版本后不显示会话记录和定时任务"

```
诊断流程：

1. 检查服务状态
   ├─ curl http://127.0.0.1:8642/health ✓ (Gateway 正常)
   ├─ curl http://127.0.0.1:8648/ ✓ (Web UI 正常)
   └─ 确认两个服务都在运行

2. 检查会话数据
   ├─ 源数据库：605 个会话 ✓
   ├─ Web UI 数据库：0 个会话 ✗
   └─ 问题确认：会话同步失败

3. 检查定时任务数据
   ├─ hermes cron list：6 个任务 ✓
   ├─ Gateway API：返回 6 个任务 ✓
   ├─ Web UI API：Invalid API key ✗
   └─ 问题确认：认证配置缺失

4. 定位会话同步问题
   ├─ 搜索 "api_server" 过滤
   ├─ 发现硬编码 source='api_server'
   ├─ 验证会话来源：cli/telegram/weixin 等
   └─ 确认根因：过滤条件错误

5. 定位定时任务认证问题
   ├─ 检查 jobs 控制器：代理到 Gateway
   ├─ 检查 getApiKey()：从 .env 读取
   ├─ 检查 .env 文件：不存在 ✗
   └─ 确认根因：缺少 .env 配置文件

6. 应用修复
   ├─ 会话同步：修改源码 'api_server' → undefined
   ├─ 定时任务：创建 ~/.hermes/.env 文件
   ├─ 清空数据库重新同步
   └─ 重启服务

7. 验证结果
   ├─ 会话：401 个，来源分布正确 ✓
   ├─ 消息：15,198 条 ✓
   └─ 定时任务：6 个 ✓

8. 提交 PR
   ├─ Fork 仓库
   ├─ 创建分支 fix/sync-all-session-sources
   ├─ 推送并创建 PR #369
   └─ 详细说明问题和修复方案
```

## 参考资料

- **问题发现会话：** 2026-05-01 10:00-10:45
- **修复 PR：** https://github.com/EKKOLearnAI/hermes-web-ui/pull/369
- **涉及版本：** hermes-web-ui v0.5.4
- **相关文件：**
  - `packages/server/src/services/hermes/session-sync.ts` - 同步逻辑
  - `packages/server/src/db/hermes/sessions-db.ts` - 查询逻辑
  - `packages/server/src/db/hermes/session-store.ts` - 存储逻辑
  - `packages/server/src/services/hermes/gateway-manager.ts` - 认证配置
  - `packages/server/src/controllers/hermes/jobs.ts` - 定时任务代理
  - `packages/client/src/shared/session-display.ts` - 来源标签
  - `packages/client/src/components/hermes/chat/ChatPanel.vue` - 分组显示
