---
name: setup-autocli-wechat-obsidian-automation
description: 在 Hermes 中搭建 AutoCLI + 微信推送 + Obsidian 全自动知识入库工作流，从财联社等来源抓取内容自动归档到 Obsidian 知识库并推送日报到微信
---

# AutoCLI + 微信推送 + Obsidian 自动化知识工作流搭建

本技能指导你搭建一套类似文章《Hermes+AutoCLI+Obsidian： 打造自动入库、自动整理、自动微信汇报的知识系统》描述的完整自动化系统。

## 适用场景

- 每日定时抓取财经热点、AI资讯等内容
- 自动整理成 LLM Wiki 格式存入 Obsidian 知识库
- 自动推送当日热点列表到微信
- 形成「抓取→整理→推送→存档」的闭环工作流

## 前置条件

- 已安装 autocli (`autocli --version` 可验证)
- 已配置微信消息推送（Hermes 已连接微信）
- Obsidian 知识库已创建
- Hermes cronjob 功能可用

## 搭建步骤

### 1. 安装 autocli-skill

```bash
# Clone autocli-skill 到 hermes skills 目录
cd ~/.hermes/skills
git clone https://github.com/nashsu/autocli-skill.git
cd autocli-skill
chmod +x ./install.sh
./install.sh
```

安装后验证：
```bash
autocli --version
```

如果输出版本信息表示安装成功。

### 2. 创建目录结构

在 Obsidian vault 中创建知识库目录：

```bash
mkdir -p ~/Documents/Obsidian/AI-NEWS-HUB/{daily,raw/daily-finance,raw/articles,entities,concepts,comparisons,queries}
```

### 2. 初始化 LLM Wiki 基础文件

根据你的领域（比如财经新闻）创建基础文件：

- `SCHEMA.md` — 定义领域、约定、标签分类
- `index.md` — 内容索引
- `log.md` — 操作日志

模板参考[llm-wiki](research/llm-wiki)技能。

### 3. 创建/修复 AutoCLI 适配器

对于需要抓取的网站（如财联社）：

```bash
# 如果自动生成不正确，使用 explore 分析接口
autocli explore "https://www.cls.cn"
# 手动编辑修正选择器
vim ~/.autocli/adapters/cls/hot.yaml
```

财联社热点的正确选择器：
- `title: item.title`（自动生成经常错写成 `item.ad.title`）
- 输出列：`["rank", "title", "reading_num", "author", "time"]`

### 4. 创建自动化 Python 脚本

脚本路径：`~/.hermes/scripts/daily-cls-ingest.py`

功能要点：
1. 调用 `autocli cls hot` 获取数据
2. 解析表格输出（autocli 默认不输出JSON）
3. 保存原始JSON到 `raw/daily-finance/YYYY-MM-DD.json`
4. 生成 Obsidian 格式每日汇总页面到 `daily/YYYY-MM-DD.md`
5. 更新 `index.md`（添加今日链接、更新总页数）
6. 更新 `log.md`（追加操作日志）
7. 输出 `--- WECHAT PUSH ---` 包裹的推送内容供 cronjob 提取

完整脚本代码示例：

```python
#!/usr/bin/env python3
"""
每日财联社热门新闻自动抓取入库脚本
适配 Hermes + AutoCLI + Obsidian 工作流
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 配置
VAULT_PATH = Path(os.path.expanduser("~/Documents/Obsidian/AI-NEWS-HUB"))
RAW_DIR = VAULT_PATH / "raw" / "daily-finance"
DAILY_DIR = VAULT_PATH / "daily"

def fetch_cls_hot() -> list:
    """使用autocli抓取财联社热门新闻，解析表格输出"""
    result = subprocess.run(['autocli', 'cls', 'hot'], 
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
            if len(cols) >= 4:
                rank, title, reading, author = cols[:4]
                if title != 'title':
                    data.append({
                        'rank': rank,
                        'title': title,
                        'reading_num': reading,
                        'author': author
                    })
    print(f"✅ 抓取到 {len(data)} 条热门主题")
    return data

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
title: 每日财经热点 {today}
created: {today}
updated: {today}
type: daily
tags: [每日汇总]
sources: [{str(raw_file.relative_to(VAULT_PATH))}]
---

# 每日财经热点 {today}

## Top 热门主题

| # | 标题 | 阅读量 | 来源 |
|---|------|--------|------|
"""
    
    for i, item in enumerate(data[:20], 1):
        title = item.get('title', '').strip()
        reading = item.get('reading_num', '')
        author = item.get('author', '-')
        content += f"| {i} | {title} | {reading} | {author} |\n"
    
    content += """
## 热点分析

> （人工补充分析，或AI生成分析）

## 相关链接

<!-- 链接到相关实体/概念页面 -->

"""
    
    with open(daily_file, 'w', encoding='utf-8') as f:
        f.write(content)
    return daily_file

def update_index():
    index_path = VAULT_PATH / "index.md"
    today = datetime.now().strftime("%Y-%m-%d")
    
    def count_md(directory):
        return len(list(Path(directory).glob('*.md')))
    
    total = sum([
        count_md(VAULT_PATH / "entities"),
        count_md(VAULT_PATH / "concepts"),
        count_md(VAULT_PATH / "comparisons"),
        count_md(VAULT_PATH / "queries"),
        count_md(VAULT_PATH / "daily")
    ])
    
    with open(index_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if line.startswith('> 最新更新：'):
            new_lines.append(f'> 最新更新：{today} | 总页数：{total}\n')
        elif '## 每日汇总' in line:
            new_lines.append(line)
            new_lines.append(f"- [[{today}]] 每日财经热点汇总\n")
        else:
            new_lines.append(line)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def update_log():
    log_path = VAULT_PATH / "log.md"
    today = datetime.now().strftime("%Y-%m-%d")
    
    entry = f"\n## [{today}] daily-ingest | 财联社每日热门新闻自动抓取\n- 原始数据保存到 raw/daily-finance/{today}.json\n- 生成每日汇总页面 daily/{today}.md\n- 更新 index.md\n"
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(entry)

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    
    data = fetch_cls_hot()
    if not data:
        print("❌ 没有获取到数据")
        return 1
    
    raw_file = save_raw(data)
    daily_file = generate_daily_page(data, raw_file)
    update_index()
    update_log()
    
    # 输出推送内容供cronjob提取
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n--- WECHAT PUSH ---")
    print(f"📊 **财联社每日热门热点 | {today}**\n")
    for i, item in enumerate(data[:10], 1):
        title = item['title']
        reading = item['reading_num']
        print(f"{i}. **{title}** ({reading} 阅读)")
    print(f"\n📍 完整内容已自动入库到 Obsidian AI-NEWS-HUB/daily/{today}.md")
    print(f"--- END ---")
    
    print(f"\n✅ 全部完成！今日热点已入库")
    return 0

if __name__ == "__main__":
    exit(main())
```

### 5. 创建定时 cronjob

```python
cronjob create:
- action: create
- name: "每日财联社热点自动入库"
- schedule: "0 8 * * *" (每天早上8点)
- prompt: |
  运行脚本 `/Users/me/.hermes/scripts/daily-cls-ingest.py` 自动抓取财联社每日热门新闻，存入 Obsidian 知识库 `~/Documents/Obsidian/AI-NEWS-HUB/`。

  请捕获完整的脚本输出，找到 `--- WECHAT PUSH ---` 和 `--- END ---` 之间的内容，然后使用 send_message 工具将这段内容推送到微信 home channel。推送完成后报告结果即可。

  脚本已经抓取并生成了推送内容，你只需要提取内容并推送。
```

**重要：Hermes v0.10.0 已知行为变更**

❌ **错误做法**：在 cronjob 中同时使用 `deliver` + `send_message` 推送相同目标 — 会被去重机制跳过

✅ **正确做法**：使用 `deliver` 配置让 cron 系统自动投递最终回复到微信 home channel，无需在任务内部重复调用 `send_message`。cron 会自动将你的最终响应推送到目标频道。

**关键配置：**
- `WEIXIN_HOME_CHANNEL` 只需要配置纯ID，**不要带 `weixin:` 前缀**：
  ```bash
  hermes config set WEIXIN_HOME_CHANNEL o9cq80znDxnUb_ojFoc-8kBCdqdE@im.wechat
  ```
- 在 cronjob 创建时使用 `deliver: "weixin"` 来自动投递到 home channel：
  ```
  deliver: "weixin"
  ```

**去重机制**：如果 cronjob 已配置 `deliver`，任务内调用 `send_message` 到相同目标会被自动跳过（`skipped: true, reason: cron_auto_delivery_duplicate_target`），这是预期行为，不是错误。

### 6. 微信推送故障排查

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `Timeout context manager should be used inside a task` | cronjob `deliver` 在后台异步上下文推送，微信模块依赖当前会话的异步上下文 | 修改 cronjob prompt，让任务内部调用 `send_message`，不使用 `deliver` 字段 |
| `iLink sendmessage error: ret=-2` | Token无效/过期，或机器人无权限发送到该频道 | 检查 Token 是否正确，确认机器人已加入频道并有权限发送消息 |
| `No home channel set for weixin` | `WEIXIN_HOME_CHANNEL` 带了 `weixin:` 前缀 | 只设置纯ID：`hermes config set WEIXIN_HOME_CHANNEL o9cq80znDxnUb_ojFoc-8kBCdqdE@im.wechat` |
| 财联社数据抓取为空 | 自动生成的 CSS selector 错误 | 使用 `item.title` 而不是自动生成的 `item.ad.title` |
| `autocli cls hot` 返回 `(empty)` | 财联社接口无数据返回 | 可能是源网站结构变化或接口限流。验证：`autocli cls hot -v` 确认输出。解决：等待接口恢复，或更新 AutoCLI，或更换数据源 |
| `autocli` 编译后被 macOS `Killed: 9` 杀死 | 从源码编译后，新编译的二进制被 macOS  Gatekeeper 因为签名问题终止 | 问题通常出现在 `make install` 编译后。尝试：<br>1. `xattr -d com.apple.provenance /path/to/autocli`<br>2. 如果仍然被杀，下载预编译版本而不是源码编译 |
| HTTP 422 Unprocessable Entity | 旧版本 API 接口失效 | 需要升级到最新版本的 AutoCLI |

常见问题：

## 验证搭建成功

手动运行脚本：

```bash
python3 ~/.hermes/scripts/daily-cls-ingest.py
```

检查：
- `~/Documents/Obsidian/AI-NEWS-HUB/daily/YYYY-MM-DD.md` 已创建
- 表格格式正确
- `index.md` 已添加今日链接
- cronjob 运行后微信收到推送

## 扩展

要添加更多来源（比如微信公众号文章提取）：
1. 创建适配器：`autocli generate <url>` 或手动写 `weixin/article.yaml`
2. 开启 `browser: true` 绕过反爬
3. 使用 `autocli weixin article --url <url>` 提取全文
4. 可以扩展脚本自动将提取的文章存入 `raw/articles/` 并编译到知识库
