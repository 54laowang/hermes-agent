#!/usr/bin/env python3
"""
Advanced Tool Router v2.0 DEMO

Showcases all evolution features:
  1. 🧠 Context-Aware Routing
  2. 🎯 Multi-Intent Detection  
  3. 🛡️ Fallback Mechanism
  4. 📊 Real-time Statistics
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.tool_router_advanced import AdvancedToolRouter


def demo_context_aware():
    """Show context-aware routing in action."""
    print("=" * 70)
    print("🧠 FEATURE 1: Context-Aware Routing")
    print("=" * 70)
    print()
    print("Conversation evolves, router remembers recent tool usage")
    print()
    
    router = AdvancedToolRouter()
    router.client = None
    
    conversation = [
        ("user", "Hello! What can you do?", None),
        ("assistant", "I can help with coding, research, automation...", None),
        ("user", "Great! Let's write a Python script", None),
        ("assistant", "Sure! What kind of script?", ["write_file", "terminal"]),
        ("user", "Now I need to research best practices", None),  # Context: just did CODE
    ]
    
    print("📋 Conversation History:")
    print("-" * 70)
    
    for role, msg, tools in conversation[:-1]:
        router.update_context(role, msg, tools)
        icon = "👤" if role == "user" else "🤖"
        print(f"   {icon} {msg}")
        if tools:
            print(f"      Tools used: {', '.join(tools)}")
    
    # Last message - the test
    last_msg = conversation[-1][1]
    print(f"\n👤 New message: {last_msg}")
    
    # Without context
    base_intent, _ = router.classify_by_keywords(last_msg)
    print(f"\n   ❌ Without context: Intent = {base_intent}")
    
    # With context
    intent, toolsets, confidence = router.analyze_with_context(last_msg)
    print(f"   ✅ With context:    Intent = {intent} (confidence: {confidence:.2f})")
    print(f"                    Tools = {', '.join(toolsets)}")
    print()
    print("💡 The router remembers we were coding, and keeps CODE tools available")
    print("   while also adding RESEARCH tools.")


def demo_multi_intent():
    """Show multi-intent detection."""
    print("\n" + "=" * 70)
    print("🎯 FEATURE 2: Multi-Intent Detection")
    print("=" * 70)
    print()
    print("Handles messages with multiple intents simultaneously")
    print()
    
    router = AdvancedToolRouter()
    router.client = None
    
    test_messages = [
        "Write a script AND search for documentation",
        "Analyze the data THEN send results via Telegram",
        "Search for info AND schedule a daily task",
    ]
    
    for msg in test_messages:
        all_intents = router._detect_all_intents(msg)
        intent, toolsets, conf = router.analyze_with_context(msg)
        
        print(f"👤 Message: '{msg}'")
        print(f"   🎯 Detected intents: {', '.join(all_intents.keys())}")
        print(f"   🛠️ Merged tools: {', '.join(toolsets)}")
        print()
    
    print("💡 Messages with mixed intents get union of all relevant tools")
    print("   No more 'tool not available' errors during complex tasks")


def demo_fallback_mechanism():
    """Show intelligent fallback and recovery."""
    print("\n" + "=" * 70)
    print("🛡️ FEATURE 3: Smart Fallback Mechanism")
    print("=" * 70)
    print()
    print("Learns from mistakes and prevents cascading failures")
    print()
    
    router = AdvancedToolRouter()
    router.client = None
    router.fallback_threshold = 2  # Lower for demo
    
    # Simulate a routing failure scenario
    print("📋 Scenario:")
    print("   1. User asks a simple question → GENERAL intent (minimal tools)")
    print("   2. But LLM actually needs to read a file")
    print("   3. Router learns and adapts")
    print()
    
    message = "What's in the config file?"
    intent, toolsets, _ = router.analyze_with_context(message)
    
    print(f"👤 User: {message}")
    print(f"🎯 Router:  Intent = {intent}")
    print(f"           Tools  = {', '.join(toolsets)}")
    print()
    
    # Oh no! LLM tries to use read_file but it's not available
    print("❌ LLM tries to call: read_file (NOT IN ROUTED SET!)")
    print()
    print("📝 Router records the fallback event and learns...")
    print()
    
    router.record_missing_tool("read_file", message)
    router.record_missing_tool("search_files", message)
    
    print(f"   Fallback count: {router.consecutive_fallbacks}/{router.fallback_threshold}")
    print(f"   Force full mode: {router.force_full_mode}")
    
    # Second fallback triggers full mode
    print()
    print("🔄 Second fallback triggers safety mode...")
    router.record_missing_tool("web_search", "another message")
    
    print(f"   Fallback count: {router.consecutive_fallbacks}/{router.fallback_threshold}")
    print(f"   Force full mode: {router.force_full_mode}")
    print()
    print("✅ Now router uses FULL toolset until things stabilize")
    print("   No more frustration from missing tools!")


def demo_real_statistics():
    """Show real statistics collection."""
    print("\n" + "=" * 70)
    print("📊 FEATURE 4: Real-Time Statistics & Reporting")
    print("=" * 70)
    print()
    
    router = AdvancedToolRouter()
    router.client = None
    
    # Simulate a day's worth of routing
    simulated_day = [
        ("Hello!", "GENERAL", [], True),
        ("Search for Python news", "RESEARCH", ["web_search"], True),
        ("Write a script", "CODE", ["write_file", "execute_code"], True),
        ("Run the script", "CODE", ["terminal", "execute_code"], True),
        ("Schedule daily run", "AUTOMATION", ["cronjob"], True),
        ("What did we do?", "MEMORY", ["session_search"], True),
    ]
    
    for msg, intent, tools, success in simulated_day:
        router.current_intent = intent
        router.current_toolsets = router.get_tools_for_intent(intent)
        router.update_context("user", msg, tools)
        if success:
            router.record_successful_routing()
    
    # Add one fallback
    router.record_missing_tool("vision_analyze", "need to analyze image")
    
    # Show report
    router.print_status_report()
    
    # Monetary estimate
    stats = router.get_detailed_stats()
    saved = stats["advanced"]["actual_savings"]["total_saved_tokens"]
    # Estimate: $0.01 per 1K tool tokens (mixed input pricing)
    saved_usd = saved * 0.01 / 1000
    
    print()
    print(f"💰 Estimated cost saved: ${saved_usd:.4f} USD")
    print(f"   (at $0.01/1K tool tokens)")
    print()
    print("💡 At 100 turns/day/user → ~$10-50/user/month saved!")


def main():
    """Run all demos."""
    print()
    print("🚀 TOOL ROUTER v2.0 - EVOLUTION DEMO")
    print("=" * 70)
    
    demo_context_aware()
    demo_multi_intent()
    demo_fallback_mechanism()
    demo_real_statistics()
    
    print("\n" + "=" * 70)
    print("🏆 EVOLUTION SUMMARY")
    print("=" * 70)
    print()
    print("v1.0 → v2.0 IMPROVEMENTS:")
    print()
    print("  🧠 Context Awareness:")
    print("     • Uses conversation history, not just single message")
    print("     • Maintains continuity during task switching")
    print("     • Better confidence scoring")
    print()
    print("  🎯 Multi-Intent Support:")
    print("     • Detects ALL intents in complex messages")
    print("     • Merges toolsets automatically")
    print("     • Handles 'do A AND do B' patterns")
    print()
    print("  🛡️ Fallback Protection:")
    print("     • Learns from missing tool incidents")
    print("     • Auto-switches to full toolset when needed")
    print("     • Prevents cascading failures")
    print()
    print("  📊 Real Statistics:")
    print("     • Tracks actual (not estimated) token savings")
    print("     • Tool usage patterns for optimization")
    print("     • Fallback rate monitoring")
    print()
    print("📈 NEXT EVOLUTION (v3.0):")
    print("     • ML model for intent classification")
    print("     • Personalized routing per user")
    print("     • A/B testing framework")
    print("     • Predictive tool pre-loading")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
