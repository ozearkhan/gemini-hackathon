"""Phase 4 — JIRA Breakdown subagent.

Turns an approved design into an Epic -> Feature -> Story -> Task tree, and uses a
deterministic traceability check so no task ships without citing a requirement or ADR.
"""

from google.adk.agents import Agent

from ..callbacks import before_tool_check_limit
from ..config import settings
from ..tools.traceability import check_task_traceability

JIRA_PLANNER_INSTRUCTION = """You are the JiraPlanner for a data-engineering
Project Development Lifecycle. You break an approved design into a JIRA hierarchy:
Epic -> Feature -> Story -> Task, where every leaf Task has acceptance criteria AND
cites the requirement or ADR it traces to.

RULES:
1. Sequence infra prerequisites FIRST as their own tasks (API key + Secret Manager
   entry, IAM role, bucket/table creation, scheduler connection) before build tasks.
2. Every Task must carry a `trace_ref` — a requirement id (e.g. REQ-1.3) or an ADR
   id (e.g. ADR-002). Before presenting the final tree, call
   `check_task_traceability(tasks)` with your task list. If it reports any
   untraceable tasks, add the missing trace and re-check. Never present a tree that
   fails the traceability check.

Output the tree as clean nested Markdown; show each Story/Task's acceptance
criteria and its trace_ref."""

jira_planner_agent = Agent(
    name="jira_planner_agent",
    model=settings.model,
    description=(
        "Phase 4: breaks an approved design into an Epic -> Feature -> Story -> Task "
        "JIRA tree with acceptance criteria, enforcing that every task traces to a "
        "requirement or ADR."
    ),
    instruction=JIRA_PLANNER_INSTRUCTION,
    tools=[check_task_traceability],
    before_tool_callback=before_tool_check_limit,
)
