---
name: initialize-mempalace
description: MemPalace 记忆宫殿完整管理流程 - 初始化配置、状态查看、健康诊断、可视化展示
category: knowledge-management
---

# MemPalace 记忆宫殿完整管理流程

## 前置条件
- Hermes Agent 已配置 MCP mempalace 工具
- **重要**: MemPalace 通过 MCP 工具操作，**没有 `mempalace` CLI 命令**

## 核心功能模块

### 模块一：初始化配置（从零创建）
适用于：宫殿为空状态 (mempalace_status 返回 total_drawers: 0)

### 模块二：状态查看（日常使用）
适用于：查看记忆系统当前状态、检查健康指标

### 模块三：健康诊断（定期维护）
适用于：深度检查记忆系统完整性、发现潜在问题
## 模块一：初始化配置

### 1. 确认宫殿状态
```javascript
// 调用 MCP 工具: mempalace_status
// 确认 palace_path 配置正确，total_drawers = 0
```

### 2. 创建核心抽屉 (Drawers)

#### 🔹 用户翼 (wing: user)
- **Room: user-profile** - 用户基本信息、语言偏好、关注领域、使用习惯

#### 🔹 创意翼 (wing: creative)
- **Room: novel-time-rift** - 小说《时间裂隙》项目设定、人物、写作进度
- **Room: game-projects** - AI 游戏开发项目 (Claude-Code-Game-Studios 等)

#### 🔹 技术翼 (wing: technical)
- **Room: autocli-automation** - AutoCLI + 微信推送 + Obsidian 自动化配置
- **Room: gpt-image2-prompts** - GPT-Image-2 提示词知识库
- **Room: oh-my-claudecode** - 多智能体编排框架项目
- **Room: hermes-config** - Hermes Agent 配置、技能、网关设置

#### 🔹 财经翼 (wing: finance)
- **Room: market-analysis** - A股市场分析、上市公司跟踪、AI产业链研究

### 3. 建立知识图谱关系 (Knowledge Graph)

#### 用户实体关系:
```
用户 → 偏好 → 中文界面
用户 → 关注 → 全球财经
用户 → 关注 → A股市场
用户 → 关注 → AI科技前沿
用户 → 使用 → macOS系统
```

#### 项目实体关系:
```
时间裂隙 → 主角 → 陈默
时间裂隙 → 主角 → 林小雨
时间裂隙 → 主角 → 沈天机
时间裂隙 → 核心设定 → 平行世界
时间裂隙 → 类型 → 小说创作
```

### 4. 写入初始化日记
```javascript
// 调用: mempalace_diary_write
// 格式 (AAAK):
// SESSION:YYYY-MM-DD|初始化记忆宫殿+N抽屉+M三元组|WINGS:分类统计|★★★
```

### 5. 验证完成
```javascript
mempalace_status()    // 确认抽屉数
mempalace_kg_stats()  // 确认实体和三元组数
```

---

## 陷阱与注意事项 ⚠️

1. **不要尝试 CLI 命令**: `mempalace: command not found` 是正常的，所有操作通过 MCP 工具完成
2. **抽屉内容要具体**: 不要写空抽屉，每个抽屉应包含可检索的实际内容
3. **中文实体名**: 知识图谱使用中文实体名，保持与用户语言一致
4. **日记使用 AAAK 格式**: 压缩格式，便于长期检索
5. **先查询后回答**: 遵循 MemPalace 协议，回答用户问题前先查询宫殿

---

## 后续维护

- 每次会话结束调用 `mempalace_diary_write` 记录
- 事实变更时: `mempalace_kg_invalidate` 旧事实 + `mempalace_kg_add` 新事实
- 定期调用 `mempalace_status` 和 `mempalace_kg_stats` 检查健康状态
- 重要新知识及时通过 `mempalace_add_drawer` 归档

---

## 状态查看与诊断

### 快速健康检查
```javascript
// 1. 查看整体状态
mempalace_status()           // 宫殿概览 + 协议提醒 + AAAK 方言说明

// 2. 查看知识图谱统计
mempalace_kg_stats()         // 实体数、三元组数、关系类型

// 3. 查看最近日记
mempalace_diary_read(agent_name, last_n=5)  // 最近会话记录
```

### 完整诊断流程

#### 1. 宫殿结构分析
```javascript
mempalace_get_taxonomy()     // 完整分类树（翼→房间→抽屉数）
mempalace_list_wings()       // 所有翼及其抽屉数统计
```

#### 2. 知识图谱检查
```javascript
// 查询特定实体
mempalace_kg_query("用户")   // 返回该实体的所有关系

// 搜索相关内容
mempalace_search("交易")     // 在所有抽屉中搜索关键词
```

#### 3. 日记审查
```javascript
// 查看特定日期的日记
mempalace_diary_read_by_date(agent_name, date)

// 查看特定主题的日记
mempalace_diary_read_by_topic(agent_name, topic)
```

### 健康指标标准

#### ✅ 健康状态
- 抽屉数 ≥ 10（信息丰富）
- 实体数 ≥ 15（知识图谱完整）
- 三元组数 ≥ 10（关系充分）
- 过期事实 = 0（数据新鲜）
- 日记连续（会话记录完整）

#### ⚠️ 需要维护
- 抽屉数 < 5（信息匮乏）
- 实体数 < 8（知识图谱不完整）
- 过期事实 > 0（需要清理）
- 日记中断超过 3 天（记录缺失）

### 可视化展示模板

```
## 📊 MemPalace 记忆宫殿状态总览

### 整体统计
- 总抽屉数：N 个
- 翼数量：M 个
- 房间数量：K 个
- 知识图谱实体：E 个
- 关系三元组：T 条

### 翼分布（ASCII 柱状图）
```
wing_name    ████████ N 个
other_wing   ███ M 个
...
```

### 最近日记记录
```
日期 | 重要度 | 主题
YYYY-MM-DD | ★★★★★ | 主题描述
...
```

### 知识图谱关系类型
- 关系1、关系2、关系3...

### 房间分类（按翼）
```
wing / room    描述
...
```
```

---

## 初始化完成标准

- ✅ 抽屉数 ≥ 5
- ✅ 实体数 ≥ 8
- ✅ 三元组数 ≥ 8
- ✅ 初始化日记已写入
- ✅ 所有核心项目已归档