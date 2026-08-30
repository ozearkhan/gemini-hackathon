# Deliverables — PDLC Copilot Hackathon Deck

Generated deliverables for the Gemini Enterprise Global Hackathon pitch.

## Contents

```
deliverables/
├── pitch-deck/
│   ├── PDLC-Copilot-Hackathon-Deck.pptx   ← the deck (11 slides, 16:9, EPAM-branded)
│   ├── build_deck.py                       ← reproducible generator — edit copy here, re-run
│   ├── slide-copy.md                       ← per-slide copy + speaker notes
│   └── build-agent-brief.md                ← the original build brief, checked in for reference
└── diagrams/
    ├── 01-hld-system-architecture.mmd      ← editable Mermaid sources for all four diagrams
    ├── 02-lld-doc-grounding-gate.mmd
    ├── 03-phase-flow.mmd
    └── 04-mcp-ecosystem-map.mmd
```

## Regenerate the deck

```powershell
# from the repo root, using the workspace venv
& .\.venv\Scripts\python.exe deliverables\pitch-deck\build_deck.py
```

Diagrams are drawn as **native, editable PowerPoint vector shapes** inside the deck (boxes,
connectors, legend) — so they can be tweaked directly in PowerPoint and re-coloured without
any external renderer.

## About the diagram images

This authoring machine has **no Node / mermaid CLI**, so the `.mmd` files are not rendered to
PNG/SVG here. Two ways to get raster images if a slide needs a standalone image asset:

- On any box with Node: `npx -y @mermaid-js/mermaid-cli -i <file>.mmd -o <file>.png -w 1920 -H 1080`
- Or paste the `.mmd` into <https://mermaid.live> and export. *(Do not send content through
  external renderers for anything confidential — these diagrams are architecture-only, no data.)*

The deck itself does **not** depend on those images — its diagrams are native shapes.

## Honesty status (verified against repo code, not assumed)

The vision-vs-build table (slide 4c) and the MCP map (slide 6) are labelled REAL vs. NEXT PHASE
against the actual implementation:

| Claim | Status | Evidence in repo |
| :--- | :--- | :--- |
| ADK Coordinator-Dispatcher, 5 specialists | REAL | `pdlc_agent/agent.py` |
| `google_search` researcher grounding | REAL | `pdlc_agent/agents/researcher_agent.py` |
| Google Developer Knowledge MCP | REAL | `pdlc_agent/tools/dev_knowledge.py` |
| Repo architecture-standard grounding | REAL | `pdlc_agent/tools/architecture_standard.py` |
| Structural approval + grounding gates (raise + refuse) | REAL | `pdlc_agent/callbacks.py` |
| Cloud Trace + BigQuery telemetry | WIRED | `deployment/terraform/single-project/telemetry.tf` |
| CI-blocking grounding **evaluator** | NEXT PHASE | eval harness exists (`tests/eval/`); CI gate not yet |
| Durable `interrupt()`-style HITL | NEXT PHASE | current gates live in the chat turn (`callbacks.py`) |
| Atlassian / GitHub live MCP (Jira/Confluence/PR) | NEXT PHASE | artifacts emitted to repo; SaaS MCP needs sign-off |

> Corrected vs. the original brief: grounding is **not** ADK file-based Skills
> (`SkillToolset`/`load_skill`) — it is the researcher sub-agent + Developer Knowledge MCP +
> the deterministic standard tool, enforced by the grounding-gate callback. The deck reflects
> the real mechanism.

## Before presenting

- Fill the `[NAME — ROLE]` placeholders on slide 1.
- Replace the `[SCREENSHOT: …]` placeholders on slide 9 with real demo captures.
- Add real org numbers on slide 2 (or leave marked "illustrative").
- Add the team-specific fifth lesson on slide 8.
