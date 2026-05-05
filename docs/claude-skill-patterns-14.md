# 14 个 Claude Skill 编写模式 - 学习笔记

**来源**: 丁光华《什点悟智》（Bilgin Ibryam 系列第三篇翻译）
**时间**: 2026-04-26
**核心价值**: Skill 触发率、Token 经济、指令校准、工作流控制

---

## 📊 全局框架：14 模式 × 5 类

| 类别 | 解决什么问题 | 模式数 | 核心痛点 |
|------|-------------|--------|----------|
| **一、发现与选择** | Skill 能不能被触发 | 2 | 触发率低 |
| **二、上下文经济** | Skill 烧多少 token | 2 | Token 浪费 |
| **三、指令校准** | 把模型管太严还是太松 | 5 | 过度约束 |
| **四、工作流控制** | 多步流程不丢步 | 3 | 跳步遗忘 |
| **五、可执行代码** | 哪些事别让模型做 | 2 | 可靠性差 |

---

## 一、发现与选择（触发率生死关）

### 🎯 模式 1：激活元数据（Activation Metadata）

**核心认知**：
> description 不是摘要，是 **唯一的触发信号**。

**生死关口**：
- 会话开始时，Claude **只看到** 所有 skill 的 `name` + `description`
- 如果在 metadata-only 环节被刷掉，后面写得再漂亮也没用

**核心动作**：description 里塞两样东西
1. **做什么**（这个 skill 干嘛的）
2. **什么时候触发**（哪些关键词、场景、用户原话）

**Anthropic 推荐技巧**：
> 写得稍微"推销"一点——因为模型有"宁可不触发也不要触发错"的保守倾向

**示例写法**：
```yaml
description: |
  AI image generation with reference images and batch processing.
  Only this skill handles text-to-image, draw, 生成图片, 画图.
  Use even when user says "generate" without explicit "image" keyword.
```

**Trade-off**：
- Claude Code: description + when_to_use ≤ 1536 字符
- 开放 Skill spec: ≤ 1024 字符
- **每一句话都在和触发词、排除词、领域关键词抢空间**

**踩坑案例**：
- 第一版写 "AI 图像生成" → 触发率低
- 第二版列出所有触发词 → 触发率立即上升

---

### 🚫 模式 2：排除条款（Exclusion Clause）

**核心认知**：
> description 只说"什么时候触发"是不够的，还要说"**什么时候别触发**"。

**Ruben Hassid 观点**：
> 这一行可能是整个 description 里最重要的一行——比正面触发词还重要。

**逻辑**：
- **正面词把 skill 拉进来**
- **排除词把它推出去**
- 两个都需要

**经典写法**：
```yaml
description: |
  Format markdown documents for technical documentation.
  Do NOT use for blog articles, newsletters, emails, tweets, or long-form content.
```

**Trade-off**：
- 维护成本高：skill 库越大，排除条款越要互相对齐
- "Do NOT use for X" —— X 到底归谁？会随时间漂移

**最佳实践**：
> 每加一个新 skill，都要回过头检查现有同类 skill 的排除条款有没有被"撞"到

---

## 二、上下文经济（Token 预算）

### 💰 模式 3：上下文预算（Context Budget）

**核心认知**：
> Claude 已经知道的东西就别再教它一遍。

**错误示范**：
```markdown
PDF 是一种由 Adobe 设计的文档格式...
```
→ Claude 知道 PDF 是什么，**这一段就是纯浪费**

**唯一准则**：
> 默认假设：Claude 是聪明的。如果删掉一段不会让一个有经验的工程师产生疑惑，那就删。

**具体准则**：
1. **术语要一致**：要么都叫 "field"，要么都叫 "box"，不要混用
2. **不要写时间敏感的措辞**："before August 2025..." 三个月后就老了
3. **不要堆背景故事**：直接说 "do X"，不要先讲 "in 2023, we used to..."

**Trade-off**：
- Sonnet 觉得简洁优雅的描述，Haiku 可能太跳
- 如果要支持多个模型，**目标是最弱的那个**

**踩坑案例**：
> 早期 yotok-skills 里有大段背景"为什么我们做这个"——后来全删了。**没有人会读，连模型都不会读全。**

---

### 📖 模式 4：渐进式披露（Progressive Disclosure）

**核心认知**：
> SKILL.md 是目录，不是百科全书。

**问题**：
- 800 行细节全塞进 SKILL.md → **每次会话不管用不用都得加载**
- 用户根本没问表单问题，但"表单字段补全"细节也跟着加载进来

**具体做法**：
```
✅ SKILL.md 控制在 500 行以内
✅ 详细内容拆到独立文件：
   - FORMS.md
   - REFERENCE.md
   - reference/finance.md
✅ 加载层次：
   metadata（每次会话）→ SKILL.md（触发时）→ 详细文件（task 引用时）
✅ 脚本放在 scripts/ 下，不会被加载到上下文
✅ 引用图保持浅：每个文件离 SKILL.md 一跳
```

**最后一招（特别强调）**：
> **长 reference 文件顶上加一个目录**
> 
> Claude 可能只读了一半就被截断，目录在最上面至少知道还有什么没读到

**Trade-off**：
- 碎片化：拆成多个文件后，作者自己都很难一眼装下整个 skill 的逻辑
- Claude 路由也会出错——把流程导向了错误的子文件，浪费一轮

---

## 三、指令校准（约束旋钮）

### 🎚️ 模式 5：控制力调校（Control Tuning）

**核心认知**：
> 指令的自由度，要匹配任务的脆弱度。

**自由度对照表**：

| 自由度 | 用什么形式 | 什么任务 |
|--------|-----------|----------|
| **高自由** | 文字指令、"用你的判断" | 代码 review（多种合理做法） |
| **中自由** | 伪代码、可参数化的脚本 | 部署 runbook（有偏好但灵活） |
| **低自由** | 精确脚本、不允许任何 flag、"do not modify" | 数据库迁移（错一步全完） |

**Tone 的作用**：
> 开头来一句 persona（"你是一个看重正确性甚于风格的资深 reviewer"）会**为整个 skill 设定判断基准**

**Trade-off**：
> **作者们会无意识地往"约束太死"那边走**——因为严格的指令感觉更安全。
> 
> 它不安全，**它只是换了一种失败方式**。

---

### 🧠 模式 6：解释 Why（Explain-the-Why）

**核心认知**：
> 不要只写规则，要写规则**为什么**这样。

**错误示范**：
```markdown
MUST use constructor injection. NEVER use field injection.
```

**正确示范**：
```markdown
Use constructor injection. Field injection breaks testability because we 
cannot mock the field without Spring context.
```

**核心差异**：
> **前者只能命中你列出来的情况，后者能让 Claude 在你没列出来的边界情况里自己判断**

**Anthropic skill-creator 建议**：
> 把全大写的 MUST/ALWAYS/NEVER 列为 "yellow flag"——看到就回头改写

**判断方式**：
> 当我开始想敲 ALWAYS 的时候，我就停下来想：
> **这条规则它如果不知道为什么，会不会用错？**
> 
> 会用错，就写出 why；不会用错，简洁就行。

**Trade-off**：
- 给每条规则加上理由会变长，token 也变多
- **对于真的很脆弱的步骤，裸指令仍然是对的**
- Prose-with-reasoning 留给"需要 Claude 自己判断"的场景

---

### 🏗️ 模式 7：模板脚手架（Template Scaffold）

**核心认知**：
> 当输出的结构很重要时——给一个填空模板。

**适用场景**：
- 报告
- commit message
- API payload
- release notes

**这些东西结构本身就有价值**。如果不给模板，Claude 每次都重新发明一个差不多但不一样的格式，下游解析器会哭。

**模板分两档**：

| 档位 | 用途 | 示例 |
|------|------|------|
| **Strict** | 机器要解析的输出 | 数据契约、API 格式 |
| **Flexible** | 人读的文档 | "这是一个合理的默认，按需调整" |

**Trade-off**：
> Strict 模板会压制掉一些边界情况下原本更好的表达。
> 
> **默认用 flexible，除非有机器在解析。**

---

### 📝 模式 8：In-Skill 示例（In-Skill Examples）

**核心认知**：
> 描述说不清"调性"的时候——上 few-shot 例子。

**Description 的局限**：
- 能告诉 Claude **结构**（commit message 要有 type prefix）
- 但说不清 **调性**（团队里的 commit 写得是简洁还是稍带情感）

**示例**：
```markdown
Input: 修复了登录页面的图标加载问题
Output: fix(login): correct icon loading on slow networks

Input: 添加了一个新的 API 用来导出 CSV
Output: feat(export): add CSV export endpoint with streaming
```

**组合使用**：
> **模板（模式 7）给的是骨架，例子给的是肉。**
> 
> 两个组合用——模板定形，例子定味。

**Trade-off**：
> 例子有偏向性。如果你给的 3 个例子都偏正式，Claude 之后产出的东西就全是正式的——哪怕用户的对话很轻松。
> 
> **例子要覆盖你想支持的全部 variation。**

---

### ⚠️ 模式 9：已知坑位（Known Gotchas）

**核心认知**：
> 把踩过的具体坑专门列一节。

**问题**：
> 只写 "happy path" 的 skill 教 Claude **该做什么**，但不教它**该警惕什么**。
> 
> 第一次撞上真实世界的边界情况——某个表单字段不存在、某条命令在 macOS 能跑但 Linux 死掉、某个库静默返回空数组——Claude 没有先验，**就开始编**。

**经典写法**：
```markdown
**Known Gotchas**:

- Scanned PDFs return [] silently. Check page type first.
- Rotated pages need `page.rotation = 0` before column extraction.
- macOS `date -d` doesn't work; use `gdate` (coreutils).
```

**核心观点**：
> **成熟 skill 里 gotchas 这一节的价值最高**。
> 
> 这一节的内容只能从"真实跑出来的失败案例"里捞——你坐在桌子前 brainstorm 是写不出来的。

**Trade-off**：
> 会过期。库会更新、API 会改——**陈旧的 gotcha 会让 Claude 去修一个其实早就修好的问题**。

---

## 四、工作流控制（不丢步）

### ✅ 模式 10：执行清单（Execution Checklist）

**核心认知**：
> 给一个 Claude 自己复制到回复里逐项打勾的 checklist。

**典型失败**：
> **Claude 在第 4 步说"I think we are done"**，但流程其实有 6 步。
> 
> 它跳了一步、不知道自己跳了哪一步、或干脆忘了在第几步。

**示例**：
```markdown
Publishing Progress:
- [ ] Step 0: Load preferences
- [ ] Step 1: Determine input type
- [ ] Step 2: Configure credentials
- [ ] Step 3: Validate metadata
- [ ] Step 4: Publish to platform
- [ ] Step 5: Verify publication
```

**核心机制**：
> 把"我在哪一步"的状态外化到对话里，Claude 自己、用户、后续轮次都能看到。

---

### 🔄 模式 11：自修正循环（Self-Correcting Loop）

**核心认知**：
> 加进迭代，"做完检查，错了再做"。

**适用场景**：
- 输出质量敏感
- 可验证性高
- 错误代价大

**经典模式**：
```
1. Generate output
2. Validate output
3. If validation fails:
   - Analyze failure
   - Generate corrected output
   - Go to step 2
4. If validation passes: done
```

**关键点**：
- **验证标准要明确**：什么叫"通过"
- **失败分析要具体**：哪里错了、为什么错
- **迭代上限要设置**：避免无限循环

---

### 📋 模式 12：Plan-Validate-Execute

**核心认知**：
> 在动手之前先产出一个**可验证的中间产物**。

**三阶段**：
1. **Plan**：产出计划（可审查）
2. **Validate**：用户/系统审查计划
3. **Execute**：执行已验证的计划

**适用场景**：
- 不可逆操作（数据库迁移、生产部署）
- 高风险操作（删除、重命名、权限变更）
- 复杂依赖操作（多服务重启、级联更新）

**示例**：
```markdown
## Plan
1. Backup database (预计 5 分钟)
2. Run migration script (预计 2 分钟)
3. Verify data integrity (预计 3 分钟)
4. Restart API service (预计 1 分钟)

**请确认执行此计划**
```

---

## 五、可执行代码（可靠性）

### 🔧 模式 13：脚本优于指令（Script Over Instruction）

**核心认知**：
> 哪些事别让模型做、丢给脚本。

**适用场景**：
- **确定性强**的操作（文件操作、数据处理）
- **可重复**的任务（构建、部署、测试）
- **有工具支持**的场景（grep、jq、curl）

**示例**：
```markdown
# 错误：让 Claude 用自然语言处理
"Parse the JSON file and extract the name field"

# 正确：给具体命令
jq '.name' config.json
```

**原因**：
- 脚本不会"忘记"参数
- 脚本不会"理解偏差"
- 脚本可复用、可测试

---

### 🧪 模式 14：可验证输出（Verifiable Output）

**核心认知**：
> 输出要能被脚本/工具验证。

**设计原则**：
1. **结构化输出**：JSON、YAML、CSV（可解析）
2. **校验字段**：必填、格式、范围
3. **验证脚本**：输出后立即验证

**示例**：
```markdown
# 生成 API 配置后验证
cat api-config.json | jq 'has("endpoint") and has("method")'
```

---

## 🎯 实战检查清单

### Skill 触发检查

```markdown
- [ ] description 包含"做什么"
- [ ] description 包含"什么时候触发"
- [ ] description 包含触发关键词（中英文）
- [ ] description 包含排除条款（Do NOT use for...）
- [ ] description 字符数 < 1024（开放 spec）/< 1536（Claude Code）
```

### Token 经济检查

```markdown
- [ ] SKILL.md < 500 行
- [ ] 删除 Claude 已知的背景知识
- [ ] 术语一致
- [ ] 无时间敏感措辞
- [ ] 详细内容拆到独立文件
- [ ] 长文件顶部有目录
```

### 指令校准检查

```markdown
- [ ] 自由度匹配任务脆弱度
- [ ] 无 MUST/ALWAYS/NEVER（除非必要）
- [ ] 关键规则解释 why
- [ ] 有模板（如输出结构重要）
- [ ] 有示例（如调性重要）
- [ ] 有 Known Gotchas 节
```

### 工作流检查

```markdown
- [ ] 长流程有 Execution Checklist
- [ ] 高风险任务有 Self-Correcting Loop
- [ ] 不可逆操作有 Plan-Validate-Execute
```

### 可靠性检查

```markdown
- [ ] 确定性任务用脚本而非指令
- [ ] 输出可被工具验证
- [ ] 关键输出有验证脚本
```

---

## 💡 核心洞见

### 1. 触发是生死关口

> Skill 的整个生命周期里有一个**生死关口**——会话开始时，Claude 只看到所有已安装 skill 的 `name` 和 `description`。
> 
> **如果一个 skill 在这个 metadata-only 的环节就被刷掉，它后面写得再漂亮也没用。**

### 2. 约束太死是普遍错误

> **作者们普遍犯的错是——约束得太死**，因为严格的指令"看上去更安全"。
> 
> 它不安全，**它只是换了一种方式失败**。

### 3. Gotchas 价值最高

> **成熟 skill 里 gotchas 这一节的价值最高**。
> 
> 这一节的内容只能从"真实跑出来的失败案例"里捞——你坐在桌子前 brainstorm 是写不出来的。

### 4. 渐进式披露是 Token 关键

> SKILL.md 是目录，不是百科全书。
> 
> 如果你把 800 行细节全塞进 SKILL.md——**每次会话不管用不用都得加载**。

### 5. 解释 Why 胜过 MUST/NEVER

> **前者只能命中你列出来的情况，后者能让 Claude 在你没列出来的边界情况里自己判断**。

---

## 📚 参考资料

- **原文**: Bilgin Ibryam《Skill Authoring Patterns from Anthropic's Best Practices》
- **翻译**: 丁光华《什点悟智》
- **系列**: Claude Code 三部曲之三
- **参考**: Ruben Hassid 关于 Exclusion Clause 的观点

---

**学习时间**: 2026-05-05
**应用价值**: 所有 Hermes Skill 编写
