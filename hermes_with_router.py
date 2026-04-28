#!/usr/bin/env python3
"""
Hermes with Tool Router - Wrapper Script

Usage:
    python hermes_with_router.py [normal hermes args]
    python hermes_with_router.py --disable-tool-router
"""

import sys
import os

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load config
from agent.tool_router_cli import ToolRouterConfig
cfg = ToolRouterConfig()

# Import the real main
from run_agent import main as real_main

# Wrap agent creation
_original_init = None

def patched_main():
    # Store original AIAgent
    from run_agent import AIAgent
    original_init = AIAgent.__init__
    
    def wrapped_init(self, *args, **kwargs):
        # Call original init first
        original_init(self, *args, **kwargs)
        
        # Apply router patch if enabled
        if cfg.enabled:
            from agent.tool_router_adapter import apply_tool_router_patch
            self._router_adapter = apply_tool_router_patch(self)
    
    AIAgent.__init__ = wrapped_init
    
    # Run main
    return real_main()

if __name__ == "__main__":
    sys.exit(patched_main())
