---
name: hermes-dashboard-i18n
description: 自定义 Hermes Dashboard Web UI 的字体和本地化设置
version: 1.0
---

# Hermes Dashboard 本地化指南

自定义 Hermes Dashboard Web UI 的字体和语言设置。

## 项目结构

```
~/.hermes/hermes-agent/
├── web/                        # 前端代码
│   ├── src/
│   │   ├── index.css           # 全局样式和字体定义
│   │   ├── App.tsx             # 主应用和导航栏
│   │   └── pages/              # 各页面组件
│   │       ├── StatusPage.tsx
│   │       ├── SessionsPage.tsx
│   │       ├── ConfigPage.tsx
│   │       ├── SkillsPage.tsx
│   │       ├── CronPage.tsx
│   │       ├── LogsPage.tsx
│   │       └── EnvPage.tsx
│   └── package.json
└── hermes_cli/web_dist/       # 构建输出目录
```

## 字体更改

修改 `web/src/index.css`，替换 `@font-face` 和字体栈：

```css
/* 系统字体栈（中英文支持） */
--font-sans: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;
--font-mono: "SF Mono", "Cascadia Code", "Fira Code", Menlo, Consolas, monospace;

body {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;
}
```

## 本地化方法

使用 `patch` 工具修改 TSX 文件中的用户可见文本：

```bash
patch --mode replace --path "web/src/App.tsx" \
  --old-string 'label: "Status"' \
  --new-string 'label: "状态"'
```

## 并行处理多个文件

使用 `delegate_task` 同时处理多个文件，提高效率：

```
delegate_task(
  goal="汉化 SessionsPage.tsx",
  context="文件路径: ~/.hermes/hermes-agent/web/src/pages/SessionsPage.tsx",
  toolsets=["file"]
)
```

## 批量处理多个字符串 (execute_code)

使用 `execute_code` 撰写 Python 脚本循环处理多个替换，比逐个调 patch 更高效：

```python
from hermes_tools import patch

patches = [
    ('old_string_1', 'new_string_1'),
    ('old_string_2', 'new_string_2'),
    # ...更多替换对
]

for old, new in patches:
    result = patch(mode="replace", path="目标文件.tsx", old_string=old, new_string=new)
    if result.get("success"):
        print(f"OK: {old[:30]}...")
    else:
        print(f"FAIL: {old[:30]}...")
```

## 处理非唯一字符串

当 `old_string` 匹配多处时：
1. **增加上下文** - 包含更多行/代码使其唯一
2. **使用 `replace_all=true`** - 当所有出现都需要替换时：
   ```python
   patch(mode="replace", path="...", old_string="...", new_string="...", replace_all=True)
   ```

## 启动 Dashboard

Dashboard 需要同时运行前端和后端服务：

### 方式一：一体化启动（推荐）

```bash
hermes dashboard --port 9119
```

访问 http://127.0.0.1:9119

### 方式二：开发模式（前后端分离）

便于前端热更新调试：

```bash
# 终端 1：启动后端 API
cd ~/.hermes/hermes-agent && source venv/bin/activate
hermes dashboard --port 9119

# 终端 2：启动前端开发服务器
cd ~/.hermes/hermes-agent/web && npm run dev
```

前端访问 http://localhost:5173 或 5174，API 自动代理到 9119。

## 常见问题排查

### 前端编译错误

如果 Vite 报 JSX 语法错误，检查以下常见问题：

1. **JSX 标签未闭合**
   ```tsx
   // 错误：自闭合标签漏了 /
   <div className="h-2 w-2" />
   
   // 错误：标签未闭合
   <div>内容</div>  // 正确
   <div>内容        // 错误
   ```

2. **模板字符串末尾多余的 `}`**
   ```tsx
   // 错误
   sub={`${value} 文本`}`
   
   // 正确
   sub={`${value} 文本`}
   ```

3. **缩进混乱导致标签嵌套错误**
   - 检查 `patch` 后的文件，确保 JSX 结构正确

### API 500 错误

前端响应 500 表示后端未运行：

```bash
# 检查后端状态
curl http://127.0.0.1:9119/api/status

# 启动后端
hermes dashboard --port 9119
```

### 命令不存在

注意：CLI 命令是 `hermes dashboard`，不是 `hermes web`：

```bash
# 正确
hermes dashboard

# 错误（会报 invalid choice）
hermes web
```

## 构建和验证

修改完成后重新构建前端：

```bash
cd ~/.hermes/hermes-agent/web
npm run build
```

重启 Dashboard：

```bash
hermes dashboard
```

访问 http://127.0.0.1:9119 验证更改。

## 注意事项

1. 只修改用户可见的文本，保持变量名/函数名不变
2. 专业术语可保留英文（API, YAML, JSON, Telegram 等）
3. 使用 patch 的 replace 模式，确保 old_string 有足够的上下文保证唯一性
4. 构建前检查 TypeScript 错误：`cd web && npm run build`
