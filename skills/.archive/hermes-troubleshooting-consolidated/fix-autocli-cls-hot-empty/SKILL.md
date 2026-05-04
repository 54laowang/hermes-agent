---
name: fix-autocli-cls-hot-empty
title: 修复 AutoCLI 财联社热点返回空数据问题
description: 解决 AutoCLI cls hot 返回 empty 问题，包括固定时间戳和浏览器内存问题
---

# 修复 AutoCLI 财联社热点返回空数据问题

## 问题现象
- `autocli cls hot` 返回 `(empty)`，没有任何数据
- 定时任务抓取失败，无法生成每日财联社热点推送
- 进程被系统杀死 `Killed: 9`，因为浏览器模式内存不足

## 根因分析
1. **固定时间戳问题**：AutoCLI 自动生成的配置中，API URL 的 `lastTime` 和 `last_time` 参数写死了一个过期时间戳，财联社API返回空数据
2. **浏览器模式问题**：配置默认启用 `browser: true`，需要启动浏览器进行抓取，在内存有限的环境下进程会被 OOM 杀死

## 修复步骤

### 步骤1：修复 AutoCLI 配置（如果继续使用 AutoCLI）
文件位置：`~/.autocli/adapters/cls/hot.yaml`

将固定时间戳改为动态生成：

```javascript
(async () => {
  const lastTime = Math.floor(Date.now() / 1000);
  const res = await fetch(`https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&lastTime=${lastTime}&last_time=${lastTime}&os=web&refresh_type=1&rn=20&sv=8.4.6`, {
    credentials: 'include'
  });
  const data = await res.json();
  return (data?.data?.roll_data || []);
})()
```

### 步骤2：推荐方案 - 改用 Python 直接请求 API（绕过浏览器内存问题）

修改 `daily-cls-ingest.py` 中的 `fetch_cls_hot()` 函数：

```python
def fetch_cls_hot() -> list:
    """直接请求财联社API抓取热门新闻"""
    print("🔍 正在抓取财联社热门新闻...")
    last_time = int(time.time())
    url = f"https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&lastTime={last_time}&last_time={last_time}&os=web&refresh_type=1&rn=20&sv=8.4.6"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.cls.cn/",
        "Origin": "https://www.cls.cn"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"❌ 请求失败: HTTP {resp.status_code}")
            return []
        
        data = resp.json()
        roll_data = data.get("data", {}).get("roll_data", [])
        
        # 过滤掉标题为空的条目
        result = []
        for i, item in enumerate(roll_data, 1):
            title = item.get('title', '').strip()
            if title:  # 只保留有标题的
                result.append({
                    'rank': str(i),
                    'title': title,
                    'reading_num': str(item.get('reading_num', 0)),
                    'author': item.get('author', '-') or '-'
                })
        
        print(f"✅ 抓取到 {len(result)} 条有效热门主题")
        return result
    except Exception as e:
        print(f"❌ 抓取异常: {e}")
        return []
```

需要导入 `time` 模块：

```python
import os
import subprocess
import json
import requests
import time  # 新增
from datetime import datetime
from pathlib import Path
```

## 验证
运行脚本验证修复效果：

```bash
python3 /Users/me/.hermes/scripts/daily-cls-ingest.py
```

正常输出应类似：
```
🔍 正在抓取财联社热门新闻...
✅ 抓取到 12 条有效热门主题
💾 原始数据已保存: /Users/me/Documents/Obsidian/AI-NEWS-HUB/raw/daily-finance/YYYY-MM-DD.json
📄 每日汇总页面已生成: ...
```

## 要点
- API 本身不需要 Cookie 即可访问，直接请求就能拿到数据
- 需要过滤掉空标题条目，API 返回的数据中有些条目标题为空
- 动态时间戳保证每次能拉取到最新热点
- 绕过浏览器模式解决内存不足问题，更稳定可靠
