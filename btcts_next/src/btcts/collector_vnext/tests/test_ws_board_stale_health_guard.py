# path: ./btcts_next/src/btcts/collector_vnext/tests/test_ws_board_stale_health_guard.py
# desc: Guards that WS board BROKEN/stale state is not hidden by healthy REST runtime.

from __future__ import annotations

import json

from btcts.collector_vnext.config import load_config


class _FakeScheduler:
    def snapshot(self) -> dict:
        return {
            "items": {
                "bitflyer": {
                    "mode": "NORMAL",
                    "request_classes": {
                        "board_snapshot": {},
                        "rest_trades": {},
                    },
                    "domains": {
                        "market_data": {
                            "mode": "NORMAL",
                            "requests_60s": 12,
                            "requests_300s": 55,
                            "utilization": 0.25,
                        }
                    },
                }
            }
        }


def _runtime_paths(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(tmp_path / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(tmp_path / "state"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")
    monkeypatch.setenv("BTCTS_UNIFIED_MARKET_STATE_ENABLED", "0")


def test_unified_ws_board_origin_status_separates_write_ts_and_last_event_ts(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    import btcts.collector_vnext.unified_ws_board_lane as lane_mod

    monkeypatch.setattr(lane_mod, "now_iso_utc", lambda: "2026-06-27T08:00:00Z")

    lane = lane_mod.UnifiedWsBoardLane()
    lane._set_state(
        lane_state="degraded",
        ws_state="BROKEN",
        last_event_ts="2026-06-26T19:02:06Z",
        last_error="Connection to remote host was lost.",
        restart_count=107,
        saw_snapshot=True,
        saw_delta=True,
    )
    lane._write_origin_status()

    payload = json.loads(
        (tmp_path / "state" / "collector_vnext" / "unified_origin_status.json").read_text(
            encoding="utf-8"
        )
    )

    assert payload["ts"] == "2026-06-27T08:00:00Z"
    assert payload["last_event_ts"] == "2026-06-26T19:02:06Z"
    assert payload["ws_state"] == "BROKEN"
    assert payload["lane_state"] == "degraded"


def test_unified_runtime_marks_ws_board_broken_as_degraded(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    import btcts.collector_vnext.unified_runtime as runtime_mod

    old_board_event_ts = "2026-06-26T19:02:06Z"

    monkeypatch.setattr(
        runtime_mod,
        "_load_unified_origin_status",
        lambda cfg: {
            "ts": "2026-06-27T08:00:00Z",
            "last_event_ts": old_board_event_ts,
            "runtime_kind": "unified",
            "exchange": "bitflyer",
            "channel": "board_ws",
            "ws_state": "BROKEN",
            "lane_state": "degraded",
            "last_error": "Connection to remote host was lost.",
            "saw_snapshot": True,
            "saw_delta": True,
            "restart_count": 107,
        },
    )
    monkeypatch.setattr(
        runtime_mod,
        "_load_unified_executions_status",
        lambda cfg: {
            "ts": "2026-06-27T08:00:00Z",
            "last_event_ts": "2026-06-27T08:00:00Z",
            "connected_ts": "2026-06-27T07:59:00Z",
            "runtime_kind": "unified",
            "exchange": "bitflyer",
            "channel": "executions_ws",
            "ws_state": "LIVE",
            "lane_state": "live",
            "last_error": None,
            "trade_count": 1,
            "restart_count": 1,
        },
    )

    cfg = load_config()
    scheduler = _FakeScheduler()

    health = runtime_mod._build_health_payload(
        cfg=cfg,
        exchange="bitflyer",
        scheduler=scheduler,
    )
    status = runtime_mod._build_status_payload(
        cfg=cfg,
        session_id="collector_main-unified",
        scheduler=scheduler,
        exchange="bitflyer",
        last_result={},
    )

    assert health["ok"] is False
    assert health["status"] == "degraded"
    assert health["ws_freshness"] == "BROKEN"
    assert health["ws_last_event_ts"] == old_board_event_ts

    assert status["mode"] == "DEGRADED"
    assert status["ws_board_lane"]["ws_freshness"] == "BROKEN"
    assert status["ws_board_lane"]["last_event_ts"] == old_board_event_ts
