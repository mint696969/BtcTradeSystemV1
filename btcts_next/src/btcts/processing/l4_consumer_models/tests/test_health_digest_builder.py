# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_health_digest_builder.py
# desc: Verify shared L4 health digest builder builds a reusable wording-free bundle.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared import (  # noqa: E402
    HealthDigestBuildInput,
    build_health_digest,
)


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
    }

    market_state_row = {
        "exchange": "bitflyer",
        "symbol_raw": "BTC_JPY",
        "market_uid": "bitflyer.spot.BTC_JPY",
        "collector_ts": "2026-04-11T15:00:00Z",
        "trust_state": "trusted",
        "continuity_state": "continuous",
        "interpretation_bucket": "allow_structural_use",
        "interpretation_reason": "continuity_trusted",
        "source_series_id": "bf-sess-1:series:120",
    }

    market_diagnostics = {
        "source_kind": "market_state_preferred",
        "preferred_row_freshness": "LIVE",
        "preferred_row_age_sec": 5.0,
        "preferred_row_source_series_id": "bf-sess-1:series:120",
    }

    semantic_usage_summary = {
        "source_kind": "market_state_semantic_usage_summary",
        "observer_status": "healthy",
    }

    semantic_usage_rows = [
        {
            "event_family": "wall",
            "usage_grade": "strong",
        }
    ]

    runtime_contract_summary = {
        "wiring_status": "wired",
        "contract_rows_present": True,
        "contract_rows_count": 1,
    }

    orderbook_runtime_summary = {
        "contract_status_source": "market_state_orderbook_contract_status",
        "wiring_status": "partial",
        "freshness": "LIVE",
        "summary_slots_present": ["near_wall", "support"],
        "present_count": 2,
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
    }

    digest = build_health_digest(
        HealthDigestBuildInput(
            collector_state=collector_state,
            market_state_row=market_state_row,
            market_diagnostics=market_diagnostics,
            semantic_usage_summary=semantic_usage_summary,
            semantic_usage_rows=semantic_usage_rows,
            runtime_contract_summary=runtime_contract_summary,
            orderbook_runtime_summary=orderbook_runtime_summary,
        )
    )

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
    assert digest.api_runtime["provider"] == "bitflyer"
    assert digest.api_runtime["mode"] == "normal"
    assert digest.ws_runtime["board_state"] == "healthy"
    assert digest.market_runtime["trust_state"] == "trusted"
    assert digest.market_runtime["continuity_state"] == "continuous"
    assert digest.market_runtime["interpretation_bucket"] == "allow_structural_use"

    assert digest.semantic_usage["summary_source"] == "market_state_semantic_usage_summary"
    assert digest.semantic_usage["observer_status"] == "healthy"
    assert digest.semantic_usage["runtime_wiring_status"] == "wired"
    assert digest.semantic_usage["contract_rows_count"] == 1

    assert digest.orderbook_runtime["contract_status_source"] == "market_state_orderbook_contract_status"
    assert digest.orderbook_runtime["wiring_status"] == "partial"
    assert digest.orderbook_runtime["summary_slots_present"] == ["near_wall", "support"]
    assert digest.orderbook_runtime["summary_slots_count"] == 2
    assert digest.orderbook_runtime["active_event_count"] == 1
    assert digest.orderbook_runtime["active_event_contracts"][0]["event_name"] == "near_wall_continued"

    empty = build_health_digest(HealthDigestBuildInput())
    assert empty.digest_type == "health_digest"
    assert empty.source_kind == "health_data_service"
    assert empty.freshness == "UNKNOWN"
    assert empty.is_stale is None
    assert empty.semantic_usage["runtime_wiring_status"] == "missing"
    assert empty.orderbook_runtime["summary_slots_present"] == []

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())