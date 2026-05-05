# Claude Code 架构设计哲学

> **来源**：论文《Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems》(arXiv:2604.14228, 2026-04-14) + 公众号文章《撕开Claude Code真相：让它好用的98.4%，是工程不是AI》

## 核心洞察：98.4%是工程，不是AI

### 马的隐喻

> 「一匹马可以跑得很快很有力，但它自己不知道往哪儿走：整套挽具决定了它的方向。」

**类比到AI编程**：模型本身能力很强，但它不知道在你的代码库里该往哪儿走。**Harness（鞍具）就是你为它造的方向盘+刹车+导航。**

### 能力占比真相

| 维度 | 传统认知 | 实际真相 |
|------|----------|----------|
| AI能力占比 | 认为是核心 | 仅占1.6% |
| 工程架构占比 | 被忽视 | 占98.4% |
| 工程师角色 | 写代码 | 设计约束环境 |
| 提升路径 | 换更好的模型 | 优化Harness |

---

## Claude Code核心架构

### 简单的while循环

```
while True:
    1. 调用模型 (call the model)
    2. 运行工具 (run tools)
    3. 重复 (repeat)
```

**关键洞察**：核心逻辑极其简单，但**98.4%的代码**都在这个循环周围的系统。

### 5大人类价值驱动架构设计

根据论文分析，Claude Code的架构由5个人类价值驱动：

1. **人类决策权威** (Human Decision Authority)
2. **安全与保障** (Safety and Security)
3. **可靠执行** (Reliable Execution)
4. **能力放大** (Capability Amplification)
5. **上下文适应性** (Contextual Adaptability)

### 核心组件（围绕while循环）

| 组件 | 说明 | 价值映射 |
|------|------|---------|
| **权限系统** | 7种模式 + ML分类器 | 安全与保障 |
| **上下文管理** | 5层压缩管道 | 上下文适应性 |
| **扩展机制** | MCP、Plugins、Skills、Hooks | 能力放大 |
| **子代理委托** | Worktree隔离 | 可靠执行 |
| **会话存储** | Append-oriented设计 | 可靠执行 |

---

## 4种扩展机制详解

### 1. MCP (Model Context Protocol)
- **作用**：连接外部工具服务器
- **场景**：数据库查询、API调用、文件系统操作
- **示例**：GitHub集成、PostgreSQL查询、Puppeteer浏览器自动化

### 2. Plugins（插件）
- **作用**：扩展Claude Code内置能力
- **场景**：添加新的工具类型、自定义命令
- **管理**：`claude plugin install <name>`

### 3. Skills（技能）
- **作用**：自然语言触发的领域知识
- **场景**：特定任务的流程、最佳实践
- **位置**：`.claude/skills/*.md`（项目）或 `~/.claude/skills/*.md`（全局）

### 4. Hooks（钩子）
- **作用**：事件驱动的自动化
- **场景**：
  - `PreToolUse`：执行前安全检查
  - `PostToolUse`：执行后自动格式化
  - `PostToolUse`：写文件后自动lint
- **示例**：
  ```json
  {
    "PostToolUse": [{
      "matcher": "Write(*.py)",
      "hooks": [{"type": "command", "command": "ruff check --fix $CLAUDE_FILE_PATHS"}]
    }]
  }
  ```

**关键洞察**：Hook是98.4%里最有杠杆的部分——不依赖AI变聪明，依赖确定性代码做强制检查。

---

## OpenAI Frontier团队：100万行0人工实验

### 核心实践

#### 1. 层级架构强约束
```
Types → Config → Repo → Service → Runtime → UI
```
- 依赖关系单向流动
- 由linter在CI层强制执行
- Agent写出违反层级的代码？直接构建失败

#### 2. Linter错误信息即修复指令
- **普通项目**：lint错误是"violation detected"，给人看的
- **OpenAI Frontier**：lint错误是具体的修复指令，给Agent看的
- 这是最反直觉的细节

#### 3. 文档作为单一事实来源
- 所有架构图、execution plans、设计规范都在仓库内部的`docs/`目录
- Agent不需要外部知识库，一切就在repo里

---

## 今天就能做的3件事

### 1️⃣ 建立CLAUDE.md

**位置**：项目根目录

**内容**：
- 团队的架构规则
- 命名约定
- 测试要求
- 反复踩过的坑

**时间**：10分钟就能写完一个能用的版本

**心态**：下次AI犯错时，先不要手动修，而是问自己——CLAUDE.md里缺了什么？

### 2️⃣ 把重复做的事变成Skill

> 「如果你每天做某件事超过一次，把它变成skill或command。」——Boris Cherny

**应该变成Skill的事**：
- Code review
- 生成commit message
- 写发布说明
- 修一类重复的bug

**不该是**：每天手敲提示词

### 3️⃣ 在容易踩坑的地方加Hook

**核心原则**：
- 不依赖AI变聪明
- 依赖确定性代码做强制检查
- 把人类工程师的判断力翻译成机器可读约束

**这件事的核心不在写代码，而在写规则**

---

## LangChain实践案例

**变化**：模型没有换，但调整了harness
- 系统提示
- 工具
- 中间件
- 推理模式

**结果**：Terminal Bench 2.0分数从52.8提升到66.5

**启示**：不换模型，优化Harness也能显著提升效果

---

## 未来5年的能力曲线转移

> 「我已经从80%手动写代码变成了80%交给Agent写。」——Karpathy (2026-01)

**工程师价值重定义**：
- ❌ 旧范式：「我能写多少行代码」
- ✅ 新范式：「我能为AI设计多严格的工作环境」

**核心洞察**：
- 写代码的活儿正在被Agent接管
- 但设计那个让Agent能写出好代码的世界，还是人的工作
- 而且比以前更难、更重要、也更有意思

---

## 与OpenClaw对比（论文要点）

| 维度 | Claude Code | OpenClaw |
|------|-------------|----------|
| 部署环境 | CLI单进程 | Gateway控制平面 |
| 安全模型 | 每动作分类 | 边界级访问控制 |
| 循环架构 | 单一CLI循环 | Gateway内嵌运行时 |
| 扩展方式 | 上下文窗口扩展 | Gateway级能力注册 |

**启示**：同样的设计问题，在不同部署环境下会产生不同的架构答案。

---

## 6个未来设计方向（论文指出）

1. **多Agent协作编排**
2. **长期记忆与知识管理**
3. **安全边界的动态调整**
4. **上下文压缩的语义保留**
5. **人机协同的决策边界**
6. **跨会话的持续学习**

---

## 参考资料

- **论文**：[Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems](https://arxiv.org/abs/2604.14228)
- **代码仓库**：[github.com/VILA-Lab/Dive-into-Claude-Code](https://github.com/VILA-Lab/Dive-into-Claude-Code)
- **公众号文章**：《撕开Claude Code真相：让它好用的98.4%，是工程不是AI》（新智元，2026-04）
- **Karpathy推文**：https://x.com/karpathy/status/1748050645675626496

---

## 关键引用

> 「模型本身能力很强，但它不知道在你的代码库里该往哪儿走。Harness就是你为它造的方向盘+刹车+导航。」

> 「Hook是98.4%里最有杠杆的那部分——它不依赖AI变聪明，它依赖确定性代码做强制检查。这是把人类工程师的判断力翻译成机器可读约束的过程。」

> 「这件事的核心不在写代码，而在写规则。」

> 「未来五年，工程师的能力曲线正在从"我能写多少行代码"转向"我能为AI设计多严格的工作环境"。」
