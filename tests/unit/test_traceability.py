"""Phase 4 — JIRA task traceability (Data Engineering PDLC Playbook).

Encodes the playbook's Phase-4 rule as a deterministic check BEFORE implementation
(TDD): every leaf task must cite a requirement or ADR id.
"""

from pdlc_agent.tools.traceability import check_task_traceability


def test_all_tasks_traced_is_ok():
    tasks = [
        {"title": "Implement API client", "trace_ref": "REQ-1.3"},
        {"title": "fact_daily_price MERGE", "trace_ref": "ADR-002"},
    ]
    r = check_task_traceability(tasks)
    assert r["ok"] is True
    assert r["untraceable"] == []
    assert r["total"] == 2 and r["traced"] == 2


def test_missing_trace_ref_is_flagged():
    tasks = [
        {"title": "Implement API client", "trace_ref": "REQ-1.3"},
        {"title": "Orphan task"},
    ]
    r = check_task_traceability(tasks)
    assert r["ok"] is False
    assert "Orphan task" in r["untraceable"]


def test_blank_trace_ref_is_flagged():
    r = check_task_traceability([{"title": "Blank ref", "trace_ref": "  "}])
    assert r["ok"] is False
    assert r["untraceable"] == ["Blank ref"]


def test_empty_task_list_is_ok_but_zero():
    r = check_task_traceability([])
    assert r["ok"] is True
    assert r["total"] == 0
