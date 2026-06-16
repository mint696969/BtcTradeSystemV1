# path: ./btcts_next/src/btcts/autotrade/execution/command_status.py
# desc: Read-only command request ledger status summary. No command append, no mode change, no broker execution.

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.execution.command_ledger import CommandLedgerRecord, default_command_ledger_path
from btcts.autotrade.execution.command_request import CommandRequest, CommandType


@dataclass(frozen=True)
class CommandLedgerReadResult:
    path: Path
    rows: Tuple[CommandLedgerRecord, ...]
    skipped_count: int = 0
    error_samples: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "rows": [row.to_dict() for row in self.rows],
            "skipped_count": self.skipped_count,
            "error_samples": list(self.error_samples),
        }


@dataclass(frozen=True)
class CommandLedgerSummary:
    path: Path
    exists: bool
    total_rows: int
    accepted_count: int
    rejected_count: int
    skipped_rows: int
    latest_command_id: str | None = None
    latest_command_type: str | None = None
    latest_target: str | None = None
    latest_current_mode: str | None = None
    latest_accepted: bool | None = None
    latest_requested_by: str | None = None
    latest_requested_at: str | None = None
    latest_blocked_by: Tuple[str, ...] = ()
    latest_readiness_observer_run_id: str | None = None
    latest_readiness_observer_blocked_by: Tuple[str, ...] = ()
    latest_readiness_observer_would_send_to_broker: bool | None = None
    latest_readiness_observer_bounded: bool | None = None
    latest_readiness_parameter_bundle_runtime: Dict[str, Any] | None = None
    latest_mode_change_readiness_command_id: str | None = None
    latest_mode_change_readiness_requested_by: str | None = None
    latest_mode_change_readiness_requested_at: str | None = None
    latest_mode_change_readiness_accepted: bool | None = None
    latest_mode_change_readiness_command_blocked_by: Tuple[str, ...] = ()
    latest_mode_change_readiness_ready: bool | None = None
    latest_mode_change_readiness_current_mode: str | None = None
    latest_mode_change_readiness_target_mode: str | None = None
    latest_mode_change_readiness_blocked_by: Tuple[str, ...] = ()
    latest_mode_change_readiness_warnings: Tuple[str, ...] = ()
    latest_mode_change_readiness_health_state: str | None = None
    latest_mode_change_readiness_observer_run_id: str | None = None
    latest_mode_change_readiness_observer_blocked_by: Tuple[str, ...] = ()
    latest_mode_change_readiness_observer_would_send_to_broker: bool | None = None
    latest_mode_change_readiness_observer_bounded: bool | None = None
    latest_mode_change_readiness_parameter_bundle_runtime: Dict[str, Any] | None = None
    command_type_counts: Dict[str, int] = field(default_factory=dict)
    target_counts: Dict[str, int] = field(default_factory=dict)
    blocked_by_counts: Dict[str, int] = field(default_factory=dict)
    error_samples: Tuple[str, ...] = ()
    would_send_to_broker: bool = False
    read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


def _iter_recent_lines(path: Path, *, max_lines: int | None = None) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    if max_lines is not None and max_lines >= 0:
        return lines[-max_lines:]
    return lines


def _parse_record(obj: Any) -> CommandLedgerRecord:
    if not isinstance(obj, dict):
        raise ValueError("not_object")
    command_obj = obj.get("command") or {}
    if not isinstance(command_obj, dict):
        raise ValueError("command_not_object")
    command_type = CommandType(str(command_obj.get("command_type") or "REQUEST_HALT_NEW"))
    command = CommandRequest(
        command_id=str(command_obj.get("command_id") or ""),
        command_type=command_type,
        requested_by=str(command_obj.get("requested_by") or ""),
        requested_at=str(command_obj.get("requested_at") or ""),
        current_mode=str(command_obj.get("current_mode") or ""),
        target=command_obj.get("target"),
        confirmation=bool(command_obj.get("confirmation")),
        reason_codes=tuple(command_obj.get("reason_codes") or ()),
        note=str(command_obj.get("note") or ""),
    )
    return CommandLedgerRecord(
        command_id=str(obj.get("command_id") or command.command_id),
        accepted=bool(obj.get("accepted")),
        blocked_by=tuple(obj.get("blocked_by") or ()),
        command=command,
        ledger_event=str(obj.get("ledger_event") or "autotrade.command_request_validated"),
    )


def _readiness_note_payload(row: CommandLedgerRecord | None) -> Dict[str, Any]:
    if row is None or not row.command.note:
        return {}
    try:
        payload = json.loads(row.command.note)
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    if payload.get("kind") != "autotrade.mode_change_readiness_snapshot":
        return {}
    return payload


def read_command_ledger_rows(path: Path | None = None, *, max_lines: int | None = 1000) -> CommandLedgerReadResult:
    target = path or default_command_ledger_path(ensure=False)
    rows: list[CommandLedgerRecord] = []
    skipped = 0
    errors: list[str] = []
    for index, line in enumerate(_iter_recent_lines(target, max_lines=max_lines), start=1):
        text = line.strip()
        if not text:
            continue
        try:
            rows.append(_parse_record(json.loads(text)))
        except Exception as exc:
            skipped += 1
            if len(errors) < 5:
                errors.append(f"line:{index}:{exc.__class__.__name__}")
    return CommandLedgerReadResult(path=target, rows=tuple(rows), skipped_count=skipped, error_samples=tuple(errors))


def summarize_command_ledger(path: Path | None = None, *, max_lines: int | None = 1000) -> CommandLedgerSummary:
    target = path or default_command_ledger_path(ensure=False)
    read = read_command_ledger_rows(target, max_lines=max_lines)
    rows = read.rows
    latest = rows[-1] if rows else None
    command_counter: Counter[str] = Counter()
    target_counter: Counter[str] = Counter()
    blocked_counter: Counter[str] = Counter()
    for row in rows:
        command_counter[row.command.command_type.value] += 1
        if row.command.target:
            target_counter[str(row.command.target)] += 1
        blocked_counter.update(row.blocked_by)
    accepted = sum(1 for row in rows if row.accepted)
    rejected = len(rows) - accepted
    latest_readiness_note = _readiness_note_payload(latest)
    latest_mode_change_readiness_row: CommandLedgerRecord | None = None
    latest_mode_change_readiness_note: Dict[str, Any] = {}
    for row in reversed(rows):
        note_payload = _readiness_note_payload(row)
        if row.command.command_type == CommandType.REQUEST_MODE_CHANGE and note_payload:
            latest_mode_change_readiness_row = row
            latest_mode_change_readiness_note = note_payload
            break
    return CommandLedgerSummary(
        path=target,
        exists=target.exists(),
        total_rows=len(rows),
        accepted_count=accepted,
        rejected_count=rejected,
        skipped_rows=read.skipped_count,
        latest_command_id=latest.command_id if latest is not None else None,
        latest_command_type=latest.command.command_type.value if latest is not None else None,
        latest_target=str(latest.command.target) if latest is not None and latest.command.target is not None else None,
        latest_current_mode=latest.command.current_mode if latest is not None else None,
        latest_accepted=latest.accepted if latest is not None else None,
        latest_requested_by=latest.command.requested_by if latest is not None else None,
        latest_requested_at=latest.command.requested_at if latest is not None else None,
        latest_blocked_by=latest.blocked_by if latest is not None else (),
        latest_readiness_observer_run_id=latest_readiness_note.get("observer_latest_run_id"),
        latest_readiness_observer_blocked_by=tuple(latest_readiness_note.get("observer_latest_blocked_by") or ()),
        latest_readiness_observer_would_send_to_broker=latest_readiness_note.get("observer_latest_would_send_to_broker"),
        latest_readiness_observer_bounded=latest_readiness_note.get("observer_latest_bounded"),
        latest_readiness_parameter_bundle_runtime=latest_readiness_note.get("parameter_bundle_runtime"),
        latest_mode_change_readiness_command_id=latest_mode_change_readiness_row.command_id if latest_mode_change_readiness_row is not None else None,
        latest_mode_change_readiness_requested_by=latest_mode_change_readiness_row.command.requested_by if latest_mode_change_readiness_row is not None else None,
        latest_mode_change_readiness_requested_at=latest_mode_change_readiness_row.command.requested_at if latest_mode_change_readiness_row is not None else None,
        latest_mode_change_readiness_accepted=latest_mode_change_readiness_row.accepted if latest_mode_change_readiness_row is not None else None,
        latest_mode_change_readiness_command_blocked_by=latest_mode_change_readiness_row.blocked_by if latest_mode_change_readiness_row is not None else (),
        latest_mode_change_readiness_ready=latest_mode_change_readiness_note.get("ready"),
        latest_mode_change_readiness_current_mode=latest_mode_change_readiness_note.get("current_mode"),
        latest_mode_change_readiness_target_mode=latest_mode_change_readiness_note.get("target_mode"),
        latest_mode_change_readiness_blocked_by=tuple(latest_mode_change_readiness_note.get("blocked_by") or ()),
        latest_mode_change_readiness_warnings=tuple(latest_mode_change_readiness_note.get("warnings") or ()),
        latest_mode_change_readiness_health_state=latest_mode_change_readiness_note.get("health_state"),
        latest_mode_change_readiness_observer_run_id=latest_mode_change_readiness_note.get("observer_latest_run_id"),
        latest_mode_change_readiness_observer_blocked_by=tuple(latest_mode_change_readiness_note.get("observer_latest_blocked_by") or ()),
        latest_mode_change_readiness_observer_would_send_to_broker=latest_mode_change_readiness_note.get("observer_latest_would_send_to_broker"),
        latest_mode_change_readiness_observer_bounded=latest_mode_change_readiness_note.get("observer_latest_bounded"),
        latest_mode_change_readiness_parameter_bundle_runtime=latest_mode_change_readiness_note.get("parameter_bundle_runtime"),
        command_type_counts=dict(command_counter),
        target_counts=dict(target_counter),
        blocked_by_counts=dict(blocked_counter),
        error_samples=read.error_samples,
        would_send_to_broker=False,
        read_only=True,
    )
