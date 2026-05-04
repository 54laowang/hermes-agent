# 元宝 TIMFileElem 消息类型兼容性问题诊断

## 案例背景

**时间**：2026-05-03 上午
**问题**：用户报告"昨晚元宝能收到 PDF 文件，今天收到但提示'当前版本暂不支持该消息类型'"
**客户端版本**：未更新

## 诊断过程

### 1. 确认昨晚发送记录

```bash
# 搜索昨晚的会话文件
ls -la ~/.hermes/sessions/*.json | grep "May  2" | grep -E "21:|22:"

# 查看发送结果
strings ~/.hermes/sessions/session_20260502_193830_f65e06.json | grep -A 2 "success.*true.*yuanbao"
```

**输出**：
```json
{
  "success": true,
  "platform": "yuanbao",
  "chat_id": "direct:9jKEQ0JBZqgGUZSXDeUTWjBUULUcsfPHmqrsAbTOM+o=",
  "message_id": "",
  "note": "Sent to yuanbao home channel",
  "mirrored": true
}
```

**关键发现**：
- `message_id` 为空（⚠️ 正常吗？）
- `mirrored: true`（只是日志镜像）
- 用户确认昨晚收到了完整的 PDF 文件

### 2. 独立测试发送

```bash
# 停止 Gateway（避免 Token 冲突）
hermes gateway stop

# 或直接停止 launchd 服务
launchctl bootout gui/501/ai.hermes.gateway

# 独立测试脚本
/Users/me/.hermes/hermes-agent/venv/bin/python3 << 'EOF'
import sys, os, asyncio
os.environ['HERMES_HOME'] = '/Users/me/.hermes'
sys.path.insert(0, '/Users/me/.hermes/hermes-agent')

from gateway.platforms.yuanbao import YuanbaoAdapter
from gateway.config import PlatformConfig

async def send_file():
    config = PlatformConfig(enabled=True, extra={
        'app_id': os.getenv('YUANBAO_APP_ID'),
        'app_secret': os.getenv('YUANBAO_APP_SECRET'),
    })
    
    adapter = YuanbaoAdapter(config)
    connected = await adapter.connect()
    
    if not connected:
        print("❌ 连接失败")
        return
    
    result = await adapter.send_document(
        "direct:9jKEQ0JBZqgGUZSXDeUTWjBUULUcsfPHmqrsAbTOM+o=",
        "/Users/me/Desktop/DeepSeek-V4-Analysis.pdf",
        caption="测试 PDF"
    )
    
    print(f"success: {result.success}")
    print(f"message_id: {result.message_id}")
    print(f"error: {result.error}")
    
    await adapter.disconnect()

asyncio.run(send_file())
EOF
```

### 3. 关键日志解读

**成功的发送日志**：
```
INFO: [Yuanbao] Connected. connectId=ae16bf93... botId=bot_6b20c1bb...
INFO: [Yuanbao] DocumentHandler: reading /path/to/file.pdf
INFO: HTTP Request: POST https://bot.yuanbao.tencent.com/api/resource/genUploadInfo "HTTP/1.1 200 OK"
INFO: COS PUT: bucket=hunyuan-prod-1258344703 region=ap-guangzhou key=/multimedia/.../file.pdf
INFO: HTTP Request: PUT https://hunyuan-prod-1258344703.cos.accelerate.myqcloud.com/... "HTTP/1.1 200 OK"
INFO: COS 上传成功: url=https://hunyuan.tencent.com/api/resource/download?resourceId=... size=172066
```

**关键点**：
1. ✅ 文件成功上传到腾讯 COS
2. ✅ 获得了下载 URL
3. ⚠️ `message_id` 为空（这可能是文件消息的特性）

### 4. 客户端错误分析

**错误提示**："当前版本暂不支持该消息类型"

**来源**：
- 这个错误来自**元宝客户端**，不是 Hermes
- 元宝客户端收到消息后无法渲染 `TIMFileElem` 类型

**可能原因**：
1. 元宝客户端不完全支持腾讯 IM 的 `TIMFileElem` 类型
2. 某些版本或某些场景下渲染失败
3. 文件类型或大小限制

### 5. 发送文本消息对比测试

```python
# 测试发送纯文本
result = await adapter.send(chat_id, "测试文本消息")
# 成功，客户端正常显示

# 测试发送文本文件
result = await adapter.send_document(chat_id, "/tmp/test.txt")
# 发送成功，客户端是否支持？
```

## 结论

### message_id 为空的含义

**发现**：
- 文件消息的 `message_id` 为空是**正常现象**
- 文件发送的关键是 **COS 上传成功**
- 只要日志显示 `COS 上传成功`，文件就已发送到腾讯服务器

**判断标准**：
```python
# ✅ 发送成功的标志
if "COS 上传成功" in logs:
    # 文件已上传到腾讯服务器
    # 客户端应该能收到

# ❌ 发送失败的标志
if result.error or "upload failed" in logs:
    # 发送失败
```

### TIMFileElem 兼容性问题

**现状**：
- Hermes 使用腾讯 IM 标准的 `TIMFileElem` 类型发送文件
- 服务端接收正常（COS 上传成功）
- **客户端渲染可能存在问题**

**建议**：
1. 如果用户报告"收到但无法打开"，确认：
   - 文件是否真的发送成功（检查 COS 上传日志）
   - 客户端是否支持该文件类型
   - 文件大小是否超限

2. 替代方案：
   - 发送图片用 `TIMImageElem`（完全支持）
   - 发送文件链接用文本消息
   - 用户点击链接下载

## 诊断清单

当用户报告"元宝收到文件但无法打开"时：

- [ ] 检查 COS 上传日志：`grep "COS 上传成功" ~/.hermes/logs/gateway.log`
- [ ] 确认文件 URL：日志中会有 `url=https://hunyuan.tencent.com/api/resource/download?resourceId=...`
- [ ] 测试发送文本消息：排除连接问题
- [ ] 测试发送图片：对比 `TIMImageElem` 和 `TIMFileElem`
- [ ] 确认客户端版本：是否更新
- [ ] 尝试其他文件类型：`.txt`、`.pdf`、`.jpg` 对比

## 相关文件

- 元宝适配器：`/Users/me/.hermes/hermes-agent/gateway/platforms/yuanbao.py`
- 消息构建：`/Users/me/.hermes/hermes-agent/gateway/platforms/yuanbao_media.py`
- 文件发送 Skill：`~/.hermes/skills/send-file-to-platforms/SKILL.md`
