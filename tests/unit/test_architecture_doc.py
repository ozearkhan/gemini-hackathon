"""Phase 2 — architecture doc persistence tests (deterministic file I/O)."""

from pdlc_agent.tools.architecture_doc import save_architecture_doc


def test_writes_versioned_doc_to_repo(tmp_path):
    result = save_architecture_doc(
        slug="stock-tracker", version="v1.0", markdown_content="# HLD\n...", base_dir=str(tmp_path)
    )
    written = tmp_path / "stock-tracker-v1.0.md"
    assert written.exists()
    assert written.read_text() == "# HLD\n..."
    assert result["path"] == str(written)


def test_returns_slug_and_version(tmp_path):
    result = save_architecture_doc(
        slug="other-request", version="v2.1", markdown_content="content", base_dir=str(tmp_path)
    )
    assert result["slug"] == "other-request"
    assert result["version"] == "v2.1"
