"""Reusable research sub-agent — real web-grounded research, not hardcoded facts.

Uses ADK's built-in `google_search` tool: model-internal Google Search grounding,
GCP-native (no external SaaS, no sign-off required). Per the ADK skill, this tool
cannot be mixed with custom FunctionTools in the same agent (it disables automatic
function calling), so it lives on its own dedicated sub-agent and is delegated to
by phase specialists that also need FunctionTools.

A factory (not a shared singleton) because an ADK agent instance has one parent —
each caller that wants a researcher gets its own instance.
"""

from __future__ import annotations

from google.adk.agents import Agent
from google.adk.tools import google_search

from ..config import settings

RESEARCHER_INSTRUCTION = """You are a research specialist. Given a specific
question, use Google Search grounding to find current, real information — never
answer a factual question (API capabilities, rate limits, pricing, current GCP
service limits, vendor comparisons, TOS terms) from memory alone.

Be concise and concrete:
- State the fact plainly, with the source noted.
- If sources disagree or information is uncertain, say so explicitly rather than
  picking one answer with false confidence.
- If you cannot find a reliable answer, say that clearly instead of guessing."""


def build_researcher_agent(name: str, description: str) -> Agent:
    """Build a fresh research sub-agent instance.

    Args:
        name: unique ADK agent name (must be distinct across the agent tree).
        description: shown to the delegating parent to decide when to use it.
    """
    return Agent(
        name=name,
        model=settings.reasoning_model,
        description=description,
        instruction=RESEARCHER_INSTRUCTION,
        tools=[google_search],
        disallow_transfer_to_peers=True,
        disallow_transfer_to_parent=False,
    )
