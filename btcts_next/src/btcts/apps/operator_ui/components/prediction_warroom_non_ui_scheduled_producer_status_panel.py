# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_status_panel.py
# desc: PS-Q16C WarRoom read-only panel/loader for non-UI producer status. Reads prediction/status/non_ui_scheduled_producer_status.json only when explicitly allowed; renders status/warnings/safe flags without triggering producer, scheduler, runtime writes, parameter mutation, ledger, AutoTrade, or broker behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

import streamlit as st

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_non_ui_scheduled_producer_contract import (
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    REQUIRED_STATUS_FIELDS,
)

PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_STATUS_PANEL_VERSION = (
    "prediction_warroom_non_ui_scheduled_producer_status_panel.ps_q16c.v1"
)


@dataclass(frozen=True)
class PredictionWarRoomNonUiScheduledProducerStatusPanelPacket:
    panel_version: str
    panel_id: str
    panel_state: str
    hot_latest_root_hint: str
    status_artifact_relative_path: str = PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    status_artifact_path: str = ""
    allow_actual_read_requested: bool = False
    allow_guard_test_root: bool = False
    target_root_valid: bool = False
    path_exists: bool = False
    observed_file_size_bytes: int | None = None
    observed_age_sec: int | None = None
    observed_last_modified_at: str = ""
    actual_file_read_attempted: bool = False
    actual_file_read_succeeded: bool = False
    payload_decode_attempted: bool = False
    payload_decode_succeeded: bool = False
    payload: Mapping[str, Any] = field(default_factory=dict)
    status_rows: Tuple[Mapping[str, Any], ...] = ()
    safety_rows: Tuple[Mapping[str, Any], ...] = ()
    warning_rows: Tuple[Mapping[str, Any], ...] = ()
    missing_required_fields: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    display_only: bool = True
    guarded_loader_only: bool = True
    render_intent_only: bool = True
    warroom_ui_trigger_enabled: bool = False
    producer_runner_invoked: bool = False
    scheduler_enabled_by_this_panel: bool = False
    runtime_artifact_write_allowed: bool = False
    latest_prediction_artifact_write_allowed: bool = False
    status_artifact_write_allowed: bool = False
    parameter_apply_allowed: bool = False
    parameter_staging_write_allowed: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    would_write_runtime_artifact: bool = False
    would_write_latest_prediction_artifact: bool = False
    would_write_status_artifact: bool = False
    would_write_collector_state: bool = False
    would_mutate_live_parameters: bool = False
    would_append_parameter_version: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "panel_version": self.panel_version,
            "panel_id": self.panel_id,
            "panel_state": self.panel_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "status_artifact_relative_path": self.status_artifact_relative_path,
            "status_artifact_path": self.status_artifact_path,
            "allow_actual_read_requested": self.allow_actual_read_requested,
            "allow_guard_test_root": self.allow_guard_test_root,
            "target_root_valid": self.target_root_valid,
            "path_exists": self.path_exists,
            "observed_file_size_bytes": self.observed_file_size_bytes,
            "observed_age_sec": self.observed_age_sec,
            "observed_last_modified_at": self.observed_last_modified_at,
            "actual_file_read_attempted": self.actual_file_read_attempted,
            "actual_file_read_succeeded": self.actual_file_read_succeeded,
            "payload_decode_attempted": self.payload_decode_attempted,
            "payload_decode_succeeded": self.payload_decode_succeeded,
            "payload": dict(self.payload),
            "status_rows": [dict(row) for row in self.status_rows],
            "safety_rows": [dict(row) for row in self.safety_rows],
            "warning_rows": [dict(row) for row in self.warning_rows],
            "missing_required_fields": list(self.missing_required_fields),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "display_only": self.display_only,
            "guarded_loader_only": self.guarded_loader_only,
            "render_intent_only": self.render_intent_only,
            "warroom_ui_trigger_enabled": self.warroom_ui_trigger_enabled,
            "producer_runner_invoked": self.producer_runner_invoked,
            "scheduler_enabled_by_this_panel": self.scheduler_enabled_by_this_panel,
            "runtime_artifact_write_allowed": self.runtime_artifact_write_allowed,
            "latest_prediction_artifact_write_allowed": self.latest_prediction_artifact_write_allowed,
            "status_artifact_write_allowed": self.status_artifact_write_allowed,
            "parameter_apply_allowed": self.parameter_apply_allowed,
            "parameter_staging_write_allowed": self.parameter_staging_write_allowed,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_latest_prediction_artifact": self.would_write_latest_prediction_artifact,
            "would_write_status_artifact": self.would_write_status_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_mutate_live_parameters": self.would_mutate_live_parameters,
            "would_append_parameter_version": self.would_append_parameter_version,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


def _hot_root_ok(root: str, *, allow_guard_test_root: bool = False) -> bool:
    normalized = str(root).rstrip("\\/").lower().replace("/", "\\")
    if normalized == "d:\\btc_ts_hot":
        return True
    return bool(allow_guard_test_root and normalized)


def _status_path(root: str) -> Path:
    return Path(str(root).rstrip("\\/")) / "prediction" / "status" / "non_ui_scheduled_producer_status.json"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _age_and_mtime(path: Path) -> tuple[int | None, str]:
    if not path.exists():
        return None, ""
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age = max(0, int((datetime.now(timezone.utc) - modified).total_seconds()))
    return age, modified.isoformat()


def _status_rows(payload: Mapping[str, Any], *, path: str, age: int | None) -> tuple[Mapping[str, Any], ...]:
    return (
        {"item": "producer_state", "value": payload.get("producer_state"), "read_only": True, "execution": False},
        {"item": "producer_enabled", "value": payload.get("producer_enabled"), "read_only": True, "execution": False},
        {"item": "scheduler_enabled", "value": payload.get("scheduler_enabled"), "read_only": True, "execution": False},
        {"item": "runtime_artifact_write_enabled", "value": payload.get("runtime_artifact_write_enabled"), "read_only": True, "execution": False},
        {"item": "last_run_started_at", "value": payload.get("last_run_started_at"), "read_only": True, "execution": False},
        {"item": "last_success_at", "value": payload.get("last_success_at"), "read_only": True, "execution": False},
        {"item": "last_failure_at", "value": payload.get("last_failure_at"), "read_only": True, "execution": False},
        {"item": "last_success_generated_at", "value": payload.get("last_success_generated_at"), "read_only": True, "execution": False},
        {"item": "last_prediction_run_id", "value": payload.get("last_prediction_run_id"), "read_only": True, "execution": False},
        {"item": "warning_blocker_count", "value": f"warnings={payload.get('last_warning_count')}; blockers={payload.get('last_blocker_count')}", "read_only": True, "execution": False},
        {"item": "status_path", "value": path, "read_only": True, "execution": False},
        {"item": "status_age_sec", "value": age, "read_only": True, "execution": False},
    )


def _safety_rows(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    safe_flags = _as_mapping(payload.get("safe_flags"))
    rows = [
        {"boundary": "producer_enabled", "enabled": payload.get("producer_enabled") is True},
        {"boundary": "scheduler_enabled", "enabled": payload.get("scheduler_enabled") is True},
        {"boundary": "runtime_artifact_write_enabled", "enabled": payload.get("runtime_artifact_write_enabled") is True},
        {"boundary": "disable_rollback_state", "enabled": payload.get("disable_rollback_state")},
    ]
    rows.extend({"boundary": str(key), "enabled": bool(value)} for key, value in safe_flags.items())
    return tuple(rows)


def _warning_rows(payload: Mapping[str, Any], blockers: tuple[str, ...], warnings: tuple[str, ...]) -> tuple[Mapping[str, Any], ...]:
    rows: list[Mapping[str, Any]] = []
    rows.extend({"severity": "blocker", "reason": item, "read_only": True, "execution": False} for item in blockers)
    rows.extend({"severity": "warning", "reason": item, "read_only": True, "execution": False} for item in warnings)
    rows.extend({"severity": "blocker", "reason": str(item), "read_only": True, "execution": False} for item in _list(payload.get("blockers")))
    rows.extend({"severity": "warning", "reason": str(item), "read_only": True, "execution": False} for item in _list(payload.get("warnings")))
    if not rows:
        rows.append({"severity": "ok", "reason": "no_producer_status_blockers_or_warnings", "read_only": True, "execution": False})
    return tuple(rows)


def build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    allow_actual_read: bool = False,
    allow_guard_test_root: bool = False,
) -> PredictionWarRoomNonUiScheduledProducerStatusPanelPacket:
    """Build a read-only WarRoom producer-status display packet.

    The loader reads only prediction/status/non_ui_scheduled_producer_status.json after
    explicit allow_actual_read. It never invokes the producer runner or writes artifacts.
    """
    blockers: list[str] = []
    warnings: list[str] = []
    target_root_valid = _hot_root_ok(str(hot_latest_root_hint), allow_guard_test_root=allow_guard_test_root)
    if not target_root_valid:
        blockers.append("target_root_invalid_for_producer_status_panel")
    if not allow_actual_read:
        blockers.append("allow_actual_read_false")
    path = _status_path(str(hot_latest_root_hint))
    age, modified = _age_and_mtime(path)
    payload: Mapping[str, Any] = {}
    read_attempted = bool(allow_actual_read and target_root_valid)
    read_ok = False
    decode_attempted = False
    decode_ok = False
    if read_attempted:
        if not path.exists():
            warnings.append("producer_status_artifact_missing")
        else:
            try:
                text = path.read_text(encoding="utf-8")
                read_ok = True
                decode_attempted = True
                decoded = json.loads(text)
                if isinstance(decoded, Mapping):
                    payload = decoded
                    decode_ok = True
                else:
                    blockers.append("producer_status_payload_not_mapping")
            except Exception as exc:  # noqa: BLE001 - fail closed and report display-only diagnostic
                blockers.append("producer_status_read_or_decode_failed:" + exc.__class__.__name__)
                warnings.append(str(exc))
    missing = tuple(field for field in REQUIRED_STATUS_FIELDS if decode_ok and field not in payload)
    if missing:
        blockers.append("producer_status_missing_required_fields")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    state = "producer_status_panel_loaded" if decode_ok and not unique_blockers else (
        "producer_status_panel_missing" if read_attempted and not path.exists() and not unique_blockers else "producer_status_panel_blocked"
    )
    status_rows = _status_rows(payload, path=str(path), age=age) if payload else ()
    safety_rows = _safety_rows(payload) if payload else ()
    warning_rows = _warning_rows(payload, unique_blockers, unique_warnings)
    return PredictionWarRoomNonUiScheduledProducerStatusPanelPacket(
        panel_version=PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_STATUS_PANEL_VERSION,
        panel_id=f"{PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_STATUS_PANEL_VERSION}:{state}",
        panel_state=state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        status_artifact_path=str(path),
        allow_actual_read_requested=allow_actual_read,
        allow_guard_test_root=allow_guard_test_root,
        target_root_valid=target_root_valid,
        path_exists=path.exists(),
        observed_file_size_bytes=int(path.stat().st_size) if path.exists() else None,
        observed_age_sec=age,
        observed_last_modified_at=modified,
        actual_file_read_attempted=read_attempted,
        actual_file_read_succeeded=read_ok,
        payload_decode_attempted=decode_attempted,
        payload_decode_succeeded=decode_ok,
        payload=payload,
        status_rows=status_rows,
        safety_rows=safety_rows,
        warning_rows=warning_rows,
        missing_required_fields=missing,
        blocker_count=len(unique_blockers) + len(_list(payload.get("blockers"))) if payload else len(unique_blockers),
        warning_count=len(unique_warnings) + len(_list(payload.get("warnings"))) if payload else len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
    )


def render_prediction_warroom_non_ui_scheduled_producer_status_panel(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
) -> Mapping[str, Any]:
    """Render PS-Q16C producer status rows in WarRoom as read-only observation."""
    packet = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet(
        hot_latest_root_hint=hot_latest_root_hint,
        allow_actual_read=True,
    ).to_dict()
    st.session_state["warroom_non_ui_scheduled_producer_status_panel_snapshot"] = {
        "panel_version": packet.get("panel_version"),
        "panel_state": packet.get("panel_state"),
        "status_artifact_path": packet.get("status_artifact_path"),
        "path_exists": packet.get("path_exists"),
        "payload_decode_succeeded": packet.get("payload_decode_succeeded"),
        "blocker_count": packet.get("blocker_count"),
        "warning_count": packet.get("warning_count"),
        "safe_boundary": {
            "read_only": packet.get("read_only") is True,
            "producer_runner_invoked_false": packet.get("producer_runner_invoked") is False,
            "scheduler_enabled_by_this_panel_false": packet.get("scheduler_enabled_by_this_panel") is False,
            "would_write_status_artifact_false": packet.get("would_write_status_artifact") is False,
            "would_write_latest_prediction_artifact_false": packet.get("would_write_latest_prediction_artifact") is False,
            "autotrade_trigger_allowed_false": packet.get("autotrade_trigger_allowed") is False,
            "broker_private_api_allowed_false": packet.get("broker_private_api_allowed") is False,
        },
    }
    st.caption(
        "PS-Q16C producer status is read-only: reads status artifact only; no producer trigger, "
        "no scheduler, no latest prediction write, no parameter apply/staging, no ledger, no AutoTrade, no broker."
    )
    st.caption(
        "panel_state={state}; exists={exists}; decoded={decoded}; age_sec={age}; blockers={blockers}; warnings={warnings}".format(
            state=packet.get("panel_state"),
            exists=packet.get("path_exists"),
            decoded=packet.get("payload_decode_succeeded"),
            age=packet.get("observed_age_sec"),
            blockers=packet.get("blocker_count"),
            warnings=packet.get("warning_count"),
        )
    )
    if packet.get("status_rows"):
        st.dataframe(packet.get("status_rows"), width="stretch", hide_index=True)
    if packet.get("safety_rows"):
        st.caption("Producer safety / disable state")
        st.dataframe(packet.get("safety_rows"), width="stretch", hide_index=True)
    if packet.get("warning_rows"):
        st.caption("Producer warnings / blockers")
        st.dataframe(packet.get("warning_rows"), width="stretch", hide_index=True)
    return packet
