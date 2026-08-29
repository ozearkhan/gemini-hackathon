"""Data Engineering PDLC Assistant — root coordinator.

Adopts the Coordinator-Dispatcher pattern: a lightweight root agent that routes
each request to the phase-specialist subagent that owns it. Each subagent has a
narrow scope and a limited tool set (limited-scope agents score better and
hallucinate less than one monolithic agent).

The root_agent variable is the ADK entry point — it MUST be named 'root_agent'.
"""

from google.adk.agents import Agent

from .agents.architecture_agent import architecture_agent
from .config import settings

COORDINATOR_INSTRUCTION = """You are the coordinator for a Data Engineering
Project Development Lifecycle (PDLC) assistant. You turn a data request (e.g.
"build a daily competitor stock tracker") into concrete lifecycle artifacts by
delegating to the right phase specialist.

DELEGATION RULES:
- For questions about High-Level Design, architecture, Architecture Decision
  Records, or how to LOAD/STORE a data source (full vs incremental vs append,
  Parquet vs Delta), delegate to `architecture_agent`.
- Delegate to exactly ONE specialist for a single-topic request. Do not fan out
  to multiple specialists unless the user explicitly asks for a full,
  multi-phase workup.

RESPONSE STYLE:
- Lead with a one-sentence direct answer, then the specialist's structured output.
- Never invent architecture facts yourself — that is the specialist's job, and
  the specialist grounds its answers in deterministic tools."""

root_agent = Agent(
    name="pdlc_coordinator",
    model=settings.fast_model,
    description=(
        "Coordinator for a Data Engineering PDLC assistant. Routes requests to "
        "phase-specialist subagents that each produce one lifecycle artifact."
    ),
    instruction=COORDINATOR_INSTRUCTION,
    sub_agents=[architecture_agent],
)

