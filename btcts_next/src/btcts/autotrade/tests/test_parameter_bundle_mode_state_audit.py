# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_mode_state_audit.py
# desc: Guards parameter bundle readiness recheck evidence in mode_state ledger records.

from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from btcts.autotrade.execution import mode_command_applier
from btcts.autotrade.execution.command_ledger import CommandLedgerRecord, append_command_ledger_record
from btcts.autotrade.execution.command_request import CommandRequest, CommandType
from btcts.autotrade.execution.mode_state import read_mode_state_records, summarize_mode_state
from btcts.autotrade.modes import AutoTradeMode


def _candidate_parameter_bundle_runtime() -> Dict[str, Any]:
    return {
        "schema_version": "autotrade_parameter_bundle_runtime_status.v1",
        "registry_exists": True,
        "event_ledger_exists": True,
        "registry": {"active_shadow_bundle_id": "pb_candidate_shadow"},
        "event_count": 1,
        "would_send_to_broker": False,
    }


def _recheck_parameter_bundle_runtime() -> Dict[str, Any]:
    return {
        "schema_version": "autotrade_parameter_bundle_runtime_status.v1",
        "registry_exists": True,
        "event_ledger_exists": True,
        "registry": {"active_shadow_bundle_id": "pb_recheck_shadow"},
        "event_count": 2,
        "would_send_to_broker": False,
    }


class _FakeRuntime:
    live_ready = True


class _FakeObserverRuns:
    latest_run_id = "obs_mode_state_audit"
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
    warnings: Tuple[str, ...] = ()
    health = _FakeHealth()
    parameter_bundle_runtime = _recheck_parameter_bundle_runtime()
    would_send_to_broker = False

    def __init__(self, *, ready: bool, blocked_by: Tuple[str, ...] = ()) -> None:
        self.ready = ready
        self.blocked_by = blocked_by

    def to_dict(self):
        return {
            "ready": self.ready,
            "current_mode": self.current_mode.value,
            "target_mode": self.target_mode.value,
            "blocked_by": list(self.blocked_by),
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


def _mode_change_record() -> CommandLedgerRecord:
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
            "observer_latest_run_id": "obs_candidate",
            "observer_latest_blocked_by": [],
            "observer_latest_would_send_to_broker": False,
            "observer_latest_bounded": True,
            "runtime_live_ready": True,
            "enforce_parameter_bundle_runtime": False,
            "required_parameter_bundle_stage": "shadow",
            "parameter_bundle_runtime": _candidate_parameter_bundle_runtime(),
            "mode_changed": False,
            "would_send_to_broker": False,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    command = CommandRequest(
        command_id="cmd_mode_state_audit_001",
        command_type=CommandType.REQUEST_MODE_CHANGE,
        requested_by="test",
        requested_at="2026-06-17T00:00:00Z",
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


def test_mode_state_record_stores_accepted_readiness_recheck_parameter_bundle_audit(monkeypatch, tmp_path) -> None:
    command_path = tmp_path / "commands.jsonl"
    mode_state_path = tmp_path / "mode_state.jsonl"
    append_command_ledger_record(command_path, _mode_change_record())

    monkeypatch.setattr(
        mode_command_applier,
        "evaluate_autotrade_live_readiness",
        lambda **kwargs: _FakeReadiness(ready=True),
    )

    result = mode_command_applier.apply_latest_mode_change_command_once_with_readiness_recheck(
        command_path=command_path,
        mode_state_path=mode_state_path,
        max_lines=100,
        allow_warnings=True,
    )

    rows = read_mode_state_records(mode_state_path).rows
    summary = summarize_mode_state(mode_state_path).to_dict()
    audit = rows[-1].readiness_recheck

    assert result.applied is True
    assert audit is not None
    assert audit["schema_version"] == "autotrade.mode_state_readiness_recheck.v1"
    assert audit["ready"] is True
    assert audit["enforce_parameter_bundle_runtime"] is False
    assert audit["required_parameter_bundle_stage"] == "shadow"
    assert audit["candidate_parameter_bundle_runtime"]["registry"]["active_shadow_bundle_id"] == "pb_candidate_shadow"
    assert audit["parameter_bundle_runtime"]["registry"]["active_shadow_bundle_id"] == "pb_recheck_shadow"
    assert audit["would_send_to_broker"] is False
    assert summary["latest_readiness_recheck"]["ready"] is True


def test_mode_state_record_stores_rejected_readiness_recheck_parameter_bundle_audit(monkeypatch, tmp_path) -> None:
    command_path = tmp_path / "commands.jsonl"
    mode_state_path = tmp_path / "mode_state.jsonl"
    append_command_ledger_record(command_path, _mode_change_record())

    monkeypatch.setattr(
        mode_command_applier,
        "evaluate_autotrade_live_readiness",
        lambda **kwargs: _FakeReadiness(ready=False, blocked_by=("parameter_bundle_runtime_not_ready",)),
    )

    result = mode_command_applier.apply_latest_mode_change_command_once_with_readiness_recheck(
        command_path=command_path,
        mode_state_path=mode_state_path,
        max_lines=100,
        allow_warnings=True,
    )

    rows = read_mode_state_records(mode_state_path).rows
    audit = rows[-1].readiness_recheck

    assert result.applied is False
    assert result.rejected_by_readiness is True
    assert rows[-1].accepted is False
    assert audit is not None
    assert audit["ready"] is False
    assert "parameter_bundle_runtime_not_ready" in audit["blocked_by"]
    assert audit["required_parameter_bundle_stage"] == "shadow"
    assert audit["parameter_bundle_runtime"]["registry"]["active_shadow_bundle_id"] == "pb_recheck_shadow"
    assert audit["would_send_to_broker"] is False
