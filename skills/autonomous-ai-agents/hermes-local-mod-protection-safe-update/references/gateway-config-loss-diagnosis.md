# Gateway 配置丢失诊断指南

## 问题场景

用户报告："之前配置过 Telegram/QQ/企业微信/飞书，但现在配置找不到了"

## 诊断流程

### Phase 1: 确认配置状态

```bash
# 1. 检查当前 .env 文件
cd ~/.hermes
cat .env

# 2. 检查 config.yaml 中的 platforms 配置
grep -A 20 "^platforms:" config.yaml

# 3. 检查备份文件
ls -la *.backup *.bak 2>/dev/null
grep "telegram\|qqbot\|wecom\|feishu" *.backup *.bak
```

### Phase 2: 时间线追溯

**关键方法**：通过 SQLite 会话记录追溯配置丢失时间点

```bash
cd ~/.hermes

# 1. 查找最后一次使用某平台的记录
sqlite3 state.db "
SELECT datetime(timestamp, 'unixepoch', 'localtime'), substr(content, 1, 200)
FROM messages 
WHERE role='assistant' 
  AND content LIKE '%Telegram%正常%'
ORDER BY timestamp DESC 
LIMIT 5;"

# 2. 查找配置操作记录
sqlite3 state.db "
SELECT datetime(timestamp, 'unixepoch', 'localtime'), role, substr(content, 1, 150)
FROM messages 
WHERE datetime(timestamp, 'unixepoch', 'localtime') BETWEEN '2026-04-30 00:00:00' AND '2026-05-01 23:59:59'
  AND (content LIKE '%config%' OR content LIKE '%配置%' OR content LIKE '%platform%')
ORDER BY timestamp;"

# 3. 查找问题报告时间点
sqlite3 state.db "
SELECT datetime(timestamp, 'unixepoch', 'localtime'), role, substr(content, 1, 100)
FROM messages 
WHERE role='user' 
  AND (content LIKE '%不回复%' OR content LIKE '%不工作%' OR content LIKE '%找不到%')
ORDER BY timestamp DESC 
LIMIT 10;"
```

### Phase 3: 锁定丢失原因

**常见原因**：

| 原因 | 证据 | 解决方案 |
|------|------|---------|
| **保守式更新误操作** | `.env` 修改时间在 rebase 操作期间 | 从备份恢复或重新配置 |
| **手动重建配置** | `.env` 文件很小，只有部分配置 | 重新配置缺失平台 |
| **Git 操作误删** | `.env` 被 `git clean` 或 `git rm` 删除 | `.env` 应在 `.gitignore` 中 |
| **从未保存** | 备份文件中也没有相关配置 | 通过会话记录确认配置来源 |

### Phase 4: 验证假设

```bash
# 检查 .env 文件修改时间
ls -la ~/.hermes/.env
stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" ~/.hermes/.env

# 检查 .gitignore 是否包含 .env
cat ~/.hermes/.gitignore | grep -E "env|\.env"

# 检查 Git 历史（如果 .env 被误提交）
cd ~/.hermes
git log --all --oneline -- .env

# 检查是否有其他备份位置
find ~ -maxdepth 3 -name ".env*" 2>/dev/null | grep -v "venv\|node_modules\|cache"
```

## 实战案例：2026-05-02 配置丢失诊断

### 问题描述

用户报告："telegram，qq和企业微信，飞书我都配置过，为什么配置找不到了"

### 诊断过程

1. **当前状态确认**：
   - `.env` 只有 4 行配置（API_SERVER_KEY + 微信相关）
   - 修改时间：2026-05-01 22:35

2. **时间线追溯**：
   ```
   2026-04-30 11:21  ✅ 5个平台正常运行（会话记录显示）
   2026-05-01 21:00  开始保守式更新
   2026-05-01 22:35  发现微信不工作
   2026-05-01 22:41  重新扫码配置微信
   ```

3. **根本原因**：
   - 配置在 5月1日 21:00-22:35 之间丢失
   - 可能是保守式更新期间的某个操作导致
   - 但备份文件（4月23日、5月1日 21:22）中也没有这些配置
   - **结论**：这些平台的配置从未保存在当前的 `.env` 文件中

### 经验总结

1. **`.env` 文件不在 Git 管理中**：
   - `.gitignore` 包含 `.env*` 规则
   - Git 不会跟踪 `.env` 的变更
   - 无法通过 `git log` 追溯

2. **备份策略不足**：
   - 只有 `config.yaml` 有备份（`.bak`, `.backup`）
   - `.env` 没有自动备份机制
   - 建议：定期手动备份 `.env`

3. **会话记录是关键证据源**：
   - `state.db` 保存所有对话历史
   - 可以通过关键词搜索找到配置操作记录
   - 时间戳精确到秒，便于定位问题

## 预防措施

### 1. 定期备份 `.env` 文件

```bash
# 创建自动备份脚本
cat > ~/.hermes/hooks/pre-commit-backup-env.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/.hermes/env-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
cp "$HOME/.hermes/.env" "$BACKUP_DIR/.env.$TIMESTAMP"

# 只保留最近 30 个备份
cd "$BACKUP_DIR"
ls -t .env.* | tail -n +31 | xargs rm -f 2>/dev/null
EOF

chmod +x ~/.hermes/hooks/pre-commit-backup-env.sh
```

### 2. 配置验证脚本

```bash
# 检查关键平台配置
python3 << 'EOF'
import os
from pathlib import Path

env_file = Path.home() / ".hermes" / ".env"
required_vars = {
    "TELEGRAM_BOT_TOKEN": "Telegram",
    "WEIXIN_ACCOUNT_ID": "微信",
    "WECOM_BOT_KEY": "企业微信",
    "FEISHU_APP_ID": "飞书",
    "QQBOT_BOT_TOKEN": "QQ Bot"
}

if env_file.exists():
    content = env_file.read_text()
    print("=== 平台配置状态 ===\n")
    for var, platform in required_vars.items():
        status = "✅" if var in content else "❌"
        print(f"{status} {platform}: {var}")
else:
    print("❌ .env 文件不存在")
EOF
```

### 3. 会话记录审计

```bash
# 查找最近的配置操作
cd ~/.hermes
sqlite3 state.db "
SELECT datetime(timestamp, 'unixepoch', 'localtime'), substr(content, 1, 100)
FROM messages 
WHERE (content LIKE '%TELEGRAM%' OR content LIKE '%WECOM%' OR content LIKE '%FEISHU%')
  AND datetime(timestamp, 'unixepoch', 'localtime') > datetime('now', '-7 days')
ORDER BY timestamp DESC 
LIMIT 20;"
```

## 恢复配置流程

### 重新配置各平台

**Telegram**:
```bash
# 1. 找 @BotFather 创建/查看 Bot
# 2. 获取 Token
hermes config set platforms.telegram.enabled true
# 手动添加到 .env: TELEGRAM_BOT_TOKEN=your_token
```

**企业微信**:
```bash
# 1. 在企业微信管理后台创建应用
# 2. 获取 AgentId 和 Secret
# 手动添加到 .env:
# WECOM_BOT_KEY=your_key
# WECOM_API_BASE_URL=https://qyapi.weixin.qq.com
```

**飞书**:
```bash
# 1. 在飞书开放平台创建应用
# 2. 获取 App ID 和 App Secret
# 手动添加到 .env:
# FEISHU_APP_ID=your_app_id
# FEISHU_APP_SECRET=your_secret
```

**QQ Bot**:
```bash
# 1. 在 QQ 开放平台创建 Bot
# 2. 获取 AppId 和 Token
# 手动添加到 .env:
# QQBOT_BOT_APPID=your_appid
# QQBOT_BOT_TOKEN=your_token
```

### 配置后验证

```bash
# 重启 Gateway
hermes gateway restart

# 检查日志
tail -50 ~/.hermes/logs/gateway.log | grep -E "(Telegram|Wecom|Feishu|QQBot)"

# 预期看到：
# ✓ [Telegram] Connected
# ✓ [Wecom] Connected
# ✓ [Feishu] Connected
# ✓ [QQBot] Connected
```

## 相关文件

| 文件 | 说明 |
|------|------|
| `~/.hermes/.env` | 环境变量配置 |
| `~/.hermes/config.yaml` | 主配置文件 |
| `~/.hermes/state.db` | 会话记录数据库 |
| `~/.hermes/logs/gateway.log` | Gateway 日志 |
| `~/.hermes/.gitignore` | Git 忽略规则 |

## 参考链接

- Hermes Gateway 配置：https://hermes-agent.nousresearch.com/docs/gateway
- 平台适配器文档：`gateway/platforms/` 源码
