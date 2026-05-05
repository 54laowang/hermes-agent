"""
Integration hook for Tool Router - Paste into your main agent file.

This is the minimal code needed to integrate intelligent tool routing.
"""

# -----------------------------------------------------------------------------
# 1. IMPORTS (add at top of file)
# -----------------------------------------------------------------------------
from agent.tool_router import ToolRouter, INTENT_DEFINITIONS, TOOLSET_TOOLS


# -----------------------------------------------------------------------------
# 2. INITIALIZATION (add to __init__)
# -----------------------------------------------------------------------------
def __init__(self, ..., enable_tool_router: bool = True):
    # ... existing init code ...
    
    # Initialize intelligent tool router
    self.tool_router = ToolRouter(enabled=enable_tool_router)
    self._tool_router_did_route = False


# -----------------------------------------------------------------------------
# 3. CHAT METHOD HOOK (add at START of chat/handle_message method)
# -----------------------------------------------------------------------------
def chat(self, message: str, ...):
    # =========================================
    # INTELLIGENT TOOL ROUTING (NEW FEATURE)
    # =========================================
    if self.tool_router.enabled:
        intent, toolsets = self.tool_router.analyze_intent(message)
        
        should_update = not self._tool_router_did_route or self.tool_router.should_switch_intent(message)
        
        if should_update:
            # Get tools for this intent
            new_toolsets = self.tool_router.get_tools_for_intent(intent)
            
            # Always add essential tools
            for essential in ["clarify", "memory"]:
                if essential not in new_toolsets:
                    new_toolsets.append(essential)
            
            # Show routing info
            savings = self.tool_router.estimate_savings()
            if not self.quiet_mode:
                print(f"\n🎯 Tool Router: Intent = [{intent}] → {', '.join(toolsets)}")
                print(f"   Token savings: {savings['savings_percent']:.1f}%")
            
            # Store for tool filtering
            self._current_routed_toolsets = new_toolsets
            self._tool_router_did_route = True
    # =========================================
    # END TOOL ROUTING
    # =========================================
    
    # ... rest of chat method ...


# -----------------------------------------------------------------------------
# 4. TOOL FILTERING (apply when building messages for LLM)
# -----------------------------------------------------------------------------
def _build_messages(self, ...):
    # ... existing code ...
    
    # Filter tools based on routing
    tools_to_send = self.all_tools
    
    if hasattr(self, '_current_routed_toolsets') and self._current_routed_toolsets:
        routed_tool_names = set()
        for ts in self._current_routed_toolsets:
            routed_tool_names.update(TOOLSET_TOOLS.get(ts, []))
        
        if routed_tool_names:
            tools_to_send = [t for t in self.all_tools
                             if t["function"]["name"] in routed_tool_names]
            
            if not self.quiet_mode:
                print(f"   Filtered: {len(tools_to_send)}/{len(self.all_tools)} tools")
    
    # Use tools_to_send instead of self.all_tools
    # ...


# -----------------------------------------------------------------------------
# 5. CLI ARGUMENTS (add to argparse)
# -----------------------------------------------------------------------------
#     parser.add_argument("--enable-tool-router", action="store_true",
#                         default=True, help="Enable intelligent tool routing")
#     parser.add_argument("--disable-tool-router", action="store_true",
#                         help="Disable intelligent tool routing")
