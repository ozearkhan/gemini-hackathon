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
    # Coordinator's routing model — bumped to the top reasoning model per explicit
    # request; note this trades away the original cheap-routing cost optimization.
    fast_model: str = field(
        default_factory=lambda: os.environ.get("PDLC_FAST_MODEL", "gemini-3.1-pro-preview")
    )
    # Model for reasoning-heavier phase subagents.
    model: str = field(
        default_factory=lambda: os.environ.get("PDLC_MODEL", "gemini-3.1-pro-preview")
    )
    # Model for research + gap analysis (Phase 1) and GCP design reasoning (Phase 2).
    # Confirmed best available reasoning-tier model for this project via
    # `client.models.list()` (see docs/deployment.md Step 0b) — 2026-08-30.
    reasoning_model: str = field(
        default_factory=lambda: os.environ.get("PDLC_REASONING_MODEL", "gemini-3.1-pro-preview")
    )
    # Defensive ceiling on tool calls per turn — prevents runaway subagent loops.
    max_tool_calls_per_turn: int = field(
        default_factory=lambda: int(os.environ.get("PDLC_MAX_TOOL_CALLS", "10"))
    )


settings = Settings()
