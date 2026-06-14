# path: ./btcts_next/src/btcts/autotrade/execution/command_request.py
# desc: AutoTrade command request contracts. UI may request; runtime validates.

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Tuple


class CommandType(str, Enum):
    REQUEST_MODE_CHANGE = "REQUEST_MODE_CHANGE"
    REQUEST_KILL_SWITCH = "REQUEST_KILL_SWITCH"
    REQUEST_PARAMETER_APPLY = "REQUEST_PARAMETER_APPLY"
    REQUEST_MANUAL_APPROVE_ORDER_INTENT = "REQUEST_MANUAL_APPROVE_ORDER_INTENT"
    REQUEST_CANCEL_ORDER = "REQUEST_CANCEL_ORDER"
    REQUEST_EMERGENCY_FLATTEN = "REQUEST_EMERGENCY_FLATTEN"
    REQUEST_HALT_NEW = "REQUEST_HALT_NEW"
    REQUEST_HALT_AND_CANCEL = "REQUEST_HALT_AND_CANCEL"


DANGEROUS_COMMANDS = frozenset(
    {
        CommandType.REQUEST_MODE_CHANGE,
        CommandType.REQUEST_PARAMETER_APPLY,
        CommandType.REQUEST_MANUAL_APPROVE_ORDER_INTENT,
        CommandType.REQUEST_CANCEL_ORDER,
        CommandType.REQUEST_EMERGENCY_FLATTEN,
        CommandType.REQUEST_HALT_AND_CANCEL,
    }
)


@dataclass(frozen=True)
class CommandRequest:
    command_id: str
    command_type: CommandType
    requested_by: str
    requested_at: str
    current_mode: str
    target: str | None
    confirmation: bool
    reason_codes: Tuple[str, ...] = ()
    note: str = ""

    @property
    def confirmation_required(self) -> bool:
        return self.command_type in DANGEROUS_COMMANDS

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["command_type"] = self.command_type.value
        data["confirmation_required"] = self.confirmation_required
        return data


@dataclass(frozen=True)
class CommandValidationResult:
    accepted: bool
    blocked_by: Tuple[str, ...]
    command: CommandRequest

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accepted": self.accepted,
            "blocked_by": list(self.blocked_by),
            "command": self.command.to_dict(),
        }


def validate_command_request(command: CommandRequest) -> CommandValidationResult:
    blocked: list[str] = []
    if command.confirmation_required and not command.confirmation:
        blocked.append("confirmation_required")
    if not command.command_id.startswith("cmd_"):
        blocked.append("invalid_command_id")
    if not command.requested_by:
        blocked.append("requested_by_required")
    return CommandValidationResult(accepted=not blocked, blocked_by=tuple(blocked), command=command)
