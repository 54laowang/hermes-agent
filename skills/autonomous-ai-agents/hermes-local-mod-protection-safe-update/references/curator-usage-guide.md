# Curator 功能使用指南

**更新时间**: 2026-05-01  
**来源**: 上游 v0.12.0 新增功能 (PR #18033)

---

## 概述

Curator 是 Hermes Agent 的后台技能维护系统，负责自动归档长期未使用的技能。

**2026-04-30 上游更新** 新增：
- **最活跃技能统计** (most active)
- **最少活跃技能统计** (least active)
- **活动追踪增强** (activity_count = use + view + patches)

---

## 命令使用

### 查看状态（核心功能）

```bash
# 方法 1: Python 模块调用
python -m hermes_cli.curator status

# 方法 2: CLI 交互模式（如果配置）
hermes curator status
```

### 其他子命令

```bash
# 手动运行一次清理
python -m hermes_cli.curator run

# 暂停/恢复自动清理
python -m hermes_cli.curator pause
python -m hermes_cli.curator resume

# 固定/取消固定技能（防止被归档）
python -m hermes_cli.curator pin <skill-name>
python -m hermes_cli.curator unpin <skill-name>

# 恢复已归档的技能
python -m hermes_cli.curator restore <skill-name>
```

---

## 状态报告解读

### 基本信息

```
curator: ENABLED              # 状态：ENABLED/PAUSED/DISABLED
  runs:           1           # 已运行次数
  last run:       1d ago      # 上次运行时间
  interval:       every 7d    # 自动运行间隔
  stale after:    30d unused  # 标记为陈旧的天数
  archive after:  90d unused  # 自动归档的天数
```

### 技能统计（新增功能）

#### 1. 最活跃技能 (most active)

```
most active (top 5):
  us-stock-data-acquisition-sop             activity= 21  use=  0  view=  9  patches= 12
  grid-trading-monitor                      activity= 21  use=  0  view=  6  patches= 15
  agchk-agent-self-audit                    activity= 18  use=  0  view=  4  patches= 14
```

**指标含义**：
- `activity`: 总活动次数 = use + view + patches
- `use`: 被加载使用的次数
- `view`: 被查看的次数
- `patches`: 被修改/补丁的次数

**用途**：
- ✅ 识别高频使用的核心技能
- ✅ 发现价值最高的技能（值得持续优化）
- ✅ 了解自己的工作模式

#### 2. 最少活跃技能 (least active)

```
least active (top 5):
  Agent Cognitive Architecture Evolution    activity=  0  use=  0  view=  0  patches=  0
  Auto Fact Extraction                      activity=  0  use=  0  view=  0  patches=  0
```

**含义**：
- 从未被使用的技能
- 可能是创建后忘记的技能

**用途**：
- ⚠️ 识别废弃技能（考虑删除或归档）
- 💡 发现需要改进的技能（可能功能不明确）
- 🗑️ 清理冗余，释放空间

#### 3. 最近最少活跃技能 (least recently active)

```
least recently active (top 5):
  design-image-studio                       activity=  1  use=  0  view=  1  patches=  0  last_activity=1d ago
```

**含义**：
- 按时间排序，最久未被使用的技能
- 反映的是**最近性**，而非**频率**

**用途**：
- 🕐 识别可能过时的技能
- 📅 发现阶段性使用的技能（如某个项目结束后不再需要）

---

## 实际应用场景

### 场景 1: 优化技能库

```bash
# 1. 查看最少使用的技能
python -m hermes_cli.curator status

# 2. 识别长期未用的技能（如 activity=0）

# 3. 决策：
#    - 删除：确认不再需要
#    - 归档：暂时不需要但可能有用
#    - 改进：功能不明确，需要优化描述

# 4. 固定重要技能（防止误删）
python -m hermes_cli.curator pin us-stock-data-acquisition-sop
```

### 场景 2: 发现核心工作流

```bash
# 查看最活跃的技能
python -m hermes_cli.curator status

# 分析结果：
# - us-stock-data-acquisition-sop (21次活动)
# - grid-trading-monitor (21次活动)
# - agchk-agent-self-audit (18次活动)

# 结论：用户的工作重心在
# 1. 美股数据分析
# 2. 网格交易监控
# 3. Agent 自审计

# 优化建议：可以将这些技能整合成工作流 Skill
```

### 场景 3: 技能健康检查

```bash
# 每周运行一次，检查技能使用情况
python -m hermes_cli.curator status > ~/skill-health-report.txt

# 对比上周报告，发现：
# - 新增的技能是否被使用？
# - 哪些技能从 active 变成 stale？
# - 哪些技能使用频率上升？
```

---

## 配置调整

编辑 `~/.hermes/config.yaml`:

```yaml
curator:
  enabled: true
  interval_hours: 168  # 7天运行一次
  stale_after_days: 30  # 30天未用标记为 stale
  archive_after_days: 90  # 90天未用自动归档
```

---

## 最佳实践

1. **定期检查** - 每周运行 `curator status` 查看技能使用情况
2. **固定核心技能** - 对高频使用的技能执行 `pin` 操作，防止误删
3. **清理废弃技能** - `activity=0` 的技能考虑删除或改进
4. **工作流优化** - 将高频使用的技能整合成工作流
5. **监控趋势** - 定期保存 status 报告，观察使用趋势

---

## 当前用户系统状态示例

```
agent-created skills: 297 total
  active     297
  stale      0
  archived   0

最活跃技能：
1. us-stock-data-acquisition-sop (21次)
2. grid-trading-monitor (21次)
3. agchk-agent-self-audit (18次)

最少活跃技能：
- Agent Cognitive Architecture Evolution (从未使用)
- Auto Fact Extraction (从未使用)
```

**建议**：
- ✅ 前三个技能是核心工作流，建议 `pin` 固定
- ⚠️ 从未使用的技能考虑删除或改进
