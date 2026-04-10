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
from btcts.processing.l3_market_semantics.event_usage_policy import (
    build_event_usage_contract_rows,
)


def main() -> int:
    rows = build_layer3_semantic_usage_rows(
        interpretation_bucket="observe_only",
    )

    by_family = {str(row["event_family"]): row for row in rows}

    assert by_family["pressure"]["usage_grade"] == "watch_weak"
    assert by_family["wall"]["usage_grade"] == "watch"
    assert by_family["support_resistance"]["usage_grade"] == "watch"
    assert by_family["sweep"]["usage_grade"] == "tentative"
    assert by_family["absorption"]["usage_grade"] == "tentative"

    invalid_rows = build_layer3_semantic_usage_rows(
        interpretation_bucket="reanchor_required",
    )
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
                "observer_status": "healthy",
                "total_rows": 8,
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
    assert live_summary["strong_count"] == 8
    assert live_summary["invalid_count"] == 0

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

    partial_orderbook = build_layer3_orderbook_runtime_summary(
        market_latest={
            "orderbook_semantics_summary": {
                "near_wall": {"side": "bid"},
                "support": {"side": "bid"},
                "active_event_count": 2,
                "active_event_names": ["support_candidate", "near_wall_continued"],
                "active_event_contracts": [
                    {
                        "event_name": "support_candidate",
                        "event_family": "support_resistance",
                        "usage_grade": "watch",
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
    assert partial_orderbook["active_event_contracts"][0]["event_family"] == "support_resistance"
    assert partial_orderbook["active_event_contracts"][0]["usage_grade"] == "watch"

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