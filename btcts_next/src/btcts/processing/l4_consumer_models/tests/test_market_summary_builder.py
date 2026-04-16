# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_market_summary_builder.py
# desc: Verify shared L4 market summary builder builds a reusable wording-free bundle.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (
    MarketSummaryBuildInput,
    build_market_summary,
)


def main() -> int:
    row = {
        "exchange": "bitflyer",
        "symbol_raw": "BTC_JPY",
        "market_uid": "bitflyer.spot.BTC_JPY",
        "source_series_id": "bf-sess-1:series:100",
        "collector_ts": "2026-04-06T12:00:00Z",
        "trust_state": "provisional",
        "continuity_state": "resynced",
        "interpretation_bucket": "observe_only",
        "interpretation_reason": "recent_resync",
        "semantic_observer_status": "healthy",
        "semantic_usage_summary": {
            "source_kind": "market_state_semantic_usage_summary",
            "contract_source": "l3_event_usage_policy",
            "meaning_version": "l3_event_usage_policy.v1alpha1",
            "observer_status": "healthy",
            "total_rows": 1,
            "active_event_count": 1,
            "mapped_event_count": 1,
            "unknown_event_count": 0,
            "event_family_distribution": {"wall": 1},
            "trust_bucket_distribution": {"trusted": 1},
            "interpretation_bucket_distribution": {"observe_only": 1},
            "consumer_distribution": {"health": 1},
        },
        "semantic_usage_contract_rows": [
            {
                "contract_source": "l3_event_usage_policy",
                "interpretation_bucket": "observe_only",
                "meaning_version": "l3_event_usage_policy.v1alpha1",
                "event_family": "wall",
                "usage_grade": "watch",
            }
        ],
    }
    diagnostics = {
        "source_kind": "market_state_preferred",
        "preferred_row_age_sec": 12.0,
        "preferred_row_freshness": "LIVE",
        "preferred_row_source_series_id": "bf-sess-1:series:100",
    }

    summary = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row=row,
            diagnostics=diagnostics,
        )
    )

    assert summary.summary_type == "market_summary"
    assert summary.exchange == "bitflyer"
    assert summary.symbol_raw == "BTC_JPY"
    assert summary.market_uid == "bitflyer.spot.BTC_JPY"
    assert summary.source_kind == "market_state_preferred"
    assert summary.source_series_id == "bf-sess-1:series:100"
    assert summary.event_ts == "2026-04-06T12:00:00Z"
    assert summary.age_sec == 12.0
    assert summary.freshness == "LIVE"
    assert summary.is_stale is False
    assert summary.trust_state == "provisional"
    assert summary.continuity_state == "resynced"
    assert summary.interpretation_bucket == "observe_only"
    assert summary.interpretation_reason == "recent_resync"
    assert summary.semantic_summary_source == "market_state_semantic_usage_summary"
    assert summary.semantic_contract_source == "l3_event_usage_policy"
    assert summary.semantic_meaning_version == "l3_event_usage_policy.v1alpha1"
    assert summary.semantic_observer_status == "healthy"
    assert summary.semantic_observer_present is True
    assert summary.semantic_usage_summary_present is True
    assert summary.semantic_contract_rows_present is True
    assert summary.semantic_contract_rows_count == 1
    assert summary.semantic_runtime_wiring_status == "wired"
    assert summary.semantic_total_rows == 1
    assert summary.semantic_active_event_count == 1
    assert summary.semantic_mapped_event_count == 1
    assert summary.semantic_unknown_event_count == 0
    assert summary.semantic_event_family_distribution == {"wall": 1}
    assert summary.semantic_trust_bucket_distribution == {"trusted": 1}
    assert summary.semantic_interpretation_bucket_distribution == {"observe_only": 1}
    assert summary.semantic_consumer_distribution == {"health": 1}
    assert summary.semantic_usage_contract_rows[0]["contract_source"] == "l3_event_usage_policy"
    assert summary.semantic_usage_contract_rows[0]["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert summary.semantic_usage_contract_rows[0]["event_family"] == "wall"
    assert summary.semantic_usage_contract_rows[0]["usage_grade"] == "watch"

    assert "fresh_source" in summary.notable_events
    assert "trust_degraded" in summary.notable_events
    assert "resync_recent" in summary.notable_events
    assert "review_required" in summary.notable_events

    assert summary.orderbook_active_event_contracts == []
    assert summary.orderbook_active_event_names == []
    assert summary.orderbook_active_event_count == 0
    assert summary.orderbook_summary_slots_present == []
    assert summary.orderbook_summary_slots_count == 0
    assert summary.orderbook_near_wall_present is False
    assert summary.orderbook_support_present is False
    assert summary.orderbook_resistance_present is False
    assert summary.orderbook_persistence_present is False
    assert summary.orderbook_wiring_status == "missing"
    assert summary.orderbook_contract_status_source == "orderbook_summary_inference"
    assert summary.orderbook_persistence_observable is False

    stale_missing = build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": "bitflyer",
                "symbol_raw": "BTC_JPY",
                "market_uid": "bitflyer.spot.BTC_JPY",
                "collector_ts": "2026-04-11T15:00:00Z",
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": "allow_structural_use",
                "orderbook_semantics_contract_status": "missing",
                "orderbook_persistence_observable": True,
                "orderbook_semantics_summary": {
                    "near_wall": {"side": "bid"},
                    "summary_slots_present": ["near_wall"],
                    "summary_slots_count": 1,
                    "active_event_count": 1,
                    "active_event_contracts": [
                        {
                            "event_name": "near_wall_continued",
                            "event_family": "wall",
                            "usage_grade": "strong",
                            "side": "bid",
                        }
                    ],
                },
            },
            diagnostics={
                "preferred_row_age_sec": 8.0,
                "preferred_row_freshness": "LIVE",
                "source_kind": "market_state_preferred",
            },
        )
    )
    assert stale_missing.semantic_summary_source == "unknown"
    assert stale_missing.semantic_contract_source == "unknown"
    assert stale_missing.semantic_meaning_version == "unknown"
    assert stale_missing.semantic_observer_status == "unknown"
    assert stale_missing.semantic_observer_present is False
    assert stale_missing.semantic_usage_summary_present is False
    assert stale_missing.semantic_contract_rows_present is False
    assert stale_missing.semantic_contract_rows_count == 0
    assert stale_missing.semantic_runtime_wiring_status == "missing"
    assert stale_missing.semantic_total_rows == 0
    assert stale_missing.semantic_active_event_count == 0
    assert stale_missing.semantic_mapped_event_count == 0
    assert stale_missing.semantic_unknown_event_count == 0
    assert stale_missing.semantic_event_family_distribution == {}
    assert stale_missing.semantic_trust_bucket_distribution == {}
    assert stale_missing.semantic_interpretation_bucket_distribution == {}
    assert stale_missing.semantic_consumer_distribution == {}
    assert stale_missing.orderbook_active_event_names == ["near_wall_continued"]
    assert stale_missing.orderbook_active_event_count == 1
    assert stale_missing.orderbook_summary_slots_present == ["near_wall"]
    assert stale_missing.orderbook_summary_slots_count == 1
    assert stale_missing.orderbook_near_wall_present is True
    assert stale_missing.orderbook_support_present is False
    assert stale_missing.orderbook_resistance_present is False
    assert stale_missing.orderbook_persistence_present is False
    assert stale_missing.orderbook_wiring_status == "partial"
    assert (
        stale_missing.orderbook_contract_status_source
        == "orderbook_summary_inference_overrode_missing"
    )
    assert stale_missing.orderbook_persistence_observable is True

    empty = build_market_summary(MarketSummaryBuildInput())
    assert empty.source_kind == "unknown"
    assert empty.freshness == "UNKNOWN"
    assert empty.is_stale is None
    assert empty.notable_events == []
    assert empty.alert_candidates == []

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())