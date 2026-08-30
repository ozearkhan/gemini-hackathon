"""Deterministic persistence for the Requirement Analysis artifact (Phase 1.6).

Writes the agent-authored Markdown doc to the repo instead of an external SaaS
(Confluence) — same "repo artifact, not external tool" pattern used for JIRA.
Note: on Cloud Run the container filesystem is ephemeral per revision/instance;
this tool is fully functional for local dev and is the seam a future upgrade
(ADK Artifact Service / GCS-backed) would slot into for production persistence.
"""

from tests.unit.test_requirement_doc import *  # noqa - placeholder removed below
