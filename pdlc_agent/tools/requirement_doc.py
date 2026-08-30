"""Deterministic persistence for the Requirement Analysis artifact (Phase 1.6).

Writes the agent-authored Markdown doc into the repo instead of an external SaaS
(Confluence) — same "repo artifact, not external tool" pattern already used for
the JIRA breakdown. Pure file I/O: deterministic and safe to unit test, unlike the
agent's actual research/reasoning output.

Note: on Cloud Run the container filesystem is ephemeral per revision; this tool
is fully functional for local dev, and is the seam a future upgrade (ADK Artifact
Service / GCS-backed) would slot into for production persistence.
"""

from __future__ import annotations

from pathlib import Path


def save_requirement_doc(
    slug: str, version: str, markdown_content: str, base_dir: str = "docs/requirements"
) -> dict[str, str]:
    """Persist a versioned Requirement Analysis doc to the repo.

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
