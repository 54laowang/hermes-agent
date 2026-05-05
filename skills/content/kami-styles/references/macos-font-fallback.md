# macOS 字体回退方案

## 问题

Pillow 加载中文字体时，`/System/Library/Fonts/PingFang.ttc` 可能无法直接使用：
```
OSError: cannot open resource
```

## 可用字体

macOS 系统自带中文字体（已验证）：

| 字体名 | 路径 | 风格 | 适用场景 |
|-------|------|------|---------|
| STHeiti Medium | `/System/Library/Fonts/STHeiti Medium.ttc` | 黑体 | 标题、正文 |
| STHeiti Light | `/System/Library/Fonts/STHeiti Light.ttc` | 细黑体 | 副标题 |
| Songti | `/System/Library/Fonts/Supplemental/Songti.ttc` | 宋体 | 衬线正文 |

## 验证字体可用

```python
from PIL import ImageFont
import os

font_paths = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]

for path in font_paths:
    if os.path.exists(path):
        try:
            font = ImageFont.truetype(path, 20)
            print(f"✅ {path}")
        except Exception as e:
            print(f"❌ {path}: {e}")
```

## Kami 设计适配

Kami 设计规范使用衬线字体，macOS 回退方案：

```python
# Kami 风格字体加载
font_path = "/System/Library/Fonts/STHeiti Medium.ttc"

font_title = ImageFont.truetype(font_path, 48)    # 24pt 标题
font_body = ImageFont.truetype(font_path, 20)     # 10pt 正文
font_small = ImageFont.truetype(font_path, 18)    # 9pt 小字
```

## 配色方案

Kami 设计系统核心配色：

```python
PARCHMENT = "#f5f4ed"  # 暖色画布（米色纸张）
BRAND = "#1B365D"      # 墨蓝强调（唯一彩色）
NEAR_BLACK = "#141413" # 近黑正文
OLIVE = "#504e49"      # 橄榄灰副文
STONE = "#6b6a64"      # 石灰元信息
IVORY = "#faf9f5"      # 象牙卡片背景
TAG_BG = "#E4ECF5"     # 标签背景（实色，无 rgba）
```

## 注意事项

1. **标签背景用实色**：`#E4ECF5` 而非 `rgba()`，避免 WeasyPrint 双矩形 bug
2. **字体粗细**：标题 500，正文 400，避免合成粗体
3. **行高**：紧凑标题 1.1-1.3，密集正文 1.4-1.45

---

## Pillow 快速生图方案

当需要生成移动端信息图时，Pillow 直接绘制比 WeasyPrint → PDF → 图片更快：

**性能对比**：
- Pillow 直接绘制：**0.3秒**
- WeasyPrint → PDF → 图片：**5-10秒**

**移动端信息图实践**：见 `references/mobile-infographic-pillow.md`

**层次增强技巧**（用户反馈"缺乏层次感"后优化）：
- 顶部渐变背景
- 导语框高亮背景
- 两栏独立色块（不同颜色）
- 序号圆点标记（品牌色背景 + 白色文字）
- Callout 品牌色背景
- 卡片阴影效果

---

验证时间：2026-05-03
验证环境：macOS + Pillow
