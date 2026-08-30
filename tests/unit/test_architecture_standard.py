"""Phase 2 — architecture standard grounding tool tests."""

from pdlc_agent.tools.architecture_standard import get_architecture_standard


def test_reads_the_real_committed_standard_doc():
    r = get_architecture_standard()
    assert r["error"] == ""
    assert "Data Platform Architecture Pattern" in r["content"]
    assert "When to deviate" in r["content"]


def test_missing_doc_is_flagged_not_fabricated(tmp_path):
    r = get_architecture_standard(path=str(tmp_path / "does-not-exist.md"))
    assert r["content"] == ""
    assert r["error"]
