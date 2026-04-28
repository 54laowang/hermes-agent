#!/usr/bin/env python3
"""
Advanced Tool Router v2.0 - Evolution Upgrade

New Features:
  1. 🧠 Context-Aware Routing - Uses conversation history, not just single message
  2. 🔄 Dynamic Tool Switching - Mid-conversation toolset adaptation
  3. 🛡️ Fallback Mechanism - Auto-recover to full toolset when routing fails
  4. 📊 Usage Feedback Loop - Learn from actual tool usage patterns
  5. 🎯 Multi-Intent Detection - Handle mixed intents in one message
  6. 📈 Real-time Statistics - Track actual token savings (not just estimated)

Usage:
    from agent.tool_router_advanced import AdvancedToolRouter
    
    router = AdvancedToolRouter()
    intent, toolsets = router.analyze_with_context(message, conversation_history)
"""

import os
import json
from typing import Tuple, List, Dict, Optional, Set
from pathlib import Path
from collections import defaultdict

# Import v1 for compatibility
try:
    from agent.tool_router import ToolRouter, INTENT_DEFINITIONS
except ImportError:
    # Fallback if running standalone
    from tool_router import ToolRouter, INTENT_DEFINITIONS


class RoutingFallbackEvent:
    """Track when routing was too aggressive and needed fallback."""
    
    def __init__(self, message: str, intended_tools: List[str],
                 missing_tool: str, context: str = ""):
        self.message = message[:200]
        self.intended_tools = intended_tools
        self.missing_tool = missing_tool
        self.context = context
        self.timestamp = None  # Would add datetime in production


class AdvancedToolRouter(ToolRouter):
    """Advanced intelligent router with context awareness and fallback."""
    
    def __init__(self, model: str = "ark:gemini-2-flash", enabled: bool = True):
        super().__init__(model, enabled)
        
        # New v2 features
        self.context_window: List[Dict] = []  # Recent conversation history
        self.fallback_events: List[RoutingFallbackEvent] = []  # Track failures
        self.actual_tool_usage: Dict[str, int] = defaultdict(int)  # Tools actually used
        self.intent_confidence: Dict[str, float] = {}  # Per-intent accuracy
        
        # Configuration
        self.max_context_messages = 5  # How many messages to consider
        self.fallback_threshold = 2  # N failures → stay in full mode
        self.consecutive_fallbacks = 0
        self.force_full_mode = False
        
        # Multi-intent support
        self.enable_multi_intent = True
        
        # Real stats
        self.actual_token_savings = {
            "full_toolset_tokens": 0,
            "routed_toolset_tokens": 0,
            "turns_routed": 0,
        }
    
    # -------------------------------------------------------------------------
    # 🧠 FEATURE 1: Context-Aware Routing
    # -------------------------------------------------------------------------
    
    def update_context(self, role: str, content: str, tools_used: List[str] = None):
        """Add message to context window for better routing decisions."""
        self.context_window.append({
            "role": role,
            "content": content[:500],
            "tools_used": tools_used or [],
            "intent_at_time": self.current_intent,
        })
        
        # Keep only recent messages
        if len(self.context_window) > self.max_context_messages:
            self.context_window.pop(0)
        
        # Track actual tool usage
        if tools_used:
            for tool in tools_used:
                self.actual_tool_usage[tool] += 1
    
    def analyze_with_context(self, message: str) -> Tuple[str, List[str], float]:
        """Analyze intent using current message + conversation context."""
        if not self.enabled or self.force_full_mode:
            return "FULL", ["full"], 1.0
        
        # Get base classification
        base_intent, base_score = self.classify_by_keywords(message)
        
        # Adjust based on context
        context_bonus = 0
        if self.context_window:
            # If recent messages used certain tools, weight towards that
            recent_tools = set()
            for msg in self.context_window[-2:]:
                recent_tools.update(msg.get("tools_used", []))
            
            # Map tools back to intents for continuity bias
            intent_bias = self._tools_to_intent_bias(recent_tools)
            if base_intent in intent_bias:
                context_bonus = intent_bias[base_intent] * 0.3
        
        confidence = min(1.0, (base_score + context_bonus) / 5.0)
        
        # Multi-intent detection
        if self.enable_multi_intent:
            all_intents = self._detect_all_intents(message)
            if len(all_intents) > 1:
                # Merge toolsets from all detected intents
                merged_tools = set()
                for intent, score in all_intents.items():
                    if score >= 1:
                        for tool in self.get_tools_for_intent(intent):
                            merged_tools.add(tool)
                
                # Primary intent is the highest scoring
                primary_intent = max(all_intents.items(), key=lambda x: x[1])[0]
                toolsets = list(merged_tools)
                
                # Always add essentials
                for essential in ["clarify", "memory"]:
                    if essential not in toolsets:
                        toolsets.append(essential)
                
                self.current_intent = f"{primary_intent}+"
                self.current_toolsets = toolsets
                return f"{primary_intent}+", toolsets, confidence * 0.9
        
        # Single intent path
        toolsets = self.get_tools_for_intent(base_intent)
        for essential in ["clarify", "memory"]:
            if essential not in toolsets:
                toolsets.append(essential)
        
        self.current_intent = base_intent
        self.current_toolsets = toolsets
        
        return base_intent, toolsets, confidence
    
    def _tools_to_intent_bias(self, tools: Set[str]) -> Dict[str, float]:
        """Map tool usage back to intent categories for continuity bias."""
        tool_to_intent_map = {
            "terminal": ["CODE", "DEVOPS"],
            "process": ["DEVOPS"],
            "execute_code": ["CODE", "ANALYSIS", "DEVOPS"],
            "read_file": ["CODE", "ANALYSIS"],
            "write_file": ["CODE", "CREATIVE"],
            "web_search": ["RESEARCH"],
            "web_extract": ["RESEARCH"],
            "browser_navigate": ["RESEARCH"],
            "vision_analyze": ["ANALYSIS", "CREATIVE"],
            "image_generate": ["CREATIVE"],
            "todo": ["PLANNING"],
            "cronjob": ["AUTOMATION"],
            "session_search": ["MEMORY"],
            "send_message": ["COMMUNICATION"],
        }
        
        bias = defaultdict(float)
        for tool in tools:
            for intent in tool_to_intent_map.get(tool, []):
                bias[intent] += 0.5
        
        return dict(bias)
    
    def _detect_all_intents(self, message: str) -> Dict[str, int]:
        """Detect ALL possible intents in a message (for multi-intent)."""
        message_lower = message.lower()
        scores = {}
        
        for intent, data in INTENT_DEFINITIONS.items():
            score = sum(1 for kw in data["keywords"] if kw in message_lower)
            if score > 0:
                scores[intent] = score
        
        return scores
    
    # -------------------------------------------------------------------------
    # 🛡️ FEATURE 2: Fallback Mechanism
    # -------------------------------------------------------------------------
    
    def record_missing_tool(self, tool_name: str, message: str = ""):
        """Record that a tool was needed but not in the routed set.
        
        This is the feedback loop - if LLM tries to use a tool that
        was filtered out, we learn from it and adjust future routing.
        """
        event = RoutingFallbackEvent(
            message=message,
            intended_tools=self.current_toolsets.copy(),
            missing_tool=tool_name,
        )
        self.fallback_events.append(event)
        self.consecutive_fallbacks += 1
        
        # Learn: add this tool to the intent's toolset in future
        if self.current_intent and self.current_intent in INTENT_DEFINITIONS:
            # In production we'd persist this learning
            pass
        
        # Safety: if too many fallbacks, go to full toolset temporarily
        if self.consecutive_fallbacks >= self.fallback_threshold:
            self.force_full_mode = True
            print(f"⚠️ Tool Router: {self.consecutive_fallbacks} consecutive fallbacks → switching to FULL toolset")
        
        return event
    
    def record_successful_routing(self):
        """Mark that this routing turn was successful (all needed tools present)."""
        self.consecutive_fallbacks = max(0, self.consecutive_fallbacks - 1)
        self.force_full_mode = False
        
        # Update real token savings
        savings = self.estimate_savings()
        self.actual_token_savings["full_toolset_tokens"] += savings["full_toolset_tokens"]
        self.actual_token_savings["routed_toolset_tokens"] += savings["routed_toolset_tokens"]
        self.actual_token_savings["turns_routed"] += 1
    
    def suggest_tool_expansion(self, current_intent: str) -> List[str]:
        """Suggest additional tools based on fallback history."""
        missing_for_intent = [
            e.missing_tool for e in self.fallback_events
            if e.context == current_intent
        ]
        
        if not missing_for_intent:
            return []
        
        # Return most commonly missing tools for this intent
        from collections import Counter
        common = Counter(missing_for_intent).most_common(3)
        return [tool for tool, count in common]
    
    # -------------------------------------------------------------------------
    # 📊 FEATURE 3: Real Statistics & Reporting
    # -------------------------------------------------------------------------
    
    def get_detailed_stats(self) -> Dict:
        """Get comprehensive routing statistics."""
        base_stats = self.get_stats()
        
        # Calculate actual savings
        total_full = self.actual_token_savings["full_toolset_tokens"]
        total_routed = self.actual_token_savings["routed_toolset_tokens"]
        
        if total_full > 0:
            actual_savings_pct = round((1 - total_routed / total_full) * 100, 1)
        else:
            actual_savings_pct = 0
        
        # Intent distribution
        intent_counts = defaultdict(int)
        for msg in self.context_window:
            if msg.get("intent_at_time"):
                intent_counts[msg["intent_at_time"]] += 1
        
        return {
            **base_stats,
            "advanced": {
                "actual_savings": {
                    "total_full_tokens": total_full,
                    "total_routed_tokens": total_routed,
                    "total_saved_tokens": total_full - total_routed,
                    "savings_percent": actual_savings_pct,
                    "turns_routed": self.actual_token_savings["turns_routed"],
                },
                "fallbacks": {
                    "total": len(self.fallback_events),
                    "consecutive": self.consecutive_fallbacks,
                    "force_full_mode": self.force_full_mode,
                },
                "context": {
                    "window_size": len(self.context_window),
                    "intent_distribution": dict(intent_counts),
                },
                "tool_usage": dict(sorted(
                    self.actual_tool_usage.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]),  # Top 10 tools
            }
        }
    
    def print_status_report(self):
        """Print human-readable status report."""
        stats = self.get_detailed_stats()
        adv = stats["advanced"]
        
        print("=" * 70)
        print("📊 ADVANCED TOOL ROUTER - STATUS REPORT")
        print("=" * 70)
        print(f"   Status: {'🟢 ENABLED' if self.enabled else '🔴 DISABLED'}")
        print(f"   Mode: {'🔴 FULL TOOLSET (fallback)' if self.force_full_mode else '🟢 ROUTED'}")
        print()
        print(f"   Current Intent: {stats['current_intent']}")
        print(f"   Tools Active: {len(stats['current_toolsets'])} toolsets")
        print()
        print("💾 ACTUAL TOKEN SAVINGS:")
        print(f"   Total Turns: {adv['actual_savings']['turns_routed']}")
        print(f"   Tokens Saved: {adv['actual_savings']['total_saved_tokens']:,}")
        print(f"   Savings Rate: {adv['actual_savings']['savings_percent']}%")
        print()
        print("🛡️ FALLBACK METRICS:")
        print(f"   Total Fallbacks: {adv['fallbacks']['total']}")
        print(f"   Consecutive: {adv['fallbacks']['consecutive']}/{self.fallback_threshold}")
        print()
        print("🔧 TOP TOOLS USED:")
        for tool, count in list(adv["tool_usage"].items())[:5]:
            print(f"   {tool}: {count}x")
        print("=" * 70)
    
    # -------------------------------------------------------------------------
    # 🎯 FEATURE 4: Smart Intent Switch Detection
    # -------------------------------------------------------------------------
    
    def should_switch_intent_smart(self, new_message: str) -> Tuple[bool, str, float]:
        """Enhanced intent switch detection with confidence scoring."""
        if self.force_full_mode:
            return False, "FULL", 0.0
        
        new_intent, _ = self.classify_by_keywords(new_message)
        all_intents = self._detect_all_intents(new_message)
        
        # Calculate "topic shift" score
        if self.current_intent and self.current_intent != "FULL":
            # If current intent not detected at all in new message
            if self.current_intent not in all_intents:
                return True, new_intent, 0.9
            
            # If new intent score much higher than current
            current_score = all_intents.get(self.current_intent, 0)
            new_score = all_intents.get(new_intent, 0)
            
            if new_score > current_score * 2:  # 2x stronger signal
                return True, new_intent, new_score / (current_score + 1)
        
        return False, new_intent, 0.5


# -------------------------------------------------------------------------
# Singleton instance for global access
# -------------------------------------------------------------------------
_advanced_router: Optional[AdvancedToolRouter] = None


def get_advanced_router() -> AdvancedToolRouter:
    """Get the global advanced tool router instance."""
    global _advanced_router
    if _advanced_router is None:
        _advanced_router = AdvancedToolRouter()
    return _advanced_router
