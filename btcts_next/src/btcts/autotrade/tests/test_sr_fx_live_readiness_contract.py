# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_live_readiness_contract.py
# desc: SR-FX live readiness contract tests. Read-only; no broker calls.

from __future__ import annotations

from btcts.autotrade.execution.intents import attach_execution_market, build_order_intent_from_decision
from btcts.autotrade.execution.live_readiness_contract import evaluate_fx_live_readiness_contract
from btcts.autotrade.execution.order_preview import build_bitflyer_fx_manual_order_preview
from btcts.autotrade.execution.reconciliation import reconcile_fx_private_state_with_paper


def _readiness(*, fresh: bool = True, clear: bool = True) -> dict:
    return {
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "private_state_known_and_fresh": fresh,
        "account_clear_for_new_auto_entry": clear,
        "existing_positions_detected": not clear,
        "existing_open_orders_detected": not clear,
        "order_send_allowed": False,
        "reason": "ok_clear" if clear else "account_not_clear_for_new_auto_entry",
        "account_state_summary": {
            "position_item_count": 0 if clear else 1,
            "open_order_item_count": 0 if clear else 20,
            "own_execution_item_count": 0,
        },
    }


def _public_market(ok: bool = True) -> dict:
    return {
        "ok": ok,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "market_role": "execution",
        "rest_market_ok": True,
        "ws_market_ok": ok,
        "require_ws_ok": True,
        "blocked_by": [] if ok else ["fx_public_ws_preflight_not_ok"],
        "warnings": [] if ok else ["ws_executions_not_ok:RuntimeError"],
        "read_only": True,
        "would_send_to_broker": False,
        "contract_version": "unit_public_market",
    }


def _intent():
    base = build_order_intent_from_decision(
        decision_id="decision_live_contract_001",
        snapshot_id="snapshot_live_contract_001",
        forecast_id=None,
        parameter_set_id="params_001",
        logic_version="logic_test",
        side="buy",
        size=0.001,
        price=100.0,
        reason_codes=("unit_test",),
        risk_gate_allowed=True,
        mode="LIVE_MIN_SIZE",
    )
    return attach_execution_market(
        base,
        exchange="bitflyer",
        product_code="FX_BTC_JPY",
        market_type="fx",
        market_uid="bitflyer.fx.FX_BTC_JPY",
    )


def _parts(readiness: dict):
    reconciliation = reconcile_fx_private_state_with_paper(private_readiness=readiness, paper_orders=())
    preview = build_bitflyer_fx_manual_order_preview(_intent(), private_readiness=readiness)
    return reconciliation, preview


def test_live_contract_not_ready_until_sender_exists_even_when_clear_and_flags_enabled() -> None:
    readiness = _readiness(clear=True)
    reconciliation, preview = _parts(readiness)

    result = evaluate_fx_live_readiness_contract(
        private_readiness=readiness,
        reconciliation=reconciliation,
        order_preview=preview,
        public_market_readiness=_public_market(ok=True),
        bitflyer_order_send_enabled=True,
        autotrade_live_order_enabled=True,
        order_sender_implemented=False,
    )

    assert result.ready is False
    assert result.public_market_ok is True
    assert "order_sender_not_implemented" in result.blocked_by
    assert result.would_send_to_broker is False
    assert result.read_only is True


def test_live_contract_blocks_public_market_not_ready() -> None:
    readiness = _readiness(clear=True)
    reconciliation, preview = _parts(readiness)

    result = evaluate_fx_live_readiness_contract(
        private_readiness=readiness,
        reconciliation=reconciliation,
        order_preview=preview,
        public_market_readiness=_public_market(ok=False),
        bitflyer_order_send_enabled=True,
        autotrade_live_order_enabled=True,
        order_sender_implemented=True,
    )

    assert result.ready is False
    assert result.public_market_ok is False
    assert "public_market_not_ready" in result.blocked_by
    assert "fx_public_ws_preflight_not_ok" in result.blocked_by
    assert "ws_executions_not_ok:RuntimeError" in result.warnings


def test_live_contract_blocks_missing_public_market_readiness() -> None:
    readiness = _readiness(clear=True)
    reconciliation, preview = _parts(readiness)

    result = evaluate_fx_live_readiness_contract(
        private_readiness=readiness,
        reconciliation=reconciliation,
        order_preview=preview,
        bitflyer_order_send_enabled=True,
        autotrade_live_order_enabled=True,
        order_sender_implemented=True,
    )

    assert result.ready is False
    assert result.public_market_ok is False
    assert "public_market_readiness_missing" in result.blocked_by


def test_live_contract_blocks_existing_exchange_state() -> None:
    readiness = _readiness(clear=False)
    reconciliation, preview = _parts(readiness)

    result = evaluate_fx_live_readiness_contract(
        private_readiness=readiness,
        reconciliation=reconciliation,
        order_preview=preview,
        public_market_readiness=_public_market(ok=True),
        bitflyer_order_send_enabled=False,
        autotrade_live_order_enabled=False,
        order_sender_implemented=False,
    )

    assert result.ready is False
    assert "account_not_clear_for_new_auto_entry" in result.blocked_by
    assert "reconciliation_not_clean" in result.blocked_by
    assert "order_preview_not_ok" in result.blocked_by
    assert "bitflyer_order_send_flag_disabled" in result.blocked_by
    assert "autotrade_live_order_flag_disabled" in result.blocked_by
    assert result.would_send_to_broker is False


def test_live_contract_blocks_stale_private_state() -> None:
    readiness = _readiness(fresh=False, clear=True)
    reconciliation, preview = _parts(readiness)

    result = evaluate_fx_live_readiness_contract(
        private_readiness=readiness,
        reconciliation=reconciliation,
        order_preview=preview,
        public_market_readiness=_public_market(ok=True),
        bitflyer_order_send_enabled=True,
        autotrade_live_order_enabled=True,
        order_sender_implemented=True,
    )

    assert result.ready is False
    assert "private_state_not_fresh" in result.blocked_by


def test_live_contract_can_be_ready_only_when_all_inputs_and_sender_are_ready() -> None:
    readiness = _readiness(clear=True)
    reconciliation, preview = _parts(readiness)

    result = evaluate_fx_live_readiness_contract(
        private_readiness=readiness,
        reconciliation=reconciliation,
        order_preview=preview,
        public_market_readiness=_public_market(ok=True),
        bitflyer_order_send_enabled=True,
        autotrade_live_order_enabled=True,
        order_sender_implemented=True,
    )

    assert result.ready is True
    assert result.public_market_ok is True
    assert result.blocked_by == ()
    assert result.would_send_to_broker is False
    assert result.read_only is True


def test_live_contract_rejects_non_live_target_mode() -> None:
    readiness = _readiness(clear=True)
    reconciliation, preview = _parts(readiness)

    result = evaluate_fx_live_readiness_contract(
        private_readiness=readiness,
        reconciliation=reconciliation,
        order_preview=preview,
        public_market_readiness=_public_market(ok=True),
        target_mode="PAPER_OR_REPLAY",
        bitflyer_order_send_enabled=True,
        autotrade_live_order_enabled=True,
        order_sender_implemented=True,
    )

    assert result.ready is False
    assert "target_mode_not_live_capable" in result.blocked_by



def test_live_contract_blocks_active_paper_orders_from_ledger_reconciliation() -> None:
    readiness = _readiness(clear=True)
    reconciliation, preview = _parts(readiness)
    reconciliation = type(reconciliation)(
        ok=reconciliation.ok,
        product_code=reconciliation.product_code,
        market_uid=reconciliation.market_uid,
        private_state_known_and_fresh=reconciliation.private_state_known_and_fresh,
        account_clear_for_new_auto_entry=reconciliation.account_clear_for_new_auto_entry,
        position_item_count=reconciliation.position_item_count,
        open_order_item_count=reconciliation.open_order_item_count,
        own_execution_item_count=reconciliation.own_execution_item_count,
        active_paper_order_count=1,
        terminal_paper_order_count=0,
        paper_order_ledger_path="D:/btc_ts_hot/autotrade/decisions/paper_orders.jsonl",
        paper_order_ledger_skipped_rows=0,
        blocked_by=reconciliation.blocked_by,
        warnings=reconciliation.warnings,
        would_send_to_broker=False,
        read_only=True,
    )

    result = evaluate_fx_live_readiness_contract(
        private_readiness=readiness,
        reconciliation=reconciliation,
        order_preview=preview,
        public_market_readiness=_public_market(ok=True),
        bitflyer_order_send_enabled=True,
        autotrade_live_order_enabled=True,
        order_sender_implemented=True,
    )

    assert result.ready is False
    assert "active_paper_orders_present" in result.blocked_by
    assert result.active_paper_order_count == 1
    assert result.paper_order_ledger_path == "D:/btc_ts_hot/autotrade/decisions/paper_orders.jsonl"
    assert result.would_send_to_broker is False
    assert result.read_only is True
