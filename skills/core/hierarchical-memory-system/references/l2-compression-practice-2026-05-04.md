# L2 短期记忆压缩实战 - 2026-05-04

## 问题场景

运行 `daily-summarizer-v3.py` 超时（60s），无法自动生成摘要。

## 问题原因

v3 版本使用 LLM API 调用（Hermes Provider API），当网络或服务不可用时会导致超时：

```python
response = requests.post(HERMES_API_URL, headers=headers, json=payload, timeout=30)
```

超时设置为 30 秒，但整个脚本可能在处理大量会话时卡住。

## 解决方案

### 方案 1：手动压缩（推荐）

使用 `manual-compress-l2.py` 脚本：

```bash
python3 ~/.hermes/skills/core/hierarchical-memory-system/scripts/manual-compress-l2.py 2026-05-03
```

**优点**：
- 不依赖 LLM API
- 快速（<1s）
- 保留核心信息

**缺点**：
- 需要手动补充"主要工作/重要成果"章节
- 无自动事实提取

### 方案 2：修复 LLM API 后重试

1. 检查 Hermes Gateway 是否运行：
   ```bash
   hermes gateway status
   ```

2. 检查 Provider API 是否可用：
   ```bash
   curl http://localhost:8642/v1/models
   ```

3. 重启 Gateway：
   ```bash
   hermes gateway restart
   ```

4. 重新运行 v3：
   ```bash
   python3 ~/.hermes/skills/core/hierarchical-memory-system/scripts/daily-summarizer-v3.py
   ```

## 压缩效果统计

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 文件大小 | 40 KB | 1.3 KB | ↓ 96.9% |
| 行数 | 1064 行 | 38 行 | ↓ 96.4% |
| 检索速度 | 慢（扫描全文） | 快（结构化） | ↑ 28 倍 |

## 压缩策略

### 保留内容
- ✅ 今日概览（会话数、核心话题数、主要工作）
- ✅ 核心话题前10个（去重后）
- ✅ 重要成果（5项已完成任务）
- ✅ 用户偏好更新
- ✅ 技术知识沉淀（3条要点）
- ✅ 归档记录（fact_store / MemPalace / Git）

### 删除内容
- ❌ 93个会话的完整详情（每个会话15-106轮对话）
- ❌ 工具调用次数统计（冗余信息）
- ❌ 重复的话题记录
- ❌ 时间戳详情（保留日期即可）

## 后续改进

1. **自动降级机制**：v3 超时自动切换到手动压缩
2. **增量压缩**：实时压缩，避免单次处理大量会话
3. **并行处理**：使用多线程处理会话数据

## 相关文件

- `scripts/daily-summarizer-v3.py` - LLM 增强版摘要器
- `scripts/manual-compress-l2.py` - 手动压缩脚本（新增）
- `~/.hermes/memory/short-term/YYYY-MM-DD.md` - L2 记忆文件
