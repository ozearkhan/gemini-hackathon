# Project Rules — Gemini Enterprise Hackathon (Stream 2)

These rules are binding for every task in this repo. Read before editing or running anything.

## RULE 1 — Dev-here / Run-on-remote (NON-NEGOTIABLE)

This workstation **cannot authenticate to GCP**. It is an **authoring-only** machine.

- ✅ **DO here:** edit code, write tests/evals, run linters and offline unit tests,
  scaffold, plan, and commit + push with git.
- ❌ **NEVER here:** `gcloud`, `adk deploy`, `adk web` against cloud, `agents-cli deploy`,
  `agents-cli eval` (cloud), or anything needing GCP / ADC auth. These will fail — do not attempt.
- 🚀 **Execution happens on the REMOTE machine only.** Workflow is always:
  1. Make ALL changes locally on this machine.
  2. `git commit` + `git push origin master` to `https://github.com/ozearkhan/gemini-hackathon`.
  3. Remote machine does `git pull` and runs the command.
  4. Paste the remote output back here for analysis.
- 🔒 **The remote is execute-only. NEVER edit source on the remote.** Source of truth is this
  machine. Any change made on the remote is a bug — reproduce it here and push instead.
- When a task needs a cloud command, **do not run it** — output the exact command(s) for the
  user to run on the remote, then wait for the output.

## RULE 2 — Skills-first: use agents-cli + google/skills for EVERYTHING (MANDATORY)

We lack deep GCP exposure. The vendored Google skills in `.github/skills/` carry the
correct, current GCP + ADK context — using them is how we avoid deploy and
Gemini-Enterprise registration failures later. **agents-cli is our golden path and
is always active.**

**Before implementing ANYTHING** — agent/tool code, an eval, a deploy step, an
IAM/security choice, a `gcloud` command — FIRST open the best-matching skill in
`.github/skills/` and follow it. Do not improvise when a skill covers the task.

Skill routing — match the task to the skill folder under `.github/skills/`:

| Task | Skill |
|---|---|
| ADK agent / tool / orchestration code | `google-agents-cli-adk-code`, `google-agents-cli-workflow` |
| New project / scaffolding | `google-agents-cli-scaffold` |
| Evals & test methodology | `google-agents-cli-eval`, `agent-platform-eval-flywheel` |
| Deploy (Cloud Run / Agent Engine) | `google-agents-cli-deploy`, `cloud-run-basics`, `google-cloud-solution-build-deploy-agents` |
| Register agent in Gemini Enterprise | `google-agents-cli-publish` |
| Authenticate to GCP | `google-cloud-recipe-auth` |
| `gcloud` CLI usage | `gcloud` |
| Security / least-privilege / guardrails | `google-cloud-waf-security` |
| Logging / tracing / observability | `google-agents-cli-observability` |

- On the remote, invoke the toolchain directly: `uvx google-agents-cli <cmd>`.
- **Test-Driven:** write the eval/test that defines "done" BEFORE implementing. Red → green → refine.
- **Code preservation:** do not delete or rewrite working code without cause. Surgical changes only.

## RULE 3 — Security & structure (maps to judging criteria)

- **No hardcoded secrets / API keys.** Use env vars locally (`.env`, git-ignored) and
  **Secret Manager** on GCP. Never commit `.env`.
- **Least-privilege IAM.** Grant only the roles a service needs.
- **ADK packaging rule:** `requirements.txt` and `agent.json` MUST live inside the agent
  package folder (`pdlc_agent/`), never at the top level. ADK only copies the package.
- **Infra as Code:** all GCP resources defined in Terraform (`infra/`), not clicked in the console.
- The ADK entry point variable MUST be named `root_agent`.

## RULE 4 — Documentation (15% of score)

Keep these current as the build progresses: `README.md` (developer landing page),
`docs/architecture.md` (+ diagram), `docs/deployment.md`. Link them from the README.

## RULE 5 — EPAM sandbox guardrails (hard constraints from the hackathon KB)

- **Cloud Run: always `--no-allow-unauthenticated`.** Org policy rejects
  `--allow-unauthenticated`. Grant `roles/run.invoker` (+ `roles/aiplatform.user`
  for Agent Runtime) to the Layer 1 Discovery Engine SA
  `service-71784361107@gcp-sa-discoveryengine.iam.gserviceaccount.com`.
- **$100 hard cap per project** (auto-stop at 100%; alerts 50/75/90%). Use
  backoff, caching, prompt compression; never bypass billing controls.
- **No external non-GCP services / paid APIs / unvetted SaaS without Platform
  Architect sign-off.** Prefer GCP-native (Vertex AI, Google Developer Knowledge
  MCP, BigQuery). Context7 / Atlassian / GitHub MCP are NOT default-approved →
  grounding uses Dev-Knowledge MCP + Vertex AI; ticket/doc trees are emitted as
  repo artifacts, not pushed to external SaaS.
- **No live client / PII / confidential data.** Synthetic + public data only.
- **No GKE / GPU / large persistent compute.** Cloud Run + Agent Runtime only.
- **Never modify Layer 1.** Binding/registration is via support ticket only.
- **Submission repo = EPAM GitLab** (`git.garage.epam.com/[team-slug]`). GitHub
  `origin` is our dev sync; mirror to GitLab for the final submission.
