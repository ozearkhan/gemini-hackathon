# EPAM Hackathon — ADK Demo Agent

A minimal, production-ready **Google ADK agent** that serves as a reference example for Stream 2 participants. Clone this repo, set your project ID, and deploy in minutes.

Deployable to:
- **Cloud Run** with A2A (Agent-to-Agent) protocol — for Gemini Enterprise agent integration
- **Vertex AI Agent Engine** — for serverless managed agent hosting

---

## Folder Structure

```
demo_agent/                     ← Run all commands from this folder
├── README.md                   ← This file
├── .env.example                ← Copy to .env and fill in your values
├── deploy.sh                   ← ./deploy.sh [local|cloud_run|agent_engine]
├── requirements.txt            ← (top-level, informational only)
└── demo_agent/                 ← Agent package (Python)
    ├── __init__.py             ← Package marker
    ├── agent.py                ← Root agent definition (root_agent variable)
    ├── agent.json              ← A2A agent card (update url before submitting ticket)
    └── requirements.txt        ← ✅ Installed in container — MUST be here, not top-level
```

> **⚠️ Key Rule:** `requirements.txt` and `agent.json` MUST be **inside the agent package folder** (`demo_agent/demo_agent/`), NOT at the top level. ADK copies only the package subfolder into the container.

---

## Step 0 — Set Up Your Team Configuration

```bash
# Clone this repo
git clone git@eu.git.epam.com:gcpp-ccoe/global-epam-ge-hackathon-2026/demo_agent.git
cd demo_agent

# Copy the config template
cp .env.example .env
```

Edit `.env` and set your team's GCP sandbox project ID:

```bash
# Your GCP sandbox project ID — provided by the Hackathon support team
GOOGLE_CLOUD_PROJECT=your-sandbox-project-id

# Region — keep us-central1
GOOGLE_CLOUD_LOCATION=us-central1
```

---

## Step 1 — Authenticate

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project $GOOGLE_CLOUD_PROJECT
```

---

## Local Development

```bash
source .env && ./deploy.sh local
# Opens ADK web UI at http://localhost:8000
```

---

## Deployment: Option A — Cloud Run with A2A

Deploys the agent as a **Cloud Run service** with the A2A endpoint at `/a2a/demo_agent`.

```bash
source .env && ./deploy.sh cloud_run
```

This script automatically:
1. Builds and deploys the container to Cloud Run
2. Grants the Gemini Enterprise Discovery Engine SA `roles/run.invoker`

**Verify A2A is live:**
```bash
TOKEN=$(gcloud auth print-identity-token)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://[your-service-url]/a2a/demo_agent" \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"messageId":"m1","role":"user","parts":[{"kind":"text","text":"Hello!"}]}}}'
```

### 🔴 Register in Gemini Enterprise — Submit a Support Ticket (A2A)

> **Teams do not have access to add agents to the Gemini Enterprise App directly.**

1. Open `demo_agent/agent.json` and update the `url` field to your Cloud Run service URL:
   ```
   https://[your-service-url]/a2a/demo_agent
   ```
2. **Raise a Hackathon Support Ticket** with:
   - **Subject:** `[Team Name] — Add A2A Agent to Gemini Enterprise App`
   - **Include:** your updated `agent.json` content + Cloud Run service URL

---

## Deployment: Option B — Vertex AI Agent Engine

```bash
source .env && ./deploy.sh agent_engine
```

Copy the **Resource Name** from the output:
```
projects/[project-number]/locations/us-central1/reasoningEngines/[ID]
```

### 🔴 Register in Gemini Enterprise — Submit a Support Ticket (Agent Engine)

> **Teams do not have access to add agents to the Gemini Enterprise App directly.**

**Raise a Hackathon Support Ticket** with:
- **Subject:** `[Team Name] — Add Agent Engine Agent to Gemini Enterprise App`
- **Include:** the full Resource Name above

---

## agent.json — A2A Agent Card Requirements

The Gemini Enterprise App validates the agent card strictly. Ensure these fields are correct:

| Field | Required Value | Common Error |
|---|---|---|
| `protocolVersion` | `"1.0"` | "Missing required field: protocolVersion" |
| `defaultInputModes` | `["text/plain"]` | "Value 'text' is invalid — must be MIME type" |
| `defaultOutputModes` | `["text/plain"]` | Same MIME type error |
| `skills[].inputModes` | `["text/plain"]` | Same MIME type error |
| `url` | `https://[service-url]/a2a/demo_agent` | Must include `/a2a/{name}` suffix |

---

## Extending the Agent

Edit `demo_agent/agent.py` to add tools:

```python
from google.adk.tools import tool

@tool
def my_custom_tool(query: str) -> dict:
    """Call your API or data source here."""
    return {"result": "..."}

root_agent = Agent(
    ...
    tools=[my_custom_tool],
)
```

Add packages to `demo_agent/requirements.txt` (inside the package folder).

---

## Environment Variables

| Variable | Required | Description | Default |
|---|---|---|---|
| `GOOGLE_CLOUD_PROJECT` | ✅ Yes | Your GCP sandbox project ID | _(must be set)_ |
| `GOOGLE_CLOUD_LOCATION` | No | GCP region | `us-central1` |
| `CLOUD_RUN_SERVICE_NAME` | No | Cloud Run service name | `epam-hackathon-demo` |
| `STAGING_BUCKET` | No | Agent Engine staging bucket | `gs://[PROJECT]-staging` |
