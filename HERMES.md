<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: Even in command chains with `&&`, use `rtk`:
```bash
# ❌ Wrong
git add . && git commit -m "msg" && git push

# ✅ Correct
rtk git add . && rtk git commit -m "msg" && rtk git push
```

## RTK Commands by Workflow

### Build & Compile (80-90% savings)
```bash
rtk cargo build         # Cargo build output
rtk cargo check         # Cargo check output
rtk cargo clippy        # Clippy warnings grouped by file (80%)
rtk tsc                 # TypeScript errors grouped by file/code (83%)
rtk lint                # ESLint/Biome violations grouped (84%)
rtk prettier --check    # Files needing format only (70%)
rtk next build          # Next.js build with route metrics (87%)
```

### Test (90-99% savings)
```bash
rtk cargo test          # Cargo test failures only (90%)
rtk vitest run          # Vitest failures only (99.5%)
rtk playwright test     # Playwright failures only (94%)
rtk test <cmd>          # Generic test wrapper - failures only
```

### Git (59-80% savings)
```bash
rtk git status          # Compact status
rtk git log             # Compact log (works with all git flags)
rtk git diff            # Compact diff (80%)
rtk git show            # Compact show (80%)
rtk git add             # Ultra-compact confirmations (59%)
rtk git commit          # Ultra-compact confirmations (59%)
rtk git push            # Ultra-compact confirmations
rtk git pull            # Ultra-compact confirmations
rtk git branch          # Compact branch list
rtk git fetch           # Compact fetch
rtk git stash           # Compact stash
rtk git worktree        # Compact worktree
```

Note: Git passthrough works for ALL subcommands, even those not explicitly listed.

### GitHub (26-87% savings)
```bash
rtk gh pr view <num>    # Compact PR view (87%)
rtk gh pr checks        # Compact PR checks (79%)
rtk gh run list         # Compact workflow runs (82%)
rtk gh issue list       # Compact issue list (80%)
rtk gh api              # Compact API responses (26%)
```

### JavaScript/TypeScript Tooling (70-90% savings)
```bash
rtk pnpm list           # Compact dependency tree (70%)
rtk pnpm outdated       # Compact outdated packages (80%)
rtk pnpm install        # Compact install output (90%)
rtk npm run <script>    # Compact npm script output
rtk npx <cmd>           # Compact npx command output
rtk prisma              # Prisma without ASCII art (88%)
```

### Files & Search (60-75% savings)
```bash
rtk ls <path>           # Tree format, compact (65%)
rtk read <file>         # Code reading with filtering (60%)
rtk grep <pattern>      # Search grouped by file (75%)
rtk find <pattern>      # Find grouped by directory (70%)
```

### Analysis & Debug (70-90% savings)
```bash
rtk err <cmd>           # Filter errors only from any command
rtk log <file>          # Deduplicated logs with counts
rtk json <file>         # JSON structure without values
rtk deps                # Dependency overview
rtk env                 # Environment variables compact
rtk summary <cmd>       # Smart summary of command output
rtk diff                # Ultra-compact diffs
```

### Infrastructure (85% savings)
```bash
rtk docker ps           # Compact container list
rtk docker images       # Compact image list
rtk docker logs <c>     # Deduplicated logs
rtk kubectl get         # Compact resource list
rtk kubectl logs        # Deduplicated pod logs
```

### Network (65-70% savings)
```bash
rtk curl <url>          # Compact HTTP responses (70%)
rtk wget <url>          # Compact download output (65%)
```

### Meta Commands
```bash
rtk gain                # View token savings statistics
rtk gain --history      # View command history with savings
rtk discover            # Analyze Claude Code sessions for missed RTK usage
rtk proxy <cmd>         # Run command without filtering (for debugging)
rtk init                # Add RTK instructions to CLAUDE.md
rtk init --global       # Add RTK to ~/.claude/CLAUDE.md
```

## Token Savings Overview

| Category | Commands | Typical Savings |
|----------|----------|-----------------|
| Tests | vitest, playwright, cargo test | 90-99% |
| Build | next, tsc, lint, prettier | 70-87% |
| Git | status, log, diff, add, commit | 59-80% |
| GitHub | gh pr, gh run, gh issue | 26-87% |
| Package Managers | pnpm, npm, npx | 70-90% |
| Files | ls, read, grep, find | 60-75% |
| Infrastructure | docker, kubectl | 85% |
| Network | curl, wget | 65-70% |

Overall average: **60-90% token reduction** on common development operations.
<!-- /rtk-instructions -->

---

# Hermes Agent 项目大脑

> **核心理念**：98.4% 是工程，不是 AI。优化重点在"为 AI 设计严格的工作环境"。

---

## 项目概览

| 组件 | 位置 | 说明 |
|------|------|------|
| **配置文件** | `~/.hermes/config.yaml` | 主配置 |
| **环境变量** | `~/.hermes/.env` | API 密钥和敏感信息 |
| **会话存储** | `~/.hermes/sessions/` | SQLite 会话记录 |
| **Skills 目录** | `~/.hermes/skills/` | 已安装技能 |
| **Hooks 目录** | `~/.hermes/hooks/` | 自动化脚本 |
| **日志目录** | `~/.hermes/logs/` | Gateway 和错误日志 |

---

## 核心约束（最高优先级）

### 1. 时间锚定宪法

**任何数据分析前必须建立时间锚点**：

```
1. 确认当前时间 → 判断市场状态
2. 构建搜索关键词（必须包含：精确日期 + 时间节点）
3. 验证数据时间戳是否匹配当前市场状态
4. 不匹配 = 拒绝使用，重新搜索
```

**市场状态判断**：
- **A股**：盘前(09:30前) / 早盘(09:30-11:30) / 午盘(11:30-13:00) / 午后(13:00-15:00) / 收盘(15:00后)
- **美股**：需换算美东时间（北京 - 12小时），美东收盘日期 = 北京日期 - 1（凌晨04:00后）

**示例**：
- ✅ "A股收盘 2026年5月1日"
- ✅ "美股收盘 2026年4月30日"（美东日期）
- ❌ "A股行情"（缺少日期）
- ❌ "美股走势"（缺少日期和时间节点）

---

### 2. 数据交叉验证原则

**强制要求**：
- 至少 **3 个独立数据源**
- 时间戳一致性检查
- 数据性质确认（涨/跌/买/卖等）

**数据源分级**：

| 级别 | 数据源 | 使用场景 |
|------|--------|---------|
| **P0** | 财联社电报、交易所公告、官方财报 | 最高优先级，实时数据 |
| **P1** | 东方财富、同花顺、Wind、Choice | 高优先级，行情数据 |
| **P2** | 新浪财经、证券时报、上海证券报 | 中优先级，新闻报道 |
| **P3** | 自媒体、论坛、个人博客 | 低优先级，谨慎使用 |

**强制标注格式**：
```
数据：[具体数据]
来源：[媒体名]（P0/P1/P2/P3）
时间：[YYYY-MM-DD]
验证：[已验证/待验证/无法验证]
可信度：[★数量]
```

---

### 3. 禁止行为清单

**绝对禁止**：

| 禁止行为 | 后果 |
|---------|------|
| 用过时数据凑数 | 分析无效，必须重做 |
| 跳过时间验证 | 记录错误，触发自我审计 |
| 时区混乱 | 强制学习 us-stock-data-acquisition-sop |
| 单一数据源 | 必须补充验证 |
| 无时间戳数据 | 拒绝使用 |

---

## 工具使用规范

### 优先级规则

```
1. 文件读取：read_file > terminal cat
2. 内容搜索：search_files > terminal grep
3. 网络请求：web_extract > terminal curl
4. 文件编辑：patch > terminal sed
5. 所有命令：rtk <command>（节省 60-90% token）
```

### 工具集启用检查

```bash
hermes tools list          # 查看所有工具状态
hermes tools enable web    # 启用 web 工具集
hermes tools disable moa   # 禁用 moa 工具集
```

---

## 工作流程标准

### 财经分析流程

```
1. 加载 time-anchor-constitution（自动）
2. 确认时间 → 判断市场状态
3. 构建搜索关键词（日期 + 时间节点）
4. 获取数据（P0 → P1 → P2）
5. 交叉验证（至少3源）
6. 输出分析（标注来源 + 时间戳 + 可信度）
```

### 代码任务流程

```
1. 加载相关 Skill（skill_view）
2. 理解需求 → 规划步骤
3. 执行 → 验证结果
4. 更新 Skill（如发现新坑点）
```

### 公众号文章学习流程

```
1. 下载文章（wechat-download MCP）
2. 提取核心内容
3. 结构化总结
4. 归档到 MemPalace + fact_store
5. 生成可执行行动项
```

---

## 常见陷阱

### 已知问题

| 陷阱 | 表现 | 解决方案 |
|------|------|---------|
| **用过时数据凑数** | 用午盘数据代替收盘 | 严格执行时间锚定原则 |
| **假设数据是最新的** | 直接用搜索第一条 | 必须验证时间戳 |
| **忽略时区差异** | 用北京时间搜索美股 | 先换算美东时间 |
| **单一数据源** | 只查一个网站 | 至少3源交叉验证 |
| **推测当事实** | "应该是..."、"可能是..." | 明确标注为推测 |

### 错误后反思流程

**每次 AI 犯错后**：
1. 问自己："HERMES.md 里缺了什么？"
2. 补充到本文档
3. 更新相关 Skill
4. 记录到 fact_store

---

## 记忆系统架构

```
L6: Skills 系统（82 个可复用流程）
    ↓
L5: Context Memory（任务特定上下文）
    ↓
L4: 全息记忆（fact_store + KG）
    ↓
L3: 知识归档（MemPalace）
    ↓
L2: 短期记忆（memory tool）
    ↓
L1: 会话记忆（SQLite sessions）
```

**使用场景**：
- **memory**：用户偏好、环境配置、持续有效的约束
- **fact_store**：关键事实、实体关系、需要推理查询的知识
- **MemPalace**：完整文档、历史记录、需要语义搜索的内容
- **Skills**：可复用的工作流程、操作步骤
- **Context Memory**：任务特定上下文、步骤追踪、中间结果

## 缓存优化系统

**已集成 DeepSeek Prefix Caching 优化**：
- 自动构建缓存友好的 Prompt
- 平均命中率 90-95%
- 节省成本 80%+

**查看统计**：
```bash
hermes-cache stats      # 查看统计报告
hermes-cache optimize   # 优化建议
```

**缓存分层**：
```
固定前缀（95% 命中）
    ↓
半固定内容（80% 命中）
    ↓
工具上下文（60% 命中）
    ↓
会话历史（40% 命中）
    ↓
用户输入（0% 命中）
```

---

## 快速参考

### 常用命令

```bash
# 配置管理
hermes config edit          # 编辑配置
hermes config check         # 检查配置
hermes doctor --fix         # 诊断问题

# Skills 管理
hermes skills list          # 列出已安装
hermes skills search <q>    # 搜索技能
hermes skills install <id>  # 安装技能

# 会话管理
hermes sessions list        # 列出会话
hermes sessions browse      # 交互式选择

# Gateway 管理
hermes gateway status       # 查看状态
hermes gateway restart      # 重启服务
```

### 重要 Skills

| Skill | 用途 | 优先级 |
|-------|------|--------|
| `time-anchor-constitution` | 时间锚定宪法 | P0（自动加载） |
| `wechat-article-learning` | 公众号文章学习 | P1 |
| `a-share-market-analysis` | A股市场分析 | P1 |
| `grid-trading-monitor` | 网格交易监控 | P1 |
| `hierarchical-memory-system` | 分层记忆系统 | P1 |

---

## 更新日志

### 2026-05-01
- 基于文章《撕开Claude Code真相》重构
- 新增：项目大脑概念、核心约束、工作流程标准
- 新增：常见陷阱和错误反思流程
- 优化：RTK 指令集成到顶部

---

**记住**：每次 AI 犯错后，问自己"HERMES.md 里缺了什么"，然后补充进来。这就是持续积累的过程。
