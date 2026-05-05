# MemPalace MCP 故障排查指南

## 问题症状

**2026-05-03 会话中发现**：
- `hermes mcp test mempalace` 连接成功（494ms）
- 但实际调用 MCP 工具时失败：`ClosedResourceError`
- 进程启动后立即退出

## 诊断流程

### 1. 检查进程状态
```bash
ps aux | grep -i mempalace | grep -v grep
```

**正常情况**：应该看到 1 个进程
**异常情况**：看到 2 个进程（PID 冲突）或 0 个进程

### 2. 检查数据库文件
```bash
ls -lh ~/.hermes/mempalace/*.sqlite3
ls -lh ~/.hermes/mempalace/*.sqlite3-wal
```

**文件说明**：
- `knowledge_graph.sqlite3` - 知识图谱（entities, triples 表）
- `chroma.sqlite3` - ChromaDB 向量存储（drawers 集合）

### 3. 测试 MCP 连接
```bash
hermes mcp test mempalace
```

**成功输出**：
```
✓ Connected (494ms)
✓ Tools discovered: 29
```

**失败输出**：
- `ClosedResourceError`
- `MCP server 'mempalace' is unreachable`

### 4. 检查 Gateway 状态
```bash
hermes gateway status
```

**关键信息**：
- PID - 进程是否在运行
- LastExitStatus - 上次退出状态码

## 常见问题与解决方案

### 问题 1：双进程冲突

**症状**：
- 两个 MemPalace 进程同时运行
- `ClosedResourceError` 或数据库锁错误

**原因**：
- 手动启动进程与 Gateway 启动的进程冲突
- 旧进程未正确清理

**解决**：
```bash
# 1. 终止所有 MemPalace 进程
ps aux | grep -i mempalace | grep -v grep | awk '{print $2}' | xargs kill

# 2. 重启 Gateway
hermes gateway restart

# 3. 等待 5 秒
sleep 5

# 4. 测试连接
hermes mcp test mempalace
```

### 问题 2：进程立即退出

**症状**：
- `hermes mcp test` 成功
- 但实际工具调用失败

**原因**：
- stdio 模式的 MCP 服务器需要父进程维持
- 测试时启动临时进程，调用时进程已退出

**解决**：
```bash
# 重启 Gateway（它会维持 MCP 进程）
hermes gateway restart

# 等待 MCP 初始化
sleep 5

# 测试实际调用
hermes chat -q "测试 mempalace 状态"
```

### 问题 3：数据库锁

**症状**：
- `database is locked` 错误
- 写入操作失败

**原因**：
- SQLite 连接未正确关闭
- 并发写入冲突

**解决**：
```bash
# 1. 检查 WAL 文件
ls -lh ~/.hermes/mempalace/*.sqlite3-wal

# 2. 如果 WAL 文件很大，说明有未提交的事务
# 重启所有相关进程
hermes gateway stop
ps aux | grep mempalace | awk '{print $2}' | xargs kill
hermes gateway start

# 3. 等待恢复
sleep 10
```

## 三重保险策略

当 MemPalace 不可用时，使用以下归档策略：

### 1. fact_store（主要归档）
```python
fact_store(
    action="add",
    content="关键事实内容",
    category="general",
    tags="tag1,tag2"
)
```

**优点**：
- SQLite 持久化，稳定可靠
- 不依赖 MCP 进程
- 支持实体、标签、信任度

### 2. 文件系统（完整报告）
```bash
# 写入实施记录
echo "# 实施记录\n..." > ~/.hermes/memory/darwin-evolution/YYYY-MM-DD-record.md

# 写入日报
echo "# 日报\n..." > ~/.hermes/memory/darwin-evolution/YYYY-MM-DD-report.md
```

**优点**：
- 完全自主控制
- 易于查阅和版本管理
- 不依赖任何外部服务

### 3. pending_sync.jsonl（待同步队列）
```json
{"content": "内容", "wing": "ai-agent", "room": "darwin-evolution", "timestamp": "2026-05-03T11:25:00"}
```

**优点**：
- MemPalace 恢复后可批量同步
- JSON 格式易于解析
- 不会丢失数据

## 手动同步到 MemPalace

MemPalace 恢复后，执行以下脚本同步待处理内容：

```python
import json
from pathlib import Path

# 读取待同步队列
pending_file = Path.home() / ".hermes" / "mempalace" / "pending_sync.jsonl"
if not pending_file.exists():
    print("没有待同步内容")
    exit(0)

with open(pending_file, 'r') as f:
    pending_items = [json.loads(line) for line in f]

print(f"发现 {len(pending_items)} 条待同步内容")

# 逐条同步（需要手动执行 MCP 调用）
for item in pending_items:
    print(f"\n同步: {item['content'][:50]}...")
    # 在 Hermes 会话中执行：
    # mempalace_add_drawer(content=item['content'], wing=item['wing'], room=item['room'])

# 同步完成后清空队列
# pending_file.unlink()
```

## 预防措施

### 1. 定期检查进程状态
```bash
# 添加到 crontab（每小时检查一次）
0 * * * * ps aux | grep -i mempalace | grep -v grep > /dev/null || hermes gateway restart
```

### 2. 监控日志
```bash
# 实时监控 MemPalace 相关日志
tail -f ~/.hermes/logs/gateway.log | grep -i mempalace
```

### 3. 使用 fact_store 优先
- fact_store 更稳定，不依赖 MCP 进程
- MemPalace 作为增强功能，不可用时不影响核心记忆

## 相关资源

- MemPalace 文档：https://github.com/your-repo/mempalace
- Hermes MCP 配置：`~/.hermes/config.yaml`
- 数据库位置：`~/.hermes/mempalace/`
- 日志位置：`~/.hermes/logs/gateway.log`

---

**创建时间**：2026-05-03  
**适用版本**：MemPalace 3.3.2 + Hermes Agent  
**维护者**：Hermes Agent
