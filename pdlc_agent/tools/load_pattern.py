"""Phase 2.2 — load-pattern decision tree.

Encodes the Data Engineering PDLC Playbook's highest-leverage HLD decision:
given the nature of the source data, what load pattern, write mode, and storage
format should the pipeline use? Deterministic so the answer is always traceable
back to a stated requirement (the whole point of an ADR).
"""

from __future__ import annotations

from typing import Any


def decide_load_pattern(
    is_mutable_state: bool,
    has_delta_signal: bool,
    dataset_is_small: bool,
    restatement_risk: bool,
) -> dict[str, Any]:
    """Decide the ingestion load pattern for a data source.

    Args:
        is_mutable_state: True if a record can change over time (e.g. a customer
            profile); False if it is an immutable point-in-time fact (e.g. a
            stock's closing price for a given day).
        has_delta_signal: True if the source API exposes a delta mechanism
            (updated_since, cursor, or changelog endpoint).
        dataset_is_small: True if the full dataset is small enough to pull and
            diff in one pass (10s-1000s of rows).
        restatement_risk: True if an otherwise-immutable fact can be
            retroactively restated (e.g. stock splits/dividends adjusting
            historical closes).

    Returns:
        A decision dict with load_pattern, write_mode, storage_format,
        rationale, and any warnings.
    """
    warnings: list[str] = []

    if is_mutable_state:
        if has_delta_signal:
            load_pattern = "incremental"
            write_mode = "merge"
            rationale = (
                "Mutable source exposes a delta signal -> pull only changed rows "
                "via watermark/cursor and MERGE (upsert) into the target."
            )
        elif dataset_is_small:
            load_pattern = "full_snapshot"
            write_mode = "overwrite"
            rationale = (
                "Mutable source with no delta signal but small volume -> full "
                "load each run and diff against the previous snapshot."
            )
        else:
            load_pattern = "full_snapshot"
            write_mode = "overwrite"
            rationale = (
                "Mutable source with no delta signal and large volume -> full "
                "load is the only option but does not scale."
            )
            warnings.append(
                "Large mutable source with no delta signal: full-load diffing "
                "does not scale. Seek a delta mechanism or a CDC feed before build."
            )
        # Mutable state needs update-in-place -> Delta/Iceberg for MERGE support.
        storage_format = "delta"
    else:
        # Immutable point-in-time fact: never re-pull or overwrite history.
        load_pattern = "append_only"
        if restatement_risk:
            write_mode = "merge"
            storage_format = "delta"
            rationale = (
                "Immutable fact, but subject to retroactive restatement (e.g. "
                "corporate actions) -> append daily, keep MERGE capability, use "
                "Delta for update-in-place on the fact table."
            )
        else:
            write_mode = "append"
            storage_format = "parquet"
            rationale = (
                "Pure immutable fact with no restatement risk -> append-only; "
                "Parquet is sufficient and cheaper to maintain than Delta."
            )

    return {
        "load_pattern": load_pattern,
        "write_mode": write_mode,
        "storage_format": storage_format,
        "rationale": rationale,
        "warnings": warnings,
    }
