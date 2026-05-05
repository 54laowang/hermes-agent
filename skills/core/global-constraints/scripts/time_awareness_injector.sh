#!/bin/bash

# 全局约束 - 时间感知注入
# 通过 Shell Hook 在每个 LLM 调用前自动注入时间上下文

# 获取当前时间信息
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
HOUR=$(date '+%H')
WEEKDAY=$(date '+%A')
WEEKDAY_CN=$(date '+%u') # 1-7, 1=Monday

# 判断时间段
if [ $HOUR -ge 0 ] && [ $HOUR -lt 5 ]; then
    TIME_PERIOD="凌晨"
    TIME_ALERT="🌙 凌晨时段：最高优先级提醒用户休息"
elif [ $HOUR -ge 5 ] && [ $HOUR -lt 8 ]; then
    TIME_PERIOD="清晨"
    TIME_ALERT="🌅 清晨时段：关心夜班工作者状态"
elif [ $HOUR -ge 8 ] && [ $HOUR -lt 12 ]; then
    TIME_PERIOD="上午"
    TIME_ALERT="☀️ 上午时段：正常工作模式"
elif [ $HOUR -ge 12 ] && [ $HOUR -lt 14 ]; then
    TIME_PERIOD="中午"
    TIME_ALERT="🍽️ 中午时段：轻松语气"
elif [ $HOUR -ge 14 ] && [ $HOUR -lt 18 ]; then
    TIME_PERIOD="下午"
    TIME_ALERT="📊 下午时段：高效工作模式"
elif [ $HOUR -ge 18 ] && [ $HOUR -lt 20 ]; then
    TIME_PERIOD="傍晚"
    TIME_ALERT="🌆 傍晚时段：过渡时段"
elif [ $HOUR -ge 20 ] && [ $HOUR -lt 22 ]; then
    TIME_PERIOD="晚上"
    TIME_ALERT="🌃 晚上时段：轻松模式"
else
    TIME_PERIOD="深夜"
    TIME_ALERT="🌙 深夜时段：提醒用户休息"
fi

# 判断是否周末
if [ $WEEKDAY_CN -ge 6 ]; then
    IS_WEEKEND="是"
    WEEKEND_ALERT="🎉 周末时段：理解用户可能不想聊严肃工作话题"
else
    IS_WEEKEND="否"
    WEEKEND_ALERT=""
fi

# 判断是否夜班工作者刚下班（基于用户 profile）
# 用户工作时间：20:00-08:00
if [ $HOUR -ge 6 ] && [ $HOUR -lt 8 ]; then
    NIGHT_SHIFT_ALERT="🌅 用户刚下夜班：关心休息，简洁执行"
else
    NIGHT_SHIFT_ALERT=""
fi

# 输出时间感知上下文
cat <<EOF

---
【全局约束 - 时间感知】
现在是：$CURRENT_TIME
星期：$WEEKDAY
时间段：$TIME_PERIOD
是否周末：$IS_WEEKEND

行为准则：
1. 如果当前是凌晨（0:00-5:00）或深夜（22:00 以后），主动提醒用户注意休息
2. 如果是周末，理解用户可能不想聊严肃的工作话题（除非用户明确要求）
3. 感知时间流逝，长时间间隔后的对话可以自然地"重新接上话题"
---

EOF

# 输出特定时段提醒
if [ -n "$TIME_ALERT" ]; then
    echo "⏰ $TIME_ALERT"
fi

if [ -n "$WEEKEND_ALERT" ]; then
    echo "$WEEKEND_ALERT"
fi

if [ -n "$NIGHT_SHIFT_ALERT" ]; then
    echo "$NIGHT_SHIFT_ALERT"
fi

# 判断是否需要特殊行为
if [ $HOUR -ge 0 ] && [ $HOUR -lt 5 ]; then
    echo "⚠️ 凌晨时段强制约束："
    echo "  - 开场白必须提醒休息"
    echo "  - 禁止主动推送工作内容"
    echo "  - 禁止长篇大论分析"
fi

if [ $HOUR -ge 22 ]; then
    echo "⚠️ 深夜时段推荐约束："
    echo "  - 可选提醒休息"
    echo "  - 任务执行简洁高效"
fi
