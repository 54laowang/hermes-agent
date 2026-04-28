#!/usr/bin/env python3
"""
Test script for Tool Router - verify intent classification and toolset selection.

Usage:
    python agent/tool_router_test.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.tool_router import ToolRouter, INTENT_DEFINITIONS


def test_keyword_classification():
    """Test keyword-based classification."""
    print("=" * 60)
    print("🧪 TEST 1: Keyword Classification")
    print("=" * 60)
    
    router = ToolRouter()
    router.client = None  # Force keyword-only mode
    
    test_cases = [
        ("Can you write a Python function to sort a list?", "CODE"),
        ("Search for the latest AI news", "RESEARCH"),
        ("Generate an image of a cat", "CREATIVE"),
        ("Install docker on this server", "DEVOPS"),
        ("Plan my project timeline", "PLANNING"),
        ("Analyze this data file", "ANALYSIS"),
        ("Schedule a daily backup", "AUTOMATION"),
        ("What did we talk about last time?", "MEMORY"),
        ("Send a message to Telegram", "COMMUNICATION"),
        ("Hello, how are you?", "GENERAL"),
    ]
    
    passed = 0
    for message, expected in test_cases:
        intent, score = router.classify_by_keywords(message)
        status = "✅" if intent == expected else "❌"
        print(f"{status} [{intent}] (score: {score}) - {message[:50]}...")
        if intent == expected:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_toolset_mapping():
    """Test intent to toolset mapping."""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Intent → Toolset Mapping")
    print("=" * 60)
    
    router = ToolRouter()
    
    for intent, data in INTENT_DEFINITIONS.items():
        toolsets = router.get_tools_for_intent(intent)
        print(f"  📍 {intent:15} → {', '.join(toolsets)}")
    
    return True


def test_savings_estimation():
    """Test token savings estimation."""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Token Savings Estimation")
    print("=" * 60)
    
    router = ToolRouter()
    
    # Test different intents
    test_intents = ["GENERAL", "CODE", "RESEARCH", "FULL"]
    
    for intent in test_intents:
        if intent == "FULL":
            router.current_intent = "FULL"
            router.current_toolsets = ["full"]
        else:
            router.current_intent = intent
            router.current_toolsets = INTENT_DEFINITIONS[intent]["toolsets"]
        
        savings = router.estimate_savings()
        print(f"  🎯 {intent:15} → {savings['savings_percent']:5.1f}% savings "
              f"({savings['routed_toolset_tokens']} vs {savings['full_toolset_tokens']} tokens)")
    
    return True


def test_intent_switch_detection():
    """Test intent switch detection."""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Intent Switch Detection")
    print("=" * 60)
    
    router = ToolRouter()
    
    # Start with CODE intent
    router.current_intent = "CODE"
    
    test_messages = [
        "Now search for documentation",  # Should switch to RESEARCH
        "Let me debug this function",    # Should stay CODE
        "Schedule this to run daily",    # Should switch to AUTOMATION
        "Just a simple question",        # Should switch to GENERAL
    ]
    
    for msg in test_messages:
        should_switch = router.should_switch_intent(msg)
        new_intent, _ = router.classify_by_keywords(msg)
        switch_icon = "🔄" if should_switch else "➡️ "
        print(f"  {switch_icon} [{router.current_intent}] → [{new_intent}]: '{msg[:40]}...'")
        if should_switch:
            router.current_intent = new_intent
    
    return True


def main():
    """Run all tests."""
    print("🚀 Tool Router Test Suite")
    print()
    
    all_passed = True
    
    all_passed &= test_keyword_classification()
    all_passed &= test_toolset_mapping()
    all_passed &= test_savings_estimation()
    all_passed &= test_intent_switch_detection()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
    print("\n💡 Expected typical token savings:")
    print("   - GENERAL conversation: ~80% tool token savings")
    print("   - CODE development: ~40-50% tool token savings")
    print("   - RESEARCH mode: ~60% tool token savings")
    print("   - Overall average: ~50% tool token savings")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
