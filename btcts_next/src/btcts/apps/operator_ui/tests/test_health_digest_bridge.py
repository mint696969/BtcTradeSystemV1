# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_digest_bridge.py
# desc: Verify health digest UI bridge hides direct adapter usage from views.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.health_digest_bridge import (  # noqa: E402
    build_health_digest_payload,
    build_health_digest_ui_bundle,
    build_health_digest_widget,
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
        },
        api_runtime={
            "provider": "bitflyer",
            "mode": "normal",
            "utilization": 0.22,
            "requests_60s": 14,
        },
        ws_runtime={
            "board_state": "healthy",
            "executions_state": "healthy",
            "board_freshness": "LIVE",
            "executions_freshness": "LIVE",
        },
        market_runtime={
            "trust_state": "trusted",
            "continuity_state": "continuous",
            "interpretation_bucket": "allow_structural_use",
        },
        semantic_usage={
            "summary_source": "market_state_semantic_usage_summary",
            "observer_status": "healthy",
            "runtime_wiring_status": "wired",
            "observer_present": True,
            "usage_summary_present": True,
            "contract_rows_present": True,
            "source_series_present": True,
            "contract_rows_count": 2,
            "contract_rows": [{"event_family": "wall"}],
        },
        orderbook_runtime={
            "contract_status_source": "market_state_orderbook_contract_status",
            "wiring_status": "partial",
            "summary_slots_count": 3,
            "summary_slots_present": ["near_wall", "support", "persistence"],
            "near_wall_present": True,
            "support_present": True,
            "resistance_present": False,
            "persistence_present": True,
            "persistence_observable": True,
            "active_event_count": 1,
            "active_event_names": ["near_wall_continued"],
            "active_event_contracts": [{"event_name": "near_wall_continued"}],
        },
        diagnostics={"preferred_row_age_sec": 5.0},
    )

    bundle = build_health_digest_ui_bundle(digest)
    assert bundle["widget"].widget_kind == "health_digest"
    assert bundle["widget"].freshness_key == "LIVE"
    assert bundle["payload"]["source_kind"] == "health_data_service"
    assert bundle["payload"]["semantic_usage_summary_source"] == "market_state_semantic_usage_summary"
    assert bundle["payload"]["semantic_usage_contract_rows_count"] == 2
    assert bundle["payload"]["orderbook_summary_slots_count"] == 3
    assert bundle["payload"]["orderbook_active_event_names"] == ["near_wall_continued"]
    assert bundle["payload"]["orderbook_active_event_count"] == 1
    assert bundle["payload"]["orderbook_active_event_contracts_count"] == 1

    widget = build_health_digest_widget(digest)
    assert widget.collector_mode_key == "unified"
    assert widget.semantic_summary_source_key == "market_state_semantic_usage_summary"
    assert widget.semantic_observer_status_key == "healthy"
    assert widget.orderbook_contract_status_source_key == "market_state_orderbook_contract_status"
    assert widget.semantic_observer_present_key == "true"
    assert widget.semantic_usage_summary_present_key == "true"
    assert widget.semantic_contract_rows_present_key == "true"
    assert widget.semantic_source_series_present_key == "true"
    assert widget.orderbook_near_wall_present_key == "true"
    assert widget.orderbook_support_present_key == "true"
    assert widget.orderbook_resistance_present_key == "false"
    assert widget.orderbook_persistence_present_key == "true"
    assert widget.orderbook_persistence_observable_key == "true"
    assert widget.orderbook_summary_slots_present == ["near_wall", "support", "persistence"]
    assert widget.orderbook_active_event_names == ["near_wall_continued"]
    assert widget.orderbook_summary_slots_count == 3

    payload = build_health_digest_payload(digest)
    assert payload["freshness"] == "LIVE"
    assert payload["orderbook_summary_slots_present"] == [
        "near_wall",
        "support",
        "persistence",
    ]

    empty_bundle = build_health_digest_ui_bundle(None)
    assert empty_bundle["widget"].freshness_key == "UNKNOWN"
    assert empty_bundle["payload"] == {}

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())