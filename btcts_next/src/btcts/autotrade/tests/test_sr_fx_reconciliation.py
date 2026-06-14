# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_reconciliation.py
# desc: SR-FX read-only reconciliation tests. No broker calls.

from __future__ import annotations

from btcts.autotrade.execution.intents import attach_execution_market, build_order_intent_from_decision
from btcts.autotrade.execution.reconciliation import (
    paper_order_counts,
    private_readiness_counts,
    reconcile_fx_private_state_with_paper,
    reconcile_fx_private_state_with_paper_ledger,
)
from btcts.autotrade.execution.paper_intent import build_fx_paper_order_intent_from_service_input
from btcts.autotrade.execution.paper_ledger import default_paper_order_ledger_path, record_paper_order
from btcts.autotrade.replay.paper_engine import PaperExecutionEngine


def _readiness(*, fresh: bool = True, clear: bool = True, positions: int = 0, open_orders: int = 0) -> dict:
    return {
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "private_state_known_and_fresh": fresh,
        "account_clear_for_new_auto_entry": clear,
        "account_state_summary": {
            "position_item_count": positions,
            "open_order_item_count": open_orders,
            "own_execution_item_count": 0,
        },
    }


def _fx_intent():
    base = build_order_intent_from_decision(
        decision_id="decision_recon_001",
        snapshot_id="snapshot_recon_001",
        forecast_id=None,
        parameter_set_id="params_001",
        logic_version="logic_test",
        side="buy",
        size=0.001,
        price=100.0,
        reason_codes=("unit_test",),
        risk_gate_allowed=True,
        mode="PAPER_OR_REPLAY",
    )
    return attach_execution_market(
        base,
        exchange="bitflyer",
        product_code="FX_BTC_JPY",
        market_type="fx",
        market_uid="bitflyer.fx.FX_BTC_JPY",
    )


def test_private_readiness_counts_extracts_summary() -> None:
    counts = private_readiness_counts(_readiness(positions=1, open_orders=2))

    assert counts["position_item_count"] == 1
    assert counts["open_order_item_count"] == 2
    assert counts["own_execution_item_count"] == 0


def test_reconciliation_ok_when_fresh_clear_and_no_active_paper_orders() -> None:
    result = reconcile_fx_private_state_with_paper(private_readiness=_readiness(clear=True), paper_orders=())

    assert result.ok is True
    assert result.blocked_by == ()
    assert result.would_send_to_broker is False
    assert result.read_only is True


def test_reconciliation_blocks_existing_exchange_state_for_new_auto_entry() -> None:
    result = reconcile_fx_private_state_with_paper(
        private_readiness=_readiness(clear=False, positions=1, open_orders=20),
        paper_orders=(),
    )

    assert result.ok is False
    assert "account_not_clear_for_new_auto_entry" in result.blocked_by
    assert "exchange_positions_detected" in result.warnings
    assert "exchange_open_orders_detected" in result.warnings
    assert "exchange_open_orders_without_active_paper_orders" in result.warnings


def test_reconciliation_blocks_stale_private_state() -> None:
    result = reconcile_fx_private_state_with_paper(private_readiness=_readiness(fresh=False, clear=True), paper_orders=())

    assert result.ok is False
    assert "private_state_not_fresh" in result.blocked_by


def test_paper_order_counts_active_and_terminal() -> None:
    engine = PaperExecutionEngine()
    intent = _fx_intent()
    accepted = engine.submit_fx_execution_intent(intent, ts="2026-06-14T00:00:00Z")
    assert accepted.status.value == "accepted"
    counts = paper_order_counts(engine.all_orders())
    assert counts["active_paper_order_count"] == 1
    assert counts["terminal_paper_order_count"] == 0

    engine.cancel(intent.decision_id, ts="2026-06-14T00:00:01Z", reason="unit_cancel")
    counts = paper_order_counts(engine.all_orders())
    assert counts["active_paper_order_count"] == 0
    assert counts["terminal_paper_order_count"] == 1



def _service_input():
    return {
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


def test_reconciliation_reads_active_paper_orders_from_hot_ledger(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    intent_build = build_fx_paper_order_intent_from_service_input(
        _service_input(),
        decision_id="decision_recon_ledger_001",
        snapshot_id="snapshot_recon_ledger_001",
        forecast_id=None,
        parameter_set_id="params_001",
        logic_version="logic_test",
        side="buy",
        size=0.001,
        price=100.0,
        risk_gate_allowed=True,
        mode="PAPER_OR_REPLAY",
    )
    assert intent_build.intent is not None
    order = PaperExecutionEngine().submit_fx_execution_intent(intent_build.intent, ts="2026-06-14T00:00:00Z")
    record_paper_order(intent_build=intent_build, order=order, recorded_at="2026-06-14T00:00:01Z")

    result = reconcile_fx_private_state_with_paper_ledger(private_readiness=_readiness(clear=True))

    assert result.ok is True
    assert result.active_paper_order_count == 1
    assert result.terminal_paper_order_count == 0
    assert result.paper_order_ledger_path == str(default_paper_order_ledger_path(ensure=False))
    assert "active_paper_orders_without_exchange_open_orders" in result.warnings
    assert result.read_only is True
    assert result.would_send_to_broker is False


def test_reconciliation_ledger_summary_failsoft_malformed_rows(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("BTC_TS_AUTOTRADE_RUNTIME_ROOT", str(tmp_path / "btc_ts_hot"))
    path = default_paper_order_ledger_path(ensure=True)
    path.write_text("not-json\n", encoding="utf-8")

    result = reconcile_fx_private_state_with_paper_ledger(private_readiness=_readiness(clear=True))

    assert result.ok is True
    assert result.paper_order_ledger_skipped_rows == 1
    assert "paper_order_ledger_has_skipped_rows" in result.warnings
    assert result.read_only is True
    assert result.would_send_to_broker is False
