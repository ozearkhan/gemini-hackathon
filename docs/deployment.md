# Deployment & GCP Runbook

> **Where these run:** every command here needs GCP auth, so it runs on the **remote** machine (per [.github/copilot-instructions.md](../.github/copilot-instructions.md) RULE 1). This workstation is authoring-only. Workflow: edit here → `git push` → pull on remote → run → paste output back.
>
> Replace `[PROJECT_ID]` with your EPAM Layer-2 sandbox project ID throughout.

**Our values** — Team `agenti-1711` (Agentic PDLC, Stream 2): `PROJECT_ID = hl2-gcpp-ccoe-ge-h-agenti-1711`, region `us-central1`.

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

# Cloud Build image pushes
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer" --condition=None
```

---

## Step 3 — Environment + local dev (on remote)

```bash
git pull origin master
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt -r demo_agent/requirements.txt
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
The script deploys with `--no-allow-unauthenticated` and grants the Layer 1 DE SA `roles/run.invoker`. Copy the printed **A2A endpoint** `https://[service-url]/a2a/demo_agent`. Verify:
```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://[service-url]/a2a/demo_agent -X POST -H "Content-Type: application/json" \
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
A2A Endpoint URL: https://[service-url]/a2a/demo_agent
Validated agent.json Content: { ... from demo_agent/agent.json ... }
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
