# 环境变量配置丢失排查流程

## 问题现象

保守式更新后，发现消息平台（Telegram、企业微信、飞书、QQ Bot 等）无法连接，检查 `.env` 文件发现配置丢失。

## 排查步骤

### 1. 确认配置丢失时间点

```bash
# 检查 .env 文件修改时间
ls -la ~/.hermes/.env

# 查看文件内容
cat ~/.hermes/.env

# 统计环境变量数量
grep -E "^[A-Z_]+=" ~/.hermes/.env | wc -l
```

### 2. 查找备份文件

```bash
# 查找所有 .env 备份
find ~/.hermes -name "*.env*" -o -name "env-backup*" 2>/dev/null

# 查找 patch 备份目录
ls -lh ~/.hermes/patch-backups/

# 检查是否有 env 备份
ls -lh ~/.hermes/patch-backups/env-backup-*.env 2>/dev/null
```

### 3. 从会话记录重建历史

```bash
# 查询历史配置（需要知道大概时间范围）
cd ~/.hermes

# 查看特定时间点的平台状态
sqlite3 state.db "
SELECT datetime(timestamp, 'unixepoch', 'localtime'), substr(content, 1, 200)
FROM messages 
WHERE role='tool' 
  AND content LIKE '%Available messaging targets%'
  AND datetime(timestamp, 'unixepoch', 'localtime') BETWEEN '2026-04-20' AND '2026-04-30'
ORDER BY timestamp DESC
LIMIT 5;
"

# 查看平台连接历史
sqlite3 state.db "
SELECT datetime(timestamp, 'unixepoch', 'localtime'), substr(content, 1, 150)
FROM messages
WHERE role='assistant'
  AND (content LIKE '%Telegram%' OR content LIKE '%飞书%' OR content LIKE '%企业微信%')
  AND datetime(timestamp, 'unixepoch', 'localtime') BETWEEN '2026-04-20' AND '2026-05-01'
ORDER BY timestamp DESC
LIMIT 10;
"
```

### 4. 检查 Git 操作历史

```bash
cd ~/.hermes/hermes-agent

# 查看 Git 操作历史
git reflog --all | head -30

# 查看特定时间段的提交
git log --oneline --since="2026-04-28" --until="2026-05-02"

# 检查 .gitignore 是否包含 .env
cat ~/.hermes/.gitignore | grep -E "env|\.env"
```

### 5. 恢复配置

#### 方案 A：从备份恢复

```bash
# 找到最新的备份
LATEST_BACKUP=$(ls -t ~/.hermes/patch-backups/env-backup-*.env | head -1)

# 恢复配置
cp "$LATEST_BACKUP" ~/.hermes/.env

# 验证
grep -E "^[A-Z_]+=" ~/.hermes/.env | wc -l
```

#### 方案 B：重新配置

由于 Token 等敏感信息不会存储在日志中，如果备份不存在，只能重新获取：

**Telegram**:
1. 打开 Telegram → @BotFather
2. 发送 `/mybots` 查看已有的 Bot
3. 选择 Bot → API Token 查看 Token
4. 添加到 `.env`: `TELEGRAM_BOT_TOKEN=your_token`

**企业微信**:
1. 登录企业微信管理后台 → 应用管理
2. 获取 AgentId, Secret, CorpId
3. 添加到 `.env`

**飞书**:
1. 登录飞书开放平台 → 应用详情 → 凭证与基础信息
2. 获取 App ID, App Secret
3. 添加到 `.env`

**QQ Bot**:
1. 登录 QQ 开放平台 → 机器人管理
2. 获取 Bot AppID, Bot Token
3. 添加到 `.env`

### 6. 验证恢复结果

```bash
# 重启 Gateway
hermes gateway restart

# 检查平台状态
hermes gateway status

# 查看日志
tail -50 ~/.hermes/logs/gateway.log | grep -E "Telegram|Feishu|Wecom|QQBot"

# 测试发送消息（使用 send_message list）
```

## 预防措施

### 1. 在保守式更新前自动备份

```bash
# 添加到 ~/.hermes/safe-update.sh 或在更新前手动执行
timestamp=$(date +%Y%m%d_%H%M%S)
cp ~/.hermes/.env ~/.hermes/patch-backups/env-backup-$timestamp.env
echo "✅ .env 已备份"
```

### 2. 定期备份环境变量

```bash
# 创建每日备份 cron 任务
# crontab -e
# 0 0 * * * cp ~/.hermes/.env ~/.hermes/patch-backups/env-daily-$(date +\%Y\%m\%d).env
```

### 3. 使用密钥管理工具

将 Token 存储在：
- 1Password
- iCloud Keychain
- 其他密码管理器

需要时从密钥管理器复制到 `.env`。

## 常见原因

| 原因 | 表现 | 解决方案 |
|------|------|---------|
| **更新脚本误删** | 更新后 .env 为空 | 在脚本中添加 .env 备份步骤 |
| **手动操作失误** | 记得编辑过 .env | 建立备份习惯 |
| **工具重写配置** | 只有部分平台配置 | 更新前完整备份 .env |
| **Git 操作覆盖** | .env 被 Git 管理 | 确保 .env 在 .gitignore 中 |

## 案例：2026-05-01 配置丢失事件

**时间线**:
- 4月30日 11:21: 5个平台正常运行（Telegram, 飞书, 企业微信, QQ, 微信）
- 5月1日 21:00-22:35: 保守式更新操作
- 5月1日 22:35: 发现微信不工作，.env 被清空
- 5月1日 22:41: 重新扫码配置微信（其他平台未恢复）

**根本原因**: `.env` 文件在保守式更新期间被清空或覆盖，且没有备份机制。

**教训**: 
1. **必须**在保守式更新前备份 `.env` 文件
2. 更新后立即验证环境变量数量和平台配置
3. 建立定期备份机制

## 相关文档

- [Dashboard 启动指南](dashboard-startup-guide.md)
- [保守式更新主流程](../SKILL.md#phase-15-保守式更新完整流程)
