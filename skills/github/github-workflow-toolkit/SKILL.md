---
name: github-workflow-toolkit
description: |
  GitHub 工作流工具集 - 项目分析、趋势追踪、知识管理等 GitHub 相关任务。
  包含项目 README 分析、趋势项目追踪、知识库同步等功能。
version: 1.0.0
category: github
keywords:
  - github
  - trending
  - readme
  - analysis
  - knowledge
  - stats
---

# GitHub 工作流工具集

## 工具分类

### 项目分析

| 工具 | 功能 |
|------|------|
| `github-project-readme-analysis` | README 结构化分析 |
| `github-trending-stats` | 获取趋势项目统计 |
| `github-trending-ai-project-analysis` | AI 项目趋势分析 |
| `github-trending-ai-game-projects` | AI 游戏项目趋势 |
| `github-knowledge-tracker` | 知识库追踪与定期更新 |

---

## 核心功能

### 1. 项目 README 分析

快速获取并结构化分析 GitHub 项目 README：

- 项目概述提取
- 功能特性列表
- 安装使用说明
- 技术栈识别
- 对比分析

**使用场景：**
- 快速了解项目
- 技术选型评估
- 项目对比分析

### 2. 趋势项目追踪

获取 GitHub Trending 热门项目：

- 按语言筛选
- 按时间范围（今日/本周/本月）
- 星数增长分析
- 项目关系对比

**使用场景：**
- 技术趋势发现
- 开源项目推荐
- 学习资源收集

### 3. AI 项目专项分析

针对 AI 领域项目的深度分析：

- 技术方向分类
- 创新点识别
- 社区活跃度
- 应用场景评估

### 4. 知识库同步

从 GitHub 仓库提取知识并定期更新：

- 提示词库维护
- 模板库同步
- 动态资源追踪

---

## 使用示例

### 分析项目 README

```python
# 调用 github-project-readme-analysis
# 输入: 项目 URL
# 输出: 结构化分析报告
```

### 获取趋势项目

```python
# 调用 github-trending-stats
# 参数: language, since, spoken_language
# 输出: 趋势项目列表
```

### 追踪知识库更新

```python
# 调用 github-knowledge-tracker
# 配置: repo_url, update_interval
# 输出: 变更检测 + 更新通知
```

---

## 与其他技能协作

- `github-pr-workflow` - PR 生命周期管理
- `github-issues` - Issue 管理
- `github-repo-management` - 仓库管理
- `github-auth` - 认证配置
- `github-code-review` - 代码审查

---

## 配置要求

- GitHub Token（可选，用于提高 API 限额）
- `gh` CLI 工具（推荐）

```bash
# 配置 GitHub CLI
gh auth login

# 或设置 Token
export GITHUB_TOKEN=your_token
```
