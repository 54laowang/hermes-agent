# 安全检查脚本参考

## 概述

**位置**: `scripts/security_check.py`

**用途**: Pre-commit 安全检查，防止新安全问题引入

## 检查项

### HIGH 级别

1. **subprocess(shell=True)** - 命令注入风险
   - 严重性: HIGH
   - 风险: 命令注入攻击
   - 修复: 使用 `shell=False` 和参数列表

2. **硬编码密钥** - 凭证泄露风险
   - 严重性: HIGH
   - 风险: API 密钥/密码泄露
   - 修复: 使用环境变量或密钥管理器

### MEDIUM 级别

3. **exec()/eval()/compile()** - 代码注入风险
   - 严重性: MEDIUM
   - 风险: 动态代码执行
   - 修复: 使用 `ast.literal_eval()` 或预定义函数

4. **危险导入** - pickle/marshal 等
   - 严重性: MEDIUM
   - 风险: 反序列化漏洞
   - 修复: 使用 JSON 或安全的序列化方式

## 使用方法

### 基础用法

```bash
# 检查当前目录
python scripts/security_check.py

# 检查特定文件
python scripts/security_check.py path/to/file.py

# 检查多个文件
python scripts/security_check.py file1.py file2.py file3.py

# 静默模式（只返回退出码）
python scripts/security_check.py --quiet
```

### 退出码

- `0` - 无问题
- `1` - 发现问题
- `2` - 检查失败

### 输出示例

```
🔒 安全检查启动

发现 25 个安全问题:

  HIGH: 3
  MEDIUM: 22

HIGH model_tools.py:678
  subprocess(shell=True) - 命令注入风险
  💡 使用 shell=False 和参数列表: subprocess.run(['cmd', 'arg1', 'arg2'])

HIGH config.py:42
  硬编码 API 密钥
  💡 使用环境变量或密钥管理器: os.environ.get('API_KEY')

... 还有 23 个问题

❌ 发现高风险问题，请修复后再提交
```

## 排除规则

### 自动排除

脚本自动排除以下情况：

1. **测试文件**
   - 文件名包含 `test`
   - 例如: `test_agent.py`, `tests/test_security.py`

2. **注释行**
   - 以 `#` 开头的行
   - 包含 `# TODO` 或 `# FIXME` 的行

3. **示例文件**
   - 文件名包含 `example`, `template`, `sample`
   - 例如: `config.yaml.example`

### 手动排除

在代码中添加注释：

```python
# 安全用法（排除检查）
subprocess.run(cmd, shell=True)  # noqa: security

# 测试数据（排除检查）
API_KEY = "test_key_12345"  # TEST DATA
```

## 修复建议

### subprocess(shell=True)

❌ **错误**:
```python
subprocess.run(f"ls {user_input}", shell=True)
```

✅ **正确**:
```python
subprocess.run(["ls", user_input], shell=False)
```

### exec()/eval()

❌ **错误**:
```python
result = eval(user_input)
```

✅ **正确**:
```python
import ast
result = ast.literal_eval(user_input)
```

### 硬编码密钥

❌ **错误**:
```python
API_KEY = "sk-1234567890abcdef"
```

✅ **正确**:
```python
import os
API_KEY = os.environ.get("API_KEY")
```

### 危险导入

❌ **错误**:
```python
import pickle
data = pickle.loads(user_data)
```

✅ **正确**:
```python
import json
data = json.loads(user_data)
```

## 集成点

### Pre-commit Hook

自动触发：每次 `git commit` 前

配置文件：`.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: security-check
        name: Security Check
        entry: python scripts/security_check.py
        language: system
        types: [python]
        pass_filenames: false
```

### CI/CD

自动触发：Push/PR/定时

配置文件：`.github/workflows/security-audit.yml`

```yaml
- name: Run security check
  run: python scripts/security_check.py
```

## 自定义配置

### 添加新的检查规则

编辑 `scripts/security_check.py`：

```python
def check_my_custom_issue(content: str, filepath: str) -> List[SecurityIssue]:
    """检查自定义问题"""
    issues = []
    pattern = r'my_dangerous_pattern'
    
    for i, line in enumerate(content.split('\n'), 1):
        if re.search(pattern, line):
            issues.append(SecurityIssue(
                file=filepath,
                line=i,
                severity="HIGH",
                issue="自定义安全问题",
                recommendation="修复建议"
            ))
    
    return issues
```

### 修改严重性阈值

调整退出逻辑：

```python
# 只在 HIGH 级问题时失败
if high_count > 0:
    return 1
else:
    return 0  # MEDIUM 问题不阻止提交
```

## 最佳实践

1. **提交前检查**: 每次提交前手动运行
2. **修复优先级**: 先修复 HIGH 级问题
3. **定期审计**: 每周运行全量检查
4. **团队培训**: 分享常见安全问题

## 参考资料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Pre-commit Documentation](https://pre-commit.com)
