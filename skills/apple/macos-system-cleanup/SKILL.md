---
name: macos-system-cleanup
description: macOS 系统诊断和垃圾文件清理，检查 CPU、内存、磁盘并安全清理缓存
author: Hermes
category: apple
tags:
  - macos
  - cleanup
  - disk
  - cache
  - maintenance
---

# macOS System Cleanup Skill

## 描述
在 macOS 上进行系统诊断和垃圾文件清理，检查 CPU、内存、磁盘使用情况，并安全清理缓存文件释放空间。

## 触发条件
用户要求"诊断 Mac"、"检查资源占用"、"清理垃圾文件"、"释放磁盘空间"时使用。

## 步骤

### 1. 系统基础诊断
```bash
# CPU使用率和负载
top -l 1 | head -10

# 内存使用
vm_stat

# 磁盘空间
df -h /Users
```

### 2. 查看进程占用排行榜
```bash
# 按CPU排序
ps -eo pcpu,pmem,comm | sort -k 1 -r | head -20

# 按内存排序
ps -eo pcpu,pmem,comm | sort -k 2 -r | head -20
```

### 3. 扫描大体积缓存文件
```bash
# 检查常见缓存目录大小
du -sh ~/Library/Caches/* | sort -rh | head -20
```

### 4. 可安全清理的常见大缓存

| 路径 | 说明 | 是否可删 |
|------|------|---------|
| `~/Library/Caches/ms-playwright` | Playwright浏览器测试缓存 | ✅ 可删，下次自动下载 |
| `~/Library/Caches/com.anthropic.claudefordesktop.ShipIt` | Claude Desktop更新缓存 | ✅ 安装完成后可删 |
| `~/Library/Caches/com.anthropic.claude-code` | Claude Code缓存 | ✅ 可删 |
| `~/Library/Caches/Google/Chrome/Default/Cache` | Chrome浏览器缓存 | ✅ 可删，不影响数据 |
| `~/Library/Caches/cn.trae.app.ShipIt` | Trae AI更新缓存 | ✅ 可删 |
| `~/Library/Caches/*` | 大多数应用缓存 | ✅ 安全删除，系统自动重建 |

### 5. 清理命令
```bash
# 清理目标缓存
rm -rf [path]
```

## 注意事项
1. **不要删除** `~/Library/Preferences/` 下的配置文件
2. **不要删除** `~/Library/Containers/` 中应用数据除非你知道后果
3. 清理后空闲空间会立即释放，无需重启
4. macOS 内存压缩机制：即使显示"空闲内存少"，只要没用到交换分区就没问题

## 验证
清理后重新检查磁盘空间确认释放：
```bash
df -h /Users
```
