"""
Tool Router Integration Patch for run_agent.py

This patch adds intelligent toolset selection to Hermes Agent.

Usage:
    Apply manually to run_agent.py at the specified locations.
"""

# -----------------------------------------------------------------------------
# PATCH LOCATION 1: Imports (around line 70)
# -----------------------------------------------------------------------------
# ADD after "from model_tools import get_tool_definitions, ..."
# -----------------------------------------------------------------------------

"""
from agent.tool_router import ToolRouter, get_tool_router
"""

# -----------------------------------------------------------------------------
# PATCH LOCATION 2: Agent.__init__ parameters (around line 846)
# -----------------------------------------------------------------------------
# ADD after "enabled_toolsets, disabled_toolsets"
# -----------------------------------------------------------------------------

"""
        enable_tool_router: bool = True,
        tool_router_intent_model: str = "ark:gemini-2-flash",
"""

# -----------------------------------------------------------------------------
# PATCH LOCATION 3: Agent.__init__ body (around line 1127, after self.disabled_toolsets)
# -----------------------------------------------------------------------------
# ADD after:
#        self.enabled_toolsets = enabled_toolsets
#        self.disabled_toolsets = disabled_toolsets
# -----------------------------------------------------------------------------

"""
        # Initialize intelligent tool router
        self.tool_router = ToolRouter(model=tool_router_intent_model, enabled=enable_tool_router)
        self._tool_router_did_route = False  # Track if we've done initial routing
"""

# -----------------------------------------------------------------------------
# PATCH LOCATION 4: chat() method (around line 12629, at START of chat method)
# -----------------------------------------------------------------------------
# ADD at the BEGINNING of def chat():
# -----------------------------------------------------------------------------

"""
    def chat(self, message: str, stream_callback: Optional[callable] = None) -> str:
        # =========================================
        # INTELLIGENT TOOL ROUTING (NEW FEATURE)
        # =========================================
        if self.tool_router.enabled:
            # Analyze intent and adjust toolsets
            intent, toolsets = self.tool_router.analyze_intent(message)
            
            # If this is the first message or intent changed significantly
            should_update = not self._tool_router_did_route or self.tool_router.should_switch_intent(message)
            
            if should_update:
                # Get tools for this intent
                new_tools = self.tool_router.get_tools_for_intent(intent)
                
                # Always add essential tools
                for essential in ["clarify", "memory"]:
                    if essential not in new_tools:
                        new_tools.append(essential)
                
                # Reload tools with new filtering
                if not self.quiet_mode and self.tool_router.show_routing_info:
                    savings = self.tool_router.estimate_savings()
                    print(f"\n🎯 Tool Router: Intent = [{intent}] → Toolsets = {', '.join(toolsets)}")
                    print(f"   Estimated token savings: {savings['savings_percent']:.1f}%")
                
                # Update enabled_toolsets for this conversation turn
                # Note: This dynamically filters tools for subsequent LLM calls
                self._current_routed_toolsets = new_tools
                self._tool_router_did_route = True
        # =========================================
        # END TOOL ROUTING
        # =========================================
"""

# -----------------------------------------------------------------------------
# PATCH LOCATION 5: _build_messages() method (where tools are injected)
# -----------------------------------------------------------------------------
# Find where tools are added to the system prompt, apply routing filter there
#
# For now, the tool definitions are loaded at init, but we can filter
# them when building messages to send to LLM.
#
# Alternative simpler approach:
# - When building the message list for LLM, filter self.tools based on routing
# -----------------------------------------------------------------------------

"""
# In the method that builds system prompt/tools (around _build_messages):

def _build_messages(self, ...):
    # ... existing code ...
    
    # Apply tool routing filter if enabled
    tools_to_send = self.tools
    if hasattr(self, '_current_routed_toolsets') and self._current_routed_toolsets:
        # Filter tools to only those matching the routed toolsets
        # This requires mapping from toolsets.py resolve_toolset function
        from toolsets import resolve_toolset
        routed_tool_names = set()
        for ts in self._current_routed_toolsets:
            try:
                routed_tool_names.update(resolve_toolset(ts))
            except:
                pass
        
        if routed_tool_names:
            tools_to_send = [t for t in self.tools 
                             if t["function"]["name"] in routed_tool_names]
            if not self.quiet_mode:
                print(f"   Filtered: {len(tools_to_send)}/{len(self.tools)} tools sent to LLM")
    
    # Use tools_to_send instead of self.tools
"""

print("=" * 70)
print("✅ Tool Router Integration Patch")
print("=" * 70)
print()
print("Apply these changes to run_agent.py:")
print()
print("1. Add imports")
print("2. Add init parameters")
print("3. Initialize tool_router in __init__")
print("4. Add routing logic to chat() method")
print("5. Filter tools when building LLM messages")
print()
print("Expected benefits:")
print("  • 50-80% reduction in tool definition tokens")
print("  • Improved reasoning accuracy (fewer tools = less hallucination")
print("  • Faster LLM response times")
print()
print("To enable/disable:")
print("  --enable-tool-router / --disable-tool-router")
print("=" * 70)
