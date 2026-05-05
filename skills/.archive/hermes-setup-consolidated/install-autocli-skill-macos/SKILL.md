---
name: install-autocli-skill-macos
description: 在 macOS 上安装和配置 autocli + autocli-skill，处理 sudo 权限问题
---

# install-autocli-skill-macos

在 macOS 上安装和配置 autocli + autocli-skill 的完整步骤。

## 描述

autocli 是一个用 Rust 编写的极速 CLI 工具，支持 55+ 主流平台（B站、知乎、微博、Twitter、YouTube、雪球等），复用 Chrome 登录会话，不需要 API Key。本技能记录了在 macOS 上手动安装的完整流程（处理 sudo 密码问题）。

## 安装步骤

### 1. 下载最新版本二进制

```bash
cd /tmp
curl -L -o autocli.tar.gz https://github.com/nashsu/autocli/releases/latest/download/autocli-aarch64-apple-darwin.tar.gz
tar xzf autocli.tar.gz
```

### 2. 安装到 ~/.local/bin（不需要 sudo）

```bash
mkdir -p ~/.local/bin
cp /tmp/autocli ~/.local/bin/
chmod +x ~/.local/bin/autocli
```

### 3. 添加到 PATH（如果还没有）

检查 `~/.zshrc` 是否包含：
```bash
export PATH="$HOME/.local/bin:$PATH"
```

重新加载：
```bash
source ~/.zshrc
```

### 4. 验证安装

```bash
autocli --version
# 应该输出: autocli X.X.X

autocli doctor
```

### 5. 安装 autocli-skill 到 Hermes

```bash
cd /Users/me
git clone https://github.com/nashsu/autocli-skill.git
cp -r ./autocli-skill ~/.hermes/skills/
```

### 6. 安装 Chrome 扩展（必需，Browser 模式需要）

1. 从 https://github.com/nashsu/autocli/releases/latest 下载 `autocli-chrome-extension.zip`
2. 解压到任意目录
3. 打开 Chrome → 访问 `chrome://extensions`
4. 开启右上角「开发者模式」
5. 点击「加载已解压的扩展程序」，选择解压后的文件夹
6. 扩展安装后会自动连接 autocli daemon

## 验证安装

测试 Public 模式（无需扩展）：
```bash
autocli hackernews top --limit 5 --format table
```

应该能看到表格形式的热门文章。

## 常见问题

**Q: `autocli: command not found`**  
A: 确认 `~/.local/bin` 在 PATH 中，或者用完整路径 `/Users/me/.local/bin/autocli`

**Q: Chrome 扩展显示无法连接**  
A: 确认 `autocli doctor` 显示 `Daemon running`，重启 Chrome 扩展

**Q: 网络问题无法从 GitHub 下载**  
A: 可以使用代理下载后手动放到 `~/.local/bin/`

## 支持的模式

- **Public**: 公开 API，无需浏览器/扩展 → 直接可用
- **Browser**: 需要 Chrome + 扩展 + 已登录 → 大部分国内网站需要
- **Desktop**: 需要对应桌面应用运行 → 控制 Cursor/Notion/ChatGPT 等

## 使用方式

安装完成后，Hermes 会自动加载 skill，使用自然语言请求即可：
- "查一下 B 站今天热门"
- "搜索知乎上关于 AI 的讨论"
- "看微博热搜"
- "查询茅台股票行情"
- "获取 HackerNews 热门"

## 搭建 Hermes+AutoCLI+Obsidian 全自动化知识系统

### 概述
搭建每日自动抓取新闻 → 自动整理入库到 Obsidian → 定时运行的闭环系统。

### 步骤

#### 1. 创建自定义适配器

对于没有预定义适配器的网站，先生成初始配置，再探索修正：

```bash
# 生成初始配置
autocli generate "https://www.cls.cn/ --goal hot

# 探索API找到正确数据结构
autocli explore "https://www.cls.cn/"
```

财联社热点示例配置（`~/.autocli/adapters/cls/hot.yaml`）：

```yaml
name: "cls hot"
domain: "cls.cn"
url: "https://www.cls.cn/"
selectors:
  - name: "rank"
    selector: "index + 1"
  - name: "title"
    selector: "item.title"
  - name: "reading_num"
    selector: "item.reading_num"
  - name: "author"
    selector: "item.brief"
columns: ["rank", "title", "reading_num", "author"]
output: table
```

测试：
```bash
autocli cls hot
```

#### 2. 微信公众号文章提取适配器

微信反爬，需自定义适配器开启浏览器模式（`~/.autocli/adapters/weixin/article.yaml`）：

```yaml
name: "weixin article"
domain: "mp.weixin.qq.com"
url: "https://mp.weixin.qq.com/s/{{url}}"
browser: true
selectors:
  - name: "title"
    selector: "title"
  - name: "content"
    selector: "rich_media_content | html"
columns: ["title", "content"]
```

使用：
```bash
autocli weixin article --url "s/3G6Dw7Up_fFgu1gGzqrV2A"
```

#### 3. 创建 Obsidian LLM Wiki 目录结构

```bash
VAULT=~/Documents/Obsidian
mkdir -p $VAULT/AI-NEWS-HUB/{raw/daily-finance,raw/articles,entities,concepts,comparisons,queries,daily}
```

创建基础文件：
- `SCHEMA.md` — 定义领域规范和标签分类
- `index.md` — 内容索引
- `log.md` — 操作日志

#### 4. 自动化抓取脚本

完整 Python 脚本保存到 `~/.hermes/scripts/daily-cls-ingest.py`：

脚本功能：
1. 调用 `autocli cls hot` 获取热门新闻
2. 解析表格输出
3. 保存原始 JSON 到 `raw/daily-finance/`
4. 生成带 YAML frontmatter 的每日汇总页面
5. 自动更新 `index.md` 和 `log.md`

添加执行权限：
```bash
chmod +x ~/.hermes/scripts/daily-cls-ingest.py
```

完整脚本见 [references/daily-cls-ingest.py](./references/daily-cls-ingest.py]

#### 5. 测试运行

```bash
python3 ~/.hermes/scripts/daily-cls-ingest.py
```

成功输出：
```
✅ 抓取到 10 条热门主题
💾 原始数据已保存
📄 每日汇总页面已生成
🔄 index.md 已更新
📝 log.md 已更新
✅ 完成！今日热点已入库
```

#### 6. 配置定时任务

使用 Hermes cronjob 创建每日定时任务：

```python
cronjob {
  "action": "create",
  "name": "每日财联社热点自动入库",
  "prompt": "每日自动运行财联社财经新闻抓取入库脚本",
  "schedule": "0 18 * * *"  # 每天 18:00 运行
}
```

### 常见问题

**Q: 自动生成后抓取为空**  \nA: 自动选择器通常不正确，必须 `autocli explore` 找到正确路径后手动修正。

**Q: 表格解析包含表头行**  \nA: 在解析代码中跳过表头：`if title != 'title': data.append(...)`

**Q: X/Twitter 抓取为空**  \nA: 需要 Chrome 已登录，否则无法访问。改用公开新闻源更稳定。

**Q: 微信提取失败**  \nA: 确认 `browser: true` 必须开启，Chrome 扩展必须安装正确。
