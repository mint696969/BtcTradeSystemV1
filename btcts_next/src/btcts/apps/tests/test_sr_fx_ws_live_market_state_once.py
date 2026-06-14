# path: ./btcts_next/src/btcts/apps/tests/test_sr_fx_ws_live_market_state_once.py
# desc: SR-FX WS live canonical -> L3 market_state bridge tests. Read-only; no broker calls.

from __future__ import annotations

from datetime import datetime, timezone

from btcts.apps import sr_fx_ws_live_market_state_once as app
from btcts.autotrade.read_model.fx_market_state_ws_live import (
    FxWsLiveMarketStateResult,
    build_fx_market_state_record_from_ws_live,
    write_fx_market_state_from_ws_live_canonical,
)


def _env(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("BTCTS_LOGS_ROOT", str(tmp_path / "logs"))
    monkeypatch.setenv("BTCTS_STATE_ROOT", str(tmp_path / "state"))
    monkeypatch.setenv("BTCTS_EXECUTION_PRODUCT_CODE", "FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_UID", "bitflyer.fx.FX_BTC_JPY")
    monkeypatch.setenv("BTCTS_EXECUTION_MARKET_TYPE", "fx")


def _board() -> dict:
    return {
        "source": "live_canonical",
        "event_ts": "2026-06-14T00:00:00Z",
        "record_type": "market.orderbook.snapshot",
        "stream_session_id": "unit:fx_ws_board",
        "best_bid": 100.0,
        "best_ask": 101.0,
        "spread": 1.0,
        "bid_levels": 10,
        "ask_levels": 10,
        "bid_depth": 3.0,
        "ask_depth": 1.0,
        "continuity_state": "continuous",
        "is_resync": False,
    }


def _balanced_board() -> dict:
    data = _board()
    data["bid_depth"] = 1.0
    data["ask_depth"] = 1.0
    return data


def _flow() -> dict:
    return {
        "source": "live_canonical",
        "event_ts": "2026-06-14T00:00:01Z",
        "buy_size": 1.0,
        "sell_size": 0.4,
        "delta": 0.6,
        "trade_count": 3,
        "last_price": 100.5,
    }


def test_build_record_marks_ws_live_continuous_and_orderbook_partial() -> None:
    record = build_fx_market_state_record_from_ws_live(
        board=_board(),
        flow=_flow(),
        exchange="bitflyer",
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        stream_session_id="unit:fx_ws_board",
    )
    data = record.to_dict()

    assert data["symbol_raw"] == "FX_BTC_JPY"
    assert data["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert data["continuity_state"] == "continuous"
    assert data["interpretation_bucket"] == "allow_structural_use"
    assert data["best_bid"] == 100.0
    assert data["best_ask"] == 101.0
    assert data["trade_delta"] == 0.6
    assert round(float(data["wall_ratio"]), 3) == 0.5
    assert data["wall_side"] == "bid"
    assert data["orderbook_semantics_contract_status"] == "partial"
    assert data["orderbook_semantics_summary"]["summary_slots_present"] == ["near_wall"]
    assert data["interpretation_policy"]["delta_orderbook_application_complete"] is False



def test_build_record_treats_balanced_observed_orderbook_as_partial_context() -> None:
    record = build_fx_market_state_record_from_ws_live(
        board=_balanced_board(),
        flow=_flow(),
        exchange="bitflyer",
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        stream_session_id="unit:fx_ws_board",
    )
    data = record.to_dict()

    assert data["wall_side"] == "balanced"
    assert data["orderbook_semantics_contract_status"] == "partial"
    assert data["orderbook_semantics_summary"]["summary_slots_present"] == []
    assert data["orderbook_semantics_summary"]["active_event_count"] == 0
    assert data["zone_density_metadata"]["orderbook_observed"] is True
    assert data["interpretation_policy"]["context_only_not_order_signal"] is True


def test_write_ws_live_market_state_from_fx_live_canonical(monkeypatch, tmp_path) -> None:
    _env(monkeypatch, tmp_path)
    board_calls: list[tuple[str, str]] = []
    flow_calls: list[tuple[str, str, int]] = []

    result = write_fx_market_state_from_ws_live_canonical(
        latest_board_func=lambda **kwargs: board_calls.append((kwargs["exchange"], kwargs["symbol"])) or _board(),
        recent_tradeflow_func=lambda **kwargs: flow_calls.append((kwargs["exchange"], kwargs["symbol"], kwargs["lines"])) or _flow(),
        now=datetime(2026, 6, 14, 0, 0, 30, tzinfo=timezone.utc),
    )

    assert result.ok is True
    assert board_calls == [("bitflyer", "FX_BTC_JPY")]
    assert flow_calls == [("bitflyer", "FX_BTC_JPY", 80)]
    assert result.product_code == "FX_BTC_JPY"
    assert result.market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert result.market_state_path is not None
    assert "symbol=FX_BTC_JPY" in str(result.market_state_path)
    assert result.row is not None
    assert result.row["continuity_state"] == "continuous"
    assert result.read_only is True
    assert result.would_send_to_broker is False
    assert "ws_live_canonical_bridge_not_full_delta_orderbook_engine" in result.warnings

def test_write_ws_live_market_state_blocks_missing_live_board(monkeypatch, tmp_path) -> None:
    _env(monkeypatch, tmp_path)

    result = write_fx_market_state_from_ws_live_canonical(
        latest_board_func=lambda **kwargs: {},
        recent_tradeflow_func=lambda **kwargs: _flow(),
        now=datetime(2026, 6, 14, 0, 0, 30, tzinfo=timezone.utc),
    )

    assert result.ok is False
    assert "fx_ws_live_board_missing" in result.blocked_by
    assert result.market_state_path is None
    assert result.read_only is True
    assert result.would_send_to_broker is False


def test_write_ws_live_market_state_blocks_stale_live_canonical(monkeypatch, tmp_path) -> None:
    _env(monkeypatch, tmp_path)

    result = write_fx_market_state_from_ws_live_canonical(
        latest_board_func=lambda **kwargs: _board(),
        recent_tradeflow_func=lambda **kwargs: _flow(),
        now=datetime(2026, 6, 14, 0, 5, 0, tzinfo=timezone.utc),
        max_age_sec=120.0,
    )

    assert result.ok is False
    assert "fx_ws_live_board_stale" in result.blocked_by
    assert "fx_ws_live_tradeflow_stale" in result.blocked_by
    assert result.market_state_path is None
    assert result.read_only is True
    assert result.would_send_to_broker is False


def test_app_payload_is_read_only(monkeypatch, tmp_path) -> None:
    _env(monkeypatch, tmp_path)
    wrapped = FxWsLiveMarketStateResult(
        ok=True,
        exchange="bitflyer",
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        state_type="market.overview",
        market_state_path=None,
        blocked_by=(),
        warnings=("unit_wrapper",),
        row={"symbol_raw": "FX_BTC_JPY", "market_uid": "bitflyer.fx.FX_BTC_JPY"},
        read_only=True,
        would_send_to_broker=False,
    )
    calls: list[tuple[object, object]] = []

    def fake_writer(*, latest_board_func, recent_tradeflow_func):
        calls.append((latest_board_func, recent_tradeflow_func))
        return wrapped

    monkeypatch.setattr(app, "write_fx_market_state_from_ws_live_canonical", fake_writer)

    payload = app.build_sr_fx_ws_live_market_state_payload()

    assert payload["stage"] == "sr_fx_ws_live_market_state_once"
    assert payload["ok"] is True
    assert payload["result"]["row"]["symbol_raw"] == "FX_BTC_JPY"
    assert payload["read_only"] is True
    assert payload["would_send_to_broker"] is False
    assert len(calls) == 1
