---
name: mitmproxy-credential-interception
description: mitmproxy HTTPS代理流量拦截与凭证提取配置流程 - 证书安装、代理配置、流量监控
author: Hermes
keywords: mitmproxy, proxy, traffic interception, credential extraction, HTTPS, 中间人代理
---

# mitmproxy HTTPS 流量拦截配置

## 适用场景

- 捕获 HTTPS 请求的登录凭证（Cookie、Token、Authorization）
- 分析网站的加密参数和签名算法
- 绕过需要登录的网站（配合 autocli 或浏览器自动化）
- 研究移动端 App 的 API 请求格式
- 反爬虫机制研究

## 核心原理

mitmproxy 是一个 HTTPS 中间人代理，通过安装 CA 证书，可以解密和查看所有 HTTPS 流量。

```
浏览器 → mitmproxy(解密) → 目标服务器
       ↓
   凭证提取脚本
```

## 完整配置流程

### 1. 安装 mitmproxy

```bash
# macOS
brew install mitmproxy

# 或 Python pip
pip install mitmproxy
```

### 2. 启动 mitmdump 加载插件

```bash
# 基础启动（默认监听 8080）
mitmdump -s credential.py -q

# 自定义端口
mitmdump -p 8888 -s credential.py -q

# 参数说明：
# -s: 加载 Python 插件脚本
# -q: 安静模式（减少日志）
# -p: 指定代理端口（默认 8080）
```

### 3. 安装 HTTPS 证书（关键！）

**方案 A：手动安装（推荐）**
```bash
# 打开证书文件
open ~/.mitmproxy/mitmproxy-ca-cert.pem

# 在"钥匙串访问"中：
# 1. 搜索 "mitmproxy"
# 2. 双击证书
# 3. 展开"信任"
# 4. 选择"始终信任"
# 5. 输入密码确认
```

**方案 B：命令行安装（需要 sudo）**
```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  ~/.mitmproxy/mitmproxy-ca-cert.pem
```

**证书文件说明**：
- `mitmproxy-ca-cert.pem`: PEM 格式（macOS/Linux）
- `mitmproxy-ca-cert.p12`: PKCS12 格式（Windows）
- `mitmproxy-ca-cert.cer`: CER 格式（Windows）

### 4. 配置代理

**方案 A：系统全局代理**
```bash
# 查看网络服务名称
networksetup -listallnetworkservices

# 设置代理（以 Wi-Fi 为例）
networksetup -setwebproxy Wi-Fi 127.0.0.1 8080
networksetup -setsecurewebproxy Wi-Fi 127.0.0.1 8080

# 开启代理
networksetup -setwebproxystate Wi-Fi on
networksetup -setsecurewebproxystate Wi-Fi on

# 验证配置
networksetup -getwebproxy Wi-Fi
networksetup -getsecurewebproxy Wi-Fi
```

**方案 B：Chrome 独立代理（推荐）**
```bash
# 启动带代理的 Chrome（不影响系统其他应用）
open -a "Google Chrome" --args --proxy-server="http://127.0.0.1:8080"
```

**方案 C：Firefox 手动配置**
1. 打开 Settings → General → Network Settings
2. Manual proxy configuration
3. HTTP Proxy: 127.0.0.1, Port: 8080
4. 勾选 "Use this proxy server for all protocols"

### 5. 验证流量拦截

```bash
# 测试 HTTP 请求（无需证书）
curl --proxy http://127.0.0.1:8080 http://example.com

# 测试 HTTPS 请求（需要证书信任）
curl --proxy http://127.0.0.1:8080 https://httpbin.org/ip

# 如果返回正常 IP 地址，说明配置成功
```

### 6. 查看捕获的凭证

**通过 HTTP API（如果插件提供）**：
```bash
# 假设插件在 8088 端口提供 API
curl -H "Authorization: YOUR_SESSION_KEY" \
  http://localhost:8088/credentials
```

**直接查看文件**：
```bash
# 查看插件保存的凭证文件
cat credentials.json

# 实时监控
tail -f credentials.json
```

### 7. 停止监控

```bash
# 关闭系统代理
networksetup -setwebproxystate Wi-Fi off
networksetup -setsecurewebproxystate Wi-Fi off

# 停止 mitmdump
pkill mitmdump
# 或找到进程 ID
ps aux | grep mitmdump
kill <PID>
```

## 凭证提取脚本示例

### 示例 1：捕获微信文章 Cookie

```python
import mitmproxy.http
import json
from urllib.parse import urlparse, parse_qs

class ExtractWeChatCookie:
    def __init__(self):
        self.cookies = {}
    
    def response(self, flow: mitmproxy.http.HTTPFlow):
        # 过滤微信公众号文章
        if flow.request.url.startswith("https://mp.weixin.qq.com/s?__biz="):
            parsed = urlparse(flow.request.url)
            query = parse_qs(parsed.query)
            biz = query.get('__biz', [None])[0]
            
            if biz:
                set_cookie = flow.response.headers.get("Set-Cookie")
                if set_cookie:
                    self.cookies[biz] = {
                        "url": flow.request.url,
                        "cookie": set_cookie,
                    }
                    # 保存到文件
                    with open("credentials.json", "w") as f:
                        json.dump(self.cookies, f, indent=2)

addons = [ExtractWeChatCookie()]
```

### 示例 2：捕获所有 Authorization Header

```python
import mitmproxy.http
import json

class ExtractAuthHeader:
    def __init__(self):
        self.tokens = []
    
    def request(self, flow: mitmproxy.http.HTTPFlow):
        auth = flow.request.headers.get("Authorization")
        if auth:
            self.tokens.append({
                "url": flow.request.url,
                "method": flow.request.method,
                "authorization": auth,
            })
            print(f"[Token] {flow.request.url}: {auth[:20]}...")

addons = [ExtractAuthHeader()]
```

### 示例 3：捕获特定域名 API

```python
import mitmproxy.http
import json

class CaptureAPI:
    def __init__(self):
        self.apis = []
    
    def response(self, flow: mitmproxy.http.HTTPFlow):
        # 只捕获特定域名
        if "api.example.com" in flow.request.host:
            self.apis.append({
                "url": flow.request.url,
                "method": flow.request.method,
                "request_body": flow.request.text[:500],
                "response_body": flow.response.text[:500],
                "cookies": dict(flow.request.cookies),
            })
            
            # 实时打印
            print(f"[API] {flow.request.method} {flow.request.path}")

addons = [CaptureAPI()]
```

## 与 autocli 的配合

### 场景 1：autocli 无法访问的登录墙页面

```
1. mitmproxy 捕获浏览器登录后的 Cookie/Token
2. 将凭证注入 autocli 配置
3. autocli 使用凭证访问需要登录的页面
```

### 场景 2：研究 API 签名算法

```
1. mitmproxy 捕获 App/工具的完整请求
2. 分析加密参数（sign、timestamp、token）
3. 在 autocli 或爬虫脚本中复现签名逻辑
```

## 常见问题排查

### 问题 1：证书不信任，HTTPS 请求失败

**症状**：
```
curl: (60) SSL certificate problem: unable to get local issuer certificate
```

**解决**：
```bash
# 确认证书已安装
security find-certificate -c "mitmproxy" -a | grep "mitmproxy"

# 重新设置信任
open ~/.mitmproxy/mitmproxy-ca-cert.pem
# 在钥匙串中设为"始终信任"
```

### 问题 2：代理不生效，流量没有被捕获

**排查步骤**：
```bash
# 1. 确认 mitmdump 正在运行
ps aux | grep mitmdump

# 2. 确认端口监听
lsof -i :8080

# 3. 确认代理配置
networksetup -getwebproxy Wi-Fi
networksetup -getsecurewebproxy Wi-Fi

# 4. 测试代理
curl --proxy http://127.0.0.1:8080 http://example.com
```

### 问题 3：Chrome 代理设置不生效

**原因**：Chrome 使用系统代理或命令行参数，不能混用

**解决**：
```bash
# 方案 A：使用系统代理（全局生效）
networksetup -setwebproxystate Wi-Fi on

# 方案 B：使用命令行参数（仅 Chrome 生效，推荐）
# ⚠️ 关键：必须完全关闭 Chrome 再重新打开
osascript -e 'quit app "Google Chrome"'
sleep 2
open -a "Google Chrome" --args --proxy-server="http://127.0.0.1:8080"

# 验证 Chrome 是否连接到代理
lsof -i :8080 | grep ESTABLISHED
# 应该看到 Google Chrome 进程的连接

# ⚠️ 重要：如果 Chrome 已经打开，代理参数不会生效
# 必须先完全关闭 Chrome（不是新标签页），然后用命令行参数重新打开
# 如果不确定，先检查是否有 ESTABLISHED 连接：
# lsof -i :8080 | grep ESTABLISHED
# 没有 Google Chrome 的连接 = 代理未生效
```

### 问题 4：脚本过滤条件不匹配

**症状**：mitmdump 运行正常，但 credentials.json 为空

**排查**：
```python
# 在脚本中添加调试输出
def response(self, flow):
    print(f"[DEBUG] {flow.request.url}")  # 查看所有 URL
    # 然后调整过滤条件
```

**微信公众号特殊注意事项**：
- **Set-Cookie 只在首次访问或登录后设置**
  - 如果浏览器已经登录微信，访问文章不会设置新的 Cookie
  - 解决方案：
    1. 使用 Chrome 无痕模式：`open -a "Google Chrome" --args --proxy-server="http://127.0.0.1:8080" --incognito`
    2. 清除微信 Cookie：开发者工具 → Application → Cookies → mp.weixin.qq.com → 删除所有
    3. 使用 autocli 替代（如果只需访问已登录页面）
- 测试 URL（如 `__biz=xxx&mid=test`）不会触发真实响应
- 必须访问真实的公众号文章链接
- 有些请求没有 Set-Cookie header（返回 200 但只有其他 header）
- **调试流程**：
  1. 先用测试脚本验证流量拦截是否正常
  2. 确认能看到请求被捕获
  3. 再切换到生产脚本提取凭证
  4. 如果生产脚本没有数据，检查过滤条件是否匹配实际 URL

```python
# test_credential.py - 用于验证监控是否工作
import mitmproxy.http
import json

class TestCapture:
    def __init__(self):
        self.captured = []

    def response(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request.scheme == "https":
            self.captured.append({
                "url": flow.request.url,
                "status": flow.response.status_code,
            })
            print(f"[捕获] {flow.request.url[:80]} -> {flow.response.status_code}")
            
            with open("test_capture.json", "w") as f:
                json.dump(self.captured, f, indent=2)

addons = [TestCapture()]
```

运行验证：
```bash
mitmdump -s test_credential.py -q
# 在另一个终端测试
curl --proxy http://127.0.0.1:8080 https://httpbin.org/ip
# 检查 test_capture.json 是否生成
```

### 示例 4：微信公众号凭证捕获（生产级）

```python
import mitmproxy.http
import json
import time
from urllib.parse import urlparse, parse_qs

class ExtractWeChatCookie:
    def __init__(self):
        self.cookies = {}
        self.all_requests = []
    
    def response(self, flow: mitmproxy.http.HTTPFlow):
        # 捕获所有微信相关请求
        if "weixin.qq.com" not in flow.request.url:
            return
        
        parsed_url = urlparse(flow.request.url)
        query_params = parse_qs(parsed_url.query)
        biz = query_params.get('__biz', [None])[0]
        
        # 记录请求信息
        request_info = {
            "url": flow.request.url,
            "path": parsed_url.path,
            "biz": biz,
            "status": flow.response.status_code,
            "has_cookie": bool(flow.response.headers.get("Set-Cookie"))
        }
        
        self.all_requests.append(request_info)
        
        # 检查 Set-Cookie
        set_cookie = flow.response.headers.get("Set-Cookie")
        if set_cookie:
            print(f"\n✅ [Set-Cookie] {parsed_url.path}")
            print(f"   URL: {flow.request.url[:100]}")
            
            # 如果有 __biz，保存到 cookies
            if biz:
                self.cookies[biz] = {
                    "url": flow.request.url,
                    "set_cookie": set_cookie,
                    "timestamp": int(time.time() * 1000),
                }
                print(f"   ✅ 已保存 __biz: {biz[:20]}...")
        
        # 记录文章页面请求
        if "/s?" in flow.request.url:
            print(f"\n📄 [文章页面] {flow.request.url[:120]}")
            print(f"   状态: {flow.response.status_code}")
            print(f"   有 __biz: {bool(biz)}")
            print(f"   有 Cookie: {bool(set_cookie)}")
        
        # 每 10 个请求保存一次
        if len(self.all_requests) % 10 == 0:
            output = {
                "cookies": self.cookies,
                "total_requests": len(self.all_requests),
                "requests_with_biz": sum(1 for r in self.all_requests if r.get("biz")),
                "requests_with_cookie": sum(1 for r in self.all_requests if r.get("has_cookie")),
                "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open("credentials.json", "w") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

addons = [ExtractWeChatCookie()]
print("微信凭证监控已启动 - 详细调试模式")
```

**使用此脚本**：
```bash
# 1. 启动 mitmdump
mitmdump -s credential.py -q

# 2. 验证代理连接
lsof -i :8080 | grep ESTABLISHED
# 应该看到 Chrome 的连接

# 3. 在 Chrome 中访问真实公众号文章

# 4. 检查输出
cat credentials.json
# 如果 total_requests > 0 但 cookies 为空，说明：
# - 流量拦截正常
# - 但浏览器已登录，没有新的 Set-Cookie
# 解决方案：使用无痕模式或清除 Cookie
```

## 注意事项

1. **法律合规**：仅用于自己的账号或授权测试，不得用于非法窃取他人凭证
2. **证书安全**：CA 证书私钥在 `~/.mitmproxy/mitmproxy-ca.p12`，注意保护
3. **性能影响**：开启代理后所有 HTTPS 流量都会解密，可能影响速度
4. **关闭清理**：使用完毕后关闭系统代理，避免影响正常上网
5. **浏览器差异**：
   - Chrome：支持命令行参数代理，但需要完全关闭后重启才能生效
   - Firefox：需要手动配置或使用扩展
   - Safari：使用系统代理设置
6. **微信公众号监控**：
   - 真实文章才有 Set-Cookie，测试 URL 无效
   - 建议先用测试脚本验证流量拦截
   - autocli 可能是更简单的替代方案（如果只需访问已登录页面）

## mitmproxy vs 其他工具

| 工具 | 定位 | 优势 | 适用场景 |
|------|------|------|----------|
| **mitmproxy** | 流量拦截代理 | 完整解密、Python 插件、实时分析 | API 研究、凭证提取、签名分析 |
| **autocli** | 浏览器自动化 | 使用现有登录会话、无需证书 | 已登录页面抓取、内容提取 |
| **CamouFox** | 隐身浏览器 | 反检测、指纹旋转、人类模拟 | 绕过 Bot 检测、复杂登录墙 |
| **Scrapling** | 反爬绕过 | Cloudflare 绕过、自适应解析 | 反爬严格网站、电商数据 |

**选择建议**：
- 需要分析 API 或签名 → **mitmproxy**
- 只需访问已登录页面 → **autocli**
- 需要 Bot 检测绕过 → **CamouFox**
- 遇到 Cloudflare 拦截 → **Scrapling**

## 进阶用法

### 1. 移动端流量捕获

```bash
# 1. 查看本机 IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# 2. mitmproxy 监听所有接口
mitmdump --listen-host 0.0.0.0 -p 8080

# 3. 手机配置代理
# 设置 → Wi-Fi → 代理 → 手动
# 服务器：电脑IP，端口：8080

# 4. 手机安装证书
# 访问 http://mitm.it 选择对应平台

# 5. 开始捕获 App 流量
```

### 2. 反向代理模式

```bash
# mitmproxy 作为反向代理，转发到目标服务器
mitmdump --mode reverse:https://target.example.com -p 8080

# 访问 http://localhost:8080 即可访问目标服务器
# 所有请求会被记录
```

### 3. 流量录制回放

```bash
# 录制流量到文件
mitmdump -w traffic.flow

# 回放流量
mitmdump -r traffic.flow

# 分析录制文件
mitmproxy -r traffic.flow
```
