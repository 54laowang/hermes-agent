---
name: desktop-pet
description: 桌面宠物系统 - 跨平台透明窗口宠物，支持多皮肤、动画、消息气泡、HTTP控制、Hermes Agent集成
version: 1.0.0
category: ui
keywords:
  - desktop-pet
  - transparent-window
  - animation
  - hermes-integration
---

# 桌面宠物系统 v1.0

跨平台桌面宠物，支持 Hermes Agent 任务提醒。

## 快速开始

```bash
python3 ~/.hermes/desktop-pet/pet_main.py
```

## 核心功能

1. **透明窗口宠物** - 真透明，无边框
2. **动画系统** - idle/walk/run/sprint 四种状态
3. **消息气泡** - 自动换行，3秒消失
4. **HTTP控制** - 端口 51983，远程推送消息
5. **Hermes集成** - 任务完成提醒、日程通知

## 文件结构

```
~/.hermes/desktop-pet/
├── pet_main.py          # 主程序
├── pet_window.py        # 窗口管理
├── pet_animation.py     # 动画系统
├── pet_bubble.py        # 消息气泡
├── pet_server.py        # HTTP服务器
├── pet_hermes.py        # Hermes集成
├── skins/               # 皮肤目录
│   └── default/
│       ├── skin.json
│       ├── idle.gif
│       └── walk.gif
└── assets/
    └── bubble.png       # 气泡素材
```

## 皮肤开发

### skin.json 格式

```json
{
  "name": "Default Pet",
  "version": "1.0.0",
  "format": "gif",
  "animations": {
    "idle": {"file": "idle.gif", "fps": 8},
    "walk": {"file": "walk.gif", "fps": 10}
  }
}
```

## HTTP API

```bash
# 显示消息
curl "http://127.0.0.1:51983/msg?text=任务完成"

# 切换动画
curl "http://127.0.0.1:51983/state?name=run"

# 健康检查
curl "http://127.0.0.1:51983/health"
```

## Hermes 集成

自动监听 Hermes Agent 事件：
- 任务完成 → 气泡提醒
- 日程提醒 → 语音播报
- 错误告警 → 闪烁动画

## 技术栈

- **PyQt6**: 跨平台GUI
- **PIL**: 图像处理
- **Flask**: HTTP服务器（轻量级）
- **Threading**: 多线程架构

## 依赖安装

```bash
pip3 install PyQt6 Pillow flask
```

## 开发计划

- [x] 基础窗口和动画
- [ ] 多皮肤系统
- [ ] HTTP控制接口
- [ ] Hermes Agent集成
- [ ] 语音播报
- [ ] 天气/日程提醒
