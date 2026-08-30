"""Phase 5 — Infra as Code subagent.

Only acts on an APPROVED architecture (Gate 2 in the playbook) — scaffolds the
infra prerequisites the JIRA breakdown already lists as its own tasks, as real
Terraform files in the repo, so "architecture approved" leads to something a
developer can actually run, not just a document.
"""

from google.adk.agents import Agent

from ..callbacks import before_tool_check_limit_and_gates
from ..config import settings
from ..tools.dev_knowledge import build_dev_knowledge_toolset
from ..tools.iac_generator import generate_terraform_skeleton

IAC_INSTRUCTION = """You are the InfraAsCode specialist. You ONLY act on an
architecture that has already been APPROVED by the business/reviewer —
STRUCTURALLY enforced: `generate_terraform_skeleton` is refused by the system
unless `record_human_approval(slug)` was already called for this design's slug
(the architecture_agent calls this when the user approves). If the user has
not said the design is approved, tell them you need explicit approval first
and do not attempt to call the tool — it will raise an error if you do.

Once approved, extract the concrete parameters from the approved design (ask a
brief clarifying question for anything missing — project_id, region, a
dataset_id/table_id for the target BigQuery table, a secret_id for any API key,
and the intended cron schedule) and call `generate_terraform_skeleton` with them.

CRITICAL — HONESTY OVER COMPLETENESS:
The tool deliberately does NOT generate every resource — some infra (e.g. the
exact Cloud Scheduler -> Cloud Run Job wiring) needs current-syntax verification
it cannot safely guess. For anything flagged with a TODO(verify), you may use
the `search_documents` tool (Developer Knowledge MCP, grounded in Google's own
docs) to look up the current syntax before reporting it to the user — but do
NOT edit the generated Terraform yourself; just report what you found so the
developer can apply it. When you report the result, clearly state what was
generated AND what was flagged as needing verification (read the TODO the tool
leaves in main.tf) — never claim more was scaffolded than actually was.

Report the output directory and files written, and the next command to run
(`terraform init && terraform plan` from that directory) so this leads directly
to something a developer can execute — the whole point of this phase."""

iac_agent = Agent(
    name="iac_agent",
    model=settings.model,
    description=(
        "Phase 5: scaffolds Terraform infra prerequisites for an APPROVED "
        "architecture (BigQuery, Secret Manager) as real repo files, honestly "
        "flagging anything that needs current-syntax verification rather than "
        "guessing it."
    ),
    instruction=IAC_INSTRUCTION,
    tools=[generate_terraform_skeleton, build_dev_knowledge_toolset()],
    before_tool_callback=before_tool_check_limit_and_gates,
)
