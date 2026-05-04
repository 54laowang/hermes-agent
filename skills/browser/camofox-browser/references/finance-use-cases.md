# 财经数据获取示例

## 场景: 获取需要登录的财经网站数据

很多财经数据需要登录才能查看完整内容:
- 券商研报
- VIP 财经资讯
- 付费数据服务
- 个人持仓信息

## 解决方案

### 方案 1: Cookie 导入

```bash
# 1. 从浏览器导出 Cookie(Netscape 格式)
# Chrome 扩展: EditThisCookie -> Export -> Netscape format

# 2. 导入到 Camofox
POST http://localhost:9377/sessions/hermes-user/cookies
Content-Type: text/plain

# Netscape cookie file
.finance-site.com	TRUE	/	FALSE	0	session_id	abc123
.finance-site.com	TRUE	/	FALSE	0	user_token	xyz789
```

### 方案 2: VNC 可视化登录

```bash
# 1. 启动 VNC 会话
POST http://localhost:9377/vnc/sessions
{
  "userId": "hermes-user",
  "url": "https://finance-site.com/login"
}

# 返回: {"vncUrl": "http://localhost:9377/vnc?session=xxx"}

# 2. 用户在浏览器中完成登录
# 3. 导出 storage state
POST http://localhost:9377/vnc/sessions/:sessionId/export
{
  "userId": "hermes-user"
}
```

## 实际案例: 获取券商研报

```bash
# 1. 创建标签页
curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "hermes-finance",
    "sessionKey": "research-report",
    "url": "https://broker-site.com/research"
  }' | jq -r '.tabId' > /tmp/tab_id.txt

TAB_ID=$(cat /tmp/tab_id.txt)

# 2. 获取页面快照(已登录状态)
curl -s "http://localhost:9377/tabs/$TAB_ID/snapshot?userId=hermes-finance" | jq

# 3. 点击特定研报
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "hermes-finance",
    "ref": "e15"
  }'

# 4. 获取研报内容
sleep 2
curl -s "http://localhost:9377/tabs/$TAB_ID/snapshot?userId=hermes-finance" | jq -r '.snapshot'

# 5. 清理
curl -s -X DELETE "http://localhost:9377/tabs/$TAB_ID?userId=hermes-finance"
```

## 与现有工具集成

### 配合 Tushare

```python
# Tushare 获取基础数据
import tushare as ts

# Camofox 获取需要登录的补充数据
# 例如: 券商研报、VIP 资讯、个人持仓

# 整合到 Hermes 的分析流程
```

### 配合问财接口

```bash
# 问财: 获取公开的选股结果
# Camofox: 获取需要登录的详细数据
# 组合: 完整的分析报告
```

## 注意事项

1. **合规性**: 只访问你有权限的内容
2. **频率控制**: 避免过于频繁的请求
3. **数据安全**: 敏感数据不要泄露
4. **Session 管理**: 定期清理不需要的 Session

## 数据源建议

**公开数据**(不需要 Camofox):
- Tushare
- AkShare
- 问财接口
- 财联社

**需要登录**(适合 Camofox):
- 券商研报系统
- 付费财经资讯
- 个人账户数据
- VIP 数据服务

## 最佳实践

1. **混合使用**: 公开数据用 API,登录数据用 Camofox
2. **缓存策略**: 避免重复访问同一页面
3. **错误处理**: 登录态过期时通知用户
4. **日志记录**: 记录访问历史便于审计
