# Chrome Cookie 导入 Camofox 操作指南

## 快速开始

### 一键导出 + 导入

```bash
# 1. 确保已关闭 Chrome
pkill -i "Google Chrome"

# 2. 导出 Cookie
hermes skill load camofox-browser
./scripts/export-cookies.sh
# 选择网站(如小红书)

# 3. 导入到 Camofox
./scripts/import-cookies.sh hermes cookies_xiaohongshu.com.txt

# 4. 测试访问
curl -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId": "hermes", "url": "https://www.xiaohongshu.com/explore"}'
```

---

## 支持的网站

脚本预置了常用网站:

| 网站名 | 域名 | 用途 |
|--------|------|------|
| 小红书 | xiaohongshu.com | 社交媒体/电商 |
| 淘宝 | taobao.com | 电商平台 |
| 京东 | jd.com | 电商平台 |
| 东方财富 | eastmoney.com | 财经数据 |
| 同花顺 | 10jqka.com.cn | 财经数据 |
| 财联社 | cls.cn | 财经资讯 |
| 雪球 | xueqiu.com | 投资社区 |

**自定义域名**: 脚本支持输入任意域名

---

## 前提条件

### 必须满足

1. **Chrome 已关闭**: 脚本需要独占访问 Cookie 数据库
   ```bash
   pkill -i "Google Chrome"
   ```

2. **已登录目标网站**: 在 Chrome 中至少登录过一次目标网站

3. **Camofox 服务运行**: 导入前需要启动服务
   ```bash
   cd ~/projects/camofox-browser && npm start
   ```

### 可选

- EditThisCookie 扩展(手动导出时需要)
- jq 工具(美化 JSON 输出)

---

## 详细步骤

### 步骤 1: 导出 Cookie

**自动导出(推荐)**:
```bash
./scripts/export-cookies.sh
```

**手动导出(EditThisCookie)**:
1. 安装扩展: https://chrome.google.com/webstore/detail/editthiscookie/
2. 打开目标网站
3. 点击扩展图标 -> Export -> Netscape format
4. 保存为 `cookies.txt`

### 步骤 2: 导入到 Camofox

```bash
./scripts/import-cookies.sh hermes cookies_xiaohongshu.com.txt
```

**参数说明**:
- `hermes`: 用户 ID(用于隔离不同用户的 Session)
- `cookies_xiaohongshu.com.txt`: Cookie 文件路径

### 步骤 3: 验证导入

```bash
# 创建标签页
TAB_ID=$(curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId": "hermes", "url": "https://www.xiaohongshu.com/explore"}' \
  | jq -r '.tabId')

# 获取快照(应显示登录后内容)
curl "http://localhost:9377/tabs/$TAB_ID/snapshot?userId=hermes" | jq

# 清理
curl -X DELETE "http://localhost:9377/tabs/$TAB_ID?userId=hermes"
```

---

## Cookie 文件格式

### Netscape 格式

```
# Netscape HTTP Cookie File
# 格式: domain	flag	path	secure	expiration	name	value

.xiaohongshu.com	TRUE	/	FALSE	0	session_id	abc123
.xiaohongshu.com	TRUE	/	FALSE	0	user_token	xyz789
```

**字段说明**:
- `domain`: Cookie 作用域(以 `.` 开头表示包含子域名)
- `flag`: 是否包含子域名(TRUE/FALSE)
- `path`: Cookie 路径(通常是 `/`)
- `secure`: 是否仅 HTTPS(TRUE/FALSE)
- `expiration`: 过期时间(Unix 时间戳,0=会话 Cookie)
- `name`: Cookie 名称
- `value`: Cookie 值

---

## 故障排查

### 问题 1: "Chrome 正在运行"

**原因**: Cookie 数据库被 Chrome 锁定

**解决**:
```bash
pkill -i "Google Chrome"
# 等待几秒后重试
```

### 问题 2: "未找到 Cookie"

**可能原因**:
- 未在 Chrome 中登录过该网站
- Cookie 已过期
- 域名输入错误

**解决**:
1. 打开 Chrome,访问目标网站并登录
2. 重新导出 Cookie

### 问题 3: "Cookie 导入后无效"

**可能原因**:
- Cookie 缺少关键字段
- 网站检测到异常(IP 变化等)
- Cookie 已过期

**解决方案 A: 重新导出**
```bash
# 在 Chrome 中重新登录网站
# 然后重新导出 Cookie
```

**解决方案 B: VNC 可视化登录**
```bash
# 启动 VNC 会话
curl -X POST http://localhost:9377/vnc/sessions \
  -H "Content-Type: application/json" \
  -d '{"userId": "hermes", "url": "https://target-site.com/login"}'

# 返回 VNC URL,在浏览器中完成登录
# 然后导出 storage state
curl -X POST http://localhost:9377/vnc/sessions/{sessionId}/export \
  -H "Content-Type: application/json" \
  -d '{"userId": "hermes"}'
```

---

## 安全最佳实践

### ✅ 推荐做法

1. **及时清理**: 使用后删除 Cookie 文件
   ```bash
   rm cookies_*.txt
   ```

2. **隔离存储**: 不同网站使用不同文件
   ```
   cookies_xiaohongshu.txt
   cookies_taobao.txt
   cookies_jd.txt
   ```

3. **定期更新**: Cookie 有有效期,过期后重新导出

4. **权限控制**: Cookie 文件权限设为 600
   ```bash
   chmod 600 cookies_*.txt
   ```

### ❌ 禁止事项

- 不要将 Cookie 文件提交到 Git
- 不要分享 Cookie 文件给他人
- 不要在不安全的网络环境中传输 Cookie

### Git 忽略

```bash
# 添加到 .gitignore
echo "cookies*.txt" >> .gitignore
```

---

## 工作流示例

### 场景: 获取需要登录的财经数据

```bash
# 1. 导出东方财富 Cookie
pkill -i "Google Chrome"
./scripts/export-cookies.sh
# 选择 "东方财富"

# 2. 启动 Camofox
cd ~/projects/camofox-browser && npm start &
sleep 5

# 3. 导入 Cookie
./scripts/import-cookies.sh hermes-finance cookies_eastmoney.com.txt

# 4. 访问需要登录的页面
TAB_ID=$(curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId": "hermes-finance", "url": "https://data.eastmoney.com/vip"}' \
  | jq -r '.tabId')

# 5. 获取数据
curl "http://localhost:9377/tabs/$TAB_ID/snapshot?userId=hermes-finance" | jq

# 6. 清理
curl -X DELETE "http://localhost:9377/tabs/$TAB_ID?userId=hermes-finance"
rm cookies_eastmoney.com.txt
```

---

## 与现有工具集成

### 配合 Tushare

```python
# Tushare: 公开数据
import tushare as ts
df = ts.get_k_data('000001')

# Camofox: 登录后的 VIP 数据
# 使用 Cookie 访问东方财富 VIP 数据
```

### 配合问财接口

```bash
# 问财: 公开选股结果
# Camofox: 登录后的详细数据
# 组合: 完整的分析报告
```

---

## 环境变量

脚本支持以下环境变量:

```bash
# Camofox 服务地址
export CAMOFOX_URL=http://localhost:9377

# Cookie 输出目录
export CAMOFOX_DIR=~/projects/camofox-browser
```

---

## 参考资源

- **详细文档**: ~/projects/camofox-browser/COOKIE_IMPORT_GUIDE.md
- **快速开始**: ~/projects/camofox-browser/QUICK_START.md
- **测试报告**: ~/projects/camofox-browser/TEST_REPORT.md

---

**更新时间**: 2026-05-03
**适用版本**: Camofox v1.8.15+, Chrome 90+
