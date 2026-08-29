"""Guardrail callbacks shared across agents.

Kept thin: the enforcement logic is a pure function so it can be unit-tested
without constructing ADK runtime objects, and the ADK callback is a small wrapper.
"""

from __future__ import annotations

from typing import Any

from .config import settings


class ToolCallLimitError(RuntimeError):
    """Raised when a single turn exceeds the allowed number of tool calls."""


def enforce_tool_call_limit(state: dict[str, Any], max_calls: int) -> int:
    """Increment the per-turn tool-call counter and stop runaway loops.

    Returns the new count. Raises ToolCallLimitError once the count exceeds
    max_calls.
    """
    count = state.get("_turn_tool_call_count", 0) + 1
    state["_turn_tool_call_count"] = count
    if count > max_calls:
        raise ToolCallLimitError(
            f"Defensive stop: exceeded {max_calls} tool calls in a single turn."
        )
    return count


def before_tool_check_limit(tool: Any, args: dict[str, Any], tool_context: Any) -> None:
    """ADK before_tool_callback: cap tool calls per turn."""
    enforce_tool_call_limit(tool_context.state, settings.max_tool_calls_per_turn)
