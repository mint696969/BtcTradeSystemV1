# path: ./btcts_next/src/btcts/autotrade/execution/mode_state.py
# desc: AutoTrade mode-state ledger contract. Records mode-state transitions only; no broker execution.

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.execution.command_ledger import CommandLedgerRecord
from btcts.autotrade.execution.command_request import CommandType
from btcts.autotrade.modes import AutoTradeMode
from btcts.autotrade.runtime_paths import decision_ledger_path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_mode_state_ledger_path(*, ensure: bool = True) -> Path:
    return decision_ledger_path("mode_state.jsonl", ensure=ensure)


@dataclass(frozen=True)
class ModeStateRecord:
    current_mode: AutoTradeMode
    previous_mode: AutoTradeMode
    changed_at: str
    source_command_id: str | None
    requested_by: str | None
    accepted: bool
    mode_changed: bool
    reason_codes: Tuple[str, ...] = ()
    blocked_by: Tuple[str, ...] = ()
    ledger_event: str = "autotrade.mode_state_recorded"
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["current_mode"] = self.current_mode.value
        data["previous_mode"] = self.previous_mode.value
        return data


@dataclass(frozen=True)
class ModeStateReadResult:
    path: Path
    rows: Tuple[ModeStateRecord, ...]
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
class ModeStateSummary:
    path: Path
    exists: bool
    total_rows: int
    skipped_rows: int
    current_mode: AutoTradeMode
    previous_mode: AutoTradeMode
    latest_changed_at: str | None = None
    latest_source_command_id: str | None = None
    latest_requested_by: str | None = None
    latest_accepted: bool | None = None
    latest_mode_changed: bool | None = None
    latest_ledger_event: str | None = None
    latest_reason_codes: Tuple[str, ...] = ()
    latest_blocked_by: Tuple[str, ...] = ()
    latest_would_send_to_broker: bool | None = None
    mode_counts: Dict[str, int] = field(default_factory=dict)
    blocked_by_counts: Dict[str, int] = field(default_factory=dict)
    error_samples: Tuple[str, ...] = ()
    would_send_to_broker: bool = False
    read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        data["current_mode"] = self.current_mode.value
        data["previous_mode"] = self.previous_mode.value
        return data


DEFAULT_MODE_STATE = ModeStateRecord(
    current_mode=AutoTradeMode.OFF,
    previous_mode=AutoTradeMode.OFF,
    changed_at="1970-01-01T00:00:00Z",
    source_command_id=None,
    requested_by="default",
    accepted=True,
    mode_changed=False,
    reason_codes=("default_off",),
    blocked_by=(),
    ledger_event="autotrade.mode_state_default",
    would_send_to_broker=False,
)


def _coerce_mode(value: AutoTradeMode | str | None, *, default: AutoTradeMode = AutoTradeMode.OFF) -> AutoTradeMode:
    if isinstance(value, AutoTradeMode):
        return value
    if value is None:
        return default
    return AutoTradeMode(str(value))


def build_mode_state_record_from_command(
    *,
    current_mode: AutoTradeMode | str,
    command_record: CommandLedgerRecord,
    changed_at: str | None = None,
) -> ModeStateRecord:
    previous = _coerce_mode(current_mode)
    command = command_record.command
    is_mode_change = command.command_type == CommandType.REQUEST_MODE_CHANGE
    accepted = bool(command_record.accepted and is_mode_change)
    target = _coerce_mode(command.target, default=previous) if accepted else previous
    mode_changed = bool(accepted and target != previous)
    blocked = list(command_record.blocked_by)
    if not is_mode_change:
        blocked.append("not_mode_change_command")
    if not command_record.accepted:
        blocked.append("source_command_not_accepted")
    return ModeStateRecord(
        current_mode=target,
        previous_mode=previous,
        changed_at=changed_at or _utc_now(),
        source_command_id=command_record.command_id,
        requested_by=command.requested_by,
        accepted=accepted,
        mode_changed=mode_changed,
        reason_codes=tuple(command.reason_codes),
        blocked_by=tuple(dict.fromkeys(blocked)),
        ledger_event="autotrade.mode_state_recorded",
        would_send_to_broker=False,
    )


def append_mode_state_record(path: Path, record: ModeStateRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + chr(10))


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


def _parse_record(obj: Any) -> ModeStateRecord:
    if not isinstance(obj, dict):
        raise ValueError("not_object")
    return ModeStateRecord(
        current_mode=_coerce_mode(obj.get("current_mode")),
        previous_mode=_coerce_mode(obj.get("previous_mode")),
        changed_at=str(obj.get("changed_at") or ""),
        source_command_id=obj.get("source_command_id"),
        requested_by=obj.get("requested_by"),
        accepted=bool(obj.get("accepted")),
        mode_changed=bool(obj.get("mode_changed")),
        reason_codes=tuple(obj.get("reason_codes") or ()),
        blocked_by=tuple(obj.get("blocked_by") or ()),
        ledger_event=str(obj.get("ledger_event") or "autotrade.mode_state_recorded"),
        would_send_to_broker=bool(obj.get("would_send_to_broker", False)),
    )


def read_mode_state_records(path: Path | None = None, *, max_lines: int | None = 1000) -> ModeStateReadResult:
    target = path or default_mode_state_ledger_path(ensure=False)
    rows: list[ModeStateRecord] = []
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
    return ModeStateReadResult(path=target, rows=tuple(rows), skipped_count=skipped, error_samples=tuple(errors))


def current_mode_state(path: Path | None = None, *, max_lines: int | None = 1000) -> ModeStateRecord:
    read = read_mode_state_records(path, max_lines=max_lines)
    if not read.rows:
        return DEFAULT_MODE_STATE
    return read.rows[-1]


def summarize_mode_state(path: Path | None = None, *, max_lines: int | None = 1000) -> ModeStateSummary:
    target = path or default_mode_state_ledger_path(ensure=False)
    read = read_mode_state_records(target, max_lines=max_lines)
    latest = read.rows[-1] if read.rows else DEFAULT_MODE_STATE
    mode_counter: Counter[str] = Counter(row.current_mode.value for row in read.rows)
    blocked_counter: Counter[str] = Counter()
    for row in read.rows:
        blocked_counter.update(row.blocked_by)
    return ModeStateSummary(
        path=target,
        exists=target.exists(),
        total_rows=len(read.rows),
        skipped_rows=read.skipped_count,
        current_mode=latest.current_mode,
        previous_mode=latest.previous_mode,
        latest_changed_at=latest.changed_at,
        latest_source_command_id=latest.source_command_id,
        latest_requested_by=latest.requested_by,
        latest_accepted=latest.accepted,
        latest_mode_changed=latest.mode_changed,
        latest_ledger_event=latest.ledger_event,
        latest_reason_codes=latest.reason_codes,
        latest_blocked_by=latest.blocked_by,
        latest_would_send_to_broker=latest.would_send_to_broker,
        mode_counts=dict(mode_counter),
        blocked_by_counts=dict(blocked_counter),
        error_samples=read.error_samples,
        would_send_to_broker=False,
        read_only=True,
    )
