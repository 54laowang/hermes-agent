# PDF 生成故障排除与备用方案

## 常见错误

### WeasyPrint 依赖缺失（macOS）

**错误信息**：
```
OSError: cannot load library 'libgobject-2.0-0': 
dlopen(libgobject-2.0-0, 0x0002): tried: 'libgobject-2.0-0' (no such file), 
'/System/Volumes/Preboot/Cryptexes/OSlibgobject-2.0-0' (no such file), 
'/usr/lib/libgobject-2.0-0' (no such file, not in dyld cache)
```

**原因**：WeasyPrint 依赖 GObject/Pango/Cairo 系统库，这些不在 Python 包中。

**解决方案**：
```bash
# 安装系统依赖
brew install pango gobject-introspection

# 验证
python3 -c "from weasyprint import HTML; print('OK')"
```

---

## 零依赖备用方案：浏览器打印

当 PDF 工具链完全失败时，**浏览器打印-to-PDF** 是最可靠的 fallback。

### 操作流程

```bash
# 1. 生成 HTML
# (已完成，HTML 文件路径已知)

# 2. 在默认浏览器中打开
open /path/to/document.html

# 3. 用户手动操作
# - macOS: Cmd+P → 左下角"PDF"下拉 → "存储为PDF"
# - Windows: Ctrl+P → "另存为 PDF"
```

### 输出质量对比

| 方案 | CSS 支持 | 依赖 | 可靠性 | 质量 |
|------|---------|------|-------|------|
| WeasyPrint | 完整 | GObject/Pango | 需配置 | ★★★★★ |
| wkhtmltopdf | 大部分 | 单独安装 | 中等 | ★★★★☆ |
| 浏览器打印 | 完整 | 无（系统自带） | 极高 | ★★★★★ |

### 适用场景

**浏览器打印优先**：
- 用户说"马上要"、"急着用"
- 依赖安装失败或耗时过长
- 临时测试/预览

**WeasyPrint 优先**：
- 批量生成多份文档
- 自动化工作流
- 需要精确控制 PDF 元数据

---

## 实战案例

### 2026-05-02: DeepSeek V4 分析报告

**场景**：用户要求生成 PDF 报告，WeasyPrint 缺依赖

**错误**：
```
OSError: cannot load library 'libgobject-2.0-0'
```

**解决**：
1. 尝试安装 WeasyPrint → 依赖问题
2. 立即 fallback 到 `open /tmp/deepseek-v4-analysis.html`
3. 用户通过浏览器打印拿到 PDF

**耗时**：< 1 分钟（跳过依赖排查）

**教训**：优先提供可用方案，依赖问题可后续优化

---

## 其他 PDF 工具

### wkhtmltopdf

```bash
# 安装
brew install wkhtmltopdf

# 使用
wkhtmltopdf --encoding utf-8 input.html output.pdf
```

**限制**：
- 对 CSS Grid 支持有限
- 中文字体需额外配置
- 不支持某些 CSS3 特性

### Pandoc + wkhtmltopdf

```bash
pandoc input.md -o output.pdf --pdf-engine=wkhtmltopdf
```

**适用**：Markdown 直接转 PDF，跳过 HTML 中间态

---

## 推荐策略

```
PDF 生成决策树：
1. WeasyPrint 可用？ → 直接用
2. 不可用 + 可安装依赖？ → 安装后用
3. 不可用 + 急用？ → 浏览器打印
4. 批量/自动化场景？ → 必须修好 WeasyPrint
```
