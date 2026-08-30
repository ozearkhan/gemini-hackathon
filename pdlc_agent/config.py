"""Central configuration for the PDLC agent.

Values are read from the environment so the same code runs locally and on the
remote/Cloud Run without edits. No secrets live here — only model names and
defensive limits.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    # Coordinator's routing model — gemini-3.7-flash was erroring on
    # GOOGLE_CLOUD_LOCATION=us-central1; gemini-2.5-pro is confirmed working
    # everywhere else in this project, so used consistently for all roles.
    fast_model: str = field(
        default_factory=lambda: os.environ.get("PDLC_FAST_MODEL", "gemini-2.5-pro")
    )
    # Model for reasoning-heavier phase subagents.
    model: str = field(
        default_factory=lambda: os.environ.get("PDLC_MODEL", "gemini-2.5-pro")
    )
    # Model for research + gap analysis (Phase 1) and GCP design reasoning (Phase 2).
    # Best available GA (non-preview) reasoning-tier model, confirmed available
    # directly in us-central1 — preview-tier models (e.g. gemini-3.1-pro-preview)
    # are avoided here since they can be region-restricted to "global" only and
    # are subject to change/removal without notice.
    reasoning_model: str = field(
        default_factory=lambda: os.environ.get("PDLC_REASONING_MODEL", "gemini-2.5-pro")
    )
    # Defensive ceiling on tool calls per turn — prevents runaway subagent loops.
    max_tool_calls_per_turn: int = field(
        default_factory=lambda: int(os.environ.get("PDLC_MAX_TOOL_CALLS", "10"))
    )


settings = Settings()
