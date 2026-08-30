# Deployment & GCP Runbook

> **Where these run:** every command here needs GCP auth, so it runs on the **remote** machine (per [.github/copilot-instructions.md](../.github/copilot-instructions.md) RULE 1). This workstation is authoring-only. Workflow: edit here → `git push` → pull on remote → run → paste output back.
>
> Replace `[PROJECT_ID]` with your EPAM Layer-2 sandbox project ID throughout.

**Our values** — Team `agenti-1711` (Agentic PDLC, Stream 2): `PROJECT_ID = hl2-gcpp-ccoe-ge-h-agenti-1711`, region `us-central1`.

---

## Step 0a — First-time remote bootstrap (install the toolchain)

Run **once** on a fresh remote. Unlike this authoring workstation (where we bypassed installs), the remote has full permissions and installs everything directly.

```bash
# 1. Google Cloud SDK — required for gcloud + adk deploy. Verify (install if missing):
gcloud --version          # missing? https://cloud.google.com/sdk/docs/install

# 2. Python 3.11+ (ADK and agents-cli require it)
python3 --version

# 3. uv — fast Python tool runner (no admin needed)
curl -LsSf https://astral.sh/uv/install.sh | sh    # or: pip install --user uv
uv --version

# 4. agents-cli — our golden path (scaffold/eval/deploy/publish). Installed globally via uv:
uv tool install google-agents-cli
agents-cli --version

# 5. Authenticate to GCP (human login + Application Default Credentials for SDKs)
gcloud auth login
gcloud auth application-default login
```

> **Node.js is NOT required** for `agents-cli deploy/eval/publish`. It's only needed by `agents-cli setup` (which wires skills into a coding agent) — and our skills are already vendored in `.github/skills/`, so the remote never needs Node.
>
> **What uses what:** our **deploy** path is `./deploy.sh` (wraps `adk deploy`, from `google-adk` in the venv). `agents-cli` powers **eval** (Slice 6) and is the declared golden path — installing it now means it's ready when we wire evals.

---

## Step 0 — Connectivity smoke test (do this first)

Confirm we can reach the sandbox *before* building anything else. Run on the remote and paste the output back.

```bash
# 1. Who am I / is auth working?
gcloud auth list
gcloud config get-value project

# 2. Point at our sandbox
gcloud config set project [PROJECT_ID]

# 3. Can we see the project + its number? (project number is needed for IAM)
gcloud projects describe [PROJECT_ID] --format="value(projectId, projectNumber)"

# 4. What's already enabled? (sanity — expect aiplatform, run, storage, etc.)
gcloud services list --enabled --project=[PROJECT_ID] --format="value(config.name)" | sort
```

**Pass criteria:** command 3 returns our project ID + a numeric project number, and command 4 lists services without a permission error. If auth fails, follow the `google-cloud-recipe-auth` skill (`gcloud auth login` + `gcloud auth application-default login`).

---

## Step 0b — Verify the reasoning model (do this before first deploy of `pdlc_agent`)

`requirements_analyst_agent` and `architecture_agent` use `settings.reasoning_model`
(`PDLC_REASONING_MODEL`, defaults to `gemini-3.1-pro-preview` — the best available
reasoning-tier model confirmed via the command below on 2026-08-30). Per the ADK
skill, never trust a model name from memory — list what's actually available for
this project and override the env var if a newer/better reasoning model exists:

```bash
python -c "from google import genai; client = genai.Client(vertexai=True, project='hl2-gcpp-ccoe-ge-h-agenti-1711', location='us-central1'); [print(m.name) for m in client.models.list()]"
```

If a newer reasoning-tier model is listed, set `PDLC_REASONING_MODEL=<name>` in `.env`
before deploying.

---

## Step 1 — Enable the API baseline

Safe to re-run even if some are already on (KB §4.2).

```bash
gcloud services enable \
  agentregistry.googleapis.com \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  cloudtrace.googleapis.com \
  discoveryengine.googleapis.com \
  iap.googleapis.com \
  notebooks.googleapis.com \
  observability.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  --project=[PROJECT_ID]
```

> Do **not** enable APIs beyond what you need — unnecessary APIs increase attack surface (KB §4).

---

## Step 2 — IAM: let Layer 1 Gemini Enterprise invoke us

Grant the shared Discovery Engine SA the invoker roles (KB §9.1). Required before registration works.

```bash
PROJECT_ID=[PROJECT_ID]
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
LAYER1_DE_SA="service-71784361107@gcp-sa-discoveryengine.iam.gserviceaccount.com"

# Agent Runtime path
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$LAYER1_DE_SA" \
  --role="roles/aiplatform.user" --condition=None

# Cloud Run A2A path
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$LAYER1_DE_SA" \
  --role="roles/run.invoker" --condition=None

# Cloud Build image pushes — grant the SAME KB role (artifactregistry.writer) to
# BOTH candidate build service accounts. `gcloud run deploy --source` (what
# `adk deploy` wraps) runs the build as the COMPUTE default SA on new projects,
# not the @cloudbuild SA the KB assumes — so without this the push fails with:
# denied: Permission 'artifactregistry.repositories.uploadArtifacts'.
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer" --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/artifactregistry.writer" --condition=None
```

---

## Step 3 — Environment + local dev (on remote)

```bash
git pull origin master
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt -r pdlc_agent/requirements.txt
python -m pytest                      # deterministic tool tests — expect all green

cp .env.example .env                  # set GOOGLE_CLOUD_PROJECT=[PROJECT_ID]
source .env && ./deploy.sh local      # ADK dev UI at http://localhost:8000
```

---

## Step 4 — Deploy

Pick one target. Both are org-policy compliant (`--no-allow-unauthenticated`).

### 4a. Cloud Run with A2A
```bash
source .env && ./deploy.sh cloud_run
```
The script deploys with `--no-allow-unauthenticated` and grants the Layer 1 DE SA `roles/run.invoker`. Copy the printed **A2A endpoint** `https://[service-url]/a2a/pdlc_agent`. Verify:
```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://[service-url]/a2a/pdlc_agent -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"messageId":"m1","role":"user","parts":[{"kind":"text","text":"Hello"}]}}}'
```

### 4b. Vertex AI Agent Runtime
```bash
source .env && ./deploy.sh agent_engine
```
Copy the `reasoningEngines/[RESOURCE-ID]` from the output. (Do **not** pass `--staging_bucket` — deprecated in ADK 2.x, KB §6.2.)

---

## Step 5 — Register in Gemini Enterprise (support ticket — Layer 1, team-gated)

We cannot self-register. Post to the **MS Teams "Gemini Enterprise Hackathon Support"** channel using the matching template (KB §9.2):

**Cloud Run (A2A):**
```
[AGENT REGISTRATION REQUEST — A2A]
Team Slug: [team-slug]
Sandbox Project ID: [PROJECT_ID]
Sandbox Project Number: [PROJECT_NUMBER]
A2A Endpoint URL: https://[service-url]/a2a/pdlc_agent
Validated agent.json Content: { ... from pdlc_agent/agent.json ... }
```

**Agent Runtime:**
```
[AGENT REGISTRATION REQUEST — AGENT RUNTIME]
Team Slug: [team-slug]
Sandbox Project ID: [PROJECT_ID]
Sandbox Project Number: [PROJECT_NUMBER]
Reasoning Engine Resource Name: projects/[PROJECT_NUMBER]/locations/us-central1/reasoningEngines/[RESOURCE-ID]
```

A Platform Admin completes the Layer 1 IAM + app registration and confirms in-thread.

---

## Cost guardrails ($100 hard cap)

Auto-stop at 100%; alerts at 50/75/90%. Keep spend low: fast model for routing, backoff + response caching, prompt compression, and no idle Cloud Run min-instances. Never bypass billing controls (KB §Quotas).

---

## Submission note — GitHub vs GitLab

Our `origin` is GitHub (dev sync). The hackathon **submits on EPAM GitLab** (`git.garage.epam.com/[team-slug]`). Before the deadline, add a GitLab remote and mirror:
```bash
git remote add gitlab https://git.garage.epam.com/[team-slug]/[repo].git
git push gitlab master
```
