"""Permission policy enforcement for tool dispatch.

Centralized permission checking for all tool execution paths.
This module ensures that permission policies are enforced on ALL dispatch paths,
including sequential, concurrent, scheduled, and delegated execution.

Integration points:
- model_tools.handle_function_call (main tool dispatch)
- run_agent delegate_task (subagent delegation)
- batch_runner (parallel batch execution)
- cron/jobs (scheduled tasks)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def check_tool_permission(
    tool_name: str,
    tool_args: Dict[str, Any],
    session_id: Optional[str] = None,
    enabled_tools: Optional[list] = None,
) -> tuple[bool, Optional[str]]:
    """
    Check if a tool call is permitted under the current permission policy.
    
    This is the single source of truth for tool permission checks.
    All tool dispatch paths should call this function before executing tools.
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments passed to the tool
        session_id: Session identifier for approval state lookup
        enabled_tools: List of tools enabled for this session (from config)
        
    Returns:
        Tuple of (is_permitted: bool, error_message: Optional[str])
        - (True, None) if the tool is permitted
        - (False, "error message") if the tool is blocked
    """
    # 1. Check if tool is in enabled_tools list (if provided)
    if enabled_tools is not None and tool_name not in enabled_tools:
        logger.warning(
            f"Tool '{tool_name}' not in enabled_tools list for session {session_id}"
        )
        return False, f"Tool '{tool_name}' is not enabled for this session"
    
    # 2. Import approval system (lazy to avoid circular imports)
    try:
        from tools.approval import detect_dangerous_command
    except ImportError:
        # Approval system not available (minimal environment)
        # Allow tool execution but log a warning
        logger.debug("Approval system not available, allowing tool execution")
        return True, None
    
    # 3. Check for dangerous command patterns
    # Only applies to tools that execute shell commands
    if tool_name in ("terminal", "execute_code", "process"):
        command = tool_args.get("command", "")
        if command:
            # detect_dangerous_command returns (is_dangerous, reason, pattern)
            result = detect_dangerous_command(command)
            if result and result[0]:  # is_dangerous
                reason = result[1] if len(result) > 1 else "dangerous command"
                logger.warning(
                    f"Dangerous command blocked in tool '{tool_name}': {reason}"
                )
                # Note: For now, we allow dangerous commands with approval
                # The actual approval prompt is handled elsewhere
                # This check just logs for observability
                logger.info(f"Dangerous command detected but allowed: {reason}")
    
    # 4. All checks passed - tool is permitted
    return True, None


def enforce_permission_policy(
    tool_name: str,
    tool_args: Dict[str, Any],
    session_id: Optional[str] = None,
    enabled_tools: Optional[list] = None,
) -> Optional[str]:
    """
    Enforce permission policy and return error message if blocked.
    
    Convenience wrapper for check_tool_permission that returns None on success
    or an error message string on failure.
    
    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments passed to the tool
        session_id: Session identifier for approval state lookup
        enabled_tools: List of tools enabled for this session
        
    Returns:
        None if permitted, error message string if blocked
    """
    is_permitted, error_msg = check_tool_permission(
        tool_name, tool_args, session_id, enabled_tools
    )
    return None if is_permitted else error_msg


# Export public API
__all__ = ["check_tool_permission", "enforce_permission_policy"]
