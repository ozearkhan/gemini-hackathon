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
    # Fast, low-cost model for the coordinator's routing decisions.
    fast_model: str = field(
        default_factory=lambda: os.environ.get("PDLC_FAST_MODEL", "gemini-2.5-flash")
    )
    # Model for reasoning-heavier phase subagents.
    model: str = field(
        default_factory=lambda: os.environ.get("PDLC_MODEL", "gemini-2.5-flash")
    )
    # Defensive ceiling on tool calls per turn — prevents runaway subagent loops.
    max_tool_calls_per_turn: int = field(
        default_factory=lambda: int(os.environ.get("PDLC_MAX_TOOL_CALLS", "10"))
    )


settings = Settings()
