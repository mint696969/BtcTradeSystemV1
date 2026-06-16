# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_data_service_sr_fx_integrity_gate.py
# desc: SR-FX Data/UI Integrity Gate tests for Health aggregate pressure and WS lane separation.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.health_data_service as svc  # noqa: E402
from btcts.apps.operator_ui.views import health_page  # noqa: E402


def _patch_time(monkeypatch):
    buckets = [
        svc.parse_ts("2026-06-14T00:00:00Z"),
        svc.parse_ts("2026-06-14T00:01:00Z"),
        svc.parse_ts("2026-06-14T00:02:00Z"),
    ]
    monkeypatch.setattr(svc, "range_config", lambda range_key: {"window_minutes": 3, "bucket_minutes": 1})
    monkeypatch.setattr(svc, "time_buckets", lambda window_minutes, bucket_minutes: list(buckets))
    monkeypatch.setattr(svc, "display_buckets", lambda items, include_in_progress=False: list(items))


def test_health_series_separates_ws_board_and_executions(monkeypatch) -> None:
    _patch_time(monkeypatch)
    rows = [
        {
            "ts": "2026-06-14T00:00:10Z",
            "event": "collector_vnext.unified.ws_executions.message.received",
            "payload": {"provider": "bitflyer_ws_executions"},
        },
        {
            "ts": "2026-06-14T00:01:10Z",
            "event": "collector_vnext.unified.ws_board.message.received",
            "payload": {"provider": "bitflyer_ws_board"},
        },
    ]

    series = svc.build_recent_api_ws_series(range_key="1h", audit_rows=rows)

    assert series[0]["ws_events"] == 1.0
    assert series[0]["ws_board_events"] == 0.0
    assert series[0]["ws_exec_events"] == 1.0
    assert series[1]["ws_events"] == 1.0
    assert series[1]["ws_board_events"] == 1.0
    assert series[1]["ws_exec_events"] == 0.0

    rails = svc.build_ws_continuity_rail(
        range_key="1h",
        audit_rows=rows,
        state={
            "status": {"ws_board_lane": {"ws_state": "LIVE", "last_event_ts": "2026-06-14T00:01:10Z"}},
            "origin": {},
            "executions": {"ws_state": "LIVE", "last_event_ts": "2026-06-14T00:00:10Z"},
        },
    )
    board = rails[0]
    executions = rails[1]

    assert board["venue"] == "bitflyer_ws_board"
    assert executions["venue"] == "bitflyer_ws_executions"
    assert board["cells"][0]["level"] == "gray"
    assert executions["cells"][0]["level"] == "green"
    assert board["cells"][1]["level"] == "green"
    assert executions["cells"][1]["level"] == "gray"


def test_rate_overlay_uses_bitflyer_aggregate_not_market_data_domain(monkeypatch) -> None:
    _patch_time(monkeypatch)
    monkeypatch.setattr(
        svc,
        "load_state",
        lambda: {
            "rate": {
                "items": {
                    "bitflyer": {
                        "budget": {"budget_60s": 475, "budget_300s": 475},
                        "requests_60s": 10,
                        "requests_300s": 20,
                        "utilization": 0.04,
                        "target_utilization": 0.95,
                        "hard_cap_utilization": 0.98,
                        "domains": {
                            "market_data": {
                                "budget": {"budget_60s": 100, "budget_300s": 100},
                                "requests_60s": 3,
                                "requests_300s": 4,
                                "utilization": 0.01,
                            }
                        },
                    }
                }
            }
        },
    )

    overlay = svc.build_rate_limit_overlay(range_key="1h")

    assert overlay[-1]["source_kind"] == "rate_state_overlay"
    assert overlay[-1]["overlay_scope"] == "bitflyer_aggregate"
    assert overlay[-1]["budget_60s"] == 475
    assert overlay[-1]["requests_60s"] == 10
    assert overlay[-1]["requests_300s"] == 20


def test_health_page_sums_public_and_private_request_classes() -> None:
    classes = {
        "board_snapshot": {"requests_60s": 1, "requests_300s": 11},
        "rest_trades": {"requests_60s": 2, "requests_300s": 22},
        "public_rest_market_data": {"requests_60s": 3, "requests_300s": 33},
        "private_rest_account_state": {"requests_60s": 4, "requests_300s": 44},
        "private_rest_order_state": {"requests_60s": 5, "requests_300s": 55},
        "private_rest_own_fills": {"requests_60s": 6, "requests_300s": 66},
    }

    public = health_page._sum_request_classes(
        classes,
        ("board_snapshot", "rest_trades", "public_rest_market_data"),
    )
    private = health_page._sum_request_classes(
        classes,
        ("private_rest_account_state", "private_rest_order_state", "private_rest_own_fills"),
    )

    assert public == {"requests_60s": 6, "requests_300s": 66}
    assert private == {"requests_60s": 15, "requests_300s": 165}
