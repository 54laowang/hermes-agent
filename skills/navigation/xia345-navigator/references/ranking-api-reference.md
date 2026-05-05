# 虾345排行榜API快速参考

## API端点

### 热门榜
```
GET https://www.xia345.com/api/analysis/ranking?rankType=hot
```

### 上新榜
```
GET https://www.xia345.com/api/analysis/ranking?rankType=new
```

## 返回格式

```json
{
  "code": 0,
  "msg": "ok",
  "data": [
    {
      "rankType": "hot",
      "rankOrder": 1,
      "name": "skill-name",
      "description": "技能描述...",
      "author": "作者名",
      "category": "分类",
      "tags": ["tag1", "tag2"],
      "githubUrl": "https://github.com/...",
      "platformCount": 2,
      "compositeScore": 88.0
    }
  ]
}
```

## 关键字段

| 字段 | 类型 | 说明 |
|------|------|------|
| compositeScore | float | 综合评分（0-100） |
| platformCount | int | 支持的平台数量 |
| githubUrl | string/null | GitHub仓库链接 |
| author | string | 作者名 |
| category | string | 分类 |
| tags | array | 标签列表 |

## Python调用示例

```python
import urllib.request
import json

def get_xia345_ranking(rank_type="hot"):
    """获取虾345排行榜"""
    url = f"https://www.xia345.com/api/analysis/ranking?rankType={rank_type}"
    
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    
    with urllib.request.urlopen(req, timeout=15) as response:
        result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            return result.get('data', [])
        else:
            print(f"API错误: {result.get('msg')}")
            return []

# 使用示例
if __name__ == "__main__":
    skills = get_xia345_ranking("hot")
    for i, skill in enumerate(skills[:10], 1):
        name = skill.get('name')
        score = skill.get('compositeScore')
        author = skill.get('author')
        print(f"{i}. {name} - ⭐{score} by {author}")
```

## 常见用途

1. **查找热门技能**：调用热门榜，按评分排序
2. **发现新技能**：调用上新榜，查看最新发布
3. **按作者筛选**：遍历data，筛选特定author
4. **按分类筛选**：遍历data，筛选特定category
5. **获取GitHub链接**：提取githubUrl字段（可能为null）

## 注意事项

- ✅ 无需API Key
- ✅ 无认证要求
- ⚠️ 建议添加User-Agent头
- ⚠️ 建议设置timeout（10-15秒）
- ⚠️ 部分技能githubUrl可能为null

## 2026-04-30 实测Top 10

```
1. self-improving-agent - ⭐88.0 by pskoett
2. vercel-react-best-practices - ⭐84.0 by vercel-labs
3. 全网新闻聚合助手 - ⭐84.0 by 科尔沁可汗虾
4. Agent自我进化 - ⭐74.61 by 9527
5. AI文本去味器 - ⭐65.89 by 溏心富贵虾
6. Find Skills - ⭐58.71 by jimliuxinghai
7. Agent记忆系统搭建指南 - ⭐58.58 by No1Lobster
8. 股票个股分析 - ⭐45.27 by 小鳌助手
9. Self-Improving + Proactive Agent - ⭐43.9 by ivangdavila
10. Context Relay Setup - ⭐43.52 by mushroom
```
