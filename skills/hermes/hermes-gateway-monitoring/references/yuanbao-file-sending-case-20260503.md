# 元宝文件发送诊断案例 - 2026-05-03

## 用户报告

**症状**：昨晚元宝能收到文件，现在元宝没收到

## 诊断过程

### 1. 时间戳定位

用户提到"昨晚21:16元宝有收到文件"。

```bash
# 查找对应时间的会话文件
ls -la ~/.hermes/sessions/*.json | grep "May  2" | grep -E "21:|22:"
# 找到：session_20260502_193830_f65e06.json (最后修改时间 21:26)
```

### 2. 会话文件分析

```bash
# 搜索会话中的用户消息
python3 << 'EOF'
import json
with open('~/.hermes/sessions/session_20260502_193830_f65e06.json', 'r') as f:
    content = f.read()
user_messages = re.findall(r'"role":\s*"user".*?"content":\s*"([^"]+)"', content)
for msg in user_messages:
    print(msg[:200])
EOF

# 找到用户请求：
# "同时发送到微信和元宝"
```

### 3. 发送结果检查

```bash
# 搜索 send_message 调用和结果
grep -A 50 "同时发送到微信和元宝" session_20260502_193830_f65e06.json | grep -E "send_message|yuanbao|success|error"

# 发现：
# 1. 元宝发送：
#    {"success": true, "platform": "yuanbao", "chat_id": "direct:9jKEQ0JBZqgGUZSXDeUTWjBUULUcsfPHmqrsAbTOM+o=", "mirrored": true}
#
# 2. 微信发送：
#    {"error": "Weixin send failed: Timeout context manager should be used inside a task"}
```

### 4. Gateway 日志验证

```bash
# 检查昨晚日志
grep "2026-05-02.*21:1" ~/.hermes/logs/gateway.log | grep yuanbao

# 检查当前连接状态
tail -100 ~/.hermes/logs/gateway.log | grep -E "Connected|connected"
# 输出：
# 2026-05-03 09:38:22,829 INFO gateway.platforms.yuanbao: [Yuanbao] Connected. connectId=...
# 2026-05-03 09:38:22,834 INFO gateway.run: ✓ yuanbao connected
```

## 结论

### 实际情况

1. **昨晚（21:16）元宝发送记录** ⚠️
   - 文件：`/Users/me/Desktop/DeepSeek-V4-Analysis.pdf`
   - chat_id：`direct:9jKEQ0JBZqgGUZSXDeUTWjBUULUcsfPHmqrsAbTOM+o=`
   - 结果：`{"success": true, "message_id": "", "mirrored": true}`
   - **关键发现**：`message_id` 为空，`mirrored: true`

2. **message_id 为空意味着什么？**
   - 空的 `message_id` 表示**没有真正发送消息到腾讯 IM 服务器**
   - `mirrored: true` 表示只是镜像到了会话日志
   - 用户可能收到的是文本消息（文件名或描述），不是实际的 PDF 文件

3. **今天测试验证**
   - 独立调用 `YuanbaoAdapter.connect()` + `send_document()` 成功
   - 发送结果：`success: True, message_id: ""`
   - 用户反馈：客户端提示"当前版本暂不支持该消息类型"

4. **昨晚微信发送失败** ❌
   - 错误：`Timeout context manager should be used inside a task`
   - 原因：网络超时，不是连接问题

5. **当前元宝连接正常** ✅
   - Gateway 已连接
   - 元宝平台状态：Connected

### 问题类型判断

| 判断依据 | 结论 |
|---------|------|
| 会话文件显示 `success: true` | ⚠️ 需要检查 `message_id` |
| `message_id` 为空 | ❌ 未真正发送到服务器 |
| `mirrored: true` | ✅ 只是镜像到日志 |
| 用户确认"昨晚收到" | ⚠️ 可能是文本，不是文件 |
| 用户确认"客户端无更新" | ✅ 不是版本问题 |
| 客户端提示"不支持该消息类型" | ❌ TIMFileElem 兼容性问题 |

### 问题根因分析

**元宝文件发送的 TIMFileElem 兼容性问题**：

1. **昨晚的情况**：
   - 用户说"昨晚收到了文件"
   - 但 `message_id` 为空，说明可能没发送文件实体
   - 用户可能收到的是文本描述或文件名

2. **今天的情况**：
   - 文件确实上传到 COS 并发送（服务端成功）
   - 客户端收到但提示"不支持该消息类型"
   - 元宝客户端可能不再支持 `TIMFileElem` 消息类型

3. **腾讯 IM 支持的消息类型**：
   - `TIMTextElem` - 文本消息 ✅
   - `TIMImageElem` - 图片消息 ✅
   - `TIMFileElem` - 文件消息 ⚠️ 客户端可能不支持

## 关键教训

### 1. 时间戳是诊断的关键

用户提到具体时间（如"21:16"），立即定位：
- 会话文件（包含完整的 send_message 调用和结果）
- Gateway 日志（包含连接状态和发送日志）

### 2. 区分"连接问题"vs"发送问题"

| 症状 | 问题类型 | 诊断方法 |
|------|----------|----------|
| 平台显示 Connected | 连接正常 | 检查 Gateway 日志 |
| `success: true` | 发送成功 | 检查会话文件 |
| `Timeout` 错误 | 网络超时 | 检查错误消息 |
| `Media file not found` | 文件路径错误 | 检查文件是否存在 |

### 3. 会话文件是最好的证据

- 用户记忆可能模糊（"昨晚收到" vs "现在没收到"）
- Gateway 日志显示连接状态
- **会话文件记录了完整的 send_message 调用和结果**，这是判断发送是否成功的最终证据

### 4. 跨平台对比

同时发送到多个平台时：
- 每个平台独立判断成功/失败
- 一个平台失败不代表所有平台失败
- 分别记录在会话文件中

## 验证方法

```bash
# 1. 检查当前 Gateway 状态
hermes gateway status

# 2. 检查元宝连接
tail -100 ~/.hermes/logs/gateway.log | grep yuanbao

# 3. 测试发送（可选）
# 通过 API 或会话发送测试消息
```

## 相关问题

- **问题 6: 连接问题 vs 发送超时问题** - SKILL.md 中的标准诊断流程
- **微信超时问题** - `Timeout context manager should be used inside a task` 是网络问题，不是 Hermes 问题
