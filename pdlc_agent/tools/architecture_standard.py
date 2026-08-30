"""Phase 2 — reference the org's real architecture standard, don't hallucinate it.

Deterministic file read: the architecture_agent MUST call this before proposing
a pattern, so its recommendation is grounded in an actual, versioned, reviewable
document (the repo's equivalent of an org's internal Confluence standard) rather
than invented from memory.
"""

from __future__ import annotations

from pathlib import Path

_DEFAULT_STANDARD_PATH = "docs/architecture-standard-gcp.md"


def get_architecture_standard(path: str = _DEFAULT_STANDARD_PATH) -> dict[str, str]:
    """Read the approved default architecture standard.

    Args:
        path: repo-relative path to the standard doc.

    Returns:
        {path, content} — content is empty and an error note is set if the file
        is missing (never silently fabricated).
    """
    file_path = Path(path)
    if not file_path.exists():
        return {"path": path, "content": "", "error": f"Standard doc not found at {path}."}
    return {"path": path, "content": file_path.read_text(encoding="utf-8"), "error": ""}
