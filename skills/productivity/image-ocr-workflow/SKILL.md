---
name: image-ocr-workflow
description: 图片识别与 OCR 工作流 - 根据图片类型智能选择识别方案（视觉模型/专业OCR），避免幻觉陷阱。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [OCR, Image, Vision, Tesseract, PaddleOCR, GLM]
    related_skills: [ocr-and-documents]
    triggers: ["图片识别", "OCR", "识别图片", "提取文字", "vision_analyze"]
---

# 图片识别与 OCR 工作流

## 核心原则

**⚠️ 重要警告：GLM-5 视觉模型存在严重幻觉问题**
- 会编造不存在的代码、文本、场景
- **绝不**直接信任 GLM-5 的视觉识别结果
- 必须用专业 OCR 工具交叉验证

## 决策流程

```
用户发送图片
    ↓
1. 图片类型判断
    ├─ 代码截图 → 专业 OCR (Tesseract/PaddleOCR)
    ├─ 文档扫描 → marker-pdf (见 ocr-and-documents skill)
    ├─ 自然场景 → 视觉模型 (GPT-4o/Claude)
    └─ 表格/图表 → PaddleOCR + 结构化解析
    ↓
2. 执行识别
    ↓
3. 质量验证
    ├─ 检查输出是否合理
    ├─ 对比多个工具结果
    └─ 标注置信度
```

---

## 工具选择矩阵

| 工具 | 适用场景 | 准确度 | 速度 | 依赖 |
|------|---------|--------|------|------|
| **Tesseract** | 英文代码、纯文本 | ⭐⭐⭐ | ⚡⚡⚡ | brew install tesseract tesseract-lang |
| **PaddleOCR** | 中英文混合、表格 | ⭐⭐⭐⭐⭐ | ⚡⚡ | pip install paddleocr (~100MB 首次下载) |
| **macOS Vision** | macOS 系统原生 | ⭐⭐⭐⭐ | ⚡⚡⚡ | pip install pyobjc-framework-Vision |
| **GLM-4V/5** | ❌ **不推荐** - 幻觉严重 | ⭐ | ⚡⚡ | 已集成但不可靠 |
| **GPT-4o** | 复杂场景、图表 | ⭐⭐⭐⭐⭐ | ⚡ | 需切换模型 |
| **Claude 3.5** | 代码、文档 | ⭐⭐⭐⭐⭐ | ⚡ | 需切换模型 |

---

## 快速使用指南

### 方案 1: Tesseract（英文优先）

```bash
# 安装
brew install tesseract tesseract-lang

# 基础识别
tesseract image.jpg stdout

# 中英文混合
tesseract image.jpg stdout -l chi_sim+eng

# 指定 PSM 模式（单行文本、代码等）
tesseract image.jpg stdout -l eng --psm 6
```

**PSM 模式说明**：
- `--psm 3` 自动分页（默认）
- `--psm 6` 单块文本
- `--psm 7` 单行文本
- `--psm 11` 稀疏文本

---

### 方案 2: PaddleOCR（中文首选）

```bash
# 安装（首次需下载 ~100MB 模型）
pip install paddleocr

# 命令行识别
paddleocr ocr -i image.jpg --lang ch

# Python 脚本
python3 -c "
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch')
result = ocr.ocr('image.jpg')
for line in result:
    if line:
        for word_info in line:
            print(word_info[1][0])
"
```

**⚠️ 首次运行注意**：
- 首次调用会下载模型文件（~100MB）
- 超时时间设置至少 180 秒
- 模型缓存位置：`~/.paddleocr/`

---

### 方案 3: macOS Vision 框架

```bash
# 安装依赖
pip install pyobjc-framework-Vision

# Python 脚本
python3 << 'EOF'
import Vision
from Foundation import NSURL

url = NSURL.fileURLWithPath('image.jpg')
request = Vision.VNRecognizeTextRequest.alloc().init()
request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)

handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(url, None)
handler.performRequests_error_([request], None)

for observation in request.results():
    print(observation.topCandidates_(1)[0].string())
EOF
```

**优势**：系统原生、无额外下载、中英文支持良好

---

### 方案 4: 切换视觉模型

如果用户允许，切换到视觉能力更强的模型：

```bash
# 查看可用模型
hermes config show | grep -A5 "models:"

# 临时切换（在 config.yaml 中修改）
model:
  default: deepseek-v3-2-251201  # 或 kimi-k2-250905
```

**推荐模型**：
- **DeepSeek V3.2** - 视觉能力强，中文友好
- **Kimi K2** - 月之暗面，视觉理解优秀
- **GPT-4o** - OpenAI 最强视觉模型（需配置 API）

---

## 参考资料

- `references/glm5-vision-hallucination-case.md` - GLM-5 视觉幻觉完整案例
- `references/tesseract-chinese-setup.md` - Tesseract 中文 OCR 实战指南（安装、使用、最佳实践）

---

## 已知陷阱

### 1. GLM-5 视觉幻觉 ⚠️

**表现**：
- 编造不存在的代码内容
- 虚构文档标题和段落
- 将简单图片"脑补"成复杂场景

**案例**（2026-05-03）：
```
实际图片：Main.java 的简单类定义
GLM-5 输出：LeetCode 209 滑动窗口完整代码（完全编造）
第二次输出：Python 变量命名教程（再次编造）
```

**解决方案**：
- ❌ **禁止**直接使用 GLM-5 视觉识别
- ✅ 用专业 OCR 工具交叉验证
- ✅ 或切换到更可靠的视觉模型

---

### 2. Tesseract 中文支持

**问题**：默认只支持英文

**解决**：
```bash
# 安装中文语言包
brew install tesseract-lang

# 或手动下载
curl -L -o /opt/homebrew/share/tessdata/chi_sim.traineddata \
  https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
```

---

### 3. PaddleOCR 首次超时

**问题**：首次运行下载模型耗时 2-5 分钟

**解决方案**：
```python
# 提前预热模型
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch')  # 在空闲时运行一次
```

或在命令中设置足够超时：
```bash
# 至少 180 秒
timeout 180 paddleocr ocr -i image.jpg --lang ch
```

---

### 4. PaddleOCR v5 API 变更 ⚠️

**问题**（2026-05-03 实测）：
- `PaddleOCR()` 构造函数参数已变更：`use_gpu`、`use_angle_cls`、`show_log` 均已废弃，传入会抛 `ValueError: Unknown argument`
- CLI 用法变更：需指定子命令 `paddleocr ocr -i <path>`，不再支持 `--image_path` 参数

**正确用法**：
```bash
# CLI（v5+）
paddleocr ocr -i /path/to/image.jpg --lang ch

# Python（v5+）— 不传废弃参数
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='ch')
result = ocr.ocr('image.jpg')
```

**首次运行**：下载模型 ~100MB，需 ≥ 180 秒超时，首次后缓存到 `~/.paddleocr/`

---

### 5. Tesseract 中文实际准确度

**2026-05-03 实测结果**：
- 安装 `brew install tesseract-lang` 后中文识别可用
- 整体准确度约 **95%**
- 已知混淆字符：
  - "函数" → 误识别为 "困数"
  - "loop" → 误识别为 "1oop"（数字1 vs 小写L）
  - 顶部时间戳等小字识别差
- **适用场景**：快速预览、结构识别，**不适合精确代码/文字提取**

---

### 6. 图片质量影响

**最佳实践**：
- 分辨率 ≥ 300 DPI
- 避免倾斜、模糊、反光
- 代码截图用等宽字体
- 表格保持网格线清晰

---

## 工作流示例

### 场景：识别代码截图

```bash
# 1. 判断图片类型（代码截图）
file image.jpg  # 确认是 JPEG

# 2. 优先用 Tesseract（英文代码识别快）
tesseract image.jpg stdout -l eng --psm 6

# 3. 如果识别效果差，尝试 PaddleOCR
timeout 180 paddleocr ocr -i image.jpg --lang ch

# 4. 验证输出是否合理
# 检查关键字、语法结构、括号匹配
```

### 场景：识别中文文档

```bash
# 1. PaddleOCR 首选
timeout 180 paddleocr ocr -i doc.jpg --lang ch

# 2. 或用 macOS Vision
python3 vision_ocr.py doc.jpg

# 3. 如果文档是 PDF，使用 marker-pdf
# （见 ocr-and-documents skill）
```

---

## 质量验证检查清单

识别完成后，执行以下验证：

- [ ] 输出长度是否合理？（不应远超图片文字量）
- [ ] 关键信息是否匹配？（文件名、日期、专有名词）
- [ ] 格式是否正确？（代码缩进、表格对齐）
- [ ] 是否有明显的"脑补"内容？（图片中不存在的文字）
- [ ] 多个工具结果是否一致？

**如果验证失败**：
1. 尝试其他 OCR 工具
2. 切换视觉模型
3. 标注置信度并告知用户

---

## 相关技能

- **ocr-and-documents** - PDF 和文档 OCR
- **hermes-agent** - 模型切换配置

---

## 参考资料

- **[GLM-5 视觉幻觉案例](references/glm5-vision-hallucination-case.md)** - 详细记录 GLM-5 在图片识别中的严重幻觉问题
- **[OCR 工具实测对比 2026-05-03](references/session-2026-05-03-ocr-comparison.md)** - Tesseract/PaddleOCR/GLM-5 实测结果与 API 变更记录
- Tesseract 文档：https://tesseract-ocr.github.io/
- PaddleOCR GitHub：https://github.com/PaddlePaddle/PaddleOCR
- macOS Vision 框架：https://developer.apple.com/documentation/vision

---

## 更新日志

- **2026-05-03** - v1.0.0 - 创建技能，记录 GLM-5 视觉幻觉问题
