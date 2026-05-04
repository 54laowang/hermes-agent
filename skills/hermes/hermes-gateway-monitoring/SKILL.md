---
name: hermes-gateway-monitoring
description: Hermes Gateway 监控与故障修复 - Token 监控误判修复、进程守护、连接状态诊断、企业微信文件发送支持确认。当用户报告 Gateway 连接问题、消息无响应、平台配置丢失或询问文件发送支持时使用。
triggers:
  - Gateway 连接问题
  - 消息平台无响应
  - Token 监控误判
  - 企业微信文件发送
  - Gateway 进程守护
---

# Hermes Gateway 监控与故障修复

## 核心问题诊断清单

### 0. 日志级别检查（首选检查项）

```bash
# 检查日志级别配置
grep -A2 "^logging:" ~/.hermes/config.yaml

# 如果显示 level: WARNING，改为 INFO
# 否则 INFO 级别的连接日志不会显示
```

### 1. Gateway 进程状态检查

```bash
# 检查 Gateway 是否存活
hermes gateway status

# 检查 launchd 服务状态
launchctl list | grep hermes

# 检查进程 PID
ps aux | grep "gateway run" | grep -v grep
```

### 2. 日志诊断

```bash
# 主要日志
tail -100 ~/.hermes/logs/gateway.log

# 错误日志
tail -50 ~/.hermes/logs/gateway.error.log

# 搜索特定平台
grep -i "wecom\|WeCom" ~/.hermes/logs/gateway.log | tail -20
```

### 3. 平台连接状态

```bash
# 检查已加载的平台配置
python3 -c "
from gateway.config import load_gateway_config, Platform
config = load_gateway_config()
for p, c in config.platforms.items():
    if c.enabled:
        print(f'{p.value}: enabled={c.enabled}')
"
```

## 常见问题与修复

### 问题 1: Token 监控脚本误判导致 Gateway 重启

**症状**：
- 凌晨 3:25 Gateway 自动重启
- 日志显示 `Token 失效: 异常状态码: 400`

**根因**：
- `monitor-token-status.py` 将 400 状态码误判为 Token 失效
- 实际上 400 可能是请求参数问题，不是认证问题

**修复**：
```python
# 修改 monitor-token-status.py 的判断逻辑
elif response.status_code == 400:
    # 400 通常是请求参数问题，不是 Token 问题
    try:
        resp_json = response.json()
        error_msg = resp_json.get('error', {}).get('message', '')
        if 'auth' in error_msg.lower() or 'token' in error_msg.lower():
            return False, f"认证问题: {error_msg}"
    except:
        pass
    return True, f"Token 有效 (状态码 400 可能是请求参数问题)"
```

### 问题 2: 飞书权限错误触发重启

**症状**：
- 日志显示大量 `[Feishu] Failed to get chat info` 错误
- 错误计数超过阈值触发重启

**修复**：
```python
# 在 check_gateway_logs() 中添加忽略规则
ignore_patterns = ['Failed to get chat info', 'RemoteProtocolError', 'TimedOut']

for line in result.stdout.split('\n'):
    should_ignore = any(pattern in line for pattern in ignore_patterns)
    if should_ignore:
        continue
```

### 问题 3: 企业微信 WebSocket 断开

**症状**：
- 日志显示 `[Wecom] WebSocket error: WeCom websocket closed`
- 看不到连接成功的日志

**诊断步骤**：
```bash
# 1. 首先检查日志级别（最常见原因！）
grep -A2 "^logging:" ~/.hermes/config.yaml
# 如果显示 level: WARNING，则 INFO 日志不会显示

# 2. 检查环境变量
grep "WECOM" ~/.hermes/.env

# 3. 检查 config.yaml 配置
grep -A10 "wecom:" ~/.hermes/config.yaml

# 4. 测试适配器连接（直接验证）
cd ~/.hermes/hermes-agent && source venv/bin/activate
python3 << 'EOF'
import os, asyncio
os.chdir(os.path.expanduser('~/.hermes'))
from gateway.config import PlatformConfig
from gateway.platforms.wecom import WeComAdapter

async def test():
    adapter = WeComAdapter(PlatformConfig())
    print(f"bot_id: {adapter._bot_id}")
    result = await adapter.connect()
    print(f"连接结果: {result}")
    if result:
        await asyncio.sleep(2)
        await adapter.disconnect()

asyncio.run(test())
EOF
```

**可能原因（按优先级排序）**：

1. **日志级别设置过高**（最常见！）
   - `config.yaml` 中 `logging.level: WARNING`
   - 导致 INFO 级别的连接日志不显示
   - 实际上平台已正常连接，只是看不到日志
   - **修复**：改为 `level: INFO`

2. Bot Token 过期（需要重新扫码配对）
3. 企业微信服务端主动断开
4. 环境变量未正确加载

**解决方案**：
```yaml
# 修改 ~/.hermes/config.yaml
logging:
  level: INFO  # 从 WARNING 改为 INFO
```

然后重启 Gateway：
```bash
hermes gateway restart
```

**验证**：
```bash
# 现在应该能看到完整的连接日志
tail -50 ~/.hermes/logs/gateway.log | grep -E "Connecting|connected|wecom"
# 期望输出：
# Connecting to wecom...
# [Wecom] Connected to wss://openws.work.weixin.qq.com
# ✓ wecom connected
```

### 问题 4: 企业微信发送文件失败

**症状**：
- 日志显示 `Failed to send media (.pdf): Media file not found`

**结论**：
- **企业微信完全支持发送文件**（图片、文档、视频、语音）
- 失败原因是**文件路径不存在**，不是不支持

**支持的发送方法**：
- `send_image_file` - 发送图片
- `send_document` - 发送文档/文件
- `send_video` - 发送视频
- `send_voice` - 发送语音

**修复**：
- 确保文件路径正确且文件存在
- 使用绝对路径而非相对路径

### 问题 5: 飞书权限缺失导致功能异常

**症状**：
- 日志显示 `[Feishu] Failed to get chat info: [99991672] Access denied`
- 提示缺少 `im:chat:readonly`、`im:chat`、`im:chat:read` 权限
- 飞书 Bot 无法获取聊天信息

**根因**：
- 飞书应用未开通必要的应用身份权限
- 导致无法读取聊天信息、发送消息等功能

**修复**：
1. 打开飞书开放平台权限申请链接（日志中会提供）
2. 申请并开通任一权限：`im:chat:readonly` 或 `im:chat` 或 `im:chat:read`
3. 重启 Gateway 使权限生效

**验证**：
```bash
# 检查飞书权限错误是否消失
grep "Access denied" ~/.hermes/logs/gateway.log | tail -5
```

### 问题 6: 连接问题 vs 发送超时问题（用户报告诊断）

**症状**：
- 用户报告"昨晚 XX 平台有连接问题"或"XX 平台没收到消息"
- 用户确认特定时间点（如"21:16"）收到了内容

**诊断步骤**：

1. **定位会话文件**（精确时间匹配）
```bash
# 根据用户提到的时间查找会话
ls -la ~/.hermes/sessions/*.json | grep "May  2" | grep -E "21:|22:"

# 或直接搜索日志中的时间戳
grep "2026-05-02 21:16" ~/.hermes/logs/gateway.log
```

2. **检查会话内容**（查找 send_message 调用）
```bash
# 搜索会话文件中的消息发送记录
grep -A 5 "send_message" ~/.hermes/sessions/session_TIMESTAMP.json | grep -E "success|error|MEDIA"
```

3. **检查 message_id（关键！）**
```bash
# message_id 为空意味着未真正发送到服务器
# 格式：{"success": true, "message_id": "", "mirrored": true}
# 需要检查 message_id 是否为空
strings session.json | grep -A 2 "success.*true" | grep message_id
```

4. **区分问题类型**

| 症状 | 实际问题 | 诊断方法 |
|------|----------|----------|
| 用户说"没收到"但会话显示成功 | **检查 message_id** | `message_id` 为空 = 未真正发送 |
| 会话显示 `Timeout` 错误 | **网络超时，非连接问题** | 日志中搜索 `Timeout context manager` |
| 会话显示 `Media file not found` | **文件路径错误** | 检查 MEDIA: 路径是否存在 |
| 日志中没有该平台记录 | **真正的连接问题** | 检查平台启用状态和连接日志 |
| 客户端提示"不支持该消息类型" | **消息类型兼容性** | 检查消息类型（如 TIMFileElem） |

**典型案例**：
```json
// ⚠️ 注意：message_id 为空
{"success": true, "platform": "yuanbao", "message_id": "", "mirrored": true}

// ✅ 真正发送成功（有 message_id）
{"success": true, "platform": "telegram", "message_id": "242"}

// ❌ 发送失败
{"error": "Weixin send failed: Timeout context manager should be used inside a task"}
```

**关键结论**：
- **`success: true` 不等于真正发送**：必须检查 `message_id` 是否非空
- **`mirrored: true` 只是日志镜像**：表示消息被记录到会话日志，不代表发送成功
- **连接正常 ≠ 发送成功**：平台已连接，但发送可能因网络超时失败
- **用户确认收到 = 连接正常**：如果用户确认特定时间收到内容，说明平台连接正常
- **优先查会话文件**：会话文件记录了完整的 send_message 调用和结果

**验证步骤**：
```bash
# 1. 检查当前 Gateway 状态
hermes gateway status

# 2. 检查平台连接日志
tail -100 ~/.hermes/logs/gateway.log | grep -E "Connected|connected"

# 3. 测试发送（可选）
python3 ~/.hermes/scripts/send_file.py wecom TestUser /tmp/test.txt "测试"
```

### 问题 7: 元宝文件发送 - TIMFileElem 兼容性

**症状**：
- 元宝发送文件返回 `success: true`
- 但客户端提示"当前版本暂不支持该消息类型"
- 或客户端收到消息但无法打开文件

**根因分析**：

1. **消息类型检查**
```bash
# 元宝文件发送使用 TIMFileElem 消息类型
# 检查发送的消息类型
grep "TIMFileElem\|TIMImageElem" ~/.hermes/logs/gateway.log
```

2. **message_id 检查（关键！）**
```bash
# 如果 message_id 为空，说明未真正发送到腾讯服务器
strings session.json | grep "success.*true.*yuanbao"
# 输出示例：{"success": true, "message_id": "", "mirrored": true}
# ⚠️ 空的 message_id 表示未发送到服务器
```

3. **腾讯 IM 消息类型支持**

| 消息类型 | 说明 | 元宝客户端支持 |
|---------|------|---------------|
| `TIMTextElem` | 文本消息 | ✅ 完全支持 |
| `TIMImageElem` | 图片消息 | ✅ 完全支持 |
| `TIMFileElem` | 文件消息 | ⚠️ 可能不支持 |

**诊断流程**：

```bash
# 1. 独立测试发送（停止 Gateway）
hermes gateway stop

# 2. 直接调用适配器发送
python3 << 'EOF'
import sys, os, asyncio
os.environ['HERMES_HOME'] = '/Users/me/.hermes'
sys.path.insert(0, '/Users/me/.hermes/hermes-agent')

from gateway.platforms.yuanbao import YuanbaoAdapter
from gateway.config import PlatformConfig

async def test():
    config = PlatformConfig(enabled=True, extra={
        'app_id': os.getenv('YUANBAO_APP_ID'),
        'app_secret': os.getenv('YUANBAO_APP_SECRET'),
    })
    adapter = YuanbaoAdapter(config)
    await adapter.connect()
    result = await adapter.send_document(
        "direct:USER_ACCOUNT",
        "/path/to/file.pdf",
        caption="测试"
    )
    print(f"成功: {result.success}")
    print(f"message_id: {result.message_id}")  # 关键！
    print(f"错误: {result.error}")
    await adapter.disconnect()

asyncio.run(test())
EOF

# 3. 重启 Gateway
hermes gateway start
```

**解决方案**：

1. **如果 message_id 为空**：
   - 说明未真正发送到服务器
   - 检查 COS 上传是否成功
   - 检查腾讯 IM API 调用是否正确

2. **如果 message_id 非空但客户端不支持**：
   - 元宝客户端可能不支持 `TIMFileElem` 类型
   - 尝试发送图片（`TIMImageElem`）
   - 或发送文本消息 + 文件链接

3. **替代方案**：
   - 先上传文件到 COS 获取 URL
   - 发送文本消息包含文件链接
   - 用户点击链接下载文件

**重要提示**：
- 元宝客户端"当前版本暂不支持该消息类型"错误来自**客户端**，不是 Hermes
- 即使 Hermes 发送成功，客户端也可能无法渲染
- 需要确认元宝客户端是否支持 `TIMFileElem` 类型

### 问题 8: 跨平台消息转发限制

**症状**：
- 从飞书转发消息到元宝，元宝客户端显示"当前版本暂不支持该消息类型"
- 某些特殊消息类型无法正确渲染

**根因**：
- 飞书的某些消息类型（如合并转发、分享卡片、特殊卡片）无法跨平台转发
- Hermes 会将这些消息提取成文本描述，但元宝客户端可能无法识别
- 这个错误来自**元宝客户端**，不是 Hermes

**跨平台转发限制**：

| 消息类型 | 飞书 → 元宝 | 飞书 → 企业微信 | 说明 |
|---------|------------|----------------|------|
| 文本消息 | ✅ 支持 | ✅ 支持 | 正常转发 |
| 图片消息 | ✅ 支持 | ✅ 支持 | 提取后发送 |
| 文件消息 | ❌ 不支持 | ❌ 不支持 | 无法跨平台转发文件实体 |
| 合并转发 | ⚠️ 部分支持 | ⚠️ 部分支持 | 提取文本，可能显示异常 |
| 分享卡片 | ⚠️ 部分支持 | ⚠️ 部分支持 | 提取文本，可能显示异常 |

**解决方案**：
1. **文件转发**：先下载文件到本地，再用 `send_file.py` 发送到目标平台
2. **特殊消息**：复制文本内容，重新发送纯文本消息
3. **权限问题**：确保飞书 Bot 有必要权限，避免消息提取失败

### 问题 5: Gateway 进程意外停止

**解决方案**：添加进程守护脚本

```bash
# 创建 gateway-watchdog.py
# 每 5 分钟检查 Gateway 是否存活
# 意外停止时自动重启并发送微信告警

# 添加到 crontab
*/5 * * * * ~/.hermes/scripts/gateway-watchdog.py >> ~/.hermes/logs/gateway-watchdog.log 2>&1
```

## 配置文件检查

### .env 文件
```bash
# 检查关键环境变量
cat ~/.hermes/.env | grep -E "WECOM|FEISHU|TELEGRAM|WEIXIN"
```

### config.yaml
```yaml
# 正确的平台配置格式
platforms:
  wecom:
    enabled: true
    extra:
      bot_id: ${WECOM_BOT_ID}
      secret: ${WECOM_SECRET}
      home_channel: ${WECOM_HOME_CHANNEL}
```

## 重要注意事项

### 0. 日志级别影响诊断（最高优先级）

**关键发现**：
- `config.yaml` 中 `logging.level: WARNING` 会导致所有 INFO 日志不显示
- Gateway 的平台连接日志（`Connecting to...`、`✓ wecom connected`）都是 INFO 级别
- **如果看不到连接日志，首先检查日志级别！**

**快速诊断**：
```bash
# 检查当前日志级别
grep -A2 "^logging:" ~/.hermes/config.yaml
```

**正确配置**：
```yaml
logging:
  level: INFO  # 或 DEBUG，不要用 WARNING
```

**症状对比**：
| 症状 | 可能原因 | 日志级别影响 |
|------|----------|-------------|
| 看不到 "Connecting to..." | 日志级别 WARNING | ✅ 是这个原因 |
| 看不到平台连接成功 | 日志级别 WARNING | ✅ 是这个原因 |
| 只看到 WARNING/ERROR | 日志级别 WARNING | ✅ 是这个原因 |
| 看到飞书 Lark 连接日志 | 飞书用独立 SDK | 不受影响 |
| 看到错误但没有 INFO | 日志级别 WARNING | ✅ 是这个原因 |

### 1. Token 监控脚本优化原则

**不要因为非关键错误触发重启**：
- 400 状态码 ≠ Token 失效
- 飞书权限错误 ≠ Gateway 故障
- 网络抖动 ≠ 需要重启

**只在以下情况重启**：
- 明确的 401/403 认证错误
- 大量致命错误（需要设置更高阈值）

### 2. 进程守护原则

- 每 5 分钟检查一次即可（不要太频繁）
- 停止后先尝试重启
- 重启成功/失败都发送告警
- 包含诊断信息便于排查

### 3. 企业微信文件发送

- 完全支持，无需怀疑
- 失败时检查文件路径是否存在
- 支持 MEDIA: 标签发送

## 文件发送工具

### 快速发送文件到多平台

```bash
# 企业微信（独立可用，无需停止 Gateway）
python3 ~/.hermes/scripts/send_file.py \
  wecom WangTaoTao /path/to/file.pdf "文件说明"

# Telegram（需要先停止 Gateway，因为 Token 被锁定）
hermes gateway stop
python3 ~/.hermes/scripts/send_file.py \
  telegram 7954228359 /path/to/file.pdf "文件说明"
hermes gateway start

# 元宝（需要先停止 Gateway，chat_id 必须是用户/群组）
hermes gateway stop
python3 ~/.hermes/scripts/send_file.py \
  yuanbao "direct:user_account" /path/to/file.pdf "文件说明"
hermes gateway start
```

### 平台 Chat ID 获取

| 平台 | Chat ID 示例 | 获取方式 |
|------|-------------|----------|
| 企业微信 | `WangTaoTao` | 用户名或频道名 |
| Telegram | `7954228359` | 查看 Gateway 日志中的 `chat=` |
| 元宝 | `direct:user_account` 或 `group:group_code` | 私聊用 direct，群组用 group |

### ⚠️ 元宝 Chat ID 注意事项

**不要使用 bot_id 作为 chat_id！**
- bot_id（如 `bot_6b20c1bb...`）是 Bot 的标识，不是发送目标
- 发送到 bot_id 会返回成功但消息无处投递
- 正确格式：
  - 私聊：`direct:{user_account}`
  - 群组：`group:{group_code}`

### Token 锁定说明

**企业微信**：独立可用，不与 Gateway 竞争 Token

**Telegram/元宝**：Gateway 运行时会锁定 Token/连接
- 独立脚本发送会报错 `Token already in use`
- 解决方案：先停止 Gateway，发送文件，再启动

## 案例参考

- `references/connection-debugging-case-20260502.md` - 连接问题诊断完整案例：用户报告连接问题，实际是发送超时，包含完整的时间戳匹配、会话文件分析、结果判断流程
- `references/yuanbao-file-sending-case-20260503.md` - 元宝文件发送诊断案例：用户报告"昨晚能收到现在收不到"，通过时间戳定位会话文件发现实际发送成功，包含跨平台对比和用户误判分析
- `references/yuanbao-timfileelem-compatibility-20260503.md` - 元宝 TIMFileElem 兼容性诊断：客户端提示"当前版本暂不支持该消息类型"，包含 COS 上传日志解读、message_id 判断标准、替代方案建议
- `references/platform-file-sending-comparison-20260503.md` - **平台文件发送对比诊断**：CLI 端失败 vs 飞书端成功的根因分析，包含文件路径验证、平台稳定性对比（元宝 > 企业微信）、最佳实践建议

## 相关文件

- 监控脚本：`~/.hermes/scripts/monitor-token-status.py`
- 守护脚本：`~/.hermes/scripts/gateway-watchdog.py`
- 文件发送：`~/.hermes/skills/hermes/hermes-gateway-monitoring/scripts/send_file.py`
- 主配置：`~/.hermes/config.yaml`
- 环境变量：`~/.hermes/.env`
- 日志目录：`~/.hermes/logs/`
