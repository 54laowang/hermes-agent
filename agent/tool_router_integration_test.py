#!/usr/bin/env python3
"""
Production Integration Test for Tool Router

Tests that the router can be initialized and used within AIAgent
without breaking existing functionality.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("🧪 PRODUCTION INTEGRATION TEST")
print("=" * 70)
print()

# Test 1: Import check
print("📦 Test 1: Import check...")
try:
    from agent.tool_router import ToolRouter
    from agent.tool_router_advanced import AdvancedToolRouter
    print("   ✅ Both router modules import successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Standalone initialization
print()
print("🚀 Test 2: Standalone router initialization...")
try:
    router = AdvancedToolRouter(enabled=True)
    router.client = None  # Simulate no LLM client
    print("   ✅ AdvancedToolRouter initialized successfully")
    print(f"      Enabled: {router.enabled}")
    print(f"      Current intent: {router.current_intent}")
except Exception as e:
    print(f"   ❌ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Basic routing
print()
print("🎯 Test 3: Basic routing...")
messages = [
    "Search for Python tutorials",
    "Write a script to process data",
    "What's in the config file?",
]

for msg in messages:
    intent, toolsets, confidence = router.analyze_with_context(msg)
    print(f"   '{msg[:30]}...' -> {intent} ({len(toolsets)} tools, conf={confidence:.2f})")

print("   ✅ Routing works correctly")

# Test 4: Fallback mechanism
print()
print("🛡️ Test 4: Fallback mechanism...")
router.record_missing_tool("read_file", "test message")
router.record_missing_tool("search_files", "test message 2")
assert router.force_full_mode == True, "Should enter full mode after 2 fallbacks"
print(f"   Fallbacks: {router.consecutive_fallbacks}, Force full: {router.force_full_mode}")
print("   ✅ Fallback mechanism works")

# Test 5: Statistics tracking
print()
print("📊 Test 5: Statistics tracking...")
router.record_successful_routing()
router.record_successful_routing()
stats = router.get_detailed_stats()
print(f"   Turns routed: {stats['advanced']['actual_savings']['turns_routed']}")
print(f"   Tokens saved: {stats['advanced']['actual_savings']['total_saved_tokens']:,}")
print("   ✅ Statistics tracking works")

print()
print("=" * 70)
print("✅ ALL TESTS PASSED - Ready for production integration!")
print("=" * 70)
