---
name: setup-daily-ai-tech-hackernews-autopush
description: 在 Hermes 中搭建 AutoCLI + HackerNews + 微信推送 + Obsidian 全自动每日AI科技资讯抓取入库工作流，解决微信推送手动触发报错问题
---

# 每日AI科技资讯自动抓取推送工作流

本技能指导你搭建一套从 HackerNews 抓取每日AI科技资讯，自动筛选存入 Obsidian 知识库并推送日报到微信的完整自动化系统。

## 适用场景

- 每日定时抓取 HackerNews Top 30 热门
- 自动筛选AI科技相关内容
- 自动整理成 Markdown 存入 Obsidian 知识库
- 自动推送当日热点列表到微信
- 形成「抓取→筛选→整理→推送→存档」的闭环工作流

## 前置条件

- 已正确安装 autocli (`autocli --version` 可验证)
  - **⚠️ 重要：不要用 npm 安装**！`npm install -g autocli` 安装的是一个完全不同的项目，不是 AutoCLI
  - autocli 是 Rust 二进制工具，正确安装方式：`curl -fsSL https://raw.githubusercontent.com/nashsu/AutoCLI/main/scripts/install.sh | sh`
  - 如果安装有问题，可以跳过 autocli 直接使用 **HackerNews 官方 API 作为 fallback**（见下文）
- 已配置微信消息推送（Hermes 已连接微信）
- Obsidian 知识库已创建
- Hermes cronjob 功能可用

## 搭建步骤

### 1. 创建目录结构

在 Obsidian vault 中创建知识库目录：

```bash
mkdir -p ~/Documents/Obsidian/AI-NEWS-HUB/{ai-daily,raw/daily-ai}
```

### 2. 创建自动化 Python 脚本

脚本路径：`~/.hermes/scripts/daily-ai-tech.py`

```python
#!/usr/bin/env python3
"""
每日AI科技资讯自动抓取入库脚本
适配 Hermes + AutoCLI + Obsidian 工作流
获取 HackerNews 热门AI科技资讯
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 配置
VAULT_PATH = Path(os.path.expanduser("~/Documents/Obsidian/AI-NEWS-HUB"))
RAW_DIR = VAULT_PATH / "raw" / "daily-ai"
DAILY_DIR = VAULT_PATH / "ai-daily"

def fetch_hackernews_top() -> list:
    """使用autocli抓取HackerNews热门新闻"""
    result = subprocess.run(['autocli', 'hackernews', 'top', '--limit', '30'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 抓取失败: {result.stderr}")
        return []
    
    lines = result.stdout.strip().split('\n')
    data = []
    in_table = False
    header_passed = False
    for line in lines:
        if '+-' in line:
            in_table = not in_table
            if in_table:
                header_passed = True
            continue
        if in_table and line.startswith('|') and header_passed:
            cols = [col.strip() for col in line.split('|')[1:-1]]
            if len(cols) >= 5:
                rank, title, score, author, comments = cols[:5]
                if title != 'title':
                    try:
                        data.append({
                            'rank': int(rank) if rank.isdigit() else 0,
                            'title': title,
                            'score': int(score) if score.isdigit() else 0,
                            'author': author,
                            'comments': int(comments) if comments.isdigit() else 0
                        })
                    except:
                        pass
    print(f"✅ 抓取到 {len(data)} 条热门文章")
    return data

def filter_ai_tech(data: list) -> list:
    """筛选AI和科技相关内容"""
    ai_keywords = [
        'ai', 'llm', 'gpt', 'claude', 'model', 'machine', 'learning', 
        'neural', 'transformer', 'diffusion', 'openai', 'anthropic',
        'hackernews', 'startup', 'gpu', 'chip', 'robot', 'agent',
        '3d', 'image', 'prompt', 'token', 'dataset', 'programming'
    ]
    filtered = []
    for item in data:
        title_lower = item['title'].lower()
        if any(keyword in title_lower for keyword in ai_keywords):
            filtered.append(item)
    return filtered

def save_raw(data: list) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    raw_file = RAW_DIR / f"{today}.json"
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return raw_file

def generate_daily_page(data: list, raw_file: Path) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = DAILY_DIR / f"{today}.md"
    
    content = f"""---
title: 每日AI科技资讯 {today}
created: {today}
updated: {today}
type: daily
tags: [AI, 科技资讯, 每日汇总]
sources: [{str(raw_file.relative_to(VAULT_PATH))}]
---

# 每日AI科技资讯 {today}

来自 HackerNews 热门中的AI科技相关内容

## 热门AI科技文章

| # | 标题 | 得分 | 作者 | 评论 |
|---|------|------|------|------|
"""
    
    for i, item in enumerate(data, 1):
        rank = item.get('rank', '')
        title = item.get('title', '').strip()
        score = item.get('score', '')
        author = item.get('author', '-')
        comments = item.get('comments', 0)
        content += f"| {i} | {title} | {score} | {author} | {comments} |\n"
    
    content += """

## 要点分析

> （可人工补充分析）

## 相关链接

<!-- 链接到相关概念页面 -->

"""
    
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    with open(daily_file, 'w', encoding='utf-8') as f:
        f.write(content)
    return daily_file

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    
    data = fetch_hackernews_top()
    if not data:
        print("❌ 没有获取到数据")
        return 1
    
    ai_data = filter_ai_tech(data)
    print(f"🔍 筛选出 {len(ai_data)} 条AI科技相关内容")
    
    raw_file = save_raw(ai_data)
    daily_file = generate_daily_page(ai_data, raw_file)
    
    # 输出推送内容供cronjob提取
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n--- WECHAT PUSH ---")
    print(f"🤖 **每日AI科技资讯 | {today} (HackerNews Top 30 筛选)**\n")
    
    if not ai_data:
        print("今日无AI科技热点，请稍后再试。")
    else:
        for i, item in enumerate(ai_data[:15], 1):
            title = item['title']
            score = item['score']
            comments = item.get('comments', 0)
            print(f"{i}. **{title}** - {score} 点 · {comments} 评论")
    
    print(f"\n📍 完整内容已自动入库到 Obsidian AI-NEWS-HUB/ai-daily/{today}.md")
    print(f"--- END ---")
    
    print(f"\n✅ 全部完成！今日AI资讯已入库")
    return 0

if __name__ == "__main__":
    exit(main())
```

### 3. 添加执行权限

```bash
chmod +x ~/.hermes/scripts/daily-ai-tech.py
```

### 4. 配置微信推送

```bash
# 在 config.yaml 中配置，去掉 weixin: 前缀
WEIXIN_HOME_CHANNEL: o9cq80znDxnUb_ojFoc-8kBCdqdE@im.wechat
```

**关键要点：**
- cronjob 的 `deliver` 推送会触发 `Timeout context manager should be used inside a task` 异步上下文错误，不要使用
- 在 cronjob prompt 中让 LLM 处理完翻译后，直接调用 `send_message` 工具推送是最可靠方案
- 配置中 `WEIXIN_HOME_CHANNEL` 需要去掉 `weixin:` 前缀，仅保留 ID

### 5. 更新脚本（支持中文翻译 + 无需额外 OpenAI API）

更新脚本路径：`~/.hermes/scripts/daily-ai-tech.py`，新版本输出原始 JSON 数据供 LLM 翻译：

完整脚本替换为：

```python
#!/usr/bin/env python3
"""
每日AI科技资讯自动抓取入库脚本
适配 Hermes + AutoCLI + Obsidian 工作流
获取 HackerNews 热门AI科技资讯
输出原始JSON数据，供后续翻译推送
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 配置
VAULT_PATH = Path(os.path.expanduser("~/Documents/Obsidian/AI-NEWS-HUB"))
OUTPUT_DIR = VAULT_PATH / "ai-daily"
RAW_DIR = VAULT_PATH / "raw" / "daily-ai"

# 创建目录
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_hackernews_top() -> list:
    """使用autocli抓取HackerNews热门新闻"""
    result = subprocess.run(['autocli', 'hackernews', 'top', '--limit', '30'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 抓取失败: {result.stderr}")
        return []
    
    lines = result.stdout.strip().split('\n')
    data = []
    in_table = False
    header_passed = False
    for line in lines:
        if '+-' in line:
            in_table = not in_table
            if in_table:
                header_passed = True
            continue
        if in_table and line.startswith('|') and header_passed:
            cols = [col.strip() for col in line.split('|')[1:-1]]
            if len(cols) >= 5:
                rank, title, score, author, comments = cols[:5]
                if title != 'title':
                    try:
                        data.append({
                            'rank': int(rank) if rank.isdigit() else 0,
                            'title': title,
                            'score': int(score) if score.isdigit() else 0,
                            'author': author,
                            'comments': int(comments) if comments.isdigit() else 0
                        })
                    except:
                        pass
    print(f"✅ 抓取到 {len(data)} 条热门文章")
    return data


def filter_ai_tech(data: list) -> list:
    """筛选AI和科技相关内容"""
    ai_keywords = [
        'ai', 'llm', 'gpt', 'claude', 'model', 'machine', 'learning', 
        'neural', 'transformer', 'diffusion', 'openai', 'anthropic',
        'hackernews', 'startup', 'gpu', 'chip', 'robot', 'agent',
        '3d', 'image', 'prompt', 'token', 'dataset', 'programming',
        'language', 'coding', 'github', 'python', 'javascript', 'rust',
        'docker', 'kubernetes', 'cloud', 'serverless'
    ]
    filtered = []
    for item in data:
        title_lower = item['title'].lower()
        if any(keyword in title_lower for keyword in ai_keywords):
            filtered.append(item)
    return filtered


def save_raw(data: list) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    raw_file = RAW_DIR / f"{today}.json"
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return raw_file


def generate_daily_page(data: list, raw_file: Path) -> Path:
    """生成Obsidian页面 - 保存中英文对照"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = OUTPUT_DIR / f"{today}.md"
    
    content = f"""---
title: 每日AI科技资讯 {today}
created: {today}
updated: {today}
type: daily
tags: [AI, 科技资讯, 每日汇总]
sources: [{str(raw_file.relative_to(VAULT_PATH))}]
---

# 每日AI科技资讯 {today}

来自 HackerNews 热门中的AI科技相关内容

## 热门AI科技文章

| # | 标题（中） | 原文标题 | 得分 | 作者 | 评论 |
|---|------|------|------|------|------|
"""
    
    # 占位，翻译由LLM完成后重新写入
    for i, item in enumerate(data, 1):
        rank = item.get('rank', '')
        title = item.get('title', '').strip()
        score = item.get('score', '')
        author = item.get('author', '-')
        comments = item.get('comments', 0)
        content += f"| {i} | *待翻译* | {title} | {score} | {author} | {comments} |\n"
    
    content += """

## 要点分析

> （可人工补充分析）

## 相关链接

<!-- 链接到相关概念页面 -->

"""
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(daily_file, 'w', encoding='utf-8') as f:
        f.write(content)
    return daily_file


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    data = fetch_hackernews_top()
    if not data:
        print("❌ 没有获取到数据")
        return 1
    
    ai_data = filter_ai_tech(data)
    print(f"🔍 筛选出 {len(ai_data)} 条AI科技相关内容")
    
    raw_file = save_raw(ai_data)
    daily_file = generate_daily_page(ai_data, raw_file)
    
    # 输出JSON数据供LLM翻译
    print("\n--- RAW JSON DATA ---")
    print(json.dumps(ai_data, ensure_ascii=False))
    print("--- END RAW DATA ---")
    
    print(f"\n✅ 抓取完成，数据已存入:")
    print(f"   原始数据: {raw_file}")
    print(f"   Obsidian: {daily_file}")
    return 0


if __name__ == "__main__":
    exit(main())
```

### 6. 添加执行权限

```bash
chmod +x /Users/me/.hermes/scripts/daily-ai-tech.py
```

### 7. 创建定时 cronjob

**重要提醒：** 直接使用 `deliver` 推送会导致 `Timeout context manager should be used inside a task` 异步上下文错误。必须由任务内部调用 `send_message` 推送。

正确的 cronjob prompt 应该是：

```
运行脚本 /Users/me/.hermes/scripts/daily-ai-tech.py，这会自动抓取HackerNews热门新闻并筛选出AI科技相关内容，输出原始JSON数据并存入Obsidian。

请从输出中提取 `--- RAW JSON DATA ---` 和 `--- END RAW DATA ---` 之间的JSON数据，为每篇文章将英文标题翻译成简洁中文（保持专业术语准确）。

翻译完成后：
1. 更新 Obsidian 文件 `~/Documents/Obsidian/AI-NEWS-HUB/ai-daily/YYYY-MM-DD.md`，填入翻译好的中文标题
2. 生成微信推送内容，全部使用中文标题，格式如下：
```
🤖 **每日AI科技资讯 | YYYY-MM-DD (HackerNews Top 30 筛选)**

1. **中文标题1** - 得分 点 · 评论 评论
2. **中文标题2** - 得分 点 · 评论 评论
...

📍 完整内容（含英文原文）已自动入库到 Obsidian AI-NEWS-HUB/ai-daily/YYYY-MM-DD.md
```
3. 使用 `send_message` 工具将生成的推送内容推送到微信 home channel
4. 推送完成后报告结果即可。
```

schedule: `0 8 * * *` (每天早 8 点)

## 验证搭建成功

手动运行脚本：

```bash
python3 ~/.hermes/scripts/daily-ai-tech.py
```

检查：
- `~/Documents/Obsidian/AI-NEWS-HUB/ai-daily/YYYY-MM-DD.md` 已创建
- 表格格式正确
- cronjob 运行后微信收到推送

## 优势

- **无需登录**: HackerNews Top API公开可访问，不需要Chrome浏览器登录，不需要扩展
- **自动筛选**: 自动识别AI科技关键词，只推送相关内容
- **零维护**: 基于autocli官方适配器，稳定可靠
- **完全自动化**: 抓取→筛选→存储→推送一条龙

## 常见坑点和解决方案

1. **`Timeout context manager should be used inside a task` 异步错误**
   - **原因：** 直接使用 cronjob `deliver` 字段推送会触发异步上下文错误
   - **解决：** 在 cronjob prompt 中让 Hermes 抓取后，自己调用 `send_message` 工具推送

2. **推送全是英文标题，用户需要中文标题**
   - **原因：** Python 脚本依赖 `OPENAI_API_KEY` 环境变量做翻译，但 cron job 运行时环境变量不可靠，经常丢失导致翻译跳过
   - **教训：** 不要让脚本依赖可能在 cron 中不可用的环境变量做翻译
   - **解决：** 脚本输出原始 JSON，由 Hermes LLM 在 cron job 中直接完成翻译，**不需要额外 OpenAI API key**。Obsidian 保留中英文对照，微信推送仅显示中文标题

3. **iLink 推送 ret=-2 错误 / Token 过期**
   - **原因：** Token 过期或不匹配
   - **解决：** 重新扫码配置后需要重启 Hermes gateway：
   ```bash
   launchctl stop ai.hermes.gateway
   sleep 2
   launchctl start ai.hermes.gateway
   ```

4. **send_message 在交互式会话报错 "No home channel set"**
   - **原因：** 当前 shell 环境没有读取到 gateway 的环境变量配置
   - **解决：** 不影响 cronjob，cronjob 在 gateway 环境中能正确读取配置

5. **关键词筛选不够准确**
   - **解决：** 修改脚本中 `filter_ai_tech` 函数的 `ai_keywords` 列表，添加你关注的关键词

7. **autocli 未安装 / 安装失败**
   - **原因：** autocli 是 Rust 二进制工具，不是 npm 包；或者系统缺少安装工具
   - **Fallback 方案：** 直接使用 HackerNews 官方 API（不需要任何工具安装），Python 代码示例：
   ```python
   def fetch_hackernews_top() -> list:
       """使用 HackerNews 官方 API 抓取热门新闻"""
       import requests
       top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
       response = requests.get(top_stories_url)
       top_ids = response.json()[:30]
       
       articles = []
       for i, story_id in enumerate(top_ids):
           story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
           story = requests.get(story_url).json()
           if story and 'title' in story:
               articles.append({
                   'rank': i + 1,
                   'title': story.get('title', ''),
                   'score': story.get('score', 0),
                   'author': story.get('by', '-'),
                   'comments': story.get('descendants', 0)
               })
       print(f"✅ 抓取到 {len(articles)} 条热门文章")
       return articles
   ```
   - **优点：** 零依赖，不需要安装 autocli，不需要 Chrome，API 稳定可靠
   - **适用场景：** 所有抓取 HackerNews 的场景，效果与 autocli 完全一致
