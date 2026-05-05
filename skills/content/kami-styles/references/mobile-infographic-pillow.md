# 移动端信息图生成实践（Pillow 方案）

> 本文档记录使用 Pillow 直接绘制 Kami 风格信息图的实践经验，适用于移动端分享场景。

---

## 背景

当需要快速生成移动端信息图（如微信/元宝分享）时，Pillow 直接绘制比 WeasyPrint → PDF → 图片转换更快（0.3秒 vs 数秒），无需安装额外依赖。

---

## 字体选择

### macOS 可用中文字体

| 字体 | 路径 | 状态 | 备注 |
|------|------|------|------|
| STHeiti Medium | `/System/Library/Fonts/STHeiti Medium.ttc` | ✅ 推荐 | 黑体风格，清晰锐利 |
| STHeiti Light | `/System/Library/Fonts/STHeiti Light.ttc` | ✅ 可用 | 细体 |
| Songti | `/System/Library/Fonts/Supplemental/Songti.ttc` | ✅ 可用 | 宋体衬线 |
| PingFang | `/System/Library/Fonts/PingFang.ttc` | ❌ 失败 | 沙盒环境无法加载 |

### 字体加载代码

```python
from PIL import ImageFont

font_path = "/System/Library/Fonts/STHeiti Medium.ttc"

# 不同尺寸用途
font_title = ImageFont.truetype(font_path, 52)      # 标题
font_body = ImageFont.truetype(font_path, 22)       # 正文
font_small = ImageFont.truetype(font_path, 19)      # 小字
```

---

## Kami 设计规范实现

### 核心配色

```python
# Kami 调色板
PARCHMENT = "#f5f4ed"  # 暖色画布
BRAND = "#1B365D"      # 墨蓝强调
NEAR_BLACK = "#141413" # 近黑色文字
OLIVE = "#504e49"      # 橄榄灰
STONE = "#6b6a64"      # 石灰色
IVORY = "#faf9f5"      # 象牙白
```

### 画布尺寸

```python
# 移动端友好尺寸（A4比例）
width, height = 1080, 1920  # 9:16 比例
```

---

## 层次增强方案

### 问题诊断
用户反馈"效果一般，缺乏层次感"，原因：
- 平面化布局，所有元素同一层级
- 缺少背景色块区分
- 缺少视觉引导元素

### 解决方案（v2版本）

#### 1. 顶部渐变背景
```python
header_height = 280
for y in range(header_height):
    alpha = y / header_height
    r = int(0xf5 - (0xf5 - 0xeb) * alpha * 0.3)
    g = int(0xf4 - (0xf4 - 0xe9) * alpha * 0.3)
    b = int(0xed - (0xed - 0xe0) * alpha * 0.3)
    draw.rectangle([0, y, width, y+1], fill=f"#{r:02x}{g:02x}{b:02x}")
```

#### 2. 导语框高亮背景
```python
draw.rectangle([50, lead_y, width-50, lead_y + lead_height], 
               fill=HIGHLIGHT_BG)  # #d4e0f0
```

#### 3. 两栏独立背景块
```python
# 左栏
draw.rectangle([col1_x, col1_y, col1_x + col1_width, col1_y + 400], 
               fill=IVORY)

# 右栏（不同颜色）
draw.rectangle([col2_x, col2_y, col2_x + col2_width, col2_y + 400], 
               fill=WARM_BG)  # #ebe9e0
```

#### 4. 序号圆点标记
```python
# 圆点背景
draw.ellipse([col1_x + 20, y_offset + 5, col1_x + 36, y_offset + 21], 
             fill=BRAND)

# 白色序号
draw.text((col1_x + 24, y_offset + 6), str(index), 
          font=font_small, fill="#ffffff")
```

#### 5. Callout 品牌色背景
```python
draw.rectangle([50, callout_y, width-50, callout_y + callout_height], 
               fill=BRAND)
# 白色文字
draw.text((70, callout_y + 20), "核心原则", 
          font=font_h2, fill="#ffffff")
```

#### 6. 卡片阴影效果
```python
# 先画阴影（偏移3px）
draw.rectangle([card_x + 3, card_y + 3, 
                card_x + card_width + 3, card_y + card_height + 3], 
               fill="#d0cdc4")

# 再画卡片主体
draw.rectangle([card_x, card_y, 
                card_x + card_width, card_y + card_height], 
               fill=IVORY)
```

---

## 完整代码模板

```python
from PIL import Image, ImageDraw, ImageFont
import os

# 配色方案
PARCHMENT = "#f5f4ed"
BRAND = "#1B365D"
NEAR_BLACK = "#141413"
OLIVE = "#504e49"
STONE = "#6b6a64"
IVORY = "#faf9f5"
WARM_BG = "#ebe9e0"
HIGHLIGHT_BG = "#d4e0f0"

# 创建画布
width, height = 1080, 1920
img = Image.new('RGB', (width, height), PARCHMENT)
draw = ImageDraw.Draw(img)

# 字体
font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
font_title = ImageFont.truetype(font_path, 52)
font_body = ImageFont.truetype(font_path, 22)
font_small = ImageFont.truetype(font_path, 19)

# ... 绘制逻辑 ...

# 保存
output_path = "/tmp/kami-output/infographic.png"
img.save(output_path, quality=95)
```

---

## 对比效果

| 版本 | 问题 | 改进 |
|------|------|------|
| v1 | 平面化、无层次 | - |
| v2 | - | 渐变背景 + 独立色块 + 序号 + Callout背景 + 卡片阴影 |

**文件大小**：
- v1: 168.7 KB
- v2: 196.1 KB（增加27KB，换来了层次感）

---

## 使用场景

- ✅ 移动端快速分享（微信/元宝/企业微信）
- ✅ 需要即时生成（< 1秒）
- ✅ 无需 PDF 输出
- ❌ 需要打印（建议用 WeasyPrint → PDF）
- ❌ 需要复杂排版（建议用 HTML 模板）

---

## 关键检查点

1. **字体加载前验证**：确保字体文件存在
2. **颜色格式**：使用十六进制 `#RRGGBB`，避免 rgba
3. **尺寸适配**：移动端推荐 1080 宽度
4. **层次分明**：至少 3 层视觉层级（背景 → 色块 → 内容）
5. **对比度检查**：确保文字与背景对比度足够

---

## 参考资料

- Kami 设计规范：`references/design.md`
- PDF 生成方案：`references/pdf-generation-fallbacks.md`
- 在线示例：`assets/demos/`
