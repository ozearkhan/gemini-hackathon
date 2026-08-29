#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# org Hackathon — ADK Demo Agent Deployment Script
# ─────────────────────────────────────────────────────────────────────────────
# Usage:
#   ./deploy.sh local         — Run locally with ADK web UI
#   ./deploy.sh cloud_run     — Deploy to Cloud Run with A2A protocol
#   ./deploy.sh agent_engine  — Deploy to Vertex AI Agent Engine
#
# Prerequisites:
#   1. Copy .env.example to .env and set GOOGLE_CLOUD_PROJECT
#   2. Run: source .env && ./deploy.sh [mode]
#
# Run from this directory: repo root (contains the pdlc_agent/ package)
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
# ⚠️  SET THESE — either in .env or as environment variables before running
PROJECT="${GOOGLE_CLOUD_PROJECT:?'ERROR: Set GOOGLE_CLOUD_PROJECT in .env or environment'}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="${CLOUD_RUN_SERVICE_NAME:-org-hackathon-demo}"
AGENT_PACKAGE="pdlc_agent"

# Staging bucket for Agent Engine — ADK creates it as gs://[project-id]-staging by convention
# Override by setting STAGING_BUCKET in your .env if needed
STAGING_BUCKET="${STAGING_BUCKET:-gs://${PROJECT}-staging}"

# Gemini Enterprise Discovery Engine SA (Layer 1 project — shared, do NOT change)
# ⚠️  This SA belongs to the SHARED Layer 1 project — do NOT change this value
GE_SA="service-71784361107@gcp-sa-discoveryengine.iam.gserviceaccount.com"

# ── Mode selection ─────────────────────────────────────────────────────────────
MODE="${1:-help}"

case "$MODE" in

  # ── LOCAL DEV ──────────────────────────────────────────────────────────────
  local)
    echo "🚀 Starting ADK web UI at http://localhost:8000 ..."
    adk web "$AGENT_PACKAGE"
    ;;

  # ── CLOUD RUN + A2A ────────────────────────────────────────────────────────
  cloud_run)
    echo "🏗️  Deploying to Cloud Run (A2A enabled)..."
    echo "   Project:  $PROJECT"
    echo "   Region:   $REGION"
    echo "   Service:  $SERVICE_NAME"
    echo ""

    adk deploy cloud_run "$AGENT_PACKAGE" \
      --project="$PROJECT" \
      --region="$REGION" \
      --service_name="$SERVICE_NAME" \
      --a2a \
      -- --no-allow-unauthenticated

    echo ""
    echo "✅ Deployed! Granting Gemini Enterprise invoker access..."

    gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
      --project="$PROJECT" \
      --region="$REGION" \
      --member="serviceAccount:$GE_SA" \
      --role="roles/run.invoker"

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
      --project="$PROJECT" \
      --region="$REGION" \
      --format="value(status.url)" 2>/dev/null)

    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo "✅ Cloud Run A2A deployment complete!"
    echo ""
    echo "   Service URL:    $SERVICE_URL"
    echo "   A2A Endpoint:   $SERVICE_URL/a2a/$AGENT_PACKAGE"
    echo ""
    echo "   📋 Next step: Update 'url' in pdlc_agent/agent.json:"
    echo "      $SERVICE_URL/a2a/$AGENT_PACKAGE"
    echo ""
    echo "   📬 Then raise a Hackathon Support Ticket to register it in Gemini Enterprise"
    echo "      Subject: [Team Name] — Add A2A Agent to Gemini Enterprise App"
    echo "      Include: your updated agent.json content + service URL"
    echo ""
    echo "   🔍 Verify A2A is live:"
    TOKEN=$(gcloud auth print-identity-token 2>/dev/null || echo "TOKEN_ERROR")
    echo "      curl -X POST -H \"Authorization: Bearer \$TOKEN\" \\"
    echo "        -H \"Content-Type: application/json\" \\"
    echo "        \"$SERVICE_URL/a2a/$AGENT_PACKAGE\" \\"
    echo "        -d '{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"message/send\",\"params\":{\"message\":{\"messageId\":\"m1\",\"role\":\"user\",\"parts\":[{\"kind\":\"text\",\"text\":\"Hello!\"}]}}}'"
    echo "────────────────────────────────────────────────────────────────"
    ;;

  # ── AGENT ENGINE ──────────────────────────────────────────────────────────
  agent_engine)
    echo "🏗️  Deploying to Vertex AI Agent Engine..."
    echo "   Project: $PROJECT"
    echo "   Region:  $REGION"
    echo ""

    adk deploy agent_engine "$AGENT_PACKAGE" \
      --project="$PROJECT" \
      --region="$REGION"

    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo "✅ Agent Engine deployment complete!"
    echo ""
    echo "   Copy the Resource Name from the output above:"
    echo "   projects/[project-number]/locations/$REGION/reasoningEngines/[ID]"
    echo ""
    echo "   📬 Raise a Hackathon Support Ticket to register it in Gemini Enterprise"
    echo "      Subject: [Team Name] — Add Agent Engine Agent to Gemini Enterprise App"
    echo "      Include: the full Resource Name above"
    echo "────────────────────────────────────────────────────────────────"
    ;;

  # ── HELP ──────────────────────────────────────────────────────────────────
  *)
    echo "Usage: ./deploy.sh [local|cloud_run|agent_engine]"
    echo ""
    echo "  local         Run locally with ADK web UI (http://localhost:8000)"
    echo "  cloud_run     Deploy to Cloud Run with A2A protocol"
    echo "  agent_engine  Deploy to Vertex AI Agent Engine"
    echo ""
    echo "Prerequisites:"
    echo "  cp .env.example .env"
    echo "  # Edit .env and set GOOGLE_CLOUD_PROJECT=your-sandbox-project-id"
    echo "  source .env && ./deploy.sh [mode]"
    ;;
esac
