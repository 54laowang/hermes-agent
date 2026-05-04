---
name: arxiv
description: 使用 arXiv 免费 REST API 搜索和检索学术论文。无需 API 密钥。按关键词、作者、分类或 ID 搜索。可配合 web_extract 或 ocr-and-documents skill 阅读完整论文内容。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, Arxiv, Papers, Academic, Science, API]
    related_skills: [ocr-and-documents]
---

# arXiv Research

Search and retrieve academic papers from arXiv via their free REST API. No API key, no dependencies — just curl.

## Quick Reference

| Action | Command |
|--------|---------|
| Search papers | `curl "https://export.arxiv.org/api/query?search_query=all:QUERY&max_results=5"` |
| Get specific paper | `curl "https://export.arxiv.org/api/query?id_list=2402.03300"` |
| Read abstract (web) | `web_extract(urls=["https://arxiv.org/abs/2402.03300"])` |
| Read full paper (PDF) | `web_extract(urls=["https://arxiv.org/pdf/2402.03300"])` |

## Searching Papers

The API returns Atom XML. Parse with `grep`/`sed` or pipe through `python3` for clean output.

### Basic search

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5"
```

### Clean output (parse XML to readable format)

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5&sortBy=submittedDate&sortOrder=descending" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
for i, entry in enumerate(root.findall('a:entry', ns)):
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    published = entry.find('a:published', ns).text[:10]
    authors = ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))
    summary = entry.find('a:summary', ns).text.strip()[:200]
    cats = ', '.join(c.get('term') for c in entry.findall('a:category', ns))
    print(f'{i+1}. [{arxiv_id}] {title}')
    print(f'   Authors: {authors}')
    print(f'   Published: {published} | Categories: {cats}')
    print(f'   Abstract: {summary}...')
    print(f'   PDF: https://arxiv.org/pdf/{arxiv_id}')
    print()
"
```

## Search Query Syntax

| Prefix | Searches | Example |
|--------|----------|---------|
| `all:` | All fields | `all:transformer+attention` |
| `ti:` | Title | `ti:large+language+models` |
| `au:` | Author | `au:vaswani` |
| `abs:` | Abstract | `abs:reinforcement+learning` |
| `cat:` | Category | `cat:cs.AI` |
| `co:` | Comment | `co:accepted+NeurIPS` |

### Boolean operators

```
# AND (default when using +)
search_query=all:transformer+attention

# OR
search_query=all:GPT+OR+all:BERT

# AND NOT
search_query=all:language+model+ANDNOT+all:vision

# Exact phrase
search_query=ti:"chain+of+thought"

# Combined
search_query=au:hinton+AND+cat:cs.LG
```

## Sort and Pagination

| Parameter | Options |
|-----------|---------|
| `sortBy` | `relevance`, `lastUpdatedDate`, `submittedDate` |
| `sortOrder` | `ascending`, `descending` |
| `start` | Result offset (0-based) |
| `max_results` | Number of results (default 10, max 30000) |

```bash
# Latest 10 papers in cs.AI
curl -s "https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=10"
```

## Fetching Specific Papers

```bash
# By arXiv ID
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300"

# Multiple papers
curl -s "https://export.arxiv.org/api/query?id_list=2402.03300,2401.12345,2403.00001"
```

## BibTeX Generation

After fetching metadata for a paper, generate a BibTeX entry:

{% raw %}
```bash
curl -s "https://export.arxiv.org/api/query?id_list=1706.03762" | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
root = ET.parse(sys.stdin).getroot()
entry = root.find('a:entry', ns)
if entry is None: sys.exit('Paper not found')
title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
authors = ' and '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))
year = entry.find('a:published', ns).text[:4]
raw_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
cat = entry.find('arxiv:primary_category', ns)
primary = cat.get('term') if cat is not None else 'cs.LG'
last_name = entry.find('a:author', ns).find('a:name', ns).text.split()[-1]
print(f'@article{{{last_name}{year}_{raw_id.replace(\".\", \"\")},')
print(f'  title     = {{{title}}},')
print(f'  author    = {{{authors}}},')
print(f'  year      = {{{year}}},')
print(f'  eprint    = {{{raw_id}}},')
print(f'  archivePrefix = {{arXiv}},')
print(f'  primaryClass  = {{{primary}}},')
print(f'  url       = {{https://arxiv.org/abs/{raw_id}}}')
print('}')
"
```
{% endraw %}

## Reading Paper Content

After finding a paper, read it:

```
# Abstract page (fast, metadata + abstract)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper (PDF → markdown via Firecrawl)
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
```

For local PDF processing, see the `ocr-and-documents` skill.

## Common Categories

| Category | Field |
|----------|-------|
| `cs.AI` | Artificial Intelligence |
| `cs.CL` | Computation and Language (NLP) |
| `cs.CV` | Computer Vision |
| `cs.LG` | Machine Learning |
| `cs.CR` | Cryptography and Security |
| `stat.ML` | Machine Learning (Statistics) |
| `math.OC` | Optimization and Control |
| `physics.comp-ph` | Computational Physics |

Full list: https://arxiv.org/category_taxonomy

## Helper Script

The `scripts/search_arxiv.py` script handles XML parsing and provides clean output:

```bash
python scripts/search_arxiv.py "GRPO reinforcement learning"
python scripts/search_arxiv.py "transformer attention" --max 10 --sort date
python scripts/search_arxiv.py --author "Yann LeCun" --max 5
python scripts/search_arxiv.py --category cs.AI --sort date
python scripts/search_arxiv.py --id 2402.03300
python scripts/search_arxiv.py --id 2402.03300,2401.12345
```

No dependencies — uses only Python stdlib.

---

## Semantic Scholar (Citations, Related Papers, Author Profiles)

arXiv doesn't provide citation data or recommendations. Use the **Semantic Scholar API** for that — free, no key needed for basic use (1 req/sec), returns JSON.

### Get paper details + citations

```bash
# By arXiv ID
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,authors,citationCount,referenceCount,influentialCitationCount,year,abstract" | python3 -m json.tool

# By Semantic Scholar paper ID or DOI
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1234/example?fields=title,citationCount"
```

### Get citations OF a paper (who cited it)

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/citations?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

### Get references FROM a paper (what it cites)

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/references?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

### Search papers (alternative to arXiv search, returns JSON)

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=GRPO+reinforcement+learning&limit=5&fields=title,authors,year,citationCount,externalIds" | python3 -m json.tool
```

### Get paper recommendations

```bash
curl -s -X POST "https://api.semanticscholar.org/recommendations/v1/papers/" \
  -H "Content-Type: application/json" \
  -d '{"positivePaperIds": ["arXiv:2402.03300"], "negativePaperIds": []}' | python3 -m json.tool
```

### Author profile

```bash
curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=Yann+LeCun&fields=name,hIndex,citationCount,paperCount" | python3 -m json.tool
```

### Useful Semantic Scholar fields

`title`, `authors`, `year`, `abstract`, `citationCount`, `referenceCount`, `influentialCitationCount`, `isOpenAccess`, `openAccessPdf`, `fieldsOfStudy`, `publicationVenue`, `externalIds` (contains arXiv ID, DOI, etc.)

---

## Complete Research Workflow

1. **Discover**: `python scripts/search_arxiv.py "your topic" --sort date --max 10`
2. **Assess impact**: `curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID?fields=citationCount,influentialCitationCount"`
3. **Read abstract**: `web_extract(urls=["https://arxiv.org/abs/ID"])`
4. **Read full paper**: `web_extract(urls=["https://arxiv.org/pdf/ID"])`
5. **Find related work**: `curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID/references?fields=title,citationCount&limit=20"`
6. **Get recommendations**: POST to Semantic Scholar recommendations endpoint
7. **Track authors**: `curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=NAME"`

## Rate Limits

| API | Rate | Auth |
|-----|------|------|
| arXiv | ~1 req / 3 seconds | None needed |
| Semantic Scholar | 1 req / second | None (100/sec with API key) |

## Notes

- arXiv returns Atom XML — use the helper script or parsing snippet for clean output
- Semantic Scholar returns JSON — pipe through `python3 -m json.tool` for readability
- arXiv IDs: old format (`hep-th/0601001`) vs new (`2402.03300`)
- PDF: `https://arxiv.org/pdf/{id}` — Abstract: `https://arxiv.org/abs/{id}`
- HTML (when available): `https://arxiv.org/html/{id}`
- For local PDF processing, see the `ocr-and-documents` skill

## ID Versioning

- `arxiv.org/abs/1706.03762` always resolves to the **latest** version
- `arxiv.org/abs/1706.03762v1` points to a **specific** immutable version
- When generating citations, preserve the version suffix you actually read to prevent citation drift (a later version may substantially change content)
- The API `<id>` field returns the versioned URL (e.g., `http://arxiv.org/abs/1706.03762v7`)

## Withdrawn Papers

Papers can be withdrawn after submission. When this happens:
- The `<summary>` field contains a withdrawal notice (look for "withdrawn" or "retracted")
- Metadata fields may be incomplete
- Always check the summary before treating a result as a valid paper

---

## ✅ Done When 完成判据

> **核心思想**：从"我猜我做完了"变成"我能确认我做完了"

### 四大支柱

| 支柱 | 说明 | 本 Skill 对应 |
|------|------|--------------|
| **Goal** | 任务目标 | 成功搜索/获取论文并返回结构化信息 |
| **Context** | 上下文来源 | 用户查询关键词/作者/arXiv ID |
| **Constraints** | 约束条件 | API 响应时间、结果数量限制 |
| **Done When** | 完成判据 | 下方必检项 |

### 必检项（全部满足才算完成）

#### 【任务：论文搜索】

- [ ] **API 调用成功**
  - arXiv API 已调用（或 Semantic Scholar API）
  - HTTP 状态码 200
  - 响应内容已解析
  - **验证方法**：`curl` 返回有效 XML/JSON

- [ ] **搜索结果有效**
  - 返回论文数量 > 0
  - 每篇论文包含：标题、作者、发布日期、摘要、arXiv ID
  - 没有遇到"Paper not found"
  - **验证方法**：输出包含 ≥1 篇论文的完整信息

- [ ] **输出格式清晰**
  - 论文列表已编号
  - 每篇论文格式统一：
    ```
    1. [arXiv ID] 标题
       Authors: 作者列表
       Published: 发布日期 | Categories: 分类
       Abstract: 摘要前200字...
       PDF: https://arxiv.org/pdf/ID
    ```
  - **验证方法**：输出符合标准格式

- [ ] **排序正确**
  - 按要求排序（相关性/提交日期/更新日期）
  - 最新论文在前（如用户要求）
  - **验证方法**：检查论文日期顺序

#### 【任务：获取特定论文】

- [ ] **arXiv ID 有效**
  - ID 格式正确（新格式：`YYMM.NNNNN` 或旧格式：`类别/YYMMNNN`）
  - 论文存在（未被删除）
  - **验证方法**：`curl` 返回有效 `<entry>`

- [ ] **元数据完整**
  - 标题已提取
  - 作者列表已提取
  - 发布日期已提取
  - 摘要已提取
  - 分类已提取
  - PDF 链接已生成
  - **验证方法**：输出包含所有必要字段

- [ ] **版本信息明确**
  - 论文版本已标注（如有多个版本）
  - 使用的是最新版本（除非用户指定版本）
  - **验证方法**：输出包含版本号

#### 【任务：引用分析（Semantic Scholar）】

- [ ] **引用数据已获取**
  - 引用次数已获取
  - 影响力引用次数已获取（influentialCitationCount）
  - 参考文献数量已获取
  - **验证方法**：输出包含引用统计

- [ ] **引用/参考文献列表已生成**
  - 至少返回 10 条引用/参考文献
  - 每条包含：标题、作者、年份、引用次数
  - **验证方法**：输出包含引用列表

#### 【任务：BibTeX 生成】

- [ ] **BibTeX 格式正确**
  - 包含必要字段：title, author, year, eprint, url
  - BibTeX key 已生成（格式：`作者姓氏年份_ID`）
  - **验证方法**：输出符合 BibTeX 语法

### 可选项（加分项）

- [ ] **多个数据源交叉验证完成**
  - arXiv + Semantic Scholar 数据一致
  - **验证方法**：对比两个 API 的结果

- [ ] **论文影响力评估完成**
  - 引用次数已评估（高/中/低）
  - 作者影响力已评估（H-index、总引用数）
  - **验证方法**：输出包含影响力评价

- [ ] **相关论文推荐已提供**
  - 至少 5 篇相关论文
  - 推荐理由已说明
  - **验证方法**：输出包含「相关论文」章节

### 失败处理

| 失败场景 | 处理路径 | 用户提示 |
|---------|---------|---------|
| API 超时 | 重试 1 次 | ⚠️ arXiv API 响应慢，请稍候 |
| 无搜索结果 | 建议调整关键词 | ❌ 未找到相关论文，建议调整关键词 |
| 论文不存在 | 明确告知 | ❌ 该 arXiv ID 不存在或已删除 |
| 论文已撤回 | 标注撤回状态 | ⚠️ 该论文已被撤回，请核实 |
| Semantic Scholar 无数据 | 仅使用 arXiv | ⚠️ Semantic Scholar 暂无该论文引用数据 |

### 自检代码示例

```python
def verify_done_when(task_type, query=None, arxiv_id=None):
    """验证 Done When 是否满足"""
    
    if task_type == 'paper_search':
        # 检查 API 调用
        assert api_response is not None
        assert api_response.status_code == 200
        
        # 检查结果有效性
        papers = parse_papers(api_response)
        assert len(papers) > 0
        
        # 检查输出格式
        for paper in papers:
            assert 'arXiv ID' in paper
            assert '标题' in paper
            assert 'Authors' in paper
            assert 'PDF' in paper
    
    elif task_type == 'paper_fetch':
        # 检查 ID 有效性
        assert arxiv_id is not None
        assert paper_exists(arxiv_id)
        
        # 检查元数据完整
        paper = fetch_paper(arxiv_id)
        assert paper['title'] is not None
        assert paper['authors'] is not None
        assert paper['abstract'] is not None
    
    elif task_type == 'citation_analysis':
        # 检查引用数据
        assert 'citationCount' in output
        assert 'referenceCount' in output
        
        # 检查列表
        assert len(citations) >= 10 or len(references) >= 10
    
    elif task_type == 'bibtex':
        # 检查格式
        assert output.startswith('@article{')
        assert 'title' in output
        assert 'author' in output
        assert 'eprint' in output
    
    return True  # 所有检查通过
```
