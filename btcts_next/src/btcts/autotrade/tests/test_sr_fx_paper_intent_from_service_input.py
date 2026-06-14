# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_paper_intent_from_service_input.py
# desc: Build SR-FX paper order intents from read-only ExecutionMarketServiceInput. No broker calls.

from __future__ import annotations

from btcts.autotrade.execution.paper_intent import (
    build_fx_paper_order_intent_from_service_input,
    validate_execution_market_service_input_for_paper,
)
from btcts.autotrade.execution.order_state import PaperOrderStatus
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
        "capabilities": ["market_summary_anchor", "freshness_usable", "trusted_market_state", "structural_use_allowed"],
        "blocked_by": [],
        "warnings": ["execution_market_rest_baseline_not_continuous_ws_series"],
        "read_only": True,
        "would_send_to_broker": False,
    }
    data.update(overrides)
    return data


def _build(service_input=None, **overrides):
    kwargs = dict(
        service_input=service_input or _service_input(),
        decision_id="decision_paper_001",
        snapshot_id="snapshot_paper_001",
        forecast_id=None,
        parameter_set_id="params_fx_balanced_v0_1",
        logic_version="autotrade_logic_v0_1",
        side="buy",
        size=0.001,
        price=100.0,
    )
    kwargs.update(overrides)
    return build_fx_paper_order_intent_from_service_input(**kwargs)


def test_builds_fx_paper_order_intent_from_execution_market_service_input() -> None:
    result = _build()

    assert result.ok is True
    assert result.intent is not None
    assert result.blocked_by == ()
    assert result.read_only is True
    assert result.would_send_to_broker is False
    assert "paper_intent_from_rest_baseline_not_continuous_ws_series" in result.warnings
    assert result.intent.product_code == "FX_BTC_JPY"
    assert result.intent.market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert result.intent.market_role == "execution"
    assert result.service_input_used["service_input_role"] == "execution_market"
    assert result.intent.mode == "PAPER_OR_REPLAY"
    assert "execution_market_service_input" in result.intent.reason_codes


def test_paper_engine_accepts_intent_built_from_service_input() -> None:
    result = _build()
    assert result.intent is not None
    engine = PaperExecutionEngine()

    order = engine.submit_fx_execution_intent(result.intent, ts="2026-06-14T00:00:00Z")

    assert order.status == PaperOrderStatus.ACCEPTED
    assert order.intent.market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert order.intent.product_code == "FX_BTC_JPY"


def test_spot_service_input_is_blocked_before_paper_order() -> None:
    result = _build(
        service_input=_service_input(
            symbol_raw="BTC_JPY",
            market_uid="bitflyer.spot.BTC_JPY",
        )
    )

    assert result.ok is False
    assert result.intent is None
    assert "execution_product_code_mismatch" in result.blocked_by
    assert "execution_market_uid_mismatch" in result.blocked_by
    assert "spot_identity_forbidden_for_execution" in result.blocked_by
    assert result.would_send_to_broker is False


def test_stale_or_blocked_service_input_is_rejected() -> None:
    result = _build(
        service_input=_service_input(
            freshness="STALE",
            is_stale=True,
            blocked_by=["market_summary_stale"],
        )
    )

    assert result.ok is False
    assert result.intent is None
    assert "service_input_stale" in result.blocked_by
    assert "service_input_has_blockers" in result.blocked_by
    assert "market_summary_stale" in result.blocked_by


def test_service_input_must_be_read_only_and_non_broker_sending() -> None:
    result = _build(service_input=_service_input(read_only=False, would_send_to_broker=True))

    assert result.ok is False
    assert result.intent is None
    assert "service_input_not_read_only" in result.blocked_by
    assert "service_input_would_send_to_broker" in result.blocked_by


def test_paper_intent_schema_blocks_non_paper_mode_market_order_and_bad_size() -> None:
    from btcts.autotrade.execution.intents import OrderType

    result = _build(mode="LIVE_MIN_SIZE", order_type=OrderType.MARKET, size=0.0, price=None)

    assert result.ok is False
    assert result.intent is None
    assert "paper_intent_mode_must_be_paper_or_replay" in result.blocked_by
    assert "market_order_disabled_initially" in result.blocked_by
    assert "paper_intent_size_must_be_positive" in result.blocked_by


def test_validate_service_input_requires_autotrade_consumer() -> None:
    blocked, warnings = validate_execution_market_service_input_for_paper(
        _service_input(consumer_allowed=["workroom", "operator_ui"])
    )

    assert "autotrade_not_allowed_consumer" in blocked
    assert "paper_intent_from_rest_baseline_not_continuous_ws_series" in warnings
