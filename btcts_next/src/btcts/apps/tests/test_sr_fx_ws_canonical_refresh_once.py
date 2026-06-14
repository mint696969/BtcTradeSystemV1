# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_ws_canonical_refresh_once.py
# desc: SR-FX fresh WS canonical refresh tests. Network-free; no broker calls.

from __future__ import annotations

from datetime import datetime, timezone

from btcts.apps import sr_fx_ws_canonical_refresh_once as app
from btcts.collector_vnext.fx_public_ws_refresh import (
    refresh_fx_ws_board_snapshot_until_seen,
    refresh_fx_ws_executions_until_seen,
)
from btcts.collector_vnext.ids import SequenceManager
from btcts.collector_vnext.providers.bitflyer_ws import WSMessage
from btcts.collector_vnext.providers.bitflyer_ws_board import BoardMessage


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _runtime_paths(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(tmp_path / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(tmp_path / "state"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")


def _board_stream_delta_then_snapshot(symbol: str, *, ssl_verify: bool, ca_file: str | None = None):
    ts = _iso_now()
    yield BoardMessage(
        provider="bitflyer_ws_board",
        exchange="bitflyer",
        transport="websocket",
        channel=f"lightning_board_{symbol}",
        payload={"bids": [{"price": 98.0, "size": 0.5}], "asks": []},
        received_ts=ts,
        subscription_id=None,
        message_id=None,
        source_sequence=None,
        raw_message_meta={"subscription_channel": f"lightning_board_{symbol}", "ssl_verify": ssl_verify, "ca_file": ca_file},
    )
    yield BoardMessage(
        provider="bitflyer_ws_board_snapshot",
        exchange="bitflyer",
        transport="websocket",
        channel=f"lightning_board_snapshot_{symbol}",
        payload={"bids": [{"price": 100.0, "size": 3.0}], "asks": [{"price": 101.0, "size": 1.0}]},
        received_ts=ts,
        subscription_id=None,
        message_id=None,
        source_sequence=None,
        raw_message_meta={"subscription_channel": f"lightning_board_snapshot_{symbol}", "ssl_verify": ssl_verify, "ca_file": ca_file},
    )



def _board_stream_many_deltas_then_snapshot(symbol: str, *, ssl_verify: bool, ca_file: str | None = None):
    ts = _iso_now()
    for i in range(25):
        yield BoardMessage(
            provider="bitflyer_ws_board",
            exchange="bitflyer",
            transport="websocket",
            channel=f"lightning_board_{symbol}",
            payload={"bids": [{"price": 98.0 + i, "size": 0.5}], "asks": []},
            received_ts=ts,
            subscription_id=None,
            message_id=None,
            source_sequence=None,
            raw_message_meta={"subscription_channel": f"lightning_board_{symbol}", "ssl_verify": ssl_verify, "ca_file": ca_file},
        )
    yield BoardMessage(
        provider="bitflyer_ws_board_snapshot",
        exchange="bitflyer",
        transport="websocket",
        channel=f"lightning_board_snapshot_{symbol}",
        payload={"bids": [{"price": 100.0, "size": 3.0}], "asks": [{"price": 101.0, "size": 1.0}]},
        received_ts=ts,
        subscription_id=None,
        message_id=None,
        source_sequence=None,
        raw_message_meta={"subscription_channel": f"lightning_board_snapshot_{symbol}", "ssl_verify": ssl_verify, "ca_file": ca_file},
    )


def _execution_stream(symbol: str, *, ssl_verify: bool, recv_timeout_sec: float, ca_file: str | None = None):
    ts = _iso_now()
    yield WSMessage(
        provider="bitflyer_ws_executions",
        exchange="bitflyer",
        transport="websocket",
        channel=f"lightning_executions_{symbol}",
        payload={"id": 1, "side": "BUY", "price": 100.5, "size": 0.2, "exec_date": ts},
        received_ts=ts,
        subscription_id=None,
        message_id=None,
        source_sequence=None,
        raw_message_meta={"subscription_channel": f"lightning_executions_{symbol}", "recv_timeout_sec": recv_timeout_sec, "ssl_verify": ssl_verify, "ca_file": ca_file},
    )


def test_refresh_board_reads_until_snapshot_and_writes_fx_paths(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    out = refresh_fx_ws_board_snapshot_until_seen(
        SequenceManager.start(),
        "unit-session",
        stream_factory=_board_stream_delta_then_snapshot,
    )

    assert out["ok"] is True
    assert out["product_code"] == "FX_BTC_JPY"
    assert out["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert out["message_count"] == 2
    assert out["delta_count"] == 1
    assert out["snapshot_count"] == 1
    assert out["last_event_type"] == "snapshot"
    assert "symbol=FX_BTC_JPY" in str(out["snapshot_canonical_path"])
    assert "symbol=BTC_JPY" not in str(out["snapshot_canonical_path"])
    assert out["read_only"] is True
    assert out["would_send_to_broker"] is False


def test_refresh_executions_writes_fx_trade(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    out = refresh_fx_ws_executions_until_seen(
        SequenceManager.start(),
        "unit-session",
        stream_factory=_execution_stream,
    )

    assert out["ok"] is True
    assert out["product_code"] == "FX_BTC_JPY"
    assert out["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert out["trade_count"] == 1
    assert "symbol=FX_BTC_JPY" in str(out["canonical_path"])
    assert out["read_only"] is True
    assert out["would_send_to_broker"] is False




def test_refresh_app_default_wait_budget_survives_delta_burst_before_snapshot(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    payload = app.build_sr_fx_ws_canonical_refresh_payload(
        board_stream_factory=_board_stream_many_deltas_then_snapshot,
        executions_stream_factory=_execution_stream,
    )

    assert payload["ok"] is True
    assert payload["board_refresh"]["message_count"] == 26
    assert payload["board_refresh"]["max_messages"] == 200
    assert payload["board_refresh"]["delta_count"] == 25
    assert payload["board_refresh"]["snapshot_count"] == 1
    assert payload["l3_market_state"]["ok"] is True
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False


def test_refresh_app_writes_fresh_canonical_then_l3_market_state(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    payload = app.build_sr_fx_ws_canonical_refresh_payload(
        board_stream_factory=_board_stream_delta_then_snapshot,
        executions_stream_factory=_execution_stream,
    )

    assert payload["stage"] == "sr_fx_ws_canonical_refresh_once"
    assert payload["ok"] is True
    assert payload["board_refresh"]["snapshot_count"] == 1
    assert payload["executions_refresh"]["trade_count"] == 1
    assert payload["l3_market_state"]["ok"] is True
    assert payload["l3_market_state"]["row"]["symbol_raw"] == "FX_BTC_JPY"
    assert payload["l3_market_state"]["row"]["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert payload["l3_market_state"]["row"]["continuity_state"] == "continuous"
    assert "symbol=FX_BTC_JPY" in str(payload["l3_market_state"]["market_state_path"])
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False


def test_refresh_app_blocks_when_snapshot_missing(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    def no_snapshot(symbol: str, *, ssl_verify: bool, ca_file: str | None = None):
        ts = _iso_now()
        yield BoardMessage(
            provider="bitflyer_ws_board",
            exchange="bitflyer",
            transport="websocket",
            channel=f"lightning_board_{symbol}",
            payload={"bids": [{"price": 98.0, "size": 0.5}], "asks": []},
            received_ts=ts,
            subscription_id=None,
            message_id=None,
            source_sequence=None,
            raw_message_meta={},
        )

    payload = app.build_sr_fx_ws_canonical_refresh_payload(
        board_stream_factory=no_snapshot,
        executions_stream_factory=_execution_stream,
        max_board_messages=1,
    )

    assert payload["ok"] is False
    assert "fx_ws_board_snapshot_not_seen" in payload["blocked_by"]
    assert payload["board_refresh"]["ok"] is False
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False



def test_refresh_app_reports_tls_failure_as_blocker(monkeypatch, tmp_path) -> None:
    _runtime_paths(monkeypatch, tmp_path)

    def tls_board_failure(symbol: str, *, ssl_verify: bool, ca_file: str | None = None):
        raise RuntimeError("SSL: CERTIFICATE_VERIFY_FAILED synthetic")
        yield  # pragma: no cover

    def tls_execution_failure(symbol: str, *, ssl_verify: bool, recv_timeout_sec: float, ca_file: str | None = None):
        raise RuntimeError("SSL: CERTIFICATE_VERIFY_FAILED synthetic")
        yield  # pragma: no cover

    payload = app.build_sr_fx_ws_canonical_refresh_payload(
        board_stream_factory=tls_board_failure,
        executions_stream_factory=tls_execution_failure,
    )

    assert payload["ok"] is False
    assert "fx_ws_tls_certificate_verification_failed" in payload["blocked_by"]
    assert payload["board_refresh"]["error_class"] == "RuntimeError"
    assert payload["executions_refresh"]["error_class"] == "RuntimeError"
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False
