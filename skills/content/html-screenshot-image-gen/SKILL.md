---
name: html-screenshot-image-gen
description: 免费生图方案 - HTML 模板 + 浏览器截图，零 API 成本无限次出图
priority: P2
triggers:
  - 用户说"做成信息图"
  - 用户说"做成数据卡片"
  - 用户说"生成封面"
  - 用户说"做一张对比图"
  - 用户说"免费生图"
auto_load: false
---

# HTML 截图生图方案

## 核心原理

**把浏览器渲染引擎当成免费的图像生成器**

- HTML + CSS 像素级控制版式
- 中文渲染完美
- 完全免费，无限次使用
- 5 秒内生成高清 PNG

---

## 工作流程（三步）

### Step 1: 选择模板风格

根据用户触发词自动选择：

| 触发词 | 模板风格 | 适用场景 |
|--------|---------|---------|
| "做成信息图" | 米色暖系 | 步骤、列表、教程 |
| "做成数据卡片" | 深色极简 | 数据、金句、结论 |
| "生成封面" | 封面模板 | 公众号封面 |
| "做一张对比图" | 对比模板 | 双列对比 |

### Step 2: 填入动态内容

```python
# 从用户输入提取关键内容
title = "文章标题"
items = ["要点1", "要点2", "要点3"]
style = "warm"  # or "dark"

# 使用模板生成 HTML
html_content = generate_html(title, items, style)

# 保存到临时文件
write_file("/tmp/img-output/card.html", html_content)
```

### Step 3: 浏览器截图

```python
# 打开 HTML 文件
browser_navigate("file:///tmp/img-output/card.html")

# 截图保存
result = browser_vision("截图整个页面，展示完整视觉效果")

# 复制到输出目录
terminal(f"cp {result['screenshot_path']} /tmp/img-output/output.png")
```

---

## 内置模板

### 模板 A：米色暖系

**配色**：
- 背景：`#f5f0e8`（米色）
- 强调色：`#8b6f47`（棕褐）
- 文字：`#2d2d2d`（深灰）

**适用**：公众号配图、教程步骤、微信群精华

**HTML 模板**：见 `references/template-warm.html`

---

### 模板 B：深色极简

**配色**：
- 背景：`#0d0d0d`（纯黑）
- 强调色：`#4ade80`（荧光绿）
- 文字：`#ffffff`（白色）

**适用**：数据卡片、金句图、朋友圈传播

**HTML 模板**：见 `references/template-dark.html`

---

### 模板 C：封面模板

**尺寸**：1080x540px（公众号封面标准尺寸）

**特点**：标题居中 + 渐变背景

**HTML 模板**：见 `references/template-cover.html`

---

### 模板 D：对比模板

**布局**：双列 Grid

**适用**：工具对比、方案对比、前后对比

**HTML 模板**：见 `references/template-compare.html`

---

## 使用示例

### 示例 1：生成教程步骤信息图

**用户说**：
> "把这三点做成信息图：
> 1. 写 HTML 模板
> 2. 填入动态内容
> 3. 浏览器截图"

**执行流程**：
1. 提取标题：HTML 截图生图三步法
2. 提取列表：三个步骤
3. 选择模板：米色暖系（默认）
4. 生成 HTML → 截图 → 返回图片路径

**输出**：`/tmp/img-output/output.png`

---

### 示例 2：生成数据卡片

**用户说**：
> "做成数据卡片：效率提升 10 倍，成本降为零"

**执行流程**：
1. 提取核心数据：效率提升 10 倍
2. 提取补充信息：成本降为零
3. 选择模板：深色极简
4. 生成 HTML → 截图 → 返回图片路径

**输出**：`/tmp/img-output/output.png`

---

## 自定义模板

### 添加新模板

1. **创建 HTML 文件**
   - 路径：`references/template-{name}.html`
   - 使用 `{{placeholder}}` 标记动态内容

2. **注册到 Skill**
   - 在本文件添加模板说明
   - 更新触发词映射表

3. **测试验证**
   - 手动触发测试
   - 检查中文渲染
   - 验证输出尺寸

### 模板变量

```html
{{title}}        <!-- 标题 -->
{{subtitle}}     <!-- 副标题 -->
{{items}}        <!-- 列表项（自动展开） -->
{{highlight}}    <!-- 高亮数据 -->
{{date}}         <!-- 日期 -->
{{source}}       <!-- 来源标注 -->
```

---

## 对比传统方案

| 维度 | 生图 API | HTML 截图 |
|------|---------|----------|
| **成本** | 按次收费 | **零成本** |
| **版式控制** | 不可控 | **像素级可控** |
| **中文渲染** | 易出错 | **完美** |
| **风格统一** | 难 | **模板保证** |
| **生成速度** | 10-30秒 | **5秒** |

---

## 已知陷阱

### ⚠️ 浏览器工具不可用

**表现**：`browser_navigate` / `browser_vision` 命令不存在，或 Playwright 浏览器未安装

**原因**：浏览器工具不是命令行工具，Playwright 需要额外安装浏览器

**解决**：使用 **Pillow 直接绘制**（推荐）
```python
from PIL import Image, ImageDraw, ImageFont

# 创建画布
img = Image.new('RGB', (1080, 1920), '#f5f0e8')
draw = ImageDraw.Draw(img)

# 加载系统字体
font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 56)

# 绘制文字
draw.text((60, 60), "标题", fill='#2d2d2d', font=font)

# 保存
img.save('/tmp/output.png', quality=95)
```

**优势**：
- 无需浏览器，纯 Python 实现
- 速度快（1-2秒）
- 完全可控，无依赖问题

**示例脚本**：
- `scripts/example.py` - 交互式示例（HTML 模板）
- `scripts/direct_draw.py` - **Pillow 直接绘制米色暖系（推荐，无需浏览器）**
- `scripts/dark_card.py` - Pillow 直接绘制深色极简卡片

---

### ⚠️ 浏览器窗口大小

**表现**：截图被截断或留白

**原因**：浏览器窗口未适配内容尺寸

**解决**：
```python
# 在 HTML 中设置固定尺寸
<body style="width: 1080px; min-height: 1920px;">
```

### ⚠️ 字体加载

**表现**：截图显示默认字体

**原因**：自定义字体未加载完成

**解决**：
```html
<!-- 使用系统字体栈 -->
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", 
             "PingFang SC", "Microsoft YaHei", sans-serif;
```

### ⚠️ 中文乱码

**表现**：中文显示为方框

**原因**：HTML 未声明编码

**解决**：
```html
<head>
  <meta charset="UTF-8">
</head>
```

---

## 验证清单

- [ ] 模板风格已选择（米色暖系 / 深色极简）
- [ ] 内容已提取（标题、列表、数据）
- [ ] 生成方式已确定：
  - 浏览器可用 → HTML 模板 + 截图
  - 浏览器不可用 → Pillow 直接绘制（推荐）
- [ ] 图片已生成
- [ ] 输出路径已返回给用户

---

## 相关技能

- `kami-styles` - Kami 排版系统（文档模板）
- `design-image-studio` - 设计导向 AI 图像
- `claude-design` - HTML 原型设计

---

## 参考资料

- 原文：告别生图 API，我用 Hermes Skill 免费出图无限次
- 作者：娇姐
- 来源：娇姐话AI圈
- 日期：2026-04-30
