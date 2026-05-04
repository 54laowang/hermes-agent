# 微信公众号文章提取技术细节

## 问题：微信反爬虫机制

公众号文章直接抓取会遇到多种阻碍：

### 1. 验证码拦截
```
Title: Weixin Official Accounts Platform
Warning: This page maybe requiring CAPTCHA, please make sure you are authorized
## 环境异常
当前环境异常，完成验证后即可继续访问。
```

### 2. 解决方案优先级

| 方案 | 成功率 | 说明 |
|------|--------|------|
| `mcp_wechat_download_wechat` | 高 | 专用下载工具，返回远程服务器 URL |
| `web_extract([url])` | 低 | 可能被 Block（私人网络限制） |
| `mcp_vibe_trading_read_url` | 中 | 可能遇到验证码 |
| `curl` 直接获取 | 最低 | 需要处理 HTML |

### 3. 推荐流程

```python
# 步骤1：尝试 MCP 下载工具
result = mcp_wechat_download_wechat(url, config={"HTML": true, "MD": true})

# 步骤2：检查返回的 URL
if result.status == "completed":
    html_url = result.urls[0]  # HTML 文件
    md_url = result.urls[1]    # MD 文件
    
    # 步骤3：从远程服务器下载
    html_content = curl -sL html_url
    
    # 步骤4：提取内容
    text = extract_from_html(html_content)
```

### 4. HTML 内容提取技巧

微信公众号 HTML 结构复杂，需要多次尝试：

**方法 A：正则匹配文本块**
```python
chinese_blocks = re.findall(r'([\u4e00-\u9fff，。！？、；：""''（）\s]{30,})', html)
```

**方法 B：提取 p 标签和 span 标签**
```python
p_contents = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
span_contents = re.findall(r'<span[^>]*>(.*?)</span>', html, re.DOTALL)
```

**方法 C：查找特定关键词上下文**
```python
match = re.search(r'关键词[^\n]{0,500}', text_only)
```

### 5. 清理 HTML 实体

```python
text = re.sub(r'&nbsp;', ' ', text)
text = re.sub(r'&lt;', '<', text)
text = re.sub(r'&gt;', '>', text)
text = re.sub(r'&amp;', '&', text)
text = re.sub(r'&quot;', '"', text)
```

## 关联论文提取

公众号文章中提到的 arXiv 论文通常可以直接访问：

```
https://arxiv.org/abs/论文ID
```

使用 `mcp_vibe_trading_read_url` 或 `web_extract` 即可获取摘要和元数据。

## 实战经验

### 案例：Claude Code 文章（2026-05-01）

1. 直接抓取失败（验证码）
2. MCP 工具返回远程 URL
3. curl 下载 HTML 成功
4. 多次尝试提取：
   - 正则匹配中文块：提取到 5 个文本块
   - 匹配关键段落：成功获取核心观点
5. 同时获取 arXiv 论文摘要作为背景资料

### 提取结果示例

```markdown
【标题】撕开Claude Code真相：让它好用的98.4%，是工程不是AI

【关键段落】
1. 一匹马可以跑得很快很有力，但它自己不知道往哪儿走：整套挽具决定了它的方向。
2. 问题回到普通开发者这里：如果范式已经转移，作为一个普通工程师，今天就能做点什么。
3. 未来五年，工程师的能力曲线正在从「我能写多少行代码」转向「我能为AI设计多严格的工作环境」。
```
