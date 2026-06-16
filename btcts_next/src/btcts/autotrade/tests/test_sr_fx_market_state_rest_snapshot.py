# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_market_state_rest_snapshot.py
# desc: SR-FX public REST board to market_state bridge tests. No broker calls.

from __future__ import annotations

from btcts.autotrade.read_model.fx_market_state_rest_snapshot import build_fx_market_state_record_from_rest_board


def test_build_fx_market_state_record_from_rest_board_uses_execution_identity() -> None:
    row = build_fx_market_state_record_from_rest_board(
        payload={
            "mid_price": 100.5,
            "bids": [{"price": 100.0, "size": 1.0}, {"price": 99.0, "size": 2.0}],
            "asks": [{"price": 101.0, "size": 1.5}, {"price": 102.0, "size": 2.5}],
        },
        exchange="bitflyer",
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        received_ts="2026-06-14T08:00:00Z",
        stream_session_id="unit-session",
        near_zone_levels=1,
        trade_delta=0.25,
    )

    data = row.to_dict()
    assert data["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert data["symbol_raw"] == "FX_BTC_JPY"
    assert data["trust_state"] == "trusted"
    assert data["boundary_reason"] == "none"
    assert data["continuity_state"] == "rest_baseline_snapshot"
    assert data["interpretation_bucket"] == "allow_structural_use"
    assert data["best_bid"] == 100.0
    assert data["best_ask"] == 101.0
    assert data["spread"] == 1.0
    assert data["mid_price"] == 100.5
    assert data["price"] == 100.5
    assert data["imbalance"] == -0.2
    assert data["trade_delta"] == 0.25
    assert data["near_zone_liquidity_summary"]["bid_size_total"] == 1.0
    assert data["near_zone_liquidity_summary"]["ask_size_total"] == 1.5
    assert data["source_stream_session_id"] == "unit-session"


def test_build_fx_market_state_record_from_incomplete_board_is_provisional() -> None:
    row = build_fx_market_state_record_from_rest_board(
        payload={"bids": [], "asks": []},
        exchange="bitflyer",
        product_code="FX_BTC_JPY",
        market_uid="bitflyer.fx.FX_BTC_JPY",
        received_ts="2026-06-14T08:00:00Z",
        stream_session_id="unit-session",
    )

    data = row.to_dict()
    assert data["trust_state"] == "provisional"
    assert data["interpretation_bucket"] == "observe_only"
    assert data["best_bid"] is None
    assert data["best_ask"] is None



def test_trade_delta_from_executions_payload_uses_signed_size() -> None:
    from btcts.autotrade.read_model.fx_market_state_rest_snapshot import _trade_delta_from_executions_payload

    delta = _trade_delta_from_executions_payload(
        {
            "items": [
                {"side": "BUY", "size": 0.30},
                {"side": "SELL", "size": 0.10},
                {"side": "BUY", "size": 0.05},
                {"side": "UNKNOWN", "size": 9.99},
            ]
        }
    )

    assert round(delta or 0.0, 8) == 0.25
