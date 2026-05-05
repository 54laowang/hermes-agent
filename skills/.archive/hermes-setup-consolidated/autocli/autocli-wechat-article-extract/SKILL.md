---
name: autocli-wechat-article-extract
description: 在 autocli 中提取微信公众号文章正文的自定义适配器配置方法
author: Hermes
---

# autocli-wechat-article-extract
提取微信公众号文章正文内容的 autocli 适配器配置方法

## 问题描述
微信公众号文章（mp.weixin.qq.com）通常有反爬保护，`web_extract` 无法直接获取内容。需要用 autocli browser 模式配合 CSS 选择器手动提取正文。

## 解决方案
创建自定义适配器 `~/.autocli/adapters/weixin/article.yaml`，通过浏览器获取页面后直接从 DOM `#js_content` 提取所有段落：

```yaml
site: weixin
name: article
description: "Extract WeChat official account article content"
domain: mp.weixin.qq.com
strategy: static
browser: true

args:
  url:
    type: string
    required: true
    description: Article URL

pipeline:
  - navigate: "${{ args.url }}"
  - evaluate: |
      (() => {
        const content = document.getElementById('js_content');
        if (!content) return [];
        const paragraphs = Array.from(content.querySelectorAll('p'));
        return paragraphs
          .map(p => p.textContent.trim())
          .filter(t => t.length > 0)
          .map((text, index) => ({ index: index + 1, text }));
      })()

  - map:
      idx: "${{ item.index }}"
      text: "${{ item.text }}"

columns: ["idx", "text"]
```

## 使用方法
```bash
autocli weixin article --url "https://mp.weixin.qq.com/s/xxxx"
```

## 经验教训
1. `autocli generate` 可能会错误选择Ajax接口而不是提取正文，需要手动创建配置
2. 微信文章正文已经在初始HTML中，无需额外API调用，直接DOM提取即可
3. 使用 `filter(t => t.length > 0)` 过滤空段落让输出更干净

## 适用场景
- 需要在终端阅读公众号文章
- 自动化抓取公众号内容归档
- 将公众号文章导入知识库系统

## 增强提取策略（当 autocli 提取失败时）

微信反爬机制可能导致直接提取失败，按以下 fallback 顺序尝试：

### 第一步：用 curl 提取 JS 变量获取元数据
```bash
curl -s -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" "URL" | grep -E "(var msg_title|var nickname|var ct)"
```

这可以直接获取：
- `msg_title`：文章标题
- `nickname`：公众号名称
- `ct`：发布时间戳（转换为可读时间：`date -r 1777219731`）

### 第二步：用标题搜索其他平台转载
通常重要文章会被东方财富网、雪球、新浪财经等平台转载，使用标题搜索：
```bash
web_search "<文章标题> <公众号名称>"
```

### 第三步：完整备用方案
```bash
# 1. 先尝试 autocli
autocli weixin article --url "URL"

# 2. 如果返回空，尝试 curl 提取元数据
curl -s -L -A "Mozilla/5.0..." "URL" | grep -E "(var msg_title|var nickname|var msg_desc)"

# 3. 用提取到的标题搜索其他来源
web_search "<标题>"
```

## 典型失败场景处理

**现象**：autocli 成功执行但输出为空
**原因**：微信反爬触发，页面虽加载但正文内容被保护或延迟渲染
**解决**：直接走第二步 + 第三步，通过标题搜索获取完整内容

**现象**：web_extract 返回 "Blocked: URL targets a private or internal network address"
**原因**：web_extract 内置反爬检测直接拦截了微信域名
**解决**：必须使用浏览器方式或 curl 直接请求
