"""Phase 2 — persist the project-specific architecture doc as a repo artifact.

Same "repo artifact, not external tool" pattern as save_requirement_doc — the
deliverable a human reviews/approves is a real, versioned file, not just a chat
message that disappears.
"""

from __future__ import annotations

from pathlib import Path


def save_architecture_doc(
    slug: str, version: str, markdown_content: str, base_dir: str = "docs/architecture-decisions"
) -> dict[str, str]:
    """Persist a versioned project architecture doc to the repo.

    Args:
        slug: short kebab-case identifier for the request, e.g. 'stock-tracker'.
        version: doc version, e.g. 'v1.0' or 'v1.1'.
        markdown_content: the full Markdown document to write verbatim.
        base_dir: directory the doc is written under (relative to cwd).

    Returns:
        {path, slug, version} — the path the doc was written to.
    """
    directory = Path(base_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{slug}-{version}.md"
    path.write_text(markdown_content, encoding="utf-8")
    return {"path": str(path), "slug": slug, "version": version}
