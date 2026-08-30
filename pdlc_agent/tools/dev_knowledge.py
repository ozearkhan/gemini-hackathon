"""Google Developer Knowledge MCP — grounding in Google's own current docs.

Wired into architecture_agent, iac_agent, and jira_planner_agent only — NOT
requirements_analyst_agent, which needs third-party vendor/API research that
Developer Knowledge (Google's own docs corpus) can't cover; that agent keeps
using ADK's built-in `google_search` via requirements_researcher_agent.

Auth: this is a regular googleapis.com endpoint, not our own Cloud Run service,
so it needs an OAuth2 access token via Application Default Credentials — not an
identity token audience-scoped to a Cloud Run URL. Credentials are resolved
lazily (only when a tool call actually happens) so importing this module never
requires ADC to be present, keeping local unit tests/imports safe without
credentials. Tokens expire in ~1h, so `header_provider` refreshes per call
rather than building a static headers dict once.

A factory (not a shared singleton) — same reasoning as researcher_agent.py:
each agent that wires this tool gets its own McpToolset/session instance.
"""

from __future__ import annotations

from typing import Any

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

DEV_KNOWLEDGE_MCP_URL = "https://developerknowledge.googleapis.com/mcp"

_credentials: Any = None


def _bearer_header(_ctx: Any) -> dict[str, str]:
    global _credentials
    import google.auth
    import google.auth.transport.requests

    if _credentials is None:
        _credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
    _credentials.refresh(google.auth.transport.requests.Request())
    return {"Authorization": f"Bearer {_credentials.token}"}


def build_dev_knowledge_toolset() -> McpToolset:
    """Build a fresh Developer Knowledge MCP toolset instance."""
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=DEV_KNOWLEDGE_MCP_URL),
        header_provider=_bearer_header,
    )
