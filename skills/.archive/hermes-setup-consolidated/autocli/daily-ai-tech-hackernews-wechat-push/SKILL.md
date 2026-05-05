---
name: daily-ai-tech-hackernews-wechat-push
description: 每日从 HackerNews 抓取AI科技资讯 → 翻译中文标题 → 更新 Obsidian → 推送到微信 自动化工作流
---

# 每日 HackerNews AI 资讯自动抓取推送工作流

本技能描述了 `daily-ai-tech.py` 脚本执行后的后续处理流程，从脚本输出中提取JSON数据，翻译标题，更新Obsidian并推送微信。

## 工作流程

### 1. 运行抓取脚本
```bash
python /Users/me/.hermes/scripts/daily-ai-tech.py
```

**⚠️ 重要：如果 autocli 未安装导致脚本失败**，请不要使用 `npm install -g autocli`（那是不同的项目）。可以直接使用 HackerNews 官方 API 作为 fallback（零依赖）：
```python
import requests
# 获取 Top 30 stories
top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
top_ids = requests.get(top_stories_url).json()[:30]
# 获取每条文章详情
for story_id in top_ids:
    story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json").json()
    # 处理数据...
```

脚本已经完成：
- 抓取 HackerNews Top 30
- 筛选 AI 科技相关内容
- 输出 JSON 数据包裹在 `--- RAW JSON DATA ---` 和 `--- END RAW DATA ---` 之间
- 创建 Obsidian 基础文件 `YYYY-MM-DD.md` 并填入英文标题（中文位置为 `*待翻译*`）

### 2. 提取并解析 JSON
使用正则表达式从输出中提取 JSON 字符串，解析为文章列表。

### 3. 翻译英文标题为中文
保持专业术语准确性，简洁翻译：
- "OpenAI ad partner now selling ChatGPT ad placements based on “prompt relevance”" → "OpenAI广告合作伙伴基于「提示相关性」售卖ChatGPT广告位"
- "Soul Player C64 – A real transformer running on a 1 MHz Commodore 64" → "Soul Player C64：在1MHz commodore 64上运行的真正Transformer"
- "Deezer says 44% of songs uploaded to its platform daily are AI-generated" → "Deezer：平台每日上传歌曲中44%由AI生成"
- "Ternary Bonsai: Top Intelligence at 1.58 Bits" → "三元盆景：1.58比特实现顶级智能"
- "AI Resistance: some recent anti-AI stuff that's worth discussing" → "AI抵抗运动：近期值得讨论的反AI内容"
- "Kimi K2.6: Advancing open-source coding" → "Kimi K2.6：推进开源编码能力"

### 4. 更新 Obsidian 文件
将表格中的 `*待翻译*` 替换为翻译后的中文标题：
- 文件路径：`~/Documents/Obsidian/AI-NEWS-HUB/ai-daily/YYYY-MM-DD.md`
- 表格格式已预先创建，只需要替换占位符

### 5. 生成微信推送内容
格式：
```
🤖 **每日AI科技资讯 | YYYY-MM-DD (HackerNews Top 30 筛选)**

1. **中文标题1** - 得分 点 · 评论 评论
2. **中文标题2** - 得分 点 · 评论 评论
...

📍 完整内容（含英文原文）已自动入库到 Obsidian AI-NEWS-HUB/ai-daily/YYYY-MM-DD.md
```

### 6. 推送微信（关键说明）

根据 `setup-autocli-wechat-obsidian-automation` 技能的最佳实践：
- **如果 cronjob 已配置 `deliver: "weixin"`** → 只需要将推送内容作为最终回复输出即可，系统会自动投递到微信 home channel，不要重复调用 `send_message`
- **如果需要手动推送** → 依赖 Hermes 框架的 `send_message` 工具在任务上下文中调用，不要尝试用CLI命令推送

**常见陷阱避免：**
1. ❌ 不要尝试通过CLI调用 `send_message` — 不存在这个CLI命令，它是Hermes框架工具
2. ❌ 不要在已配置 `deliver` 的cronjob中重复调用 `send_message` — 会触发去重跳过
3. ✅ 直接输出最终推送内容作为回复，cron框架会自动处理投递

## cronjob 配置参考

```python
cronjob(action='create',
  name='每日AI科技资讯自动抓取推送',
  schedule='0 8 * * *',
  prompt='''
运行脚本 `/Users/me/.hermes/scripts/daily-ai-tech.py`，这会自动抓取HackerNews热门新闻并筛选出AI科技相关内容，输出原始JSON数据并存入Obsidian。

请从输出中提取 `--- RAW JSON DATA ---` 和 `--- END RAW DATA ---` 之间的JSON数据，为每篇文章将英文标题翻译成简洁中文（保持专业术语准确）。

翻译完成后：
1. 更新 Obsidian 文件 `~/Documents/Obsidian/AI-NEWS-HUB/ai-daily/YYYY-MM-DD.md`，填入翻译好的中文标题
2. 生成微信推送内容，全部使用中文标题，按照指定格式
3. 推送内容会由系统自动投递到微信 home channel（cron已配置 deliver），直接输出最终推送内容作为回复即可

推送完成后报告结果即可。
''',
  deliver='weixin'
)
```

## 文件位置
- 抓取脚本：`~/.hermes/scripts/daily-ai-tech.py`
- Obsidian 目录：`~/Documents/Obsidian/AI-NEWS-HUB/`
- 每日文章：`ai-daily/YYYY-MM-DD.md`
- 原始JSON：`raw/daily-ai/YYYY-MM-DD.json`
