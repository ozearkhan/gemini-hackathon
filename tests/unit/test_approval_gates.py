"""Structural enforcement tests — proving the approval/grounding gates actually
REFUSE without recorded state, not just that the happy path works. Tests the
callback's pure Python logic; agent behavior itself belongs in eval, not here.
"""

import pytest

from pdlc_agent.callbacks import (
    ApprovalRequiredError,
    GroundingRequiredError,
    before_tool_check_limit_and_gates,
    enforce_design_approved,
    enforce_research_grounded,
)
from pdlc_agent.tools.approval import mark_design_approved, record_human_approval


class _FakeTool:
    def __init__(self, name: str):
        self.name = name


class _FakeToolContext:
    def __init__(self, state: dict | None = None):
        self.state = state if state is not None else {}


# ── Approval gate: pure logic ────────────────────────────────────────────────


def test_no_approval_recorded_blocks_finalize_tool():
    state: dict = {}
    with pytest.raises(ApprovalRequiredError):
        enforce_design_approved(state, "stock-tracker", "save_architecture_doc")


def test_approval_recorded_allows_finalize_tool():
    state: dict = {}
    mark_design_approved(state, "stock-tracker")
    enforce_design_approved(state, "stock-tracker", "save_architecture_doc")  # no raise


def test_approval_is_scoped_by_slug_not_global():
    state: dict = {}
    mark_design_approved(state, "stock-tracker")
    with pytest.raises(ApprovalRequiredError):
        enforce_design_approved(state, "other-project", "save_architecture_doc")


# ── Grounding gate: pure logic ───────────────────────────────────────────────


def test_no_grounding_recorded_blocks_persist_tool():
    state: dict = {}
    with pytest.raises(GroundingRequiredError):
        enforce_research_grounded(state, "save_architecture_doc")


def test_grounding_recorded_by_any_researcher_allows_persist_tool():
    state = {"grounding_recorded": {"gcp_researcher_agent": True}}
    enforce_research_grounded(state, "save_architecture_doc")  # no raise


# ── Combined ADK-facing callback: proves the tool call is actually refused ──


def test_callback_refuses_gated_tool_with_empty_state():
    tool = _FakeTool("save_architecture_doc")
    ctx = _FakeToolContext(state={})
    with pytest.raises((ApprovalRequiredError, GroundingRequiredError)):
        before_tool_check_limit_and_gates(tool, {"slug": "stock-tracker"}, ctx)


def test_callback_refuses_iac_tool_without_approval():
    tool = _FakeTool("generate_terraform_skeleton")
    ctx = _FakeToolContext(state={})
    with pytest.raises(ApprovalRequiredError):
        before_tool_check_limit_and_gates(tool, {"slug": "stock-tracker"}, ctx)


def test_callback_allows_gated_tool_once_approved_and_grounded():
    ctx = _FakeToolContext(state={})
    record_human_approval("stock-tracker", ctx)
    ctx.state.setdefault("grounding_recorded", {})["gcp_researcher_agent"] = True
    tool = _FakeTool("save_architecture_doc")
    before_tool_check_limit_and_gates(tool, {"slug": "stock-tracker"}, ctx)  # no raise


def test_callback_ignores_ungated_tools():
    """decide_load_pattern etc. aren't finalize/persist tools — never gated."""
    tool = _FakeTool("decide_load_pattern")
    ctx = _FakeToolContext(state={})
    before_tool_check_limit_and_gates(tool, {}, ctx)  # no raise despite empty state
