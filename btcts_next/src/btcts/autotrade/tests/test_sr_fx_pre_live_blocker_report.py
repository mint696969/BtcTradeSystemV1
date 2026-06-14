# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_pre_live_blocker_report.py
# desc: SR-FX pre-live blocker report tests. Read-only; no broker calls/no mode changes.

from __future__ import annotations

from btcts.autotrade.execution.pre_live_blocker_report import build_sr_fx_pre_live_blocker_report


def _public(ok: bool = False) -> dict:
    return {
        "public_market_readiness": {
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
            "contract_version": "unit_public",
        }
    }


def _private(clear: bool = False) -> dict:
    return {
        "readiness": {
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "private_state_known_and_fresh": True,
            "account_clear_for_new_auto_entry": clear,
            "existing_positions_detected": not clear,
            "existing_open_orders_detected": not clear,
            "order_send_allowed": False,
            "reason": "ok_clear" if clear else "account_not_clear_for_new_auto_entry",
        }
    }


def _live(ready: bool = False) -> dict:
    return {
        "live_readiness_contract": {
            "ready": ready,
            "product_code": "FX_BTC_JPY",
            "market_uid": "bitflyer.fx.FX_BTC_JPY",
            "public_market_ok": ready,
            "private_state_known_and_fresh": True,
            "account_clear_for_new_auto_entry": ready,
            "reconciliation_ok": ready,
            "preview_ok": ready,
            "bitflyer_order_send_enabled": ready,
            "autotrade_live_order_enabled": ready,
            "order_sender_implemented": ready,
            "blocked_by": [] if ready else ["public_market_not_ready", "account_not_clear_for_new_auto_entry", "order_sender_not_implemented"],
            "warnings": ["unit_warning"] if not ready else [],
            "read_only": True,
            "would_send_to_broker": False,
            "contract_version": "unit_live",
        }
    }


def _autotrade(ready: bool = False) -> dict:
    return {
        "readiness": {
            "ready": ready,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "transition_allowed": True,
            "human_confirmation_required": True,
            "human_confirmed": True,
            "blocked_by": [] if ready else ["sr_fx_live_readiness_not_ready", "public_market_not_ready"],
            "warnings": ["unit_warning"] if not ready else [],
            "sr_fx_live_readiness": {"present": True},
            "read_only": True,
            "would_send_to_broker": False,
        }
    }


def test_pre_live_blocker_report_collects_current_blockers() -> None:
    report = build_sr_fx_pre_live_blocker_report(
        public_market_readiness=_public(ok=False),
        private_readiness=_private(clear=False),
        live_readiness_contract=_live(ready=False),
        autotrade_readiness=_autotrade(ready=False),
    )

    assert report.ok is False
    assert report.ready_for_live is False
    assert "fx_public_ws_preflight_not_ok" in report.primary_blockers
    assert "account_not_clear_for_new_auto_entry" in report.primary_blockers
    assert "order_sender_not_implemented" in report.primary_blockers
    assert "sr_fx_live_readiness_not_ready" in report.primary_blockers
    assert report.sections["public_market"].ok is False
    assert report.sections["private_account"].ok is False
    assert report.sections["live_contract"].ok is False
    assert report.sections["autotrade_readiness"].ok is False
    assert report.would_send_to_broker is False
    assert report.read_only is True
    assert report.mode_changed is False


def test_pre_live_blocker_report_can_be_ready_only_when_all_sections_ready() -> None:
    report = build_sr_fx_pre_live_blocker_report(
        public_market_readiness=_public(ok=True),
        private_readiness=_private(clear=True),
        live_readiness_contract=_live(ready=True),
        autotrade_readiness=_autotrade(ready=True),
    )

    assert report.ok is True
    assert report.ready_for_live is True
    assert report.primary_blockers == ()
    assert all(section.ok for section in report.sections.values())
    assert report.would_send_to_broker is False
    assert report.read_only is True


def test_pre_live_blocker_report_blocks_unexpected_broker_send_signal() -> None:
    live = _live(ready=True)
    live["live_readiness_contract"]["would_send_to_broker"] = True

    report = build_sr_fx_pre_live_blocker_report(
        public_market_readiness=_public(ok=True),
        private_readiness=_private(clear=True),
        live_readiness_contract=live,
        autotrade_readiness=_autotrade(ready=True),
    )

    assert report.ok is False
    assert "unexpected_broker_send_signal" in report.primary_blockers
    assert report.would_send_to_broker is True
