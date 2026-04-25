# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_health_digest_adapter.py
# desc: Verify operator_ui health digest adapter stays thin and wording-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.operator_ui import (  # noqa: E402
    health_digest_status_payload,
    health_digest_widget_model,
)
from btcts.processing.l4_consumer_models.shared import HealthDigest  # noqa: E402


def main() -> int:
    digest = HealthDigest(
        digest_type="health_digest",
        digest_version="v1alpha1",
        source_kind="health_data_service",
        exchange="bitflyer",
        symbol_raw="BTC_JPY",
        market_uid="bitflyer.spot.BTC_JPY",
        event_ts="2026-04-11T15:00:00Z",
        freshness="LIVE",
        is_stale=False,
        collector_runtime={
            "mode": "unified",
            "ok": True,
            "runtime_kind": "watchdog_managed",
            "daemon_runtime_kind": "unified_daemon",
            "status_source": "collector_state",
        },
        api_runtime={
            "provider": "bitflyer",
            "mode": "normal",
            "utilization": 0.22,
            "target_utilization": 0.50,
            "hard_cap_utilization": 0.85,
            "requests_60s": 14,
            "requests_300s": 48,
            "last_429_ts": None,
        },
        ws_runtime={
            "board_state": "healthy",
            "board_last_error": None,
            "executions_state": "healthy",
            "executions_last_error": None,
            "board_freshness": "LIVE",
            "executions_freshness": "LIVE",
        },
        market_runtime={
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
            "interpretation_reason": "continuity_trusted",
            "source_series_id": "bf-sess-1:series:120",
            "freshness": "LIVE",
        },
        semantic_usage={
            "summary_source": "market_state_semantic_usage_summary",
            "observer_status": "healthy",
            "summary": {
                "source_kind": "market_state_semantic_usage_summary",
                "observer_status": "healthy",
            },
            "contract_rows": [
                {
                    "event_family": "wall",
                    "usage_grade": "strong",
                }
            ],
            "runtime_wiring_status": "wired",
            "observer_present": True,
            "usage_summary_present": True,
            "contract_rows_present": True,
            "contract_rows_count": 1,
            "source_series_present": True,
        },
        orderbook_runtime={
            "contract_status_source": "market_state_orderbook_contract_status",
            "wiring_status": "partial",
            "freshness": "LIVE",
            "summary_slots_present": ["near_wall", "support"],
            "summary_slots_count": 2,
            "near_wall_present": True,
            "support_present": True,
            "resistance_present": False,
            "persistence_present": False,
            "persistence_observable": True,
            "active_event_count": 1,
            "active_event_names": ["near_wall_continued"],
            "active_event_contracts": [
                {
                    "event_name": "near_wall_continued",
                    "event_family": "wall",
                    "usage_grade": "strong",
                    "side": "bid",
                }
            ],
        },
        diagnostics={
            "preferred_row_age_sec": 5.0,
            "preferred_row_freshness": "LIVE",
        },
    )

    widget = health_digest_widget_model(digest)
    assert widget.widget_kind == "health_digest"
    assert widget.freshness_key == "LIVE"
    assert widget.collector_ok is True
    assert widget.collector_mode_key == "unified"
    assert widget.api_mode_key == "normal"
    assert widget.ws_board_state_key == "healthy"
    assert widget.ws_executions_state_key == "healthy"
    assert widget.trust_key == "trusted"
    assert widget.continuity_key == "continuous"
    assert widget.interpretation_key == "allow_structural_use"
    assert widget.semantic_wiring_key == "wired"
    assert widget.orderbook_wiring_key == "partial"
    assert widget.semantic_contract_rows_count == 1
    assert widget.orderbook_summary_slots_count == 2
    assert widget.active_event_count == 1
    assert widget.age_sec == 5.0
    assert widget.event_ts == "2026-04-11T15:00:00Z"
    assert widget.source_kind == "health_data_service"

    payload = health_digest_status_payload(digest)
    assert payload["digest_type"] == "health_digest"
    assert payload["digest_version"] == "v1alpha1"
    assert payload["source_kind"] == "health_data_service"
    assert payload["freshness"] == "LIVE"
    assert payload["health_observer_block_order"] == (
        "collector_ingestion_observability",
        "market_runtime_truth",
        "semantic_observability",
        "orderbook_active_event_observability",
    )
    assert payload["collector_ingestion_observability"]["collector_runtime"]["mode"] == "unified"
    assert payload["collector_ingestion_observability"]["api_runtime"]["mode"] == "normal"
    assert payload["collector_ingestion_observability"]["ws_runtime"]["board_state"] == "healthy"
    assert payload["market_runtime_truth"]["market_runtime"]["trust_state"] == "trusted"
    assert payload["semantic_observability"]["observer_present"] is True
    assert payload["semantic_observability"]["usage_summary_present"] is True
    assert payload["semantic_observability"]["contract_rows_present"] is True
    assert payload["semantic_observability"]["contract_rows_kind"] == "event_family_contract_rows"
    assert payload["semantic_observability"]["contract_rows_count"] == 1
    assert payload["semantic_observability"]["source_series_present"] is True
    assert payload["orderbook_active_event_observability"]["contract_status_source"] == "market_state_orderbook_contract_status"
    assert payload["orderbook_active_event_observability"]["runtime_wiring_status"] == "partial"
    assert payload["orderbook_active_event_observability"]["near_wall_present"] is True

    assert payload["semantic_usage_observer_present"] is True
    assert payload["semantic_usage_summary_present"] is True
    assert payload["semantic_usage_contract_rows_present"] is True
    assert payload["semantic_usage_contract_rows_kind"] == "event_family_contract_rows"
    assert payload["semantic_usage_contract_rows_count"] == 1
    assert payload["semantic_usage_source_series_present"] is True
    assert payload["orderbook_contract_status_source"] == "market_state_orderbook_contract_status"
    assert payload["orderbook_runtime_wiring_status"] == "partial"
    assert payload["orderbook_near_wall_present"] is True
    assert payload["orderbook_support_present"] is True
    assert payload["orderbook_resistance_present"] is False
    assert payload["orderbook_persistence_present"] is False
    assert payload["orderbook_persistence_observable"] is True
    assert payload["orderbook_summary_slots_kind"] == "summary_slot_names"
    assert payload["orderbook_summary_slots_count"] == 2
    assert payload["orderbook_summary_slots_present"] == ["near_wall", "support"]
    assert payload["orderbook_active_event_names"] == ["near_wall_continued"]
    assert payload["orderbook_active_event_count"] == 1
    assert payload["orderbook_active_event_contracts_kind"] == "active_event_contract_rows"
    assert payload["orderbook_active_event_contracts_count"] == 1
    assert payload["orderbook_active_event_contracts"][0]["event_name"] == "near_wall_continued"

    assert payload["orderbook_active_event_observability"]["support_present"] is True
    assert payload["orderbook_active_event_observability"]["resistance_present"] is False
    assert payload["orderbook_active_event_observability"]["persistence_present"] is False
    assert payload["orderbook_active_event_observability"]["persistence_observable"] is True
    assert payload["orderbook_active_event_observability"]["summary_slots_kind"] == "summary_slot_names"
    assert payload["orderbook_active_event_observability"]["summary_slots_count"] == 2
    assert payload["orderbook_active_event_observability"]["summary_slots_present"] == ["near_wall", "support"]
    assert payload["orderbook_active_event_observability"]["active_event_names"] == ["near_wall_continued"]
    assert payload["orderbook_active_event_observability"]["active_event_count"] == 1
    assert payload["orderbook_active_event_observability"]["active_event_contracts_kind"] == "active_event_contract_rows"
    assert payload["orderbook_active_event_observability"]["active_event_contracts_count"] == 1
    assert payload["orderbook_active_event_observability"]["active_event_contracts"][0]["event_name"] == "near_wall_continued"

    empty_widget = health_digest_widget_model(None)
    assert empty_widget.widget_kind == "health_digest"
    assert empty_widget.freshness_key == "UNKNOWN"
    assert empty_widget.semantic_wiring_key == "missing"
    assert empty_widget.orderbook_wiring_key == "missing"

    empty_payload = health_digest_status_payload(None)
    assert empty_payload == {}

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())