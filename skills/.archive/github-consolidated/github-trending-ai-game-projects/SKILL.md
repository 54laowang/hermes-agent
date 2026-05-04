---
name: github-trending-ai-game-projects
description: 分析 GitHub Trending 上热门的 AI 游戏开发项目，整理类似 Claude-Code-Game-Studios 的同类项目对比
author: Hermes
category: research
tags:
  - github
  - ai-game-dev
  - trending
  - project-analysis
---

# GitHub Trending AI 游戏开发项目分析技能

## 触发条件
用户询问 GitHub 上增长最快的 AI 游戏开发项目，或寻找类似 Claude-Code-Game-Studios 的同类项目

## 分析步骤

### 1. 定位项目
1. 首先通过 web_search 初步搜索关键词 `github增长最快的ai游戏开发项目 2026`
2. 如果搜索结果不够具体，直接导航到 `https://github.com/trending` 获取最新趋势数据
3. 使用 browser_vision 提取页面中与 AI 游戏开发相关的项目信息

### 2. 深度验证
- 对找到的热门项目逐个进入仓库页面
- 确认项目是否真的专注于 AI 游戏开发领域
- 提取核心功能、架构和数据

### 3. 分类整理
按项目类型分类：
- **完整垂直解决方案**：类似 Claude-Code-Game-Studios，开箱即用
- **通用智能体框架**：可用于游戏开发但不限于此
- **工具集合导航**：收录各类工具的目录
- **特定方向增强**：NPC 进化、资产生成等专项

### 4. 输出对比表格
为用户提供清晰对比，包含：
- 项目名称/地址
- 当前星标 / 日增星标
- 核心特点
- 与 Claude-Code-Game-Studios 的区别
- 适用场景

## 当前热门项目数据（2026年4月）

| 项目 | 星标 | 日增 | 类型 | 定位 |
|------|------|------|------|------|
| Donchitos/Claude-Code-Game-Studios | 11.8k | 311 | 完整方案 | 49 AI 智能体游戏工作室层级架构 |
| EvoMap/evolver | 4.2k | 737 | 进化引擎 | GEP 驱动 AI 智能体自我进化，适合 NPC |
| lsdefine/GenericAgent | 3.6k | 845 | 自进化 | 从种子自主生长技能树，token 减 6x |
| Yuan-ManX/ai-game-devtools | 1.1k | 稳定增长 | 工具合集 | 最全 AI 游戏开发工具导航 |
| openai/openai-agents-python | 21.8k | 625 | 基础框架 | OpenAI 官方多智能体协作框架 |

## 经验教训

1. **直接访问 GitHub Trending 比 web_search 更准确** — 通用搜索引擎结果滞后，Trending 是最新数据
2. **browser_vision 对长页面会像素超限失败** — 需要注意页面长度，太长的 README 使用滚动分段提取
3. **web_extract 对 github.com URL 可能被封禁** — 优先用 browser 方式提取
4. **很多热门"AI agent"项目不是专门做游戏的** — 需要进入仓库确认定位，避免误导用户

## 对比维度要点
用户通常想知道：
- 这个项目和 CCGCS 有什么区别？
- 我什么时候该用它？
- 增长速度如何？社区活跃度？

## 输出结构建议
1. 按热度/相关性排序
2. 每个项目包含：地址、增长数据、核心特点、区别
3. 最后给汇总对比表和趋势观察
4. 给出选择建议，帮助用户决策
