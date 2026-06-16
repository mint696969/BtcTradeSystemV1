# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_paper_order_ledger.py
# desc: SR-FX paper order ledger persists to AutoTrade hot runtime. No broker calls.

from __future__ import annotations

from btcts.autotrade.execution.paper_intent import build_fx_paper_order_intent_from_service_input
from btcts.autotrade.execution.paper_ledger import (
    default_paper_order_ledger_path,
    read_paper_order_ledger,
    read_paper_orders,
    record_paper_order,
)
from btcts.autotrade.replay.paper_engine import PaperExecutionEngine


def _service_input(**overrides):
    data = {
        "contract_type": "execution_market_service_input",
        "service_input_role": "execution_market",
        "exchange": "bitflyer",
        "symbol_raw": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "source_kind": "market_state_preferred",
        "source_series_id": "unit:fx:rest:series:1",
        "event_ts": "2026-06-14T00:00:00Z",
        "freshness": "LIVE",
        "is_stale": False,
        "trust_state": "trusted",
        "continuity_state": "rest_baseline_snapshot",
        "interpretation_bucket": "allow_structural_use",
        "semantic_runtime_wiring_status": "wired",
        "orderbook_wiring_status": "missing",
        "consumer_allowed": ["workroom", "operator_ui", "autotrade", "l4_consumer"],
        "capabilities": ["market_summary_anchor", "freshness_usable", "trusted_market_state"],
        "blocked_by": [],
        "warnings": ["execution_market_rest_baseline_not_continuous_ws_series"],
        "read_only": True,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def _intent_build(service_input=None):
    return build_fx_paper_order_intent_from_service_input(
        service_input or _service_input(),
        decision_id="decision_paper_ledger_001",
        snapshot_id="snapshot_paper_ledger_001",
        forecast_id=None,
        parameter_set_id="params_fx_balanced_v0_1",
        logic_version="autotrade_logic_v0_1",
        side="buy",
        size=0.001,
        price=100.0,
        reason_codes=("unit_ledger",),
        risk_gate_allowed=True,
        mode="PAPER_OR_REPLAY",
    )


def test_default_paper_order_ledger_path_uses_autotrade_hot_runtime(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))

    path = default_paper_order_ledger_path(ensure=True)

    assert str(tmp_path / "btc_ts_hot") in str(path)
    assert path.name == "paper_orders.jsonl"
    assert path.parent.name == "decisions"


def test_records_accepted_fx_paper_order_to_jsonl(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    intent_build = _intent_build()
    assert intent_build.intent is not None
    order = PaperExecutionEngine().submit_fx_execution_intent(intent_build.intent, ts="2026-06-14T00:00:00Z")

    record = record_paper_order(intent_build=intent_build, order=order, recorded_at="2026-06-14T00:00:01Z")
    path = default_paper_order_ledger_path(ensure=False)
    rows = read_paper_order_ledger(path)
    orders = read_paper_orders(path)

    assert path.exists()
    assert record.accepted is True
    assert record.read_only is True
    assert record.would_send_to_broker is False
    assert len(rows) == 1
    assert rows[0]["ledger_event"] == "autotrade.paper_order_recorded"
    assert rows[0]["order"]["status"] == "accepted"
    assert rows[0]["order"]["intent"]["product_code"] == "FX_BTC_JPY"
    assert rows[0]["order"]["intent"]["market_uid"] == "bitflyer.fx.FX_BTC_JPY"
    assert rows[0]["read_only"] is True
    assert rows[0]["would_send_to_broker"] is False
    assert len(orders) == 1
    assert orders[0].intent.market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert orders[0].status.value == "accepted"


def test_records_blocked_intent_without_order_as_rejected_ledger_row(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    intent_build = _intent_build(_service_input(freshness="STALE", is_stale=True))
    assert intent_build.ok is False
    assert intent_build.intent is None

    record = record_paper_order(intent_build=intent_build, order=None, recorded_at="2026-06-14T00:00:02Z")
    rows = read_paper_order_ledger()

    assert record.accepted is False
    assert "service_input_stale" in record.blocked_by
    assert "paper_order_missing" in record.blocked_by
    assert rows[0]["order"] is None
    assert rows[0]["accepted"] is False
    assert rows[0]["read_only"] is True
    assert rows[0]["would_send_to_broker"] is False
