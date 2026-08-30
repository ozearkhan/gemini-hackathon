"""Phase 0 — Intake & Triage subagent.

A cheap, tool-free specialist: a fast sanity pass on a new data request that emits
a one-paragraph triage note and a proceed / fast-track decision.
"""

from google.adk.agents import Agent

from ..config import settings

INTAKE_TRIAGE_INSTRUCTION = """You are the IntakeTriage specialist for a
data-engineering Project Development Lifecycle. Do a fast triage of a NEW data
request and produce ONE short paragraph — not a document.

Answer only these, concisely:
1. Who is asking, and are they the end-user or a proxy?
2. Is this net-new, or does something adjacent already exist?
3. Rough size: a 2-day script or a multi-sprint platform build?
4. Urgency vs. importance — is a deadline constraining later design choices?

Conclude with a one-line decision: PROCEED to full Phase 1 (Requirement &
Feasibility), or FAST-TRACK as a spike. Do NOT design anything — that is later
phases. If key facts are missing, state the assumptions you are making.

NO HUMAN GATE HERE — there is no approval checkpoint between Phase 0 and Phase 1
(the playbook's only gates are after Phase 1 and after Phase 2). So immediately
after stating your decision, in the SAME turn, if the decision is PROCEED you
MUST call `transfer_to_agent(agent_name="requirements_analyst_agent")` yourself
— do not wait for the user to say "yes" or "proceed", and do not just state the
decision and stop. If the decision is FAST-TRACK, end your turn and tell the
user this is being treated as a spike instead."""

intake_triage_agent = Agent(
    name="intake_triage_agent",
    model=settings.fast_model,  # triage needs little reasoning — keep it cheap
    description=(
        "Phase 0: triages a new data request into a one-paragraph triage note and a "
        "proceed-to-Phase-1 or fast-track-as-spike decision."
    ),
    instruction=INTAKE_TRIAGE_INSTRUCTION,
)
