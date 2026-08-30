# Slide Copy & Speaker Notes — PDLC Copilot

Reference for the deck in `PDLC-Copilot-Hackathon-Deck.pptx`. Rehearse slides 3, 4a–4c and 5
out loud; every jargon term gets a 4–6 word plain-language gloss the first time it appears.

Persuasive weight (spend rehearsal time here, in order): **Solution → Architecture/Vision →
Phase Flow → Next Steps.** Problem and Team are necessary, not differentiating — keep short.

---

## Slide 1 — Team
**Say:** "Team agenti-1711. We built PDLC Copilot — an agent that runs the data-engineering
project lifecycle end to end for the small requests that usually get rushed."
**Do:** fill the `[NAME — ROLE]` placeholders. Don't invent names.

## Slide 2 — The Problem
**One-liner:** every "quick" data ask needs the same six process steps a big build does — but
under deadline pressure teams skip them, and that's where debt, compliance misses, and rework come from.
**Key beat:** it's a *governance* gap, not a tooling gap. The checklist exists; consistent
execution at real request volume doesn't. Naive AI makes it worse — it hallucinates a rate
limit or invents Terraform, turning a time problem into a trust problem.

## Slide 3 — The Solution (spend the most time here)
**Plant the claim:** "This owns the *long tail* of small-to-medium data requests — and it
**can't skip a governance step even when a human would be tempted to.**"
**The what:** intake → requirement doc → sign-off gate → architecture + ADRs (Architecture
Decision Records — the written 'why' behind a choice) → review gate → infra-as-code → JIRA tree.
**The differentiator, said plainly:** the value isn't "AI writes the pipeline" — it's "AI
can't skip the paper trail." Reference case: the daily competitor stock tracker.

## Slide 4a — HLD: System (what we shipped)
**Caption:** one supervisor (Coordinator-Dispatcher — one router, many specialists), one
specialist per phase, a grounding step in front of every decision, and two human gates.
**Say:** "Centralized, not a swarm — because the PDLC *is* a paper trail. One place the state
and the trace live, so every choice is auditable." Point out the guardrails row: they *raise
and refuse* — code, not a prompt.

## Slide 4b — LLD: The Doc-Grounding Gate (the technical proof point)
**Caption:** this is the actual anti-hallucination mechanism — a graph edge, not a prompt
instruction, so the persist step is architecturally unreachable without a preceding real fetch.
**Say:** "The researcher writes evidence into shared state; the save tool checks for it and
raises `GroundingRequiredError` if it's missing. It fails *closed* — no research, nothing persists."

## Slide 4c — Original Vision vs. Hackathon Build (the credibility slide)
**Headline:** "Same architecture, two runtimes." We prototyped the full vision on
LangGraph/LangChain/MCP/LangSmith (an agent-orchestration stack); for the timebox we
re-platformed the same graph onto Google ADK (Agent Development Kit) / GCP.
**Be unembarrassed about status:** read the right column honestly — REAL where it's wired,
NEXT PHASE where it isn't. Judges trust "here's exactly how much we stood up" far more than
an overstated claim that breaks under a follow-up.
**Proof beat:** grounding is *conditional* — the architecture agent cited the standard on a
matching request and did NOT load it on a non-matching one. That's mechanical proof it's
load-bearing, not a doc dumped into every prompt.

## Slide 5 — Phase Flow (technical-depth proof)
**Say:** "Same backbone whether a human or an agent runs it — that's deliberate; it's what
makes each phase independently automatable and auditable."
**Show the unhappy path:** Gate-1 revise loop (v1.0→v1.1), Gate-2 conditional/reject loops.
**The clever bit:** infra is provisioned right after architecture approval, *before* the JIRA
breakdown — so there's no "set up the infra" ticket; the environment already exists.

## Slide 6 — Grounding & MCP Ecosystem (honest map)
**Say:** "Wired and real: Google Developer Knowledge MCP, the google_search researcher, and the
repo architecture standard. Next phase: live Jira/Confluence/GitHub — today those artifacts are
emitted to the repo, same paper trail, zero external dependency." Name the EPAM guardrail:
external non-GCP SaaS MCP needs Platform-Architect sign-off, so the default is GCP-native.

## Slide 7 — Next Steps
Frame as "close the gaps in the 4c table": (1) CI-blocking grounding evaluator, (2) dynamic
pattern-conditional MCP binding, (3) durable async approval gates, (4) enterprise-readiness
checklist (secrets, IAM per MCP, audit logging, on-call owner), (5) Patterns A–C for bigger
requests, (6) opt-in live SaaS actions once sign-off lands.

## Slide 8 — Lessons Learned
**Lead with the strongest, and it's true:** the doc-gate thesis happened to *us* — a local TDD
instruction contradicted the vendor eval skill's guidance, and we changed our instruction to
match the skill. "Grounding beats a hand-written instruction, even our own." Then: making gates
load-bearing was harder than the LLM calls; re-platforming clarified architectural vs.
framework-specific; narrow specialists beat a monolith. Add one more that's genuinely true.

## Slide 9 — Visuals / Demo
Replace the four `[SCREENSHOT: …]` placeholders with real captures: requirement doc generated,
approval gate in the chat turn, grounding gate refusing a save, generated Terraform + JIRA tree
in the repo. Live demo prompts are listed on the slide and all work today.
