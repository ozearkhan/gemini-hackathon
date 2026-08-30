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


class ApprovalRequiredError(RuntimeError):
    """Raised when a tool call would finalize/persist a design without a
    recorded human approval for it. Structural refusal, not an instruction."""


class GroundingRequiredError(RuntimeError):
    """Raised when a tool call would persist a claim without any researcher
    sub-agent having actually been consulted this session."""


# Tools that finalize/persist a design — refused without a recorded approval.
_REQUIRES_APPROVAL = {"save_architecture_doc", "generate_terraform_skeleton"}

# Tools that persist claims sourced from a researcher sub-agent — refused
# without evidence that a researcher (requirements_researcher_agent or
# gcp_researcher_agent) was actually consulted this session.
_REQUIRES_GROUNDING = {"save_architecture_doc", "save_requirement_doc"}


def enforce_design_approved(state: dict[str, Any], slug: str, tool_name: str) -> None:
    """Pure logic: raise unless `slug` has a recorded human approval."""
    if not state.get("approved_designs", {}).get(slug):
        raise ApprovalRequiredError(
            f"Refused: '{tool_name}' requires a recorded human approval for "
            f"design '{slug}' first (call record_human_approval once the user "
            f"approves). No approval recorded means the call is refused, not "
            f"just discouraged."
        )


def enforce_research_grounded(state: dict[str, Any], tool_name: str) -> None:
    """Pure logic: raise unless at least one researcher sub-agent ran this
    session (mirrors the intent of architecture.md §3's doc-gate design)."""
    if not any(state.get("grounding_recorded", {}).values()):
        raise GroundingRequiredError(
            f"Refused: '{tool_name}' persists claims that must be grounded in "
            f"live research (requirements_researcher_agent or "
            f"gcp_researcher_agent) before this call is allowed."
        )


def before_tool_check_limit_and_gates(tool: Any, args: dict[str, Any], tool_context: Any) -> None:
    """ADK before_tool_callback: tool-call ceiling + approval + grounding gates.

    Structural enforcement, not instruction text — a gated tool call is
    physically refused (raises) if the required state was never recorded.
    """
    enforce_tool_call_limit(tool_context.state, settings.max_tool_calls_per_turn)
    name = getattr(tool, "name", "")
    if name in _REQUIRES_APPROVAL:
        enforce_design_approved(tool_context.state, str(args.get("slug", "")), name)
    if name in _REQUIRES_GROUNDING:
        enforce_research_grounded(tool_context.state, name)
