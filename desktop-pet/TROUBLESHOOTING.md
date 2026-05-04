# 桌面宠物置顶问题排查与解决方案

## 问题描述
macOS 上 Qt 窗口置顶可能不生效，原因：
1. macOS 窗口管理机制限制
2. Qt 的 `WindowStaysOnTopHint` 在某些 macOS 版本上不可靠
3. 全屏应用会覆盖普通窗口

## 解决方案

### 方案1：使用增强启动器（推荐）
```bash
cd ~/.hermes/desktop-pet
python3 launcher.py
```
- 自动启动桌面宠物
- 后台持续保持置顶（每10秒检查一次）
- 按 Ctrl+C 停止

### 方案2：使用启动脚本
```bash
cd ~/.hermes/desktop-pet
./start_with_top.sh
```
- 启动宠物并调用 AppleScript 置顶
- 提供手动操作提示

### 方案3：手动切换（最简单）
1. **右键点击宠物** → 选择 "📌 取消置顶" 或 "📌 始终置顶"
2. **双击宠物** → 快速切换置顶状态

## 当前状态
- ✅ 进程运行正常（PID: 85062, 97003）
- ✅ HTTP API 正常响应
- ⚠️ 窗口置顶需要手动确认或使用增强启动器

## macOS 特殊说明

### 窗口层级（从低到高）
1. Normal - 普通窗口
2. Floating - 浮动窗口（推荐）
3. MainMenu - 菜单栏
4. Status - 状态栏
5. Dock - Dock 栏
6. ScreenSaver - 屏保

### 建议
- 使用 **Floating** 层级即可满足大部分需求
- 避免与全屏应用冲突（这是系统行为）
- 如果需要更强置顶，考虑使用 yabai 等窗口管理工具

## 测试置顶是否生效
```bash
# 发送测试消息
python3 pet_control.py msg "测试置顶"

# 切换到其他窗口，观察宠物是否仍然可见
# 如果不可见，使用方案1或方案3
```

## 已安装的工具
- `keep_on_top.py` - 持续置顶守护
- `macos_stay_on_top.py` - macOS 专用置顶
- `launcher.py` - 增强启动器（推荐）
- `start_with_top.sh` - 启动脚本
