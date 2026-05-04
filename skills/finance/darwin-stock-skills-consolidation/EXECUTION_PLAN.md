# 达尔文股票 Skills 整合 - 执行计划

**创建时间**: 2026-05-02 10:06  
**执行周期**: 7 天（2026-05-02 ~ 2026-05-09）  
**当前阶段**: Phase 1 已完成 ✅

---

## 📋 执行时间表

### Week 1: 完整整合周期

| 日期 | 阶段 | 任务 | 预计耗时 | 状态 |
|------|------|------|---------|------|
| **05-02** | Phase 1 | 现状评估与分类 | 2h | ✅ 已完成 |
| **05-03** | Phase 2.1 | stock-data-acquisition 整合 | 4h | ⏳ 待开始 |
| **05-04** | Phase 2.2 | stock-analysis-framework 整合 | 6h | ⏳ 待开始 |
| **05-05** | Phase 2.3 | grid-trading-system + market-intelligence 整合 | 6h | ⏳ 待开始 |
| **05-06** | Phase 3.1 | stock-data-acquisition 达尔文补充 | 4h | ⏳ 待开始 |
| **05-07** | Phase 3.2 | stock-analysis-framework 达尔文补充 | 4h | ⏳ 待开始 |
| **05-08** | Phase 3.3 | grid-trading + market-intelligence 达尔文补充 | 4h | ⏳ 待开始 |
| **05-09** | Phase 4 | 验证与迭代 | 4h | ⏳ 待开始 |

**总预计耗时**: 34 小时

---

## ✅ Phase 1: 现状评估与分类（已完成）

**完成时间**: 2026-05-02 10:05  
**输出文档**: `darwin-stock-skills-consolidation/SKILL.md`

### 已完成工作

1. ✅ 分析 13 个股票相关 Skills
2. ✅ 评估每个 Skill 的完整度
3. ✅ 确定整合优先级
4. ✅ 生成详细的整合计划
5. ✅ 创建功能映射表
6. ✅ 设计四层架构（数据获取 → 分析研判 → 交易执行 → 监控预警）

### 关键发现

- **平均完整度**: 40%（严重不足）
- **达标 Skills**: 仅 2 个（15%）
- **功能重叠**: 5 个 Skills 存在重叠
- **缺失检查点**: 11 个 Skills 缺少检查点
- **缺失异常处理**: 10 个 Skills 缺少异常处理

---

## 🔄 Phase 2: 功能整合与去重（下一步）

### Phase 2.1: stock-data-acquisition（预计 05-03）

**整合来源**:
- `us-stock-data-acquisition-sop`（553 行）
- `a-share-trading-calendar`（269 行）
- `stock-price-cache` ✅（591 行，已优化）
- `stock-watcher` ✅（266 行，基本完成）

**核心任务**:
1. 读取 4 个 Skills 的内容
2. 提取核心功能模块
3. 去除重复代码
4. 统一 API 接口
5. 整合到新 Skill
6. 编写集成测试

**预计产出**:
- 新 Skill: `stock-data-acquisition/SKILL.md`（~1,200 行）
- 测试脚本: `stock-data-acquisition/tests/test_integration.py`
- 功能验证报告

---

### Phase 2.2: stock-analysis-framework（预计 05-04）

**整合来源**:
- `a-share-market-analysis`（319 行）
- `st-companies-financial-analysis-cn`（119 行）
- `stock-analysis`（490 行）
- `elder-trading-for-a-living`（494 行）
- `geopolitical-commodity-analysis`（257 行）
- `vibe-trading-integration`（398 行）

**核心任务**:
1. 合并 A股分析和通用股票分析
2. 整合 ST 公司专项分析
3. 整合艾尔德三重滤网系统
4. 整合地缘政治分析
5. 集成 Vibe-Trading 平台
6. 统一分析框架

**预计产出**:
- 新 Skill: `stock-analysis-framework/SKILL.md`（~1,500 行）
- 分析模板库
- 功能验证报告

---

### Phase 2.3: grid-trading-system + market-intelligence-system（预计 05-05）

**grid-trading-system 整合来源**:
- `grid-trading-monitor`（608 行）
- `elder-trading-for-a-living`（风险管理部分）

**market-intelligence-system 整合来源**:
- `daily-market-brief`（291 行）
- `supervisor-mode-auto-trigger`（400 行）
- `stock-watcher`（预警部分）

**核心任务**:
1. 分离网格交易和风险控制
2. 分离监控和预警功能
3. 整合推送接口
4. 统一配置格式

**预计产出**:
- 新 Skill: `grid-trading-system/SKILL.md`（~800 行）
- 新 Skill: `market-intelligence-system/SKILL.md`（~900 行）
- 功能验证报告

---

## 🧬 Phase 3: 达尔文补充

### 检查点设计模板

```markdown
【检查点 N】检查点名称

**触发条件**: 何时执行此检查
**检查内容**: 
- [ ] 检查项 1
- [ ] 检查项 2
- [ ] 检查项 3

**验证方法**: 如何验证检查通过
**失败处理**: 检查失败时的处理方式
```

### 异常处理模板

```markdown
### 异常场景：异常名称

**触发条件**: 何时触发此异常
**错误表现**: 异常的具体表现
**处理策略**: 
1. 第一步处理
2. 第二步处理
3. 降级方案

**相关代码**:
```python
try:
    # 正常逻辑
except ExceptionType as e:
    # 异常处理
```
```

### 边界条件模板

```markdown
### 边界条件：边界名称

**约束项**: 具体约束
**最小值**: X
**最大值**: Y
**默认值**: Z
**调整建议**: 如何调整此边界
```

---

## 📊 进度跟踪

### 每日进度更新

**2026-05-02**:
- ✅ Phase 1 完成
- ✅ 创建整合计划文档
- ✅ 设计四层架构
- ✅ 确定整合优先级

**2026-05-03**（计划）:
- ⏳ Phase 2.1: stock-data-acquisition 整合
- ⏳ 读取 4 个源 Skills
- ⏳ 去重与整合
- ⏳ 编写测试

---

## 🎯 下一步行动

### 立即执行（05-03）

1. **读取 stock-price-cache**（已优化，作为基础）
   ```bash
   skill_view(name="stock-price-cache")
   ```

2. **读取 us-stock-data-acquisition-sop**
   ```bash
   skill_view(name="finance/us-stock-data-acquisition-sop")
   ```

3. **读取 a-share-trading-calendar**
   ```bash
   skill_view(name="finance/a-share-trading-calendar")
   ```

4. **读取 stock-watcher**
   ```bash
   skill_view(name="stock-watcher")
   ```

5. **创建新 Skill 结构**
   ```bash
   mkdir -p ~/.hermes/skills/stock-data-acquisition
   ```

6. **开始整合**
   - 提取核心功能
   - 去除重复代码
   - 统一 API 接口
   - 编写 SKILL.md

---

## 📝 备注

### 暂停与恢复

如果中途需要暂停，记录当前进度：
```bash
# 记录当前状态
echo "Phase 2.1 进行中，已完成 50%" > ~/.hermes/darwin-progress.txt

# 恢复时查看
cat ~/.hermes/darwin-progress.txt
```

### 风险预警

如果遇到以下情况，立即停止并报告：
- ❌ 功能丢失或回退
- ❌ 性能严重下降（> 50%）
- ❌ 大量测试失败（> 30%）
- ❌ 用户反馈强烈不适

---

**执行计划版本**: v1.0  
**最后更新**: 2026-05-02 10:06  
**负责人**: Hermes Agent  
**用户**: 54laowang
