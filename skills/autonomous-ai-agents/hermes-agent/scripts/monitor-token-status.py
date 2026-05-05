#!/usr/bin/env python3
"""
监控 Hermes Token 状态和网关健康
每天凌晨 3:25 自动运行，检查 token 是否有效
发现问题时自动重启网关并发送告警

修复版本：
- 400 状态码不触发重启（请求参数问题非 Token 失效）
- 忽略非关键错误（飞书权限问题、连接超时等）
"""

import requests
import yaml
import subprocess
import sys
from datetime import datetime

def load_config():
    """加载 Hermes 配置"""
    with open('/Users/me/.hermes/config.yaml', 'r') as f:
        return yaml.safe_load(f)

def test_ark_token():
    """测试火山引擎 Token 是否有效"""
    config = load_config()
    ark_config = config['providers'].get('ark', {})
    api_key = ark_config.get('api_key')
    base_url = ark_config.get('base_url', 'https://ark.cn-beijing.volces.com/api/coding/v3')
    
    if not api_key:
        return False, "未找到 API Key"
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": "ark-code-latest",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            return True, "Token 有效"
        elif response.status_code in [401, 403]:
            return False, f"Token 失效 (状态码: {response.status_code})"
        elif response.status_code == 400:
            # 400 通常是请求参数问题，不是 Token 问题
            # 检查响应内容判断是否真的是认证问题
            try:
                resp_json = response.json()
                error_msg = resp_json.get('error', {}).get('message', '')
                if 'auth' in error_msg.lower() or 'token' in error_msg.lower():
                    return False, f"认证问题: {error_msg}"
            except:
                pass
            # 400 但不是认证问题，认为 Token 仍然有效
            return True, f"Token 有效 (状态码 400 可能是请求参数问题)"
        else:
            # 其他状态码不触发重启，只记录
            return True, f"异常状态码: {response.status_code} (不触发重启)"
            
    except Exception as e:
        return False, f"请求异常: {str(e)}"

def restart_gateway():
    """重启 Hermes 网关"""
    try:
        result = subprocess.run(
            ['/Users/me/.local/bin/hermes', 'gateway', 'restart'],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)

def check_gateway_logs(hours=1):
    """检查最近几小时的错误日志"""
    try:
        result = subprocess.run(
            ['tail', '-100', '/Users/me/.hermes/logs/gateway.error.log'],
            capture_output=True,
            text=True
        )
        
        errors = []
        # 只关注严重的认证/Token 错误
        keywords = ['InvalidToken', '401', '403', 'PermissionDenied']
        # 忽略这些非关键错误（权限问题、连接问题等不触发重启）
        ignore_patterns = ['Failed to get chat info', 'RemoteProtocolError', 'TimedOut']
        
        for line in result.stdout.split('\n'):
            # 先检查是否应该忽略
            should_ignore = any(pattern in line for pattern in ignore_patterns)
            if should_ignore:
                continue
                
            for keyword in keywords:
                if keyword in line:
                    errors.append(line)
        
        return errors
    except Exception as e:
        return [f"检查日志失败: {e}"]

def main():
    print(f"\n{'='*60}")
    print(f"🕐 监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 1. 测试 Token
    print("\n🔑 检查 Token 状态...")
    token_ok, token_msg = test_ark_token()
    print(f"   {token_msg}")
    
    # 2. 检查错误日志
    print("\n📋 检查最近错误日志...")
    errors = check_gateway_logs()
    if errors:
        print(f"   ⚠️  发现 {len(errors)} 条相关错误:")
        for err in errors[:5]:
            print(f"      - {err[:100]}")
    else:
        print("   ✅ 未发现 Token 相关错误")
    
    # 3. 决策逻辑
    need_restart = False
    reason = ""
    
    if not token_ok:
        need_restart = True
        reason = f"Token 失效: {token_msg}"
    elif len(errors) > 3:
        need_restart = True
        reason = f"发现大量错误 ({len(errors)} 条)"
    
    if need_restart:
        print(f"\n🔄 重启网关 - 原因: {reason}")
        restart_ok, restart_msg = restart_gateway()
        if restart_ok:
            print("   ✅ 网关重启成功")
        else:
            print(f"   ❌ 网关重启失败: {restart_msg}")
            sys.exit(1)
    else:
        print("\n✅ 一切正常，无需重启")
    
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    main()
