# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_health_digest.py
# desc: Verify health_data_service returns shared L4 health_digest as additive current-state bundle.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.health_data_service as svc  # noqa: E402


def main() -> int:
    collector_state = {
        "mode": "unified",
        "health": {"ok": True},
        "status": {
            "runtime_kind": "watchdog_managed",
            "daemon_runtime_kind": "unified_daemon",
            "source_kind": "collector_state",
            "ws_board_lane": {
                "state": "healthy",
                "freshness": "LIVE",
            },
            "ws_executions_lane": {
                "state": "healthy",
                "freshness": "LIVE",
            },
        },
        "rate": {
            "items": {
                "bitflyer": {
                    "domains": {
                        "market_data": {
                            "provider": "bitflyer",
                            "mode": "normal",
                            "utilization": 0.22,
                            "target_utilization": 0.50,
                            "hard_cap_utilization": 0.85,
                            "requests_60s": 14,
                            "requests_300s": 48,
                        }
                    }
                }
            }
        },
        "rate_domains": {},
        "domain_names": [],
        "shared_ip": {},
        "shared_ip_budget": {},
    }

    market_latest = {
        "exchange": "bitflyer",
        "symbol_raw": "BTC_JPY",
        "market_uid": "bitflyer.spot.BTC_JPY",
        "collector_ts": "2026-04-11T15:00:00Z",
        "trust_state": "trusted",
        "continuity_state": "continuous",
        "interpretation_bucket": "allow_structural_use",
        "interpretation_reason": "continuity_trusted",
        "source_series_id": "bf-sess-1:series:120",
        "semantic_observer_status": "healthy",
        "semantic_usage_summary": {
            "observer_status": "healthy",
            "total_rows": 1,
            "strong_count": 1,
            "watch_count": 0,
            "watch_weak_count": 0,
            "tentative_count": 0,
            "invalid_count": 0,
            "unknown_count": 0,
        },
        "semantic_usage_contract_rows": [
            {
                "contract_source": "l3_event_usage_policy",
                "interpretation_bucket": "allow_structural_use",
                "event_family": "wall",
                "usage_grade": "strong",
            }
        ],
        "orderbook_semantics_contract_status": "missing",
        "orderbook_semantics_summary": {
            "near_wall": {"side": "bid"},
            "support": {"side": "bid"},
            "summary_slots_present": ["near_wall", "support"],
            "summary_slots_count": 2,
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
        "orderbook_persistence_observable": True,
    }

    market_diag = {
        "source_kind": "market_state_preferred",
        "preferred_row_freshness": "LIVE",
        "preferred_row_age_sec": 5.0,
        "preferred_row_source_series_id": "bf-sess-1:series:120",
        "preferred_row_trust_state": "trusted",
        "preferred_row_continuity_state": "continuous",
        "preferred_row_interpretation_bucket": "allow_structural_use",
    }

    svc.load_state = lambda: collector_state
    svc.load_latest_market_state = lambda: market_latest
    svc.market_state_diagnostics = lambda: market_diag

    svc.build_recent_api_ws_series = lambda **kwargs: []
    svc.build_rate_limit_overlay = lambda **kwargs: []
    svc.build_recent_layer3_series = lambda **kwargs: []
    svc.build_api_continuity_rail = lambda **kwargs: []
    svc.build_ws_continuity_rail = lambda **kwargs: []
    svc.build_recent_anomaly_rows = lambda **kwargs: []

    snapshot = svc.load_health_snapshot(range_key="1h")
    digest = snapshot["health_digest"]

    assert digest.digest_type == "health_digest"
    assert digest.digest_version == "v1alpha1"
    assert digest.source_kind == "health_data_service"
    assert digest.exchange == "bitflyer"
    assert digest.symbol_raw == "BTC_JPY"
    assert digest.market_uid == "bitflyer.spot.BTC_JPY"
    assert digest.event_ts == "2026-04-11T15:00:00Z"
    assert digest.freshness == "LIVE"
    assert digest.is_stale is False

    assert digest.collector_runtime["mode"] == "unified"
    assert digest.collector_runtime["ok"] is True
    assert digest.market_runtime["trust_state"] == "trusted"
    assert digest.semantic_usage["runtime_wiring_status"] == "wired"
    assert digest.semantic_usage["contract_rows_count"] == 1
    assert digest.orderbook_runtime["wiring_status"] == "partial"
    assert digest.orderbook_runtime["summary_slots_present"] == ["near_wall", "support"]
    assert digest.orderbook_runtime["summary_slots_count"] == 2
    assert digest.orderbook_runtime["active_event_count"] == 1

    assert snapshot["layer3_semantic_usage_rows"][0]["event_family"] == "wall"
    assert snapshot["layer3_runtime_contract_summary"]["wiring_status"] == "wired"
    assert snapshot["layer3_orderbook_runtime_summary"]["wiring_status"] == "partial"
    assert (
        snapshot["layer3_orderbook_runtime_summary"]["contract_status_source"]
        == "orderbook_summary_inference_overrode_missing"
    )
    assert snapshot["layer3_orderbook_runtime_summary"]["summary_slots_present"] == [
        "near_wall",
        "support",
    ]

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())