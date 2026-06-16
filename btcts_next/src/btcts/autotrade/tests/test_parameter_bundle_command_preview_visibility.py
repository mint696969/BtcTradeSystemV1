# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_command_preview_visibility.py
# desc: Guards parameter bundle runtime visibility in command summaries and mode apply previews.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from btcts.autotrade.execution.command_ledger import CommandLedgerRecord, append_command_ledger_record
from btcts.autotrade.execution.command_request import CommandRequest, CommandType
from btcts.autotrade.execution.command_status import summarize_command_ledger
from btcts.autotrade.execution import mode_command_applier
from btcts.autotrade.modes import AutoTradeMode


def _parameter_bundle_runtime() -> Dict[str, Any]:
    return {
        "schema_version": "autotrade_parameter_bundle_runtime_status.v1",
        "registry_exists": True,
        "event_ledger_exists": True,
        "registry": {
            "active_shadow_bundle_id": "pb_shadow",
            "active_live_bundle_id": "pb_live",
            "last_known_good_bundle_id": "pb_live",
        },
        "event_count": 2,
        "latest_event_type": "bundle_activated_live",
        "would_send_to_broker": False,
    }


def _readiness_note() -> str:
    return json.dumps(
        {
            "kind": "autotrade.mode_change_readiness_snapshot",
            "ready": True,
            "current_mode": "ARMED_DRY_RUN",
            "target_mode": "LIVE_MIN_SIZE",
            "blocked_by": [],
            "warnings": [],
            "health_state": "ok",
            "observer_run_fresh": True,
            "observer_latest_run_id": "obs_pb_001",
            "observer_latest_blocked_by": [],
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "runtime_live_ready": True,
            "parameter_bundle_runtime": _parameter_bundle_runtime(),
            "mode_changed": False,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _mode_change_record() -> CommandLedgerRecord:
    command = CommandRequest(
        command_id="cmd_pb_visibility_001",
        command_type=CommandType.REQUEST_MODE_CHANGE,
        requested_by="test",
        requested_at="2026-06-16T22:00:00Z",
        current_mode=AutoTradeMode.ARMED_DRY_RUN.value,
        target=AutoTradeMode.LIVE_MIN_SIZE.value,
        confirmation=True,
        reason_codes=("mode_change_request", "readiness_preflight"),
        note=_readiness_note(),
    )
    return CommandLedgerRecord(
        command_id=command.command_id,
        accepted=True,
        blocked_by=(),
        command=command,
        ledger_event="autotrade.mode_change_command_request_validated",
    )


class _FakeRuntime:
    live_ready = True


class _FakeObserverRuns:
    latest_run_id = "obs_recheck"
    latest_blocked_by = ()
    latest_would_send_to_broker = False
    latest_bounded = True


class _FakeHealth:
    health_state = "ok"
    observer_run_fresh = True
    observer_runs = _FakeObserverRuns()
    runtime = _FakeRuntime()


class _FakeReadiness:
    current_mode = AutoTradeMode.ARMED_DRY_RUN
    target_mode = AutoTradeMode.LIVE_MIN_SIZE
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
                "health_state": "ok",
                "observer_run_fresh": True,
                "observer_runs": {
                    "latest_run_id": "obs_recheck",
                    "latest_blocked_by": [],
                    "latest_would_send_to_broker": False,
                    "latest_bounded": True,
                },
            },
            "parameter_bundle_runtime": self.parameter_bundle_runtime,
            "would_send_to_broker": False,
        }


def test_command_ledger_summary_exposes_parameter_bundle_runtime_from_readiness_note(tmp_path) -> None:
    command_path = tmp_path / "commands.jsonl"
    append_command_ledger_record(command_path, _mode_change_record())

    summary = summarize_command_ledger(command_path)
    data = summary.to_dict()

    assert data["latest_readiness_parameter_bundle_runtime"]["registry"]["active_live_bundle_id"] == "pb_live"
    assert data["latest_mode_change_readiness_parameter_bundle_runtime"]["registry"]["active_shadow_bundle_id"] == "pb_shadow"
    assert data["latest_mode_change_readiness_parameter_bundle_runtime"]["would_send_to_broker"] is False
    assert data["would_send_to_broker"] is False


def test_mode_change_apply_preview_exposes_candidate_parameter_bundle_runtime(monkeypatch, tmp_path) -> None:
    command_path = tmp_path / "commands.jsonl"
    mode_state_path = tmp_path / "mode_state.jsonl"
    append_command_ledger_record(command_path, _mode_change_record())

    monkeypatch.setattr(mode_command_applier, "evaluate_autotrade_live_readiness", lambda **kwargs: _FakeReadiness())

    preview = mode_command_applier.preview_latest_mode_change_command_apply_with_readiness_recheck(
        command_path=command_path,
        mode_state_path=mode_state_path,
        max_lines=100,
        allow_warnings=True,
    )
    data = preview.to_dict()

    assert data["candidate_readiness_parameter_bundle_runtime"]["registry"]["active_live_bundle_id"] == "pb_live"
    assert data["readiness"]["parameter_bundle_runtime"]["registry"]["active_shadow_bundle_id"] == "pb_shadow"
    assert data["would_send_to_broker"] is False
