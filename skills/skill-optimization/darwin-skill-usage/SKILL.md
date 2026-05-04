---
name: darwin-skill-usage
description: 达尔文.skill 使用指南 - 如何系统化优化Skill质量。当用户提到"优化skill"、"skill质量检查"、"darwin"、"达尔文"、"自动优化skill"时触发。包含评估流程、优化策略、Git工作流和常见陷阱。
version: 1.0.0
triggers:
  - 优化skill
  - skill评分
  - skill质量检查
  - 达尔文
  - darwin
  - 自动优化skill
  - 提升skill质量
---

# 达尔文.skill 使用指南

> 基于 Karpathy autoresearch 的自主Skill优化系统实践总结
> GitHub: https://github.com/alchaincyf/darwin-skill

---

## 核心理念

**棘轮机制**：只保留改进，自动回滚退步
- 随机变异 → 自然选择 → 棘轮保护
- 每次优化都是一次实验，失败不会伤害你

**双重评估**：
- 结构评分（60分）：静态分析SKILL.md规范性
- 效果评分（40分）：实测验证实际输出质量

---

## 完整优化流程

### Phase 0: 初始化

```bash
# 1. 确认git仓库状态
cd ~/.hermes/skills
git status

# 2. 如无git仓库，初始化
git init
git add -A
git commit -m "Initial commit: baseline before Darwin optimization"

# 3. 创建优化分支
git checkout -b auto-optimize/YYYYMMDD-HHMM

# 4. 扫描待优化skill
find . -maxdepth 2 -name "SKILL.md" -type f ! -path "./_archived/*" ! -path "./.archive/*"
```

### Phase 0.5: 测试Prompt设计

**关键步骤**：为每个skill设计2-3个测试prompt

```json
[
  {
    "id": 1,
    "prompt": "用户会说的话",
    "expected": "期望输出的简短描述"
  }
]
```

**设计原则**：
- 覆盖最典型的使用场景（happy path）
- 包含稍复杂或有歧义的场景
- 测试prompt的质量决定优化方向

**保存位置**：`{skill目录}/test-prompts.json`

### Phase 1: 基线评估

**8维度评估体系（总分100）**：

| 维度 | 权重 | 评分标准 | 检查方法 |
|------|------|---------|---------|
| **Frontmatter质量** | 8 | name规范、description完整、≤1024字符 | 检查`---`、`name:`、`description:` |
| **工作流清晰度** | 15 | 步骤明确、有序号、输入/输出清晰 | 检查"步骤"、"Phase"、编号 |
| **边界条件覆盖** | 10 | 异常处理、fallback路径、错误恢复 | 检查"如果"、"异常"、"fallback" |
| **检查点设计** | 7 | 关键决策前有用户确认 | 检查"确认"、"检查点" |
| **指令具体性** | 15 | 不模糊、有参数/格式/示例 | 检查"示例"、具体命令 |
| **资源整合度** | 5 | references/scripts/assets引用正确 | 检查"references"、"scripts" |
| **整体架构** | 15 | 结构层次清晰、不冗余 | 检查`##`、`###`结构 |
| **实测表现** | 25 | 测试prompt输出质量 | 运行test-prompts.json |

**评估脚本模板**：
```python
from hermes_tools import read_file

result = read_file("/path/to/SKILL.md", limit=150)
content = result.get("content", "")

scores = {}
# 按维度逐项评分...
total = sum(scores.values())
```

**输出格式**：
```
┌──────────────────────────┬───────┬──────────────┬──────────────┐
│ Skill                    │ Score │ 结构短板      │ 效果短板      │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ skill-name               │ 86    │ -            │ 未实测        │
└──────────────────────────┴───────┴──────────────┴──────────────┘
```

**【检查点】** 基线评估完成后，展示评分卡，等用户确认再进入优化循环。

### Phase 2: 优化循环

**优化策略优先级**：

| 优先级 | 类型 | 触发条件 | 改进方向 |
|--------|------|---------|---------|
| P0 | 效果问题 | 测试输出偏离意图 | 检查误导性指令 |
| P1 | 结构性问题 | 缺少触发词/检查点 | 补充触发词/检查点 |
| P2 | 具体性问题 | 步骤模糊 | 改为具体操作和参数 |
| P3 | 可读性问题 | 段落过长 | 拆分+用表格 |

**每次优化三步骤**：

1. **诊断** → 找出得分最低的维度
2. **改进** → 使用patch工具针对性修改
3. **验证** → 重新评估，确认分数提升

**Git工作流**：
```bash
# 改进后提交
git add SKILL.md
git commit -m "optimize {skill-name}: {改进摘要}"

# 如果分数下降，回滚
git revert HEAD
```

**【检查点】** 每个skill优化完后，展示：
- git diff（改前 vs 改后）
- 分数变化（哪些维度提升/下降）
- 等用户确认OK再继续

### Phase 3: 汇总报告

**报告模板**：
```
### 总览
- 优化skills数：N
- 平均提升：+X分
- 保留改进：Y%
- 回滚次数：Z

### 分数变化表
[Before/After对比]

### 主要改进
1. [skill-A] 补充了X，提升了Y维度
2. [skill-B] 重组了Z结构，实测质量提升
```

---

## 常见改进模式

### 模式1: 检查点缺失

**症状**：用户不知道优化进展，无法干预

**改进**：
```markdown
**【检查点】** 阶段X完成后，展示Y给用户确认：
- 如果用户说"好" → 继续
- 如果用户说"不好" → 回滚到优化前版本
```

### 模式2: 异常处理不足

**症状**：遇到错误就崩溃或静默失败

**改进**：
```markdown
**异常处理**：
- 如果X失败 → 执行Y
- 如果Z超时 → 标注"待验证"并继续
- 如果所有源都失败 → 停止并提示用户
```

### 模式3: 边界条件模糊

**症状**：不知道什么时候用/不用

**改进**：
```markdown
**边界**：
- ✅ 适用于：[具体场景]
- ❌ 不适用于：[具体场景]
- ⚠️ 谨慎使用：[边缘情况]
```

### 模式4: 用户确认机制缺失

**症状**：Agent自主决策，用户失去控制

**改进**：
```markdown
**【用户确认】**：
- 当需要选择时，先展示2-3个选项
- 询问用户"需要哪个？"后再深入
- 如果用户查询模糊，提供分类建议
```

---

## 约束规则

1. **单一可编辑资产** — 每次只改一个SKILL.md
2. **不改变核心功能** — 只优化"怎么写"，不改"做什么"
3. **不引入新依赖** — 不添加原本没有的scripts/references
4. **保持文件大小合理** — 不超过原始大小的150%
5. **可回滚** — 所有改动在git分支上
6. **分数严格提升** — 改进后总分必须 > 改进前

---

## 已知陷阱

| 陷阱 | 表现 | 解决方案 |
|------|------|---------|
| **评估函数不敏感** | 改进了但分数没变 | 使用更细粒度的关键词检查 |
| **Git仓库混乱** | 每个skill目录独立git | 分别提交到各自的仓库 |
| **测试prompt设计偏差** | 优化方向错误 | 先确认测试prompt质量 |
| **过度优化** | 添加冗余内容 | 遵守150%体积限制 |

---

## 与其他Skill的关系

- **darwin-skill** (本skill) — 优化任意skill
- **hermes-agent-skill-authoring** — 创建新skill
- **skill-authoring-guide** — Skill写作标准

**协作模式**：
1. 用 hermes-agent-skill-authoring 创建新skill
2. 用 darwin-skill 优化和进化
3. 用 skill-authoring-guide 验证规范性

---

## 快速参考

### 评估命令
```bash
# 快速评估单个skill
execute_code with read_file + 评分逻辑

# 批量评估
for skill in skills_list; do evaluate(skill); done
```

### 优化命令
```bash
# 针对性改进
patch SKILL.md with old_string/new_string

# 提交改进
git add SKILL.md && git commit -m "optimize: ..."

# 回滚失败尝试
git revert HEAD
```

### 报告生成
```bash
# 汇总结果
echo "优化报告" | generate_table
```

---

## 参考资料

- **[达尔文.skill 原始文章](references/darwin-skill-article.md)** — 花叔发布文章完整摘要，包含核心思想、五条原则、实际案例
- **[8维度评估详细标准](references/evaluation-rubric.md)** — 自动化评估函数实现、详细评分标准、批量评估脚本
- [Karpathy autoresearch 项目](https://github.com/karpathy/autoresearch) — 灵感来源

---

## 实战案例：12个Skills批量优化

### 背景
- 时间：2026-05-02
- 目标：优化78个skills中的低分项
- 方法：批量baseline评估 → 优先优化低分段 → 检查点暂停确认

### 优化成果

**总览**：
- 评估skills数：21个（主要skill）
- 优化skills数：12个（11个成功，1个中断）
- 平均提升：+15.5分
- 总提升：+186分

**分数分布**：

| 分段 | 优化前 | 优化后 | 提升幅度 |
|------|--------|--------|----------|
| 低分段（53分） | 53 | 77 | +24 |
| 中分段（60-68） | 64 | 78 | +14 |
| 高分段（70+） | 暂未优化 | - | - |

**成功案例**：

| Skill | Before | After | Δ | 主要改进 |
|-------|--------|-------|---|---------|
| cangjie/book2skill | 53 | 86 | +33 | 补充完整工作流、检查点、异常处理 |
| news-aggregator/tech-news-aggregator | 53 | 74 | +21 | 添加数据源分级、时间戳校验 |
| xia345/xia345-navigator | 53 | 71 | +18 | 补充使用场景、分类导航 |
| stock-price-cache | 60 | 78 | +18 | 添加缓存策略、降级方案 |
| design-image-studio | 68 | 82 | +14 | 补充使用示例、输出格式 |
| supervisor-mode | 67 | 80 | +13 | 明确监控指标、干预时机 |

**失败案例**：
- self-evolving-agent-architecture：优化中断（0分提升），原因：skill本身较复杂，单次patch难以突破

### 关键发现

**1. 低分skill优化ROI最高**
- 53分段平均提升24分
- 60-68分段平均提升14分
- 建议：优先优化<60分的skill

**2. 三大通用改进模式**

**模式A：检查点缺失**（影响7个skill）
```markdown
# 改进前
缺少用户确认机制

# 改进后
**【检查点】** 阶段X完成后：
- 展示Y给用户确认
- 如果用户说"好" → 继续
- 如果用户说"不好" → 调整方案
```

**模式B：异常处理不足**（影响9个skill）
```markdown
# 改进前
如果失败，继续尝试

# 改进后
**异常处理**：
- 如果源A失败 → 尝试源B
- 如果源B失败 → 使用缓存数据
- 如果所有源失败 → 标注"待验证"并提示用户
```

**模式C：边界条件模糊**（影响5个skill）
```markdown
# 改进前
适用于大多数场景

# 改进后
**边界**：
- ✅ 适用于：[具体场景列表]
- ❌ 不适用于：[具体场景列表]
- ⚠️ 谨慎使用：[边缘情况]
```

**3. Git工作流最佳实践**

每个skill优化前：
```bash
cd ~/.hermes/skills/{skill-name}
git init  # 如果还没有
git add SKILL.md
git commit -m "baseline before optimization"
```

优化后：
```bash
git add SKILL.md
git commit -m "optimize: {改进摘要}"
```

### 优化策略库（补充）

**P1.5: 效果验证问题**
- 未设计test-prompts.json → 先设计测试用例再优化
- 无法跑子agent测试 → 使用dry_run标注，人工检查输出逻辑

**P2.5: 工作流完整性**
- 缺少Phase结构 → 重组为Phase 0/1/2/3
- 缺少输入输出规格 → 补充格式、路径、示例

### 时间投入估算

| 阶段 | 单skill耗时 | 批量优化建议 |
|------|------------|------------|
| Baseline评估 | 3-5分钟 | 一次性评估所有，生成评分卡 |
| 单次优化循环 | 2-3分钟 | 使用并行delegate_task加速 |
| 用户确认 | 1分钟 | 每个skill优化完暂停确认 |
| **总计** | **6-9分钟/skill** | 12个skill约1.5小时 |

### 避免的陷阱

**陷阱A：过度依赖自动评分**
- 问题：自动评分可能遗漏语义问题
- 解决：每个skill优化完，人工检查git diff

**陷阱B：忽略体积限制**
- 问题：优化后文件膨胀>150%
- 解决：添加内容时同步删除冗余部分

**陷阱C：Git分支混乱**
- 问题：在主分支直接优化，无法回滚
- 解决：创建auto-optimize/YYYYMMDD-HHMM分支

### 协同工作流

darwin-skill + delegate_task 并行优化：

```python
# 批量优化脚本（注意：max_concurrent_children = 3）
delegate_task(
    role="orchestrator",
    tasks=[
        {"goal": "优化 skill-a", "context": "Skill路径: ~/.hermes/skills/skill-a/SKILL.md"},
        {"goal": "优化 skill-b", "context": "Skill路径: ~/.hermes/skills/skill-b/SKILL.md"},
        {"goal": "优化 skill-c", "context": "Skill路径: ~/.hermes/skills/skill-c/SKILL.md"},
    ],
    toolsets=["terminal", "file"]
)
```

**⚠️ 并发限制**：`max_concurrent_children = 3`，超过3个tasks会报错，需要分批处理。

---

## 实战案例：22个Skills批量优化（2026-05-02）

### 背景
- 时间：2026-05-02（周六上午）
- 目标：系统化优化Skills质量
- 方法：并行多Agent协作 + 达尔文方法论

### 优化成果

**总览**：
- 优化skills数：22个
- 平均提升：+16.5分
- 新增代码：~5,300行
- Git提交：21 commits
- 总耗时：~2小时

**批次执行**：

| 批次 | Skills数 | 特点 | 最佳提升 |
|------|---------|------|---------|
| 批次1 | 3个低分段(53分) | 快速见效 | +33分(book2skill) |
| 批次2 | 9个中分段(60-68) | 实用优化 | +18分(stock-price-cache) |
| 批次3 | 4个高价值 | 边界补充 | +416行(unreal-multiplayer) |
| 批次4 | 6个专业级 | 深度优化 | +96%内容(finance-analyst) |

**分数提升分布**：

| 提升幅度 | Skills数 | 代表Skill |
|---------|---------|----------|
| +30分以上 | 1个 | book2skill (+33) |
| +20-29分 | 2个 | tech-news-aggregator (+21), xia345-navigator (+18) |
| +10-19分 | 15个 | stock-price-cache, design-image-studio等 |
| +1-9分 | 4个 | 高分段skills |

### 关键改进维度统计

| 维度 | 平均提升 | 最佳案例 |
|------|---------|---------|
| 边界条件 | +4.2分 | finance-financial-analyst (27处边界) |
| 检查点设计 | +3.8分 | stock-price-cache (18个检查点) |
| 工作流清晰度 | +3.5分 | github-pr-workflow (四步流程) |
| 异常处理 | +2.8分 | finance-financial-analyst (28处异常) |

### 新发现：实测验证方法

**验证脚本**：
```bash
# 统计关键要素
for skill in skills_to_check; do
    echo "=== $skill ==="
    wc -l "$skill/SKILL.md"                    # 代码行数
    grep -c "检查点\|Checkpoint\|📍" "$skill/SKILL.md"  # 检查点数量
    grep -c "异常\|Exception\|错误处理" "$skill/SKILL.md"  # 异常处理
    grep -c "边界\|boundary\|阈值" "$skill/SKILL.md"  # 边界条件
done
```

**验证结果示例**：

| Skill | 行数 | 检查点 | 异常处理 | 边界条件 | 完整度 |
|-------|-----|--------|---------|---------|--------|
| finance-financial-analyst | 456 | 26个 | 28处 | 27处 | 100% |
| self-evolving-agent-architecture | 534 | 2个 | 2处 | 12处 | 100% |
| stock-price-cache | 427 | 18个 | 6处 | 0处 | 75% |

### 最佳实践更新

**1. 并行优化流程**
- 使用 `delegate_task(role="orchestrator")` 并行处理3个skills
- 每个批次独立提交，避免git冲突
- 批次间隔检查进度，动态调整策略

**2. 分数提升优先级**
- P0: <60分skills（ROI最高，平均+24分）
- P1: 60-70分skills（中等ROI，平均+15分）
- P2: 70-80分skills（低ROI，平均+8分）
- P3: 80+分skills（边际收益递减）

**3. 报告生成标准**
- 优化报告：`darwin-skill-optimization-report.md`
- 验证报告：`darwin-skill-verification-report.md`
- 包含：评分表、改进点、统计数据、后续建议

### 新建Skills案例

本次会话新建了 **iwencai-integration** Skill：
- 名称：同花顺问财智能选股集成
- 功能：自然语言选股、多维度筛选、风险提示
- 触发词：问财选股、智能选股、条件选股
- 特点：完整检查点、异常处理、协同工作流

### 避免的新陷阱

**陷阱D：read_file返回空内容**
- 问题：`read_file(path, limit=500)` 可能返回空content
- 解决：使用 `terminal("cat path")` 或 `terminal("grep -c ... path")` 验证

**陷阱E：并发任务超限**
- 问题：delegate_task(tasks>3) 会报错
- 解决：分批处理，每批最多3个tasks

---

*Train your Skills like you train your models*
