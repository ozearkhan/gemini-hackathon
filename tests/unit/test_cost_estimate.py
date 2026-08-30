"""Phase 2.6 — cost-estimate tool tests (deterministic ROM math)."""

from pdlc_agent.tools.cost_estimate import estimate_gcp_cost


def test_lightweight_pattern_is_cheap_for_small_volume():
    r = estimate_gcp_cost("lightweight", storage_gb=0.1, tib_scanned_per_month=0.001)
    assert r["total_monthly_usd"] < 5.0
    assert r["breakdown_usd_per_month"]["orchestrator"] == 0.0


def test_enterprise_composer_pattern_dominated_by_environment_cost():
    r = estimate_gcp_cost("enterprise_composer", storage_gb=0.1, tib_scanned_per_month=0.001)
    assert r["breakdown_usd_per_month"]["orchestrator"] >= 300.0
    assert r["total_monthly_usd"] >= 300.0


def test_heavier_pattern_costs_more_for_identical_small_workload():
    """Justifies the ADR trade-off: a heavier pattern is a deliberate deviation,
    not a free default, for a workload that doesn't need it."""
    light = estimate_gcp_cost("lightweight", storage_gb=0.1)
    heavy = estimate_gcp_cost("enterprise_composer", storage_gb=0.1)
    assert heavy["total_monthly_usd"] > light["total_monthly_usd"]


def test_unknown_pattern_is_flagged_not_guessed():
    r = estimate_gcp_cost("some_made_up_pattern", storage_gb=1.0)
    assert r["verdict"] == "unknown_pattern"
    assert "total_monthly_usd" not in r


def test_result_always_carries_a_basis_disclaimer():
    r = estimate_gcp_cost("lakehouse_dataflow", storage_gb=10.0)
    assert r["basis"]
