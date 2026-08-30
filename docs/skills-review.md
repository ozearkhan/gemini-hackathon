# Agent Skills Review — Expected vs. Current

An honest, engineer-level audit of each of the 5 skills advertised in
[`pdlc_agent/agent.json`](../pdlc_agent/agent.json). For every skill: what
input it's meant to take, what "done right" looks like, and — separately —
exactly what the current implementation actually does today, including named
gaps. Written after the 2026-08-30 real-transcript audit that found the
researcher-handoff stall bug (fixed) — this doc exists so the next gap isn't
found the same way.

---

## 1. `intake_triage` — Phase 0

**Expected input:** a raw, informal new data request (Slack message, email,
ticket) — no structure required.

**Expected behavior:** one short paragraph answering who's asking / net-new or
not / rough size / urgency, ending in a PROCEED-to-Phase-1 or
FAST-TRACK-as-spike decision, then **immediately continuing into Phase 1**
without waiting for a human — the playbook defines no gate here.

**Current implementation:**
- Tool-free, `fast_model` (`gemini-3.7-flash`) — cheap and fast by design.
- **Just fixed (2026-08-30):** previously stated its decision and stopped,
  requiring the user to say "yes"/"proceed" before continuing — an
  unintentional pause with no corresponding gate in the playbook. Instruction
  now explicitly commands `transfer_to_agent(agent_name="requirements_analyst_agent")`
  immediately on PROCEED. **Not yet re-verified end-to-end after redeploy.**

---

## 2. `requirement_analysis` — Phase 1

**Expected input:** the same raw request (often already triaged), or a reply
to previously raised Open Questions.

**Expected behavior:** a 10-point structured checklist (end-user archetype,
business impact, semantic scope, entity/list stability, historical depth,
source feasibility, output schema/cadence, non-functional reqs, data quality,
missing-but-needed info) producing a versioned Requirement Analysis with a
Build-Readiness verdict, gated by a Go/No-Go decision before Phase 2 begins.
Every vendor/API factual claim must be grounded in live research, never memory.

**Current implementation:**
- Delegates all factual research to `requirements_researcher_agent`
  (real `google_search` grounding — confirmed working with real citations in
  the 2026-08-30 test transcript: Alpha Vantage/Finnhub/IEX Cloud/Marketstack
  with real domains).
- **Structurally enforced:** `save_requirement_doc` is refused by
  `before_tool_check_limit_and_gates` unless the researcher actually ran this
  session (not just an instruction — raises an error if skipped).
- **Critical bug, just fixed:** the researcher never returned control to this
  agent — it kept chatting directly with the user turn after turn, so the
  Requirement Analysis doc was **never produced** in the real test run. This
  is why gaps like "which specific 10 tickers?" were never surfaced — the
  checklist that would have caught it (items #4, #10) never got a chance to
  run. **Not yet re-verified end-to-end after redeploy.**
- **Known, un-fixed gap:** `save_requirement_doc` (like `save_architecture_doc`)
  writes to the container's local filesystem via `Path.write_text` — on
  Cloud Run this is ephemeral and never visible outside the running
  container. The only way a user actually *sees* the doc is if the model
  echoes the full markdown in its own chat response (which the instruction
  requires, but nothing structurally enforces it). No downloadable artifact
  exists in Gemini Enterprise today.

---

## 3. `architecture_hld` — Phase 2

**Expected input:** an approved (or at least drafted) Requirement Analysis,
or a direct methodology question (load pattern, cost comparison).

**Expected behavior:** ground the recommendation in the org's real
architecture standard first, use a deterministic decision tree for the one
fixed methodology question (load pattern), research everything else
GCP-specific live, propose a cost comparison across viable patterns, produce
an ADR-bearing HLD document, and **refuse to finalize without explicit human
approval**.

**Current implementation:**
- `get_architecture_standard` reads a real, committed doc
  ([`docs/architecture-standard-gcp.md`](architecture-standard-gcp.md)) — not
  hallucinated; flags if missing rather than fabricating content.
- `decide_load_pattern` — deterministic, unit-tested (6 tests covering
  mutable/immutable, delta signal, restatement risk combinations).
- `estimate_gcp_cost` — **known limitation, honestly labeled**: a rough-order-
  -of-magnitude calculator built from general GCP pricing knowledge, *not*
  from live Cloud Billing/Recommender APIs (the actual toolchain the
  `google-cloud-waf-cost-optimization` skill recommends). Every result
  carries a `basis` disclaimer stating this.
- `gcp_researcher_agent` (real `google_search`) + **newly wired**
  `search_documents` (Developer Knowledge MCP, Google's own docs) — the MCP
  wiring is committed but **not yet verified with a real query** on the
  deployed service.
- **Structurally enforced:** `save_architecture_doc` refused without
  `record_human_approval(slug)` having been called first.
- Same ephemeral-storage gap as `requirement_analysis` (§2) applies here too.

---

## 4. `iac_scaffolding` — Phase 5

**Expected input:** an approved architecture with concrete parameters
(project_id, region, dataset/table/secret IDs, cron schedule).

**Expected behavior:** provision the real Terraform prerequisites for the
approved design, refuse to run without approval, and be **honest about what
it couldn't safely generate** rather than guessing at unverified syntax.

**Current implementation:**
- `generate_terraform_skeleton` generates **only** BigQuery dataset/table and
  Secret Manager + IAM resources — verified-syntax only. It deliberately
  leaves a `TODO(verify)` marker for Cloud Scheduler → Cloud Run Job wiring
  rather than guessing. This is a **known, intentional, and honestly-flagged**
  scope limit, not a hidden bug.
- **Newly wired:** `search_documents` (Developer Knowledge MCP) so the agent
  *could* now look up the current syntax for that TODO instead of just
  flagging it — instruction updated to allow this, but the tool itself
  (`generate_terraform_skeleton`) was **not** changed to actually emit the
  extra resource; the agent can only report what it found, not act on it yet.
  This is a real opportunity for a follow-up feature, not yet built.
- **Structurally enforced:** refused without recorded approval, same
  mechanism as architecture.

---

## 5. `jira_breakdown` — Phase 4

**Expected input:** an approved, infra-provisioned design.

**Expected behavior:** break the remaining development work into an
Epic → Feature → Story → Task tree, every leaf task traceable to a
requirement or ADR, and refuse to run before infra is provisioned.

**Current implementation:**
- `check_task_traceability` is a **purely syntactic** validator — it checks
  that a `trace_ref` string is present and non-blank on every task. It does
  **not** verify that the referenced ID (e.g. `REQ-1.3`, `ADR-002`) actually
  exists in a previously-saved Requirement Analysis or Architecture doc. A
  task citing a made-up ID would currently pass. This is a real, un-flagged
  gap — worth fixing if traceability needs to be provably correct rather than
  just present.
- Gate on "infra provisioned first" is instruction-only (no structural
  enforcement equivalent to the approval/grounding gates elsewhere) — relies
  on the model reading the user's stated context correctly, not a hard
  refusal like the other four skills have.
- **Newly wired:** `search_documents` (Developer Knowledge MCP) for confirming
  exact GCP service/resource names in task wording — unverified with a real
  query so far.

---

## Cross-cutting gaps (affect multiple skills)

1. **Ephemeral document storage** (§2, §3): `save_requirement_doc` /
   `save_architecture_doc` write to the container's local filesystem. Works
   perfectly when running locally (`agents-cli playground`) since the write
   lands in the real git working directory — but on the deployed Cloud Run
   service there is no way to retrieve that file afterward. The only
   guaranteed-visible copy is whatever the model echoes in chat.
2. **`jira_breakdown`'s traceability check is syntactic, not semantic** (§5).
3. **`iac_scaffolding` can now research the TODO but not yet act on it** (§4).
4. **Cost estimates are ROM, not live-priced** (§3) — labeled, not hidden.

None of these four are corrected in this pass — they're documented here so
they're a deliberate backlog item, not a surprise found later.
