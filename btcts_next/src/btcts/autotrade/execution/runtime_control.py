# path: ./btcts_next/src/btcts/autotrade/execution/runtime_control.py
# desc: AutoTrade runtime control scaffold for kill switch / incident / heartbeat. Read-only by default; no broker calls.

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Tuple

from btcts.autotrade.execution.command_request import CommandType
from btcts.autotrade.runtime_paths import autotrade_runtime_paths

DEFAULT_KILL_SWITCH_ACTION = "HALT_NEW"
VALID_KILL_SWITCH_ACTIONS = frozenset({"HALT_NEW", "HALT_AND_CANCEL", "EMERGENCY_FLATTEN"})
DEFAULT_HEARTBEAT_MAX_AGE_SEC = 10


@dataclass(frozen=True)
class RuntimeKillSwitchState:
    active: bool
    action: str = DEFAULT_KILL_SWITCH_ACTION
    reason: str | None = None
    source: str = "runtime_control"
    command_id: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeHeartbeatState:
    component: str
    observed_at: str | None
    now: str
    max_age_sec: int = DEFAULT_HEARTBEAT_MAX_AGE_SEC
    age_sec: float | None = None
    fresh: bool = False
    blocked_by: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeIncidentRecord:
    incident_id: str
    severity: str
    status: str
    opened_at: str
    reason: str
    command_id: str | None = None
    closed_at: str | None = None

    @property
    def open(self) -> bool:
        return self.status.strip().lower() not in {"closed", "resolved"}

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["open"] = self.open
        return data


@dataclass(frozen=True)
class RuntimeControlSnapshot:
    ok: bool
    kill_switch: RuntimeKillSwitchState
    heartbeat: RuntimeHeartbeatState
    incidents: Tuple[RuntimeIncidentRecord, ...]
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...]
    read_only: bool = True
    would_send_to_broker: bool = False
    mode_changed: bool = False
    contract_version: str = "autotrade_runtime_control_snapshot.v1"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["kill_switch"] = self.kill_switch.to_dict()
        data["heartbeat"] = self.heartbeat.to_dict()
        data["incidents"] = [incident.to_dict() for incident in self.incidents]
        data["blocked_by"] = list(self.blocked_by)
        data["warnings"] = list(self.warnings)
        return data


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _unique(items: Iterable[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def runtime_control_state_path(*, ensure: bool = True) -> Path:
    paths = autotrade_runtime_paths(ensure=ensure)
    out = paths.diagnostics_dir / "runtime_control_state.json"
    if ensure:
        out.parent.mkdir(parents=True, exist_ok=True)
    return out


def build_runtime_heartbeat_state(
    *,
    component: str = "autotrade.runtime",
    observed_at: str | None = None,
    now: str | None = None,
    max_age_sec: int = DEFAULT_HEARTBEAT_MAX_AGE_SEC,
) -> RuntimeHeartbeatState:
    now_value = now or _utc_now_iso()
    blocked: list[str] = []
    observed_dt = _parse_ts(observed_at)
    now_dt = _parse_ts(now_value)
    age_sec: float | None = None

    if observed_dt is None:
        blocked.append("heartbeat_missing")
    elif now_dt is None:
        blocked.append("heartbeat_now_invalid")
    else:
        age_sec = max((now_dt - observed_dt).total_seconds(), 0.0)
        if age_sec > int(max_age_sec):
            blocked.append("heartbeat_stale")

    return RuntimeHeartbeatState(
        component=component,
        observed_at=observed_at,
        now=now_value,
        max_age_sec=int(max_age_sec),
        age_sec=age_sec,
        fresh=not blocked,
        blocked_by=_unique(blocked),
    )


def build_runtime_kill_switch_state(
    *,
    active: bool = False,
    action: str = DEFAULT_KILL_SWITCH_ACTION,
    reason: str | None = None,
    source: str = "runtime_control",
    command_id: str | None = None,
) -> RuntimeKillSwitchState:
    normalized_action = str(action or DEFAULT_KILL_SWITCH_ACTION).strip().upper()
    if normalized_action == CommandType.REQUEST_HALT_NEW.value:
        normalized_action = "HALT_NEW"
    elif normalized_action == CommandType.REQUEST_HALT_AND_CANCEL.value:
        normalized_action = "HALT_AND_CANCEL"
    elif normalized_action == CommandType.REQUEST_EMERGENCY_FLATTEN.value:
        normalized_action = "EMERGENCY_FLATTEN"

    if normalized_action not in VALID_KILL_SWITCH_ACTIONS:
        normalized_action = DEFAULT_KILL_SWITCH_ACTION

    return RuntimeKillSwitchState(
        active=bool(active),
        action=normalized_action,
        reason=reason,
        source=source or "runtime_control",
        command_id=command_id,
    )


def build_runtime_incident_record(
    *,
    incident_id: str,
    severity: str,
    status: str = "open",
    opened_at: str | None = None,
    reason: str,
    command_id: str | None = None,
    closed_at: str | None = None,
) -> RuntimeIncidentRecord:
    return RuntimeIncidentRecord(
        incident_id=incident_id,
        severity=str(severity or "unknown"),
        status=str(status or "open"),
        opened_at=opened_at or _utc_now_iso(),
        reason=str(reason or "unspecified"),
        command_id=command_id,
        closed_at=closed_at,
    )


def build_runtime_control_snapshot(
    *,
    kill_switch: RuntimeKillSwitchState | Mapping[str, Any] | None = None,
    heartbeat: RuntimeHeartbeatState | Mapping[str, Any] | None = None,
    incidents: Iterable[RuntimeIncidentRecord | Mapping[str, Any]] = (),
) -> RuntimeControlSnapshot:
    warnings: list[str] = ["runtime_control_scaffold_read_only"]
    blocked: list[str] = []

    if isinstance(kill_switch, RuntimeKillSwitchState):
        kill_state = kill_switch
    elif isinstance(kill_switch, Mapping):
        kill_state = build_runtime_kill_switch_state(
            active=bool(kill_switch.get("active")),
            action=str(kill_switch.get("action") or DEFAULT_KILL_SWITCH_ACTION),
            reason=kill_switch.get("reason"),
            source=str(kill_switch.get("source") or "runtime_control"),
            command_id=kill_switch.get("command_id"),
        )
    else:
        kill_state = build_runtime_kill_switch_state()

    if isinstance(heartbeat, RuntimeHeartbeatState):
        heartbeat_state = heartbeat
    elif isinstance(heartbeat, Mapping):
        heartbeat_state = build_runtime_heartbeat_state(
            component=str(heartbeat.get("component") or "autotrade.runtime"),
            observed_at=heartbeat.get("observed_at"),
            now=heartbeat.get("now"),
            max_age_sec=int(heartbeat.get("max_age_sec") or DEFAULT_HEARTBEAT_MAX_AGE_SEC),
        )
    else:
        heartbeat_state = build_runtime_heartbeat_state()

    incident_rows: list[RuntimeIncidentRecord] = []
    for item in incidents:
        if isinstance(item, RuntimeIncidentRecord):
            incident_rows.append(item)
        elif isinstance(item, Mapping):
            incident_rows.append(
                build_runtime_incident_record(
                    incident_id=str(item.get("incident_id") or "incident_unknown"),
                    severity=str(item.get("severity") or "unknown"),
                    status=str(item.get("status") or "open"),
                    opened_at=item.get("opened_at"),
                    reason=str(item.get("reason") or "unspecified"),
                    command_id=item.get("command_id"),
                    closed_at=item.get("closed_at"),
                )
            )

    if kill_state.active:
        blocked.append("kill_switch_active")
        blocked.append(f"kill_switch_action:{kill_state.action}")
    if kill_state.action == "EMERGENCY_FLATTEN":
        blocked.append("emergency_flatten_requires_separate_human_protocol")
    blocked.extend(heartbeat_state.blocked_by)
    if any(row.open for row in incident_rows):
        blocked.append("open_incident_present")

    blocked_tuple = _unique(blocked)
    return RuntimeControlSnapshot(
        ok=not blocked_tuple,
        kill_switch=kill_state,
        heartbeat=heartbeat_state,
        incidents=tuple(incident_rows),
        blocked_by=blocked_tuple,
        warnings=_unique(warnings),
        read_only=True,
        would_send_to_broker=False,
        mode_changed=False,
    )


def write_runtime_control_snapshot(snapshot: RuntimeControlSnapshot, path: Path | None = None) -> Path:
    out = path or runtime_control_state_path(ensure=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def read_runtime_control_snapshot(path: Path | None = None) -> Dict[str, Any]:
    src = path or runtime_control_state_path(ensure=False)
    if not src.exists():
        return {
            "exists": False,
            "path": str(src),
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
            "blocked_by": ["runtime_control_snapshot_missing"],
        }
    data = json.loads(src.read_text(encoding="utf-8"))
    data["exists"] = True
    data["path"] = str(src)
    data.setdefault("read_only", True)
    data.setdefault("would_send_to_broker", False)
    data.setdefault("mode_changed", False)
    return data
