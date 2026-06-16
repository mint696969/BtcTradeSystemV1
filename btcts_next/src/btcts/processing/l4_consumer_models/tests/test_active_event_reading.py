# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_active_event_reading.py
# desc: Verify wording-free active-event compact rows for Health / WarRoom L4 bundles.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    ACTIVE_EVENT_STABLE_KEYS,
    HealthDigestBuildInput,
    MarketSummaryBuildInput,
    build_active_event_compact_rows,
    build_health_digest,
    build_market_summary,
)


def main() -> int:
    raw_rows = [
        {
            "contract_source": "l3_event_usage_policy",
            "event_name": "near_wall_continued",
            "event_family": "wall",
            "meaning_version": "l3_event_usage_policy.v1alpha1",
            "usage_grade": "strong",
            "interpretation_bucket": "allow_structural_use",
            "trust_bucket": "trusted",
            "consumer_allowed": ["ui", "ai"],
            "actionability": "review",
            "forecast_horizon_hint": "short",
            "half_life_sec": "30",
            "invalidates_on": ["series_boundary"],
            "evidence_refs": ["l2:book_depth"],
            "side": "bid",
            "confidence": 0.88,
        },
        {
            "event_family": "ignored_without_event_name",
        },
    ]

    expected = [
        {
            "contract_source": "l3_event_usage_policy",
            "event_name": "near_wall_continued",
            "event_family": "wall",
            "meaning_version": "l3_event_usage_policy.v1alpha1",
            "usage_grade": "strong",
            "interpretation_bucket": "allow_structural_use",
            "trust_bucket": "trusted",
            "actionability": "review",
            "forecast_horizon_hint": "short",
            "half_life_sec": 30,
            "side": "bid",
        }
    ]

    compact_rows = build_active_event_compact_rows(raw_rows)
    assert compact_rows == expected
    assert tuple(compact_rows[0].keys()) == ACTIVE_EVENT_STABLE_KEYS

    summary = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol_raw": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-05-16T12:00:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": "allow_structural_use",
                "orderbook_semantics_summary": {
                    "summary_slots_present": ["near_wall"],
                    "active_event_count": 1,
                    "active_event_contracts": raw_rows,
                },
            },
            diagnostics={
                "source_kind": "market_state_preferred",
                "preferred_row_age_sec": 4.0,
                "preferred_row_freshness": "LIVE",
            },
        )
    )
    assert summary.orderbook_active_event_compact_rows == expected

    digest = build_health_digest(
        HealthDigestBuildInput(
            market_diagnostics={
                "preferred_row_freshness": "LIVE",
            },
            orderbook_runtime_summary={
                "wiring_status": "partial",
                "active_event_count": 1,
                "active_event_names": ["near_wall_continued"],
                "active_event_contracts": raw_rows,
            },
        )
    )
    assert digest.orderbook_runtime["active_event_compact_rows"] == expected

    empty = build_active_event_compact_rows(None)
    assert empty == []

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())