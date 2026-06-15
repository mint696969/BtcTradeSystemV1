# path: ./btcts_next/src/btcts/collector_vnext/tests/test_unified_ws_board_lane_audit_heartbeat.py
# desc: Network-free guard for throttled Unified WS board audit heartbeat.

from __future__ import annotations

import threading

from btcts.collector_vnext.providers.bitflyer_ws_board import BoardMessage
from btcts.collector_vnext.unified_ws_board_lane import UnifiedWsBoardLane


def _runtime_paths(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(tmp_path / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(tmp_path / "state"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")
    monkeypatch.setenv("BTCTS_UNIFIED_WS_BOARD_AUDIT_HEARTBEAT_SEC", "60")


def _board_message(index: int) -> BoardMessage:
    return BoardMessage(
        provider="bitflyer_ws_board_snapshot" if index == 1 else "bitflyer_ws_board",
        exchange="bitflyer",
        transport="websocket",
        channel="lightning_board_snapshot_FX_BTC_JPY" if index == 1 else "lightning_board_FX_BTC_JPY",
        payload={"bids": [{"price": 100.0, "size": 1.0}], "asks": [{"price": 101.0, "size": 1.0}]},
        received_ts=f"2026-06-15T00:00:0{index}Z",
        subscription_id=None,
        message_id=None,
        source_sequence=index,
        raw_message_meta={},
    )


def test_unified_ws_board_audit_heartbeat_is_throttled_and_fail_soft(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    messages = [_board_message(1), _board_message(2), _board_message(3)]

    stop_event = threading.Event()

    def fake_stream(symbol: str, *, ssl_verify: bool, ca_file: str | None = None):
        try:
            yield from messages
        finally:
            stop_event.set()

    emitted: list[tuple[str, dict]] = []

    def fake_emit(event: str, **kwargs):
        emitted.append((event, kwargs))
        if event == "collector_vnext.unified.ws_board.message.received":
            raise RuntimeError("audit write failed")

    monotonic_values = iter([100.0, 101.0, 102.0])

    monkeypatch.setattr("btcts.collector_vnext.unified_ws_board_lane.connect_and_stream_board", fake_stream)
    monkeypatch.setattr("btcts.collector_vnext.unified_ws_board_lane.audit.emit", fake_emit)
    monkeypatch.setattr("btcts.collector_vnext.unified_ws_board_lane.time.monotonic", lambda: next(monotonic_values))

    lane = UnifiedWsBoardLane()
    lane.run_forever(stop_event)

    heartbeat_events = [event for event, _ in emitted if event == "collector_vnext.unified.ws_board.message.received"]
    assert len(heartbeat_events) == 1
    snap = lane.snapshot()
    assert snap["ws_state"] == "LIVE"
    assert snap["saw_snapshot"] is True
    assert snap["saw_delta"] is True
    assert snap["last_error"] is None
