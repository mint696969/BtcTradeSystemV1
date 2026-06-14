# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_order_preview.py
# desc: SR-FX order preview tests. Preview only; no broker calls.

from __future__ import annotations

from btcts.autotrade.execution.intents import (
    OrderType,
    attach_execution_market,
    build_order_intent_from_decision,
)
from btcts.autotrade.execution.order_preview import (
    build_bitflyer_fx_manual_order_preview,
    build_bitflyer_fx_order_request_preview,
)


def _readiness(clear: bool = True) -> dict:
    return {
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "private_state_known_and_fresh": True,
        "account_clear_for_new_auto_entry": clear,
        "existing_positions_detected": not clear,
        "existing_open_orders_detected": not clear,
        "order_send_allowed": False,
        "reason": "ok_clear" if clear else "account_not_clear_for_new_auto_entry",
    }


def _intent(*, price: float | None = 100.0, market_type: str = "fx", product_code: str = "FX_BTC_JPY", market_uid: str = "bitflyer.fx.FX_BTC_JPY"):
    base = build_order_intent_from_decision(
        decision_id="decision_preview_001",
        snapshot_id="snapshot_preview_001",
        forecast_id=None,
        parameter_set_id="params_001",
        logic_version="logic_test",
        side="buy",
        size=0.001,
        price=price,
        reason_codes=("unit_test",),
        risk_gate_allowed=True,
        mode="ARMED_DRY_RUN",
    )
    return attach_execution_market(
        base,
        exchange="bitflyer",
        product_code=product_code,
        market_type=market_type,
        market_uid=market_uid,
    )


def test_build_bitflyer_fx_order_request_preview_limit() -> None:
    preview = build_bitflyer_fx_order_request_preview(_intent())

    assert preview.product_code == "FX_BTC_JPY"
    assert preview.child_order_type == "LIMIT"
    assert preview.side == "BUY"
    assert preview.size == 0.001
    assert preview.price == 100.0


def test_manual_preview_ok_when_fx_identity_and_account_clear() -> None:
    result = build_bitflyer_fx_manual_order_preview(_intent(), private_readiness=_readiness(clear=True))

    assert result.ok is True
    assert result.broker_request_preview is not None
    assert result.would_send_to_broker is False
    assert result.send_allowed is False
    assert result.order_send_allowed is False
    assert result.preview_only is True
    assert "preview_only_no_broker_send" in result.warnings


def test_manual_preview_blocks_when_account_not_clear() -> None:
    result = build_bitflyer_fx_manual_order_preview(_intent(), private_readiness=_readiness(clear=False))

    assert result.ok is False
    assert result.broker_request_preview is None
    assert "account_not_clear_for_new_auto_entry" in result.blocked_by
    assert "existing_positions_detected" in result.warnings
    assert "existing_open_orders_detected" in result.warnings
    assert result.would_send_to_broker is False


def test_manual_preview_rejects_spot_identity() -> None:
    result = build_bitflyer_fx_manual_order_preview(
        _intent(market_type="spot", product_code="BTC_JPY", market_uid="bitflyer.spot.BTC_JPY"),
        private_readiness=_readiness(clear=True),
    )

    assert result.ok is False
    assert "spot_identity_forbidden_for_execution" in result.blocked_by
    assert result.would_send_to_broker is False


def test_manual_preview_requires_fresh_private_state() -> None:
    readiness = _readiness(clear=True)
    readiness["private_state_known_and_fresh"] = False

    result = build_bitflyer_fx_manual_order_preview(_intent(), private_readiness=readiness)

    assert result.ok is False
    assert "private_state_not_fresh" in result.blocked_by


def test_manual_preview_blocks_market_order_initially() -> None:
    intent = _intent()
    intent = type(intent)(**{**intent.to_dict(), "side": intent.side, "order_type": OrderType.MARKET})

    result = build_bitflyer_fx_manual_order_preview(intent, private_readiness=_readiness(clear=True))

    assert result.ok is False
    assert "market_order_disabled_initially" in result.blocked_by
    assert result.would_send_to_broker is False
