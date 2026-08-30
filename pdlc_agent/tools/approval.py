"""Deterministic recording of human approval — the enforcement half of the
architecture/IaC approval gate (see pdlc_agent/callbacks.py for the refusal).

The LLM's job is to detect that the user approved (a judgment call); recording
that decision is deterministic and shared across the whole session, so later
tool calls (in this or another sub-agent) can be gated on it.
"""

from __future__ import annotations

from typing import Any

from google.adk.tools import ToolContext


def mark_design_approved(state: dict[str, Any], slug: str) -> dict[str, Any]:
    """Pure logic: record that `slug`'s design has been approved."""
    state.setdefault("approved_designs", {})[slug] = True
    return {"slug": slug, "approved": True}


def record_human_approval(slug: str, tool_context: ToolContext) -> dict[str, Any]:
    """Call this once the user has explicitly approved a design, before
    persisting it or scaffolding its infra — those calls are refused otherwise.

    Args:
        slug: the same short kebab-case identifier used for the design's
            persisted artifacts (e.g. 'stock-tracker').
    """
    return mark_design_approved(tool_context.state, slug)
