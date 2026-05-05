---
name: wechat-content-workflow
description: |
  微信内容工作流 - 从文章下载、内容处理到发布推送的完整流程。
  包含公众号文章下载、内容提取、格式转换、发布推送等自动化能力。
version: 1.0.0
category: content
keywords:
  - wechat
  - weixin
  - 公众号
  - 文章下载
  - 内容发布
  - 推送自动化
---

# 微信内容工作流

## 完整流程

```
文章链接 → 下载提取 → 格式转换 → 内容处理 → 发布推送
```

---

## 一、文章下载

### 公众号文章下载

使用 `wechat-article-downloader` 或 `wechat` MCP 工具：

```bash
# 方法1: 使用 MCP wechat 工具
# 支持：公众号文章、网易新闻、今日头条、360图书馆等
# 输出：MD、HTML、PDF、WORD、TXT、MHTML

# 方法2: 直接使用下载技能
# 自动提取标题、正文、图片
```

### 支持的格式

| 格式 | 用途 |
|------|------|
| MD | Markdown 笔记、Obsidian 入库 |
| HTML | 网页存档、原样保留 |
| PDF | 长期存档、打印 |
| WORD | 编辑修改 |

---

## 二、内容处理

### 内容提取

- 标题、作者、发布时间
- 正文内容（自动清洗广告）
- 图片下载与本地化

### 格式转换

- `baoyu-url-to-markdown` - URL 转 Markdown
- `baoyu-format-markdown` - Markdown 格式化
- `baoyu-markdown-to-html` - Markdown 转 HTML
- `baoyu-translate` - 文章翻译

---

## 三、发布推送

### 微信公众号发布

- `baoyu-post-to-wechat` - 通过 API 发布到公众号草稿箱
- 支持图文消息、多图文

### 其他平台发布

- `baoyu-post-to-weibo` - 发布到微博
- `baoyu-post-to-x` - 发布到 X/Twitter
- `baoyu-xhs-images` - 生成小红书图片系列

---

## 四、自动化推送

### 配置推送目标

```yaml
# 在 cronjob 中配置
deliver: weixin:user_id
# 或
deliver: weixin:group_id
```

### 推送注意事项

1. **Token 过期处理**
   - 微信 Token 有效期有限
   - 需定期重新扫码登录
   - 错误 `ret=-2` 通常表示 Token 过期

2. **限流防护**
   - 长消息自动分块发送
   - 配置发送间隔避免限流
   - 分块延迟建议 0.8s 以上

3. **异步上下文**
   - 在 cronjob 中使用 `deliver` 自动投递
   - 避免在任务内主动调用 `send_message`
   - 或让任务输出标记内容供系统提取

---

## 五、相关技能

- `wechat-article-downloader` - 文章下载核心
- `wechat-article-publisher` - 文章发布
- `wechat-author-thought-distillation` - 作者思维蒸馏

---

## 常见问题

### 下载失败

- 检查链接是否有效
- 确认文章未被删除
- 尝试使用浏览器模式

### 发布失败

- 检查公众号 Token 配置
- 确认素材已上传
- 验证内容符合平台规范

### 推送失败

- 检查 Token 是否过期
- 确认目标 ID 正确
- 查看 gateway 日志排查
