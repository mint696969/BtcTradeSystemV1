# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_semantic_usage.py
# desc: Minimal contract test for Health semantic usage observer rows.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.health_data_service import (
    build_layer3_orderbook_runtime_summary,
    build_layer3_runtime_contract_summary,
    build_layer3_semantic_usage_rows,
    build_layer3_semantic_usage_summary,
)
from btcts.market_engine.config import MarketEngineConfig
from btcts.market_engine.market_state.projector import MarketStateProjector
from btcts.market_engine.types import (
    BoundaryReason,
    MarketUID,
    SeriesID,
    StreamSessionID,
    TrustState,
)
from btcts.processing.l3_market_semantics.continuity.models.book_state import BookState
from btcts.processing.l3_market_semantics.continuity.models.series_state import SeriesState
from btcts.processing.l3_market_semantics.event_usage_policy import (
    build_event_usage_contract_rows,
)


def main() -> int:
    rows = build_layer3_semantic_usage_rows(
        interpretation_bucket="observe_only",
    )

    by_family = {str(row["event_family"]): row for row in rows}

    assert all(row["source_kind"] == "layer3_semantic_usage_observer" for row in rows)
    assert all(row["contract_source"] == "l3_event_usage_policy" for row in rows)
    assert all(row["interpretation_bucket"] == "observe_only" for row in rows)

    live_rows = build_layer3_semantic_usage_rows(
        interpretation_bucket="observe_only",
        market_latest={
            "semantic_usage_contract_rows": [
                {
                    "contract_source": "l3_event_usage_policy",
                    "interpretation_bucket": "observe_only",
                    "event_family": "wall",
                    "usage_grade": "watch",
                },
                {
                    "contract_source": "l3_event_usage_policy",
                    "interpretation_bucket": "observe_only",
                    "event_family": "absorption",
                    "usage_grade": "tentative",
                },
            ]
        },
    )
    assert [row["source_kind"] for row in live_rows] == [
        "market_state_semantic_usage_contract_rows",
        "market_state_semantic_usage_contract_rows",
    ]
    assert [row["event_family"] for row in live_rows] == ["wall", "absorption"]
    assert [row["usage_grade"] for row in live_rows] == ["watch", "tentative"]
    assert [row["meaning_version"] for row in live_rows] == [
        "l3_event_usage_policy.v1alpha1",
        "l3_event_usage_policy.v1alpha1",
    ]

    assert by_family["pressure"]["usage_grade"] == "watch_weak"
    assert by_family["wall"]["usage_grade"] == "watch"
    assert by_family["support_resistance"]["usage_grade"] == "watch"
    assert by_family["sweep"]["usage_grade"] == "tentative"
    assert by_family["absorption"]["usage_grade"] == "tentative"

    invalid_rows = build_layer3_semantic_usage_rows(
        interpretation_bucket="reanchor_required",
    )
    assert all(row["contract_source"] == "l3_event_usage_policy" for row in invalid_rows)
    assert all(row["usage_grade"] == "invalid" for row in invalid_rows)

    contract_rows = build_event_usage_contract_rows(
        interpretation_bucket="observe_only",
    )
    assert any(
        row["event_family"] == "wall" and row["usage_grade"] == "watch"
        for row in contract_rows
    )
    assert any(
        row["event_family"] == "sweep" and row["usage_grade"] == "tentative"
        for row in contract_rows
    )

    summary = build_layer3_semantic_usage_summary(
        interpretation_bucket="observe_only",
    )
    assert summary["contract_source"] == "l3_event_usage_policy"
    assert summary["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert summary["observer_status"] == "caution"
    assert summary["strong_count"] == 0
    assert summary["watch_count"] >= 1
    assert summary["watch_weak_count"] == 1
    assert summary["tentative_count"] == 2
    assert summary["invalid_count"] == 0

    broken_summary = build_layer3_semantic_usage_summary(
        interpretation_bucket="reanchor_required",
    )
    assert broken_summary["observer_status"] == "broken"
    assert broken_summary["invalid_count"] == broken_summary["total_rows"]

    live_summary = build_layer3_semantic_usage_summary(
        interpretation_bucket="observe_only",
        market_latest={
            "semantic_observer_status": "healthy",
            "semantic_usage_summary": {
                "contract_source": "l3_event_usage_policy",
                "observer_status": "healthy",
                "total_rows": 8,
                "active_event_count": 2,
                "mapped_event_count": 1,
                "unknown_event_count": 1,
                "event_family_distribution": {
                    "support_resistance": 1,
                    "unknown": 1,
                },
                "trust_bucket_distribution": {"degraded": 1, "trusted": 1},
                "interpretation_bucket_distribution": {
                    "allow_structural_use": 1,
                    "observe_only": 1,
                },
                "consumer_distribution": {
                    "ai": 2,
                    "alert": 2,
                    "execution": 1,
                    "strategy": 1,
                    "ui": 2,
                },
                "strong_count": 8,
                "watch_count": 0,
                "watch_weak_count": 0,
                "tentative_count": 0,
                "invalid_count": 0,
                "unknown_count": 0,
            },
        },
    )
    assert live_summary["observer_status"] == "healthy"
    assert live_summary["contract_source"] == "l3_event_usage_policy"
    assert live_summary["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert live_summary["event_family_distribution"] == {
        "support_resistance": 1,
        "unknown": 1,
    }
    assert live_summary["trust_bucket_distribution"] == {"degraded": 1, "trusted": 1}
    assert live_summary["interpretation_bucket_distribution"] == {
        "allow_structural_use": 1,
        "observe_only": 1,
    }
    assert live_summary["consumer_distribution"] == {
        "ai": 2,
        "alert": 2,
        "execution": 1,
        "strategy": 1,
        "ui": 2,
    }
    assert live_summary["strong_count"] == 8
    assert live_summary["invalid_count"] == 0

    projector = MarketStateProjector()
    projected_record = projector.project(
        cfg=MarketEngineConfig(
            exchange="bitflyer",
            symbol_raw="BTC_JPY",
            instrument_id="bitflyer.spot.BTC_JPY",
            market_uid="bitflyer.spot.BTC_JPY",
            profile_name="bitflyer",
        ),
        book_state=BookState(
            best_bid=100.0,
            best_ask=101.0,
            spread=1.0,
            mid_price=100.5,
            continuity_state="continuous",
            collector_ts="2026-04-11T15:00:00Z",
            exchange_ts="2026-04-11T15:00:00Z",
            trust_state=TrustState.TRUSTED,
            boundary_reason=BoundaryReason.NONE,
            interpretation_bucket="observe_only",
            interpretation_reason="continuity_caution",
            interpretation_policy={},
        ),
        series_state=SeriesState(
            market_uid=MarketUID("bitflyer.spot.BTC_JPY"),
            stream_session_id=StreamSessionID("bf-sess-1"),
            series_id=SeriesID("bf-sess-1:series:1"),
            anchor_event_id="bf-anchor-1",
            start_sequence=1,
            end_sequence=2,
            boundary_reason=BoundaryReason.NONE,
            trust_state=TrustState.TRUSTED,
        ),
        zone_metadata={"mode": "hybrid"},
        orderbook_semantics_contract_status="partial",
        orderbook_semantics_summary={
            "near_wall": {"side": "bid"},
            "support": None,
            "resistance": None,
            "persistence": None,
            "summary_slots_present": ["near_wall"],
            "summary_slots_count": 1,
            "active_event_count": 2,
            "active_event_names": [
                "support_candidate",
                "unknown_event_name",
            ],
            "active_event_contracts": [
                {
                    "contract_source": "l3_event_usage_policy",
                    "event_name": "support_candidate",
                    "event_family": "support_resistance",
                    "usage_grade": "watch",
                    "interpretation_bucket": "observe_only",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "confidence": 0.55,
                    "trust_bucket": "degraded",
                    "consumer_allowed": ["ui", "alert", "ai"],
                    "actionability": "review",
                    "forecast_horizon_hint": "short",
                    "half_life_sec": 30,
                    "invalidates_on": ["series_boundary", "reanchor_required"],
                    "evidence_refs": [],
                    "side": "bid",
                },
                {
                    "contract_source": "l3_event_usage_policy",
                    "event_name": "unknown_event_name",
                    "event_family": "unknown",
                    "usage_grade": "unknown",
                    "interpretation_bucket": "observe_only",
                    "meaning_version": "l3_event_usage_policy.v1alpha1",
                    "confidence": 0.10,
                    "trust_bucket": "trusted",
                    "consumer_allowed": ["ui", "alert", "ai"],
                    "actionability": "review",
                    "forecast_horizon_hint": "unknown",
                    "half_life_sec": None,
                    "invalidates_on": ["series_boundary", "reanchor_required"],
                    "evidence_refs": [],
                    "side": None,
                },
            ],
        },
        orderbook_persistence_observable=False,
    )

    projected_live_rows = build_layer3_semantic_usage_rows(
        interpretation_bucket="observe_only",
        market_latest={
            "semantic_usage_contract_rows": projected_record.semantic_usage_contract_rows,
        },
    )
    assert all(
        row["source_kind"] == "market_state_semantic_usage_contract_rows"
        for row in projected_live_rows
    )
    assert all(
        row["meaning_version"] == "l3_event_usage_policy.v1alpha1"
        for row in projected_live_rows
    )

    projected_live_summary = build_layer3_semantic_usage_summary(
        interpretation_bucket="observe_only",
        market_latest={
            "semantic_observer_status": projected_record.semantic_observer_status,
            "semantic_usage_summary": projected_record.semantic_usage_summary,
        },
    )
    assert projected_live_summary["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert projected_live_summary["active_event_count"] == 2
    assert projected_live_summary["mapped_event_count"] == 1
    assert projected_live_summary["unknown_event_count"] == 1
    assert projected_live_summary["event_family_distribution"] == {
        "support_resistance": 1,
        "unknown": 1,
    }
    assert projected_live_summary["trust_bucket_distribution"] == {
        "degraded": 1,
        "trusted": 1,
    }
    assert projected_live_summary["interpretation_bucket_distribution"] == {
        "observe_only": 2,
    }
    assert projected_live_summary["consumer_distribution"] == {
        "ai": 2,
        "alert": 2,
        "ui": 2,
    }

    wired_contract = build_layer3_runtime_contract_summary(
        market_latest={
            "semantic_observer_status": "healthy",
            "semantic_usage_summary": {"observer_status": "healthy"},
            "source_series_id": "bf-sess-1:series:100",
        },
        market_diag={"preferred_row_freshness": "LIVE"},
        semantic_usage_summary={
            "source_kind": "market_state_semantic_usage_summary",
        },
    )
    assert wired_contract["wiring_status"] == "wired"
    assert wired_contract["observer_present"] is True
    assert wired_contract["usage_summary_present"] is True
    assert wired_contract["source_series_present"] is True

    fallback_contract = build_layer3_runtime_contract_summary(
        market_latest={},
        market_diag={"preferred_row_freshness": "QUIET"},
        semantic_usage_summary={
            "source_kind": "layer3_semantic_usage_summary",
        },
    )
    assert fallback_contract["wiring_status"] == "fallback"

    missing_contract = build_layer3_runtime_contract_summary(
        market_latest={},
        market_diag={"preferred_row_freshness": "UNKNOWN"},
        semantic_usage_summary={},
    )
    assert missing_contract["wiring_status"] == "missing"

    missing_orderbook = build_layer3_orderbook_runtime_summary(
        market_latest={
            "orderbook_semantics_contract_status": "missing",
            "orderbook_semantics_summary": {
                "near_wall": None,
                "support": None,
                "resistance": None,
                "persistence": None,
            },
            "orderbook_persistence_observable": False,
        },
        market_diag={"preferred_row_freshness": "UNKNOWN"},
    )
    assert missing_orderbook["wiring_status"] == "missing"
    assert missing_orderbook["contract_status_source"] == "market_state_orderbook_contract_status"
    assert missing_orderbook["freshness"] == "UNKNOWN"
    assert missing_orderbook["persistence_observable"] is False

    stale_missing_orderbook = build_layer3_orderbook_runtime_summary(
        market_latest={
            "orderbook_semantics_contract_status": "missing",
            "orderbook_semantics_summary": {
                "near_wall": {"side": "bid"},
                "support": None,
                "resistance": None,
                "persistence": None,
                "summary_slots_present": ["near_wall"],
                "summary_slots_count": 1,
                "active_event_count": 1,
                "active_event_names": ["near_wall_continued"],
                "active_event_contracts": [
                    {
                        "event_name": "near_wall_continued",
                        "event_family": "wall",
                        "usage_grade": "watch",
                        "side": "bid",
                    }
                ],
            },
            "orderbook_persistence_observable": True,
        },
        market_diag={"preferred_row_freshness": "QUIET"},
    )
    assert stale_missing_orderbook["wiring_status"] == "partial"
    assert (
        stale_missing_orderbook["contract_status_source"]
        == "orderbook_summary_inference_overrode_missing"
    )
    assert stale_missing_orderbook["summary_slots_present"] == ["near_wall"]
    assert stale_missing_orderbook["active_event_count"] == 1

    partial_orderbook = build_layer3_orderbook_runtime_summary(
        market_latest={
            "orderbook_semantics_summary": {
                "near_wall": {"side": "bid"},
                "support": {"side": "bid"},
                "summary_slots_present": ["near_wall", "support"],
                "summary_slots_count": 2,
                "active_event_count": 2,
                "active_event_names": ["support_candidate", "near_wall_continued"],
                "active_event_contracts": [
                    {
                        "contract_source": "l3_event_usage_policy",
                        "event_name": "support_candidate",
                        "event_family": "support_resistance",
                        "usage_grade": "watch",
                        "interpretation_bucket": "observe_only",
                        "meaning_version": "l3_event_usage_policy.v1alpha1",
                        "confidence": 0.55,
                        "trust_bucket": "degraded",
                        "consumer_allowed": ["ui", "alert", "ai"],
                        "actionability": "review",
                        "forecast_horizon_hint": "short",
                        "half_life_sec": 30,
                        "invalidates_on": ["series_boundary", "reanchor_required"],
                        "evidence_refs": [],
                        "side": "bid",
                    },
                    {
                        "event_name": "near_wall_continued",
                        "event_family": "wall",
                        "usage_grade": "watch",
                        "side": "bid",
                    },
                ],
            },
            "orderbook_persistence_observable": True,
        },
        market_diag={"preferred_row_freshness": "QUIET"},
    )
    assert partial_orderbook["persistence_observable"] is True 
    assert partial_orderbook["wiring_status"] == "partial"
    assert partial_orderbook["contract_status_source"] == "orderbook_summary_inference"
    assert partial_orderbook["freshness"] == "QUIET"
    assert partial_orderbook["present_count"] == 2
    assert partial_orderbook["summary_slots_present"] == [
        "near_wall",
        "support",
    ]
    assert partial_orderbook["near_wall_present"] is True
    assert partial_orderbook["near_wall_side"] == "bid"
    assert partial_orderbook["support_present"] is True
    assert partial_orderbook["support_side"] == "bid"
    assert partial_orderbook["resistance_present"] is False
    assert partial_orderbook["resistance_side"] is None
    assert partial_orderbook["persistence_present"] is False
    assert partial_orderbook["persistence_event_name"] is None
    assert partial_orderbook["persistence_side"] is None
    assert partial_orderbook["active_event_count"] == 2
    assert partial_orderbook["active_event_names"] == [
        "support_candidate",
        "near_wall_continued",
    ]
    assert partial_orderbook["active_event_contracts"][0]["meaning_version"] == "l3_event_usage_policy.v1alpha1"
    assert partial_orderbook["active_event_contracts"][0]["contract_source"] == "l3_event_usage_policy"
    assert partial_orderbook["active_event_contracts"][0]["trust_bucket"] == "degraded"
    assert partial_orderbook["active_event_contracts"][0]["actionability"] == "review"
    assert partial_orderbook["active_event_contracts"][0]["forecast_horizon_hint"] == "short"
    assert partial_orderbook["active_event_contracts"][0]["half_life_sec"] == 30

    wired_orderbook = build_layer3_orderbook_runtime_summary(
        market_latest={
            "orderbook_semantics_summary": {
                "near_wall": {"side": "bid"},
                "support": {"side": "bid"},
                "resistance": {"side": "ask"},
                "persistence": {"event_name": "support_continued", "side": "bid"},
            },
            "orderbook_persistence_observable": True,
        },
        market_diag={"preferred_row_freshness": "LIVE"},
    )
    assert wired_orderbook["persistence_observable"] is True
    assert wired_orderbook["wiring_status"] == "wired"
    assert wired_orderbook["freshness"] == "LIVE"
    assert wired_orderbook["present_count"] == 4
    assert wired_orderbook["summary_slots_present"] == [
        "near_wall",
        "support",
        "resistance",
        "persistence",
    ]
    assert wired_orderbook["near_wall_side"] == "bid"
    assert wired_orderbook["support_side"] == "bid"
    assert wired_orderbook["resistance_side"] == "ask"
    assert wired_orderbook["persistence_event_name"] == "support_continued"
    assert wired_orderbook["persistence_side"] == "bid"

    explicit_partial_orderbook = build_layer3_orderbook_runtime_summary(
        market_latest={
            "orderbook_semantics_contract_status": "partial",
            "orderbook_semantics_summary": {
                "near_wall": {"side": "bid"},
                "support": {"side": "bid"},
                "resistance": {"side": "ask"},
                "persistence": {"event_name": "support_continued", "side": "bid"},
            },
        },
        market_diag={"preferred_row_freshness": "LIVE"},
    )
    assert explicit_partial_orderbook["wiring_status"] == "partial"
    assert explicit_partial_orderbook["contract_status_source"] == "market_state_orderbook_contract_status"
    assert explicit_partial_orderbook["present_count"] == 4

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())