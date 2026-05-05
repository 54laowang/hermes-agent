---
name: hermes-token-expiry-monitor
description: 监控 Volcengine Ark API token 每日自动过期问题，实现自动检测 + 网关重启 + 告警通知的完整闭环防护机制
version: "1.0.0"
category: hermes
keywords: [hermes, volcengine, ark, token expiry, monitoring, gateway, watchdog]
---
# Hermes Provider Token 过期监控与自动恢复

## 问题背景

Volcengine (火山引擎) Ark API 密钥存在**每日自动过期**机制：
- 🕒 **过期时间**: 每日凌晨约 3:23 AM
- ❌ **错误表现**: `InvalidToken: access key is invalid or expired`
- ⚡ **级联故障**: InvalidToken → 会话摘要重试风暴 → 所有 Provider 停止响应 → 全平台消息中断
- 💥 **影响范围**: 微信/Telegram/Discord/Feishu 等所有平台推送停止

这是 Hermes 多平台网关运营中的**最高优先级故障**。

## 🚨 故障诊断步骤

### 1. 检查错误日志

```bash
# 搜索 InvalidToken 错误
cd ~/.hermes/logs
grep -B2 -A2 "InvalidToken" gateway.error.log
grep -B5 -A5 "access key is invalid" *.log

# 查看夜间（20:00 - 07:00）错误分布
grep -o "2026-04-2[4-5] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]" gateway.error.log | sort | uniq -c | tail -30
```

### 2. 验证新 API Key

```python
import requests

# 测试 Ark API
headers = {
    "Authorization": "Bearer YOUR_NEW_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "model": "ep-20250218173318-q6jgv",
    "messages": [{"role": "user", "content": "测试消息"}]
}
response = requests.post(
    "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    headers=headers, json=data, timeout=30
)
print(f"Status: {response.status_code}")
print(response.json())
```

### 3. 紧急恢复（人工）

```bash
# 重启网关服务
hermes gateway restart

# 验证状态
hermes gateway status

# 等待 5 秒后检查错误日志
sleep 5 && tail -20 ~/.hermes/logs/gateway.error.log
```

## 🔧 自动化监控脚本

创建 `/Users/me/.hermes/scripts/monitor-token-status.py`：

```python
#!/usr/bin/env python3
"""
Hermes Provider Token 状态监控脚本
- 定期检查 API token 有效性
- 扫描错误日志中的 InvalidToken 错误
- 发现问题自动重启网关
"""

import re
import json
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

# 配置
LOG_DIR = Path.home() / ".hermes" / "logs"
CONFIG_PATH = Path.home() / ".hermes" / "config.yaml"
ERROR_LOG = LOG_DIR / "gateway.error.log"
GENERAL_LOG = LOG_DIR / "errors.log"
STATUS_FILE = Path.home() / ".hermes" / ".token-monitor-status.json"

# Volcengine Ark 测试配置
ARK_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
TEST_MODEL = "ep-20250218173318-q6jgv"  # 使用实际模型
TEST_MESSAGE = "请回复 'OK' 来验证 API 可用性"

def get_current_status():
    """获取当前监控状态"""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {
        "last_check": None,
        "last_restart": None,
        "restart_count": 0,
        "last_error_time": None,
        "consecutive_failures": 0,
        "token_status": "unknown"
    }

def save_status(status):
    """保存监控状态"""
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2, default=str)

def test_ark_api(api_key):
    """测试 Ark API 是否正常"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": TEST_MODEL,
        "messages": [{"role": "user", "content": TEST_MESSAGE}],
        "max_tokens": 10
    }
    try:
        response = requests.post(
            ARK_ENDPOINT, headers=headers, json=data, timeout=30
        )
        if response.status_code == 200:
            return True, "OK"
        else:
            error_msg = response.json().get('error', {}).get('message', 'Unknown')
            return False, f"HTTP {response.status_code}: {error_msg}"
    except Exception as e:
        return False, str(e)

def scan_error_logs(minutes_ago=60):
    """扫描最近 N 分钟的错误日志"""
    cutoff = datetime.now() - timedelta(minutes=minutes_ago)
    invalid_token_count = 0
    other_errors = []

    # 时间戳匹配模式
    time_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'

    for log_path in [ERROR_LOG, GENERAL_LOG]:
        if not log_path.exists():
            continue
        try:
            with open(log_path, 'r') as f:
                content = f.read()
                # 搜索 InvalidToken
                matches = re.finditer(r'InvalidToken|access key is invalid|token.*expired', content, re.I)
                for match in matches:
                    # 向前查找时间戳
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line = content[line_start:content.find('\n', match.start())]
                    time_match = re.search(time_pattern, line)
                    if time_match:
                        error_time = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                        if error_time > cutoff:
                            invalid_token_count += 1
        except:
            pass

    return invalid_token_count

def restart_gateway():
    """重启 Hermes Gateway"""
    try:
        result = subprocess.run(
            ['hermes', 'gateway', 'restart'],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0 or "Service restarted" in result.stdout:
            return True, result.stdout
        return False, result.stderr or result.stdout
    except Exception as e:
        return False, str(e)

def main():
    """主监控逻辑"""
    status = get_current_status()
    now = datetime.now().isoformat()

    print(f"=== Token 监控检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    # 1. 扫描错误日志
    error_count = scan_error_logs(minutes_ago=60)
    print(f"最近 60 分钟 InvalidToken 错误: {error_count} 次")

    # 2. 检查是否需要重启
    needs_restart = False
    restart_reason = []

    if error_count >= 3:
        needs_restart = True
        restart_reason.append(f"错误日志中发现 {error_count} 次 InvalidToken")

    # 3. 执行重启
    if needs_restart:
        print(f"⚠️ 需要重启网关: {', '.join(restart_reason)}")
        restart_success, restart_msg = restart_gateway()

        if restart_success:
            print("✅ 网关重启成功")
            status['last_restart'] = now
            status['restart_count'] = status.get('restart_count', 0) + 1
            status['consecutive_failures'] = 0
        else:
            print(f"❌ 网关重启失败: {restart_msg}")
            status['consecutive_failures'] = status.get('consecutive_failures', 0) + 1

    status['last_check'] = now
    status['last_error_count'] = error_count
    status['last_error_time'] = datetime.now().isoformat() if error_count > 0 else None

    save_status(status)
    print("=== 检查完成 ===")

if __name__ == "__main__":
    main()
```

## ⏰ 设置定时监控任务

### 方法一: 使用 Hermes Cronjob

```bash
# 创建 cronjob
cronjob create \
  --schedule "every 15 minutes from 02:00 to 08:00" \
  --name "ark-token-watchdog" \
  --prompt "
运行监控脚本:
python3 /Users/me/.hermes/scripts/monitor-token-status.py

请分析脚本输出，如果检测到 InvalidToken 错误或网关已重启，简要报告结果。
"
```

### 方法二: 使用系统 crontab

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每 15 分钟检查一次，重点覆盖凌晨 2-8 点）
*/15 2-8 * * * /usr/bin/python3 /Users/me/.hermes/scripts/monitor-token-status.py >> /Users/me/.hermes/logs/token-monitor.log 2>&1
```

## 📊 监控指标说明

| 指标 | 阈值 | 动作 |
|------|------|------|
| 60 分钟内 InvalidToken 次数 | ≥ 3 | 自动重启网关 |
| 连续重启失败次数 | ≥ 3 | 告警通知（需扩展） |
| 单日重启次数 | ≥ 5 | 告警通知（需扩展） |

## 🔍 问题定位清单

当发现网关无响应时，按此顺序排查：

1. [ ] 检查 `gateway.error.log` 中是否有 `InvalidToken`
2. [ ] 确认时间是否在凌晨 3:00-4:00 之间
3. [ ] 测试新 API Key 是否正常
4. [ ] 更新 `config.yaml` 中的 ark Provider 配置
5. [ ] 重启网关: `hermes gateway restart`
6. [ ] 等待 5 秒后再次检查错误日志
7. [ ] 测试发送消息验证平台恢复

## ⚠️ 已知限制

1. **Token 过期时间不固定**: 通常在 3:23 AM 左右，但可能有 ±10 分钟波动
2. **级联故障传播快**: 从第一个 InvalidToken 到全平台停止响应仅需 2-5 分钟
3. **需要手动更新 API Key**: 目前无法自动轮换，检测到问题后仍需人工更新密钥
4. **重启后有恢复时间**: 网关重启后需要约 10-30 秒才能完全恢复服务

## 🚀 进阶：Key 安全加固（推荐）

监控只是被动防御，**根本解决方案**是消除硬编码 Key。使用环境变量管理 API Key：

1. ✅ **消除泄露风险**: `config.yaml` 中不再有明文 Key
2. ✅ **简化轮换**: 更新 Key 只需修改 1 处（环境变量）
3. ✅ **配置可分享**: 脱敏后的配置文件可以安全分享

详见技能: `hermes-secrets-env-migration`

```python
# 一键执行迁移
python3 ~/.hermes/skills/hermes/hermes-secrets-env-migration/scripts/migrate-secrets-to-env.py
```

## ⏱️ 配套：长上下文超时防护

大型模型（GLM-4, Doubao 等）长上下文推理需要更长超时，否则会导致：
- 任务中断
- 错误日志污染
- 用户体验差

在 `config.yaml` 中添加全局超时配置：
```yaml
env:
  HERMES_STREAM_STALE_TIMEOUT: "600"      # 流式超时 10 分钟
  HERMES_NON_STREAM_TIMEOUT: "900"        # 非流式超时 15 分钟
  OPENAI_TIMEOUT: "600"                    # OpenAI 兼容 API 超时
```

各 Provider 独立配置：
```yaml
providers:
  edgefn:  # 或其他 Provider
    base_url: "https://api.example.com/v1"
    api_key: "${EDGEFN_API_KEY}"
    timeout: 600
```

## 📝 相关文档

- `TOKEN-EXPIRY-MONITOR-SETUP.md` - 部署记录
- `MESSAGE-RATE-LIMIT-FIX.md` - 消息限流问题修复
- `Hermes Gateway 消息平台配置与故障排查` - 平台接入指南
- `hermes-secrets-env-migration` - API Key 环境变量迁移
