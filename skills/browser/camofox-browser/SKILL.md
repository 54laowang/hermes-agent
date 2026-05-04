---
name: camofox-browser
description: Camofox 反检测浏览器 - 让 Hermes 稳定访问真实网页世界
version: 1.0.0
author: Hermes Agent
tags: [browser, anti-detection, automation, web-scraping]
min_hermes_version: 0.5.0
---

# Camofox Browser Skill

## 核心价值

让 Hermes 从"能搜索网页"升级为"能稳定使用网页"。

**关键能力**:
- ✅ 反检测(C++ 层指纹伪装)
- ✅ 登录态保持(userId 隔离)
- ✅ Token 节省(accessibility snapshot 比 HTML 小 90%)
- ✅ 稳定交互(stable element refs: e1, e2...)

## 快速工具

### Cookie 导入工具

```bash
# 导出 Chrome Cookie
./scripts/export-cookies.sh
# 选择网站或输入自定义域名

# 导入到 Camofox
./scripts/import-cookies.sh hermes cookies_xiaohongshu.com.txt
```

**详细指南**: `references/cookie-import-guide.md`

### 快速测试

```bash
# 验证 Camofox 功能
./scripts/quick-test.sh
```

---

## 安装启动

```bash
# 克隆项目
cd ~/projects
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser

# 安装依赖(首次运行会下载 ~300MB Camoufox 二进制)
npm install

# 启动服务(默认端口 9377)
npm start

# 验证服务
curl http://localhost:9377/health
```

### Hermes 配置

```yaml
# ~/.hermes/config.yaml
browser:
  default: camofox
  camofox:
    url: http://localhost:9377
    managed_persistence: true
```

## 核心功能

### 1. 创建标签页

```bash
POST /tabs
{
  "userId": "hermes-user",
  "sessionKey": "task-123",
  "url": "https://example.com"
}

# 或使用搜索宏
{
  "userId": "hermes-user",
  "macro": "@google_search",
  "query": "AI agent"
}
```

**搜索宏列表**:
- `@google_search` - Google 搜索
- `@youtube_search` - YouTube 搜索
- `@amazon_search` - Amazon 搜索
- `@reddit_search` - Reddit 搜索
- `@wikipedia_search` - Wikipedia 搜索
- `@twitter_search` - Twitter/X 搜索
- 更多见 AGENTS.md

### 2. 获取页面快照

```bash
GET /tabs/:tabId/snapshot?userId=hermes-user

# 返回格式
{
  "url": "https://example.com/",
  "snapshot": "- heading \"Example Domain\"\n- paragraph: This domain...\n- link \"Learn more\" [e1]",
  "refsCount": 1,
  "totalChars": 237
}
```

**关键特性**:
- 比 HTML 小 ~90%
- 结构化 accessibility tree
- 稳定元素引用 [e1], [e2]...

### 3. 交互操作

```bash
# 点击元素
POST /tabs/:tabId/click
{
  "userId": "hermes-user",
  "ref": "e1"  # 或 "selector": "button.submit"
}

# 输入文本
POST /tabs/:tabId/type
{
  "userId": "hermes-user",
  "ref": "e2",
  "text": "search query",
  "pressEnter": true
}

# 滚动页面
POST /tabs/:tabId/scroll
{
  "userId": "hermes-user",
  "direction": "down",
  "amount": 500
}
```

### 4. 登录态管理

**方案 A: Cookie 导入**

```bash
# 导出浏览器的 Cookie(Netscape 格式)
# 然后导入到 Camofox
POST /sessions/:userId/cookies
Content-Type: text/plain

# Netscape cookie file format
.example.com	TRUE	/	FALSE	0	cookie_name	cookie_value
```

**方案 B: VNC 可视化登录**

```bash
# 启动 VNC 会话
POST /vnc/sessions
{
  "userId": "hermes-user",
  "url": "https://accounts.google.com"
}

# 返回 noVNC URL,用户在浏览器中完成登录
# 登录后导出 storage state 给 Agent 使用
```

### 5. Session 管理

```bash
# 列出用户的所有标签页
GET /tabs?userId=hermes-user

# 删除用户所有 Session 数据
DELETE /sessions/:userId
```

## 典型应用场景

### 场景 1: 访问登录后的资料库

**问题**: 很多内容需要登录才能看(知识库、课程后台、内部文档)

**解决**:
1. 导入已登录的 Cookie
2. 或通过 VNC 完成一次登录
3. 后续访问自动保持登录态

```bash
# 导入 Cookie 后访问
POST /tabs
{
  "userId": "hermes-user",
  "url": "https://private-knowledge-base.com/dashboard"
}

# 获取内容
GET /tabs/:tabId/snapshot?userId=hermes-user
```

### 场景 2: 操作复杂后台

**问题**: 广告后台、电商后台、CRM 只有网页界面

**解决**: 稳定的浏览器身份 + 任务理解

```bash
# 1. 登录广告后台
# 2. 点击筛选
# 3. 下载数据
# 4. 整理报告
```

### 场景 3: 高风控网站

**问题**: 频繁访问触发验证码/风控

**解决**: 
- Camofox 的 C++ 层指纹伪装
- 稳定的浏览器身份
- 本地部署(敏感数据不离开本地)

### 场景 4: 小红书评论抓取(案例)

**流程**:
1. Agent 访问帖子页面
2. 发现需要登录才能看完整评论
3. 告知用户:"需要登录才能查看第 200 条评论"
4. 提供 VNC 登录链接
5. 用户扫码授权
6. Agent 继续操作已授权的浏览器

**关键**: 遵循"用户授权"原则,而不是硬绕过

## API 端点速查

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/tabs` | POST | 创建标签页 |
| `/tabs/:tabId/snapshot` | GET | 获取页面快照 |
| `/tabs/:tabId/click` | POST | 点击元素 |
| `/tabs/:tabId/type` | POST | 输入文本 |
| `/tabs/:tabId/scroll` | POST | 滚动页面 |
| `/tabs/:tabId/navigate` | POST | 导航到新 URL |
| `/tabs/:tabId/links` | GET | 获取页面链接 |
| `/tabs/:tabId` | DELETE | 关闭标签页 |
| `/sessions/:userId/cookies` | POST | 导入 Cookie |
| `/sessions/:userId` | DELETE | 清除用户数据 |

完整文档: http://localhost:9377/docs

## 与现有工具对比

| 特性 | Playwright | Camofox | 优势 |
|------|-----------|---------|------|
| 反检测 | ❌ 需要插件 | ✅ C++ 层伪装 | 更难被识别 |
| 登录态 | ⚠️ 临时 | ✅ 持久化 | 长期可用 |
| Token 消耗 | ❌ 完整 HTML | ✅ Accessibility | 节省 90% |
| 元素定位 | ⚠️ Selector 易变 | ✅ Stable refs | 更稳定 |
| 部署 | ✅ 简单 | ✅ 简单 | 相同 |

## 注意事项

### 安全性

- ✅ 本地优先(敏感数据在自己机器)
- ✅ 用户授权(不是绕过权限)
- ✅ 状态隔离(不同用户不同 profile)
- ✅ 可观测可关闭

### 适用边界

**推荐使用**:
- 访问你自己的账号/后台
- 已授权的订阅服务
- 合法的自动化任务

**禁止使用**:
- 绕过付费墙
- 非法采集数据
- 攻击网站

### 性能优化

```yaml
# 空闲时内存占用 ~40MB
# 懒加载浏览器
# 30 分钟无活动自动关闭

# 生产环境建议
browser:
  camofox:
    url: http://localhost:9377
    timeout: 30000
    retry:
      max_attempts: 3
      delay: 1000
```

## 故障排查

### 服务启动失败

```bash
# 检查端口占用
lsof -i :9377

# 检查 Camoufox 二进制
ls -la ~/projects/camofox-browser/node_modules/camoufox-js/

# 查看日志
npm start 2>&1 | tee camofox.log
```

### 访问被拦截

1. 检查是否需要登录(Cookie 导入)
2. 尝试 VNC 可视化登录
3. 查看是否触发验证码(等待后重试)

### Token 消耗高

确保使用 `/snapshot` 而不是原始 HTML:
```bash
# ✅ 正确
GET /tabs/:tabId/snapshot

# ❌ 避免
# 不要手动获取 HTML 再处理
```

## 参考资料

- 项目地址: https://github.com/jo-inc/camofox-browser
- Camoufox 文档: https://camoufox.com
- 原文: https://mp.weixin.qq.com/s/wW_PuopLy0e9RKxqrdPsAQ

## 支持文件

### 脚本工具
- `scripts/export-cookies.sh` - Chrome Cookie 一键导出
- `scripts/import-cookies.sh` - Cookie 导入到 Camofox
- `scripts/quick-test.sh` - 快速功能验证

### 参考文档
- `references/cookie-import-guide.md` - Cookie 导入完整指南
- `references/finance-use-cases.md` - 财经数据获取案例

## 测试验证

```bash
# 运行完整测试
cd ~/projects/camofox-browser
./test_camofox.sh

# 测试小红书登录态
./test_xiaohongshu.sh
```

---

## 版本历史

- v1.0.0 (2026-05-03): 初始版本,核心功能验证通过
