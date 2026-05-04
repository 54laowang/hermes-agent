#!/usr/bin/env python3
"""
Tool Router - Intelligent Toolset Selection

Analyzes user intent and selects minimal necessary toolset,
reducing token usage by 50-80% while improving reasoning accuracy.
"""

from typing import Tuple, List, Dict, Optional

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
        "toolsets": ["clarify"],
    },
}

# Approximate token counts per tool for savings estimation
TOOL_TOKEN_ESTIMATE = {
    "terminal": 200, "process": 150,
    "web_search": 180, "web_extract": 150,
    "browser_navigate": 250, "browser_click": 120, "browser_type": 120,
    "browser_scroll": 100, "browser_back": 80, "browser_press": 100,
    "browser_get_images": 100, "browser_vision": 150, "browser_console": 120,
    "browser_cdp": 200, "browser_dialog": 100,
    "read_file": 150, "write_file": 150, "patch": 200, "search_files": 150,
    "vision_analyze": 200, "image_generate": 180,
    "todo": 150, "memory": 150, "session_search": 180,
    "clarify": 150, "execute_code": 250, "delegate_task": 300,
    "cronjob": 200, "send_message": 180,
}

# Toolset name to individual tools mapping
TOOLSET_TOOLS = {
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
    "full": list(TOOL_TOKEN_ESTIMATE.keys()),
}


class ToolRouter:
    """Intelligent toolset router based on user intent."""
    
    def __init__(self, model: str = "ark:gemini-2-flash", enabled: bool = True):
        self.model = model
        self.enabled = enabled
        self.current_intent: Optional[str] = None
        self.current_toolsets: List[str] = []
        self.history: List[Dict] = []
        self.client = None  # Initialize with your LLM client
    
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
        
        intent_list = "\n".join([f"- {k}: {v['description']}" 
                                for k, v in INTENT_DEFINITIONS.items()])
        
        prompt = f"""Classify this message into ONE category:\n{intent_list}\n
        Message: {message[:500]}\nReturn only the category name."""
        
        # Call your LLM here
        # response = self.client.chat(...)
        
        return self.classify_by_keywords(message)[0]  # Fallback
    
    def analyze_intent(self, message: str, use_llm: bool = True) -> Tuple[str, List[str]]:
        """Analyze user message intent and return recommended toolsets."""
        if not self.enabled:
            return "FULL", ["full"]
        
        if use_llm and self.client:
            intent = self.classify_by_llm(message)
        else:
            intent, _ = self.classify_by_keywords(message)
        
        toolsets = INTENT_DEFINITIONS[intent]["toolsets"]
        
        # Always add essential tools
        for essential in ["clarify", "memory"]:
            if essential not in toolsets:
                toolsets.append(essential)
        
        self.current_intent = intent
        self.current_toolsets = toolsets
        
        return intent, toolsets
    
    def get_tools_for_intent(self, intent: str) -> List[str]:
        """Get recommended toolsets for a given intent."""
        if intent not in INTENT_DEFINITIONS:
            intent = "GENERAL"
        return INTENT_DEFINITIONS[intent]["toolsets"]
    
    def should_switch_intent(self, new_message: str, threshold: int = 3) -> bool:
        """Detect if intent has changed significantly."""
        new_intent, score = self.classify_by_keywords(new_message)
        if self.current_intent and new_intent != self.current_intent and score >= threshold:
            return True
        return False
    
    def estimate_savings(self) -> Dict[str, int]:
        """Estimate token savings from tool routing."""
        full_tokens = sum(TOOL_TOKEN_ESTIMATE.values())
        current_tokens = sum(
            TOOL_TOKEN_ESTIMATE.get(t, 150)
            for ts in self.current_toolsets
            for t in TOOLSET_TOOLS.get(ts, [])
        )
        
        return {
            "full_toolset_tokens": full_tokens,
            "routed_toolset_tokens": current_tokens,
            "savings_tokens": full_tokens - current_tokens,
            "savings_percent": round((1 - current_tokens / full_tokens) * 100, 1)
            if full_tokens > 0 else 0,
        }
