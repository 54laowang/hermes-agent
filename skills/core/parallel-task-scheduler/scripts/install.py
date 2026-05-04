#!/usr/bin/env python3
"""
并行任务调度器 - 安装脚本
创建目录结构、配置使用说明
"""

import os
import sys
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"
SKILL_DIR = HERMES_DIR / "skills" / "core" / "parallel-task-scheduler"


def make_executable(path: Path):
    """给文件加执行权限"""
    mode = path.stat().st_mode
    path.chmod(mode | 0o111)


def setup_directories():
    """创建目录结构"""
    print("📁 创建目录结构...")
    
    directories = [
        SKILL_DIR / "task-templates",
        SKILL_DIR / "results",
    ]
    
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d.relative_to(Path.home())}")


def create_templates():
    """创建常用的任务模板"""
    print("\n📋 创建任务模板...")
    
    templates = {
        "research-comparison.md": """# 多方案对比调研模板

## 使用方法
```
并行执行以下 {{n}} 个调研任务：

{% for topic in topics %}
任务 {{loop.index}}：深度调研 {{topic}} 的架构、优缺点、适用场景
{% endfor %}

输出要求：
1. 每个方案用表格对比核心指标
2. 交叉验证不同方案之间的矛盾点
3. 最后给出选型建议和适用场景
```

## 常用调研主题
- 向量数据库：Pinecone / Chroma / Weaviate / Milvus
- Agent 框架：OpenClaw / Claude Code / AutoGPT / LangGraph
- 推理后端：vLLM / Text Generation Inference / Ollama
- 多模态模型：GPT-4o / Claude 3 Opus / Gemini Pro
""",
        
        "code-review-multi-angle.md": """# 多角度代码评审模板

## 使用方法
```
并行执行以下 3 个代码评审任务，最后汇总：

任务 1【安全性】：只关注安全问题、漏洞、注入风险、权限问题
任务 2【性能】：只关注性能瓶颈、时间复杂度、内存泄漏、N+1 问题
任务 3【可维护性】：只关注代码结构、命名、注释、重复代码、架构合理性

评审目标文件：{{file_path}}
```
""",
        
        "cross-validation.md": """# 信息交叉验证模板

## 使用方法
```
对同一个主题，并行让 3 个 Agent 从不同来源独立调研：

任务 1：从官方文档/技术白皮书调研 {{topic}}
任务 2：从社区/博客/Stack Overflow 调研 {{topic}} 的实际使用体验
任务 3：从 GitHub Issues/PR 调研 {{topic}} 的已知问题和限制

最后对比三个来源的信息，找出：
1. 三方共识的结论
2. 有矛盾的点
3. 被官方忽略但用户实际遇到的问题
```
""",
    }
    
    for filename, content in templates.items():
        filepath = SKILL_DIR / "task-templates" / filename
        filepath.write_text(content, encoding="utf-8")
        print(f"  ✅ {filename}")


def create_usage_guide():
    """创建使用指南"""
    usage_guide = """# 并行任务调度器 - 使用指南

## 🚀 快速开始

### 方式 1：自然语言指令（推荐）

直接跟 Hermes 说：

> "并行调研以下 3 种 AI Agent 记忆方案，最后汇总对比：
> 1. 向量数据库方案
> 2. 分层文件记忆方案
> 3. 知识图谱方案
> 
> 每个方案一个 Agent 专门调研，输出表格对比优缺点。"

### 方式 2：使用模板

复制 `task-templates/` 下的模板，填入你的任务。

---

## 📊 最佳实践

### ✅ 适合并行的任务
- [x] 多方案对比调研（3-10 倍收益）
- [x] 多角度代码评审（2-3 倍收益）
- [x] 多来源信息交叉验证（3-5 倍收益）
- [x] 翻译 + 校对 + 润色（3 倍收益）
- [x] 不同风格内容创作（2-5 倍收益）

### ❌ 不适合并行的任务
- [ ] 有强依赖关系的任务（必须先做 A 才能做 B）
- [ ] 需要上下文继承的任务
- [ ] 单一步骤、不可拆分的简单任务

---

## 🎯 推荐并行度

| 任务类型 | 推荐并行度 | 预期收益 |
|----------|-----------|---------|
| 信息调研 | 3-5 个 | 2-3 倍 |
| 代码评审 | 2-3 个 | 1.5-2 倍 |
| 交叉验证 | 3 个 | 2 倍 |
| 创意写作 | 2-5 个 | 2-4 倍 |

> 注意：并行度超过 5 以后，汇总开销会显著增加，收益边际递减。

---

## ⚡ 示例对话

### 示例 1：架构选型调研

**你：**
```
并行调研以下 4 个向量数据库：
1. Pinecone（托管）
2. Chroma（本地）
3. Weaviate（开源托管）
4. Milvus（自建）

每个 Agent 独立调研一个数据库，最后输出对比表格包含：
- 部署难度
- 查询性能
- 成本估算
- 优缺点
- 适用场景

最后给一个 500 字以内的选型建议。
```

### 示例 2：多角度代码评审

**你：**
```
对以下文件做并行代码评审：
/path/to/your/code.py

任务 1：只看安全问题
任务 2：只看性能问题
任务 3：只看可维护性问题

最后汇总所有问题，按严重程度分级。
```

---

## 🔧 高级功能

### 自定义每个 Agent 的 System Prompt

```
并行执行 3 个任务：

任务 1：
目标：调研 OpenClaw 架构
Agent 角色：你是一个开源架构师，只关注代码结构和设计模式

任务 2：
目标：调研 OpenClaw 社区生态
Agent 角色：你是一个社区运营专家，只关注 GitHub Stars、贡献者数量、生态成熟度

任务 3：
目标：调研 OpenClaw 实际落地案例
Agent 角色：你是一个技术顾问，只关注真实生产环境的使用效果和踩坑记录
```

---

## 💡 设计哲学

> **把 Agent 当"工人"，不要当"主管"。**
>
> 一个全能 Agent 什么都能做，但什么都做不快。
>
> 给它配 10 个专门的"工人 Agent"，指挥它们并行干活，它只需要做"主管"的汇总工作。
>
> 这就是人类组织效率提升的本质：分工 + 并行。
"""
    
    (SKILL_DIR / "USAGE.md").write_text(usage_guide, encoding="utf-8")
    print(f"  ✅ USAGE.md")


def main():
    print("=" * 60)
    print("   ⚡ 并行任务调度器 Parallel Task Scheduler")
    print("   安装程序")
    print("=" * 60)
    
    setup_directories()
    create_templates()
    create_usage_guide()
    
    # 给脚本加执行权限
    make_executable(SKILL_DIR / "scripts" / "parallel-scheduler.py")
    
    print("\n" + "=" * 60)
    print("   ✅ 安装完成！")
    print("=" * 60)
    print(f"""
📋 功能清单：

✅ 并行任务调度核心
   - 同时启动 N 个 sub-agent
   - 信号量控制并发度
   - 每个任务独立超时控制
   - 自动重试失败任务

✅ 结果汇总与交叉验证
   - 自动检测不同 Agent 结论的矛盾点
   - 去重与结构化输出
   - 溯源：哪个结论来自哪个 Agent

✅ 3 个任务模板
   - 多方案对比调研（research-comparison）
   - 多角度代码评审（code-review-multi-angle）
   - 信息交叉验证（cross-validation）

📚 使用方法：

直接用自然语言跟 Hermes 说即可，例如：

> "并行调研 3 种 Agent 记忆方案，最后汇总对比：
> 向量数据库、分层文件记忆、知识图谱"

> "对这个文件做并行评审：
> 任务 1 看安全，任务 2 看性能，任务 3 看可维护性"

更多示例见：~/.hermes/skills/core/parallel-task-scheduler/USAGE.md
""")


if __name__ == "__main__":
    main()
