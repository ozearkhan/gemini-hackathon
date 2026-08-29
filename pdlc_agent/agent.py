"""Data Engineering PDLC Assistant — root coordinator.

Adopts the Coordinator-Dispatcher pattern: a lightweight root agent that routes
each request to the phase-specialist subagent that owns it. Each subagent has a
narrow scope and a limited tool set (limited-scope agents score better and
hallucinate less than one monolithic agent).

The root_agent variable is the ADK entry point — it MUST be named 'root_agent'.
"""

from google.adk.agents import Agent

from .agents.architecture_agent import architecture_agent
from .agents.intake_triage_agent import intake_triage_agent
from .agents.requirements_analyst_agent import requirements_analyst_agent
from .config import settings

COORDINATOR_INSTRUCTION = """You are the coordinator for a Data Engineering
Project Development Lifecycle (PDLC) assistant. You turn a data request (e.g.
"build a daily competitor stock tracker") into concrete lifecycle artifacts by
delegating to the right phase specialist.

DELEGATION RULES (delegate to exactly ONE specialist for a single-topic request):
- Phase 0 — a NEW/incoming request that needs triaging (net-new? size? urgency?):
  delegate to `intake_triage_agent`.
- Phase 1 — requirements, scope, or whether a data source/API is viable
  (rate limits, delay, free tier, delta support): delegate to
  `requirements_analyst_agent`.
- Phase 2 — High-Level Design, ADRs, or how to LOAD/STORE a source (full vs
  incremental vs append, Parquet vs Delta): delegate to `architecture_agent`.

Only fan out to multiple specialists if the user explicitly asks for a full,
multi-phase workup.

RESPONSE STYLE:
- Lead with a one-sentence direct answer, then the specialist's structured output.
- Never invent triage, requirement, or architecture facts yourself — that is the
  specialist's job, and specialists ground their answers in deterministic tools."""

root_agent = Agent(
    name="pdlc_coordinator",
    model=settings.fast_model,
    description=(
        "Coordinator for a Data Engineering PDLC assistant. Routes requests to "
        "phase-specialist subagents that each produce one lifecycle artifact."
    ),
    instruction=COORDINATOR_INSTRUCTION,
    sub_agents=[intake_triage_agent, requirements_analyst_agent, architecture_agent],
)

