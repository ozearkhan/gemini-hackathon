"""Phase 4 — JIRA traceability check.

Deterministic guard for the playbook's Phase-4 rule: every leaf task must cite a
requirement or ADR id. Keeps the JIRA planner honest instead of trusting the LLM
to self-enforce traceability.
"""

from __future__ import annotations

from typing import Any


def check_task_traceability(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Verify every task cites a requirement or ADR id.

    Args:
        tasks: list of task dicts, each with a 'title' and a 'trace_ref'
            (e.g. 'REQ-1.3' or 'ADR-002'). A missing or empty trace_ref fails.

    Returns:
        {ok, total, traced, untraceable}, where untraceable lists the titles of
        tasks that lack a trace.
    """
    untraceable: list[str] = []
    for task in tasks:
        ref = str(task.get("trace_ref", "")).strip()
        if not ref:
            untraceable.append(str(task.get("title", "<untitled task>")))

    return {
        "ok": len(untraceable) == 0,
        "total": len(tasks),
        "traced": len(tasks) - len(untraceable),
        "untraceable": untraceable,
    }
