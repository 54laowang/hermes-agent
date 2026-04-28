#!/usr/bin/env python3
"""
CLI Integration for Tool Router

Adds --enable-tool-router / --disable-tool-router flags
and config.yaml support.

Usage:
    hermes --enable-tool-router
    hermes --disable-tool-router
    
Config (config.yaml):
    tool_router:
        enabled: true
        model: "ark:gemini-2-flash"
        fallback_threshold: 2
        always_enabled: ["clarify", "memory"]
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ToolRouterConfig:
    """Load and manage tool router configuration from config.yaml."""
    
    DEFAULT_CONFIG = {
        "enabled": True,
        "model": "ark:gemini-2-flash",
        "fallback_threshold": 2,
        "always_enabled": ["clarify", "memory"],
        "llm_classification_enabled": False,
        "context_window": 5,
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.hermes/config.yaml")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load config from file with fallback to defaults."""
        cfg = dict(self.DEFAULT_CONFIG)
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    full_config = yaml.safe_load(f) or {}
                
                # Merge tool_router section if exists
                if "tool_router" in full_config:
                    tool_cfg = full_config["tool_router"]
                    for key in cfg:
                        if key in tool_cfg:
                            cfg[key] = tool_cfg[key]
                            
            except Exception as e:
                print(f"⚠️ Error loading tool router config: {e}")
        
        return cfg
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value."""
        return self.config.get(key, default)
    
    @property
    def enabled(self) -> bool:
        return self.config.get("enabled", True)
    
    @property
    def model(self) -> str:
        return self.config.get("model", "ark:gemini-2-flash")
    
    def apply_cli_override(self, disable: bool = False, enable: bool = False):
        """Apply CLI flag overrides."""
        if disable:
            self.config["enabled"] = False
        if enable:
            self.config["enabled"] = True


# ---------------------------------------------------------------------
# CLI Argument Parser Patch
# ---------------------------------------------------------------------

CLI_PATCH = """
# ---------------------------------------------------------------------
# TOOL ROUTER CLI OPTIONS - Add this to your argparser
# ---------------------------------------------------------------------

def add_tool_router_args(parser):
    \"\"\"Add tool router arguments to an ArgumentParser.\"\"\"
    
    group = parser.add_argument_group('Tool Router Options')
    
    group.add_argument(
        '--enable-tool-router',
        action='store_true',
        default=None,
        help='Enable intelligent tool routing (overrides config)'
    )
    
    group.add_argument(
        '--disable-tool-router',
        action='store_true',
        help='Disable intelligent tool routing (overrides config)'
    )
    
    group.add_argument(
        '--tool-router-model',
        type=str,
        default=None,
        help='Model to use for LLM-based intent classification'
    )
    
    group.add_argument(
        '--show-tool-routing',
        action='store_true',
        help='Print routing statistics at session end'
    )
    
    return group


# ---------------------------------------------------------------------
# USAGE in your main function:
# ---------------------------------------------------------------------
#
#   from agent.tool_router_cli import add_tool_router_args, ToolRouterConfig
#
#   # Add to parser
#   add_tool_router_args(parser)
#
#   # Load config + CLI overrides
#   cfg = ToolRouterConfig()
#   cfg.apply_cli_override(
#       disable=args.disable_tool_router,
#       enable=args.enable_tool_router
#   )
#
#   # After creating agent:
#   if cfg.enabled:
#       from agent.tool_router_adapter import apply_tool_router_patch
#       router = apply_tool_router_patch(agent)
#
"""


# ---------------------------------------------------------------------
# Quick-start wrapper script
# ---------------------------------------------------------------------

WRAPPER_SCRIPT = """#!/usr/bin/env python3
\"\"\"
Hermes with Tool Router - Wrapper Script

Usage:
    python hermes_with_router.py [normal hermes args]
    python hermes_with_router.py --disable-tool-router
\"\"\"

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
"""


if __name__ == "__main__":
    print("=" * 70)
    print("🎮 CLI INTEGRATION - Tool Router")
    print("=" * 70)
    print()
    
    # Test config loading
    cfg = ToolRouterConfig()
    print("📋 Current Configuration:")
    print(f"   Enabled: {cfg.enabled}")
    print(f"   Model: {cfg.model}")
    print(f"   Fallback Threshold: {cfg.get('fallback_threshold')}")
    print(f"   Always Enabled: {cfg.get('always_enabled')}")
    print()
    
    print("🎯 CLI Flags to add:")
    print("   --enable-tool-router     Force enable routing")
    print("   --disable-tool-router    Force disable routing")
    print("   --tool-router-model X    Set classification model")
    print("   --show-tool-routing      Show stats at end of session")
    print()
    
    print("📦 config.yaml section:")
    print(yaml.dump({"tool_router": ToolRouterConfig.DEFAULT_CONFIG}, 
                    default_flow_style=False, indent=2))
    
    # Create wrapper script
    wrapper_path = Path(__file__).parent.parent / "hermes_with_router.py"
    with open(wrapper_path, 'w') as f:
        f.write(WRAPPER_SCRIPT)
    
    print(f"✅ Created wrapper script: {wrapper_path}")
    print()
    print("🚀 Try it: python hermes_with_router.py 'hello'")
    print("=" * 70)
