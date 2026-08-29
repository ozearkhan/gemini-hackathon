"""Phase 1.3 — deterministic source-feasibility facts.

Verified facts for known stock-price providers so the requirements analyst grounds
its API claims (rate limits, delay, tiers, delta support) instead of hallucinating
them. Facts checked against the playbook's Phase 1.3 worked example.
"""

from __future__ import annotations

from typing import Any

_KNOWN_SOURCES: dict[str, dict[str, Any]] = {
    "alpha_vantage": {
        "auth": "api_key",
        "delay": "15-min delayed, daily bars",
        "daily_ceiling": 25,
        "per_minute_limit": 5,
        "supports_delta": False,
        "paid_only": False,
        "notes": "Broadest data breadth (50+ indicators); tight daily cap.",
    },
    "finnhub": {
        "auth": "api_key",
        "delay": "~20-min delayed",
        "daily_ceiling": None,  # capped per-minute, not per-day
        "per_minute_limit": 60,
        "supports_delta": False,
        "paid_only": False,
        "notes": "Most generous free rate limit; good for scheduled polling.",
    },
    "twelve_data": {
        "auth": "api_key",
        "delay": "up to 4-hr delay on free tier",
        "daily_ceiling": 800,
        "per_minute_limit": None,
        "supports_delta": False,
        "paid_only": False,
        "notes": "Best free daily volume; wide exchange coverage.",
    },
    "polygon": {
        "auth": "api_key",
        "delay": "real-time (paid)",
        "daily_ceiling": 0,
        "per_minute_limit": None,
        "supports_delta": False,
        "paid_only": True,
        "notes": "No usable free tier; production-grade but pay-from-day-one.",
    },
}


def evaluate_source_feasibility(source: str, expected_calls_per_day: int) -> dict[str, Any]:
    """Assess a known data source against expected daily call volume.

    Args:
        source: provider key, e.g. 'alpha_vantage', 'finnhub', 'twelve_data', 'polygon'.
        expected_calls_per_day: expected number of API calls per day for the pipeline.

    Returns:
        A dict with auth, delay, supports_delta, daily_ceiling, expected_calls_per_day,
        headroom, verdict (viable | tight | not_viable | paid_required | unknown), and notes.
    """
    key = source.strip().lower().replace(" ", "_").replace("-", "_")
    facts = _KNOWN_SOURCES.get(key)

    if facts is None:
        return {
            "source": source,
            "verdict": "unknown",
            "notes": (
                "Source not in the verified catalog. Check its docs for auth, rate "
                "limit, delta support, free-tier ceiling, delay, and TOS before use."
            ),
        }

    if facts["paid_only"]:
        verdict, headroom, ceiling = "paid_required", None, facts["daily_ceiling"]
    else:
        # Effective daily ceiling: explicit daily cap, else derived from the per-minute limit.
        if facts["daily_ceiling"] is not None:
            ceiling = facts["daily_ceiling"]
        else:
            ceiling = facts["per_minute_limit"] * 60 * 24
        headroom = ceiling - expected_calls_per_day
        if expected_calls_per_day > ceiling:
            verdict = "not_viable"
        elif expected_calls_per_day > ceiling * 0.8:
            verdict = "tight"
        else:
            verdict = "viable"

    return {
        "source": key,
        "auth": facts["auth"],
        "delay": facts["delay"],
        "supports_delta": facts["supports_delta"],
        "daily_ceiling": ceiling,
        "expected_calls_per_day": expected_calls_per_day,
        "headroom": headroom,
        "verdict": verdict,
        "notes": facts["notes"],
    }
