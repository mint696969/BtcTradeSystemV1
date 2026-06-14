# path: ./btcts_next/src/btcts/collector_vnext/tests/test_fx_public_ws_identity.py
# desc: Tests for SR-FX public WS identity/channel/path separation. Network-free.

from __future__ import annotations

from btcts.collector_vnext.fx_public_ws import emit_fx_ws_board_smoke, emit_fx_ws_trade_smoke, fx_ws_channel_plan
from btcts.collector_vnext.ids import SequenceManager
from btcts.collector_vnext.providers.bitflyer_ws import WSMessage
from btcts.collector_vnext.providers.bitflyer_ws_board import BoardMessage


def _runtime_paths(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(tmp_path / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(tmp_path / "state"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")


def test_fx_ws_channel_plan_uses_fx_product(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    plan = fx_ws_channel_plan()

    assert plan["product_code"] == "FX_BTC_JPY"
    assert plan["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert plan["market_role"] == "execution"
    assert plan["channels"]["board_snapshot"] == "lightning_board_snapshot_FX_BTC_JPY"
    assert plan["channels"]["board_delta"] == "lightning_board_FX_BTC_JPY"
    assert plan["channels"]["executions"] == "lightning_executions_FX_BTC_JPY"
    assert plan["path_guard"]["all_channels_are_fx_symbol"] is True
    assert plan["path_guard"]["no_channel_is_spot_symbol"] is True


def test_emit_fx_ws_trade_smoke_writes_fx_symbol_paths(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)
    calls = []

    def fake_stream(symbol: str, *, ssl_verify: bool, recv_timeout_sec: float):
        calls.append((symbol, ssl_verify, recv_timeout_sec))
        yield WSMessage(
            provider="bitflyer_ws_executions",
            exchange="bitflyer",
            transport="websocket",
            channel=f"lightning_executions_{symbol}",
            payload={"id": 1, "side": "BUY", "price": 100.0, "size": 0.01, "exec_date": "2026-06-14T00:00:00Z"},
            received_ts="2026-06-14T00:00:00Z",
            subscription_id=None,
            message_id=None,
            source_sequence=None,
            raw_message_meta={"subscription_channel": f"lightning_executions_{symbol}"},
        )

    out = emit_fx_ws_trade_smoke(SequenceManager.start(), "unit-session", stream_factory=fake_stream)

    assert calls[0][0] == "FX_BTC_JPY"
    assert out["product_code"] == "FX_BTC_JPY"
    assert out["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert out["request_class"] == "public_ws_connect_subscribe"
    assert out["trade_count"] == 1
    assert "symbol=FX_BTC_JPY" in str(out["raw_path"])
    assert "symbol=FX_BTC_JPY" in str(out["canonical_path"])
    assert "symbol=BTC_JPY" not in str(out["raw_path"])
    assert "symbol=BTC_JPY" not in str(out["canonical_path"])


def test_emit_fx_ws_board_smoke_writes_fx_symbol_paths(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)
    calls = []

    def fake_stream(symbol: str, *, ssl_verify: bool):
        calls.append((symbol, ssl_verify))
        yield BoardMessage(
            provider="bitflyer_ws_board_snapshot",
            exchange="bitflyer",
            transport="websocket",
            channel=f"lightning_board_snapshot_{symbol}",
            payload={"bids": [{"price": 99.0, "size": 1.0}], "asks": [{"price": 101.0, "size": 1.0}]},
            received_ts="2026-06-14T00:00:00Z",
            subscription_id=None,
            message_id=None,
            source_sequence=None,
            raw_message_meta={"subscription_channel": f"lightning_board_snapshot_{symbol}"},
        )

    out = emit_fx_ws_board_smoke(SequenceManager.start(), "unit-session", stream_factory=fake_stream)

    assert calls[0][0] == "FX_BTC_JPY"
    assert out["product_code"] == "FX_BTC_JPY"
    assert out["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert out["request_class"] == "public_ws_connect_subscribe"
    assert out["event_type"] == "snapshot"
    assert "symbol=FX_BTC_JPY" in str(out["raw_path"])
    assert "symbol=FX_BTC_JPY" in str(out["canonical_path"])
    assert "symbol=BTC_JPY" not in str(out["raw_path"])
    assert "symbol=BTC_JPY" not in str(out["canonical_path"])



def test_fx_ws_preflight_success_with_fake_streams(monkeypatch, tmp_path) -> None:
    from btcts.collector_vnext.fx_public_ws import preflight_fx_public_ws

    _runtime_paths(monkeypatch, tmp_path)

    def fake_executions(symbol: str, *, ssl_verify: bool, recv_timeout_sec: float):
        yield WSMessage(
            provider="bitflyer_ws_executions",
            exchange="bitflyer",
            transport="websocket",
            channel=f"lightning_executions_{symbol}",
            payload={"id": 1, "side": "BUY", "price": 100.0, "size": 0.01},
            received_ts="2026-06-14T00:00:00Z",
            subscription_id=None,
            message_id=None,
            source_sequence=None,
            raw_message_meta={},
        )

    def fake_board(symbol: str, *, ssl_verify: bool):
        yield BoardMessage(
            provider="bitflyer_ws_board_snapshot",
            exchange="bitflyer",
            transport="websocket",
            channel=f"lightning_board_snapshot_{symbol}",
            payload={"bids": [], "asks": []},
            received_ts="2026-06-14T00:00:00Z",
            subscription_id=None,
            message_id=None,
            source_sequence=None,
            raw_message_meta={},
        )

    out = preflight_fx_public_ws(executions_stream_factory=fake_executions, board_stream_factory=fake_board)

    assert out["ok"] is True
    assert out["product_code"] == "FX_BTC_JPY"
    assert out["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert out["attempts"]["executions"]["actual_channel"] == "lightning_executions_FX_BTC_JPY"
    assert out["attempts"]["board"]["actual_channel"] == "lightning_board_snapshot_FX_BTC_JPY"
    assert out["would_send_to_broker"] is False
    assert out["read_only"] is True


def test_fx_ws_preflight_connection_failure_is_safe(monkeypatch, tmp_path) -> None:
    from btcts.collector_vnext.fx_public_ws import preflight_fx_public_ws

    _runtime_paths(monkeypatch, tmp_path)

    def failing_executions(symbol: str, *, ssl_verify: bool, recv_timeout_sec: float):
        raise RuntimeError("synthetic ssl failure")
        yield  # pragma: no cover

    def failing_board(symbol: str, *, ssl_verify: bool):
        raise RuntimeError("synthetic board failure")
        yield  # pragma: no cover

    out = preflight_fx_public_ws(executions_stream_factory=failing_executions, board_stream_factory=failing_board)

    assert out["ok"] is False
    assert out["product_code"] == "FX_BTC_JPY"
    assert out["attempts"]["executions"]["ok"] is False
    assert out["attempts"]["board"]["ok"] is False
    assert out["attempts"]["executions"]["error_class"] == "RuntimeError"
    assert out["would_send_to_broker"] is False
    assert out["read_only"] is True
