"""Phase 1.3 — source-feasibility facts (Data Engineering PDLC Playbook).

Encodes the decision as a deterministic tool BEFORE implementation (TDD). The
verified provider facts come from the playbook's Phase 1.3 worked example, so the
expected values here are the definition of done for `evaluate_source_feasibility`.
"""

from pdlc_agent.tools.feasibility import evaluate_source_feasibility


def test_alpha_vantage_low_volume_is_viable():
    r = evaluate_source_feasibility("alpha_vantage", expected_calls_per_day=10)
    assert r["verdict"] == "viable"
    assert r["daily_ceiling"] == 25


def test_alpha_vantage_over_daily_cap_not_viable():
    r = evaluate_source_feasibility("alpha_vantage", expected_calls_per_day=30)
    assert r["verdict"] == "not_viable"


def test_finnhub_daily_tracker_viable_despite_per_minute_limit():
    """Finnhub caps per-minute, not per-day — ample for a daily tracker."""
    r = evaluate_source_feasibility("finnhub", expected_calls_per_day=10)
    assert r["verdict"] == "viable"


def test_polygon_requires_paid_tier():
    r = evaluate_source_feasibility("polygon", expected_calls_per_day=10)
    assert r["verdict"] == "paid_required"


def test_unknown_source_is_flagged_not_guessed():
    r = evaluate_source_feasibility("some_random_api", expected_calls_per_day=10)
    assert r["verdict"] == "unknown"
    assert r["notes"], "unknown source must carry guidance, not a fabricated verdict"


def test_result_carries_auth_and_delay_facts():
    r = evaluate_source_feasibility("finnhub", expected_calls_per_day=10)
    assert r["auth"] and r["delay"]
