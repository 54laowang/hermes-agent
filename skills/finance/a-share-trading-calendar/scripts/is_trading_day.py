#!/usr/bin/env python3
"""
A股交易日判断脚本
用于定时任务中判断是否需要执行数据收集

使用方法：
    python3 is_trading_day.py [--date YYYY-MM-DD] [--next]
    
返回：
    退出码 0 = 交易日
    退出码 1 = 休市
    
输出：
    日期、状态、原因、下一交易日（休市时或 --next 参数）
"""

import sys
import akshare as ak
from datetime import datetime
from typing import Optional, Tuple

# 2026年法定节假日（硬编码备份）
HOLIDAYS_2026 = {
    '元旦': ('2026-01-01', '2026-01-01'),
    '春节': ('2026-01-28', '2026-02-04'),
    '清明': ('2026-04-04', '2026-04-06'),
    '劳动节': ('2026-05-01', '2026-05-05'),
    '端午节': ('2026-05-31', '2026-06-02'),
    '中秋节': ('2026-10-03', '2026-10-05'),
    '国庆节': ('2026-10-01', '2026-10-07'),
}


def is_in_holiday(date_str: str) -> Tuple[bool, Optional[str]]:
    """
    判断是否在法定节假日中
    
    Args:
        date_str: 日期字符串 YYYY-MM-DD
    
    Returns:
        (is_holiday, holiday_name)
    """
    date = datetime.strptime(date_str, '%Y-%m-%d')
    
    for name, (start, end) in HOLIDAYS_2026.items():
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
        
        if start_date <= date <= end_date:
            return True, name
    
    return False, None


def get_next_trading_day(date_str: str) -> Optional[str]:
    """
    获取下一个交易日
    
    Args:
        date_str: 日期字符串 YYYY-MM-DD
    
    Returns:
        下一交易日字符串 YYYY-MM-DD，或 None
    """
    try:
        df = ak.tool_trade_date_hist_sina()
        dates = df['trade_date'].astype(str).tolist()
        
        # 找到当前日期之后的第一个交易日
        for d in dates:
            if d > date_str:
                return d
        
        return None
    except Exception as e:
        print(f"获取交易日历失败: {e}", file=sys.stderr)
        return None


def is_trading_day(date_str: Optional[str] = None) -> Tuple[bool, str]:
    """
    判断是否为交易日
    
    Args:
        date_str: 日期字符串，默认今天
    
    Returns:
        (is_trading, reason)
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 1. 检查是否为周末
    date = datetime.strptime(date_str, '%Y-%m-%d')
    weekday = date.weekday()
    
    if weekday >= 5:  # 周六=5, 周日=6
        return False, f"周末（星期{'六' if weekday == 5 else '日'}）"
    
    # 2. 检查是否为法定节假日
    is_holiday, holiday_name = is_in_holiday(date_str)
    if is_holiday:
        return False, f"{holiday_name}假期"
    
    # 3. 使用 AkShare 查询交易日历
    try:
        df = ak.tool_trade_date_hist_sina()
        dates = df['trade_date'].astype(str).tolist()
        
        if date_str not in dates:
            return False, "非交易日"
        
        return True, "交易日"
        
    except Exception as e:
        print(f"查询交易日历失败: {e}，使用硬编码节假日", file=sys.stderr)
        # 如果 API 失败，默认为交易日（保守策略）
        return True, "交易日（API 失败，保守判断）"


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='判断A股交易日')
    parser.add_argument('--date', help='日期 YYYY-MM-DD，默认今天')
    parser.add_argument('--next', action='store_true', help='显示下一交易日')
    args = parser.parse_args()
    
    date_str = args.date or datetime.now().strftime('%Y-%m-%d')
    
    # 判断交易日
    is_trading, reason = is_trading_day(date_str)
    
    print(f"日期: {date_str}")
    print(f"状态: {'✅ 交易日' if is_trading else '❌ 休市'}")
    print(f"原因: {reason}")
    
    # 如果是休市，显示下一交易日
    if not is_trading or args.next:
        next_trade = get_next_trading_day(date_str)
        if next_trade:
            print(f"下一交易日: {next_trade}")
    
    # 返回退出码
    sys.exit(0 if is_trading else 1)


if __name__ == '__main__':
    main()
