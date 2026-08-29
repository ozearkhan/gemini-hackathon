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

## RULE 2 — Use agents-cli skills; never ship bad code

We lack deep GCP exposure, so we lean on Google's skills to stay on the golden path.

- Follow the **agents-cli** skills for all ADK work: `workflow` (lifecycle + code-preservation),
  `adk-code` (agent/tool/orchestration API), `scaffold`, `eval`, `deploy`, `publish`,
  `observability`. Prefer their patterns over improvised code.
- Follow selected **google/skills** for GCP foundations (auth, Cloud Run, Secret Manager,
  IAM, Well-Architected security). See `docs/skills.md` for the picked list.
- **Test-Driven:** write the eval/test that defines "done" BEFORE implementing. Red → green → refine.
- **Code preservation:** do not delete or rewrite working code without cause. Surgical changes only.

## RULE 3 — Security & structure (maps to judging criteria)

- **No hardcoded secrets / API keys.** Use env vars locally (`.env`, git-ignored) and
  **Secret Manager** on GCP. Never commit `.env`.
- **Least-privilege IAM.** Grant only the roles a service needs.
- **ADK packaging rule:** `requirements.txt` and `agent.json` MUST live inside the agent
  package folder (`demo_agent/demo_agent/`), never at the top level. ADK only copies the package.
- **Infra as Code:** all GCP resources defined in Terraform (`infra/`), not clicked in the console.
- The ADK entry point variable MUST be named `root_agent`.

## RULE 4 — Documentation (15% of score)

Keep these current as the build progresses: `README.md` (developer landing page),
`docs/architecture.md` (+ diagram), `docs/deployment.md`. Link them from the README.
