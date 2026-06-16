# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_paper_lifecycle.py
# desc: SR-FX paper/replay lifecycle tests. Simulation only; no broker calls.

from __future__ import annotations

from btcts.autotrade.execution.intents import (
    attach_execution_market,
    build_order_intent_from_decision,
    validate_fx_execution_market_intent,
)
from btcts.autotrade.execution.order_state import PaperOrderStatus
from btcts.autotrade.replay.paper_engine import PaperExecutionEngine, is_terminal_status


def _base_intent(risk_gate_allowed: bool = True):
    return build_order_intent_from_decision(
        decision_id="decision_fx_001",
        snapshot_id="snapshot_fx_001",
        forecast_id="forecast_001",
        parameter_set_id="params_001",
        logic_version="logic_test",
        side="buy",
        size=0.03,
        price=100.0,
        reason_codes=("unit_test",),
        risk_gate_allowed=risk_gate_allowed,
        mode="PAPER_OR_REPLAY",
    )


def _fx_intent(risk_gate_allowed: bool = True):
    return attach_execution_market(
        _base_intent(risk_gate_allowed=risk_gate_allowed),
        exchange="bitflyer",
        product_code="FX_BTC_JPY",
        market_type="fx",
        market_uid="bitflyer.fx.FX_BTC_JPY",
    )


def test_fx_execution_market_intent_accepts_only_fx_identity() -> None:
    intent = _fx_intent()

    assert validate_fx_execution_market_intent(intent) == ()


def test_spot_identity_is_rejected_for_fx_paper_submit() -> None:
    spot_intent = attach_execution_market(
        _base_intent(),
        exchange="bitflyer",
        product_code="BTC_JPY",
        market_type="spot",
        market_uid="bitflyer.spot.BTC_JPY",
    )
    engine = PaperExecutionEngine()

    order = engine.submit_fx_execution_intent(spot_intent, ts="2026-06-14T00:00:00Z")

    assert order.status == PaperOrderStatus.REJECTED
    assert order.reject_reason is not None
    assert "spot_identity_forbidden_for_execution" in order.reject_reason


def test_paper_order_partial_fill_then_final_fill() -> None:
    engine = PaperExecutionEngine()
    intent = _fx_intent()

    order = engine.submit_fx_execution_intent(intent, ts="2026-06-14T00:00:00Z")
    assert order.status == PaperOrderStatus.ACCEPTED

    order = engine.partial_fill(intent.decision_id, ts="2026-06-14T00:00:01Z", fill_size=0.01, fill_price=101.0)
    assert order is not None
    assert order.status == PaperOrderStatus.PARTIALLY_FILLED
    assert order.filled_size == 0.01
    assert round(order.remaining_size, 8) == 0.02
    assert is_terminal_status(order.status) is False

    order = engine.partial_fill(intent.decision_id, ts="2026-06-14T00:00:02Z", fill_size=0.02, fill_price=103.0)
    assert order is not None
    assert order.status == PaperOrderStatus.FILLED
    assert round(order.filled_size, 8) == 0.03
    assert round(order.remaining_size, 8) == 0.0
    assert round(float(order.fill_price), 8) == round(((101.0 * 0.01) + (103.0 * 0.02)) / 0.03, 8)
    assert is_terminal_status(order.status) is True


def test_rejected_risk_gate_still_blocks_fx_paper_submit() -> None:
    engine = PaperExecutionEngine()
    intent = _fx_intent(risk_gate_allowed=False)

    order = engine.submit_fx_execution_intent(intent, ts="2026-06-14T00:00:00Z")

    assert order.status == PaperOrderStatus.REJECTED
    assert order.reject_reason == "risk_gate_not_allowed"


def test_cancel_allowed_after_partial_fill_for_paper_replay() -> None:
    engine = PaperExecutionEngine()
    intent = _fx_intent()

    order = engine.submit_fx_execution_intent(intent, ts="2026-06-14T00:00:00Z")
    order = engine.partial_fill(intent.decision_id, ts="2026-06-14T00:00:01Z", fill_size=0.01, fill_price=101.0)
    order = engine.cancel(intent.decision_id, ts="2026-06-14T00:00:02Z", reason="unit_cancel")

    assert order is not None
    assert order.status == PaperOrderStatus.CANCELED
    assert order.filled_size == 0.01
    assert order.cancel_reason == "unit_cancel"
    assert is_terminal_status(order.status) is True
