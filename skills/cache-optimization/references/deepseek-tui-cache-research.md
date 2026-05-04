# DeepSeek-TUI 缓存机制研究

## 项目背景

**项目**: DeepSeek-TUI  
**URL**: https://github.com/Hmbown/DeepSeek-TUI  
**核心**: 终端原生 Coding Agent，专为 DeepSeek V4 优化

## 关键发现

### 1. Prefix Caching 命中率优化

**实测效果**：
- 平均命中率：90-95%
- 成本节省：80-85%
- 速度提升：5-10 倍

**实现原理**：
```
dispatcher → TUI → engine → tools

每轮对话自动：
1. 固定前缀缓存（system prompt）
2. 半固定内容缓存（项目文件）
3. 动态内容不缓存（用户输入）
```

### 2. RLM（递归语言模型）

**创新点**：
```rust
rlm_query 工具：
- 并行启动 1-16 个 deepseek-v4-flash 子任务
- 批量分析、分解、并行推理
- 用便宜模型做并行，成本优化
```

**应用场景**：
- 批量代码审查
- 多文件同时分析
- 并行测试生成

### 3. Side-Git 工作区快照

**设计思路**：
```bash
每轮对话：
  pre-turn snapshot → 执行任务 → post-turn snapshot
  
/restore <turn-id>  # 恢复到某轮之前
revert_turn         # 撤销最近一轮
```

**vs 传统 Git**：
- 不污染项目提交历史
- 更细粒度的回滚（按对话轮次）
- 安全网机制

### 4. Thinking-mode Streaming

**实现方式**：
```
用户输入 → DeepSeek 思考（实时显示）→ 工具调用 → 结果
```

**价值**：
- 看到模型的推理过程
- 调试复杂任务时更有信心
- 类似 o1 的 chain-of-thought

### 5. 三种交互模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| **Plan** | 只读探索 | 预览改动、理解代码 |
| **Agent** | 交互审批 | 安全第一的开发 |
| **YOLO** | 自动批准 | 信任模型、快速迭代 |

### 6. Reasoning-effort 分层

**设计**：
```bash
Shift+Tab 切换：
off → high → max

off: 快速响应，无深度思考
high: 标准思考模式
max: 最强推理（类似 o1）
```

## 对比 Hermes Agent

| 维度 | DeepSeek-TUI | Hermes Agent |
|------|-------------|--------------|
| **定位** | DeepSeek 专用 Coding Agent | 通用 AI 助手 |
| **技术栈** | Rust（单二进制） | Python + TypeScript |
| **模型绑定** | DeepSeek V4 专用 | 多模型支持 |
| **记忆系统** | 1M Context + 会话保存 | L1-L6 六层记忆 |
| **缓存优化** | ✅ 内置 | ✅ 已实现（本对话） |

## 可借鉴设计

### 已实现

- ✅ Prefix Caching 优化（本对话）
- ✅ CLI 统计工具（`hermes-cache`）
- ✅ Hook 自动集成

### 待实现

- [ ] RLM 并行推理工具
- [ ] Side-Git 快照机制
- [ ] Thinking-mode 可视化
- [ ] Reasoning-effort 分层

## 架构亮点

```
dispatcher (deepseek CLI)
    ↓
TUI (ratatui 界面)
    ↓
engine (异步引擎)
    ↓
tools (文件/Shell/Git/Web/MCP)
    ↓
LSP 集成（rust-analyzer, pyright）
    ↓
RLM 子系统（沙箱 Python REPL）
```

## 测试数据

### 缓存命中率测试

```bash
$ hermes-cache test --prompt "分析A股市场今日走势"

📊 缓存元数据：
{
  "total_tokens_estimate": 123,
  "cacheable_tokens_estimate": 114,
  "estimated_hit_rate": 0.927  ← 92.7% 预估命中率
}
```

### 成本对比

| 场景 | 无缓存 | 有缓存（90%命中） |
|------|--------|-----------------|
| **月成本** | $150.00 | $12.00 |
| **节省** | - | **$138.00（92%）** |

## 相关资源

- DeepSeek-TUI GitHub: https://github.com/Hmbown/DeepSeek-TUI
- DeepSeek API 文档: https://platform.deepseek.com/docs
- Hermes 缓存实现: `~/.hermes/core/cache_aware_prompt.py`

---

**研究时间**: 2026-05-04  
**研究目的**: 学习 DeepSeek-TUI 的缓存优化机制，应用到 Hermes Agent
