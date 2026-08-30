"""Phase 4 — JIRA Breakdown subagent.

Runs AFTER `iac_agent` has provisioned the infra (not before): since the agent
provisions real infra directly, there's no need for a human-facing "set up the
bucket/IAM/secret" ticket — the JIRA tree covers the remaining DEVELOPMENT work
that a team can actually pick up and iterate on against infra that already
exists. Uses a deterministic traceability check so no task ships without citing
a requirement or ADR.
"""

from google.adk.agents import Agent

from ..callbacks import before_tool_check_limit
from ..config import settings
from ..tools.traceability import check_task_traceability

JIRA_PLANNER_INSTRUCTION = """You are the JiraPlanner for a data-engineering
Project Development Lifecycle. You break an approved, infra-provisioned design
into a JIRA hierarchy: Epic -> Feature -> Story -> Task, where every leaf Task
has acceptance criteria AND cites the requirement or ADR it traces to.

GATE — CHECK ORDER FIRST:
This phase runs AFTER infra has been provisioned by `iac_agent`, not before. If
the user has not indicated that infra scaffolding/provisioning already happened
for this design, tell them to run that first (delegate back to `iac_agent`) and
do not produce a JIRA tree yet.

RULES:
1. Do NOT include manual infra-setup tasks (bucket/IAM/secret/scheduler
   creation) as tickets — that infra is already provisioned as code by
   `iac_agent`. If anything from the approved design still needs infra that
   `iac_agent` did NOT cover (check its "flagged for verification" note if
   given), add exactly ONE ticket for a human to close that specific gap —
   don't reintroduce full manual-provisioning tickets for what's already done.
2. Focus the tree on the DEVELOPMENT work: Ingestion, Modeling, Dashboard,
   Observability — the tasks a developer picks up and iterates on now that the
   environment exists.
3. Every Task must carry a `trace_ref` — a requirement id (e.g. REQ-1.3) or an ADR
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
        "Phase 4: breaks an approved, infra-provisioned design into an Epic -> "
        "Feature -> Story -> Task JIRA tree covering the remaining development "
        "work, with acceptance criteria, enforcing that every task traces to a "
        "requirement or ADR. Runs AFTER iac_agent, not before."
    ),
    instruction=JIRA_PLANNER_INSTRUCTION,
    tools=[check_task_traceability],
    before_tool_callback=before_tool_check_limit,
)
