#!/bin/bash
# Hindsight 停止脚本

echo "=== 停止 Hindsight 记忆系统 ==="

if docker ps | grep -q hindsight; then
    docker stop hindsight
    echo "✅ Hindsight 已停止"
elif docker ps -a | grep -q hindsight; then
    echo "⚠️  Hindsight 已处于停止状态"
else
    echo "⚠️  Hindsight 容器不存在"
fi
