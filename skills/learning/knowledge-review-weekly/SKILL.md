---
name: knowledge-review-weekly
description: 每周知识复盘 - 整理本周学习内容、归档重要信息、清理过时数据
priority: P2
triggers:
  - 用户说"周复盘"
  - 用户说"本周总结"
  - 用户说"整理一下记忆"
auto_load: false
---

# 每周知识复盘流程

## 核心目标
系统化整理本周学习内容，归档重要信息，清理过时数据，保持记忆系统健康。

## 标准流程

### 步骤 1: 会话回顾
- 使用 `session_search` 搜索本周会话
- 提取关键词：学习、分析、创建、优化
- 识别重要知识点和决策

### 步骤 2: 知识提取

**从会话中提取**：
1. **新学知识点** → fact_store
2. **完整方法论** → MemPalace
3. **可复用流程** → Skills
4. **重要决策** → fact_store（带时间戳）

### 步骤 3: 记忆归档

**fact_store 归档规则**：
```python
fact_store(
  action="add",
  content="关键事实",
  category="general|project|tool|user_pref",
  tags="关键词1,关键词2"
)
```

**MemPalace 归档规则**：
```python
mcp_mempalace_mempalace_add_drawer(
  wing="learning|project|reference",
  room="主题分类",
  content="完整内容",
  source_file="来源"
)
```

### 步骤 4: 过时数据清理

**清理对象**：
- 临时任务状态（已完成）
- 过时的会话上下文
- 重复的 fact_store 条目

**清理方法**：
```python
# 检查 fact_store 状态
fact_store(action="list")

# 删除过时条目
fact_store(action="remove", fact_id=XX)

# MemPalace 检查
mcp_mempalace_mempalace_status()
```

### 步骤 5: 输出周报

```markdown
# 📚 本周知识复盘 | YYYY年MM月DD日

## ✅ 新增知识

### 技能
- [Skill名称] - 一句话描述

### 知识点
- [知识点1] - [分类]
- [知识点2] - [分类]

## 📊 记忆系统状态

| 系统 | 条目数 | 状态 |
|------|--------|------|
| fact_store | XX | 健康 |
| MemPalace | XX drawers | 健康 |
| Skills | XX | 健康 |

## 🧹 清理内容

- 删除过时条目：X 条
- 合并重复内容：X 组

## 📌 下周计划

- [ ] 待学习主题
- [ ] 待优化流程

---
复盘时间：YYYY-MM-DD
下次复盘：YYYY-MM-DD
```

## 已知陷阱

### ⚠️ 重复归档
- **表现**：同一知识点多次归档
- **原因**：未检查是否已存在
- **解决**：归档前先用 `mcp_mempalace_mempalace_check_duplicate` 检查

### ⚠️ 过度清理
- **表现**：误删有价值的信息
- **原因**：未评估信息的长期价值
- **解决**：清理前先备份，遵循"7天原则"（7天内可能用到的保留）

### ⚠️ 格式混乱
- **表现**：归档内容格式不统一
- **原因**：未遵循标准格式
- **解决**：使用 `skill-authoring-guide` 的模板

## 验证清单

- [ ] 本周会话已回顾
- [ ] 新知识已提取
- [ ] 归档格式统一
- [ ] 重复内容已合并
- [ ] 过时数据已清理
- [ ] 周报已输出

## 定时配置

**推荐时间**：每周日 21:00

```bash
hermes cron create "0 21 * * 0" --skill knowledge-review-weekly --target weixin
```

## 相关技能

- `hierarchical-memory-system` - 分层记忆系统
- `neat-freak` - 会话结束知识清理
- `skill-authoring-guide` - Skill 创作指南
