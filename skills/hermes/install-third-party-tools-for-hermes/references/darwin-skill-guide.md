# 达尔文.skill 参考文档

> 来源：https://mp.weixin.qq.com/s/4ICQJGwa2MD616_oFmJb4w  
> GitHub: https://github.com/alchaincyf/darwin-skill  
> 作者：花叔  
> 发布时间：2026-04-13

## 核心概念

达尔文.skill 是一个让 Skill 系统自主进化的元技能，灵感来自 Karpathy 的 autoresearch 项目。

**核心理念**：评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚 → 生成成果卡片

## 五条核心原则

### 1. 单一可编辑资产
- 每次只改一个 SKILL.md
- 避免同时修改多个 skill 导致无法判断因果关系

### 2. 双重评估
- **结构评分**（60分）：静态分析 SKILL.md 质量
- **效果评分**（40分）：实测表现，跑测试 prompt 看输出

### 3. 棘轮机制
- 分数只升不降
- 改差了 git revert，当这次修改没发生过
- 只有成功会被保留

### 4. 独立评分
- 改 skill 的 agent ≠ 评分的 agent
- 避免「自己改自己评」的认知偏差
- 类似萨班斯法案的审计独立性

### 5. 人在回路
- 机器做初筛，人做终审
- 每个skill优化完后暂停，用户确认再继续

## 8维度评估体系（100分制）

### 结构维度（60分）— 静态分析

| # | 维度 | 权重 | 评分标准 |
|---|------|------|----------|
| 1 | Frontmatter质量 | 8 | name规范、description包含做什么+何时用+触发词、≤1024字符 |
| 2 | 工作流清晰度 | 15 | 步骤明确可执行、有序号、每步有明确输入/输出 |
| 3 | 边界条件覆盖 | 10 | 处理异常情况、有fallback路径、错误恢复 |
| 4 | 检查点设计 | 7 | 关键决策前有用户确认、防止自主失控 |
| 5 | 指令具体性 | 15 | 不模糊、有具体参数/格式/示例、可直接执行 |
| 6 | 资源整合度 | 5 | references/scripts/assets引用正确、路径可达 |

### 效果维度（40分）— 需要实测

| # | 维度 | 权重 | 评分标准 |
|---|------|------|----------|
| 7 | 整体架构 | 15 | 结构层次清晰、不冗余不遗漏、与花叔生态一致 |
| 8 | **实测表现** | 25 | 用测试prompt跑一遍，输出质量是否符合skill宣称的能力 |

**关键**：实测表现权重最高（25分），因为「实际效果比纸面规范重要」

## 优化循环流程

### Phase 0: 初始化
1. 确认优化范围（全部skills / 指定skills）
2. 创建 git 分支：`auto-optimize/YYYYMMDD-HHMM`
3. 初始化 `results.tsv`
4. 读取历史优化记录

### Phase 0.5: 测试Prompt设计
- 为每个skill设计2-3个测试prompt
- 覆盖典型使用场景 + 稍复杂场景
- 保存到 `skill目录/test-prompts.json`
- **用户确认后再进入评估**

### Phase 1: 基线评估（Baseline）
- 结构评分：主agent直接打分（维度1-7）
- 效果评分：spawn独立子agent重跑测试prompt（维度8）
- 汇总加权总分
- 展示评分卡，**暂停等用户确认**

### Phase 2: 优化循环
```
for each skill:
  round = 0
  while round < MAX_ROUNDS (默认3):
    round += 1
    
    # Step 1: 诊断
    找出得分最低的维度
    
    # Step 2: 提出改进方案
    针对最低维度，生成1个具体改进方案
    
    # Step 3: 执行改进
    编辑 SKILL.md
    git add + commit
    
    # Step 4: 重新评估
    spawn独立子agent重跑测试prompt
    
    # Step 5: 决策
    if 新总分 > 旧总分:
      status = "keep"，更新旧总分
    else:
      status = "revert"
      git revert HEAD
      break
    
    # Step 6: 日志
    results.tsv 追加行
  
  # === 每个skill优化完后的人类检查点 ===
  展示改动摘要，等用户确认 OK 再继续
```

### Phase 2.5: 探索性重写（可选）
- 当 hill-climbing 连续2个skill都在 round 1 就 break 时
- 提议「探索性重写」：从头重写SKILL.md
- 解决局部最优问题
- **必须征得用户同意**

### Phase 3: 汇总
- 输出 Before/After 分数表
- 生成可视化成果卡片

## 棘轮机制详解

**示例流程**：
```
基线分数: 72

第1轮优化后 → 78 ✅ 保留
第2轮优化后 → 75 ❌ 比当前最优78低 → 回滚，有效基线还是78
第3轮优化后 → 84 ✅ 保留
第4轮优化后 → 87 ✅ 保留

最终: 72 → 87，净提升15分
```

**棘轮的美感**：
- 可以放心做实验，失败不会伤害你
- 只有成功会被保留
- 类似结构：科学理论、民主制度、git历史

## 与 autoresearch 的关系

**达尔文.skill 设计 100% 受 Karpathy autoresearch 启发**：

| autoresearch | 达尔文.skill |
|--------------|--------------|
| 优化训练代码 | 优化 SKILL.md |
| 用 loss 判断好坏 | 用 8维度加权总分判断 |
| 改好了 commit | 改好了 commit |
| 改差了 revert | 改差了 revert |
| 全自主（机器比数字） | 人在回路（人做终审） |

**关键区别**：
- autoresearch：loss 是数字，机器自己比就行
- 达尔文：skill 好坏需要人判断，加了 Human in the Loop

## 与女娲.skill 的关系

```
女娲.skill → 从0到1（造skill）
达尔文.skill → 从1到N（磨skill）
```

**闭环机制**：
- 女娲生成skill后，自动启动「Phase 5双Agent精炼」
- Agent A：达尔文8维度评估
- Agent B：skill-creator视角的触发条件评审
- 出厂就经过一轮进化

## 实际优化案例

### huashu-slides（做PPT的skill）
- **5轮优化**，改动最多
- 第1轮：style-samples引用不存在目录 → 改成可选引用
- 第2轮：补充错误处理和生成后必检清单
- 第3轮：5种风格实测，标注噪点风险分级
- 第4轮：防泄漏铁律，精简base style
- 第5轮：四项并行冲刺，目标90分
- **结果**：从「能用但随时可能翻车」→「可以去泡杯咖啡回来看结果」

### comedy（脱口秀编剧skill）
- **1轮优化**搞定
- 问题：风格选择没有结构，每次都要重新描述
- 解决：加风格选择三方案制、推荐矩阵、反默认规则
- 效果：改动不大但效果明显

### 7个perspective skill（芒格、费曼等）
- **5轮批量优化**
- 第1轮：角色扮演规则和身份卡补充
- 第2轮：扩展Frontmatter触发词和调研来源
- 第3轮：添加示例对话提升实测表现
- 第4轮：收紧触发词、加中文表达DNA适配
- 第5轮：参考内容拆分到references目录
- **结果**：从「能用」→「风格稳定、不会漂移、有自检清单」

## 与 Anthropic 官方 skill-creator 的区别

| 维度 | skill-creator | 达尔文.skill |
|------|---------------|--------------|
| 目标 | 单个skill的创建和调优 | 批量skill的质量管理和持续优化 |
| 流程 | 捕获意图→访谈→写SKILL.md→测试→迭代 | 评估→改进→实测→确认→保留/回滚 |
| 交互 | 一对一协作打磨 | 批量自主优化 + 人工终审 |
| 定位 | 手工裁缝 | 质量管理体系（QA） |

**关系**：互补
- skill-creator：创建新skill
- 达尔文：优化现有skill
- 达尔文的评估体系参考了skill-creator的标准

## 安装方法

```bash
# 一键安装
npx skills add alchaincyf/darwin-skill

# 跳过确认
npx skills add alchaincyf/darwin-skill --yes
```

**安装位置**：
- `.agents/skills/darwin-skill/`
- 符号链接到 Claude Code、OpenClaw 等平台

## 使用方法

**触发词**：
- "优化skill"
- "skill评分"
- "自动优化"
- "skill质量检查"
- "达尔文"
- "darwin"
- "帮我改改skill"
- "skill怎么样"
- "提升skill质量"
- "skill review"
- "skill打分"

**使用示例**：
```
"优化所有skills"
"用达尔文优化一下这个skill"
"给我所有skill打个分"
"我的skill质量怎么样"
```

## 核心价值

1. **自动找短板**：8维度评估，精准定位问题
2. **实测验证**：不只看结构，更看实际跑出来的效果
3. **棘轮保护**：改差了自动回滚，零风险
4. **人在回路**：机器初筛 + 人工终审，质量可控
5. **批量优化**：一次处理所有skill，效率翻倍

## 哲学启示

> **当你给任何创造性工作加上「只保留改进」的约束时，时间就站在了你这边。**

这个道理适用于：
- Skill优化
- 写作
- 做产品
- 过日子

你不需要每一步都走对，你只需要确保走错的那步不留痕迹。

---

**参考链接**：
- GitHub: https://github.com/alchaincyf/darwin-skill
- 公众号文章: https://mp.weixin.qq.com/s/4ICQJGwa2MD616_oFmJb4w
- Karpathy autoresearch: https://github.com/karpathy/autoresearch
