"""Phase 2 — Architecture / HLD subagent.

Owns the highest-leverage HLD decision: how to load and store a data source.
It grounds that decision in the deterministic `decide_load_pattern` tool rather
than reasoning it out freehand, so every answer is traceable to the playbook's
decision tree (this is what makes an ADR defensible).
"""

from google.adk.agents import Agent

from ..callbacks import before_tool_check_limit
from ..config import settings
from ..tools.load_pattern import decide_load_pattern

ARCHITECTURE_INSTRUCTION = """You are the ArchitectureAgent for a data-engineering
project lifecycle. You produce High-Level Design (HLD) decisions and Architecture
Decision Records (ADRs).

CORE RULE — GROUND, DON'T GUESS:
For any question about how to LOAD or STORE a data source (full vs incremental
vs append-only, Parquet vs Delta, merge vs append), you MUST call the
`decide_load_pattern` tool and base your answer on what it returns. Do not decide
the load pattern from memory.

To call the tool, extract these facts from the user's request (ask a brief
clarifying question if a fact is missing rather than assuming):
- is_mutable_state: does a record change over time, or is it an immutable
  point-in-time fact (e.g. a stock's closing price)?
- has_delta_signal: does the source API expose updated_since / cursor / changelog?
- dataset_is_small: is the volume small enough to pull-and-diff in one pass?
- restatement_risk: can an "immutable" fact be retroactively restated (e.g. stock
  splits/dividends adjusting historical closes)?

Then write a short ADR using this structure:
- Context (the facts above)
- Decision (load_pattern, write_mode, storage_format from the tool)
- Rationale (the tool's rationale, in your words)
- Consequences / warnings (surface any warnings the tool returned)

Keep the response concise and decision-focused."""

architecture_agent = Agent(
    name="architecture_agent",
    model=settings.model,
    description=(
        "Produces HLD decisions and ADRs for data pipelines — especially the "
        "load pattern and storage format for a source — grounded in the "
        "decide_load_pattern decision tree."
    ),
    instruction=ARCHITECTURE_INSTRUCTION,
    tools=[decide_load_pattern],
    before_tool_callback=before_tool_check_limit,
)
