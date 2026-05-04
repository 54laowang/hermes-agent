# 自进化系统完整架构

> 本文档补充说明 L6 层（双层自演进）的完整实现细节

---

## 核心文件位置

```
~/.hermes/hermes-agent/agent/
├── self_evolution_agent.py      (15KB) — 主控制器
├── self_evolution_feedback.py   (12KB) — 反馈捕获引擎
├── self_evolution_mining.py     (14KB) — 模式挖掘引擎
├── self_evolution_optimizer.py  (14KB) — 规则优化引擎
├── self_evolution_healing.py    (12KB) — 自愈引擎
└── self_evolution_predictor.py  (13KB) — 意图预测引擎
```

---

## 进化生命周期

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Observe │────▶│ Discover│────▶│ Improve │
└─────────┘     └─────────┘     └─────────┘
      ▲              │               │
      │              ▼               ▼
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Predict │────▶│ Recover │◀────│ Measure │
└─────────┘     └─────────┘     └─────────┘
```

---

## 五大核心能力

### 1. Feedback Capture（反馈捕获）

**职责**：观察每次交互，记录成功/失败

**数据结构**：
```python
@dataclass
class InteractionRecord:
    timestamp: float
    session_id: str
    turn_id: str
    user_message: str
    detected_intent: str
    tools_used: List[str]
    success_rating: int  # 0=失败, 1=部分成功, 2=完全成功
    tokens_saved: int
    latency_ms: float
```

**存储位置**：SQLite 数据库 (`/tmp/self_evolution_db`)

---

### 2. Pattern Mining（模式挖掘）

**职责**：发现重复模式，识别优化机会

**触发条件**：
- 同类交互出现 ≥3 次
- 成功率波动 > 20%
- 新工具使用模式出现

**输出**：`DiscoveredPattern` 对象，包含：
- 模式描述
- 出现频率
- 关联工具
- 潜在优化方向

---

### 3. Rule Optimization（规则优化）

**职责**：改进路由规则，提升准确率

**优化策略**：
- Hill-climbing 搜索
- A/B 测试验证
- 保留最优规则

**触发条件**：
- 每 50 次交互触发一次进化周期
- 准确率 < 60% 时立即优化

---

### 4. Self-Healing（自愈）

**职责**：检测异常自动恢复

**健康检查**：
- 响应时间监控
- 错误率追踪
- 工具可用性检测

**恢复机制**：
- 自动重试（最多 3 次）
- 降级到备用方案
- 记录异常日志

---

### 5. Intent Prediction（意图预测）

**职责**：预测用户意图，提前准备

**预测模型**：
- 基于历史交互的模式匹配
- 上下文感知
- 置信度评分

**应用场景**：
- 预加载相关工具
- 提前准备上下文
- 优化响应时间

---

## Darwin Skill（自主优化器）

**位置**：`~/.hermes/skills/darwin-skill/`

**设计哲学**：
1. **单一可编辑资产** — 每次只改一个 SKILL.md
2. **双重评估** — 结构评分（静态）+ 效果验证（实测）
3. **棘轮机制** — 只保留改进，自动回滚退步
4. **独立评分** — 子agent评分，避免偏差
5. **人在回路** — 每次优化需用户确认

### 8维度评分 Rubric（总分100）

| 维度 | 权重 | 说明 |
|------|------|------|
| Frontmatter质量 | 8 | name规范、description完整 |
| 工作流清晰度 | 15 | 步骤明确、有输入/输出 |
| 边界条件覆盖 | 10 | 异常处理、fallback |
| 检查点设计 | 7 | 关键决策前确认 |
| 指令具体性 | 15 | 可直接执行、有示例 |
| 资源整合度 | 5 | references路径正确 |
| 整体架构 | 15 | 结构清晰、无冗余 |
| 实测表现 | 25 | 跑测试prompt验证 |

### 优化流程

```
Phase 0: 初始化 → 扫描skills、创建git分支
Phase 1: 评估 → 结构分析 + 实测验证
Phase 2: 改进 → hill-climbing搜索
Phase 3: 验证 → 子agent独立评分
Phase 4: 确认 → 用户确认后merge
Phase 5: 回滚 → 退步自动回滚
Phase 6: 卡片 → 生成可视化结果
```

---

## 效果数据（Generic Agent 论文）

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| Token 消耗 | 20万 | 10万 | -50% |
| 运行时间 | 102s | 66s | -35% |
| SOP-bench 准确率 | - | 100% | ✅ |
| Lifelong AgentBench | - | 100% | ✅ |

**Team Skills 额外效果**：
- 协作能力：单 Agent → 多 Agent 团队
- 复用性：从零开始 → 80% 复用
- 自演进：固化 → 持续优化

---

## 与记忆系统的关系

```
L6 双层自演进
    ├─ 团队技能层演进 → 调用 L4 Skills 系统
    └─ 成员技能层演进 → 调用 L3 长期记忆

L5 Context Memory
    └─ 为自进化提供任务上下文数据

L4 全息记忆
    └─ 存储进化补丁 (evolution_patches.json)

L3 知识归档
    └─ 存储优化经验、最佳实践

L2 短期记忆
    └─ 临时交互数据用于模式挖掘

L1 会话记忆
    └─ 实时反馈数据来源
```

---

## 使用方式

### 自动模式

自进化系统默认启用，无需手动触发：
- 每 50 次交互自动运行进化周期
- 准确率下降时自动优化
- 异常时自动修复

### 手动触发

```bash
# 查看 Darwin Skill 评分
hermes darwin score <skill-name>

# 手动优化 Skill
hermes darwin optimize <skill-name>

# 查看进化历史
hermes evolution history
```

---

## 配置选项

在 `~/.hermes/config.yaml` 中：

```yaml
self_evolution:
  enabled: true
  evolution_cycle_interval: 50  # 每 N 次交互触发进化
  optimize_threshold: 0.6       # 准确率低于此值时立即优化
  auto_healing: true            # 启用自愈
  prediction_enabled: true      # 启用意图预测
  
darwin:
  auto_confirm: false           # 是否自动确认优化（建议关闭）
  max_iterations: 10            # 单次优化最大迭代次数
  test_prompts: 2               # 每个skill测试prompt数量
```

---

## 参考资源

- **Generic Agent 论文**：Self-Evolving Agent Architecture
- **Darwin Skill GitHub**：https://github.com/alchaincyf/darwin-skill
- **Hermes 官方文档**：https://hermes-agent.nousresearch.com/docs
