"""Tests for the deterministic requirement-doc persistence tool (pure file I/O)."""

from pdlc_agent.tools.requirement_doc import save_requirement_doc


def test_writes_file_with_slug_and_version_in_name(tmp_path):
    result = save_requirement_doc(
        slug="stock-tracker",
        version="v1.0",
        markdown_content="# Requirement Analysis\n...",
        base_dir=str(tmp_path / "requirements"),
    )
    written = tmp_path / "requirements" / "stock-tracker-v1.0.md"
    assert written.exists()
    assert written.read_text(encoding="utf-8") == "# Requirement Analysis\n..."
    assert result["path"] == str(written)


def test_creates_base_dir_if_missing(tmp_path):
    base_dir = tmp_path / "nested" / "requirements"
    save_requirement_doc(slug="x", version="v1.0", markdown_content="doc", base_dir=str(base_dir))
    assert base_dir.exists()


def test_v1_1_does_not_overwrite_v1_0():
    """Versioning rule: never silently edit a prior version — each version is its own file."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        save_requirement_doc("stock-tracker", "v1.0", "original", base_dir=tmp)
        save_requirement_doc("stock-tracker", "v1.1", "updated", base_dir=tmp)
        from pathlib import Path

        assert (Path(tmp) / "stock-tracker-v1.0.md").read_text() == "original"
        assert (Path(tmp) / "stock-tracker-v1.1.md").read_text() == "updated"
