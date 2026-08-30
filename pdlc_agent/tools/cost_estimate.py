"""Phase 2.6 — GCP infra cost estimation (rough order of magnitude).

Per the playbook: "write the [cost] number down even when it's small — it's what
makes the ADR defensible." This is a deterministic ROM calculator with clearly
labeled, approximate unit costs (us-central1, list-price ballpark) — NOT a live
billing quote. For a precise figure, verify against Cloud Billing or delegate to
a research-grounded agent; this tool exists to make the trade-off VISIBLE when
comparing patterns (e.g. why a managed-orchestrator pattern costs far more than
a lightweight one for the same small workload), per the Well-Architected
Framework Cost Optimization pillar (Inform -> Optimize -> Operate).
"""

from __future__ import annotations

from typing import Any

# Rough, illustrative unit costs (USD, us-central1, on-demand list price ballpark).
# Always presented as an estimate — see `basis` in the returned dict.
_BIGQUERY_STORAGE_USD_PER_GB_MONTH = 0.02
_BIGQUERY_QUERY_USD_PER_TIB_SCANNED = 6.25
_SECRET_MANAGER_USD_PER_SECRET_VERSION_MONTH = 0.06
_CLOUD_SCHEDULER_USD_PER_JOB_MONTH = 0.10  # after the first 3 free jobs
_CLOUD_RUN_JOB_USD_PER_MONTH_TINY_DAILY = 0.50  # a few seconds/day, rounded up
_DATAFLOW_OR_DATAPROC_USD_PER_MONTH_SMALL = 150.00  # small recurring batch cluster/job
_COMPOSER_ENVIRONMENT_USD_PER_MONTH_MIN = 350.00  # smallest managed Airflow environment

_KNOWN_PATTERNS = {
    "lightweight",  # Cloud Run Jobs + Cloud Scheduler + BigQuery (Pattern D)
    "lakehouse_dataflow",  # Dataflow + GCS + BigLake/BigQuery ext tables (Pattern B)
    "lakehouse_dataproc",  # Dataproc + GCS/BigQuery, Spark-scale merges (Pattern C)
    "enterprise_composer",  # Managed Airflow (Composer/MSAA) + Dataform + BigQuery (Pattern A)
}


def estimate_gcp_cost(
    pattern: str, storage_gb: float, tib_scanned_per_month: float = 0.01
) -> dict[str, Any]:
    """Rough monthly GCP cost estimate for a candidate architecture pattern.

    Args:
        pattern: one of 'lightweight', 'lakehouse_dataflow', 'lakehouse_dataproc',
            'enterprise_composer'.
        storage_gb: expected BigQuery storage volume in GB.
        tib_scanned_per_month: expected data scanned by queries per month, in TiB.

    Returns:
        A dict with a cost breakdown, total_monthly_usd, and a `basis` disclaimer.
    """
    key = pattern.strip().lower().replace(" ", "_").replace("-", "_")
    if key not in _KNOWN_PATTERNS:
        return {
            "pattern": pattern,
            "verdict": "unknown_pattern",
            "notes": f"Unrecognized pattern. Known patterns: {sorted(_KNOWN_PATTERNS)}.",
        }

    storage_cost = round(storage_gb * _BIGQUERY_STORAGE_USD_PER_GB_MONTH, 2)
    query_cost = round(tib_scanned_per_month * _BIGQUERY_QUERY_USD_PER_TIB_SCANNED, 2)
    secret_cost = _SECRET_MANAGER_USD_PER_SECRET_VERSION_MONTH

    breakdown = {"bigquery_storage": storage_cost, "bigquery_queries": query_cost, "secrets": secret_cost}

    if key == "lightweight":
        breakdown["compute"] = _CLOUD_RUN_JOB_USD_PER_MONTH_TINY_DAILY
        breakdown["scheduler"] = _CLOUD_SCHEDULER_USD_PER_JOB_MONTH
        breakdown["orchestrator"] = 0.0
    elif key in ("lakehouse_dataflow", "lakehouse_dataproc"):
        breakdown["compute"] = _DATAFLOW_OR_DATAPROC_USD_PER_MONTH_SMALL
        breakdown["scheduler"] = _CLOUD_SCHEDULER_USD_PER_JOB_MONTH
        breakdown["orchestrator"] = 0.0
    else:  # enterprise_composer
        breakdown["compute"] = _CLOUD_RUN_JOB_USD_PER_MONTH_TINY_DAILY
        breakdown["scheduler"] = 0.0
        breakdown["orchestrator"] = _COMPOSER_ENVIRONMENT_USD_PER_MONTH_MIN

    total = round(sum(breakdown.values()), 2)

    return {
        "pattern": key,
        "breakdown_usd_per_month": breakdown,
        "total_monthly_usd": total,
        "basis": (
            "Rough order-of-magnitude estimate using approximate us-central1 "
            "on-demand list prices, not a Cloud Billing quote. Verify precisely "
            "via Cloud Billing reports (or a grounded research query) before "
            "committing to a budget figure."
        ),
    }
