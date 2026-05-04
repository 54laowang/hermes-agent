#!/usr/bin/env python3
"""
股价查询命令行工具
用法：
    python stock_query.py 300536          # 查询单只股票
    python stock_query.py 300536 002388   # 查询多只股票
    python stock_query.py --status        # 查看缓存状态
    python stock_query.py --clear         # 清除所有缓存
    python stock_query.py --force 300536  # 强制更新
"""

import sys
from stock_price_cache import (
    get_stock_price, 
    batch_get_stock_prices, 
    show_cache_status, 
    clear_cache
)

def main():
    args = sys.argv[1:]
    
    if not args:
        print(__doc__)
        return
    
    # 显示缓存状态
    if '--status' in args:
        show_cache_status()
        return
    
    # 清除缓存
    if '--clear' in args:
        clear_cache()
        return
    
    # 判断是否强制更新
    force_update = '--force' in args
    
    # 过滤掉选项参数
    stock_codes = [arg for arg in args if not arg.startswith('--')]
    
    if not stock_codes:
        print("❌ 请提供股票代码")
        return
    
    # 批量查询
    results = batch_get_stock_prices(stock_codes, force_update)
    
    # 格式化输出
    print("\n" + "="*60)
    print(f"{'代码':<10}{'名称':<12}{'最新价':<10}{'涨跌幅':<10}{'来源'}")
    print("="*60)
    
    for code, data in results.items():
        if 'error' not in data:
            price = data['price']
            last_close = data['last_close']
            change_pct = ((price - last_close) / last_close) * 100
            
            source = "缓存" if data.get('from_cache') else "实时"
            print(f"{code:<10}{data['name']:<12}{price:<10.2f}{change_pct:+.2f}%   {source}")
        else:
            print(f"{code:<10}{'错误':<12}{data['error']}")
    
    print("="*60)

if __name__ == "__main__":
    main()
