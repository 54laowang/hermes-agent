---
name: hermes-full-configuration-upgrade
description: "9-step满配Hermes Agent升级流程 - 从裸装版升级为全功能超级智能体，包括SOUL人格定义、Hindsight知识图谱、RTK Token压缩、211个中文AI专家角色库、GenericAgent 4层记忆架构等完整步骤"
version: "1.2.0"
author: "Hermes Auto-Learning"
tags: [hermes, configuration, optimization, token-saving, memory, agency-agents-zh]
---

# Hermes Agent 满配升级流程

按照公众号「元小二2046」7步满配教程，将裸装Hermes升级为全功能超级智能体。

## 前置检查

```bash
# 检查当前安装状态
hermes --version
ls -la ~/.hermes/
```

## 进化1：RTK Token压缩引擎（最重要）

RTK可将终端命令输出压缩60-90%，节省大量Token。

```bash
# 检查是否已安装
which rtk && rtk --version

# 在Hermes主目录初始化
cd ~/.hermes && rtk init
```

验证：查看 `~/.hermes/CLAUDE.md` 中是否包含 `rtk-instructions` 标记。

## 进化2：SOUL.md 灵魂定义

裸装Hermes只有空模板，需要定义清晰的角色人格。

```bash
# 检查当前SOUL.md
cat ~/.hermes/SOUL.md
```

**推荐配置模板**（根据用户实际需求调整）：

```markdown
# Hermes Agent Persona

你是一位专业的AI助手，专注于**全球财经分析、A股市场研究、AI科技前沿追踪**。

## 核心特征
- 使用**简体中文**回复
- 数据驱动，严谨细致，所有市场数据必须先复核日期准确性
- 提供深度分析和专业解读，不仅仅是信息罗列
- 善于发现隐藏的关联和趋势信号

## 用户画像
- 关注：全球宏观经济、A股上市公司、AI技术突破、前沿科技项目
- 偏好：深度分析、数据可视化、系统化的知识整理
- 要求：提供市场分析必须先获取当前精确时间，判断盘前/盘后状态

## 工作准则
1. **时效性优先**：财经和科技新闻必须确认时间戳
2. **准确性至上**：市值、股价等数据必须验证来源和日期
3. **系统化思维**：将零散信息整合成结构化知识
4. **持续进化**：不断学习新工具和方法论，提升能力边界
```

## 进化3：Hindsight知识图谱记忆系统

替代内置MEMORY.md只有2200字符的硬上限，Hindsight自动提取实体、事实、关系，构建知识图谱。

### 状态检查

```bash
# 检查内存插件状态
hermes memory status

# 查看当前配置
grep -A6 "memory:" ~/.hermes/config.yaml
```

### 启用Hindsight

```bash
# 修改config.yaml中的provider字段
sed -i '' 's/provider: ''/provider: hindsight/g' ~/.hermes/config.yaml
```

验证：`hermes memory status` 应显示 Provider: hindsight

## 进化4：抓取工具链验证

检查web抓取和浏览器自动化能力：

```bash
# 查看已启用工具集
hermes tools list | grep -E "web|browser"

# 检查高级抓取配置
grep -E "FIRECRAWL|BROWSERBASE" ~/.hermes/.env
```

预期输出：
- ✓ enabled  web  🔍 Web Search & Scraping
- ✓ enabled  browser  🌐 Browser Automation

## 进化5：表达能力工具链

检查多模态能力：

```bash
hermes tools list | grep -E "image|tts|vision"
```

预期：
- ✓ enabled  image_gen  🎨 Image Generation
- ✓ enabled  tts  🔊 Text-to-Speech
- ✓ enabled  vision  👁️  Vision / Image Analysis

## 进化6：Token精细管控仪表盘

Hermes内置insights工具（不需要额外安装tokenstats）：

```bash
# 查看7天Token使用统计
hermes insights --days 7

# 查看30天完整分析
hermes insights --days 30
```

**insights包含维度：**
- 总体概览（会话数、消息数、Token量、活跃时间）
- 模型使用分布（按模型统计Token消耗）
- 平台分布（CLI、微信、飞书、QQBot等）
- Top工具调用排行
- 技能使用统计
- 活动模式（星期分布、高峰时段）
- 标志性会话（最长会话、最多消息、最多Token等）

## 进化7：技能生态检查

```bash
# 统计已安装技能分类数量
ls ~/.hermes/skills/ | wc -l

# 列出分类
ls ~/.hermes/skills/

# 查看可用技能
hermes skills list
```

## 进化8：agency-agents-zh 中文专家角色库（211个）

**项目地址**：https://github.com/jnMetaCode/agency-agents-zh

包含：165个翻译角色 + 46个中国本土原创智能体，覆盖18个部门（金融、营销、工程、产品等）

### 一键安装流程

```bash
# 1. 克隆仓库
cd ~/.hermes
git clone --depth 1 https://github.com/jnMetaCode/agency-agents-zh.git

# 2. 转换为Hermes格式（必须先转换！）
cd ~/.hermes/agency-agents-zh
./scripts/convert.sh --tool hermes
# 输出：[OK] 已转换 211 个智能体 (hermes)

# 3. 安装到Hermes
./scripts/install.sh --tool hermes
# 输出：[OK]  Hermes Agent: 211 个 skills -> /Users/me/.hermes/skills
```

### 验证安装

```bash
# 检查技能分类数（应从41增加到62）
ls ~/.hermes/skills/ | wc -l

# 查看新增核心分类
ls ~/.hermes/skills/finance/
ls ~/.hermes/skills/marketing/
```

### 核心专家角色推荐

#### 📊 金融投资领域（机构级能力）

| 角色 | 适用场景 |
|------|----------|
| finance-investment-researcher | 投资研究报告、DCF估值、尽职调查 |
| finance-financial-analyst | 财务建模、盈利质量分析 |
| finance-fpa-analyst | 预算规划、滚动预测、经营分析 |
| finance-fraud-detector | 财务造假识别、财报真实性研判 |
| A股ST公司财务分析与借壳预期研判 | ST股票重组概率评估 |
| A股市场分析标准化流程 | 市场分析时间戳验证+盘前盘后判断 |

**使用方式**：
```
"激活投资研究员模式，帮我分析XX公司的投资价值，输出完整研究报告"
"激活财务分析师，帮我做一份新能源行业的财务模型，含3种场景预测"
```

#### 📱 中国市场原创（46个本土化智能体）

| 平台/领域 | 专家角色 |
|----------|---------|
| 小红书 | marketing-xiaohongshu-operator |
| 抖音 | marketing-douyin-strategist |
| B站 | marketing-bilibili-strategist |
| 视频号 | marketing-weixin-channels-strategist |
| 微信小程序 | engineering-wechat-mini-program-developer |
| 知识付费 | marketing-knowledge-commerce-strategist |
| 政务ToG | specialized-chief-of-staff |

**小红书运营专家示例**：
```
"激活小红书运营专家，帮我制定一个AI工具产品的种草投放方案"
```
> 输出包含：爆款笔记公式、达人投放矩阵、排期表+ROI追踪、平台合规检查

---

## 进化9：GenericAgent 4 层记忆架构（2026新增）

**核心理念来源**：lsdefine/GenericAgent 开源项目

**解决问题**：内置 MEMORY.md 只有 2200 字符硬上限，内容混杂、查找慢、无结构化。

---

### 四层架构设计

```
L1_Insight_Index (≤30行) → 红线规则 + 高频场景指针 + 关键字
L2_Global_Facts → 用户偏好 + 系统配置 + 项目追踪（验证过的事实）
L3_SOP → 标准化做事流程 + 避坑指南
L4_Raw_Sessions → 原始会话归档
```

**设计公理**：信息按使用频率和可执行性分层，越高层越精简、越可执行。

---

### 三大核心公理

#### 公理 1：无行动，不记忆

- 每条记忆必须对应具体的行动或决策
- 如果一条信息不能指导未来的行为，它就是噪声
- 记忆的价值 = 复用次数 × 决策质量提升

#### 公理 2：SOP = 压缩的经验

- 把踩过的坑变成标准化流程
- SOP 的价值 = 节省的注意力 - 维护成本
- 好的 SOP 让你不需要思考流程，只需要专注判断

#### 公理 3：Plan 四阶段流程

```
探索 → 规划 → 执行 → 验证（对抗性检查）
```

- **探索**：收集信息，避免盲动
- **规划**：拆分步骤，预估风险
- **执行**：按步执行，及时反馈
- **验证**：对抗性检查，确保质量

---

### 7 步升级流程

```bash
# Step 1: 诊断现状
ls -la ~/.hermes/memories/
wc -l ~/.hermes/memories/MEMORY.md

# Step 2: 创建目录结构
mkdir -p ~/.hermes/memory/L3_sop ~/.hermes/memory/L4_raw_sessions

# Step 3: 备份原有记忆
cp ~/.hermes/memories/MEMORY.md ~/.hermes/memory/L4_raw_sessions/$(date +%Y-%m-%d)_original_memory_backup.md
cp ~/.hermes/memories/USER.md ~/.hermes/memory/L4_raw_sessions/$(date +%Y-%m-%d)_original_user_backup.md 2>/dev/null || true

# Step 4: 创建 L1 洞察索引（≤30 行）
# 参考：hermes-architecture-optimization 技能模板

# Step 5: 创建 L2 全局事实库
# 只放 100% 确认的事实，不放任何推测

# Step 6: 创建核心 SOP（7 份）
# - memory_management_sop.md - 记忆管理
# - plan_mode_sop.md - 复杂任务处理
# - agent_loop_sop.md - Agent 执行循环
# - market_analysis_sop.md - 市场分析
# - wechat_push_sop.md - 微信推送
# - daily_ai_news_sop.md - 每日 AI 资讯
# - skill_invocation_sop.md - 技能调用

# Step 7: 验证
ls -lh ~/.hermes/memory/
wc -l ~/.hermes/memory/L*.txt
```

---

### 优化前后对比

| 维度 | 优化前 | 优化后 |
|------|--------|--------|
| 记忆结构 | 单文件扁平 | 4 层架构 |
| 查找速度 | 全文扫描（慢） | 层级索引（快） |
| 信息噪声 | 混合在一起 | 严格分类 |
| 避坑能力 | 靠记性 | SOP 强制提醒 |
| 可维护性 | 难以扩展 | 模块化 |

---

### 对抗性验证机制

每个重要任务完成后，站在最挑剔的用户视角问自己：

1. 如果我是用户，这个结果能满足我的需求吗？
2. 这个实现有没有遗漏边界情况？
3. 有没有更简单、更高效的方案？
4. 如果出问题了，我有备选方案吗？
5. 长期来看，这个方案可维护吗？

---

## 进化完成验证清单
|------|----------|----------|
| RTK启用 | `grep -c "rtk-instructions" ~/.hermes/CLAUDE.md` | ≥ 1 |
| SOUL充实 | `wc -c ~/.hermes/SOUL.md` | ＞500字符 |
| Hindsight启用 | `grep "provider: hindsight" ~/.hermes/config.yaml` | 匹配成功 |
| Web工具启用 | `hermes tools list | grep "web.*enabled"` | ✓ enabled |
| Insights可用 | `hermes insights --days 1` | 正常输出仪表盘 |
| agency-agents-zh | `ls ~/.hermes/skills/ | wc -l` | ≥ 62 分类 |

## 故障排查

### Hindsight不生效
- 检查config.yaml缩进是否正确（YAML对缩进敏感）
- 重启Hermes会话使配置生效

### RTK不生效
- 确保在 `~/.hermes/` 目录执行 `rtk init`
- 检查CLAUDE.md是否生成正确

### 工具未启用
```bash
# 手动启用工具集
hermes tools enable web
hermes tools enable browser
hermes tools enable image_gen
```

## 后续可探索方向

1. **Hindsight本地服务器** - 完全本地化知识图谱存储（Docker部署）
2. **Marker PDF提取** - 高精度文档解析
3. **CamoFox/Scrapling** - 高级反爬抓取引擎
4. **Mixture of Agents** - 多Agent混合推理模式
