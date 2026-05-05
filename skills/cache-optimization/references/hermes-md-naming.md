# HERMES.md 命名规范

## 背景

### 问题

Claude Code（Anthropic 的 CLI Agent）会自动读取项目根目录的 `CLAUDE.md` 作为项目约束。

Hermes 原本也使用 `~/.hermes/CLAUDE.md` 作为全局配置，导致冲突：

```bash
cd ~/.hermes
claude  # Claude Code 启动
# Claude Code 会读取 Hermes 的配置！
```

---

## 解决方案

### 文件结构

```
~/.hermes/
├── HERMES.md          # 主配置文件（Hermes 专用）
└── CLAUDE.md -> HERMES.md  # 符号链接（向后兼容）
```

### 实现

```bash
# 重命名
mv ~/.hermes/CLAUDE.md ~/.hermes/HERMES.md

# 创建符号链接
ln -sf ~/.hermes/HERMES.md ~/.hermes/CLAUDE.md
```

---

## 向后兼容

### 符号链接确保

- ✅ 旧代码仍可读取 `CLAUDE.md`
- ✅ 新代码使用 `HERMES.md`
- ✅ 两边都能正常工作

### 代码示例

```python
# 读取 HERMES.md（推荐）
read_file("~/.hermes/HERMES.md")

# 读取 CLAUDE.md（兼容）
read_file("~/.hermes/CLAUDE.md")  # 通过符号链接
```

---

## 缓存优化集成

`cache_aware_prompt.py` 已更新，从 `HERMES.md` 读取固定前缀：

```python
def _build_fixed_prefix(self):
    """构建完全固定的前缀（最易缓存）
    
    注意：内容来源于 ~/.hermes/HERMES.md
    """
    hermes_md = os.path.expanduser("~/.hermes/HERMES.md")
    if os.path.exists(hermes_md):
        with open(hermes_md, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[:2000]  # 提取核心部分
    
    # 降级：硬编码的前缀
    return "你是 Hermes Agent..."
```

---

## 最佳实践

### 推荐

- 新代码统一使用 `HERMES.md`
- 更新文档时引用 `HERMES.md`
- 符号链接保持不变

### 避免

- 不要删除符号链接 `CLAUDE.md`
- 不要在 Hermes 目录下使用 Claude Code
- 不要混淆 Hermes 配置和 Claude Code 项目配置

---

## 相关文件

- 主配置：`~/.hermes/HERMES.md`
- 符号链接：`~/.hermes/CLAUDE.md`
- 说明文档：`~/.hermes/docs/HERMES_MD_NAMING.md`
- 缓存优化：`~/.hermes/core/cache_aware_prompt.py`

---

## 参考资料

- [Claude Code 文档](https://docs.anthropic.com/claude-code)
- [缓存优化 Skill](../cache-optimization/SKILL.md)
