# Memory 自动精简归档机制

## 🎯 目标

避免 Memory 满载导致写入失败，通过自动化机制定期精简归档。

---

## 📊 当前配置状态

**用户选择**：方案C（双保险）

| 组件 | 状态 | 功能 |
|------|------|------|
| Shell Hook | ✅ 已启用 | 每次对话前检查，>85% 自动精简 |
| Cronjob 配置 | ✅ 已创建 | 每天早8点检查，>70% 发通知 |
| 核心脚本 | ✅ 已就绪 | 使用率检查 + 自动归档 |

---

## 📊 三种自动化方案

### 方案1：Cronjob 定时检查（推荐新手）

**触发频率**：每天早8点

**安装方法**：
```bash
# 方式A：直接添加到 crontab
(crontab -l 2>/dev/null; echo "0 8 * * * ~/.hermes/scripts/memory-usage-check.sh") | crontab -

# 方式B：使用 Hermes 内置命令
hermes schedule add "0 8 * * *" "memory-usage-check"
```

**检查逻辑**：
```bash
# ~/.hermes/scripts/memory-usage-check.sh
MEMORY_USAGE=$(python3 ~/.hermes/scripts/get_memory_usage.py)

if [ $(echo "$MEMORY_USAGE > 0.70" | bc) -eq 1 ]; then
    echo "⚠️ Memory 使用率 ${MEMORY_USAGE}，建议精简"
    # 发送通知（微信/Telegram）
    hermes notify "Memory 使用率 ${MEMORY_USAGE}，建议运行：python3 ~/.hermes/scripts/memory-auto-archive.py"
fi
```

---

### 方案2：Shell Hook 自动触发（推荐进阶）

**触发频率**：每次对话前

**安装方法**：

在 `~/.hermes/hooks/pre_llm_call.sh` 中添加：
```bash
# Memory 使用率检查（轻量级，<50ms）
MEMORY_USAGE=$(python3 ~/.hermes/scripts/get_memory_usage.py 2>/dev/null || echo "0")

if [ $(echo "$MEMORY_USAGE > 0.85" | bc) -eq 1 ]; then
    echo "⚠️ Memory 使用率 ${MEMORY_USAGE}，自动精简中..." >&2
    python3 ~/.hermes/hooks/memory-auto-archiver.py --quiet
fi
```

**优点**：
- 完全自动化，无需人工干预
- 精简后立即生效
- 用户无感知

**缺点**：
- 每次对话增加 ~50ms 延迟
- 需要编写轻量级检查脚本

---

### 方案3：双保险（推荐，已启用）

**触发频率**：每次对话前 + 每天 8:00

**工作流程**：
```
┌─────────────────────────────────────────────┐
│           双保险自动精简机制                 │
├─────────────────────────────────────────────┤
│                                             │
│  【实时保护 - Shell Hook】                   │
│  ├─ 触发：每次对话前（<50ms）                │
│  ├─ 条件：Memory 使用率 > 85%               │
│  └─ 动作：自动精简归档                       │
│                                             │
│  【每日提醒 - Cronjob】                      │
│  ├─ 触发：每天早 8:00                        │
│  ├─ 条件：Memory 使用率 > 70%               │
│  └─ 动作：发送通知提醒                       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🔧 核心脚本

### get_memory_usage.py（轻量级检查）

```python
#!/usr/bin/env python3
import json
from pathlib import Path

memory_file = Path.home() / ".hermes" / "memory.json"
if memory_file.exists():
    data = json.load(open(memory_file))
    total = sum(len(e) for e in data.get('entries', []))
    print(f"{total / 5000:.2f}")
else:
    print("0.00")
```

### memory-auto-archive.py（自动归档）

**核心逻辑**：
1. 读取 Memory 条目
2. 识别可归档内容（Phase报告、进度条目、技术细节）
3. 迁移到 fact_store
4. 从 Memory 删除
5. 生成精简报告

**归档规则**：
| 内容类型 | 归档条件 | 归档位置 |
|---------|---------|---------|
| Phase 报告 | 包含 "Phase"、"完成（" | fact_store (project) |
| 安装通知 | 包含 "已安装"、"已移除" | fact_store (tool) |
| 技术细节 | 包含 "检查点"、"异常处理" | fact_store (general) |

**保留规则**：
- 时间锚定宪法
- 数据交叉验证原则
- 用户偏好
- 关键路径配置

---

## 📈 效果对比

| 方案 | 自动化程度 | 延迟 | 适用场景 |
|------|----------|------|---------|
| Cronjob | ⭐⭐ | 0 | 新手、低频使用 |
| Shell Hook | ⭐⭐⭐ | ~50ms | 进阶、高频使用 |
| 双保险 | ⭐⭐⭐⭐ | ~50ms | 最佳实践 |

---

## 🚀 快速开始

```bash
# 1. 创建必要目录
mkdir -p ~/.hermes/scripts ~/.hermes/logs

# 2. 复制脚本（已完成）
# scripts/get_memory_usage.py
# hooks/memory-auto-archiver.py
# scripts/memory-usage-check.sh

# 3. 测试运行
python3 ~/.hermes/scripts/get_memory_usage.py
python3 ~/.hermes/scripts/memory-auto-archive.py --dry-run

# 4. 启用自动精简（已完成）
# Shell Hook: ~/.hermes/hooks/pre_llm_call.sh
# Cronjob: cat ~/.hermes/cronjob_memory_check.txt | crontab -
```

---

## 📝 维护日志

| 日期 | 操作 | 效果 |
|------|------|------|
| 2026-05-02 | 手动精简 | 97% → 28%，节省 3,432 字符 |
| 2026-05-02 | 启用双保险 | Shell Hook + Cronjob 自动保护 |

---

## 🔗 相关文件

- `~/.hermes/hooks/pre_llm_call.sh` - Shell Hook 配置
- `~/.hermes/scripts/get_memory_usage.py` - 使用率检查
- `~/.hermes/hooks/memory-auto-archiver.py` - 自动归档
- `~/.hermes/scripts/memory-usage-check.sh` - Cronjob 检查
- `~/.hermes/cronjob_memory_check.txt` - Cronjob 配置
- `~/.hermes/logs/memory-archiver.log` - 精简日志
- `~/.hermes/logs/memory-cron.log` - Cronjob 日志