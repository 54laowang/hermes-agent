---
name: 编译安装 FinceptTerminal (macOS Qt 6.11 兼容补丁)
title: 编译安装 FinceptTerminal (macOS Qt 6.11 兼容补丁)
description: 在 macOS 上使用 Homebrew Qt 6.11 编译安装开源量化投研终端 FinceptTerminal，解决缺失源文件和符号冲突问题
author: Hermes
created: 2025-04-21
---

FinceptTerminal 是开源量化投研终端，支持 A 股数据（通过 AkShare）。本技能记录在 macOS 上使用 Homebrew Qt 6.11 编译安装的完整流程和兼容性补丁。

## 问题背景

- 原项目要求精确 Qt 6.8.3，但 Homebrew 默认安装 Qt 6.11
- 原 CMakeLists.txt 遗漏了多个核心源文件，导致链接失败
- Unity 构建默认开启导致匿名命名空间符号冲突
- macOS 打包需要修复资源路径才能通过 `macdeployqt` 和代码签名

## 前置要求

```bash
# 安装依赖
brew install qt cmake openssl
```

## 完整编译步骤

### 1. 克隆项目
```bash
git clone --depth 1 https://github.com/Fincept-Corporation/FinceptTerminal.git /tmp/FinceptTerminal
cd /tmp/FinceptTerminal/fincept-qt
```

### 2. 应用兼容性补丁

修改 `CMakeLists.txt`，以下是必需的修改：

```diff
# 1. 关闭 Unity 构建解决符号冲突
# Screens are excluded below via SKIP_UNITY_BUILD_INCLUSION (too many local statics/functions)
-set(CMAKE_UNITY_BUILD ON)
+set(CMAKE_UNITY_BUILD OFF)
set(CMAKE_UNITY_BUILD_BATCH_SIZE 14)

# 2. 添加 NetSpeedMeter 到 NETWORK_SOURCES
set(NETWORK_SOURCES
    src/network/http/HttpClient.cpp
+   src/core/net/NetSpeedMeter.cpp
)

# 3. 添加缺失的交易核心文件到 TRADING_SOURCES
set(TRADING_SOURCES
    src/trading/PaperTrading.cpp
    src/trading/OrderMatcher.cpp
    src/trading/BrokerRegistry.cpp
+   src/trading/ExchangeSession.cpp
+   src/trading/ExchangeSessionManager.cpp
+   src/trading/ExchangeDaemonPool.cpp
    src/trading/UnifiedTrading.cpp
)

# 4. 添加 VoiceConfigSection 到 SCREEN_SOURCES (settings)
    src/screens/settings/SettingsScreen.cpp
    src/screens/settings/LlmConfigSection.cpp
+   src/screens/settings/VoiceConfigSection.cpp
    src/screens/settings/McpServersSection.cpp
)

# 5. 添加 PolymarketOrderBlotter 到 SCREEN_SOURCES (polymarket)
    src/screens/polymarket/PolymarketPriceChart.cpp
    src/screens/polymarket/PolymarketLeaderboard.cpp
    src/screens/polymarket/PolymarketActivityFeed.cpp
+   src/screens/polymarket/PolymarketOrderBlotter.cpp
    src/screens/polymarket/PolymarketStatusBar.cpp
)

# 6. 添加 SpeedSparkline 到 UI_SOURCES (widgets)
    # In-app notification widgets
    src/ui/widgets/NotifToast.cpp
    src/ui/widgets/NotifBell.cpp
    src/ui/widgets/NotifPanel.cpp
+   src/ui/widgets/SpeedSparkline.cpp
)
```

**总结：需要添加 7 个缺失的源文件：**
- `ExchangeSession.cpp`
- `ExchangeSessionManager.cpp`
- `ExchangeDaemonPool.cpp`
- `NetSpeedMeter.cpp`
- `VoiceConfigSection.cpp`
- `PolymarketOrderBlotter.cpp`
- `SpeedSparkline.cpp`

### 3. 配置 CMake
```bash
mkdir -p build && cd build
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt \
  -DFINCEPT_ALLOW_QT_DRIFT=ON
```

### 4. 编译
```bash
make -j$(sysctl -n hw.ncpu)
```

### 5. 修复 macOS 打包和签名（解决闪退问题）

原 CMake 安装把所有资源脚本放在 `Contents/MacOS/` 目录下，导致 `macdeployqt` 签名失败：

```bash
# 移动资源到正确位置
mv FinceptTerminal.app/Contents/MacOS/resources FinceptTerminal.app/Contents/Resources
mv FinceptTerminal.app/Contents/MacOS/scripts FinceptTerminal.app/Contents/Resources
mv FinceptTerminal.app/Contents/MacOS/yt-dlp FinceptTerminal.app/Contents/Resources

# 重新运行 macdeployqt 拷贝 Qt 框架到应用包
/opt/homebrew/bin/macdeployqt FinceptTerminal.app -always-overwrite

# Ad-hoc 签名让 macOS 允许运行
codesign --force --deep --sign - FinceptTerminal.app
```

### 6. 运行

```bash
# Finder 打开
open FinceptTerminal.app

# 命令行运行
./FinceptTerminal.app/Contents/MacOS/FinceptTerminal

# 安装到系统
cp -r FinceptTerminal.app /Applications/
```

## ⚠️ 重要提示：SaaS 架构

**FinceptTerminal 不是纯本地软件，而是 SaaS + 客户端架构：**

- ✅ 客户端代码开源，但需要联网注册账号获取 API Key
- ✅ 首次启动必须在登录/注册页面创建账号（连接 fincept.io 服务器）
- ✅ 登录后支持离线使用（缓存会话数据）
- ❌ 没有 Guest/演示模式，必须注册才能使用

认证机制：
- 每个账号获得永久 API Key，存储在 macOS Keychain 中
- 后端验证订阅状态和功能权限
- 支持单会话限制（通过设备ID）

## 卸载与清理

如果需要彻底卸载 FinceptTerminal：

```bash
# 删除应用程序
rm -rf /Applications/FinceptTerminal.app
rm -rf ~/Applications/FinceptTerminal.app

# 删除数据和缓存
rm -rf ~/Library/Application\ Support/FinceptTerminal
rm -rf ~/Library/Application\ Support/com.fincept.terminal
rm -rf ~/Library/Caches/com.fincept.FinceptTerminal
rm -rf ~/Library/Preferences/com.fincept.FinceptTerminal.plist
rm -rf ~/Library/Saved\ Application\ State/com.fincept.FinceptTerminal.savedState

# 删除崩溃报告（可选）
rm -f ~/Library/Application\ Support/CrashReporter/FinceptTerminal_*.plist
rm -f ~/Library/Logs/DiagnosticReports/FinceptTerminal-*.ips

# 删除 Keychain 中的凭证
security delete-generic-password -s "fincept" -a "api_key" 2>/dev/null
```

## 已知问题

- Excel 导出需要 Qt6::GuiPrivate 头文件，Homebrew Qt 不包含，自动禁用，不影响核心功能
- 启动时有一些 `QString::arg: Argument missing` CSS 警告，不影响使用
- AkShare 需要 Python 环境，首次运行按提示配置即可

## 验证结果

- ✅ Apple Silicon (arm64) 编译成功
- ✅ 所有核心源文件链接成功
- ✅ macOS 打包和签名完成，不闪退
- ✅ 原生支持 A 股数据通过 AkShare

## 适用版本

- FinceptTerminal 4.0.2
- Qt 6.11 (Homebrew)
- macOS 14+ Apple Silicon
