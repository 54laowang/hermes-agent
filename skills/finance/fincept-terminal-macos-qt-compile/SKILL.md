---
name: 编译安装 FinceptTerminal (macOS Qt 6.11 兼容补丁)
description: 在 macOS 上编译安装开源量化投研终端 FinceptTerminal，解决 Qt 版本兼容性和源文件缺失问题
tags: [finance, quant, macos, qt, compilation, fincept-terminal]
author: Hermes Agent
---

# 编译安装 FinceptTerminal (macOS Qt 6.11 兼容补丁)

在 macOS 上编译安装开源量化投研终端 FinceptTerminal，解决 Qt 版本兼容性问题和源文件缺失问题。

## 问题背景

FinceptTerminal 官方要求 **Qt 6.8.3 精确版本**，但 Homebrew 安装的是 Qt 6.11，且原项目 CMakeLists.txt 存在源文件缺失问题导致链接失败。本技能提供完整的修复方案。

## 前提条件

- macOS (Apple Silicon/Intel 都支持)
- Homebrew 已安装 Qt 6：
```bash
brew install qt cmake
```

## 完整编译步骤

### 1. 克隆项目
```bash
git clone --depth 1 https://github.com/Fincept-Corporation/FinceptTerminal.git /tmp/FinceptTerminal
cd /tmp/FinceptTerminal/fincept-qt
```

### 2. 应用兼容性补丁

需要修改 `CMakeLists.txt`，添加以下 7 处修改：

1. **关闭 Unity 构建**（解决未定义符号链接错误）：
   ```diff
   @@ -56,7 +56,7 @@ project(FinceptTerminal VERSION 4.0.2 LANGUAGES CXX)
    # Unity build for infrastructure layers (safe — no local symbol conflicts)
    # Screens are excluded below via SKIP_UNITY_BUILD_INCLUSION (too many local statics/functions)
   -set(CMAKE_UNITY_BUILD ON)
   +set(CMAKE_UNITY_BUILD OFF)
    set(CMAKE_UNITY_BUILD_BATCH_SIZE 14)
   ```

2. **添加 NetSpeedMeter 到 NETWORK_SOURCES**：
   ```diff
   @@ -436,6 +436,7 @@ set(CORE_SOURCES)
    # Network
    set(NETWORK_SOURCES
        src/network/http/HttpClient.cpp
   +    src/core/net/NetSpeedMeter.cpp
    )
   ```

3. **添加三个缺失的交易核心文件到 TRADING_SOURCES**：
   ```diff
    set(TRADING_SOURCES
        src/trading/PaperTrading.cpp
        src/trading/OrderMatcher.cpp
        src/trading/BrokerRegistry.cpp
   +    src/trading/ExchangeSession.cpp
   +    src/trading/ExchangeSessionManager.cpp
   +    src/trading/ExchangeDaemonPool.cpp
        src/trading/UnifiedTrading.cpp
   ```

4. **添加 VoiceConfigSection 到 SCREEN_SOURCES**：
   ```diff
        src/screens/settings/SettingsScreen.cpp
        src/screens/settings/LlmConfigSection.cpp
   +    src/screens/settings/VoiceConfigSection.cpp
        src/screens/settings/McpServersSection.cpp
   ```

5. **添加 PolymarketOrderBlotter 到 SCREEN_SOURCES**：
   ```diff
        src/screens/polymarket/PolymarketPriceChart.cpp
        src/screens/polymarket/PolymarketLeaderboard.cpp
        src/screens/polymarket/PolymarketActivityFeed.cpp
   +    src/screens/polymarket/PolymarketOrderBlotter.cpp
        src/screens/polymarket/PolymarketStatusBar.cpp
   ```

6. **添加 SpeedSparkline 到 UI_SOURCES**：
   ```diff
        # In-app notification widgets
        src/ui/widgets/NotifToast.cpp
        src/ui/widgets/NotifBell.cpp
        src/ui/widgets/NotifPanel.cpp
   +    src/ui/widgets/SpeedSparkline.cpp
    )
   ```

### 3. 配置和编译

```bash
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt -DFINCEPT_ALLOW_QT_DRIFT=ON
make -j$(sysctl -n hw.ncpu)
```

### 4. 部署（成功编译后）

编译成功后会生成 `FinceptTerminal.app`，可以复制到 Applications：
```bash
open .  # 在 Finder 中打开，拖动 FinceptTerminal.app 到 Applications
```

## 修复的问题清单

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 大量 undefined symbol 链接错误 | Unity 构建缓存导致符号冲突 | 关闭 CMAKE_UNITY_BUILD |
| `ExchangeSession`/`ExchangeSessionManager`/`ExchangeDaemonPool` 符号缺失 | 源文件存在但未添加到 CMakeLists.txt | 添加到 TRADING_SOURCES |
| `NetSpeedMeter` 符号缺失 | 同上 | 添加到 NETWORK_SOURCES |
| `VoiceConfigSection` 符号缺失 | 同上 | 添加到 SCREEN_SOURCES |
| `PolymarketOrderBlotter` 符号缺失 | 同上 | 添加到 SCREEN_SOURCES |
| `SpeedSparkline` 符号缺失 | 同上 | 添加到 UI_SOURCES |
| Qt 版本不匹配 (要求 6.8.3，实际 6.11) | Fincept 官方严格锁定版本 | 开启 `FINCEPT_ALLOW_QT_DRIFT=ON` 绕过检查 |
| macOS 14+ AGL framework 缺失 | Qt 6.8 FindWrapOpenGL 硬编码 fallback 到已删除的 AGL | 原项目已内置补丁，无需额外操作 |

## 功能说明

- ✅ A 股数据支持：原生集成 **AkShare** 连接器，可获取国内市场数据
- ✅ 支持多市场：A股、港股、美股、Polymarket 预测市场
- ✅ 内置 AI 分析、技术图表、投资组合管理
- ℹ️ Excel 导出：因缺少 Qt6::GuiPrivate 头文件在 Homebrew 版本中默认禁用，不影响核心功能

## 验证

编译成功后检查：
```bash
file FinceptTerminal.app/Contents/MacOS/FinceptTerminal
# 应该输出：Mach-O 64-bit executable arm64 (or x86_64)
```

## 常见问题

**Q: 链接阶段超时怎么办？**
A: 在 Apple Silicon 上链接大型可执行文件需要 2-5 分钟，请耐心等待。如果工具调用超时，手动执行 `make` 即可完成。

**Q: 找不到 Qt 怎么办？**
A: 确保 CMake 参数中 `-DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt` 正确，Homebrew Qt 安装在此路径。

**适用版本**：FinceptTerminal 4.0.2，macOS + Qt 6.11
