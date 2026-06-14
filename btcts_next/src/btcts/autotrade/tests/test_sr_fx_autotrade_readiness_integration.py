# path: ./btcts_next/src/btcts/autotrade/tests/test_sr_fx_autotrade_readiness_integration.py
# desc: SR-FX contract integration into AutoTrade live readiness. Read-only; no broker calls.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from btcts.autotrade.readiness import evaluate_autotrade_live_readiness


@dataclass(frozen=True)
class DummyRuntime:
    live_ready: bool
    blocked_by: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {"live_ready": self.live_ready, "blocked_by": list(self.blocked_by), "warnings": list(self.warnings)}


@dataclass(frozen=True)
class DummyObserverRuns:
    latest_blocked_by: Tuple[str, ...] = ()
    latest_run_id: str = "run_001"
    latest_would_send_to_broker: bool = False
    latest_bounded: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latest_blocked_by": list(self.latest_blocked_by),
            "latest_run_id": self.latest_run_id,
            "latest_would_send_to_broker": self.latest_would_send_to_broker,
            "latest_bounded": self.latest_bounded,
        }


@dataclass(frozen=True)
class DummyLedgerSummary:
    def to_dict(self) -> Dict[str, Any]:
        return {}


@dataclass(frozen=True)
class DummyHealth:
    health_state: str = "ok"
    runtime: DummyRuntime = DummyRuntime(live_ready=True)
    observer_runs: DummyObserverRuns = DummyObserverRuns()
    shadow_decisions: DummyLedgerSummary = DummyLedgerSummary()
    forecast_outcomes: DummyLedgerSummary = DummyLedgerSummary()
    observer_run_fresh: bool = True
    blocked_by: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "health_state": self.health_state,
            "runtime": self.runtime.to_dict(),
            "observer_runs": self.observer_runs.to_dict(),
            "shadow_decisions": self.shadow_decisions.to_dict(),
            "forecast_outcomes": self.forecast_outcomes.to_dict(),
            "observer_run_fresh": self.observer_run_fresh,
            "blocked_by": list(self.blocked_by),
            "warnings": list(self.warnings),
        }


def _contract(ready: bool = True) -> dict:
    return {
        "ready": ready,
        "product_code": "FX_BTC_JPY",
        "market_uid": "bitflyer.fx.FX_BTC_JPY",
        "private_state_known_and_fresh": True,
        "account_clear_for_new_auto_entry": ready,
        "reconciliation_ok": ready,
        "preview_ok": ready,
        "bitflyer_order_send_enabled": ready,
        "autotrade_live_order_enabled": ready,
        "order_sender_implemented": ready,
        "blocked_by": [] if ready else ["account_not_clear_for_new_auto_entry"],
        "warnings": ["unit_warning"],
        "would_send_to_broker": False,
        "read_only": True,
        "contract_version": "unit",
    }


def test_live_readiness_blocks_when_sr_fx_contract_not_ready(monkeypatch) -> None:
    import btcts.autotrade.readiness as readiness

    monkeypatch.setattr(readiness, "build_autotrade_runtime_health_snapshot", lambda **kwargs: DummyHealth())

    result = evaluate_autotrade_live_readiness(
        current_mode="ARMED_DRY_RUN",
        target_mode="LIVE_MIN_SIZE",
        human_confirmed=True,
        allow_warnings=True,
        sr_fx_live_contract=_contract(ready=False),
    )

    assert result.ready is False
    assert "sr_fx_live_readiness_not_ready" in result.blocked_by
    assert "account_not_clear_for_new_auto_entry" in result.blocked_by
    assert result.sr_fx_live_readiness is not None
    assert result.sr_fx_live_readiness["ready"] is False
    assert result.would_send_to_broker is False


def test_live_readiness_allows_only_when_runtime_and_sr_fx_contract_ready(monkeypatch) -> None:
    import btcts.autotrade.readiness as readiness

    monkeypatch.setattr(readiness, "build_autotrade_runtime_health_snapshot", lambda **kwargs: DummyHealth())

    result = evaluate_autotrade_live_readiness(
        current_mode="ARMED_DRY_RUN",
        target_mode="LIVE_MIN_SIZE",
        human_confirmed=True,
        allow_warnings=True,
        sr_fx_live_contract=_contract(ready=True),
    )

    assert result.ready is True
    assert result.blocked_by == ()
    assert result.sr_fx_live_readiness is not None
    assert result.sr_fx_live_readiness["ready"] is True
    assert result.would_send_to_broker is False


def test_live_readiness_blocks_missing_sr_fx_contract_for_live_target(monkeypatch) -> None:
    import btcts.autotrade.readiness as readiness

    monkeypatch.setattr(readiness, "build_autotrade_runtime_health_snapshot", lambda **kwargs: DummyHealth())
    monkeypatch.setattr(readiness, "_load_sr_fx_live_readiness_contract", lambda path=None: None)

    result = evaluate_autotrade_live_readiness(
        current_mode="ARMED_DRY_RUN",
        target_mode="LIVE_MIN_SIZE",
        human_confirmed=True,
        allow_warnings=True,
    )

    assert result.ready is False
    assert "sr_fx_live_readiness_contract_missing" in result.blocked_by
    assert "sr_fx_live_readiness_not_ready" in result.blocked_by


def test_non_live_target_does_not_require_sr_fx_contract(monkeypatch) -> None:
    import btcts.autotrade.readiness as readiness

    monkeypatch.setattr(readiness, "build_autotrade_runtime_health_snapshot", lambda **kwargs: DummyHealth())

    result = evaluate_autotrade_live_readiness(
        current_mode="SHADOW",
        target_mode="PAPER_OR_REPLAY",
        human_confirmed=True,
        allow_warnings=True,
        sr_fx_live_contract=None,
    )

    assert "sr_fx_live_readiness_contract_missing" not in result.blocked_by
    assert result.sr_fx_live_readiness is None


def test_live_readiness_reads_persisted_sr_fx_contract_file(monkeypatch, tmp_path) -> None:
    import json
    import btcts.autotrade.readiness as readiness

    monkeypatch.setattr(readiness, "build_autotrade_runtime_health_snapshot", lambda **kwargs: DummyHealth())
    contract_path = tmp_path / "bitflyer_fx_live_readiness_contract.json"
    contract_path.write_text(
        json.dumps({"live_readiness_contract": _contract(ready=False)}),
        encoding="utf-8",
    )

    result = evaluate_autotrade_live_readiness(
        current_mode="ARMED_DRY_RUN",
        target_mode="LIVE_MIN_SIZE",
        human_confirmed=True,
        allow_warnings=True,
        sr_fx_live_contract_path=contract_path,
    )

    assert result.ready is False
    assert result.sr_fx_live_readiness is not None
    assert result.sr_fx_live_readiness["present"] is True
    assert result.sr_fx_live_readiness["source"] == str(contract_path)
    assert "sr_fx_live_readiness_not_ready" in result.blocked_by


def test_autotrade_readiness_propagates_public_market_blocker_from_sr_fx_contract(monkeypatch) -> None:
    import btcts.autotrade.readiness as readiness

    monkeypatch.setattr(readiness, "build_autotrade_runtime_health_snapshot", lambda **kwargs: DummyHealth())
    contract = _contract(ready=False)
    contract["public_market_ok"] = False
    contract["blocked_by"] = ["public_market_not_ready", "fx_public_ws_preflight_not_ok"]
    contract["warnings"] = ["ws_executions_not_ok:RuntimeError"]

    result = evaluate_autotrade_live_readiness(
        current_mode="ARMED_DRY_RUN",
        target_mode="LIVE_MIN_SIZE",
        human_confirmed=True,
        allow_warnings=True,
        sr_fx_live_contract=contract,
    )

    assert result.ready is False
    assert "sr_fx_live_readiness_not_ready" in result.blocked_by
    assert "public_market_not_ready" in result.blocked_by
    assert "fx_public_ws_preflight_not_ok" in result.blocked_by
    assert "ws_executions_not_ok:RuntimeError" in result.warnings
    assert result.would_send_to_broker is False
    assert result.read_only is True
