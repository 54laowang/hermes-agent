---
name: a股-workflow
description: 从成功会话中自动提取的工作流程
version: 1.0.0
category: auto-generated
created_from: session_20260430_031953
trigger_keywords: ["A股", "数据分析"]
tools_required: ["web_extract", "web_search"]
---

# a股-workflow

## 触发条件

关键词: A股, 数据分析

## 工作流程

### 步骤 1: 搜索相关信息

**工具**: `web_search`

**参数模式**:
```json
{
  "query": "A股大盘 2026-04-30"
}
```

**成功标志**: 任务完成

### 步骤 2: 提取网页内容

**工具**: `web_extract`

**参数模式**:
```json
{
  "urls": [
    "https://..."
  ]
}
```

**成功标志**: 任务完成

## 约束条件

- 必须验证时间戳

## 原始目标

分析今日A股大盘走势，判断市场状态

## 使用方式

按 `/` 键，输入 `a股-workflow` 即可调用。

## 持续优化

使用后如有改进建议，运行：
```python
from tools.skill_refinement import refine_skill_from_feedback
refine_skill_from_feedback("a股-workflow", feedback="...")
```
