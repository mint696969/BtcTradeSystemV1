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

    svc.build_recent_api_ws_series = lambda **kwargs: [{"series": "api"}]
    svc.build_rate_limit_overlay = lambda **kwargs: [{"series": "rate"}]
    svc.build_recent_layer3_series = lambda **kwargs: [{"series": "layer3"}]
    svc.build_api_continuity_rail = lambda **kwargs: [{"rail": "api"}]
    svc.build_ws_continuity_rail = lambda **kwargs: [{"rail": "ws"}]
    svc.build_recent_anomaly_rows = lambda **kwargs: [{"event": "gap"}]
    svc._read_recent_audit_rows = lambda *, max_lines=4000: []

    current_bundle = svc.load_health_current_state_bundle(
        state=collector_state,
        market_latest=market_latest,
        market_diag=market_diag,
    )
    timeline_bundle = svc.load_health_timeline_bundle(range_key="1h")
    continuity_bundle = svc.load_health_continuity_bundle(range_key="1h")
    anomaly_bundle = svc.load_health_anomaly_bundle(max_items=12)
    page_meta_bundle = svc.load_health_page_meta_bundle(range_key="1h")

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
    assert digest.semantic_usage["observer_present"] is True
    assert digest.semantic_usage["usage_summary_present"] is True
    assert digest.semantic_usage["contract_rows_present"] is True
    assert digest.semantic_usage["contract_rows_count"] == 1
    assert digest.semantic_usage["source_series_present"] is True
    assert digest.orderbook_runtime["wiring_status"] == "partial"
    assert digest.orderbook_runtime["summary_slots_present"] == ["near_wall", "support"]
    assert digest.orderbook_runtime["summary_slots_count"] == 2
    assert digest.orderbook_runtime["active_event_count"] == 1

    assert current_bundle["health_digest"].digest_type == "health_digest"
    assert current_bundle["market_latest"]["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert current_bundle["layer3_runtime_contract_summary"]["wiring_status"] == "wired"
    assert current_bundle["layer3_orderbook_runtime_summary"]["summary_slots_present"] == [
        "near_wall",
        "support",
    ]
    assert "api_ws_series" not in current_bundle
    assert "recent_anomalies" not in current_bundle
    assert "selected_range_key" not in current_bundle

    assert timeline_bundle == {
        "api_ws_series": [{"series": "api"}],
        "rate_overlay": [{"series": "rate"}],
        "layer3_series": [{"series": "layer3"}],
    }

    assert continuity_bundle == {
        "api_continuity_rail": [{"rail": "api"}],
        "ws_continuity_rail": [{"rail": "ws"}],
    }

    assert anomaly_bundle == {
        "source_kind": "audit_recent_anomaly_feed",
        "feed_kind": "health_recent_anomalies",
        "max_items": 12,
        "items": [{"event": "gap"}],
        "recent_anomalies": [{"event": "gap"}],
    }

    assert page_meta_bundle["selected_range_key"] == "1h"
    assert page_meta_bundle["range_presets"] is svc.HEALTH_RANGE_PRESETS
    assert "paths" in page_meta_bundle
    assert page_meta_bundle["health_audit_budget"]["range_key"] == "1h"
    assert page_meta_bundle["health_audit_budget"]["max_lines"] == 12000
    assert page_meta_bundle["health_audit_budget"]["row_count"] is None
    assert page_meta_bundle["health_audit_budget"]["rows_omitted_from_metadata"] is True
    assert "rows" not in page_meta_bundle["health_audit_budget"]
    assert "health_digest" not in page_meta_bundle
    assert "api_ws_series" not in page_meta_bundle

    assert snapshot["health_digest"] == current_bundle["health_digest"]
    assert snapshot["api_ws_series"] == timeline_bundle["api_ws_series"]
    assert snapshot["recent_anomalies"] == anomaly_bundle["recent_anomalies"]
    assert snapshot["selected_range_key"] == page_meta_bundle["selected_range_key"]
    assert snapshot["health_audit_input"]["range_key"] == "1h"
    assert snapshot["health_audit_input"]["max_lines"] == 12000
    assert snapshot["health_audit_input"]["row_count"] == 0
    assert snapshot["health_audit_input"]["rows_omitted_from_metadata"] is True
    assert "rows" not in snapshot["health_audit_input"]
    assert snapshot["health_audit_budget"] == snapshot["health_audit_input"]

    assert snapshot["current_state_bundle"] == current_bundle
    assert snapshot["timeline_bundle"] == timeline_bundle
    assert snapshot["continuity_bundle"] == continuity_bundle
    assert snapshot["anomaly_bundle"] == anomaly_bundle
    assert snapshot["page_meta_bundle"]["selected_range_key"] == page_meta_bundle["selected_range_key"]
    assert snapshot["page_meta_bundle"]["range_presets"] is page_meta_bundle["range_presets"]
    assert snapshot["page_meta_bundle"]["paths"] == page_meta_bundle["paths"]
    assert snapshot["page_meta_bundle"]["health_audit_input"] == snapshot["health_audit_input"]
    assert snapshot["page_meta_bundle"]["health_audit_budget"] == snapshot["health_audit_budget"]

    assert snapshot["current_state_bundle"]["health_digest"] == snapshot["health_digest"]
    assert snapshot["timeline_bundle"]["api_ws_series"] == snapshot["api_ws_series"]
    assert snapshot["continuity_bundle"]["api_continuity_rail"] == snapshot["api_continuity_rail"]
    assert snapshot["continuity_bundle"]["ws_continuity_rail"] == snapshot["ws_continuity_rail"]
    assert snapshot["anomaly_bundle"]["items"] == snapshot["recent_anomalies"]
    assert snapshot["anomaly_bundle"]["recent_anomalies"] == snapshot["recent_anomalies"]
    assert snapshot["anomaly_bundle"]["source_kind"] == "audit_recent_anomaly_feed"
    assert snapshot["anomaly_bundle"]["feed_kind"] == "health_recent_anomalies"
    assert snapshot["anomaly_bundle"]["max_items"] == 12
    assert (
        snapshot["page_meta_bundle"]["selected_range_key"]
        == snapshot["selected_range_key"]
    )

    assert snapshot["layer3_semantic_usage_rows"][0]["event_family"] == "wall"
    assert snapshot["layer3_runtime_contract_summary"]["wiring_status"] == "wired"
    assert snapshot["layer3_orderbook_runtime_summary"]["wiring_status"] == "partial"
    assert (
        snapshot["layer3_orderbook_runtime_summary"]["contract_status_source"]
        == "orderbook_summary_inference_overrode_missing"
    )
    assert snapshot["layer3_orderbook_runtime_summary"]["summary_slots_count"] == 2
    assert snapshot["layer3_orderbook_runtime_summary"]["summary_slots_present"] == [
        "near_wall",
        "support",
    ]

    assert snapshot["selected_range_key"] == "1h"
    assert snapshot["range_presets"] is svc.HEALTH_RANGE_PRESETS
    assert snapshot["api_ws_series"] == [{"series": "api"}]
    assert snapshot["rate_overlay"] == [{"series": "rate"}]
    assert snapshot["layer3_series"] == [{"series": "layer3"}]
    assert snapshot["api_continuity_rail"] == [{"rail": "api"}]
    assert snapshot["ws_continuity_rail"] == [{"rail": "ws"}]
    assert snapshot["recent_anomalies"] == [{"event": "gap"}]
    assert "logs_dir" in snapshot["paths"]
    assert "data_dir" in snapshot["paths"]
    assert "config_dir" in snapshot["paths"]

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())