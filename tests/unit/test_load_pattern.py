"""Phase 2.2 — load-pattern decision tree (Data Engineering PDLC Playbook).

These tests encode the decision tree BEFORE the implementation exists (TDD red).
The rules under test come directly from the playbook, so the expected values are
the "definition of done" for `decide_load_pattern`.
"""

from pdlc_agent.tools.load_pattern import decide_load_pattern


def test_immutable_fact_with_restatement_risk_is_append_merge_delta():
    """Stock tracker: daily close is an immutable fact, but corporate actions
    (splits/dividends) can restate history -> append-only + MERGE + Delta."""
    result = decide_load_pattern(
        is_mutable_state=False,
        has_delta_signal=False,
        dataset_is_small=True,
        restatement_risk=True,
    )
    assert result["load_pattern"] == "append_only"
    assert result["write_mode"] == "merge"
    assert result["storage_format"] == "delta"


def test_immutable_fact_no_restatement_is_pure_append_parquet():
    result = decide_load_pattern(
        is_mutable_state=False,
        has_delta_signal=False,
        dataset_is_small=True,
        restatement_risk=False,
    )
    assert result["load_pattern"] == "append_only"
    assert result["write_mode"] == "append"
    assert result["storage_format"] == "parquet"


def test_mutable_state_with_delta_signal_is_incremental_merge():
    result = decide_load_pattern(
        is_mutable_state=True,
        has_delta_signal=True,
        dataset_is_small=True,
        restatement_risk=False,
    )
    assert result["load_pattern"] == "incremental"
    assert result["write_mode"] == "merge"
    assert result["storage_format"] == "delta"


def test_mutable_state_no_delta_small_is_full_snapshot_diff():
    result = decide_load_pattern(
        is_mutable_state=True,
        has_delta_signal=False,
        dataset_is_small=True,
        restatement_risk=False,
    )
    assert result["load_pattern"] == "full_snapshot"
    assert result["write_mode"] == "overwrite"


def test_mutable_state_no_delta_large_is_flagged_not_viable():
    """Full-load diffing only works on small datasets; a large mutable source
    with no delta signal must be flagged, not silently accepted."""
    result = decide_load_pattern(
        is_mutable_state=True,
        has_delta_signal=False,
        dataset_is_small=False,
        restatement_risk=False,
    )
    assert result["warnings"], "large mutable source with no delta signal must warn"


def test_result_always_includes_rationale():
    result = decide_load_pattern(
        is_mutable_state=False,
        has_delta_signal=False,
        dataset_is_small=True,
        restatement_risk=True,
    )
    assert result["rationale"], "every decision must carry a traceable rationale"
