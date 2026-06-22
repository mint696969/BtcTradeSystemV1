# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_bounded_manual_refresh_runner.py
# desc: PS-Q16D bounded manual refresh runner. Under explicit operator flags only, it invokes PS-Q10H actual export runner to refresh latest_prediction_system_result.json, then writes producer status visibility. No scheduler, WarRoom UI trigger, parameter mutation, ledger, AutoTrade, broker/private API, or mode/order behavior.

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_latest_payload_actual_export_runner import (
    build_prediction_warroom_latest_payload_actual_export_runner,
)
from .prediction_warroom_non_ui_scheduled_producer_contract import (
    FRESHNESS_MAX_AGE_SEC,
    LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
    REQUIRED_STATUS_FIELDS,
)

PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION = (
    "prediction_warroom_bounded_manual_refresh_runner.ps_q16d.v1"
)

BOUNDED_MANUAL_REFRESH_SEQUENCE: Tuple[str, ...] = (
    "require_operator_acknowledgement",
    "require_execute_manual_refresh_true",
    "require_actual_read_prediction_build_export_preflight_latest_export_runtime_write_flags",
    "require_status_artifact_write_flags",
    "invoke_ps_q10h_actual_export_runner_once",
    "write_producer_status_artifact_after_attempt",
    "return_stdout_safe_packet",
    "do_not_register_scheduler",
    "do_not_run_from_warroom_ui",
    "do_not_apply_or_stage_parameters",
    "do_not_append_approval_decision_or_command_ledgers",
    "do_not_trigger_autotrade_or_broker",
)

ActualExportRunner = Callable[..., Any]


@dataclass(frozen=True)
class PredictionWarRoomBoundedManualRefreshRunnerPacket:
    runner_version: str
    runner_id: str
    runner_state: str
    hot_latest_root_hint: str
    runner_sequence: Tuple[str, ...] = BOUNDED_MANUAL_REFRESH_SEQUENCE
    export_runner_packet: Mapping[str, Any] = field(default_factory=dict)
    status_payload: Mapping[str, Any] = field(default_factory=dict)
    status_artifact_path: str = ""
    status_artifact_written: bool = False
    status_artifact_size_bytes: int | None = None
    status_written_at: str = ""
    operator_acknowledged: bool = False
    execute_manual_refresh_requested: bool = False
    allow_actual_read_requested: bool = False
    allow_prediction_build_requested: bool = False
    allow_export_preflight_requested: bool = False
    allow_latest_payload_export_requested: bool = False
    allow_runtime_artifact_write_requested: bool = False
    allow_status_artifact_write_requested: bool = False
    execute_status_artifact_write_requested: bool = False
    allow_guard_test_root: bool = False
    target_root_valid: bool = False
    actual_export_runner_invoked: bool = False
    latest_prediction_artifact_written: bool = False
    latest_prediction_artifact_path: str = ""
    latest_prediction_artifact_size_bytes: int | None = None
    prediction_run_id: str = ""
    generated_at: str = ""
    exported_at: str = ""
    ready_for_warroom_status_observation: bool = False
    ready_for_scheduler_enablement: bool = False
    ready_for_automation_enablement: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    non_ui_runner_only: bool = True
    bounded_manual_run_only: bool = True
    producer_enabled: bool = False
    scheduler_enabled: bool = False
    scheduled_loop_enabled: bool = False
    warroom_ui_trigger_enabled: bool = False
    ui_triggered_runner_execution: bool = False
    runtime_artifact_write_enabled: bool = False
    latest_prediction_artifact_write_enabled: bool = False
    status_artifact_write_enabled: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    parameter_apply_allowed: bool = False
    parameter_staging_write_allowed: bool = False
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
            "runner_version": self.runner_version,
            "runner_id": self.runner_id,
            "runner_state": self.runner_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "runner_sequence": list(self.runner_sequence),
            "export_runner_packet": dict(self.export_runner_packet),
            "status_payload": dict(self.status_payload),
            "status_artifact_path": self.status_artifact_path,
            "status_artifact_written": self.status_artifact_written,
            "status_artifact_size_bytes": self.status_artifact_size_bytes,
            "status_written_at": self.status_written_at,
            "operator_acknowledged": self.operator_acknowledged,
            "execute_manual_refresh_requested": self.execute_manual_refresh_requested,
            "allow_actual_read_requested": self.allow_actual_read_requested,
            "allow_prediction_build_requested": self.allow_prediction_build_requested,
            "allow_export_preflight_requested": self.allow_export_preflight_requested,
            "allow_latest_payload_export_requested": self.allow_latest_payload_export_requested,
            "allow_runtime_artifact_write_requested": self.allow_runtime_artifact_write_requested,
            "allow_status_artifact_write_requested": self.allow_status_artifact_write_requested,
            "execute_status_artifact_write_requested": self.execute_status_artifact_write_requested,
            "allow_guard_test_root": self.allow_guard_test_root,
            "target_root_valid": self.target_root_valid,
            "actual_export_runner_invoked": self.actual_export_runner_invoked,
            "latest_prediction_artifact_written": self.latest_prediction_artifact_written,
            "latest_prediction_artifact_path": self.latest_prediction_artifact_path,
            "latest_prediction_artifact_size_bytes": self.latest_prediction_artifact_size_bytes,
            "prediction_run_id": self.prediction_run_id,
            "generated_at": self.generated_at,
            "exported_at": self.exported_at,
            "ready_for_warroom_status_observation": self.ready_for_warroom_status_observation,
            "ready_for_scheduler_enablement": self.ready_for_scheduler_enablement,
            "ready_for_automation_enablement": self.ready_for_automation_enablement,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "non_ui_runner_only": self.non_ui_runner_only,
            "bounded_manual_run_only": self.bounded_manual_run_only,
            "producer_enabled": self.producer_enabled,
            "scheduler_enabled": self.scheduler_enabled,
            "scheduled_loop_enabled": self.scheduled_loop_enabled,
            "warroom_ui_trigger_enabled": self.warroom_ui_trigger_enabled,
            "ui_triggered_runner_execution": self.ui_triggered_runner_execution,
            "runtime_artifact_write_enabled": self.runtime_artifact_write_enabled,
            "latest_prediction_artifact_write_enabled": self.latest_prediction_artifact_write_enabled,
            "status_artifact_write_enabled": self.status_artifact_write_enabled,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "parameter_apply_allowed": self.parameter_apply_allowed,
            "parameter_staging_write_allowed": self.parameter_staging_write_allowed,
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


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _hot_root_ok(root: str, *, allow_guard_test_root: bool = False) -> bool:
    normalized = str(root).rstrip("\\/").lower().replace("/", "\\")
    if normalized == "d:\\btc_ts_hot":
        return True
    return bool(allow_guard_test_root and normalized)


def _status_path(root: str) -> Path:
    return Path(str(root).rstrip("\\/")) / "prediction" / "status" / "non_ui_scheduled_producer_status.json"


def _safe_flags(*, target_file_written: bool, status_written: bool) -> Dict[str, bool]:
    return {
        "non_ui_runner_only_true": True,
        "bounded_manual_run_only_true": True,
        "operator_ack_required_true": True,
        "scheduler_enabled_false": True,
        "scheduled_loop_enabled_false": True,
        "warroom_ui_trigger_false": True,
        "producer_enabled_false": True,
        "latest_prediction_artifact_write_manual_only": bool(target_file_written),
        "status_artifact_write_manual_only": bool(status_written),
        "approval_or_authorization_allowed_false": True,
        "ledger_append_allowed_false": True,
        "autotrade_trigger_allowed_false": True,
        "broker_private_api_allowed_false": True,
        "parameter_apply_allowed_false": True,
        "parameter_staging_write_allowed_false": True,
        "would_send_to_broker_false": True,
        "would_write_collector_state_false": True,
    }


def _status_payload(
    *,
    state: str,
    now: str,
    export_packet: Mapping[str, Any],
    target_file_written: bool,
    status_written: bool,
    blockers: tuple[str, ...],
    warnings: tuple[str, ...],
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "producer_version": PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
        "producer_state": state,
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": bool(target_file_written),
        "latest_prediction_artifact_relative_path": LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
        "status_artifact_relative_path": PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
        "freshness_max_age_sec": FRESHNESS_MAX_AGE_SEC,
        "recommended_cadence_sec": RECOMMENDED_CADENCE_SEC,
        "last_run_started_at": now,
        "last_run_finished_at": now,
        "last_success_at": now if target_file_written and not blockers else None,
        "last_failure_at": None if target_file_written and not blockers else now,
        "last_success_generated_at": str(export_packet.get("generated_at") or "") if target_file_written else None,
        "last_prediction_run_id": str(export_packet.get("prediction_run_id") or "") if target_file_written else None,
        "last_target_file_size_bytes": export_packet.get("target_file_size_bytes") if isinstance(export_packet.get("target_file_size_bytes"), int) else None,
        "last_warning_count": len(warnings),
        "last_blocker_count": len(blockers),
        "consecutive_failure_count": 0 if target_file_written and not blockers else 1,
        "safe_flags": _safe_flags(target_file_written=target_file_written, status_written=status_written),
        "warnings": list(warnings),
        "blockers": list(blockers),
        "disable_rollback_state": "manual_refresh_only_disable_by_not_running; scheduler_not_registered",
    }
    missing = [field for field in REQUIRED_STATUS_FIELDS if field not in payload]
    if missing:
        payload["blockers"] = list(dict.fromkeys(list(payload["blockers"]) + ["status_payload_missing_required_fields:" + ",".join(missing)]))
        payload["last_blocker_count"] = len(payload["blockers"])
        payload["consecutive_failure_count"] = 1
    return payload


def _write_json_atomic(target: Path, payload: Mapping[str, Any]) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    body = json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n"
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(target)
    return int(target.stat().st_size)


def build_prediction_warroom_bounded_manual_refresh_runner(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    operator_acknowledged: bool = False,
    execute_manual_refresh: bool = False,
    allow_actual_read: bool = False,
    allow_prediction_build: bool = False,
    allow_export_preflight: bool = False,
    allow_latest_payload_export: bool = False,
    allow_runtime_artifact_write: bool = False,
    allow_status_artifact_write: bool = False,
    execute_status_artifact_write: bool = False,
    allow_guard_test_root: bool = False,
    actual_export_runner: ActualExportRunner | None = None,
    request_scheduler_enable: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_parameter_staging_write: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomBoundedManualRefreshRunnerPacket:
    """Run one bounded manual latest-prediction refresh only when all explicit flags are true."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not execute_manual_refresh:
        blockers.append("execute_manual_refresh_false")
    if not allow_actual_read:
        blockers.append("allow_actual_read_false")
    if not allow_prediction_build:
        blockers.append("allow_prediction_build_false")
    if not allow_export_preflight:
        blockers.append("allow_export_preflight_false")
    if not allow_latest_payload_export:
        blockers.append("allow_latest_payload_export_false")
    if not allow_runtime_artifact_write:
        blockers.append("allow_runtime_artifact_write_false")
    if not allow_status_artifact_write:
        blockers.append("allow_status_artifact_write_false")
    if not execute_status_artifact_write:
        blockers.append("execute_status_artifact_write_false")
    if request_scheduler_enable:
        blockers.append("scheduler_enable_not_allowed_in_ps_q16d")
    if request_warroom_ui_trigger:
        blockers.append("warroom_ui_trigger_not_allowed_in_ps_q16d")
    if request_parameter_apply:
        blockers.append("parameter_apply_not_allowed_in_ps_q16d")
    if request_parameter_staging_write:
        blockers.append("parameter_staging_write_not_allowed_in_ps_q16d")
    if request_approval_or_ledger_or_autotrade_or_broker:
        blockers.append("approval_ledger_autotrade_broker_not_allowed_in_ps_q16d")
    target_root_valid = _hot_root_ok(str(hot_latest_root_hint), allow_guard_test_root=allow_guard_test_root)
    if not target_root_valid:
        blockers.append("target_root_invalid_for_bounded_manual_refresh_runner")

    pre_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    export_packet: Mapping[str, Any] = {}
    actual_invoked = False
    target_file_written = False
    if not pre_blockers:
        runner = actual_export_runner or build_prediction_warroom_latest_payload_actual_export_runner
        actual_invoked = True
        export_packet = _as_mapping(
            runner(
                hot_latest_root_hint=str(hot_latest_root_hint),
                operator_acknowledged=True,
                allow_actual_read=True,
                allow_prediction_build=True,
                allow_export_preflight=True,
                allow_latest_payload_export=True,
                allow_runtime_artifact_write=True,
                allow_guard_test_root=allow_guard_test_root,
                requested_warroom_ui_trigger=False,
                requested_approval_or_ledger_or_autotrade_or_broker=False,
            )
        )
        blockers.extend(str(item) for item in export_packet.get("blocked_reasons", []))
        warnings.extend(str(item) for item in export_packet.get("warning_reasons", []))
        target_file_written = bool(export_packet.get("target_file_written")) and not export_packet.get("blocked_reasons")
        if not target_file_written:
            blockers.append("actual_export_runner_did_not_write_latest_prediction_artifact")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    now = _iso_now()
    status_path = _status_path(str(hot_latest_root_hint))
    status_state = "manual_refresh_exported" if target_file_written and not unique_blockers else "manual_refresh_blocked"
    status_payload = _status_payload(
        state=status_state,
        now=now,
        export_packet=export_packet,
        target_file_written=target_file_written,
        status_written=False,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )
    status_written = False
    status_size: int | None = None
    status_written_at = ""
    write_blockers = unique_blockers
    write_warnings = unique_warnings
    if operator_acknowledged and execute_status_artifact_write and allow_status_artifact_write and target_root_valid and execute_manual_refresh:
        try:
            status_size = _write_json_atomic(status_path, status_payload)
            status_written = True
            status_written_at = _iso_now()
            status_payload = _status_payload(
                state=status_state + "_status_written",
                now=now,
                export_packet=export_packet,
                target_file_written=target_file_written,
                status_written=True,
                blockers=unique_blockers,
                warnings=unique_warnings,
            )
            status_size = _write_json_atomic(status_path, status_payload)
        except Exception as exc:  # noqa: BLE001 - fail closed and report diagnostic
            write_blockers = tuple(dict.fromkeys(write_blockers + ("manual_refresh_status_write_failed:" + exc.__class__.__name__,)))
            write_warnings = tuple(dict.fromkeys(write_warnings + (str(exc),)))
            status_payload = _status_payload(
                state="manual_refresh_status_write_failed",
                now=now,
                export_packet=export_packet,
                target_file_written=target_file_written,
                status_written=False,
                blockers=write_blockers,
                warnings=write_warnings,
            )
    final_state = (
        "bounded_manual_refresh_exported_status_written"
        if target_file_written and status_written and not write_blockers
        else "bounded_manual_refresh_blocked_status_written"
        if status_written
        else "bounded_manual_refresh_blocked"
    )
    return PredictionWarRoomBoundedManualRefreshRunnerPacket(
        runner_version=PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION,
        runner_id=f"{PREDICTION_WARROOM_BOUNDED_MANUAL_REFRESH_RUNNER_VERSION}:{final_state}",
        runner_state=final_state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        export_runner_packet=export_packet,
        status_payload=status_payload,
        status_artifact_path=str(status_path),
        status_artifact_written=status_written,
        status_artifact_size_bytes=status_size,
        status_written_at=status_written_at,
        operator_acknowledged=operator_acknowledged,
        execute_manual_refresh_requested=execute_manual_refresh,
        allow_actual_read_requested=allow_actual_read,
        allow_prediction_build_requested=allow_prediction_build,
        allow_export_preflight_requested=allow_export_preflight,
        allow_latest_payload_export_requested=allow_latest_payload_export,
        allow_runtime_artifact_write_requested=allow_runtime_artifact_write,
        allow_status_artifact_write_requested=allow_status_artifact_write,
        execute_status_artifact_write_requested=execute_status_artifact_write,
        allow_guard_test_root=allow_guard_test_root,
        target_root_valid=target_root_valid,
        actual_export_runner_invoked=actual_invoked,
        latest_prediction_artifact_written=target_file_written,
        latest_prediction_artifact_path=str(export_packet.get("target_artifact_path") or ""),
        latest_prediction_artifact_size_bytes=export_packet.get("target_file_size_bytes") if isinstance(export_packet.get("target_file_size_bytes"), int) else None,
        prediction_run_id=str(export_packet.get("prediction_run_id") or ""),
        generated_at=str(export_packet.get("generated_at") or ""),
        exported_at=str(export_packet.get("exported_at") or ""),
        ready_for_warroom_status_observation=bool(status_written or status_payload),
        ready_for_scheduler_enablement=False,
        ready_for_automation_enablement=False,
        blocker_count=len(write_blockers),
        warning_count=len(write_warnings),
        blocked_reasons=write_blockers,
        warning_reasons=write_warnings,
        runtime_artifact_write_enabled=target_file_written,
        latest_prediction_artifact_write_enabled=target_file_written,
        status_artifact_write_enabled=status_written,
    )
