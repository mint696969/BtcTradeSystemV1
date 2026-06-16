# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_paper_position_pnl_summary.py
# desc: SR-FX paper position and realized PnL summary tests. Simulation only; no broker calls.

from __future__ import annotations

from btcts.autotrade.execution.paper_intent import build_fx_paper_order_intent_from_service_input
from btcts.autotrade.execution.paper_ledger import default_paper_order_ledger_path, record_paper_order_transition
from btcts.autotrade.execution.paper_position import summarize_paper_position_from_lifecycle
from btcts.autotrade.replay.paper_engine import PaperExecutionEngine


def _service_input(**overrides):
    data = {
        "contract_type": "execution_market_service_input",
        "service_input_role": "execution_market",
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "freshness": "LIVE",
        "is_stale": False,
        "trust_state": "trusted",
        "continuity_state": "rest_baseline_snapshot",
        "interpretation_bucket": "allow_structural_use",
        "consumer_allowed": ["workroom", "operator_ui", "autotrade", "l4_consumer"],
        "blocked_by": [],
        "warnings": [],
        "read_only": True,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def _intent_build(decision_id: str, *, side: str, size: float, price: float = 100.0):
    return build_fx_paper_order_intent_from_service_input(
        _service_input(),
        decision_id=decision_id,
        snapshot_id=f"snapshot_{decision_id}",
        forecast_id=None,
        parameter_set_id="params_fx_balanced_v0_1",
        logic_version="autotrade_logic_v0_1",
        side=side,
        size=size,
        price=price,
        reason_codes=("unit_paper_position",),
        risk_gate_allowed=True,
        mode="PAPER_OR_REPLAY",
    )


def _record_full_fill(decision_id: str, *, side: str, size: float, fill_price: float, ts: str) -> None:
    intent_build = _intent_build(decision_id, side=side, size=size)
    assert intent_build.intent is not None
    engine = PaperExecutionEngine()
    accepted = engine.submit_fx_execution_intent(intent_build.intent, ts=ts)
    filled = engine.fill(intent_build.intent.decision_id, ts=ts, fill_price=fill_price)
    assert filled is not None
    record_paper_order_transition(
        previous_order=accepted,
        order=filled,
        recorded_at=ts,
        fill_size=size,
        fill_price=fill_price,
    )


def test_paper_position_summary_tracks_open_long(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    _record_full_fill("decision_position_long_001", side="buy", size=0.01, fill_price=100.0, ts="2026-06-14T00:00:00Z")
    _record_full_fill("decision_position_long_002", side="buy", size=0.02, fill_price=110.0, ts="2026-06-14T00:00:01Z")

    summary = summarize_paper_position_from_lifecycle()
    data = summary.to_dict()

    assert summary.exists is True
    assert summary.fill_event_count == 2
    assert round(summary.net_position_size, 8) == 0.03
    assert summary.position_side == "long"
    assert round(float(summary.average_entry_price), 8) == round(((0.01 * 100.0) + (0.02 * 110.0)) / 0.03, 8)
    assert summary.realized_pnl == 0.0
    assert summary.product_code == "FX_BTC_JPY"
    assert summary.market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert data["read_only"] is True
    assert data["would_send_to_broker"] is False


def test_paper_position_summary_realizes_pnl_when_long_is_reduced(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    _record_full_fill("decision_position_buy_001", side="buy", size=0.03, fill_price=100.0, ts="2026-06-14T00:00:00Z")
    _record_full_fill("decision_position_sell_001", side="sell", size=0.01, fill_price=130.0, ts="2026-06-14T00:00:01Z")

    summary = summarize_paper_position_from_lifecycle()

    assert summary.fill_event_count == 2
    assert round(summary.net_position_size, 8) == 0.02
    assert summary.position_side == "long"
    assert summary.average_entry_price == 100.0
    assert round(summary.realized_pnl, 8) == round((130.0 - 100.0) * 0.01, 8)
    assert summary.realized_pnl_currency == "JPY"
    assert summary.latest_fill_side == "sell"
    assert summary.read_only is True
    assert summary.would_send_to_broker is False


def test_paper_position_summary_handles_short_and_cover(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    _record_full_fill("decision_position_short_001", side="sell", size=0.02, fill_price=120.0, ts="2026-06-14T00:00:00Z")
    _record_full_fill("decision_position_cover_001", side="buy", size=0.01, fill_price=100.0, ts="2026-06-14T00:00:01Z")

    summary = summarize_paper_position_from_lifecycle()

    assert round(summary.net_position_size, 8) == -0.01
    assert summary.position_side == "short"
    assert summary.average_entry_price == 120.0
    assert round(summary.realized_pnl, 8) == round((120.0 - 100.0) * 0.01, 8)
    assert summary.read_only is True
    assert summary.would_send_to_broker is False


def test_paper_position_summary_failsoft_malformed_rows(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    path = default_paper_order_ledger_path(ensure=True)
    path.write_text("not-json\n", encoding="utf-8")
    _record_full_fill("decision_position_after_bad_001", side="buy", size=0.01, fill_price=100.0, ts="2026-06-14T00:00:00Z")

    summary = summarize_paper_position_from_lifecycle(path)

    assert summary.skipped_rows == 1
    assert "paper_position_summary_skipped_malformed_rows" in summary.warnings
    assert summary.fill_event_count == 1
    assert summary.position_side == "long"
    assert summary.read_only is True
    assert summary.would_send_to_broker is False
