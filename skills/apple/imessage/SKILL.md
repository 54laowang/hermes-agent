---
name: imessage
description: 在 macOS 上通过 imsg CLI 发送和接收 iMessage/SMS。
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [iMessage, SMS, messaging, macOS, Apple]
prerequisites:
  commands: [imsg]
  os: macos
---

# iMessage

Use `imsg` to read and send iMessage/SMS via macOS Messages.app.

## Prerequisites

- **macOS** with Messages.app signed in
- Install: `brew install steipete/tap/imsg`
- Grant Full Disk Access for terminal (System Settings → Privacy → Full Disk Access)
- Grant Automation permission for Messages.app when prompted

### 前置条件检查点

在执行任何操作前，**必须按顺序验证**：

```bash
# 检查点 1: 确认是 macOS
[[ "$(uname)" != "Darwin" ]] && echo "ERROR: 仅支持 macOS" && exit 1

# 检查点 2: 确认 imsg 已安装
if ! command -v imsg &> /dev/null; then
  echo "ERROR: imsg 未安装"
  echo "FIX: brew install steipete/tap/imsg"
  exit 1
fi

# 检查点 3: 确认 Messages.app 正在运行
if ! pgrep -x "Messages" > /dev/null; then
  echo "WARN: Messages.app 未运行，正在启动..."
  open -a Messages
  sleep 2
fi

# 检查点 4: 确认用户已登录 Messages.app
# 尝试获取 chats 列表来验证登录状态
if ! imsg chats --limit 1 --json 2>/dev/null | jq -e '.[0]' > /dev/null 2>&1; then
  echo "ERROR: Messages.app 未登录或权限未授予"
  echo "FIX: 1. 打开 Messages.app 登录 Apple ID"
  echo "     2. 系统设置 → 隐私与安全 → 完全磁盘访问权限 → 添加终端"
  echo "     3. 系统设置 → 隐私与安全 → 自动化 → 确认终端可控制 Messages"
  exit 1
fi
```

## When to Use

- User asks to send an iMessage or text message
- Reading iMessage conversation history
- Checking recent Messages.app chats
- Sending to phone numbers or Apple IDs

## When NOT to Use

- Telegram/Discord/Slack/WhatsApp messages → use the appropriate gateway channel
- Group chat management (adding/removing members) → not supported
- Bulk/mass messaging → always confirm with user first
- Emergency/urgent messages → SMS 可能延迟，建议直接使用手机

## Quick Reference

### List Chats

```bash
imsg chats --limit 10 --json
```

### View History

```bash
# By chat ID
imsg history --chat-id 1 --limit 20 --json

# With attachments info
imsg history --chat-id 1 --limit 20 --attachments --json
```

### Send Messages

```bash
# Text only
imsg send --to "+141****1212" --text "Hello!"

# With attachment
imsg send --to "+141****1212" --text "Check this out" --file /path/to/image.jpg

# Force iMessage or SMS
imsg send --to "+141****1212" --text "Hi" --service imessage
imsg send --to "+141****1212" --text "Hi" --service sms
```

### Watch for New Messages

```bash
imsg watch --chat-id 1 --attachments
```

## Service Options

- `--service imessage` — Force iMessage (requires recipient has iMessage)
- `--service sms` — Force SMS (green bubble)
- `--service auto` — Let Messages.app decide (default)

## 参数验证规则

### 电话号码格式

**有效格式**：
- `+86138****1234` (带国际区号)
- `+141****1212` (美国号码)
- `138****1234` (无区号，自动识别本地)

**无效格式**：
- `abc123` (非数字)
- `+123` (太短)
- `+1234567890123456` (太长)

**验证函数**：
```bash
validate_phone() {
  local phone="$1"
  # 移除空格和短横线
  phone="${phone//[- ]/}"
  # 检查格式
  if [[ "$phone" =~ ^\+[0-9]{10,15}$ ]] || [[ "$phone" =~ ^[0-9]{11}$ ]]; then
    echo "$phone"
    return 0
  else
    echo "ERROR: 无效电话号码格式: $phone" >&2
    echo "期望: +[国际区号][号码] 或 11位本地号码" >&2
    return 1
  fi
}
```

### 文件附件验证

**检查清单**：
1. 文件是否存在
2. 文件大小限制 (iMessage 附件限制 100MB)
3. 文件类型支持

```bash
validate_attachment() {
  local file="$1"
  
  # 检查文件存在
  if [[ ! -f "$file" ]]; then
    echo "ERROR: 文件不存在: $file" >&2
    return 1
  fi
  
  # 检查文件大小 (100MB 限制)
  local size_mb=$(($(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null) / 1024 / 1024))
  if [[ $size_mb -gt 100 ]]; then
    echo "ERROR: 文件过大: ${size_mb}MB (限制 100MB)" >&2
    return 1
  fi
  
  # 警告大文件
  if [[ $size_mb -gt 50 ]]; then
    echo "WARN: 文件较大 (${size_mb}MB)，发送可能需要时间"
  fi
  
  return 0
}
```

### 消息长度限制

- **iMessage**: 无硬性限制，但建议 < 4000 字符
- **SMS**: 160 字符/条，超出会分批发送

```bash
validate_message_length() {
  local text="$1"
  local service="${2:-auto}"
  local len=${#text}
  
  if [[ "$service" == "sms" ]]; then
    if [[ $len -gt 160 ]]; then
      echo "WARN: SMS 超过 160 字符 ($len)，将分 $(( (len + 159) / 160 )) 条发送"
    fi
  elif [[ $len -gt 4000 ]]; then
    echo "WARN: 消息较长 ($len 字符)，考虑分段发送"
  fi
}
```

## 错误处理指南

### 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `command not found: imsg` | imsg 未安装 | `brew install steipete/tap/imsg` |
| `Permission denied` | 无完全磁盘访问权限 | 系统设置 → 隐私 → 完全磁盘访问权限 |
| `Automation permission denied` | 无自动化权限 | 系统设置 → 隐私 → 自动化 |
| `No chats found` | Messages.app 未登录 | 打开 Messages.app 登录 Apple ID |
| `Invalid phone number` | 号码格式错误 | 使用 +国际区号 格式 |
| `Attachment too large` | 附件超过 100MB | 压缩或分割文件 |
| `Service not available` | SMS 服务不可用 | 确认 iPhone 与 Mac 连接 |
| `Recipient not found` | 联系人不存在 | 确认号码正确，添加到通讯录 |

### 错误处理模板

```bash
send_message_safe() {
  local to="$1"
  local text="$2"
  local file="${3:-}"
  
  # 前置检查
  validate_phone "$to" || return 1
  validate_message_length "$text"
  [[ -n "$file" ]] && validate_attachment "$file" || return 1
  
  # 发送并捕获错误
  local output
  output=$(imsg send --to "$to" --text "$text" ${file:+--file "$file"} 2>&1)
  local status=$?
  
  if [[ $status -ne 0 ]]; then
    echo "ERROR: 发送失败"
    echo "命令输出: $output"
    
    # 错误分类
    if echo "$output" | grep -qi "permission"; then
      echo "DIAG: 权限问题，检查完全磁盘访问权限和自动化权限"
    elif echo "$output" | grep -qi "network\|timeout"; then
      echo "DIAG: 网络问题，检查网络连接"
    elif echo "$output" | grep -qi "invalid"; then
      echo "DIAG: 参数无效，检查号码和消息格式"
    fi
    
    return 1
  fi
  
  echo "SUCCESS: 消息已发送"
  return 0
}
```

## 边界条件处理

### 1. 空消息处理

```bash
# 禁止发送空消息
if [[ -z "$text" ]] && [[ -z "$file" ]]; then
  echo "ERROR: 不能发送空消息"
  echo "必须提供文本或附件"
  exit 1
fi
```

### 2. 特殊字符处理

```bash
# 消息中的引号需要转义
text="He said \"Hello\""
# 或使用单引号包裹
text='He said "Hello"'

# Emoji 和 Unicode 完全支持
text="Hello 👋 你好"
```

### 3. 网络中断处理

```bash
# 检查网络状态
check_network() {
  if ! ping -c 1 -W 3 apple.com &>/dev/null; then
    echo "ERROR: 网络不可用"
    echo "iMessage 需要网络连接"
    return 1
  fi
  return 0
}

# 重试机制
send_with_retry() {
  local max_retries=3
  local retry_delay=5
  local attempt=1
  
  while [[ $attempt -le $max_retries ]]; do
    if send_message_safe "$@"; then
      return 0
    fi
    
    echo "尝试 $attempt/$max_retries 失败，${retry_delay}秒后重试..."
    sleep $retry_delay
    ((attempt++))
  done
  
  echo "ERROR: 重试 $max_retries 次后仍然失败"
  return 1
}
```

### 4. 多收件人处理

**注意**: `imsg` 不支持批量发送，需要逐个发送：

```bash
send_to_multiple() {
  local recipients=("+141****1212" "+141****3456")
  local text="$1"
  
  for to in "${recipients[@]}"; do
    echo "发送到 $to..."
    if ! send_message_safe "$to" "$text"; then
      echo "WARN: 发送到 $to 失败"
    fi
    # 防止触发频率限制
    sleep 1
  done
}
```

### 5. 附件类型支持

**支持**: 图片 (jpg/png/gif/heic), 视频 (mp4/mov), PDF, 文档
**不支持**: 压缩包 (zip/rar), 可执行文件 (.app/.exe)

```bash
check_attachment_type() {
  local file="$1"
  local ext="${file##*.}"
  ext="${ext,,}"  # 小写
  
  local unsupported=("zip" "rar" "7z" "app" "exe" "dmg" "pkg")
  
  if [[ " ${unsupported[*]} " =~ " $ext " ]]; then
    echo "ERROR: 不支持的附件类型: .$ext"
    return 1
  fi
  
  return 0
}
```

## 安全与隐私

### 敏感信息处理

1. **号码脱敏**: 日志输出时脱敏中间 4 位
   ```bash
   mask_phone() {
     local phone="$1"
     echo "${phone:0:3}****${phone: -4}"
   }
   ```

2. **消息内容保护**: 避免在日志中记录完整消息
   ```bash
   log_send() {
     local to="$1"
     local text="$2"
     echo "发送消息到 $(mask_phone "$to"): ${text:0:20}..." 
   }
   ```

3. **附件路径验证**: 确保附件路径在用户授权目录
   ```bash
   validate_path_safety() {
     local file="$1"
     local resolved=$(realpath "$file")
     
     # 只允许访问用户目录下的文件
     if [[ ! "$resolved" =~ ^$HOME ]]; then
       echo "ERROR: 只能发送用户目录下的文件"
       return 1
     fi
     return 0
   }
   ```

## Rules

1. **Always confirm recipient and message content** before sending
2. **Never send to unknown numbers** without explicit user approval
3. **Verify file paths** exist before attaching
4. **Don't spam** — rate-limit yourself (至少 1 秒间隔)
5. **Mask sensitive info** in logs and confirmations
6. **Check prerequisites** before any operation

## Example Workflow

User: "Text mom that I'll be late"

```bash
# 1. 前置检查
check_prerequisites || exit 1

# 2. Find mom's chat
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 3. Confirm with user: "Found Mom at +155****3456. Send 'I'll be late' via iMessage?"

# 4. Validate and send
to="+155****3456"
text="I'll be late"
validate_phone "$to" || exit 1
validate_message_length "$text"

# 5. Send after confirmation
if send_message_safe "$to" "$text"; then
  echo "✓ 消息已发送"
else
  echo "✗ 发送失败"
fi
```

## Test Cases

### 基本功能测试

```bash
# 测试 1: 列出聊天
test_list_chats() {
  local result=$(imsg chats --limit 5 --json 2>&1)
  if echo "$result" | jq -e '.[0].chatId' > /dev/null 2>&1; then
    echo "✓ PASS: 列出聊天"
    return 0
  else
    echo "✗ FAIL: 列出聊天"
    return 1
  fi
}

# 测试 2: 参数验证
test_validate_phone() {
  validate_phone "+86138****1234" > /dev/null && echo "✓ PASS: 有效号码"
  validate_phone "invalid" > /dev/null 2>&1 && echo "✗ FAIL: 应拒绝无效号码"
}

# 测试 3: 边界条件
test_empty_message() {
  if send_message_safe "+141****1212" "" 2>&1 | grep -q "空消息"; then
    echo "✓ PASS: 拒绝空消息"
  else
    echo "✗ FAIL: 应拒绝空消息"
  fi
}
```

## Troubleshooting

### 诊断命令

```bash
# 检查 imsg 版本
imsg --version

# 检查 Messages.app 状态
ps aux | grep -i messages

# 检查权限
# 完全磁盘访问: 系统设置 → 隐私与安全 → 完全磁盘访问权限
# 自动化: 系统设置 → 隐私与安全 → 自动化

# 测试基本功能
imsg chats --limit 1 --json | jq '.[0].displayName'
```

### 常见问题 FAQ

**Q: 发送消息时提示 "Permission denied"**
A: 需要授予完全磁盘访问权限和自动化权限。系统设置 → 隐私与安全 → 完全磁盘访问权限 → 添加终端应用。

**Q: 如何发送 SMS 而非 iMessage？**
A: 使用 `--service sms` 参数。注意：SMS 需要 iPhone 与 Mac 配对且处于连接状态。

**Q: 附件发送失败**
A: 检查文件大小 (< 100MB)、文件类型、文件路径是否在用户目录下。

**Q: 中文消息乱码**
A: 确保终端使用 UTF-8 编码：`export LANG=en_US.UTF-8`

## Version History

- **1.1.0** (2026-05-02): 添加检查点、异常处理、边界条件、测试用例
- **1.0.0**: 初始版本
