---
name: wechat-article-learning
description: 微信公众号文章学习流程 - 下载、提取、总结、归档、生成行动项
priority: P1
triggers:
  - 用户发送公众号链接 (mp.weixin.qq.com)
  - 用户说"学习这篇文章"
  - 用户说"看看这篇文章"
auto_load: false
---

# 微信公众号文章学习流程

## 核心目标

将公众号文章转化为可执行的知识和行动项，而非简单的阅读总结。

## 标准流程

### 1️⃣ 下载文章

**首选方案**：使用 wechat-download MCP
```
mcp_wechat_download_wechat(
  url="https://mp.weixin.qq.com/s/...",
  config={"HTML": true, "MD": true}
)
```

**失败回退**（按优先级尝试）：
1. 尝试 `web_extract([url])` — 可能被 Block（私人网络限制）
2. 尝试 `mcp_vibe_trading_read_url(url)` — 可能遇到验证码
3. **如果文章已下载到远程服务器**：`curl -sL "远程URL" > /tmp/article.html`
4. 最后手段：`curl` 直接获取公众号 HTML

**实际案例（2026-05-01）**：
- 公众号直接抓取遇到"环境异常"验证码
- 使用 `mcp_wechat_download_wechat` 后返回远程服务器 URL
- 最终方案：`curl -sL "https://changfengbox.top/static/temp/download/wechat/文章名.html"`
- 提取内容后用正则匹配 HTML 标签，多次尝试不同提取策略

### 2️⃣ 提取核心内容

**提取清单**：
- [ ] 标题
- [ ] 作者/来源
- [ ] 发布时间
- [ ] 核心论点（3-5个）
- [ ] 关键数据/案例
- [ ] 可执行建议
- [ ] 相关资源链接

**过滤掉**：
- 推广信息
- 重复内容
- 无意义的排版元素

### 3️⃣ 结构化总结

**输出格式**：

```markdown
## 📚 文章核心要点

### 核心观点
1. [观点1]
2. [观点2]
3. [观点3]

### 关键数据
- [数据1]：[来源]（[时间]）
- [数据2]：[来源]（[时间]）

### 可执行建议
1. [建议1] - 优先级：高/中/低
2. [建议2] - 优先级：高/中/低

### 相关资源
- [资源标题]：[链接]
- [资源标题]：[链接]
```

### 4️⃣ 归档到记忆系统

**事实 → fact_store**：
```
fact_store(
  action="add",
  content="关键事实",
  category="general",
  tags="公众号,文章主题"
)
```

**完整内容 → MemPalace**：
```
mcp_mempalace_mempalace_add_drawer(
  wing="learning",
  room="articles",
  content="完整文章内容",
  source_file="公众号标题"
)
```

### 5️⃣ 生成行动项

**基于文章内容的优化建议**：

1. **如果文章讲工具/方法**：
   - 是否需要创建新 Skill？
   - 是否需要更新现有 Skill？
   - 是否需要修改 CLAUDE.md？

2. **如果文章讲趋势/洞察**：
   - 对当前工作的影响？
   - 需要关注的信号？
   - 需要准备的事项？

3. **如果文章讲案例/实践**：
   - 可借鉴的模式？
   - 需要避免的坑？
   - 可复用的模板？

**输出格式**：
```markdown
## 🎯 行动项

### 立即可做
- [ ] [行动项1]
- [ ] [行动项2]

### 近期规划
- [ ] [行动项3]
- [ ] [行动项4]

### 长期关注
- [ ] [行动项5]
```

## 实战案例

### 案例：Claude Code 文章学习

**输入**：公众号文章链接

**输出**：
1. ✅ 提取核心观点：98.4%是工程不是AI
2. ✅ 归档到 fact_store："Harness 概念"
3. ✅ 生成优化建议：
   - 扩展 CLAUDE.md
   - 创建 wechat-article-learning Skill
   - 创建数据验证 Hook

## 常见问题

### Q: 文章下载失败怎么办？
**A**: 按顺序尝试回退方案，最后可请求用户复制粘贴内容。

### Q: 如何判断哪些内容值得归档？
**A**: 遵循"未来价值"原则：
- 会再次查阅的事实 → fact_store
- 完整方法论 → MemPalace
- 临时信息 → 不归档

### Q: 如何避免学习流于形式？
**A**: 强制输出行动项：
- 每篇文章至少1个可执行的建议
- 每个建议必须有明确的下一步

## 相关技能

- `context-soul-injector` - 时间感知 + 持续学习
- `hierarchical-memory-system` - 分层记忆归档
- `neat-freak` - 会话结束知识清理

## 技术参考

- **[微信公众号文章提取技术细节](references/wechat-extraction-techniques.md)** - 反爬虫机制、提取技巧、实战案例
