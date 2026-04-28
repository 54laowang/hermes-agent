#!/usr/bin/env python3
"""
Web Server API Patch for Tool Router

Adds /api/router/* endpoints to the existing FastAPI server.
Usage: Import and call register_router_endpoints(app)
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Optional

# Global reference to the agent (set by the web server when ready)
_current_agent = None


def set_agent_for_api(agent):
    """Set the global agent reference for API calls.
    
    Call this from the web server when the agent is initialized.
    """
    global _current_agent
    _current_agent = agent


def register_router_endpoints(app):
    """Register Tool Router API endpoints on a FastAPI app.
    
    Args:
        app: FastAPI application instance
        
    Usage (in web_server.py):
        from hermes_cli.web_server_tool_router import register_router_endpoints
        register_router_endpoints(app)
    """
    from fastapi import HTTPException, Query
    
    @app.get("/api/router/status")
    async def get_router_status():
        """Get current tool router status and statistics."""
        if not _current_agent:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        # Check if tool router adapter is attached
        adapter = getattr(_current_agent, '_router_adapter', None)
        if not adapter or not adapter.enabled:
            return {
                "enabled": False,
                "message": "Tool Router not enabled",
                "current_intent": "FULL",
                "current_toolsets": ["full"],
                "savings_percent": 0,
                "total_saved": 0,
                "turns_routed": 0,
                "fallback_count": 0,
                "force_full_mode": False,
                "top_tools": [],
            }
        
        # Get status from adapter
        try:
            status = adapter.get_status()
            return {
                "enabled": status.get("enabled", False),
                "current_intent": status.get("current_intent", "AUTO"),
                "current_toolsets": status.get("current_toolsets", ["full"]),
                "savings_percent": status.get("savings_percent", 0),
                "total_saved": status.get("total_saved", 0),
                "turns_routed": status.get("turns_routed", 0),
                "fallback_count": status.get("fallback_count", 0),
                "force_full_mode": status.get("force_full_mode", False),
                "top_tools": status.get("top_tools", []),
            }
        except Exception as e:
            return {
                "enabled": False,
                "error": str(e),
            }

    @app.post("/api/router/toggle")
    async def toggle_router(enabled: bool = Query(True, description="Enable or disable routing")):
        """Enable or disable the tool router.
        
        If disabling, restores the original full toolset.
        """
        if not _current_agent:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        adapter = getattr(_current_agent, '_router_adapter', None)
        
        if enabled and not adapter:
            # Try to enable it now
            try:
                from agent.tool_router_adapter import apply_tool_router_patch
                new_adapter = apply_tool_router_patch(_current_agent, enabled=True)
                _current_agent._router_adapter = new_adapter
                return {"success": True, "enabled": True, "message": "Tool Router enabled"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to enable: {e}")
        
        if not enabled and adapter:
            # Disable
            adapter.disable()
            return {"success": True, "enabled": False, "message": "Tool Router disabled"}
        
        return {"success": True, "enabled": enabled, "message": "No change needed"}

    @app.post("/api/router/reset")
    async def reset_router():
        """Reset fallbacks and statistics.
        
        Clears consecutive fallback count and exits full-toolset mode.
        """
        if not _current_agent:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        adapter = getattr(_current_agent, '_router_adapter', None)
        if adapter and adapter.router:
            adapter.router.consecutive_fallbacks = 0
            adapter.router.force_full_mode = False
            adapter.router.fallback_events = []
            adapter.router.actual_savings = {
                "total_saved_tokens": 0,
                "turns_routed": 0,
                "full_toolset_tokens": 0,
            }
            return {"success": True, "message": "Router stats reset"}
        
        return {"success": False, "message": "Router not active"}

    @app.get("/api/router/history")
    async def get_router_history():
        """Get routing decision history."""
        if not _current_agent:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        adapter = getattr(_current_agent, '_router_adapter', None)
        if not adapter or not adapter.router:
            return {"history": []}
        
        try:
            stats = adapter.router.get_detailed_stats()
            return {
                "history": stats["advanced"].get("decision_history", []),
                "fallback_events": adapter.router.fallback_events,
            }
        except:
            return {"history": []}

    return app


# ---------------------------------------------------------------------
# Standalone demo
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("🌐 WEB API INTEGRATION - Tool Router")
    print("=" * 70)
    print()
    print("📡 New API Endpoints:")
    print()
    print("   GET  /api/router/status     → Current status & stats")
    print("   POST /api/router/toggle     → Enable/disable routing")
    print("   POST /api/router/reset      → Reset stats & fallbacks")
    print("   GET  /api/router/history    → Routing decision history")
    print()
    print("🔌 Integration Steps:")
    print()
    print("   1. In web_server.py, at the top add:")
    print()
    print("      from hermes_cli.web_server_tool_router import (")
    print("          register_router_endpoints,")
    print("          set_agent_for_api,")
    print("      )")
    print()
    print("   2. After creating the FastAPI app:")
    print()
    print("      register_router_endpoints(app)")
    print()
    print("   3. After creating/initializing the agent:")
    print()
    print("      set_agent_for_api(agent)")
    print("      from agent.tool_router_adapter import apply_tool_router_patch")
    print("      agent._router_adapter = apply_tool_router_patch(agent)")
    print()
    print("🎨 Frontend Component:")
    print()
    print("   Import in StatusBar or Sidebar:")
    print()
    print("   import { ToolRouterStatus } from './components/ToolRouterStatus'")
    print()
    print("=" * 70)
    print("✅ WEB API MODULE READY!")
    print("=" * 70)
