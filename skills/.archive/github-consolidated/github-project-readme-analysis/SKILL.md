---
name: github-project-readme-analysis
description: 快速获取并结构化分析 GitHub 项目 README，处理各种访问限制，生成清晰的项目分析报告
author: Hermes
---

# GitHub 项目 README 分析技能

## 描述
快速获取并分析 GitHub 项目的 README 内容，提取关键信息生成结构化报告。处理各种 GitHub 访问限制情况，确保能获取到完整的 README。

## 步骤

1. **初步搜索**：先用 `web_search` 获取项目基础信息确认仓库地址
2. **尝试提取**：先用 `web_extract` 尝试提取内容，如果失败继续
3. **直接 curl 获取**：对于 GitHub raw README，使用 `terminal curl` 直接获取，这通常能绕过各种访问限制
4. **结构化整理**：将 README 内容整理为分析报告，包括：
   - 项目概况（地址、版本、Star/Fork、协议、技术栈）
   - 核心功能表格
   - 技术架构分析
   - 安装方式（提供主要方案）
   - 更新活跃度评估
   - 许可说明
   - 总结优缺点

## 处理 GitHub 访问问题的经验

- GitHub HTML 页面常常被截断或需要登录，不要依赖浏览器快照
- `web_extract` 可能被 GitHub 反爬虫拦截
- **最佳方案**：直接用 `curl https://raw.githubusercontent.com/<user>/<repo>/main/README.md` 在终端获取，稳定可靠
- 如果 main 分支不行，尝试 master 分支

## 输出格式要求

使用 Markdown 标题和表格，保持结构清晰，重点突出：
- 项目概况
- 核心功能（表格形式）
- 技术架构
- 安装方式（代码块）
- 更新热度
- 许可说明
- 总结优缺点

## 特殊项目类型：AI 编程代理工具

对于 Claude Code、Cursor、jcode 等 AI 编程代理项目，需要额外的分析维度：

### 5 维度分析框架
1. **性能与资源效率**：内存占用、启动速度、多会话扩展性
2. **Provider 生态系统**：支持的模型、认证方式、多账号管理
3. **核心差异化功能**：记忆系统、多代理协作、工具集成
4. **配置管理复杂度**：配置文件格式、环境变量、GUI 工具支持
5. **目标用户画像**：适合谁、不适合谁、迁移成本

### 关键源码文件
- `src/config.rs` - Provider 配置结构、认证方式
- `src/cli/provider_init.rs` - 登录流程、支持的 Provider
- `docs/` 目录 - 架构文档、功能说明

### 详细分析方法
参见 `references/ai-coding-agent-analysis.md`，包含：
- 完整的 5 维度分析流程
- 性能数据提取技巧
- Provider 支持分析方法
- 配置文件格式研究
- 与竞品对比模板
- 常见陷阱和最佳实践

## 适用场景

用户要求"帮我看看这个 GitHub 项目"、"分析一下 XXX 项目"等查询。

**特殊场景**：
- AI 编程代理项目（Claude Code、Cursor、jcode 等）：使用 5 维度框架
- 包含性能 benchmark 的项目：优先提取对比数据
- 配置复杂的项目：详细说明配置方式和优先级
