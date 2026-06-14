# path: ./btcts_next/src/btcts/autotrade/execution/command_ledger.py
# desc: AutoTrade command request ledger persistence. Records requests only; no broker execution.

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Tuple

from btcts.autotrade.execution.command_request import CommandRequest, CommandType, validate_command_request
from btcts.autotrade.runtime_paths import command_ledger_path


@dataclass(frozen=True)
class CommandLedgerRecord:
    command_id: str
    accepted: bool
    blocked_by: Tuple[str, ...]
    command: CommandRequest
    ledger_event: str = "autotrade.command_request_validated"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ledger_event": self.ledger_event,
            "command_id": self.command_id,
            "accepted": self.accepted,
            "blocked_by": list(self.blocked_by),
            "command": self.command.to_dict(),
        }


def default_command_ledger_path(*, ensure: bool = True) -> Path:
    return command_ledger_path(ensure=ensure)


def build_command_ledger_record(command: CommandRequest) -> CommandLedgerRecord:
    validation = validate_command_request(command)
    return CommandLedgerRecord(
        command_id=command.command_id,
        accepted=validation.accepted,
        blocked_by=validation.blocked_by,
        command=command,
    )


def append_command_ledger_record(path: Path, record: CommandLedgerRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")


def validate_and_append_command(path: Path, command: CommandRequest) -> CommandLedgerRecord:
    record = build_command_ledger_record(command)
    append_command_ledger_record(path, record)
    return record


def read_command_ledger(path: Path) -> Tuple[CommandLedgerRecord, ...]:
    rows: list[CommandLedgerRecord] = []
    if not path.exists():
        return ()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        command_obj = obj.get("command") or {}
        command = CommandRequest(
            command_id=str(command_obj.get("command_id") or ""),
            command_type=CommandType(str(command_obj.get("command_type") or "REQUEST_HALT_NEW")),
            requested_by=str(command_obj.get("requested_by") or ""),
            requested_at=str(command_obj.get("requested_at") or ""),
            current_mode=str(command_obj.get("current_mode") or ""),
            target=command_obj.get("target"),
            confirmation=bool(command_obj.get("confirmation")),
            reason_codes=tuple(command_obj.get("reason_codes") or ()),
            note=str(command_obj.get("note") or ""),
        )
        rows.append(
            CommandLedgerRecord(
                command_id=str(obj.get("command_id") or command.command_id),
                accepted=bool(obj.get("accepted")),
                blocked_by=tuple(obj.get("blocked_by") or ()),
                command=command,
                ledger_event=str(obj.get("ledger_event") or "autotrade.command_request_validated"),
            )
        )
    return tuple(rows)
