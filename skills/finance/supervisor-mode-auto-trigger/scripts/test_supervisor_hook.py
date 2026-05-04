#!/usr/bin/env python3
"""
监察者模式自动触发测试脚本
测试Hook的关键词匹配、时区换算、市场状态判断等功能
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta

def test_hook_trigger():
    """测试Hook触发逻辑"""
    
    test_cases = [
        {
            "name": "美股走势分析",
            "message": "美股走势及消息面分析",
            "should_trigger": True,
            "expected_market": "us_stock"
        },
        {
            "name": "道琼斯指数",
            "message": "道琼斯指数今天怎么样",
            "should_trigger": True,
            "expected_market": "us_stock"
        },
        {
            "name": "美联储利率决议",
            "message": "美联储利率决议结果",
            "should_trigger": True,
            "expected_market": "us_stock"
        },
        {
            "name": "A股走势分析",
            "message": "A股走势分析",
            "should_trigger": True,
            "expected_market": "a_stock"
        },
        {
            "name": "上证指数",
            "message": "上证指数今天表现",
            "should_trigger": True,
            "expected_market": "a_stock"
        },
        {
            "name": "非触发消息",
            "message": "今天天气怎么样",
            "should_trigger": False,
            "expected_market": None
        },
        {
            "name": "非触发消息2",
            "message": "帮我写一个Python脚本",
            "should_trigger": False,
            "expected_market": None
        }
    ]
    
    print("🧪 监察者预检查Hook测试报告")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        # 运行Hook
        cmd = f'echo \'{json.dumps({"message": test["message"]})}\' | python3 /Users/me/.hermes/hooks/supervisor-precheck.py'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # 解析输出
        try:
            output = json.loads(result.stdout)
            triggered = bool(output.get("system_prompt_append"))
            market_type = output.get("context", {}).get("market_type")
        except:
            triggered = False
            market_type = None
        
        # 验证结果
        success = (triggered == test["should_trigger"]) and \
                  (market_type == test["expected_market"] if test["should_trigger"] else True)
        
        status = "✅ PASS" if success else "❌ FAIL"
        
        if success:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | {test['name']}")
        print(f"      消息: {test['message']}")
        print(f"      预期触发: {test['should_trigger']} | 实际触发: {triggered}")
        if test['should_trigger']:
            print(f"      预期市场: {test['expected_market']} | 实际市场: {market_type}")
        print()
    
    # 汇总
    print("=" * 60)
    print(f"📊 测试结果: {passed}/{len(test_cases)} 通过")
    print(f"   ✅ 通过: {passed}")
    print(f"   ❌ 失败: {failed}")
    print()
    
    if failed == 0:
        print("🎉 所有测试通过！监察者预检查Hook已就绪。")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查Hook逻辑。")
        return 1

def test_timezone_conversion():
    """测试时区换算逻辑"""
    
    print("\n🕐 时区换算测试")
    print("=" * 60)
    
    # 测试用例：北京时间 → 美东时间
    test_times = [
        ("2026-04-30 06:00", "2026-04-29 18:00", "收盘/盘后"),
        ("2026-04-30 21:30", "2026-04-30 09:30", "开盘"),
        ("2026-04-30 04:00", "2026-04-29 16:00", "收盘"),
        ("2026-04-30 02:00", "2026-04-29 14:00", "盘中"),
    ]
    
    for beijing_str, expected_us_str, status in test_times:
        beijing_time = datetime.strptime(beijing_str, "%Y-%m-%d %H:%M")
        us_time = beijing_time - timedelta(hours=12)
        us_str = us_time.strftime("%Y-%m-%d %H:%M")
        
        match = "✅" if us_str == expected_us_str else "❌"
        print(f"{match} 北京时间 {beijing_str} → 美东时间 {us_str} (预期: {expected_us_str}, {status})")
    
    print()

def test_market_status():
    """测试市场状态判断"""
    
    print("\n📊 市场状态判断测试")
    print("=" * 60)
    
    # 测试美股市场状态
    us_cases = [
        (8, "盘前"),
        (9, "盘前"),
        (10, "盘中"),
        (12, "盘中"),
        (15, "盘中"),
        (16, "收盘/盘后"),
        (18, "收盘/盘后"),
    ]
    
    print("美股市场状态：")
    for hour, expected_status in us_cases:
        if hour < 9.5:
            status = "盘前"
        elif 9.5 <= hour < 16:
            status = "盘中"
        else:
            status = "收盘/盘后"
        
        match = "✅" if status == expected_status else "❌"
        print(f"{match} 美东时间 {hour}:00 → {status} (预期: {expected_status})")
    
    # 测试A股市场状态
    a_cases = [
        (8, "盘前"),
        (9, "盘前"),
        (10, "早盘"),
        (11, "早盘"),
        (12, "午休"),
        (14, "午盘"),
        (16, "收盘"),
    ]
    
    print("\nA股市场状态：")
    for hour, expected_status in a_cases:
        if hour < 9.5:
            status = "盘前"
        elif 9.5 <= hour < 11.5:
            status = "早盘"
        elif 11.5 <= hour < 13:
            status = "午休"
        elif 13 <= hour < 15:
            status = "午盘"
        else:
            status = "收盘"
        
        match = "✅" if status == expected_status else "❌"
        print(f"{match} 北京时间 {hour}:00 → {status} (预期: {expected_status})")
    
    print()

def main():
    """主函数"""
    
    # 运行所有测试
    exit_code = test_hook_trigger()
    test_timezone_conversion()
    test_market_status()
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
