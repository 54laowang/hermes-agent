# .env 配置备份与恢复系统

## 背景

在保守式更新 Hermes Fork 仓库时，`.env` 配置文件可能会意外丢失。本文档记录了完整的备份恢复机制。

## 问题发生时间线

- **2026-04-30 11:21** - 用户最后确认 5 个平台正常运行（Telegram、飞书、企业微信、QQ Bot、元宝）
- **2026-05-01 21:00-22:35** - 保守式更新期间，`.env` 文件被清空
- **2026-05-02 09:33** - 发现配置丢失，用户重新配置所有平台

## 根本原因

保守式更新期间（rebase 操作），`.env` 文件可能因为以下原因被清空：

1. **Git 操作误删** - rebase 过程中可能触发了文件重置
2. **未跟踪状态** - `.env` 在 `.gitignore` 中，Git 不会保护变更
3. **缺乏备份机制** - 更新前没有专门备份 `.env` 文件

## 建立的备份机制

### 三层备份策略

| 备份类型 | 触发时机 | 位置 | 保留期限 |
|---------|---------|------|---------|
| **定时备份** | 每天凌晨 2:00 | `~/.hermes/env-backups/env-YYYYMMDD_HHMMSS.bak` | 30 天 |
| **更新前备份** | 每次保守式更新前 | `~/.hermes/patch-backups/env-backup-YYYYMMDD_HHMMSS.env` | 永久 |
| **手动备份** | 用户主动执行 | `~/.hermes/env-backups/env-YYYYMMDD_HHMMSS-manual.bak` | 永久 |

### 备份脚本

#### 1. 自动备份脚本

```bash
~/.hermes/scripts/backup-env.sh
```

功能：
- 自动备份 `.env` 文件
- 清理 30 天前的旧备份
- 显示备份文件信息

Cron Job 配置：
```
0 2 * * * /Users/me/.hermes/scripts/backup-env.sh >> ~/.hermes/logs/env-backup.log 2>&1
```

#### 2. 手动备份脚本

```bash
~/.hermes/scripts/backup-env-now.sh [备注]
```

用法：
```bash
# 立即备份（带备注）
~/.hermes/scripts/backup-env-now.sh "配置完成所有平台"

# 查看备份列表
ls -lt ~/.hermes/env-backups/
```

#### 3. 一键恢复脚本

```bash
~/.hermes/scripts/restore-env.sh
```

功能：
- 显示最近 10 个备份
- 交互式选择恢复
- 自动备份当前 `.env`（如果存在）

## 恢复流程

### 场景 1: 自动备份恢复

```bash
# 1. 查看备份列表
ls -lt ~/.hermes/env-backups/

# 2. 选择最近的备份
cp ~/.hermes/env-backups/env-20260502_020000.bak ~/.hermes/.env

# 3. 重启 Gateway
hermes gateway restart
```

### 场景 2: 交互式恢复

```bash
# 运行恢复脚本
~/.hermes/scripts/restore-env.sh

# 按提示选择备份编号
# 确认恢复
# 重启 Gateway
```

### 场景 3: 无备份时的恢复

如果没有任何备份，需要重新配置所有平台：

1. **Telegram Bot**
   - 访问 [@BotFather](https://t.me/botfather)
   - 创建新 Bot 或查看现有 Token

2. **企业微信 (WeCom)**
   - 访问企业微信管理后台
   - 应用管理 → 查看 Secret

3. **飞书 (Feishu)**
   - 访问飞书开放平台
   - 应用详情 → App ID 和 App Secret

4. **QQ Bot**
   - 访问 QQ 开放平台
   - Bot 管理 → 查看 Token

5. **微信频道 (Weixin)**
   - 扫码登录获取 Cookie

## 预防措施

### 1. 保守式更新前手动备份

```bash
# 更新前立即备份
~/.hermes/scripts/backup-env-now.sh "更新前备份"

# 然后执行更新
git pull --rebase origin main
```

### 2. 定期检查备份状态

```bash
# 检查备份目录
ls -lh ~/.hermes/env-backups/

# 检查最新备份时间
ls -lt ~/.hermes/env-backups/ | head -2

# 验证备份文件内容
head -20 ~/.hermes/env-backups/env-*.bak
```

### 3. 监控 Cron Job 状态

```bash
# 检查 Cron Job 是否运行
crontab -l | grep backup-env

# 查看备份日志
tail -20 ~/.hermes/logs/env-backup.log
```

## 配置项清单

| 配置项 | 说明 | 重要性 |
|-------|------|-------|
| `API_SERVER_KEY` | Dashboard API 密钥 | 🔴 高 |
| `WEIXIN_*` | 微信频道配置 | 🔴 高 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot | 🟡 中 |
| `FEISHU_*` | 飞书配置 | 🟡 中 |
| `WECOM_*` | 企业微信配置 | 🟡 中 |
| `QQBOT_*` | QQ Bot 配置 | 🟡 中 |
| `YUANBAO_*` | 元宝配置 | 🟡 中 |

## 最佳实践

1. ✅ **每次配置变更后手动备份** - `~/.hermes/scripts/backup-env-now.sh "说明"`
2. ✅ **更新前验证备份存在** - `ls ~/.hermes/env-backups/`
3. ✅ **定期检查 Cron Job** - `crontab -l`
4. ✅ **重要配置多重备份** - 同时保存到云盘或本地其他位置
5. ✅ **记录配置来源** - 每个平台的 Token/Secret 获取路径

## 相关文件

- 备份脚本: `~/.hermes/scripts/backup-env.sh`
- 手动备份: `~/.hermes/scripts/backup-env-now.sh`
- 恢复脚本: `~/.hermes/scripts/restore-env.sh`
- 备份目录: `~/.hermes/env-backups/`
- Skill 文档: `~/.hermes/skills/autonomous-ai-agents/hermes-local-mod-protection-safe-update/SKILL.md`

## 更新历史

- **2026-05-02** - 初版，建立三层备份机制
- **2026-05-02** - 添加 Cron Job（每天凌晨 2:00 自动备份）
