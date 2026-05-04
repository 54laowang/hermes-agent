---
name: github-trending-ai-project-analysis
description: 分析GitHub Trending上热门AI项目，提取星数增长、核心功能、项目关系对比
author: auto-generated
category: research
---

# GitHub Trending AI项目分析技能

## 描述
分析GitHub上热门快速增长的AI项目，提取关键信息（星数、Fork、增长趋势、核心功能、项目关系对比），用于技术趋势调研。

## 流程步骤

### 1. 定位项目
- 用户询问项目时，先通过web_search确认正确的仓库地址和用户名（用户可能记错用户名/拼写）
- 常见项目名称变体：`oh-my-claudecode` vs `oh-my-claude-code`，实际仓库在 `Yeachan-Heo/oh-my-claudecode`
- 不要直接使用用户给出的错误用户名，先搜索确认

### 2. 获取基础数据
- 使用 `browser_navigate` 访问GitHub仓库主页
- 从页面快照读取星数和Fork数，注意：未登录状态下星数在链接文本中（如 `Star 29.7k`）
- 如果vision多次读取不一致，优先相信browser_snapshot的结构化文本输出

### 3. 提取README内容
- 通过 `browser_scroll` 向下滚动到README区域
- 使用 `browser_vision` 提取核心信息：
  - 项目定位和标语
  - 核心功能和编排模式
  - 与其他类似项目的关系
  - 迁移路径和兼容性

### 4. 项目关系梳理
- 对于继承/演进关系项目（如 `oh-my-claudecode` 是 `Claude-Code-Game-Studios` 的继任者），必须明确说明：
  - 谁是谁的下一代
  - 迁移兼容性
  - 定位差异（垂直领域 vs 通用领域）
  - 维护状态差异

### 5. 对比输出
整理为Markdown表格对比，包括：
- 基础数据（星数、Fork、最近更新）
- 定位差异
- 适用场景推荐

## 常见陷阱

1. **用户名错误**：用户常记不住正确作者，比如oh-my-claudecode作者是Yeachan-Heo，不是zhzyker，必须先搜索确认
2. **星数读取错误**：vision AI容易看错数字（把29.7k看成283或2829），需要交叉验证browser_snapshot
3. **项目关系混淆**：oh-my-claudecode不是另一个独立于CCGS的项目，而是CCGS的下一代演进项目

## 验证要点
- 确认星数在browser_snapshot中的显示
- 确认项目关系在README中的明确迁移说明
- 确认最近提交时间反映活跃程度

## 输出模板

```markdown
# 📊 项目名称深度解析

---

## 📈 项目基础数据

| 指标 | 数值 |
|------|------|
| **GitHub地址** | [作者/项目](url) |
| **Stars** | ⭐ X.Xk |
| **Forks** | 🍴 X.Xk |
| **最近更新** | X天前 |

---

## 🎯 项目定位

...

---

## 🏗️ 核心功能

...

---

## 🔗 与其他项目的关系

...

---

## 🆚 对比

| 维度 | 项目A | 项目B |
|------|-------|-------|
| ... | ... | ... |

---

## 💡 总结

...
```
