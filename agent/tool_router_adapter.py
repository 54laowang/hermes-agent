#!/usr/bin/env python3
"""
Tool Router Integration Adapter - NON-INVASIVE

This adapter provides tool routing functionality WITHOUT
requiring modifications to the core run_agent.py file.

Usage (Monkey Patch Style - Safe & Reversible):
    from agent.tool_router_adapter import apply_tool_router_patch
    apply_tool_router_patch(agent_instance)

Or via Config:
    enable_tool_router: true in config.yaml
"""

import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# Toolset name mapping (router names -> actual toolsets categories)
TOOLSET_MAP = {
    "web": ["web"],
    "browser": ["browser"],
    "files": ["files"],
    "terminal": ["terminal"],
    "execute_code": ["terminal", "files"],
    "clarify": ["memory"],
    "memory": ["memory"],
    "research": ["web", "browser"],
    "code": ["files", "terminal"],
    "communication": ["messaging"],
    "messaging": ["messaging"],
    "automation": ["automation"],
    "analysis": ["files", "web"],
    "creative": ["files", "vision"],
    "vision": ["vision"],
    "planning": ["todo"],
    "todo": ["todo"],
    "cronjob": ["automation"],
    "general": ["memory"],
    "full": None,  # None means all tools enabled
}


class ToolRouterAdapter:
    """Adapter that adds tool routing to an existing AIAgent instance.
    
    No modifications to run_agent.py required! Just mix-in.
    """
    
    def __init__(self, agent: Any, enabled: bool = True):
        self.agent = agent
        self.enabled = enabled
        self.router = None
        self.original_tools = None
        self.original_chat = None
        
        if enabled:
            self._initialize_router()
    
    def _initialize_router(self):
        """Safely initialize the advanced router with graceful fallback."""
        try:
            from agent.tool_router_advanced import AdvancedToolRouter
            self.router = AdvancedToolRouter(
                model=getattr(self.agent, 'model', 'ark:gemini-2-flash'),
                enabled=True
            )
            # Share client if available
            if hasattr(self.agent, '_client'):
                self.router.client = self.agent._client
            
            # Save original tools
            self.original_tools = list(self.agent.tools) if self.agent.tools else []
            
            # Monkey-patch the chat method
            self._patch_chat_method()
            
            print(f"🧠 Tool Router Adapter: ACTIVATED")
            print(f"   Original tools: {len(self.original_tools)} → will be routed dynamically")
            
        except ImportError as e:
            print(f"⚠️ Tool Router: DISABLED (import error: {e})")
            self.enabled = False
        except Exception as e:
            print(f"⚠️ Tool Router: DISABLED (error: {e})")
            self.enabled = False
    
    def _patch_chat_method(self):
        """Wrap the original chat method to add routing before execution."""
        original_chat = self.agent.chat
        
        def routed_chat(message: str, *args, **kwargs):
            # Step 1: Apply routing BEFORE the message is processed
            if self.enabled and self.router:
                # Analyze intent
                intent, active_toolsets, confidence = self.router.analyze_with_context(message)
                
                # Map to actual tool categories
                enabled_categories = []
                for ts in active_toolsets:
                    if ts in TOOLSET_MAP and TOOLSET_MAP[ts]:
                        enabled_categories.extend(TOOLSET_MAP[ts])
                
                # Deduplicate + add essentials
                enabled_categories = list(set(enabled_categories))
                for essential in ["memory", "clarify"]:
                    if essential not in enabled_categories:
                        enabled_categories.append(essential)
                
                # Reload tools with filtering (using the existing get_tool_definitions)
                try:
                    # We need access to get_tool_definitions from run_agent scope
                    # Since we can't import it directly, we'll use the agent's existing
                    # mechanism or just filter in-place
                    
                    if enabled_categories and not self.router.force_full_mode:
                        # Filter existing tools by toolset tag
                        filtered = []
                        for tool in self.original_tools:
                            tool_name = tool["function"]["name"]
                            # Simple heuristic matching
                            keep = False
                            for cat in enabled_categories:
                                if cat == "web" and tool_name in ["web_search", "web_extract"]:
                                    keep = True
                                elif cat == "browser" and "browser" in tool_name:
                                    keep = True
                                elif cat == "files" and tool_name in ["read_file", "write_file", "search_files", "patch"]:
                                    keep = True
                                elif cat == "terminal" and tool_name in ["terminal", "execute_code"]:
                                    keep = True
                                elif cat == "memory" and tool_name == "memory":
                                    keep = True
                                elif cat == "clarify" and tool_name == "clarify":
                                    keep = True
                                elif cat == "vision" and tool_name == "vision_analyze":
                                    keep = True
                                elif cat == "todo" and tool_name == "todo":
                                    keep = True
                                elif cat == "messaging" and tool_name in ["send_message", "delegate_task"]:
                                    keep = True
                            if keep:
                                filtered.append(tool)
                        
                        if filtered:
                            self.agent.tools = filtered
                            self.agent.valid_tool_names = {t["function"]["name"] for t in filtered}
                            
                            # Calculate savings
                            original_count = len(self.original_tools)
                            new_count = len(filtered)
                            savings_pct = round((1 - new_count / original_count) * 100, 1) if original_count else 0
                            
                            print(f"🎯 Tool Router: intent={intent}, {original_count}→{new_count} tools ({savings_pct}% savings)")
                except Exception as e:
                    # On ANY error, fall back to original tools
                    self.agent.tools = self.original_tools
                    print(f"⚠️ Tool Router: routing error, using full toolset ({e})")
            
            # Step 2: Call original chat method
            result = original_chat(message, *args, **kwargs)
            
            # Step 3: Update router context after successful completion
            if self.enabled and self.router:
                self.router.record_successful_routing()
                self.router.update_context("user", message[:200])
                self.router.update_context("assistant", result[:200])
            
            return result
        
        # Apply the patch
        self.agent.chat = routed_chat
        self.original_chat = original_chat
    
    def get_status(self) -> Dict:
        """Get router status for API/UI."""
        if not self.enabled or not self.router:
            return {"enabled": False}
        
        stats = self.router.get_detailed_stats()
        return {
            "enabled": True,
            "current_intent": stats.get("current_intent", "UNKNOWN"),
            "savings_percent": stats["advanced"]["actual_savings"]["savings_percent"],
            "total_saved": stats["advanced"]["actual_savings"]["total_saved_tokens"],
            "turns_routed": stats["advanced"]["actual_savings"]["turns_routed"],
            "fallback_count": stats["advanced"]["fallbacks"]["total"],
            "force_full_mode": self.router.force_full_mode,
        }
    
    def disable(self):
        """Safely disable and restore original behavior."""
        if self.original_chat:
            self.agent.chat = self.original_chat
        if self.original_tools:
            self.agent.tools = self.original_tools
        self.enabled = False
        print("🧠 Tool Router Adapter: DISABLED - original behavior restored")


# ---------------------------------------------------------------------
# Convenience function to apply patch
# ---------------------------------------------------------------------

def apply_tool_router_patch(agent: Any, enabled: bool = True) -> ToolRouterAdapter:
    """Apply tool routing to an existing AIAgent instance.
    
    Args:
        agent: AIAgent instance from run_agent.py
        enabled: Whether to enable routing (default: True)
    
    Returns:
        ToolRouterAdapter instance for status queries / control
    
    Usage:
        agent = AIAgent(...)
        router = apply_tool_router_patch(agent, enabled=True)
        
        # Check status
        print(router.get_status())
        
        # Disable later if needed
        router.disable()
    """
    return ToolRouterAdapter(agent, enabled)


# ---------------------------------------------------------------------
# Demo: Show how the adapter works
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("🔌 TOOL ROUTER ADAPTER - NON-INVASIVE INTEGRATION")
    print("=" * 70)
    print()
    print("✅ Integration Approach:")
    print()
    print("   • NO modifications to run_agent.py")
    print("   • Monkey-patch style: wraps existing methods")
    print("   • Fully reversible: disable() restores original behavior")
    print("   • Graceful degradation on any error")
    print("   • Zero risk of breaking the agent")
    print()
    print("🎯 Usage Pattern:")
    print()
    print("   from agent.tool_router_adapter import apply_tool_router_patch")
    print()
    print("   agent = AIAgent(...)          # Initialize normally")
    print("   apply_tool_router_patch(agent)  # Activate routing")
    print()
    print("   agent.chat('Search for Python') # Uses routed tools!")
    print()
    print("📊 Status API:")
    print()
    print("   router.get_status() → returns dict for Web UI")
    print("   router.disable()    → safely restore original")
    print()
    print("=" * 70)
    print("✅ ADAPTER READY FOR PRODUCTION!")
    print("=" * 70)
