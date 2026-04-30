#!/usr/bin/env python3
"""
Pre-commit 安全检查脚本
自动检测常见安全问题，防止新问题引入

检查项：
1. subprocess(shell=True) - 命令注入风险
2. exec()/eval()/compile() - 代码注入风险
3. 硬编码密钥 - 凭证泄露风险
4. 危险导入 - 不安全的模块使用

使用方法：
    python scripts/security_check.py [--fix] [files...]

退出码：
    0 - 无问题
    1 - 发现问题
    2 - 检查失败
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

# ANSI 颜色
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class SecurityIssue:
    """安全问题"""

    def __init__(
        self, file: str, line: int, severity: str, issue: str, recommendation: str
    ):
        self.file = file
        self.line = line
        self.severity = severity
        self.issue = issue
        self.recommendation = recommendation

    def __str__(self):
        color = RED if self.severity == "HIGH" else YELLOW
        return f"{color}{self.severity}{RESET} {self.file}:{self.line}\n  {self.issue}\n  💡 {self.recommendation}"


def check_subprocess_shell_true(content: str, filepath: str) -> List[SecurityIssue]:
    """检查 subprocess(shell=True)"""
    issues = []
    pattern = r"subprocess\.\w+\([^)]*shell\s*=\s*True"

    for i, line in enumerate(content.split("\n"), 1):
        if re.search(pattern, line):
            # 排除测试文件和注释
            if "test" in filepath.lower() or line.strip().startswith("#"):
                continue

            issues.append(
                SecurityIssue(
                    file=filepath,
                    line=i,
                    severity="HIGH",
                    issue="subprocess(shell=True) - 命令注入风险",
                    recommendation="使用 shell=False 和参数列表: subprocess.run(['cmd', 'arg1', 'arg2'])",
                )
            )

    return issues


def check_exec_eval_compile(content: str, filepath: str) -> List[SecurityIssue]:
    """检查 exec()/eval()/compile()"""
    issues = []
    patterns = [
        (r"\beval\s*\(", "eval() - 代码注入风险"),
        (r"\bexec\s*\(", "exec() - 代码注入风险"),
        (r"\bcompile\s*\(", "compile() - 代码编译风险"),
    ]

    for i, line in enumerate(content.split("\n"), 1):
        # 排除测试文件、注释和字符串
        if "test" in filepath.lower() or line.strip().startswith("#"):
            continue

        for pattern, issue in patterns:
            if re.search(pattern, line):
                # 排除安全的用法（如 exec(open().read())）
                if "exec(open(" in line or "exec(compile(" in line:
                    continue

                issues.append(
                    SecurityIssue(
                        file=filepath,
                        line=i,
                        severity="MEDIUM",
                        issue=issue,
                        recommendation="避免动态代码执行，使用 ast.literal_eval() 或预定义函数映射",
                    )
                )

    return issues


def check_hardcoded_secrets(content: str, filepath: str) -> List[SecurityIssue]:
    """检查硬编码密钥"""
    issues = []
    patterns = [
        (
            r'(?i)(?:api[_-]?key|apikey|secret[_-]?key|token)\s*[=:]\s*["\']([a-zA-Z0-9+/]{20,}={0,2})["\']',
            "硬编码 API 密钥",
        ),
        (r'(?i)(?:password|passwd|pwd)\s*[=:]\s*["\']([^"\']{8,})["\']', "硬编码密码"),
    ]

    for i, line in enumerate(content.split("\n"), 1):
        # 排除测试文件、注释、示例和配置模板
        if any(
            x in filepath.lower() for x in ["test", "example", "template", "sample"]
        ):
            continue
        if line.strip().startswith("#") or "TODO" in line or "FIXME" in line:
            continue

        for pattern, issue in patterns:
            if re.search(pattern, line):
                issues.append(
                    SecurityIssue(
                        file=filepath,
                        line=i,
                        severity="HIGH",
                        issue=issue,
                        recommendation="使用环境变量或密钥管理器: os.environ.get('API_KEY')",
                    )
                )

    return issues


def check_dangerous_imports(content: str, filepath: str) -> List[SecurityIssue]:
    """检查危险导入"""
    issues = []
    dangerous_modules = ["pickle", "marshal", "shelve"]

    for i, line in enumerate(content.split("\n"), 1):
        for module in dangerous_modules:
            if re.search(rf"\bimport\s+{module}\b|\bfrom\s+{module}\b", line):
                issues.append(
                    SecurityIssue(
                        file=filepath,
                        line=i,
                        severity="MEDIUM",
                        issue=f"危险模块导入: {module}",
                        recommendation=f"{module} 可能导致反序列化漏洞，使用 json 或安全的序列化方式",
                    )
                )

    return issues


def scan_file(filepath: str) -> List[SecurityIssue]:
    """扫描单个文件"""
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 运行所有检查
        issues.extend(check_subprocess_shell_true(content, filepath))
        issues.extend(check_exec_eval_compile(content, filepath))
        issues.extend(check_hardcoded_secrets(content, filepath))
        issues.extend(check_dangerous_imports(content, filepath))

    except Exception as e:
        print(f"{YELLOW}警告{RESET}: 无法扫描 {filepath}: {e}")

    return issues


def scan_directory(
    directory: str, exclude_dirs: List[str] = None
) -> List[SecurityIssue]:
    """扫描目录"""
    if exclude_dirs is None:
        exclude_dirs = [
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "build",
            "dist",
        ]

    issues = []
    path = Path(directory)

    # 扫描 Python 文件
    for py_file in path.rglob("*.py"):
        # 排除目录
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue

        issues.extend(scan_file(str(py_file)))

    return issues


def main():
    parser = argparse.ArgumentParser(description="安全检查脚本")
    parser.add_argument("files", nargs="*", help="要检查的文件或目录")
    parser.add_argument("--fix", action="store_true", help="自动修复（暂未实现）")
    parser.add_argument("--quiet", action="store_true", help="静默模式")

    args = parser.parse_args()

    # 确定扫描目标
    if args.files:
        targets = args.files
    else:
        targets = ["."]  # 默认当前目录

    print(f"{BLUE}🔒 安全检查启动{RESET}\n")

    # 扫描所有目标
    all_issues = []
    for target in targets:
        if Path(target).is_file():
            all_issues.extend(scan_file(target))
        else:
            all_issues.extend(scan_directory(target))

    # 统计
    high_count = sum(1 for i in all_issues if i.severity == "HIGH")
    medium_count = sum(1 for i in all_issues if i.severity == "MEDIUM")

    # 输出结果
    if all_issues:
        if not args.quiet:
            print(f"\n{YELLOW}发现 {len(all_issues)} 个安全问题:{RESET}\n")
            print(f"  {RED}HIGH: {high_count}{RESET}")
            print(f"  {YELLOW}MEDIUM: {medium_count}{RESET}\n")

            for issue in all_issues[:20]:  # 只显示前20个
                print(f"{issue}\n")

            if len(all_issues) > 20:
                print(f"... 还有 {len(all_issues) - 20} 个问题\n")

        # 返回码
        if high_count > 0:
            print(f"{RED}❌ 发现高风险问题，请修复后再提交{RESET}\n")
            return 1
        else:
            print(f"{YELLOW}⚠️  发现中等风险问题，建议修复{RESET}\n")
            return 1
    else:
        print(f"{GREEN}✅ 未发现安全问题{RESET}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
