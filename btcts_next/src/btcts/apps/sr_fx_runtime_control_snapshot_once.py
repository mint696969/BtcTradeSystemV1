# path: ./btcts_next/src/btcts/apps/sr_fx_runtime_control_snapshot_once.py
# desc: One-shot broker-free runtime_control snapshot writer for heartbeat / incident / kill-switch visibility. No mode changes and no broker calls.

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from btcts.autotrade.execution.command_request import CommandType
from btcts.autotrade.execution.command_status import summarize_command_ledger
from btcts.autotrade.execution.runtime_control import (
    DEFAULT_HEARTBEAT_MAX_AGE_SEC,
    DEFAULT_KILL_SWITCH_ACTION,
    build_runtime_control_snapshot,
    build_runtime_heartbeat_state,
    build_runtime_incident_record,
    build_runtime_kill_switch_state,
    runtime_control_state_path,
    write_runtime_control_snapshot,
)

STAGE = "sr_fx_runtime_control_snapshot_once"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _print_json(data: Mapping[str, Any]) -> None:
    print(json.dumps(dict(data), ensure_ascii=False, indent=2, sort_keys=True, default=str))


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _env_bool_or_none(name: str) -> bool | None:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return None
    return raw in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return int(raw)


def _json_env(name: str) -> Any:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    return json.loads(raw)


def _normalize_command_action(command_type: str | None, target: str | None = None) -> str:
    value = str(command_type or target or "").strip().upper()
    target_value = str(target or "").strip().upper()
    if value == CommandType.REQUEST_HALT_AND_CANCEL.value or target_value in {"HALT_AND_CANCEL", "REQUEST_HALT_AND_CANCEL"}:
        return "HALT_AND_CANCEL"
    if value == CommandType.REQUEST_EMERGENCY_FLATTEN.value or target_value in {"EMERGENCY_FLATTEN", "REQUEST_EMERGENCY_FLATTEN"}:
        return "EMERGENCY_FLATTEN"
    return "HALT_NEW"


def _command_summary(max_lines: int) -> Dict[str, Any]:
    try:
        return summarize_command_ledger(max_lines=max_lines).to_dict()
    except Exception as exc:
        return {
            "exists": False,
            "read_only": True,
            "would_send_to_broker": False,
            "error": str(exc),
            "error_class": exc.__class__.__name__,
        }


def _kill_switch_from_inputs(command_summary: Mapping[str, Any]) -> Dict[str, Any]:
    explicit_active = _env_bool_or_none("BTCTS_RUNTIME_CONTROL_KILL_SWITCH_ACTIVE")
    explicit_action = os.getenv("BTCTS_RUNTIME_CONTROL_KILL_SWITCH_ACTION") or os.getenv("BTCTS_AUTOTRADE_KILL_SWITCH_ACTION")
    explicit_reason = os.getenv("BTCTS_RUNTIME_CONTROL_KILL_SWITCH_REASON") or os.getenv("BTCTS_AUTOTRADE_KILL_SWITCH_REASON")
    explicit_command_id = os.getenv("BTCTS_RUNTIME_CONTROL_KILL_SWITCH_COMMAND_ID")

    if explicit_active is not None:
        return {
            "active": explicit_active,
            "action": explicit_action or DEFAULT_KILL_SWITCH_ACTION,
            "reason": explicit_reason,
            "source": "env:BTCTS_RUNTIME_CONTROL_KILL_SWITCH_ACTIVE",
            "command_id": explicit_command_id,
        }

    latest_type = str(command_summary.get("latest_command_type") or "")
    latest_accepted = bool(command_summary.get("latest_accepted"))
    latest_target = command_summary.get("latest_target")
    command_trigger_types = {
        CommandType.REQUEST_KILL_SWITCH.value,
        CommandType.REQUEST_HALT_NEW.value,
        CommandType.REQUEST_HALT_AND_CANCEL.value,
        CommandType.REQUEST_EMERGENCY_FLATTEN.value,
    }
    if latest_accepted and latest_type in command_trigger_types:
        return {
            "active": True,
            "action": explicit_action or _normalize_command_action(latest_type, str(latest_target or "")),
            "reason": explicit_reason or f"latest_accepted_command:{latest_type}",
            "source": "command_ledger.latest_accepted_control_command",
            "command_id": command_summary.get("latest_command_id"),
        }

    return {
        "active": False,
        "action": explicit_action or DEFAULT_KILL_SWITCH_ACTION,
        "reason": explicit_reason,
        "source": "runtime_control_snapshot_once",
        "command_id": explicit_command_id,
    }


def _incident_rows(now: str) -> list[dict[str, Any]]:
    incidents_json = _json_env("BTCTS_RUNTIME_CONTROL_INCIDENTS_JSON")
    if incidents_json is not None:
        if not isinstance(incidents_json, list):
            raise RuntimeError("BTCTS_RUNTIME_CONTROL_INCIDENTS_JSON must be a JSON array")
        return [dict(item) for item in incidents_json if isinstance(item, Mapping)]

    if not _env_bool("BTCTS_RUNTIME_CONTROL_INCIDENT_OPEN", False):
        return []

    return [
        {
            "incident_id": os.getenv("BTCTS_RUNTIME_CONTROL_INCIDENT_ID") or "inc_runtime_control_manual",
            "severity": os.getenv("BTCTS_RUNTIME_CONTROL_INCIDENT_SEVERITY") or "medium",
            "status": os.getenv("BTCTS_RUNTIME_CONTROL_INCIDENT_STATUS") or "open",
            "opened_at": os.getenv("BTCTS_RUNTIME_CONTROL_INCIDENT_OPENED_AT") or now,
            "reason": os.getenv("BTCTS_RUNTIME_CONTROL_INCIDENT_REASON") or "manual_runtime_control_incident",
            "command_id": os.getenv("BTCTS_RUNTIME_CONTROL_INCIDENT_COMMAND_ID") or None,
            "closed_at": os.getenv("BTCTS_RUNTIME_CONTROL_INCIDENT_CLOSED_AT") or None,
        }
    ]


def build_snapshot_from_environment(*, now: str | None = None) -> dict[str, Any]:
    now_value = now or os.getenv("BTCTS_RUNTIME_CONTROL_NOW") or _utc_now_iso()
    max_lines = _env_int("BTCTS_RUNTIME_CONTROL_COMMAND_LEDGER_MAX_LINES", 1000)
    max_age = _env_int("BTCTS_RUNTIME_CONTROL_HEARTBEAT_MAX_AGE_SEC", DEFAULT_HEARTBEAT_MAX_AGE_SEC)
    observed_at = os.getenv("BTCTS_RUNTIME_CONTROL_HEARTBEAT_OBSERVED_AT") or now_value
    component = os.getenv("BTCTS_RUNTIME_CONTROL_HEARTBEAT_COMPONENT") or "autotrade.runtime"

    command = _command_summary(max_lines=max_lines)
    kill_input = _kill_switch_from_inputs(command)
    incident_input = _incident_rows(now_value)

    heartbeat = build_runtime_heartbeat_state(
        component=component,
        observed_at=observed_at,
        now=now_value,
        max_age_sec=max_age,
    )
    kill_switch = build_runtime_kill_switch_state(
        active=bool(kill_input["active"]),
        action=str(kill_input["action"] or DEFAULT_KILL_SWITCH_ACTION),
        reason=kill_input.get("reason"),
        source=str(kill_input.get("source") or "runtime_control_snapshot_once"),
        command_id=kill_input.get("command_id"),
    )
    incidents = tuple(
        build_runtime_incident_record(
            incident_id=str(row.get("incident_id") or "incident_unknown"),
            severity=str(row.get("severity") or "unknown"),
            status=str(row.get("status") or "open"),
            opened_at=row.get("opened_at") or now_value,
            reason=str(row.get("reason") or "unspecified"),
            command_id=row.get("command_id"),
            closed_at=row.get("closed_at"),
        )
        for row in incident_input
    )
    snapshot = build_runtime_control_snapshot(kill_switch=kill_switch, heartbeat=heartbeat, incidents=incidents)
    return {
        "snapshot": snapshot,
        "command_ledger_summary": command,
        "inputs": {
            "now": now_value,
            "heartbeat_observed_at": observed_at,
            "heartbeat_component": component,
            "heartbeat_max_age_sec": max_age,
            "kill_switch_source": kill_input.get("source"),
            "incident_count": len(incidents),
            "command_ledger_max_lines": max_lines,
        },
    }


def write_snapshot_from_environment(*, path: Path | None = None, now: str | None = None) -> dict[str, Any]:
    built = build_snapshot_from_environment(now=now)
    snapshot = built["snapshot"]
    out_path = write_runtime_control_snapshot(snapshot, path=path)
    loaded = snapshot.to_dict()
    loaded["exists"] = True
    loaded["path"] = str(out_path)
    return {
        "ok": bool(loaded.get("ok")),
        "stage": STAGE,
        "runtime_control_state_path": str(out_path),
        "runtime_control": loaded,
        "command_ledger_summary": built["command_ledger_summary"],
        "inputs": built["inputs"],
        "read_only": True,
        "would_send_to_broker": False,
        "mode_changed": False,
    }


def main() -> int:
    try:
        path = runtime_control_state_path(ensure=True)
        out = write_snapshot_from_environment(path=path)
    except Exception as exc:
        fallback_path = runtime_control_state_path(ensure=False)
        out = {
            "ok": False,
            "stage": STAGE,
            "runtime_control_state_path": str(fallback_path),
            "error": str(exc),
            "error_class": exc.__class__.__name__,
            "blocked_by": ["runtime_control_snapshot_write_failed"],
            "read_only": True,
            "would_send_to_broker": False,
            "mode_changed": False,
        }
    _print_json(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
