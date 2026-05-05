#!/usr/bin/env python3
"""
一键修复 Hermes 微信消息频率限流问题
Usage: python3 apply-fix.py [delay_seconds]
"""

import yaml
import sys
import subprocess

HERMES_HOME = "/Users/me/.hermes"
CONFIG_PATH = f"{HERMES_HOME}/config.yaml"

def main():
    delay = "0.8"
    if len(sys.argv) > 1:
        delay = sys.argv[1]
    
    print(f"🔧 配置消息发送延迟: {delay} 秒")
    
    # 读取配置
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    # 修改配置
    weixin_config = config.get('platforms', {}).get('weixin', {})
    extra = weixin_config.get('extra', {})
    
    old_delay = extra.get('send_chunk_delay_seconds', '默认 0.35')
    old_retries = extra.get('send_chunk_retries', '默认 2')
    
    print(f"  原延迟: {old_delay}")
    print(f"  原重试: {old_retries}")
    
    extra['send_chunk_delay_seconds'] = delay
    extra['send_chunk_retries'] = '3'
    
    weixin_config['extra'] = extra
    if 'platforms' not in config:
        config['platforms'] = {}
    config['platforms']['weixin'] = weixin_config
    
    # 保存配置
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ 配置已更新")
    print(f"   新延迟: {delay} 秒")
    print(f"   新重试: 3 次")
    print(f"   发送频率: {1/float(delay):.2f} 条/秒")
    
    # 重启网关
    print("\n🔄 重启网关...")
    result = subprocess.run(['hermes', 'gateway', 'restart'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    print("\n✅ 修复完成!")
    print("\n🧪 验证方法:")
    print("  1. 让 Agent 输出一段 1000 字的长文本")
    print("  2. 观察是否能完整、流畅地送达")
    print("  3. 查看日志: tail -50 ~/.hermes/logs/gateway.log")

if __name__ == "__main__":
    main()
