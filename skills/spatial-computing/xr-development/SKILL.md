---
name: xr-development
description: |
  XR/空间计算开发技能集 - 覆盖 VisionOS、WebXR、沉浸式界面、座舱交互等空间计算场景。
  包含 Apple Vision Pro 原生开发、WebXR 浏览器端开发、XR 界面设计等。
version: 1.0.0
category: spatial-computing
keywords:
  - xr
  - visionos
  - webxr
  - spatial-computing
  - ar
  - vr
  - immersive
---

# XR/空间计算开发

## 开发平台

### Apple VisionOS（原生开发）

使用 Swift + SwiftUI + ARKit + RealityKit 构建：

- **SwiftUI 体积式界面** - 3D 空间中的原生 UI
- **RealityKit 场景构建** - 3D 内容渲染
- **ARKit 空间追踪** - 世界追踪、手部追踪
- **Metal 渲染优化** - 高性能 3D 图形

### WebXR（浏览器端开发）

跨平台沉浸式体验：

- **WebXR Device API** - VR/AR 设备访问
- **Three.js / A-Frame** - 3D 场景构建
- **WebXR AR Module** - 增强现实功能
- **WebXR VR Module** - 虚拟现实功能

---

## 核心技能

### 空间界面设计（xr-interface-architect）

- 空间交互模式
- 沉浸式 UX 设计
- 多模态输入（手势、眼动、语音）
- 空间音频集成

### 沉浸式开发（xr-immersive-developer）

- 3D 场景构建
- 物理引擎集成
- 性能优化
- 跨平台适配

### 座舱交互（xr-cockpit-interaction-specialist）

- 车载 XR 场景
- HUD 设计
- 手势交互
- 安全约束

---

## 开发流程

```
需求分析 → 平台选择 → 空间设计 → 交互实现 → 性能优化 → 测试发布
```

### 平台选择指南

| 场景 | 推荐平台 | 原因 |
|------|----------|------|
| Apple 生态专属 | VisionOS | 原生性能、深度集成 |
| 跨平台 Web | WebXR | 无需安装、广泛兼容 |
| 企业级 AR | ARCore/ARKit | 成熟稳定、生态完善 |
| 车载场景 | 定制方案 | 安全合规要求 |

---

## 技术栈

### VisionOS

```
SwiftUI + RealityKit + ARKit + Metal
```

### WebXR

```
JavaScript + Three.js/A-Frame + WebXR API
```

### 通用工具

- Blender - 3D 建模
- Unity/Unreal - 复杂场景
- Reality Composer - AR 快速原型

---

## 最佳实践

1. **性能优先** - 维持 90fps 避免晕动症
2. **交互自然** - 符合现实世界直觉
3. **空间舒适** - 避免过度仰视/俯视
4. **渐进引导** - 用户自主控制体验深度

---

## 相关技能

- `visionos-spatial-engineer` - VisionOS 原生开发
- `xr-immersive-developer` - WebXR 开发
- `xr-interface-architect` - 空间界面设计
- `xr-cockpit-interaction-specialist` - 座舱交互
