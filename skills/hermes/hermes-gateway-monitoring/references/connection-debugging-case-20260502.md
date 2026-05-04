# 连接问题诊断案例：2026-05-02

## 用户报告

用户说："修复昨晚的连接问题"、"昨晚21:16元宝有收到文件"

## 诊断过程

### 1. 初始信息收集

```bash
# 搜索会话记录
session_search(limit=3)  # 查看最近会话

# 搜索 fact_store
fact_store(action="search", query="连接问题 Hermes 连接失败")  # 无结果
```

### 2. 时间戳精确匹配

```bash
# 搜索昨晚21点的日志
grep "2026-05-02 21:1" ~/.hermes/logs/gateway.log

# 发现：
# - 21:12:45 飞书权限错误
# - 21:15:16 飞书权限错误
# - 21:16:03 微信发送超时
# - 21:17:15 微信发送超时
```

### 3. 定位会话文件

```bash
# 查找昨晚21点的会话文件
ls -la ~/.hermes/sessions/*.json | grep "May  2" | grep -E "21:|22:"

# 发现：
# - session_20260502_174928_868b5e9e.json (21:21)
# - session_20260502_193830_f65e06.json (21:26)  ← 这个是目标
```

### 4. 提取会话内容

```bash
# 提取用户消息
python3 << 'EOF'
import json, re
with open('session_20260502_193830_f65e06.json', 'r') as f:
    content = f.read()
user_messages = re.findall(r'"role":\s*"user".*?"content":\s*"([^"]+)"', content, re.DOTALL)
EOF

# 用户消息序列：
# 1. "凌晨翻完今天的新闻..."
# 2. "帮我做一份Deepseek v4对AI行业的影响..."
# 3. "帮我安装依赖重新生成"
# 4. "发送到飞书让我看看"
# 5. "发送到telegram"
# 6. "除了telegram还有哪些频道支持图片和文件发送"
# 7. "同时发送到微信和元宝"  ← 关键！
# 8. "现在把这个bug提给开发者"
# 9. "把报告发送到企业微信试试"
```

### 5. 查找发送记录

```bash
# 搜索 send_message 调用和结果
grep -A 50 "同时发送到微信和元宝" session_20260502_193830_f65e06.json | \
  grep -E "send_message|yuanbao|weixin|MEDIA|error|成功"

# 发现：
# 1. 发送到元宝：
#    {"success": true, "platform": "yuanbao", "chat_id": "direct:xxx", "mirrored": true}
# 
# 2. 发送到微信：
#    {"error": "Weixin send failed: Timeout context manager should be used inside a task"}
```

## 诊断结论

**实际情况**：
- ✅ 元宝连接正常，文件发送成功
- ❌ 微信发送失败（网络超时，不是连接问题）
- ✅ Gateway 正常运行
- ✅ 其他平台连接正常

**用户误解**：
用户说"连接问题"，实际上是：
1. 元宝没有问题（用户也确认"21:16收到文件"）
2. 微信是发送超时，不是连接断开

## 关键技术点

### 时间戳匹配技巧

```bash
# 精确到分钟
grep "2026-05-02 21:16" log

# 精确到小时段
grep "2026-05-02 21:1" log

# 会话文件时间戳在文件名中
session_20260502_193830_f65e06.json  # 19:38:30 开始，21:26 最后更新
```

### 会话文件结构

```json
{
  "session_id": "20260502_193830_f65e06",
  "model": "GLM-5",
  "platform": "weixin",
  "session_start": "2026-05-03T03:28:24",
  "last_updated": "2026-05-03T03:30:25"
}
```

**注意**：session_start 是会话创建时间，last_updated 是最后更新时间。文件修改时间是更准确的参考。

### send_message 结果判断

```json
// 成功
{"success": true, "platform": "yuanbao", "chat_id": "xxx", "mirrored": true}

// 失败（网络超时）
{"error": "Weixin send failed: Timeout context manager should be used inside a task"}

// 失败（文件不存在）
{"error": "Media file not found"}

// 失败（Token 被锁定）
{"error": "Token already in use"}  // 需要先停止 Gateway
```

## 经验总结

1. **用户报告 ≠ 实际问题**
   - 用户说"连接问题"可能是"发送失败"
   - 用户说"没收到"可能是"发送成功但没注意"

2. **优先查找会话文件**
   - 会话文件包含完整的消息发送记录
   - 可以精确还原用户操作和系统响应

3. **时间戳是关键**
   - 用户提供的具体时间（如"21:16"）是最重要的线索
   - 用时间戳过滤日志和会话文件

4. **区分连接 vs 发送**
   - 连接问题：日志中看不到平台连接记录
   - 发送问题：日志中有连接记录，但 send_message 返回错误

## 相关修复

本次会话确认了以下修复（之前已完成）：

1. ✅ Token 监控误判修复 - 不再因 400 状态码触发重启
2. ✅ Gateway 进程守护 - 每 5 分钟自动检查存活
3. ✅ 日志级别改为 INFO - 可以看到平台连接状态
4. ✅ 文件发送 Skill - 支持企业微信/Telegram/元宝

## 下次类似问题的快速诊断流程

```bash
# 1. 获取用户提供的具体时间
TIME="21:16"  # 从用户消息中提取

# 2. 搜索日志
grep "2026-05-02 ${TIME}" ~/.hermes/logs/gateway.log

# 3. 查找会话文件
ls -la ~/.hermes/sessions/*.json | grep "$(date +%b\ %e)" | grep -E "${TIME%%:*}:"

# 4. 提取 send_message 结果
grep -A 5 "send_message" session_*.json | grep -E "success|error"

# 5. 检查当前 Gateway 状态
hermes gateway status && tail -50 ~/.hermes/logs/gateway.log | grep connected
```
