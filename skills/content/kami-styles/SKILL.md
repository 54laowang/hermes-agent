---
name: kami-styles
description: Kami 排版系统 - 专业文档视觉设计。暖色画布、墨蓝强调、衬线字体层级。8种文档模板（单页简报/长文档/信函/作品集/简历/幻灯片/股票报告/更新日志），中英文双语。触发词：「做PDF/排版/一页纸/白皮书/作品集/简历/PPT/slides」或「build me a resume/make a one-pager/design a slide deck」。
version: 1.0.0
category: content
keywords:
  - kami
  - typeset
  - pdf
  - document
  - design
  - template
---

# Kami 排版系统

**紙 · かみ** - 内容落地的纸张。

好的内容值得好的排版。一套设计语言，八种文档类型：暖色画布、墨蓝强调、衬线字体层级、紧凑编辑节奏。

---

## 快速开始

### 语言匹配

| 用户语言 | 模板后缀 |
|---------|---------|
| 中文 | `*.html` / `slides.py` |
| 英文 | `*-en.html` / `slides-en.py` |
| 日文 | `*.html`（最佳努力，需视觉验证） |

### 文档类型选择

| 用户说 | 文档类型 | 中文模板 | 英文模板 |
|-------|---------|---------|---------|
| 一页纸/方案/执行摘要 | One-Pager | `one-pager.html` | `one-pager-en.html` |
| 白皮书/长文/年度总结 | Long Doc | `long-doc.html` | `long-doc-en.html` |
| 正式信件/推荐信 | Letter | `letter.html` | `letter-en.html` |
| 作品集/案例 | Portfolio | `portfolio.html` | `portfolio-en.html` |
| 简历/CV | Resume | `resume.html` | `resume-en.html` |
| PPT/演示/幻灯片 | Slides | `slides-weasy.html` | `slides-weasy-en.html` |
| 股票分析/估值报告 | Equity Report | `equity-report.html` | `equity-report-en.html` |
| 更新日志/版本记录 | Changelog | `changelog.html` | `changelog-en.html` |

---

## 设计规范

### 核心原则

- 画布：`#f5f4ed` 暖色画布，绝不用纯白
- 强调色：墨蓝 `#1B365D`，唯一彩色
- 中性色：暖调（黄棕底色），不用冷蓝灰
- 衬线字体：正文 400，标题 500，避免合成粗体
- 行高：紧凑标题 1.1-1.3，密集正文 1.4-1.45，阅读正文 1.5-1.55
- 阴影：环形或轻柔，不用硬阴影
- 标签：纯色十六进制背景，不用 rgba

### 字体

| 语言 | 主字体 | 回退链 |
|------|--------|-------|
| 中文 | TsangerJinKai02 | Source Han Serif SC → Noto Serif CJK SC → 宋体 |
| 英文 | Charter | 系统衬线 |
| 日文 | YuMincho | Hiragino Mincho ProN → Noto Serif CJK JP |

---

## 图表类型

| 用户说 | 图表 | 模板 |
|-------|------|------|
| 架构图/系统图 | Architecture | `assets/diagrams/architecture.html` |
| 流程图/决策流 | Flowchart | `assets/diagrams/flowchart.html` |
| 象限图/优先级矩阵 | Quadrant | `assets/diagrams/quadrant.html` |
| 柱状图/分类对比 | Bar Chart | `assets/diagrams/bar-chart.html` |
| 折线图/趋势/股价 | Line Chart | `assets/diagrams/line-chart.html` |
| 环形图/占比/分布 | Donut Chart | `assets/diagrams/donut-chart.html` |
| 状态机/生命周期 | State Machine | `assets/diagrams/state-machine.html` |
| 时间线/里程碑 | Timeline | `assets/diagrams/timeline.html` |
| 泳道图/跨角色流程 | Swimlane | `assets/diagrams/swimlane.html` |
| 树状图/层级结构 | Tree | `assets/diagrams/tree.html` |
| 分层图/架构栈 | Layer Stack | `assets/diagrams/layer-stack.html` |
| 维恩图/交集关系 | Venn | `assets/diagrams/venn.html` |
| K线图/股价走势 | Candlestick | `assets/diagrams/candlestick.html` |
| 瀑布图/收入桥 | Waterfall | `assets/diagrams/waterfall.html` |

---

## 使用流程

1. **确认语言**：匹配用户语言选择模板
2. **确认文档类型**：根据关键词选择模板
3. **填充内容**：使用模板生成 HTML
4. **生成 PDF**：运行 `python3 scripts/build.py`

---

## 常见陷阱

1. 标签用 rgba 会导致 WeasyPrint 双矩形 bug → 用纯色十六进制
2. 细边框 + 圆角会导致双环 → 边框 < 1pt 时避免圆角
3. 简历严格 2 页 → 小字体/回退字体/行高/边距变化会破坏
4. flex 内 break-inside 失效 → 用块级包装器
5. @page 下 height: 100vh 不可靠 → 用显式 mm 值
6. **WeasyPrint 依赖缺失** → macOS 需 `brew install pango gobject-introspection`，缺少时用浏览器打印fallback

## 层次感设计原则

用户反馈"缺乏层次感"时的增强策略：

### 视觉层次增强清单
1. **背景分层** - 顶部渐变背景、导语框高亮背景、左右栏独立色块
2. **序号标记** - 圆点序号代替短横线，增加视觉锚点
3. **Callout强化** - 品牌色背景（而非透明+边框），核心原则更醒目
4. **卡片立体** - 阴影效果 + 标题背景分层
5. **间距拉开** - 标签加大间距，元素间留白更多

### 具体实现（Pillow 代码参考）
```python
# 顶部渐变背景
for y in range(header_height):
    alpha = y / header_height
    # 颜色渐变...

# 导语框带背景
draw.rectangle([50, lead_y, width-50, lead_y + lead_height], fill=HIGHLIGHT_BG)

# 左右栏独立背景块
draw.rectangle([col1_x, col1_y, col1_x + col1_width, col1_y + 400], fill=IVORY)

# 序号圆点
draw.ellipse([col1_x + 20, y_offset + 5, col1_x + 36, y_offset + 21], fill=BRAND)

# Callout 品牌色背景（关键！）
draw.rectangle([50, callout_y, width-50, callout_y + callout_height], fill=BRAND)

# 卡片阴影
draw.rectangle([card_x + 3, card_y + 3, card_x + card_width + 3, card_y + card_height + 3], fill="#d0cdc4")
draw.rectangle([card_x, card_y, card_x + card_width, card_y + card_height], fill=IVORY)
```

### 对比原则
| 元素 | 平面设计 | 层次设计 |
|------|---------|---------|
| 顶部 | 单色背景 | 渐变背景 |
| 导语 | 无背景 | 高亮背景框 |
| 两栏 | 同一平面 | 独立背景块 |
| 列表 | 短横线 | 序号圆点 |
| Callout | 旁注样式 | 品牌色背景强调 |
| 卡片 | 扁平 | 阴影 + 标题背景 |
| 标签 | 紧凑 | 加大间距 |
7. **信息图缺乏层次感** → 使用渐变背景 + 独立色块 + 序号标记 + Callout背景色 + 卡片阴影（见 `references/mobile-infographic-pillow.md`）

## PDF 生成故障排除

### 依赖问题（macOS 常见）

WeasyPrint 需要 GObject/Pango 系统库：
```bash
# 安装依赖
brew install pango gobject-introspection

# 重新运行
python3 scripts/build.py <input.html>
```

### 备用方案 1：ReportLab（推荐）

**ReportLab 是 macOS 上最可靠的 PDF 方案**，不依赖系统库：

```bash
# 安装
pip3 install --user reportlab

# 使用 Python 脚本生成 PDF（见 scripts/generate_pdf.py）
python3 /path/to/generate_pdf.py
```

**优势**：
- 无系统依赖，纯 Python 方案
- 支持中文（自动检测系统字体）
- 表格、样式、分页完整支持
- 输出体积小（约 150-200KB）

**适用场景**：
- WeasyPrint 依赖问题无法解决
- 需要自动化批量生成
- 服务器环境无 GUI

### 备用方案 2：浏览器打印

当工具链都失败时，**浏览器打印是最终 fallback**：

```bash
# 1. 在浏览器中打开 HTML
open /path/to/document.html

# 2. 用户手动：Cmd+P → 另存为 PDF
```

**优势**：
- 零依赖，始终可用
- 输出质量与 WeasyPrint 一致（相同的 CSS @page 规则）

**触发条件**：
- WeasyPrint 和 ReportLab 都失败
- 用户需要"马上拿到 PDF"且不愿等待依赖安装

---

## 参考资料

- `references/design.md` - 完整设计规范
- `references/writing.md` - 内容策略和质量标准
- `references/production.md` - 构建和故障排除
- `references/diagrams.md` - 图表选择指南
- `references/pdf-generation-fallbacks.md` - PDF 工具链故障排除与浏览器打印备用方案
- `references/macos-font-fallback.md` - macOS 字体回退方案（Pillow 实践 + 层次增强技巧）
- `references/mobile-infographic-pillow.md` - 移动端信息图生成（Pillow 快速方案）
- `CHEATSHEET.md` - 快速参考

## 脚本工具

- `scripts/generate_pdf.py` - ReportLab PDF 生成器（WeasyPrint 失败时的备用方案）

---

## 品牌配置（可选）

创建 `~/.config/kami/brand.md` 存储个人品牌信息：

```yaml
---
name: 你的名字
role: 你的职位
email: your@email.com
website: https://your-site.com
brand_color: "#1B365D"
language: zh
page_size: A4
---

品牌介绍和个人偏好...
```

---

## 输出示例

生成文档后，输出格式：

```
✅ 文档已生成：
- HTML: /path/to/document.html
- PDF: /path/to/document.pdf
```
