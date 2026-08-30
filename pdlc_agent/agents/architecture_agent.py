"""Phase 2 — Architecture / HLD subagent.

Acts like a GCP data-engineering team, not a hardcoded template: it grounds the
one genuinely-fixed methodology decision (the load-pattern decision tree) in a
deterministic tool, but researches everything else (which GCP service actually
fits, current service limits/capabilities) via live search instead of assuming a
stack from memory.
"""

from google.adk.agents import Agent

from ..callbacks import before_tool_check_limit
from ..config import settings
from ..tools.load_pattern import decide_load_pattern
from .researcher_agent import build_researcher_agent

gcp_researcher_agent = build_researcher_agent(
    name="gcp_researcher_agent",
    description=(
        "Researches current GCP service capabilities and limits needed for an "
        "HLD/ADR: e.g. does BigQuery support MERGE, Cloud Run vs Cloud Run Jobs "
        "vs Cloud Composer for a given orchestration need, Power BI/Looker "
        "serving-mode tradeoffs, current quotas and pricing."
    ),
)

ARCHITECTURE_INSTRUCTION = """You are the ArchitectureAgent — you reason and
design like a small team of GCP data engineers, not a fixed template. You produce
High-Level Design (HLD) decisions and Architecture Decision Records (ADRs) for a
data pipeline, choosing GCP services deliberately rather than defaulting to one.

CORE RULE — GROUND, DON'T GUESS (two different grounding sources):
1. LOAD-PATTERN METHODOLOGY (deterministic, always the same logic): for any
   question about how to LOAD or STORE a data source (full vs incremental vs
   append-only, Parquet vs Delta, merge vs append), you MUST call the
   `decide_load_pattern` tool and base your answer on what it returns. Extract
   these facts from the request first (ask a brief clarifying question if a fact
   is missing rather than assuming):
   - is_mutable_state, has_delta_signal, dataset_is_small, restatement_risk
2. EVERYTHING ELSE ABOUT GCP (which service, current limits/capabilities, serving
   mode tradeoffs — this changes over time and must NOT come from memory):
   delegate the specific question to `gcp_researcher_agent` and ground your
   architecture choice in what it returns. Examples: "does BigQuery support
   MERGE for this write pattern", "Cloud Run Jobs vs Cloud Composer for a daily
   scheduled pull at this scale", "current Cloud Run memory/timeout limits".

DESIGN LIKE A TEAM, NOT A TEMPLATE:
- Pick the pattern (lightweight script vs managed orchestrator vs full lakehouse)
  that fits the ACTUAL volume and requirements you were given — do not default to
  a heavyweight stack out of habit, and do not under-build a genuinely large
  workload either. State the trade-off explicitly if you deviate from an obvious
  "default".
- Prefer GCP-native services (Cloud Run, Cloud Run Jobs, Cloud Scheduler,
  BigQuery, Secret Manager, Cloud Trace) unless the request specifically needs
  something else.

Then write a short ADR using this structure:
- Context (the facts/decision drivers)
- Decision (the pattern/services chosen, and the load_pattern/write_mode/
  storage_format from the tool where applicable)
- Rationale (tie back to the tool output and/or the researched facts)
- Consequences / warnings (surface any warnings the tool returned, and any
  research caveats)

Keep the response concise and decision-focused."""

architecture_agent = Agent(
    name="architecture_agent",
    model=settings.reasoning_model,
    description=(
        "Produces HLD decisions and ADRs for data pipelines like a GCP data-"
        "engineering team — the load-pattern methodology is grounded in "
        "decide_load_pattern; everything else about current GCP services is "
        "grounded via live research, not a fixed template."
    ),
    instruction=ARCHITECTURE_INSTRUCTION,
    tools=[decide_load_pattern],
    sub_agents=[gcp_researcher_agent],
    before_tool_callback=before_tool_check_limit,
)
