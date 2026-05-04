---
name: github-trending-stats
title: 获取 GitHub 近期增星最快项目
description: 通过 GitHub API 获取最近创建、增星最快的热门项目统计
---

# 获取 GitHub 近期增星最快项目

获取 GitHub 上近期（最近1-2个月）创建且增星最快的热门项目统计，生成可读性报告。

## 快速开始

使用 GitHub API + Python 直接获取数据，无需第三方登录或 token（公共API足够）。

```python
import json
import urllib.request
from datetime import datetime

# 查询最近2个月创建、星数超过1000的项目，按总星数降序
url = "https://api.github.com/search/repositories?q=stars:>1000+created:2026-02-01..*&sort=stars&order=desc"
req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})

with urllib.request.urlopen(req) as response:
    data = json.load(response)

items = data.get('items', [])[:15]
now = datetime.utcnow()

results = []
for i, item in enumerate(items, 1):
    full_name = item['full_name']
    stars = item['stargazers_count']
    description = item['description'] or '-'
    language = item['language'] or '-'
    created_at = item['created_at']
    html_url = item['html_url']
    
    # 计算创建天数
    created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    days_since = (now - created).days
    if days_since <= 0:
        days_since = 1
    daily_avg = stars // days_since
    
    results.append({
        'rank': i,
        'full_name': full_name,
        'stars': stars,
        'daily_avg': daily_avg,
        'description': description,
        'language': language,
        'url': html_url,
        'days_since': days_since
    })

# 输出 markdown
output = "# GitHub 近期增星最快项目 (最近2个月)\n\n"
output += "| # | 项目 | 总星数 | 已创建天数 | 日均增星 | 语言 |\n"
output += "|---|------|-------:|-----------:|---------:|------|\n"
for r in sorted(results, key=lambda x: -x['daily_avg']):
    output += f"| {r['rank']} | **[{r['full_name']}]({r['url']})** | {r['stars']:,} | {r['days_since']} | **{r['daily_avg']}+** | {r['language']} |\n"

output += "\n## 项目简述\n\n"
for r in sorted(results, key=lambda x: -x['daily_avg']):
    output += f"**{r['rank']}. {r['full_name']}** - ⭐ {r['stars']:,} (≈{r['daily_avg']}/天)\n"
    output += f"- 描述: {r['description'][:120]}\n"
    output += f"- 语言: {r['language']}\n\n"

print(output)
```

## 方法要点

1. **搜索查询语法**：`stars:>1000+created:YYYY-MM-DD..*` 筛选指定时间创建且超过一定星数的项目
2. **排序**：`sort=stars&order=desc` 按总星数降序，总星数高的自然增速快
3. **日增估算**：根据创建日期计算平均每日新增，简单有效
4. 使用 Python `urllib` 直接请求，避免 shell 转义问题

## 输出格式

生成 markdown 表格 + 项目简述，方便阅读和分享。

## 陷阱规避

- 直接在 shell 中写复杂的 `python -c` 会遇到大量转义问题，容易语法错误
- 使用 `execute_code` 工具直接运行完整 Python 代码更可靠
- GitHub API 公共速率限制足够获取前15个结果，不需要认证

## 适用场景

- 用户问"最近GitHub有什么热门项目"
- 用户问"近期增星最快的开源项目"
- 技术趋势追踪