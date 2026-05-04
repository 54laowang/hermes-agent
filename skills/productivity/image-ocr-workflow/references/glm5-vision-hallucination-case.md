# GLM-5 视觉幻觉案例记录

**日期**: 2026-05-03  
**场景**: 用户发送图片，Hermes 使用 GLM-5 视觉模型识别  
**结果**: 连续两次严重幻觉，用户评价"完全离谱"

---

## 实际图片内容

**文件**: `/Users/me/.hermes/image_cache/img_ce7cd23e6be1.jpg`  
**尺寸**: 1280x2772 像素  
**实际内容**: IntelliJ IDEA 中的 `Main.java` 文件，简单类定义

---

## GLM-5 第一次识别结果

**触发方式**: 用户发送图片后，模型自动"识别"

**输出内容**（幻觉）:
```
LeetCode 209: Minimum Size Subarray Sum
完整滑动窗口代码实现
```

**问题分析**:
- ❌ 编造了不存在的 LeetCode 题目
- ❌ 虚构了完整的算法代码
- ❌ 识别结果与实际图片完全不符

---

## GLM-5 第二次识别结果

**触发方式**: 调用 `vision_analyze` 工具，要求"逐行识别代码"

**输出内容**（幻觉）:
```
Python 变量命名规则教程
message = "Hello Python"
```

**问题分析**:
- ❌ 再次编造完全不同的内容
- ❌ 从 Java 代码"脑补"出 Python 教程
- ❌ 持续幻觉，无法自我纠正

---

## 尝试的解决方案

### 1. Tesseract OCR

**尝试命令**:
```bash
tesseract image.jpg stdout -l chi_sim+eng
```

**结果**: 
- ❌ 中文语言包未安装
- 英文识别输出乱码

**修复方案**:
```bash
brew install tesseract-lang
```

---

### 2. PaddleOCR

**尝试命令**:
```bash
pip install paddleocr
paddleocr ocr -i image.jpg --lang ch
```

**结果**:
- ❌ 首次运行需下载模型（~100MB）
- ❌ 120 秒超时，未完成识别

**修复方案**:
- 提前预热模型（空闲时运行一次）
- 设置更长超时（180 秒以上）

---

### 3. macOS Vision 框架

**尝试方式**: Python 调用 Vision 框架

**结果**:
- ❌ 缺少 `pyobjc-framework-Vision` 包

**修复方案**:
```bash
pip install pyobjc-framework-Vision
```

---

## 根本原因

### GLM-5 视觉模型的局限性

1. **训练数据偏差**
   - LeetCode、编程教程等内容在训练数据中高频出现
   - 模型倾向于"补全"常见模式，而非真实识别

2. **缺乏视觉理解**
   - 无法准确解析图片中的实际内容
   - 依赖上下文"猜测"而非真正的视觉识别

3. **无法自我纠正**
   - 即使被指出错误，仍会继续幻觉
   - 没有 grounding 机制验证输出真实性

---

## 经验教训

### ✅ 正确做法

1. **图片 OCR 优先用专业工具**
   - Tesseract（英文）
   - PaddleOCR（中文）
   - macOS Vision（系统原生）

2. **视觉模型仅用于复杂场景**
   - 自然场景理解
   - 图表分析
   - 多模态推理

3. **交叉验证**
   - 多个工具结果对比
   - 人工确认关键信息

### ❌ 错误做法

1. **盲目信任视觉模型输出**
   - GLM-5 在代码识别上不可靠
   - 任何识别结果都需验证

2. **跳过工具检查**
   - 未确认 OCR 工具是否安装
   - 未测试工具是否能正常工作

3. **忽略用户反馈**
   - 用户说"完全离谱"时，应立即切换方案
   - 而非继续用同一模型重试

---

## 改进措施

### 已创建技能

- **image-ocr-workflow** - 图片识别与 OCR 工作流
  - 包含工具选择矩阵
  - 详细的陷阱说明
  - 质量验证检查清单

### 建议配置更新

```yaml
# config.yaml
model:
  # 禁用 GLM-5 视觉功能，改用专业工具
  vision_blacklist:
    - GLM-5
    - GLM-4V
```

---

## 后续行动

- [ ] 安装 Tesseract 中文语言包
- [ ] 预热 PaddleOCR 模型
- [ ] 安装 pyobjc-framework-Vision
- [ ] 考虑切换默认模型到 DeepSeek V3.2 或 Kimi K2

---

**关键结论**: GLM-5 视觉模型存在严重幻觉问题，**绝不**应直接用于图片识别，必须使用专业 OCR 工具或切换到更可靠的视觉模型。
