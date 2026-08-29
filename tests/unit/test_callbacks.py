"""Unit tests for the tool-call limit guardrail (pure logic, no ADK runtime)."""

import pytest

from pdlc_agent.callbacks import ToolCallLimitError, enforce_tool_call_limit


def test_counter_increments_across_calls():
    state: dict = {}
    assert enforce_tool_call_limit(state, max_calls=3) == 1
    assert enforce_tool_call_limit(state, max_calls=3) == 2
    assert state["_turn_tool_call_count"] == 2


def test_raises_once_limit_exceeded():
    state: dict = {}
    for _ in range(3):
        enforce_tool_call_limit(state, max_calls=3)
    with pytest.raises(ToolCallLimitError):
        enforce_tool_call_limit(state, max_calls=3)
