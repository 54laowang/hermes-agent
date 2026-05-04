---
name: baoyu-content-toolkit
description: |
  宝玉内容工具集 - 覆盖图片生成、格式转换、翻译、文章处理等完整内容创作流程。
  16+ 工具覆盖：封面生成、文章插图、格式转换、多平台发布、翻译等。
version: 1.1.0
category: content
keywords:
  - baoyu
  - content
  - image-gen
  - format
  - translate
  - publish
  - markdown
---

# 宝玉内容工具集

## 工具分类

### 一、AI 图片生成

| 工具 | 功能 | 用途 |
|------|------|------|
| `baoyu-image-gen` | AI 图片生成 | 通用图像生成 |
| `baoyu-cover-image` | 封面图生成 | 文章封面、主图 |
| `baoyu-article-illustrator` | 文章配图 | 自动识别配图位置 |
| `baoyu-xhs-images` | 小红书图集 | 小红书信息图系列 |
| `baoyu-slide-deck` | 幻灯片生成 | PPT 图片系列 |
| `baoyu-comic` | 知识漫画 | 教育漫画创作 |
| `baoyu-infographic` | 信息图 | 数据可视化图 |

### 二、格式转换

| 工具 | 功能 |
|------|------|
| `baoyu-url-to-markdown` | URL 转 Markdown |
| `baoyu-format-markdown` | Markdown 格式化 |
| `baoyu-markdown-to-html` | Markdown 转 HTML |
| `baoyu-compress-image` | 图片压缩（WebP/PNG） |

### 三、内容处理

| 工具 | 功能 |
|------|------|
| `baoyu-translate` | 文章翻译（快翻/普通/精翻） |
| `baoyu-youtube-transcript` | YouTube 字幕提取 |
| `baoyu-danger-x-to-markdown` | X/Twitter 转 Markdown |
| `baoyu-danger-gemini-web` | Gemini Web API 生成 |

### 四、多平台发布

| 工具 | 平台 |
|------|------|
| `baoyu-post-to-wechat` | 微信公众号 |
| `baoyu-post-to-weibo` | 微博 |
| `baoyu-post-to-x` | X/Twitter |

---

## 典型工作流

### 工作流一：公众号文章创作

```
1. baoyu-url-to-markdown    # 抓取素材
2. baoyu-translate          # 翻译（如需）
3. baoyu-format-markdown    # 格式化
4. baoyu-cover-image        # 生成封面
5. baoyu-article-illustrator # 生成配图
6. baoyu-post-to-wechat     # 发布到公众号
```

### 工作流二：小红书图集创作

```
1. 准备内容大纲
2. baoyu-xhs-images         # 生成图集
3. 发布到小红书
```

### 工作流三：信息图创作

```
1. 准备数据/内容
2. baoyu-infographic        # 生成信息图
3. 发布到各平台
```

---

## 图片生成配置

### 封面图配置（5 维度）

| 维度 | 选项 |
|------|------|
| 类型 | 风景、人物、抽象、科技... |
| 配色 | 10 种配色方案 |
| 渲染 | 7 种渲染风格 |
| 文字 | 标题文字布局 |
| 情绪 | 情感基调 |

### 信息图配置

- 21 种布局类型
- 20+ 视觉风格
- 自动适配内容结构

---

## 发布平台支持

| 平台 | 发布方式 | 内容格式 |
|------|----------|----------|
| 微信公众号 | API / CDP | HTML/MD/纯文本 |
| 微博 | CDP | 图文 |
| X/Twitter | API | 图文、长文 |

---

## 相关技能

- `design-image-studio` - 设计导向的图片生成
- `wechat-content-workflow` - 微信内容工作流

---

## 参考文件

- `references/mobile-messaging-format.md` - 飞书/微信等移动端消息格式最佳实践（表格转列表、控制长度、扁平化结构）
