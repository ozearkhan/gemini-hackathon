# Instructions for the Build Agent
## Deliverable: "PDLC Copilot" — Gemini Enterprise Global Hackathon Deck + Diagram Set

> Checked in for reference per Part 4.6. This is the original build brief. See
> [../README.md](../README.md) for the honesty-status reconciliation of the vision-vs-build
> table (some brief assumptions — e.g. ADK file-Skills as the doc-gate — were corrected to
> match the actual repo implementation: researcher sub-agent + Developer Knowledge MCP +
> deterministic standard tool, enforced by the grounding-gate callback).

Paste this whole document into the IDE agent as its brief. It has four parts:
1. The pitch (what story we're selling, and why)
2. The exact slide list and per-slide content brief
3. The diagram specs (HLD, LLD, phase flow, MCP map) — build these first, slides embed them
4. Production instructions (formats, file outputs, what "done" looks like)

Do not treat the slide template below as rigid — it's EPAM's standard hackathon skeleton
(Team / Problem / Solution / Architecture / Next Steps / Lessons Learned / Visuals). We are
keeping all seven required slides but inserting extra architecture/diagram slides between
"Solution" and "Next Steps," because the thing we're selling *is* the architecture and the
phased methodology behind it.

---

## PART 1 — THE PITCH

**One-line pitch:** We turned a senior data engineer's manual PDLC checklist — intake,
requirements, architecture, ADRs, JIRA breakdown, build, review — into a supervised,
doc-grounded agent graph that can own the *long tail* of small-to-medium data requests
end-to-end, producing the same paper trail a human team would, in hours instead of weeks.

**Who it replaces/augments:** Not senior architects on big, novel, cross-team platform
builds. The target is the "quick ask" category that consumes the most calendar time in
aggregate — a 10-ticker stock tracker, a small competitor-watch dashboard, a one-off
ingestion job — where the *process* (feasibility check, ADRs, JIRA hygiene, review gates)
is what's usually skipped under time pressure, not the code. Sell this explicitly: the value
isn't "AI writes the pipeline," it's "AI can't skip the governance steps even when a human
would be tempted to."

**The credibility hook:** Our original design was a full LangGraph/LangChain/MCP harness —
supervisor-of-workers per phase, LangSmith as the grounding-eval gate, Context7 as the
doc-truth source. For the hackathon's timebox we re-platformed onto Gemini Enterprise / GCP
and kept the same graph topology and non-negotiables (doc-before-code gate, human-in-the-loop
gates, full trace, everything traceable to a written requirement or ADR). Frame the hackathon
build as a **"vertical slice through the full architecture,"** not a toy.

**Differentiation for judges:**
- Not another code-gen copilot. We keep the boring, valuable, usually-skipped middle:
  requirement sign-off, ADRs, review gates, JIRA traceability. It's a governance/process
  product wearing an agent architecture.
- Hallucination control is architectural, not a system prompt. The doc-fetch step is a graph
  edge the code-generation node cannot be reached without.
- It's designed to *fail closed*: no human gate approval in state → cannot advance. No
  doc-fetch trace before a codegen trace → the eval gate blocks the PR.

**Part 1a — vision-vs-build mapping (literal content for slide 4c).** Verify each right-hand
cell against the real implementation before finalizing; mark anything not built as "planned /
next phase." (Done — see README honesty table.)

**Proof-of-dynamic-loading:** grounding here is conditional and load-bearing — the
architecture agent loaded/cited the standard on a request that matched the team's pattern and
did NOT load it on a non-matching internal batch job. Cite this when a judge asks "how do you
know it's really checking, not just always including everything." Attach the two transcripts
on slide 8/9.

**Persuasive weight (rehearse in order):** Solution → Architecture/Vision → Phase Flow →
Next Steps. Keep Problem and Team short.

---

## PART 1B — THE "ARCHITECT-AGENT" RIGOR STANDARD (applied to every diagram)

1. Every node carries a traceable artifact, not just a name.
2. Every arrow implies a real mechanism, statable in one clause.
3. One consistent color/notation legend, reused identically across all four diagrams
   (gray = agent-executed phase, amber = human gate, teal = published artifact/tool).
4. Every non-trivial choice answers "why," even in one clause (ADR discipline).
5. Show the unhappy path, not just the golden path.
6. Reuse the same IDs everywhere (Gate-1 / Gate-2 across diagram, slide, AC, ADR).

Density discipline: simplify until only load-bearing structure remains.

---

## PART 2 — SLIDE LIST

1. Team **[REQUIRED]**
2. The Problem **[REQUIRED]**
3. The Solution **[REQUIRED]**
4a. HLD: System Architecture — **[REQUIRED]**
4b. LLD: Doc-Grounding Gate + State — **[REQUIRED]**
4c. Original Vision vs. Hackathon Build — **[ADDED, credibility slide]**
5. Phased Rollout / Phase Flow + MCP map — **[ADDED]**
6. Next Steps **[REQUIRED]**
7. Lessons Learned **[REQUIRED]**
8. Visuals / Demo **[REQUIRED]**

Each slide carries the EPAM header/footer ("EPAM Proprietary & Confidential" /
"GEMINI ENTERPRISE GLOBAL HACKATHON") and a slide number.

*(As built, the MCP map is its own slide 6 and Next Steps/Lessons/Visuals follow — 11 slides
total including the title. See slide-copy.md.)*

---

## PART 3 — DIAGRAM SPECS

- **Diagram 1 — HLD:** whole agent system; intake → coordinator → one box per phase → two
  human gates positioned where they block → tool/MCP layer row → observability dotted across.
- **Diagram 2 — LLD:** the doc-grounding gate — plan → doc/research fetch → gate → save, with
  "only reachable path" labelled and the shared state object feeding every node.
- **Diagram 3 — Phase Flow:** Phase 0→5 with gates, artifact labelled under each box, legible
  to a non-technical judge; matches the playbook flowchart.
- **Diagram 4 — MCP Map:** which grounding source/MCP per phase; static (always loaded) vs.
  dynamic (pattern-conditional); honest wired-vs-next-phase split.

Delivered as editable `.mmd` sources in `../diagrams/` **and** as native editable vector
shapes inside the deck (no mermaid CLI on the authoring box).

---

## PART 4 — PRODUCTION INSTRUCTIONS

1. Diagrams first, then the deck (slides embed them).
2. Mermaid source kept for every diagram; rendered natively in the deck.
3. Deck as a real `.pptx` with the EPAM look (footer, header, slide numbers).
4. No fabricated facts — names, screenshots, lessons are placeholders where not available.
5. Honesty on the vision-vs-build table — "planned / not yet implemented" where not built.
6. Output: `.pptx` in `deliverables/pitch-deck/`, `.mmd` sources in `deliverables/diagrams/`,
   this brief checked in.
7. Before "done": read slides 3, 4a–4c, 5 aloud; gloss every jargon term (LangGraph, MCP,
   ADR, ADK) on first use.
