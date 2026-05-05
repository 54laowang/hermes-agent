---
name: darwin-skill
description: "Darwin Skill (达尔文.skill): autonomous skill optimizer inspired by Karpathy's autoresearch. Evaluates SKILL.md files using an 8-dimension rubric (structure + effectiveness), runs hill-climbing with git version control, validates improvements through test prompts, and generates visual result cards. Use when user mentions \"优化skill\", \"skill评分\", \"自动优化\", \"auto optimize\", \"skill质量检查\", \"达尔文\", \"darwin\", \"帮我改改skill\", \"skill怎么样\", \"提升skill质量\", \"skill review\", \"skill打分\"."
---

# Darwin Skill

> 借鉴 Karpathy autoresearch 的自主实验循环，对 skills 进行持续优化。
> 核心理念：**评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚 → 生成成果卡片**
> GitHub: https://github.com/alchaincyf/darwin-skill

---

## 设计哲学

autoresearch 的精髓：
1. **单一可编辑资产** — 每次只改一个 SKILL.md
2. **双重评估** — 结构评分（静态分析）+ 效果验证（跑测试看输出）
3. **棘轮机制** — 只保留改进，自动回滚退步
4. **独立评分** — 评分用子agent，避免「自己改自己评」的偏差
5. **人在回路** — 每个skill优化完后暂停，用户确认再继续

与纯结构审查的区别：不只看 SKILL.md 写得规不规范，更看改完后**实际跑出来的效果是否更好**。

---

## 评估 Rubric（8维度，总分100）

### 结构维度（60分）— 静态分析

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 1 | **Frontmatter质量** | 8 | name规范、description包含做什么+何时用+触发词、≤1024字符 |
| 2 | **工作流清晰度** | 15 | 步骤明确可执行、有序号、每步有明确输入/输出 |
| 3 | **边界条件覆盖** | 10 | 处理异常情况、有fallback路径、错误恢复 |
| 4 | **检查点设计** | 7 | 关键决策前有用户确认、防止自主失控 |
| 5 | **指令具体性** | 15 | 不模糊、有具体参数/格式/示例、可直接执行 |
| 6 | **资源整合度** | 5 | references/scripts/assets引用正确、路径可达 |

### 效果维度（40分）— 需要实测

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 7 | **整体架构** | 15 | 结构层次清晰、不冗余不遗漏、与花叔生态一致 |
| 8 | **实测表现** | 25 | 用测试prompt跑一遍，输出质量是否符合skill宣称的能力 |

### 评分规则
- 维度1-7：每个维度打 1-10 分，乘以权重得到该维度得分
- 维度8（实测表现）：跑2-3个测试prompt，按输出质量打1-10分
- **总分 = Σ(维度分 × 权重) / 10**，满分100
- 改进后总分必须 **严格高于** 改进前才保留

### 关于「实测表现」维度

这是与纯结构评分最大的区别。评分方式：

1. 为每个skill设计2-3个**典型用户prompt**（不是边缘case，是最常见的使用场景）
2. 用子agent执行：一个带skill跑，一个不带skill跑（baseline）
3. 对比输出质量，从以下角度打分：
   - 输出是否完成了用户意图？
   - 相比不带skill的baseline，质量提升明显吗？
   - 有没有skill引入的负面影响（过度冗余、跑偏、格式奇怪）？

如果无法跑子agent（时间/资源限制），可以退化为「干跑验证」：读完skill后模拟一个典型prompt的执行思路，判断流程是否合理。但要在results.tsv中标注 `dry_run`。

---

## 自主优化循环

### Phase 0: 初始化

```
1. 确认优化范围：
   - 全部skills → 扫描 .claude/skills/*/SKILL.md
   - 指定skills → 用户指定列表
2. 创建 git 分支：auto-optimize/YYYYMMDD-HHMM
3. 初始化 results.tsv（如不存在）
4. 读取现有 results.tsv 了解历史优化记录
```

### Phase 0.5: 测试Prompt设计

在评估之前，为每个skill设计测试prompt。这步很关键——没有测试prompt，「实测表现」维度就打不了分。

```
for each skill:
  1. 读取 SKILL.md，理解它做什么
  2. 设计2-3个测试prompt，覆盖：
     - 最典型的使用场景（happy path）
     - 一个稍复杂或有歧义的场景
  3. 保存到 skill目录/test-prompts.json：
     [
       {"id": 1, "prompt": "用户会说的话", "expected": "期望输出的简短描述"},
       {"id": 2, "prompt": "...", "expected": "..."}
     ]
```

展示所有测试prompt给用户，**确认后再进入评估**。测试prompt的质量决定了优化方向是否正确。

### Phase 1: 基线评估（Baseline）

```
for each skill in 优化范围:

  # 结构评分（主agent可以做）
  1. 读取 SKILL.md 全文
  2. 按维度1-7逐项打分（附简短理由）

  # 效果评分（用子agent做，独立于主agent）
  3. 对每个测试prompt，spawn子agent：
     - with_skill: 带着SKILL.md执行测试prompt
     - baseline: 不带skill执行同一prompt
  4. 对比两组输出，打维度8的分

  # 汇总
  5. 计算加权总分
  6. 记录到 results.tsv
```

**如果子agent不可用**（超时、环境限制），维度8用干跑验证打分，标注 `dry_run`。不要因为跑不了测试就跳过这个维度——哪怕是模拟推演也比完全不看效果好。

基线评估完成后，展示评分卡：

```
┌──────────────────────────┬───────┬──────────────┬──────────────┐
│ Skill                    │ Score │ 结构短板      │ 效果短板      │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ huashu-proofreading      │ 78    │ 边界条件      │ 测试prompt2  │
│ huashu-slides            │ 72    │ 指令具体性    │ baseline持平  │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ 平均                     │ 75    │              │              │
└──────────────────────────┴───────┴──────────────┴──────────────┘
```

**暂停等用户确认，再进入优化循环。**

### Phase 2: 优化循环

用户确认后，按基线分数从低到高排序，先优化最弱的。

```
for each skill:
  round = 0
  while round < MAX_ROUNDS (默认3):
    round += 1

    # Step 1: 诊断
    找出得分最低的维度（结构或效果都算）

    # Step 2: 提出改进方案
    针对最低维度，生成1个具体改进方案：
      - 改什么（具体段落/行）
      - 为什么改（对应rubric哪条）
      - 预期提升多少分

    # Step 3: 执行改进
    编辑 SKILL.md
    git add + commit（message: "optimize {skill}: {改进摘要}"）

    # Step 4: 重新评估
    - 结构维度：主agent重新打分
    - 效果维度：spawn独立子agent重跑测试prompt（关键！不能自己评自己）

    # Step 5: 决策
    if 新总分 > 旧总分:
      status = "keep"，更新旧总分
    else:
      status = "revert"
      git revert HEAD（创建新commit回滚，不用reset --hard）
      记录失败尝试到 results.tsv
      break  # 该skill到瓶颈，跳到下一个

    # Step 6: 日志
    results.tsv 追加行

  # === 每个skill优化完后的人类检查点 ===
  展示该skill的改动摘要：
    - git diff（改前 vs 改后）
    - 分数变化（哪些维度提升/下降）
    - 测试prompt输出对比（如果跑过的话）
  等用户确认 OK 再继续下一个skill。
  如果用户说"不好"，回滚到该skill的优化前版本。
```

### Phase 2.5: 探索性重写（可选）

当 hill-climbing 连续2个skill都在 round 1 就 break（涨不动）时，提议一次「探索性重写」：

```
1. 选一个瓶颈skill
2. git stash 保存当前最优版本
3. 从头重写SKILL.md（不是微调，是重新组织结构和表达方式）
4. 重新评估
5. if 重写版 > stash版: 采用重写版
   else: git stash pop 恢复
```

这解决了 hill-climbing 的局部最优问题——有时候需要「先拆后建」才能突破瓶颈。
**必须征得用户同意后才执行。**

### Phase 3: 汇总报告

```
## 优化报告

### 总览
- 优化skills数：N
- 总实验次数：M
- 保留改进：X（Y%）
- 回滚次数：Z
- 实测验证：A次完整测试 / B次干跑

### 分数变化
┌──────────────────────────┬────────┬────────┬────────┐
│ Skill                    │ Before │ After  │ Δ      │
├──────────────────────────┼────────┼────────┼────────┤
│ huashu-proofreading      │ 78     │ 87     │ +9     │
│ huashu-slides            │ 72     │ 83     │ +11    │
├──────────────────────────┼────────┼────────┼────────┤
│ 平均                     │ 75     │ 85     │ +10    │
└──────────────────────────┴────────┴────────┴────────┘

### 主要改进
1. [skill-A] 补充了边界条件处理，测试输出质量提升明显
2. [skill-B] 重组了workflow结构，baseline对比优势增大
```

---

## results.tsv 格式

```tsv
timestamp	commit	skill	old_score	new_score	status	dimension	note	eval_mode
2026-03-31T10:00	baseline	huashu-proofreading	-	78	baseline	-	初始评估	full_test
2026-03-31T10:05	a1b2c3d	huashu-proofreading	78	84	keep	边界条件	补充fallback	full_test
2026-03-31T10:10	b2c3d4e	huashu-proofreading	84	82	revert	指令具体性	过度细化	dry_run
```

新增 `eval_mode` 列：`full_test`（跑了子agent测试）或 `dry_run`（模拟推演）。
文件位置：`.claude/skills/darwin-skill/results.tsv`

---

## 优化策略库

按优先级排序，每轮只做最高优先级的一个：

### P0: 效果问题（实测发现的）
- 测试输出偏离用户意图 → 检查skill是否有误导性指令
- 带skill比不带还差 → skill可能过度约束，考虑精简
- 输出格式不符合预期 → 补充明确的输出模板

### P1: 结构性问题
- Frontmatter缺少触发词 → 补充中英文触发词
- 缺少Phase/Step结构 → 重组为线性流程
- 缺少用户确认检查点 → 在关键决策处插入

### P2: 具体性问题
- 步骤模糊（"处理图片"）→ 改为具体操作和参数
- 缺少输入/输出规格 → 补充格式、路径、示例
- 缺少异常处理 → 补充 "如果X失败，则Y"

### P3: 可读性问题
- 段落过长 → 拆分+用表格
- 重复描述 → 合并去重
- 缺少速查 → 添加TL;DR或决策树

---

## 异常与边界条件

流程假设环境理想，但实操常遇异常。以下预定义 fallback，保证优化过程不会「一跑就卡住」。

| 场景 | 触发条件 | 处理动作 |
|---|---|---|
| 不在 git 仓库 | `git rev-parse` 失败 | 提示用户「建议 git init」；若拒绝，用 `cp SKILL.md SKILL.md.bak.YYYYMMDD-HHMM` 文件备份代替 revert |
| results.tsv 缺失 | 文件不存在 | 新建并写表头行（9列：含 eval_mode） |
| results.tsv 损坏 | 列数不匹配 / 非TSV | 备份为 `.bak.YYYYMMDD-HHMM` 后重建，告知用户 |
| 分支已存在 | `git checkout -b` 失败 | 分支名末尾加 `-2` / `-3`；第3次失败则切回现有分支并询问继续还是新起 |
| `git revert` 失败 | 冲突 / 工作树脏 | 先 `git stash`，重试；仍失败则从上一个 commit 的 SKILL.md 读出覆盖当前文件手动恢复 |
| MAX_ROUNDS 触顶（默认3） | 已跑3轮仍有短板 | 不强制 break，展示当前最弱维度问用户「继续加1轮 / 进入Phase 2.5 / 收工」 |
| 优化后超 150% 体积 | 新文件 > 原 × 1.5 | 拒绝提交，回到改进步骤精简（删冗余/合并重复），再评 |
| test-prompts.json 已存在 | 文件已在 skill 目录 | 默认复用并展示，问用户「复用 / 重写 / 追加」三选一 |
| SKILL.md 找不到 | 目录存在但无 SKILL.md | 该 skill 终止，results.tsv 记 `status=error`，继续下一个 |
| 分数计算规则 | 浮点精度漂移 | 总分保留 1 位小数，改进需严格 > 旧分（不靠四舍五入） |

**原则**：异常先告知用户，再按规则处理；绝不静默跳过或静默失败。

---

## 约束规则

1. **不改变skill的核心功能和用途** — 只优化"怎么写"和"怎么执行"，不改"做什么"
2. **不引入新依赖** — 不添加skill原本没有的scripts或references文件
3. **每轮只改一个维度** — 避免多个变更导致无法归因
4. **保持文件大小合理** — 优化后SKILL.md不应超过原始大小的150%
5. **尊重花叔风格** — 中文为主、简洁为上
6. **可回滚** — 所有改动在git分支上，用git revert而非reset --hard
7. **评分独立性** — 效果维度必须用子agent或至少干跑验证，不能在同一上下文里「改完直接评」

---

## 使用方式

### 全量优化（推荐首次使用）
```
用户："优化所有skills"
→ Phase 0-3 完整流程
→ 建议：先基线评估，选择分数最低的5-10个重点优化
```

### 单个优化
```
用户："优化 huashu-slides 这个skill"
→ 只对指定skill执行 Phase 0.5-2
```

### 仅评估不改
```
用户："评估所有skills的质量"
→ 只执行 Phase 0.5-1（设计测试prompt + 基线评估），不进入优化循环
```

### 查看历史
```
用户："看看skill优化历史"
→ 读取并展示 results.tsv
```

### Skills 整合（Darwin Consolidation）
```
用户："整合股票相关的skills"
→ 基于达尔文进化方法论整合多个Skills为少数核心Skills
→ 四大原则：自然选择、渐进优化、功能特化、生态平衡
```

**整合流程**（参考 `darwin-stock-skills-consolidation` 实践）：

1. **Phase 1: 现状评估与分类**
   - 分析所有相关 Skills 的功能重叠
   - 评估每个 Skill 的完整度
   - 确定整合优先级
   - 生成详细的整合计划

2. **Phase 2: 功能整合与去重**
   - 按模块整合（数据获取 → 分析研判 → 交易执行 → 监控预警）
   - 去除重复代码
   - 统一 API 接口
   - 创建新的核心 Skills

3. **Phase 3: 文档补充与优化**（根据实际完成度调整）
   - **如果 Skills 已达 100% 完整度**：
     - 添加真实使用案例（每个 Skill 3-5 个）
     - 创建协同使用最佳实践文档
     - 创建快速入门指南
     - 创建常见问题 FAQ
   - **如果 Skills 完整度不足**：
     - 添加检查点（每个 Skill 20+ 个）
     - 添加异常处理（每个 Skill 15+ 处）
     - 添加边界条件（每个 Skill 20+ 项）
     - 验证完整度达到 100%

4. **Phase 4: 验证与迭代**
   - 运行集成测试（建议在周末休市场景验证边界条件）
   - 收集用户反馈
   - 发现改进点并按优先级修复（P0 > P1 > P2）
   - 更新文档

**Skills 整合经验教训**（2026-05-02 更新）：

**关键发现**：整合过程中容易遗漏用户实际使用的核心视角/方法论

**预防措施**（Phase 1 必须执行）：
1. **整合前询问用户**：明确询问是否有特定的分析视角/方法论需要保留
   - 示例话术：「这次整合涉及 XX 个 Skills，请问有哪些核心分析框架/视角是你日常使用的？是否需要特别保留？」
2. **检查原始 Skills 的独特价值**：每个 Skill 至少有一个核心差异化能力，整合时必须保留
   - 建立清单：`| Skill名称 | 核心能力 | 是否保留 | 理由 |`
3. **用户验证环节**：整合完成后主动询问是否遗漏重要内容
   - 示例话术：「整合已完成，请确认是否有遗漏的核心视角/方法论？」

**Phase 4 验证清单**（新增）：
- [ ] 用户实际使用的核心方法论是否保留？
- [ ] 多视角分析框架是否明确区分逻辑差异？
- [ ] 协同决策树是否建立？
- [ ] 用户是否确认无遗漏？

**案例**：stock-analysis-framework v1.0.0 整合时遗漏了：
- 爱在冰川周期筹码思维（周期四阶段、位置性价比公式）
- 淘股吧游资视角（龙头识别、情绪周期、溢价率）

**用户反馈**：「艾尔德，冰川，淘股吧视角有整合到里面吗，这些视角和逻辑有所不同，需详细推理判断」

**修复成本**：v2.0.0 补充了 276 行代码（+31%），新增 3 个检查点，耗时 30 分钟

**最佳实践**：
- 整合不仅仅是代码去重，更是**保留核心分析框架**
- 多视角分析框架必须明确区分逻辑差异（核心逻辑、适用场景、时间周期、风险偏好）
- 建立协同决策树，明确各视角的调用顺序和协作关系
- **用户使用的方法论 = 核心资产，不可遗漏**

**成功案例**（2026-05-02）：
- 整合 4 个 Skills → 1 个核心 Skill（stock-data-acquisition）
- 完整度提升：75% → 100%（+33%）
- 代码精简：1,679 行 → 918 行（-45%）
- 检查点：48 → 20（精简高效）
- 异常处理：28 → 34（+21%）
- 边界条件：40 → 21（去重整合）

详见：`~/.hermes/skills/finance/darwin-stock-skills-consolidation/`

**完整实践案例**: 
- `references/darwin-stock-skills-consolidation-practice.md` — 达尔文整合方法论完整实践
- `references/three-perspectives-integration-case.md` — 三大视角整合遗漏修复案例（2026-05-02）
- `references/2026-05-03-darwin-consolidation-practice.md` — Finance & Engineering 整合实战记录（2026-05-03）
- `references/2026-05-03-finance-short-term-optimization.md` — Finance/股票类短期优化实践（2026-05-03）

---

## 实战案例（2026-05-03 更新）

### 案例1：Finance 类整合

**整合前**：19个 Finance Skills
**整合后**：10个（新建 2 个核心框架）
**精简率**：47%
**检查点**：629 个集中管理

**核心成果**：
- `stock-analysis-framework`（36 检查点）- 整合A股分析、ST研判、技术分析、量化回测、地缘政治、风险管理、行为金融七大模块
- `finance-corporate-analysis`（143 检查点）- 整合财务核算、建模、预算、创业融资、风控、发票税务六大模块

**关键经验**：
1. 企业财务类 Skills 可按职能分层整合（核算层→分析层→规划层→创业层→风控层→合规层）
2. 三视角分析框架（艾尔德+爱在冰川+淘股吧）是核心竞争力，必须保留并强化
3. 已有完整框架的 Skills（如 stock-data-acquisition）无需重复整合

---

### 案例2：Engineering 类整合

**整合前**：33个 Engineering Skills
**整合后**：17个（新建 9 个核心框架，保留 8 个独立）
**精简率**：48%
**检查点**：450 个框架

**9 大核心框架**：
1. engineering-reliability-operations（60 检查点）- SRE/故障响应/DevOps
2. engineering-data-platforms（40 检查点）- 数据管线/湖仓架构
3. engineering-security-practices（45 检查点）- 应用安全/威胁检测
4. engineering-embedded-systems（50 检查点）- 固件/Linux驱动
5. engineering-integration-development（55 检查点）- 钉钉/飞书/微信
6. engineering-code-quality（35 检查点）- 代码审查/最小差异
7. engineering-architecture-design（50 检查点）- 系统架构/后端架构
8. engineering-frontend-fullstack（45 检查点）- 前端/移动端/原型
9. engineering-specialized-domains（70 检查点）- CMS/IoT/区块链/语音AI/硬件

**关键经验**：
1. Engineering 类 Skills 差异性大（前端/后端/嵌入式/AI/安全），适合按职能分组
2. 框架模板批量创建能节省 80% 时间
3. 专业领域类（CMS/IoT/区块链/FPGA）可合并为一个综合框架
4. 部分 Skills 因专业性强、无重叠，应保留独立（如 AI工程、数据库优化、Git工作流）

**整合效率数据**：
- 分析时间：约 15 分钟（33个 Skills 分析分组）
- 框架创建：约 10 分钟（9个框架模板批量生成）
- 归档标记：约 5 分钟（25个源 Skills 批量归档）
- 总耗时：约 30 分钟
- 节省时间：相比逐个优化（预计 3-4 小时），节省 85%

**质量指标**：
- 精简率：48%（达到目标 ≥40%）
- 检查点完整性：平均 50个/Skill（达到目标 ≥30个）
- 模块化程度：3-5模块/Skill（达到目标 ≥3模块）
- 文档完整性：框架 100%（内容待补充）

---

## 设计灵感

> "You write the goals and constraints in program.md; let an agent generate and test code deltas indefinitely; keep only what measurably improves the objective."
> — Karpathy, autoresearch

本skill的对应关系：
- **program.md** → 本文件（评估rubric和约束规则）
- **train.py** → 每个SKILL.md
- **val_bpb** → 8维加权总分（含实测表现）
- **git ratchet** → 只保留有改进的commit
- **test set** → 每个skill的test-prompts.json

区别：增加了人在回路（autoresearch是全自主的，skill优化需要人的判断力），以及双重评估机制（结构+效果），因为skill的「好坏」比loss数值更微妙。

---

## 成果卡片生成（Result Card）

每个skill优化完成后（或全量汇总后），自动生成视觉成果卡片，截图保存为PNG。

### 卡片模板

模板位置：`templates/result-card.html`

3种风格，每次随机选择一种：

| 风格 | CSS类 | URL hash | 视觉特点 |
|------|--------|----------|---------|
| Warm Swiss | `.theme-swiss` | `#swiss` | 暖白底+赤陶橙，Inter字体，干净网格 |
| Dark Terminal | `.theme-terminal` | `#terminal` | 近黑底+荧光绿，等宽字体，扫描线 |
| Newspaper | `.theme-newspaper` | `#newspaper` | 暖白纸+深红，衬线字体，双栏编辑风 |

### 生成流程

```
1. 复制 templates/result-card.html 到临时工作文件
2. 用 sed/编辑工具 替换占位数据：
   - data-field="skill-name" → 实际skill名
   - data-field="score-before/after/delta" → 实际分数
   - 8个维度的 dim-bar-before/after width → 实际百分比
   - data-field="improvement-1/2/3" → 实际改进摘要
   - data-field="date" → 当前日期
3. 随机选择风格：hash 设为 swiss/terminal/newspaper 之一
4. 用 scripts/screenshot.mjs 截图（2x 高清，只截 .card 元素，自动 open 图片）：
   node scripts/screenshot.mjs /abs/path/to/card.html /abs/path/to/output.png
   # 回退方案（脚本失败时）：
   npx playwright screenshot "file:///path/to/card.html#[theme]" \
     output.png --viewport-size=960,1280 --wait-for-timeout=2000
5. 提示用户查看成果卡片 PNG

### 资源文件速查

| 路径 | 用途 |
|---|---|
| `templates/result-card.html` | 3风格主模板（swiss/terminal/newspaper，hash切换） |
| `templates/result-card-dark.html` / `-white.html` | 单一风格替代模板（需要锁定风格时用） |
| `scripts/screenshot.mjs` | 2x 高清截图，只截 .card，自动 open |
| `results.tsv` | 历次优化日志（9列含 eval_mode） |
| `{skill目录}/test-prompts.json` | 每个 skill 的测试 prompt 集（用于维度8实测） |
```

### 何时生成

- **单skill卡片**：每个skill优化完成后，展示该skill的分数变化
- **总览卡片**：全部优化完成后（Phase 3），展示全局战绩

### 品牌元素

- 顶部：Darwin.skill 品牌标识 + 日期
- 底部：「Train your Skills like you train your models」+ github.com/alchaincyf/darwin-skill
