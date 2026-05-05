# L5 Context Memory - 任务上下文管理

## 概述

L5 Context Memory 是 Hermes 记忆系统的第五层，用于管理任务特定的上下文信息。补齐了 L1-L4 记忆系统后，实现了完整的六层记忆架构。

## 架构位置

```
L6: Skills 系统（82 个可复用流程）
    ↓
L5: Context Memory（任务特定上下文）← 本模块
    ↓
L4: 全息记忆（fact_store + KG）
    ↓
L3: 知识归档（MemPalace）
    ↓
L2: 短期记忆（memory tool）
    ↓
L1: 会话记忆（SQLite sessions）
```

## 核心功能

### 1. 任务生命周期管理

```python
from task_context import create_task, update_step, add_result

# 创建任务
task = create_task(
    goal="分析 A 股市场近期走势",
    constraints=[
        "必须验证时间戳",
        "至少 3 个数据源交叉验证"
    ],
    steps=[
        "获取当前时间",
        "判断市场状态",
        "获取行情数据",
        "交叉验证",
        "生成分析报告"
    ]
)

# 更新步骤
update_step("获取当前时间", "completed", "2026-05-04 06:20:00")

# 添加结果
add_result("判断市场状态", "A股已收盘（15:00后）")

# 完成任务
manager = get_task_context_manager()
manager.complete_task(final_result="分析报告已生成")
```

### 2. 上下文 Prompt 生成

```python
from task_context import get_context_prompt

# 自动注入到 LLM Prompt
prompt = get_context_prompt()

# 输出示例：
"""
### Task Context

**Task ID**: task_20260504_061732
**Goal**: 分析 A 股市场近期走势

**Progress**: 2/5 (40%)

**Current Step**: 判断市场状态

**Steps**:
  ✅ 1. 获取当前时间
→ ▶️ 2. 判断市场状态
  ⏸️ 3. 获取行情数据
  ⏸️ 4. 交叉验证
  ⏸️ 5. 生成分析报告

**Constraints**:
- 必须验证时间戳
- 至少 3 个数据源交叉验证

**Recent Results** (last 3):
- [判断市场状态]: A股已收盘（15:00后）
"""
```

### 3. 自动检测与注入

**Hook 集成**：
- `task_context_detector.py`（post_llm_call）- 检测任务关键词
- `pre_llm_call.sh` - 注入上下文 Prompt

**触发关键词**：
- 任务开始："第一步"、"首先"、"步骤"、"流程"
- 步骤更新："正在"、"现在"、"接下来"
- 任务完成："完成"、"结束"、"搞定"

## CLI 工具

```bash
# 列出任务
hermes-task list

# 显示当前任务
hermes-task current

# 创建任务
hermes-task create "分析A股市场" --steps="获取数据,分析,生成报告"

# 更新步骤
hermes-task update "获取数据" completed --result="数据已获取"

# 完成任务
hermes-task complete --result="报告已生成"

# 清理任务
hermes-task clear [task_id]
```

## 数据存储

- **存储位置**：`~/.hermes/task_contexts/`
- **文件格式**：JSON
- **命名规则**：`task_{YYYYMMDD_HHMMSS}.json`

## 使用场景

### ✅ 适合使用 Context Memory

1. **多步骤复杂任务**
   - 数据分析流程（获取 → 清洗 → 分析 → 报告）
   - 代码重构任务（分析 → 规划 → 执行 → 验证）
   - 研究任务（搜索 → 整理 → 总结 → 输出）

2. **需要追踪中间状态**
   - 长时间运行的任务
   - 需要回溯的任务
   - 可能失败重试的任务

3. **有明确约束条件**
   - 数据验证规则
   - 时间限制
   - 资源限制

### ❌ 不适合使用

1. **简单单步任务**
   - 简单问答
   - 单次查询
   - 快速翻译

2. **无需追踪状态**
   - 简单聊天
   - 一次性命令

## 与其他记忆层协作

```
用户输入："分析 A 股市场"
    ↓
L1（会话记忆）：检索当前会话历史
    ↓
L2（短期记忆）：加载用户偏好
    ↓
L3（MemPalace）：检索相关知识
    ↓
L4（fact_store）：查询实体关系
    ↓
L5（Context Memory）：创建任务上下文 ← 新增
    ↓
L6（Skills）：加载分析流程
    ↓
Agent 执行任务
    ↓
结果写回各层记忆
```

## 技术细节

### 数据结构

```python
@dataclass
class TaskContext:
    task_id: str
    goal: str
    current_step: str
    steps: List[TaskStep]
    intermediate_results: List[Dict]
    constraints: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class TaskStep:
    name: str
    status: str  # pending, in_progress, completed, failed
    result: Any
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

### 线程安全

- 使用单例模式管理全局状态
- 文件锁确保并发写入安全
- 自动持久化到磁盘

## 最佳实践

### 1. 明确任务目标

```python
# ✅ 好的目标
goal = "分析 A 股市场 2026年5月4日 收盘数据"

# ❌ 模糊的目标
goal = "分析股市"
```

### 2. 合理拆分步骤

```python
# ✅ 清晰的步骤
steps = [
    "获取当前时间",
    "判断市场状态",
    "获取收盘数据",
    "验证数据准确性",
    "生成分析报告"
]

# ❌ 过于笼统
steps = ["分析"]
```

### 3. 设置约束条件

```python
# ✅ 明确约束
constraints = [
    "必须验证时间戳",
    "至少 3 个数据源交叉验证",
    "优先使用 P0 级数据源"
]

# ❌ 无约束
constraints = []
```

## 故障排查

### 问题：任务上下文未注入

**检查清单**：
1. `~/.hermes/hooks/hooks.yaml` 是否配置正确
2. `task_context_detector.py` 是否有执行权限
3. `~/.hermes/temp/task_context_inject.txt` 是否存在

### 问题：任务列表为空

**检查清单**：
1. `~/.hermes/task_contexts/` 目录是否存在
2. JSON 文件格式是否正确
3. 文件权限是否可读

## 更新日志

- **v1.0.0** (2026-05-04)
  - 初始版本
  - 核心功能实现
  - Hook 集成
  - CLI 工具

## 相关资源

- [Hermes 记忆系统架构](~/.hermes/CLAUDE.md)
- [Skills 系统](~/.hermes/skills/)
- [MemPalace 文档](~/.hermes/mempalace/)
