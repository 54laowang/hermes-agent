#!/usr/bin/env python3
"""
Tool Router - Intelligent Toolset Selection for Hermes Agent

Analyzes user intent and selects the minimal necessary toolset,
significantly reducing token usage and improving reasoning accuracy.

Intent Categories (10):
- CODE: Coding, debugging, file manipulation
- RESEARCH: Web search, information gathering
- CREATIVE: Writing, image generation, creative tasks
- DEVOPS: Terminal, processes, system administration
- PLANNING: Todo, task breakdown, project management
- ANALYSIS: Data analysis, code review, document processing
- AUTOMATION: Cronjobs, scripting, workflow automation
- MEMORY: Recall, knowledge management, session search
- COMMUNICATION: Send messages, notifications
- GENERAL: Simple questions, no tools needed

Usage:
    from agent.tool_router import ToolRouter
    
    router = ToolRouter(model="ark:gemini-2-flash")  # Lightweight model
    intent, toolsets = router.analyze_intent(user_message)
    enabled_toolsets = router.get_tools_for_intent(intent)
"""

import os
import json
from typing import Tuple, List, Dict, Optional
from pathlib import Path

# Try to import OpenAI client - will be used for intent classification
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# Intent definitions
INTENT_DEFINITIONS = {
    "CODE": {
        "description": "Coding, debugging, file manipulation, development",
        "keywords": ["code", "debug", "fix", "write", "function", "class", "script",
                    "python", "javascript", "file", "edit", "refactor", "test"],
        "toolsets": ["files", "terminal", "execute_code", "vision"],
    },
    "RESEARCH": {
        "description": "Web search, information gathering, research",
        "keywords": ["search", "find", "research", "web", "article", "news",
                    "latest", "information", "what is", "how to", "learn"],
        "toolsets": ["web", "browser", "files"],
    },
    "CREATIVE": {
        "description": "Writing, image generation, creative tasks",
        "keywords": ["write", "create", "generate", "image", "story", "design",
                    "art", "creative", "draft", "compose"],
        "toolsets": ["image_gen", "vision", "files"],
    },
    "DEVOPS": {
        "description": "Terminal, processes, system administration",
        "keywords": ["terminal", "command", "install", "server", "deploy",
                    "process", "docker", "system", "admin", "shell"],
        "toolsets": ["terminal", "files", "process", "execute_code"],
    },
    "PLANNING": {
        "description": "Todo, task breakdown, project management",
        "keywords": ["plan", "todo", "task", "project", "breakdown",
                    "organize", "schedule", "manage", "steps"],
        "toolsets": ["todo", "memory", "files"],
    },
    "ANALYSIS": {
        "description": "Data analysis, code review, document processing",
        "keywords": ["analyze", "review", "data", "process", "summarize",
                    "extract", "parse", "understand", "explain"],
        "toolsets": ["files", "execute_code", "vision", "web"],
    },
    "AUTOMATION": {
        "description": "Cronjobs, scripting, workflow automation",
        "keywords": ["automate", "cron", "schedule", "trigger", "workflow",
                    "script", "batch", "loop", "repeat", "daily", "hourly", "backup"],
        "toolsets": ["cronjob", "execute_code", "terminal", "files"],
    },
    "MEMORY": {
        "description": "Recall, knowledge management, session search",
        "keywords": ["remember", "recall", "memory", "past", "history",
                    "search session", "what did we", "earlier"],
        "toolsets": ["memory", "session_search"],
    },
    "COMMUNICATION": {
        "description": "Send messages, notifications",
        "keywords": ["send", "message", "notify", "tell", "contact",
                    "telegram", "discord", "wechat", "email"],
        "toolsets": ["send_message", "messaging"],
    },
    "GENERAL": {
        "description": "Simple questions, no tools needed",
        "keywords": ["what", "how", "why", "when", "who", "explain",
                    "help", "hello", "hi", "thanks"],
        "toolsets": ["clarify"],  # Minimal tools
    },
}


class ToolRouter:
    """Intelligent toolset router based on user intent."""
    
    def __init__(self, model: str = "ark:gemini-2-flash", enabled: bool = True):
        self.model = model
        self.enabled = enabled
        self.current_intent: Optional[str] = None
        self.current_toolsets: List[str] = []
        self.history: List[Dict] = []  # Track intent changes
        self.token_savings = {
            "estimated_full": 0,  # Tokens if using full toolset
            "estimated_used": 0,  # Tokens actually used with routing
        }
        
        # Approximate token counts per tool (for savings estimation)
        self.tool_token_estimate = {
            "terminal": 200, "process": 150,
            "web_search": 180, "web_extract": 150,
            "browser_navigate": 250, "browser_click": 120, "browser_type": 120,
            "browser_scroll": 100, "browser_back": 80, "browser_press": 100,
            "browser_get_images": 100, "browser_vision": 150, "browser_console": 120,
            "browser_cdp": 200, "browser_dialog": 100,
            "read_file": 150, "write_file": 150, "patch": 200, "search_files": 150,
            "vision_analyze": 200, "image_generate": 180,
            "skills_list": 100, "skill_view": 120, "skill_manage": 150,
            "text_to_speech": 120,
            "todo": 150, "memory": 150, "session_search": 180,
            "clarify": 150,
            "execute_code": 250, "delegate_task": 300,
            "cronjob": 200,
            "send_message": 180,
            "ha_list_entities": 150, "ha_get_state": 150,
            "ha_list_services": 150, "ha_call_service": 180,
        }
        
        # Load config for API access
        self._init_client()
    
    def _init_client(self):
        """Initialize LLM client for intent classification."""
        if not OpenAI:
            self.client = None
            return
        
        # Try to get API key from config or env
        try:
            import yaml
            config_path = Path.home() / ".hermes" / "config.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Try ark provider first
                if 'providers' in config and 'ark' in config['providers']:
                    api_key = config['providers']['ark'].get('api_key')
                    base_url = config['providers']['ark'].get('base_url')
                    if api_key:
                        self.client = OpenAI(api_key=api_key, base_url=base_url)
                        return
        except Exception:
            pass
        
        # Fallback: use env vars
        self.client = None
    
    def classify_by_keywords(self, message: str) -> Tuple[str, int]:
        """Fast classification using keyword matching."""
        message_lower = message.lower()
        best_intent = "GENERAL"
        best_score = 0
        
        for intent, data in INTENT_DEFINITIONS.items():
            score = sum(1 for kw in data["keywords"] if kw in message_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent, best_score
    
    def classify_by_llm(self, message: str) -> str:
        """Use lightweight LLM for accurate intent classification."""
        if not self.client:
            return self.classify_by_keywords(message)[0]
        
        intent_list = "\n".join([f"- {k}: {v['description']}" for k, v in INTENT_DEFINITIONS.items()])
        
        prompt = f"""Analyze the user message and classify it into ONE of these intent categories:

{intent_list}

User message: {message[:500]}

Return ONLY the category name in JSON format: {{"intent": "CATEGORY"}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=50,
            )
            result = response.choices[0].message.content.strip()
            
            # Extract intent from response
            for intent in INTENT_DEFINITIONS.keys():
                if intent in result:
                    return intent
            
            return "GENERAL"
        except Exception:
            return self.classify_by_keywords(message)[0]
    
    def analyze_intent(self, message: str, use_llm: bool = True) -> Tuple[str, List[str]]:
        """Analyze user message intent and return recommended toolsets."""
        if not self.enabled:
            return "FULL", ["full"]
        
        # Use LLM for accurate classification, fallback to keywords
        if use_llm and self.client:
            intent = self.classify_by_llm(message)
        else:
            intent, _ = self.classify_by_keywords(message)
        
        toolsets = INTENT_DEFINITIONS[intent]["toolsets"]
        
        # Always add essential tools
        essential = ["clarify", "memory"]
        for t in essential:
            if t not in toolsets:
                toolsets.append(t)
        
        self.current_intent = intent
        self.current_toolsets = toolsets
        
        # Record history
        self.history.append({
            "message": message[:100],
            "intent": intent,
            "toolsets": toolsets,
        })
        
        return intent, toolsets
    
    def get_tools_for_intent(self, intent: str) -> List[str]:
        """Get recommended toolsets for a given intent."""
        if intent not in INTENT_DEFINITIONS:
            intent = "GENERAL"
        return INTENT_DEFINITIONS[intent]["toolsets"]
    
    def should_switch_intent(self, new_message: str, threshold: int = 3) -> bool:
        """Detect if intent has changed significantly enough to switch toolsets."""
        new_intent, score = self.classify_by_keywords(new_message)
        
        # If confident score is above threshold and different from current
        if self.current_intent and new_intent != self.current_intent and score >= threshold:
            return True
        return False
    
    def estimate_savings(self) -> Dict[str, int]:
        """Estimate token savings from tool routing."""
        # Estimate full toolset token count (~60 tools)
        full_toolset_tokens = sum(self.tool_token_estimate.values())
        
        # Estimate current toolset token count
        current_tokens = sum(
            self.tool_token_estimate.get(t, 150)
            for ts in self.current_toolsets
            for t in self._get_tools_for_toolset(ts)
        )
        
        return {
            "full_toolset_tokens": full_toolset_tokens,
            "routed_toolset_tokens": current_tokens,
            "savings_tokens": full_toolset_tokens - current_tokens,
            "savings_percent": round((1 - current_tokens / full_toolset_tokens) * 100, 1)
            if full_toolset_tokens > 0 else 0,
        }
    
    def _get_tools_for_toolset(self, toolset_name: str) -> List[str]:
        """Get individual tools for a toolset name (simplified)."""
        # Map toolset names to individual tools
        if toolset_name == "full":
            return list(self.tool_token_estimate.keys())  # All tools
        
        toolset_map = {
            "files": ["read_file", "write_file", "patch", "search_files"],
            "terminal": ["terminal", "process"],
            "execute_code": ["execute_code"],
            "vision": ["vision_analyze"],
            "web": ["web_search", "web_extract"],
            "browser": ["browser_navigate", "browser_click", "browser_type",
                       "browser_scroll", "browser_back"],
            "image_gen": ["image_generate"],
            "todo": ["todo"],
            "memory": ["memory"],
            "session_search": ["session_search"],
            "clarify": ["clarify"],
            "cronjob": ["cronjob"],
            "send_message": ["send_message"],
            "messaging": ["send_message"],
            "process": ["process"],
            "delegate_task": ["delegate_task"],
            "skills": ["skills_list", "skill_view", "skill_manage"],
        }
        return toolset_map.get(toolset_name, [])
    
    def get_stats(self) -> Dict:
        """Get router statistics."""
        return {
            "current_intent": self.current_intent,
            "current_toolsets": self.current_toolsets,
            "history_count": len(self.history),
            "estimated_savings": self.estimate_savings(),
        }


# Global singleton instance
_tool_router: Optional[ToolRouter] = None


def get_tool_router() -> ToolRouter:
    """Get the global tool router instance."""
    global _tool_router
    if _tool_router is None:
        _tool_router = ToolRouter()
    return _tool_router


def enable_tool_router():
    """Enable intelligent tool routing."""
    router = get_tool_router()
    router.enabled = True


def disable_tool_router():
    """Disable intelligent tool routing (use full toolset)."""
    router = get_tool_router()
    router.enabled = False
