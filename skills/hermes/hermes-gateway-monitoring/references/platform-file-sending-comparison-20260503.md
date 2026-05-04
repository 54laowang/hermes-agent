# 平台文件发送对比诊断案例

**日期**：2026-05-03  
**场景**：用户询问为什么 CLI 端发送文件失败，而飞书端成功

## 问题背景

用户在不同端尝试发送 DeepSeek V4 PDF 报告：

| 尝试时间 | 来源平台 | 目标平台 | 结果 |
|---------|---------|---------|------|
| 2026-05-03 08:24 | CLI | 企业微信 | ❌ 失败 |
| 2026-05-03 11:31 | 飞书 | 元宝 | ✅ 成功 |

## 失败原因分析（CLI → 企业微信）

### 1. 文件路径不存在（根本原因）

```
Media file not found: /绝对路径/文件.pdf
Media file not found: /Users/me/Documents/report.pdf
```

**诊断方法**：
```bash
# 发送前验证文件存在
ls -lh ~/Desktop/DeepSeek*.pdf

# 正确的文件路径
/Users/me/Desktop/DeepSeek-V4-Analysis.pdf (168K)
```

### 2. WeCom WebSocket 断开

```
WeCom last connected: 2026-04-28 12:04
From 2026-05-02 10:23: WeCom websocket closed
```

Gateway 重启后 WeCom WebSocket 没有自动连接。

### 3. 环境变量未传递

```
Gateway process (PID 90244) did NOT have WECOM environment variables loaded
```

launchd 服务没有从 `.env` 文件继承环境变量。

## 成功原因分析（飞书 → 元宝）

| 关键因素 | 状态 |
|---------|------|
| 文件路径 | ✅ 真实路径 `/Users/me/Desktop/DeepSeek-V4-Analysis.pdf` |
| 目标平台 | ✅ 元宝（稳定性高于企业微信） |
| 平台状态 | ✅ 刚重启 Gateway，所有平台连接正常 |
| 环境变量 | ✅ 不需要额外配置 |

## 核心差异总结

```
┌──────────────────────────────────────────────────────┐
│           文件发送成功三要素                           │
├──────────────────────────────────────────────────────┤
│ 1. 文件路径必须存在（发送前先 ls 验证）                 │
│ 2. 目标平台必须连接正常（刚重启 Gateway 更可靠）        │
│ 3. 选择稳定的平台（元宝 > 企业微信）                    │
└──────────────────────────────────────────────────────┘
```

## 平台稳定性对比

| 平台 | 连接方式 | 稳定性 | 文件发送 | 备注 |
|------|---------|--------|---------|------|
| 元宝 | 腾讯 IM | ⭐⭐⭐⭐⭐ | ✅ 支持 | 最稳定，无 WebSocket |
| 飞书 | Lark SDK | ⭐⭐⭐⭐ | ✅ 支持 | 独立 SDK，较稳定 |
| Telegram | HTTP API | ⭐⭐⭐⭐ | ✅ 支持 | 无长连接，稳定 |
| 企业微信 | WebSocket | ⭐⭐⭐ | ✅ 支持 | 需要长连接，易断开 |

## 最佳实践

### 1. 发送前验证文件

```python
# ✅ 正确做法
import os
file_path = "/Users/me/Desktop/DeepSeek-V4-Analysis.pdf"
if os.path.exists(file_path):
    send_message(message=f"MEDIA:{file_path}", target="yuanbao")
else:
    print(f"文件不存在: {file_path}")

# ❌ 错误做法
send_message(message="MEDIA:/绝对路径/文件.pdf", target="wecom")  # 路径不存在
```

### 2. 选择稳定的目标平台

```python
# 优先级：元宝 > 飞书 > Telegram > 企业微信
# 企业微信需要 WebSocket 长连接，最容易出问题
```

### 3. Gateway 重启后立即发送

```bash
# 重启后 3 秒内发送，确保平台连接正常
hermes gateway restart && sleep 3
# 然后发送文件
```

### 4. WeCom 问题排查

如果企业微信发送失败：

```bash
# 1. 检查 WeCom 是否连接
grep -i wecom ~/.hermes/logs/gateway.log | tail -20

# 2. 检查环境变量
grep "WECOM" ~/.hermes/.env

# 3. 重启 Gateway 并立即发送
hermes gateway restart
```

## 关键结论

1. **文件路径验证是第一要务** - 大多数"发送失败"其实是文件不存在
2. **平台选择影响成功率** - 元宝比企业微信更稳定
3. **Gateway 重启后立即发送** - 确保平台连接状态最佳
4. **不同端相同功能，差异在平台状态** - CLI 和飞书端本身没有功能差异
