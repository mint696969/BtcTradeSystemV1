# path: ./btcts_next/src/btcts/autotrade/execution/mode_command_applier.py
# desc: One-shot mode-change command applier. Applies accepted REQUEST_MODE_CHANGE to mode_state ledger only; no broker execution.

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.readiness import evaluate_autotrade_live_readiness
from btcts.autotrade.execution.command_ledger import default_command_ledger_path
from btcts.autotrade.execution.command_request import CommandType
from btcts.autotrade.execution.command_status import read_command_ledger_rows
from btcts.autotrade.execution.mode_state import (
    ModeStateRecord,
    append_mode_state_record,
    build_mode_state_record_from_command,
    current_mode_state,
    default_mode_state_ledger_path,
    read_mode_state_records,
    _utc_now as _mode_state_utc_now,
)


@dataclass(frozen=True)
class ModeChangeCommandApplyResult:
    applied: bool
    skipped: bool
    skip_reason: str | None
    command_id: str | None
    current_mode_before: str
    current_mode_after: str
    command_path: Path
    mode_state_path: Path
    mode_state_record: ModeStateRecord | None = None
    already_applied_command_ids: Tuple[str, ...] = ()
    candidate_command_count: int = 0
    command_read_skipped_count: int = 0
    mode_state_read_skipped_count: int = 0
    mode_changed: bool = False
    would_send_to_broker: bool = False
    read_only_command_scan: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["command_path"] = str(self.command_path)
        data["mode_state_path"] = str(self.mode_state_path)
        data["mode_state_record"] = self.mode_state_record.to_dict() if self.mode_state_record is not None else None
        return data




def _command_readiness_note_payload(command_record: Any | None) -> Dict[str, Any]:
    if command_record is None:
        return {}
    note = getattr(getattr(command_record, "command", None), "note", "")
    if not note:
        return {}
    try:
        payload = json.loads(str(note))
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    if payload.get("kind") != "autotrade.mode_change_readiness_snapshot":
        return {}
    return payload



def _candidate_parameter_bundle_recheck_controls(candidate_note: Dict[str, Any]) -> tuple[bool, str]:
    enforce = bool(candidate_note.get("enforce_parameter_bundle_runtime", True))
    stage = str(candidate_note.get("required_parameter_bundle_stage") or "live")
    return enforce, stage


def _applied_command_ids(path: Path, *, max_lines: int | None) -> tuple[set[str], int]:
    read = read_mode_state_records(path, max_lines=max_lines)
    ids = {str(row.source_command_id) for row in read.rows if row.source_command_id}
    return ids, read.skipped_count



@dataclass(frozen=True)
class ModeChangeCommandApplyPreview:
    would_apply: bool
    skip_reason: str | None
    command_id: str | None
    current_mode_before: str
    current_mode_after: str
    command_path: Path
    mode_state_path: Path
    already_applied_command_ids: Tuple[str, ...] = ()
    candidate_command_count: int = 0
    command_read_skipped_count: int = 0
    mode_state_read_skipped_count: int = 0
    mode_changed: bool = False
    would_send_to_broker: bool = False
    read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["command_path"] = str(self.command_path)
        data["mode_state_path"] = str(self.mode_state_path)
        return data


def preview_latest_mode_change_command_apply(
    *,
    command_path: Path | None = None,
    mode_state_path: Path | None = None,
    max_lines: int | None = 1000,
) -> ModeChangeCommandApplyPreview:
    commands_path = command_path or default_command_ledger_path(ensure=False)
    state_path = mode_state_path or default_mode_state_ledger_path(ensure=True)
    before = current_mode_state(state_path, max_lines=max_lines)
    already_applied, state_skipped = _applied_command_ids(state_path, max_lines=max_lines)
    command_read = read_command_ledger_rows(commands_path, max_lines=max_lines)
    candidates = [
        row
        for row in command_read.rows
        if row.accepted
        and row.command.command_type == CommandType.REQUEST_MODE_CHANGE
        and row.command_id not in already_applied
    ]
    if not candidates:
        return ModeChangeCommandApplyPreview(
            would_apply=False,
            skip_reason="no_unapplied_accepted_mode_change_command",
            command_id=None,
            current_mode_before=before.current_mode.value,
            current_mode_after=before.current_mode.value,
            command_path=commands_path,
            mode_state_path=state_path,
            already_applied_command_ids=tuple(sorted(already_applied)),
            candidate_command_count=0,
            command_read_skipped_count=command_read.skipped_count,
            mode_state_read_skipped_count=state_skipped,
            mode_changed=False,
            would_send_to_broker=False,
            read_only=True,
        )
    command = candidates[-1]
    record = build_mode_state_record_from_command(current_mode=before.current_mode, command_record=command)
    return ModeChangeCommandApplyPreview(
        would_apply=True,
        skip_reason=None,
        command_id=command.command_id,
        current_mode_before=before.current_mode.value,
        current_mode_after=record.current_mode.value,
        command_path=commands_path,
        mode_state_path=state_path,
        already_applied_command_ids=tuple(sorted(already_applied)),
        candidate_command_count=len(candidates),
        command_read_skipped_count=command_read.skipped_count,
        mode_state_read_skipped_count=state_skipped,
        mode_changed=record.mode_changed,
        would_send_to_broker=False,
        read_only=True,
    )


@dataclass(frozen=True)
class ModeChangeCommandReadinessApplyResult:
    applied: bool
    skipped: bool
    rejected_by_readiness: bool
    skip_reason: str | None
    command_id: str | None
    current_mode_before: str
    current_mode_after: str
    command_path: Path
    mode_state_path: Path
    mode_state_record: ModeStateRecord | None = None
    candidate_command_type: str | None = None
    candidate_requested_by: str | None = None
    candidate_requested_at: str | None = None
    candidate_current_mode: str | None = None
    candidate_target_mode: str | None = None
    candidate_accepted: bool | None = None
    candidate_blocked_by: Tuple[str, ...] = ()
    candidate_readiness_note_present: bool = False
    candidate_readiness_ready: bool | None = None
    candidate_readiness_current_mode: str | None = None
    candidate_readiness_target_mode: str | None = None
    candidate_readiness_blocked_by: Tuple[str, ...] = ()
    candidate_readiness_warnings: Tuple[str, ...] = ()
    candidate_readiness_health_state: str | None = None
    candidate_readiness_observer_latest_run_id: str | None = None
    candidate_readiness_observer_latest_blocked_by: Tuple[str, ...] = ()
    candidate_readiness_observer_latest_would_send_to_broker: bool | None = None
    candidate_readiness_observer_latest_bounded: bool | None = None
    candidate_readiness_parameter_bundle_runtime: Dict[str, Any] | None = None
    readiness: Any | None = None
    readiness_ready: bool = False
    blocked_by: Tuple[str, ...] = ()
    already_applied_command_ids: Tuple[str, ...] = ()
    candidate_command_count: int = 0
    command_read_skipped_count: int = 0
    mode_state_read_skipped_count: int = 0
    record_appended: bool = False
    mode_changed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["command_path"] = str(self.command_path)
        data["mode_state_path"] = str(self.mode_state_path)
        data["mode_state_record"] = self.mode_state_record.to_dict() if self.mode_state_record is not None else None
        readiness = self.readiness
        data["readiness"] = readiness.to_dict() if readiness is not None and hasattr(readiness, "to_dict") else None
        return data


def _readiness_rejected_mode_state_record(
    *,
    current_mode: Any,
    command: Any,
    readiness: Any,
    blocked_by: Tuple[str, ...],
) -> ModeStateRecord:
    return ModeStateRecord(
        current_mode=current_mode,
        previous_mode=current_mode,
        changed_at=_mode_state_utc_now(),
        source_command_id=command.command_id,
        requested_by=command.command.requested_by,
        accepted=False,
        mode_changed=False,
        reason_codes=tuple(command.command.reason_codes) + ("readiness_recheck",),
        blocked_by=blocked_by,
        ledger_event="autotrade.mode_state_readiness_recheck_rejected",
        would_send_to_broker=False,
    )



@dataclass(frozen=True)
class ModeChangeCommandReadinessApplyPreview:
    would_apply: bool
    would_reject_by_readiness: bool
    skip_reason: str | None
    command_id: str | None
    current_mode_before: str
    current_mode_after: str
    command_path: Path
    mode_state_path: Path
    candidate_command_type: str | None = None
    candidate_requested_by: str | None = None
    candidate_requested_at: str | None = None
    candidate_current_mode: str | None = None
    candidate_target_mode: str | None = None
    candidate_accepted: bool | None = None
    candidate_blocked_by: Tuple[str, ...] = ()
    candidate_readiness_note_present: bool = False
    candidate_readiness_ready: bool | None = None
    candidate_readiness_current_mode: str | None = None
    candidate_readiness_target_mode: str | None = None
    candidate_readiness_blocked_by: Tuple[str, ...] = ()
    candidate_readiness_warnings: Tuple[str, ...] = ()
    candidate_readiness_health_state: str | None = None
    candidate_readiness_observer_latest_run_id: str | None = None
    candidate_readiness_observer_latest_blocked_by: Tuple[str, ...] = ()
    candidate_readiness_observer_latest_would_send_to_broker: bool | None = None
    candidate_readiness_observer_latest_bounded: bool | None = None
    candidate_readiness_parameter_bundle_runtime: Dict[str, Any] | None = None
    readiness: Any | None = None
    readiness_ready: bool = False
    blocked_by: Tuple[str, ...] = ()
    already_applied_command_ids: Tuple[str, ...] = ()
    candidate_command_count: int = 0
    command_read_skipped_count: int = 0
    mode_state_read_skipped_count: int = 0
    mode_changed: bool = False
    would_send_to_broker: bool = False
    read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["command_path"] = str(self.command_path)
        data["mode_state_path"] = str(self.mode_state_path)
        readiness = self.readiness
        data["readiness"] = readiness.to_dict() if readiness is not None and hasattr(readiness, "to_dict") else None
        return data


def preview_latest_mode_change_command_apply_with_readiness_recheck(
    *,
    command_path: Path | None = None,
    mode_state_path: Path | None = None,
    max_lines: int | None = 1000,
    max_observer_run_age_sec: float = 120.0,
    allow_warnings: bool = False,
) -> ModeChangeCommandReadinessApplyPreview:
    commands_path = command_path or default_command_ledger_path(ensure=False)
    state_path = mode_state_path or default_mode_state_ledger_path(ensure=True)
    before = current_mode_state(state_path, max_lines=max_lines)
    already_applied, state_skipped = _applied_command_ids(state_path, max_lines=max_lines)
    command_read = read_command_ledger_rows(commands_path, max_lines=max_lines)
    candidates = [
        row
        for row in command_read.rows
        if row.accepted
        and row.command.command_type == CommandType.REQUEST_MODE_CHANGE
        and row.command_id not in already_applied
    ]
    if not candidates:
        return ModeChangeCommandReadinessApplyPreview(
            would_apply=False,
            would_reject_by_readiness=False,
            skip_reason="no_unapplied_accepted_mode_change_command",
            command_id=None,
            current_mode_before=before.current_mode.value,
            current_mode_after=before.current_mode.value,
            command_path=commands_path,
            mode_state_path=state_path,
            readiness=None,
            readiness_ready=False,
            blocked_by=(),
            already_applied_command_ids=tuple(sorted(already_applied)),
            candidate_command_count=0,
            command_read_skipped_count=command_read.skipped_count,
            mode_state_read_skipped_count=state_skipped,
            mode_changed=False,
            would_send_to_broker=False,
            read_only=True,
        )
    command = candidates[-1]
    candidate_note = _command_readiness_note_payload(command)
    enforce_parameter_bundle_runtime, required_parameter_bundle_stage = _candidate_parameter_bundle_recheck_controls(candidate_note)
    readiness = evaluate_autotrade_live_readiness(
        current_mode=before.current_mode,
        target_mode=command.command.target,
        human_confirmed=bool(command.command.confirmation),
        allow_warnings=allow_warnings,
        enforce_parameter_bundle_runtime=enforce_parameter_bundle_runtime,
        required_parameter_bundle_stage=required_parameter_bundle_stage,
        max_observer_run_age_sec=max_observer_run_age_sec,
        max_lines=max_lines,
    )
    if not readiness.ready:
        blocked = tuple(dict.fromkeys(("readiness_recheck_not_ready",) + tuple(readiness.blocked_by) + tuple(command.blocked_by)))
        return ModeChangeCommandReadinessApplyPreview(
            would_apply=False,
            would_reject_by_readiness=True,
            skip_reason="readiness_recheck_not_ready",
            command_id=command.command_id,
            candidate_command_type=command.command.command_type.value,
            candidate_requested_by=command.command.requested_by,
            candidate_requested_at=command.command.requested_at,
            candidate_current_mode=command.command.current_mode,
            candidate_target_mode=str(command.command.target) if command.command.target is not None else None,
            candidate_accepted=command.accepted,
            candidate_blocked_by=tuple(command.blocked_by),
            candidate_readiness_note_present=bool(candidate_note),
            candidate_readiness_ready=candidate_note.get("ready"),
            candidate_readiness_current_mode=candidate_note.get("current_mode"),
            candidate_readiness_target_mode=candidate_note.get("target_mode"),
            candidate_readiness_blocked_by=tuple(candidate_note.get("blocked_by") or ()),
            candidate_readiness_warnings=tuple(candidate_note.get("warnings") or ()),
            candidate_readiness_health_state=candidate_note.get("health_state"),
            candidate_readiness_observer_latest_run_id=candidate_note.get("observer_latest_run_id"),
            candidate_readiness_observer_latest_blocked_by=tuple(candidate_note.get("observer_latest_blocked_by") or ()),
            candidate_readiness_observer_latest_would_send_to_broker=candidate_note.get("observer_latest_would_send_to_broker"),
            candidate_readiness_observer_latest_bounded=candidate_note.get("observer_latest_bounded"),
            candidate_readiness_parameter_bundle_runtime=candidate_note.get("parameter_bundle_runtime"),
            current_mode_before=before.current_mode.value,
            current_mode_after=before.current_mode.value,
            command_path=commands_path,
            mode_state_path=state_path,
            readiness=readiness,
            readiness_ready=False,
            blocked_by=blocked,
            already_applied_command_ids=tuple(sorted(already_applied)),
            candidate_command_count=len(candidates),
            command_read_skipped_count=command_read.skipped_count,
            mode_state_read_skipped_count=state_skipped,
            mode_changed=False,
            would_send_to_broker=False,
            read_only=True,
        )
    record = build_mode_state_record_from_command(current_mode=before.current_mode, command_record=command)
    return ModeChangeCommandReadinessApplyPreview(
        would_apply=True,
        would_reject_by_readiness=False,
        skip_reason=None,
        command_id=command.command_id,
        candidate_command_type=command.command.command_type.value,
        candidate_requested_by=command.command.requested_by,
        candidate_requested_at=command.command.requested_at,
        candidate_current_mode=command.command.current_mode,
        candidate_target_mode=str(command.command.target) if command.command.target is not None else None,
        candidate_accepted=command.accepted,
        candidate_blocked_by=tuple(command.blocked_by),
        candidate_readiness_note_present=bool(candidate_note),
        candidate_readiness_ready=candidate_note.get("ready"),
        candidate_readiness_current_mode=candidate_note.get("current_mode"),
        candidate_readiness_target_mode=candidate_note.get("target_mode"),
        candidate_readiness_blocked_by=tuple(candidate_note.get("blocked_by") or ()),
        candidate_readiness_warnings=tuple(candidate_note.get("warnings") or ()),
        candidate_readiness_health_state=candidate_note.get("health_state"),
        candidate_readiness_observer_latest_run_id=candidate_note.get("observer_latest_run_id"),
        candidate_readiness_observer_latest_blocked_by=tuple(candidate_note.get("observer_latest_blocked_by") or ()),
        candidate_readiness_observer_latest_would_send_to_broker=candidate_note.get("observer_latest_would_send_to_broker"),
        candidate_readiness_observer_latest_bounded=candidate_note.get("observer_latest_bounded"),
        candidate_readiness_parameter_bundle_runtime=candidate_note.get("parameter_bundle_runtime"),
        current_mode_before=before.current_mode.value,
        current_mode_after=record.current_mode.value,
        command_path=commands_path,
        mode_state_path=state_path,
        readiness=readiness,
        readiness_ready=True,
        blocked_by=(),
        already_applied_command_ids=tuple(sorted(already_applied)),
        candidate_command_count=len(candidates),
        command_read_skipped_count=command_read.skipped_count,
        mode_state_read_skipped_count=state_skipped,
        mode_changed=record.mode_changed,
        would_send_to_broker=False,
        read_only=True,
    )

def apply_latest_mode_change_command_once_with_readiness_recheck(
    *,
    command_path: Path | None = None,
    mode_state_path: Path | None = None,
    max_lines: int | None = 1000,
    max_observer_run_age_sec: float = 120.0,
    allow_warnings: bool = False,
) -> ModeChangeCommandReadinessApplyResult:
    commands_path = command_path or default_command_ledger_path(ensure=False)
    state_path = mode_state_path or default_mode_state_ledger_path(ensure=True)
    before = current_mode_state(state_path, max_lines=max_lines)
    already_applied, state_skipped = _applied_command_ids(state_path, max_lines=max_lines)
    command_read = read_command_ledger_rows(commands_path, max_lines=max_lines)
    candidates = [
        row
        for row in command_read.rows
        if row.accepted
        and row.command.command_type == CommandType.REQUEST_MODE_CHANGE
        and row.command_id not in already_applied
    ]
    if not candidates:
        return ModeChangeCommandReadinessApplyResult(
            applied=False,
            skipped=True,
            rejected_by_readiness=False,
            skip_reason="no_unapplied_accepted_mode_change_command",
            command_id=None,
            current_mode_before=before.current_mode.value,
            current_mode_after=before.current_mode.value,
            command_path=commands_path,
            mode_state_path=state_path,
            mode_state_record=None,
            readiness=None,
            readiness_ready=False,
            blocked_by=(),
            already_applied_command_ids=tuple(sorted(already_applied)),
            candidate_command_count=0,
            command_read_skipped_count=command_read.skipped_count,
            mode_state_read_skipped_count=state_skipped,
            record_appended=False,
            mode_changed=False,
            would_send_to_broker=False,
        )
    command = candidates[-1]
    candidate_note = _command_readiness_note_payload(command)
    enforce_parameter_bundle_runtime, required_parameter_bundle_stage = _candidate_parameter_bundle_recheck_controls(candidate_note)
    readiness = evaluate_autotrade_live_readiness(
        current_mode=before.current_mode,
        target_mode=command.command.target,
        human_confirmed=bool(command.command.confirmation),
        allow_warnings=allow_warnings,
        enforce_parameter_bundle_runtime=enforce_parameter_bundle_runtime,
        required_parameter_bundle_stage=required_parameter_bundle_stage,
        max_observer_run_age_sec=max_observer_run_age_sec,
        max_lines=max_lines,
    )
    if not readiness.ready:
        blocked = tuple(dict.fromkeys(("readiness_recheck_not_ready",) + tuple(readiness.blocked_by) + tuple(command.blocked_by)))
        record = _readiness_rejected_mode_state_record(
            current_mode=before.current_mode,
            command=command,
            readiness=readiness,
            blocked_by=blocked,
        )
        append_mode_state_record(state_path, record)
        return ModeChangeCommandReadinessApplyResult(
            applied=False,
            skipped=False,
            rejected_by_readiness=True,
            skip_reason="readiness_recheck_not_ready",
            command_id=command.command_id,
            candidate_command_type=command.command.command_type.value,
            candidate_requested_by=command.command.requested_by,
            candidate_requested_at=command.command.requested_at,
            candidate_current_mode=command.command.current_mode,
            candidate_target_mode=str(command.command.target) if command.command.target is not None else None,
            candidate_accepted=command.accepted,
            candidate_blocked_by=tuple(command.blocked_by),
            candidate_readiness_note_present=bool(candidate_note),
            candidate_readiness_ready=candidate_note.get("ready"),
            candidate_readiness_current_mode=candidate_note.get("current_mode"),
            candidate_readiness_target_mode=candidate_note.get("target_mode"),
            candidate_readiness_blocked_by=tuple(candidate_note.get("blocked_by") or ()),
            candidate_readiness_warnings=tuple(candidate_note.get("warnings") or ()),
            candidate_readiness_health_state=candidate_note.get("health_state"),
            candidate_readiness_observer_latest_run_id=candidate_note.get("observer_latest_run_id"),
            candidate_readiness_observer_latest_blocked_by=tuple(candidate_note.get("observer_latest_blocked_by") or ()),
            candidate_readiness_observer_latest_would_send_to_broker=candidate_note.get("observer_latest_would_send_to_broker"),
            candidate_readiness_observer_latest_bounded=candidate_note.get("observer_latest_bounded"),
            candidate_readiness_parameter_bundle_runtime=candidate_note.get("parameter_bundle_runtime"),
            current_mode_before=before.current_mode.value,
            current_mode_after=before.current_mode.value,
            command_path=commands_path,
            mode_state_path=state_path,
            mode_state_record=record,
            readiness=readiness,
            readiness_ready=False,
            blocked_by=blocked,
            already_applied_command_ids=tuple(sorted(already_applied)),
            candidate_command_count=len(candidates),
            command_read_skipped_count=command_read.skipped_count,
            mode_state_read_skipped_count=state_skipped,
            record_appended=True,
            mode_changed=False,
            would_send_to_broker=False,
        )
    record = build_mode_state_record_from_command(current_mode=before.current_mode, command_record=command)
    append_mode_state_record(state_path, record)
    return ModeChangeCommandReadinessApplyResult(
        applied=True,
        skipped=False,
        rejected_by_readiness=False,
        skip_reason=None,
        command_id=command.command_id,
        candidate_command_type=command.command.command_type.value,
        candidate_requested_by=command.command.requested_by,
        candidate_requested_at=command.command.requested_at,
        candidate_current_mode=command.command.current_mode,
        candidate_target_mode=str(command.command.target) if command.command.target is not None else None,
        candidate_accepted=command.accepted,
        candidate_blocked_by=tuple(command.blocked_by),
        candidate_readiness_note_present=bool(candidate_note),
        candidate_readiness_ready=candidate_note.get("ready"),
        candidate_readiness_current_mode=candidate_note.get("current_mode"),
        candidate_readiness_target_mode=candidate_note.get("target_mode"),
        candidate_readiness_blocked_by=tuple(candidate_note.get("blocked_by") or ()),
        candidate_readiness_warnings=tuple(candidate_note.get("warnings") or ()),
        candidate_readiness_health_state=candidate_note.get("health_state"),
        candidate_readiness_observer_latest_run_id=candidate_note.get("observer_latest_run_id"),
        candidate_readiness_observer_latest_blocked_by=tuple(candidate_note.get("observer_latest_blocked_by") or ()),
        candidate_readiness_observer_latest_would_send_to_broker=candidate_note.get("observer_latest_would_send_to_broker"),
        candidate_readiness_observer_latest_bounded=candidate_note.get("observer_latest_bounded"),
        candidate_readiness_parameter_bundle_runtime=candidate_note.get("parameter_bundle_runtime"),
        current_mode_before=before.current_mode.value,
        current_mode_after=record.current_mode.value,
        command_path=commands_path,
        mode_state_path=state_path,
        mode_state_record=record,
        readiness=readiness,
        readiness_ready=True,
        blocked_by=(),
        already_applied_command_ids=tuple(sorted(already_applied)),
        candidate_command_count=len(candidates),
        command_read_skipped_count=command_read.skipped_count,
        mode_state_read_skipped_count=state_skipped,
        record_appended=True,
        mode_changed=record.mode_changed,
        would_send_to_broker=False,
    )

def apply_latest_mode_change_command_once(
    *,
    command_path: Path | None = None,
    mode_state_path: Path | None = None,
    max_lines: int | None = 1000,
) -> ModeChangeCommandApplyResult:
    commands_path = command_path or default_command_ledger_path(ensure=False)
    state_path = mode_state_path or default_mode_state_ledger_path(ensure=True)
    before = current_mode_state(state_path, max_lines=max_lines)
    already_applied, state_skipped = _applied_command_ids(state_path, max_lines=max_lines)
    command_read = read_command_ledger_rows(commands_path, max_lines=max_lines)
    candidates = [
        row
        for row in command_read.rows
        if row.accepted
        and row.command.command_type == CommandType.REQUEST_MODE_CHANGE
        and row.command_id not in already_applied
    ]
    if not candidates:
        return ModeChangeCommandApplyResult(
            applied=False,
            skipped=True,
            skip_reason="no_unapplied_accepted_mode_change_command",
            command_id=None,
            current_mode_before=before.current_mode.value,
            current_mode_after=before.current_mode.value,
            command_path=commands_path,
            mode_state_path=state_path,
            mode_state_record=None,
            already_applied_command_ids=tuple(sorted(already_applied)),
            candidate_command_count=0,
            command_read_skipped_count=command_read.skipped_count,
            mode_state_read_skipped_count=state_skipped,
            mode_changed=False,
            would_send_to_broker=False,
            read_only_command_scan=True,
        )
    command = candidates[-1]
    record = build_mode_state_record_from_command(current_mode=before.current_mode, command_record=command)
    append_mode_state_record(state_path, record)
    return ModeChangeCommandApplyResult(
        applied=True,
        skipped=False,
        skip_reason=None,
        command_id=command.command_id,
        current_mode_before=before.current_mode.value,
        current_mode_after=record.current_mode.value,
        command_path=commands_path,
        mode_state_path=state_path,
        mode_state_record=record,
        already_applied_command_ids=tuple(sorted(already_applied)),
        candidate_command_count=len(candidates),
        command_read_skipped_count=command_read.skipped_count,
        mode_state_read_skipped_count=state_skipped,
        mode_changed=record.mode_changed,
        would_send_to_broker=False,
        read_only_command_scan=True,
    )
