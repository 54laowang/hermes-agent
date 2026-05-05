# HERMES.md 命名说明

## 为什么重命名

**原因**：避免与 Claude Code 的 `CLAUDE.md` 冲突

---

## 背景

### Claude Code 的约定

Anthropic 的 Claude Code CLI 会自动读取项目根目录的 `CLAUDE.md` 作为项目级约束。

### Hermes 的使用

Hermes 原本也使用 `~/.hermes/CLAUDE.md` 作为全局配置文件。

### 冲突场景

当在 Hermes 项目目录下使用 Claude Code 时，Claude Code 会读取 Hermes 的配置文件，导致混乱。

---

## 解决方案

### 主文件：HERMES.md

```bash
~/.hermes/HERMES.md  # Hermes 的主配置文件
```

### 符号链接：CLAUDE.md（向后兼容）

```bash
~/.hermes/CLAUDE.md -> HERMES.md  # 符号链接
```

**作用**：
- ✅ 新代码使用 `HERMES.md`
- ✅ 旧代码仍可读取 `CLAUDE.md`（通过符号链接）
- ✅ Claude Code 在其他项目不会误读

---

## 文件优先级

Hermes 读取顺序：
1. `HERMES.md`（优先）
2. `CLAUDE.md`（降级，符号链接）

---

## 已更新的文件

| 文件 | 更新内容 |
|------|---------|
| `~/.hermes/HERMES.md` | 主配置文件（重命名自 CLAUDE.md） |
| `~/.hermes/core/cache_aware_prompt.py` | 从 HERMES.md 读取固定前缀 |
| `~/.hermes/skills/cache-optimization/skill.md` | 更新说明 |

---

## 向后兼容

通过符号链接，以下场景仍然有效：

```python
# 旧代码
read_file("~/.hermes/CLAUDE.md")  # ✅ 仍然可以读取

# 新代码
read_file("~/.hermes/HERMES.md")  # ✅ 推荐方式
```

---

## 最佳实践

**推荐**：
- 新代码统一使用 `HERMES.md`
- 更新文档时引用 `HERMES.md`

**避免**：
- 不要删除符号链接 `CLAUDE.md`
- 不要在 Hermes 目录下使用 Claude Code

---

## 相关链接

- [Claude Code 文档](https://docs.anthropic.com/claude-code)
- [HERMES.md 主文件](../HERMES.md)
