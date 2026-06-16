# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_mode_change_request_wiring.py
# desc: Guards parameter bundle readiness controls through mode-change command requests and Operator UI.

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Tuple

from btcts.apps.operator_ui.views import autotrade_page
from btcts.autotrade.execution import mode_change_request
from btcts.autotrade.modes import AutoTradeMode


@dataclass(frozen=True)
class _FakeRuntime:
    live_ready: bool = True


@dataclass(frozen=True)
class _FakeObserverRuns:
    latest_run_id: str = "obs_001"
    latest_blocked_by: Tuple[str, ...] = ()
    latest_would_send_to_broker: bool = False
    latest_bounded: bool = True


@dataclass(frozen=True)
class _FakeHealth:
    health_state: str = "ok"
    observer_run_fresh: bool = True
    observer_runs: _FakeObserverRuns = _FakeObserverRuns()
    runtime: _FakeRuntime = _FakeRuntime()


@dataclass(frozen=True)
class _FakeReadiness:
    current_mode: AutoTradeMode = AutoTradeMode.SHADOW
    target_mode: AutoTradeMode = AutoTradeMode.PAPER_OR_REPLAY
    ready: bool = True
    blocked_by: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    health: _FakeHealth = _FakeHealth()
    parameter_bundle_runtime: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ready": self.ready,
            "current_mode": self.current_mode.value,
            "target_mode": self.target_mode.value,
            "blocked_by": list(self.blocked_by),
            "warnings": list(self.warnings),
            "health": {
                "health_state": self.health.health_state,
                "observer_run_fresh": self.health.observer_run_fresh,
                "observer_runs": {
                    "latest_run_id": self.health.observer_runs.latest_run_id,
                    "latest_blocked_by": list(self.health.observer_runs.latest_blocked_by),
                    "latest_would_send_to_broker": self.health.observer_runs.latest_would_send_to_broker,
                    "latest_bounded": self.health.observer_runs.latest_bounded,
                },
            },
            "parameter_bundle_runtime": self.parameter_bundle_runtime,
            "would_send_to_broker": False,
        }


def _runtime_status() -> Dict[str, Any]:
    return {
        "schema_version": "autotrade_parameter_bundle_runtime_status.v1",
        "registry_exists": True,
        "event_ledger_exists": True,
        "registry": {"active_shadow_bundle_id": "pb_shadow"},
        "event_count": 1,
        "would_send_to_broker": False,
    }


def test_mode_change_request_passes_parameter_bundle_readiness_controls(monkeypatch) -> None:
    calls = {}

    def fake_evaluate_autotrade_live_readiness(**kwargs):
        calls.update(kwargs)
        return _FakeReadiness(parameter_bundle_runtime=_runtime_status())

    monkeypatch.setattr(mode_change_request, "evaluate_autotrade_live_readiness", fake_evaluate_autotrade_live_readiness)

    record, readiness = mode_change_request.build_mode_change_command_request_record(
        current_mode="SHADOW",
        target_mode="PAPER_OR_REPLAY",
        human_confirmed=True,
        allow_warnings=True,
        enforce_parameter_bundle_runtime=False,
        required_parameter_bundle_stage="shadow",
    )

    note = json.loads(record.command.note)

    assert calls["enforce_parameter_bundle_runtime"] is False
    assert calls["required_parameter_bundle_stage"] == "shadow"
    assert readiness.parameter_bundle_runtime == _runtime_status()
    assert note["parameter_bundle_runtime"]["registry"]["active_shadow_bundle_id"] == "pb_shadow"
    assert note["would_send_to_broker"] is False


def test_operator_ui_mode_change_request_passes_parameter_bundle_controls(monkeypatch) -> None:
    calls = {}

    class _FakeSubmitResult:
        def to_dict(self):
            return {
                "accepted": True,
                "blocked_by": [],
                "ledger_path": "commands.jsonl",
                "command_record": {"command_id": "cmd_001"},
                "readiness": _FakeReadiness(parameter_bundle_runtime=_runtime_status()).to_dict(),
            }

    def fake_submit_mode_change_command_request(**kwargs):
        calls.update(kwargs)
        return _FakeSubmitResult()

    monkeypatch.setattr(autotrade_page, "submit_mode_change_command_request", fake_submit_mode_change_command_request)

    result = autotrade_page._submit_mode_change_request(
        current_mode="SHADOW",
        target_mode="PAPER_OR_REPLAY",
        human_confirmed=True,
        allow_warnings=True,
        enforce_parameter_bundle_runtime=False,
        required_parameter_bundle_stage="shadow",
    )

    assert calls["enforce_parameter_bundle_runtime"] is False
    assert calls["required_parameter_bundle_stage"] == "shadow"
    assert result["readiness"]["parameter_bundle_runtime"]["registry"]["active_shadow_bundle_id"] == "pb_shadow"
    assert result["readiness"]["enforce_parameter_bundle_runtime"] is False
    assert result["readiness"]["required_parameter_bundle_stage"] == "shadow"
    assert result["would_send_to_broker"] is False
