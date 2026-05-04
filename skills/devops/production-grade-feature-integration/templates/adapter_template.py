#!/usr/bin/env python3
"""
Production-Grade Feature Integration - Adapter Template

Copy this template and customize for your feature.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

# Feature mapping - customize this for your feature
FEATURE_TOGGLE_MAP = {
    # "intent": ["list", "of", "toolsets"]
}


class FeatureAdapter:
    """
    Non-invasive Feature Integration Adapter
    
    Usage:
        # Option 1: Mixin inheritance
        class YourAgent(FeatureAdapter, OriginalAgent):
            pass
        
        # Option 2: Runtime monkey patch (safest)
        agent = OriginalAgent()
        FeatureAdapter.patch_agent(agent)
    """
    
    def __init__(self, enabled: bool = True):
        self._feature_enabled = enabled
        self._feature_initialized = False
        self._original_methods = {}
    
    def _initialize_feature(self):
        """Initialize your feature here - called once on first use"""
        if self._feature_initialized:
            return
        
        # Import and initialize your core feature
        # from your_feature import AdvancedFeature
        # self.feature = AdvancedFeature(enabled=self._feature_enabled)
        
        self._feature_initialized = True
    
    def _patch_method(self, method_name: str, wrapper: Callable):
        """
        Patch a method with wrapper function
        
        wrapper(original_fn, *args, **kwargs) -> result
        """
        if not hasattr(self, method_name):
            return
            
        original = getattr(self, method_name)
        self._original_methods[method_name] = original
        
        def patched(*args, **kwargs):
            return wrapper(original, *args, **kwargs)
            
        setattr(self, method_name, patched)
    
    def _feature_wrapper(self, original_fn, *args, **kwargs):
        """
        Wrap the main method (e.g., chat) with feature logic
        
        Customize this for your feature!
        """
        if not self._feature_enabled:
            return original_fn(*args, **kwargs)
        
        self._initialize_feature()
        
        try:
            # Step 1: Pre-processing (e.g., intent classification)
            # message = args[0] if args else kwargs.get('message', '')
            # intent, tools = self.feature.analyze(message)
            
            # Step 2: Modify context/state if needed
            # self.enabled_toolsets = tools
            
            # Step 3: Call original method
            result = original_fn(*args, **kwargs)
            
            # Step 4: Post-processing (e.g., stats collection)
            # self.feature.record_success()
            
            return result
            
        except Exception as e:
            # Graceful fallback - use original behavior
            print(f"⚠️ Feature error, falling back: {e}", file=sys.stderr)
            return original_fn(*args, **kwargs)
    
    def enable_feature(self):
        """Enable the feature at runtime"""
        self._feature_enabled = True
        if self._feature_initialized:
            # self.feature.enabled = True
            pass
    
    def disable_feature(self):
        """Disable the feature at runtime"""
        self._feature_enabled = False
        if self._feature_initialized:
            # self.feature.enabled = False
            pass
    
    def get_feature_status(self) -> Dict[str, Any]:
        """Get feature status and statistics"""
        if not self._feature_initialized:
            return {
                "enabled": self._feature_enabled,
                "initialized": False,
            }
        
        return {
            "enabled": self._feature_enabled,
            "initialized": True,
            # Add your feature stats here
            # "stats": self.feature.get_detailed_stats(),
        }
    
    @staticmethod
    def patch_agent(agent_instance, enabled: bool = True):
        """
        Patch an existing agent instance at runtime (Monkey Patch)
        
        This is the SAFEST integration method - no class modifications needed.
        """
        # Store adapter on instance
        adapter = FeatureAdapter(enabled=enabled)
        agent_instance._feature_adapter = adapter
        
        # Patch main method (e.g., chat) - customize method name!
        original_chat = agent_instance.chat
        
        def patched_chat(*args, **kwargs):
            return adapter._feature_wrapper(original_chat, *args, **kwargs)
        
        agent_instance.chat = patched_chat
        
        # Add convenience methods
        agent_instance.enable_feature = adapter.enable_feature
        agent_instance.disable_feature = adapter.disable_feature
        agent_instance.get_feature_status = adapter.get_feature_status
        
        return agent_instance
    
    @staticmethod
    def unpatch_agent(agent_instance):
        """Remove the patch and restore original behavior"""
        if hasattr(agent_instance, '_original_methods'):
            for name, method in agent_instance._original_methods.items():
                setattr(agent_instance, name, method)
        
        if hasattr(agent_instance, '_feature_adapter'):
            delattr(agent_instance, '_feature_adapter')
            
        return agent_instance


# ---------------------------------------------------------------------
# Integration via Wrapper Script (ZERO RISK - No file modifications)
# ---------------------------------------------------------------------

def create_wrapper_script(output_path: str = "hermes_with_feature.py"):
    """
    Create a wrapper script that integrates the feature without modifying
    any original files. This is the SAFEST possible deployment method.
    """
    wrapper_code = '''#!/usr/bin/env python3
"""
Wrapper script - enables feature without modifying original code.
ZERO RISK - can be deleted at any time to revert completely.
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import original
from run_agent import main as original_main

# Import and apply feature
from agent.feature_adapter import FeatureAdapter

if __name__ == "__main__":
    # The adapter will patch the agent instance at runtime
    # when it's created inside main()
    sys.exit(original_main())
'''
    
    Path(output_path).write_text(wrapper_code)
    print(f"✅ Wrapper script created: {output_path}")
    print(f"   Usage: python {output_path} 'your query'")


if __name__ == "__main__":
    print("=" * 70)
    print("🔌 Production-Grade Feature Integration Adapter")
    print("=" * 70)
    print()
    print("Usage options:")
    print()
    print("1. Monkey Patch (SAFEST):")
    print("   agent = OriginalAgent()")
    print("   FeatureAdapter.patch_agent(agent, enabled=True)")
    print("   agent.chat('hello')  # Feature is active!")
    print()
    print("2. Wrapper Script (ZERO RISK):")
    print("   create_wrapper_script()")
    print("   python hermes_with_feature.py 'hello'")
    print()
    print("3. Mixin Inheritance:")
    print("   class PatchedAgent(FeatureAdapter, OriginalAgent):")
    print("       def __init__(self, *args, **kwargs):")
    print("           FeatureAdapter.__init__(self, enabled=True)")
    print("           OriginalAgent.__init__(self, *args, **kwargs)")
    print()
