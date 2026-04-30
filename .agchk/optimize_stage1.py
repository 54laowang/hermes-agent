#!/usr/bin/env python3
"""
🚀 Hermes Agent 性能优化执行脚本
基于 agchk 审计结果的第一阶段优化

使用方法:
    python3 .agchk/optimize_stage1.py --dry-run  # 预览优化
    python3 .agchk/optimize_stage1.py --apply    # 执行优化
"""

import argparse
import re
import os
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent

class Stage1Optimizer:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.findings = defaultdict(list)
        self.fixes_applied = 0
        
    def scan_print_statements(self):
        """ 查找生产代码中的 print 语句 (应该改用 logger) """
        print("\n🔍 扫描生产代码中的 print 语句...")
        
        exclude_dirs = {
            'tests', 'node_modules', '.venv', '__pycache__',
            'ui-tui', 'web', 'scripts', 'docker'
        }
        
        for py_file in PROJECT_ROOT.rglob('*.py'):
            # 跳过排除目录
            if any(d in py_file.parts for d in exclude_dirs):
                continue
                
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # 查找 print 语句，排除注释和字符串中的 print
                    stripped = line.strip()
                    if (stripped.startswith('print(') or 
                        re.search(r'\bprint\(', stripped)) and '#' not in stripped.split('print(')[0]:
                        # 排除调试模式和 CLI 输出的合法 print
                        if any(skip in stripped for skip in [
                            'CLI', 'banner', 'help', 'error', 'warning',
                            'print(', 'pprint', 'tqdm'
                        ]):
                            continue
                            
                        self.findings['print_statements'].append({
                            'file': str(py_file.relative_to(PROJECT_ROOT)),
                            'line': i,
                            'content': stripped
                        })
            except Exception as e:
                pass
                
        print(f"   发现 {len(self.findings['print_statements'])} 个需要检查的 print 语句")

    def scan_while_true_loops(self):
        """ 查找没有保护的 while True 循环 """
        print("\n🔍 扫描无限循环保护...")
        
        for py_file in PROJECT_ROOT.rglob('*.py'):
            if 'tests' in py_file.parts:
                continue
                
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if stripped == 'while True:':
                        # 检查后续几行是否有 break 保护或计数器
                        has_protection = False
                        for j in range(i, min(i+20, len(lines))):
                            next_line = lines[j]
                            if any(protect in next_line for protect in [
                                'break', 'return', 'raise', 'timeout',
                                'max_iter', 'MAX_ITER', 'max_retries'
                            ]):
                                has_protection = True
                                break
                        
                        if not has_protection:
                            self.findings['unprotected_loops'].append({
                                'file': str(py_file.relative_to(PROJECT_ROOT)),
                                'line': i,
                                'content': stripped
                            })
            except Exception as e:
                pass
                
        print(f"   发现 {len(self.findings['unprotected_loops'])} 个无保护的无限循环")

    def scan_redundant_copies(self):
        """ 查找可能冗余的 deepcopy """
        print("\n🔍 扫描潜在的冗余 deepcopy...")
        
        for py_file in PROJECT_ROOT.rglob('*.py'):
            if 'tests' in py_file.parts:
                continue
                
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    if 'deepcopy' in line and 'import' not in line:
                        # 检查是否在循环中
                        context = '\n'.join(lines[max(0, i-5):i])
                        if 'for ' in context or 'while' in context:
                            self.findings['loop_deepcopy'].append({
                                'file': str(py_file.relative_to(PROJECT_ROOT)),
                                'line': i,
                                'content': line.strip()
                            })
            except Exception as e:
                pass
                
        print(f"   发现 {len(self.findings['loop_deepcopy'])} 个循环中的 deepcopy")

    def generate_report(self):
        """ 生成优化报告 """
        print("\n" + "="*70)
        print("📊 第一阶段优化报告")
        print("="*70)
        
        print(f"\n🚪 发现的问题总数:")
        total = sum(len(v) for v in self.findings.values())
        print(f"   总计: {total} 个问题")
        
        for category, items in self.findings.items():
            if items:
                print(f"\n📌 {category.replace('_', ' ').title()} ({len(items)}):")
                for item in items[:10]:  # 每个分类显示前 10 个
                    print(f"   - {item['file']}:{item['line']}")
                    print(f"     {item['content']}")
                if len(items) > 10:
                    print(f"     ... 还有 {len(items) - 10} 个")

        print("\n" + "="*70)
        print("💡 优化建议:")
        print("="*70)
        
        print("""
1. 🖨️ print 语句 → 改用分级 logger
   print() → logger.debug() / logger.info()
   生产环境中 debug 日志默认关闭

2. 🔄 while True 循环 → 增加迭代保护
   while True:
   →
   iteration = 0
   while iteration < MAX_ITERATIONS:
       iteration += 1

3. 📋 deepcopy 优化:
   - 循环中避免重复 deepcopy
   - 考虑使用 copy-on-write 模式
   - 评估是否真的需要深拷贝
        """)

    def apply_fixes(self):
        """ 应用自动化修复 """
        if self.dry_run:
            print("\n⚠️  DRY RUN 模式 - 不实际应用修改")
            return
            
        print("\n🚀 应用自动化修复...")
        # TODO: 实现自动修复逻辑
        print("   自动化修复功能开发中...")

def main():
    parser = argparse.ArgumentParser(description='Hermes Stage 1 Optimizer')
    parser.add_argument('--dry-run', action='store_true', help='仅扫描不修改')
    parser.add_argument('--apply', action='store_true', help='应用自动化修复')
    args = parser.parse_args()
    
    print("🚀 Hermes Agent 第一阶段性能优化")
    print("   基于 agchk 审计报告发现的内耗点")
    
    optimizer = Stage1Optimizer(dry_run=not args.apply)
    
    optimizer.scan_print_statements()
    optimizer.scan_while_true_loops()
    optimizer.scan_redundant_copies()
    
    optimizer.generate_report()
    
    if args.apply:
        optimizer.apply_fixes()
    
    print("\n✅ 扫描完成！")
    print("   详细的自我审计机制请查看: .agchk/self_audit_mechanism.md")

if __name__ == '__main__':
    main()
