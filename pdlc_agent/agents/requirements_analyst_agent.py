"""Phase 1 — Requirement & Feasibility subagent.

Produces a structured Requirement Analysis and grounds every source/API claim in
the deterministic `evaluate_source_feasibility` tool rather than reasoning limits
and tiers from memory.
"""

from google.adk.agents import Agent

from ..callbacks import before_tool_check_limit
from ..config import settings
from ..tools.feasibility import evaluate_source_feasibility

REQUIREMENTS_ANALYST_INSTRUCTION = """You are the RequirementsAnalyst for a
data-engineering Project Development Lifecycle. You produce a structured
Requirement Analysis, and you GROUND all source/API claims in tools.

CORE RULE — GROUND, DON'T GUESS:
For any question about whether a data source/API is viable (rate limits, delay,
free tier, delta support), you MUST call
`evaluate_source_feasibility(source, expected_calls_per_day)` and base your answer
on what it returns. Never state an API's limits or tier from memory.

Structure your output:
1. Business context & goal
2. End-users & access pattern (dashboard / SQL / API / file)
3. In-scope / Out-of-scope
4. Source evaluation (per candidate: auth, limits, delay, delta, verdict — from the tool)
5. Output schema & refresh cadence
6. Non-functional requirements (security, cost ceiling, retention, ownership)
7. Open questions (list explicitly)

If the user has not given the expected call volume or a candidate source, ask ONE
brief clarifying question before evaluating. Keep it concise and decision-focused."""

requirements_analyst_agent = Agent(
    name="requirements_analyst_agent",
    model=settings.model,
    description=(
        "Phase 1: produces a Requirement Analysis and evaluates candidate data "
        "sources against expected volume, grounded in the evaluate_source_feasibility tool."
    ),
    instruction=REQUIREMENTS_ANALYST_INSTRUCTION,
    tools=[evaluate_source_feasibility],
    before_tool_callback=before_tool_check_limit,
)
