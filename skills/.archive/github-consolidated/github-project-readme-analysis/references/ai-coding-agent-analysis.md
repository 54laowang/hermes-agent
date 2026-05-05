# AI Coding Agent 项目分析方法论

## 背景
AI 编程代理（如 Claude Code、Cursor、jcode 等）是一类特殊的开发者工具，需要从多个维度进行分析才能给用户提供全面的决策建议。

## 分析框架（5 维度）

### 1. 性能与资源效率
关键指标：
- **内存占用**：空闲/单会话/多会话状态
- **启动速度**：Time to first frame / first input
- **响应延迟**：流式输出、UI 渲染
- **扩展性**：每增加一个会话的额外开销

**数据来源**：
- 项目 README 中的 benchmark
- 第三方对比测试
- 实际运行 `htop`、`ps aux` 监控

**示例输出**（对比表格）：
```
| 工具 | 空闲内存 | 单会话 | 10会话 | 启动时间 |
|------|---------|--------|--------|---------|
| jcode | 28MB | 167MB | 261MB | 14ms |
| Claude Code | - | 387MB | 2301MB | 3437ms |
```

### 2. Provider 生态系统
分析要点：
- **原生 Provider**：Claude、OpenAI、Gemini、Copilot 等官方支持
- **兼容 Provider**：OpenRouter、自定义端点、本地模型
- **认证方式**：OAuth、API Key、环境变量、配置文件
- **多账号管理**：是否支持快速切换账号/订阅

**关键文件位置**：
- `src/config.rs` - Provider 配置结构
- `src/cli/provider_init.rs` - 登录流程
- 文档中的 "OAuth and Providers" 章节

**示例代码片段**：
```rust
// Provider 配置示例（从源码提取）
pub struct NamedProviderConfig {
    pub provider_type: NamedProviderType,  // OpenAI-compatible, OpenRouter
    pub base_url: String,
    pub api_key_env: Option<String>,
    pub default_model: Option<String>,
}
```

### 3. 核心差异化功能
常见卖点：
- **记忆系统**：向量检索、语义记忆、跨会话持久化
- **多代理协作**：Swarm 模式、Agent 间通信、冲突自动解决
- **工具集成**：MCP 支持、浏览器自动化、自定义工具
- **自定制能力**：Self-Dev 模式、插件系统、主题定制
- **会话恢复**：是否支持从其他工具恢复会话

**评估方法**：
1. 阅读 README 的核心功能章节
2. 查看 `docs/` 目录下的架构文档
3. 搜索关键源码文件（如 `memory.rs`、`swarm.rs`）

### 4. 配置管理复杂度
评估维度：
- **配置文件格式**：TOML、JSON、YAML
- **环境变量支持**：哪些变量会被自动读取
- **可视化工具**：是否有类似 CC-Switch 的 GUI 配置管理
- **配置继承**：全局 vs 项目级配置

**最佳实践**：
```toml
# ~/.jcode/config.toml 示例
[providers.deepseek]
type = "openai-compatible"
base_url = "https://api.deepseek.com/v1"
api_key_env = "DEEPSEEK_API_KEY"
default_model = "deepseek-chat"
```

```bash
# 环境变量方式
export DEEPSEEK_API_KEY="sk-xxx"
export OPENROUTER_API_KEY="sk-xxx"
```

### 5. 目标用户画像
明确回答：
- **谁最适合用**：多会话工作者、订阅用户、本地模型爱好者
- **谁可能不适合**：需要 GUI 配置的用户、特定 Provider 用户
- **迁移成本**：从现有工具切换的难度

## 完整分析流程（实战案例：jcode）

### Step 1: 基础信息收集
```bash
# 克隆仓库（depth=1 节省时间）
cd /tmp && git clone --depth 1 https://github.com/1jehuang/jcode.git

# 快速浏览 README
head -200 /tmp/jcode/README.md
```

### Step 2: 性能数据提取
从 README 中查找：
- Benchmark 章节
- 对比表格
- 性能演示视频/GIF

**示例**：jcode README 包含详细的内存和启动时间对比数据

### Step 3: Provider 支持分析
```bash
# 查找 Provider 相关源码
find /tmp/jcode -name "*.rs" | xargs grep -l "provider\|Provider"

# 阅读配置结构
cat /tmp/jcode/src/config.rs | grep -A 20 "NamedProviderConfig"

# 查看支持的 Provider 列表
grep -r "login --provider" /tmp/jcode/README.md
```

### Step 4: 配置文件格式研究
```bash
# 查找配置文件示例
find /tmp/jcode -name "config.toml" -o -name "*.env"

# 查找文档中的配置说明
grep -r "config.toml\|\.env\|environment variable" /tmp/jcode/README.md
```

### Step 5: 与竞品对比
使用 `web_search` 查找：
- `{项目名} vs Claude Code`
- `{项目名} vs Cursor`
- `{项目名} third party API support`

**关键对比维度**：
- 性能（内存、启动速度）
- Provider 灵活性
- 配置管理方式
- 社区活跃度

## 输出模板

### 📊 功能概览表格
| 维度 | 项目名 | 竞品 A | 竞品 B | 性能提升 |
|------|--------|--------|--------|---------|
| 内存占用 | XXX | YYY | ZZZ | Nx |
| 启动速度 | XXms | YYms | ZZms | Nx |

### 🚀 核心功能列表
1. **功能名称**：描述 + 实现方式
2. **功能名称**：描述 + 实现方式
...

### 📦 安装与配置
```bash
# 主要安装方式
curl -fsSL https://... | bash

# 第三方 API 配置示例
vim ~/.config/project/config.toml
```

### 💡 使用建议
**推荐使用的场景**：
- 场景 1
- 场景 2

**需要注意的问题**：
- 问题 1
- 问题 2

### 🔧 与现有工具的对比
| 特性 | 本项目 | 现有工具 |
|------|--------|---------|
| 定位 | XXX | YYY |
| 平台 | XXX | YYY |
| 性能 | XXX | YYY |

## 常见陷阱

### ❌ 只看 README 不看源码
- README 可能过时或夸大
- 实际配置文件格式可能与文档不符
- 源码中的 TODO/FIXME 揭示真实问题

### ❌ 忽略性能测试环境
- Benchmark 可能在特定硬件上运行
- 需要说明测试条件（CPU、内存、操作系统）
- 实际使用环境可能差异很大

### ❌ 不区分官方 Provider 和第三方兼容
- 官方 Provider 有 OAuth 登录支持
- 第三方 API 需要手动配置
- 本地模型可能有额外限制

### ❌ 不检查配置文件优先级
- 环境变量 > 配置文件 > 默认值的顺序
- 多个配置源可能冲突
- 需要明确说明哪个优先级更高

## 本次分析中的发现（jcode 案例）

### 关键发现
1. **极致性能优化**：Rust 编写，内存占用仅为 Claude Code 的 1/14
2. **灵活的 Provider 系统**：支持 20+ Provider，配置文件和环境变量两种方式
3. **配置管理差异**：不支持 CC-Switch GUI，但有命令行多账号切换
4. **创新功能**：Swarm 多代理协作、Self-Dev 自修改模式

### 可复用的分析技巧
1. **从 README 的 benchmark 章节快速提取性能数据**
2. **通过 `src/config.rs` 了解配置系统的真实实现**
3. **使用 `web_search` 查找 "vs CC-Switch" 等关键词快速定位差异点**
4. **对比表格格式让用户一目了然**

## 延伸阅读
- [GitHub 项目 README 分析 Skill](./SKILL.md)
- [AI Coding Agent Provider 配置最佳实践](../templates/provider-config-template.toml)
