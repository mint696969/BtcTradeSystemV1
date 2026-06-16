# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_mode_recheck_controls.py
# desc: Guards replay of parameter bundle readiness controls during mode-change apply recheck.

from __future__ import annotations

import json
from typing import Any, Dict

from btcts.autotrade.execution.command_ledger import CommandLedgerRecord, append_command_ledger_record
from btcts.autotrade.execution.command_request import CommandRequest, CommandType
from btcts.autotrade.execution import mode_command_applier
from btcts.autotrade.execution.mode_change_request import build_mode_change_command_request_record
from btcts.autotrade.modes import AutoTradeMode


def _parameter_bundle_runtime() -> Dict[str, Any]:
    return {
        "schema_version": "autotrade_parameter_bundle_runtime_status.v1",
        "registry_exists": True,
        "event_ledger_exists": True,
        "registry": {"active_shadow_bundle_id": "pb_shadow"},
        "event_count": 1,
        "would_send_to_broker": False,
    }


class _FakeRuntime:
    live_ready = True


class _FakeObserverRuns:
    latest_run_id = "obs_recheck_controls"
    latest_blocked_by = ()
    latest_would_send_to_broker = False
    latest_bounded = True


class _FakeHealth:
    health_state = "ok"
    observer_run_fresh = True
    observer_runs = _FakeObserverRuns()
    runtime = _FakeRuntime()


class _FakeReadiness:
    current_mode = AutoTradeMode.SHADOW
    target_mode = AutoTradeMode.PAPER_OR_REPLAY
    ready = True
    blocked_by = ()
    warnings = ()
    health = _FakeHealth()
    parameter_bundle_runtime = _parameter_bundle_runtime()

    def to_dict(self):
        return {
            "ready": True,
            "current_mode": self.current_mode.value,
            "target_mode": self.target_mode.value,
            "blocked_by": [],
            "warnings": [],
            "health": {
                "health_state": self.health.health_state,
                "observer_run_fresh": self.health.observer_run_fresh,
                "observer_runs": {
                    "latest_run_id": self.health.observer_runs.latest_run_id,
                    "latest_blocked_by": [],
                    "latest_would_send_to_broker": False,
                    "latest_bounded": True,
                },
            },
            "parameter_bundle_runtime": self.parameter_bundle_runtime,
            "would_send_to_broker": False,
        }


def _mode_change_record_with_controls() -> CommandLedgerRecord:
    note = json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": True,
            "current_mode": "SHADOW",
            "target_mode": "PAPER_OR_REPLAY",
            "blocked_by": [],
            "warnings": [],
            "health_state": "ok",
            "observer_run_fresh": True,
            "observer_latest_run_id": "obs_original",
            "observer_latest_blocked_by": [],
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "runtime_live_ready": True,
            "enforce_parameter_bundle_runtime": False,
            "required_parameter_bundle_stage": "shadow",
            "parameter_bundle_runtime": _parameter_bundle_runtime(),
            "mode_changed": False,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    command = CommandRequest(
        command_id="cmd_recheck_controls_001",
        command_type=CommandType.REQUEST_MODE_CHANGE,
        requested_by="test",
        requested_at="2026-06-16T23:00:00Z",
        current_mode=AutoTradeMode.SHADOW.value,
        target=AutoTradeMode.PAPER_OR_REPLAY.value,
        confirmation=True,
        reason_codes=("mode_change_request", "readiness_preflight"),
        note=note,
    )
    return CommandLedgerRecord(
        command_id=command.command_id,
        accepted=True,
        blocked_by=(),
        command=command,
        ledger_event="autotrade.mode_change_command_request_validated",
    )


def test_mode_change_request_note_stores_parameter_bundle_recheck_controls(monkeypatch) -> None:
    import btcts.autotrade.execution.mode_change_request as mode_change_request

    monkeypatch.setattr(mode_change_request, "evaluate_autotrade_live_readiness", lambda **kwargs: _FakeReadiness())

    record, _ = build_mode_change_command_request_record(
        current_mode="SHADOW",
        target_mode="PAPER_OR_REPLAY",
        human_confirmed=True,
        allow_warnings=True,
        enforce_parameter_bundle_runtime=False,
        required_parameter_bundle_stage="shadow",
    )

    note = json.loads(record.command.note)

    assert note["enforce_parameter_bundle_runtime"] is False
    assert note["required_parameter_bundle_stage"] == "shadow"
    assert note["parameter_bundle_runtime"]["registry"]["active_shadow_bundle_id"] == "pb_shadow"
    assert note["would_send_to_broker"] is False


def test_preview_recheck_reuses_parameter_bundle_controls_from_command_note(monkeypatch, tmp_path) -> None:
    command_path = tmp_path / "commands.jsonl"
    mode_state_path = tmp_path / "mode_state.jsonl"
    append_command_ledger_record(command_path, _mode_change_record_with_controls())

    calls = {}

    def fake_evaluate_autotrade_live_readiness(**kwargs):
        calls.update(kwargs)
        return _FakeReadiness()

    monkeypatch.setattr(mode_command_applier, "evaluate_autotrade_live_readiness", fake_evaluate_autotrade_live_readiness)

    preview = mode_command_applier.preview_latest_mode_change_command_apply_with_readiness_recheck(
        command_path=command_path,
        mode_state_path=mode_state_path,
        max_lines=100,
        allow_warnings=True,
    )

    assert calls["enforce_parameter_bundle_runtime"] is False
    assert calls["required_parameter_bundle_stage"] == "shadow"
    assert preview.candidate_readiness_parameter_bundle_runtime["registry"]["active_shadow_bundle_id"] == "pb_shadow"
    assert preview.would_send_to_broker is False


def test_apply_recheck_reuses_parameter_bundle_controls_from_command_note(monkeypatch, tmp_path) -> None:
    command_path = tmp_path / "commands.jsonl"
    mode_state_path = tmp_path / "mode_state.jsonl"
    append_command_ledger_record(command_path, _mode_change_record_with_controls())

    calls = {}

    def fake_evaluate_autotrade_live_readiness(**kwargs):
        calls.update(kwargs)
        return _FakeReadiness()

    monkeypatch.setattr(mode_command_applier, "evaluate_autotrade_live_readiness", fake_evaluate_autotrade_live_readiness)

    result = mode_command_applier.apply_latest_mode_change_command_once_with_readiness_recheck(
        command_path=command_path,
        mode_state_path=mode_state_path,
        max_lines=100,
        allow_warnings=True,
    )

    assert calls["enforce_parameter_bundle_runtime"] is False
    assert calls["required_parameter_bundle_stage"] == "shadow"
    assert result.candidate_readiness_parameter_bundle_runtime["registry"]["active_shadow_bundle_id"] == "pb_shadow"
    assert result.would_send_to_broker is False
