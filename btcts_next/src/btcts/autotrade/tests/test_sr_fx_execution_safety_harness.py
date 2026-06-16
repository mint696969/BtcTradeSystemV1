# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_execution_safety_harness.py
# desc: SR-FX execution safety harness tests. Read-only; no broker calls/no mode changes.

from __future__ import annotations

from btcts.autotrade.execution.safety_harness import evaluate_sr_fx_execution_safety_harness


def _public(ok: bool = True) -> dict:
    return {
        "ok": ok,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "blocked_by": [] if ok else ["fx_public_ws_preflight_not_ok"],
        "warnings": [],
        "read_only": True,
        "would_send_to_broker": False,
    }


def _private(clear: bool = True) -> dict:
    return {
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "private_state_known_and_fresh": True,
        "account_clear_for_new_auto_entry": clear,
        "read_only": True,
        "would_send_to_broker": False,
    }


def _live(ready: bool = True, *, active_orders: int = 0, paper_position_size: float = 0.0) -> dict:
    return {
        "ready": ready,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "active_paper_order_count": active_orders,
        "paper_position_size": paper_position_size,
        "paper_position_side": "long" if paper_position_size > 0 else "flat",
        "order_sender_implemented": ready,
        "bitflyer_order_send_enabled": ready,
        "autotrade_live_order_enabled": ready,
        "blocked_by": [] if ready else ["order_sender_not_implemented"],
        "warnings": [],
        "read_only": True,
        "would_send_to_broker": False,
    }


def _autotrade(ready: bool = True) -> dict:
    return {
        "ready": ready,
        "blocked_by": [] if ready else ["sr_fx_live_readiness_not_ready"],
        "warnings": [],
        "read_only": True,
        "would_send_to_broker": False,
    }


def test_safety_harness_allows_only_clean_ready_inputs() -> None:
    result = evaluate_sr_fx_execution_safety_harness(
        public_market_readiness=_public(ok=True),
        private_readiness=_private(clear=True),
        live_readiness_contract=_live(ready=True),
        autotrade_readiness=_autotrade(ready=True),
        target_mode="LIVE_MIN_SIZE",
    )

    assert result.ok is True
    assert result.blocked_by == ()
    assert result.product_code == "FX_BTC_JPY"
    assert result.market_uid == "bitflyer.fx.FX_BTC_JPY"
    assert result.read_only is True
    assert result.would_send_to_broker is False
    assert result.mode_changed is False


def test_safety_harness_blocks_active_paper_orders_and_open_paper_position() -> None:
    result = evaluate_sr_fx_execution_safety_harness(
        public_market_readiness=_public(ok=True),
        private_readiness=_private(clear=True),
        live_readiness_contract=_live(ready=True, active_orders=2, paper_position_size=0.001),
        autotrade_readiness=_autotrade(ready=True),
        target_mode="LIVE_MIN_SIZE",
    )

    assert result.ok is False
    assert "active_paper_orders_present" in result.blocked_by
    assert "paper_position_open" in result.blocked_by
    assert result.active_paper_order_count == 2
    assert result.paper_position_size == 0.001
    assert result.paper_position_side == "long"
    assert result.read_only is True
    assert result.would_send_to_broker is False


def test_safety_harness_blocks_kill_switch_and_unexpected_broker_send_signal() -> None:
    public = _public(ok=True)
    public["would_send_to_broker"] = True

    result = evaluate_sr_fx_execution_safety_harness(
        public_market_readiness=public,
        private_readiness=_private(clear=True),
        live_readiness_contract=_live(ready=True),
        autotrade_readiness=_autotrade(ready=True),
        target_mode="LIVE_MIN_SIZE",
        kill_switch_active=True,
        kill_switch_reason="unit_test",
    )

    assert result.ok is False
    assert "kill_switch_active" in result.blocked_by
    assert "public_market_attempted_broker_send" in result.blocked_by
    assert "kill_switch_reason:unit_test" in result.warnings
    assert result.would_send_to_broker is False
    assert result.mode_changed is False


def test_safety_harness_blocks_non_live_target_and_unready_contracts() -> None:
    result = evaluate_sr_fx_execution_safety_harness(
        public_market_readiness=_public(ok=False),
        private_readiness=_private(clear=False),
        live_readiness_contract=_live(ready=False),
        autotrade_readiness=_autotrade(ready=False),
        target_mode="PAPER_OR_REPLAY",
    )

    assert result.ok is False
    assert "target_mode_not_live_capable" in result.blocked_by
    assert "public_market_not_ready" in result.blocked_by
    assert "account_not_clear_for_new_auto_entry" in result.blocked_by
    assert "sr_fx_live_readiness_not_ready" in result.blocked_by
    assert "autotrade_readiness_not_ready" in result.blocked_by
    assert result.read_only is True
    assert result.would_send_to_broker is False
