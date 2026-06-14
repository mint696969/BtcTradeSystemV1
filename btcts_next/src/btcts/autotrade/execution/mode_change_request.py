# path: ./btcts_next/src/btcts/autotrade/execution/mode_change_request.py
# desc: Mode-change command request helper. Appends request only; no mode changes or broker execution.

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.execution.command_ledger import CommandLedgerRecord, append_command_ledger_record, default_command_ledger_path
from btcts.autotrade.execution.command_request import CommandRequest, CommandType, validate_command_request
from btcts.autotrade.modes import AutoTradeMode
from btcts.autotrade.readiness import AutoTradeReadinessResult, evaluate_autotrade_live_readiness


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _command_id() -> str:
    return f"cmd_mode_change_{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class ModeChangeCommandRequestResult:
    command_record: CommandLedgerRecord
    readiness: AutoTradeReadinessResult
    ledger_path: Path
    appended: bool
    mode_changed: bool = False
    would_send_to_broker: bool = False
    read_only_preflight: bool = True

    @property
    def accepted(self) -> bool:
        return self.command_record.accepted

    @property
    def blocked_by(self) -> Tuple[str, ...]:
        return self.command_record.blocked_by

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["command_record"] = self.command_record.to_dict()
        data["readiness"] = self.readiness.to_dict()
        data["ledger_path"] = str(self.ledger_path)
        data["accepted"] = self.accepted
        data["blocked_by"] = list(self.blocked_by)
        return data


def _readiness_note(readiness: AutoTradeReadinessResult) -> str:
    payload = {
        "kind": "autotrade.mode_change_readiness_snapshot",
        "ready": readiness.ready,
        "current_mode": readiness.current_mode.value,
        "target_mode": readiness.target_mode.value,
        "blocked_by": list(readiness.blocked_by),
        "warnings": list(readiness.warnings),
        "health_state": readiness.health.health_state,
        "observer_run_fresh": readiness.health.observer_run_fresh,
        "observer_latest_run_id": readiness.health.observer_runs.latest_run_id,
        "observer_latest_blocked_by": list(readiness.health.observer_runs.latest_blocked_by),
        "observer_latest_would_send_to_broker": readiness.health.observer_runs.latest_would_send_to_broker,
        "observer_latest_bounded": readiness.health.observer_runs.latest_bounded,
        "runtime_live_ready": readiness.health.runtime.live_ready,
        "mode_changed": False,
        "would_send_to_broker": False,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def build_mode_change_command_request_record(
    *,
    current_mode: AutoTradeMode | str,
    target_mode: AutoTradeMode | str,
    requested_by: str = "operator_ui",
    human_confirmed: bool = False,
    allow_warnings: bool = False,
    max_observer_run_age_sec: float = 120.0,
    max_lines: int | None = 1000,
) -> tuple[CommandLedgerRecord, AutoTradeReadinessResult]:
    readiness = evaluate_autotrade_live_readiness(
        current_mode=current_mode,
        target_mode=target_mode,
        human_confirmed=human_confirmed,
        allow_warnings=allow_warnings,
        max_observer_run_age_sec=max_observer_run_age_sec,
        max_lines=max_lines,
    )
    command = CommandRequest(
        command_id=_command_id(),
        command_type=CommandType.REQUEST_MODE_CHANGE,
        requested_by=requested_by,
        requested_at=_utc_now(),
        current_mode=readiness.current_mode.value,
        target=readiness.target_mode.value,
        confirmation=bool(human_confirmed),
        reason_codes=("mode_change_request", "readiness_preflight"),
        note=_readiness_note(readiness),
    )
    validation = validate_command_request(command)
    blocked = list(validation.blocked_by)
    if not readiness.ready:
        blocked.append("readiness_preflight_not_ready")
        blocked.extend(readiness.blocked_by)
    blocked_tuple = tuple(dict.fromkeys(blocked))
    return (
        CommandLedgerRecord(
            command_id=command.command_id,
            accepted=bool(validation.accepted and readiness.ready),
            blocked_by=blocked_tuple,
            command=command,
            ledger_event="autotrade.mode_change_command_request_validated",
        ),
        readiness,
    )


def submit_mode_change_command_request(
    *,
    current_mode: AutoTradeMode | str,
    target_mode: AutoTradeMode | str,
    requested_by: str = "operator_ui",
    human_confirmed: bool = False,
    allow_warnings: bool = False,
    max_observer_run_age_sec: float = 120.0,
    max_lines: int | None = 1000,
    path: Path | None = None,
) -> ModeChangeCommandRequestResult:
    record, readiness = build_mode_change_command_request_record(
        current_mode=current_mode,
        target_mode=target_mode,
        requested_by=requested_by,
        human_confirmed=human_confirmed,
        allow_warnings=allow_warnings,
        max_observer_run_age_sec=max_observer_run_age_sec,
        max_lines=max_lines,
    )
    target_path = path or default_command_ledger_path(ensure=True)
    append_command_ledger_record(target_path, record)
    return ModeChangeCommandRequestResult(
        command_record=record,
        readiness=readiness,
        ledger_path=target_path,
        appended=True,
        mode_changed=False,
        would_send_to_broker=False,
        read_only_preflight=True,
    )
