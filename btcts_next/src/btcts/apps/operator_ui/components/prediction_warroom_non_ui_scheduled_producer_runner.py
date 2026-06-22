# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_runner.py
# desc: PS-Q16B disabled-by-default non-UI Prediction producer runner scaffold. It can write only the producer status artifact when explicitly acknowledged; it does not schedule, export latest predictions, trigger WarRoom UI, mutate parameters, append ledgers, call broker/private APIs, or enable AutoTrade.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_non_ui_scheduled_producer_contract import (
    FRESHNESS_MAX_AGE_SEC,
    LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
    REQUIRED_STATUS_FIELDS,
    SAFE_FLAG_KEYS,
    build_prediction_warroom_non_ui_scheduled_producer_contract,
)

PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION = (
    "prediction_warroom_non_ui_scheduled_producer_runner.ps_q16b.v1"
)

PRODUCER_RUNNER_SEQUENCE: Tuple[str, ...] = (
    "load_ps_q16a_contract",
    "remain_disabled_by_default",
    "declare_no_scheduler_enablement",
    "declare_no_latest_prediction_artifact_write_in_ps_q16b",
    "build_status_artifact_payload",
    "write_status_artifact_only_when_operator_ack_and_execute_status_write_true",
    "return_runner_packet",
    "do_not_call_latest_payload_actual_export_runner",
    "do_not_trigger_from_warroom_ui",
    "do_not_apply_or_stage_parameters",
    "do_not_append_approval_decision_or_command_ledgers",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomNonUiScheduledProducerRunnerPacket:
    runner_version: str
    runner_id: str
    runner_state: str
    hot_latest_root_hint: str
    runner_sequence: Tuple[str, ...] = PRODUCER_RUNNER_SEQUENCE
    contract_packet: Mapping[str, Any] = field(default_factory=dict)
    status_payload: Mapping[str, Any] = field(default_factory=dict)
    status_artifact_path: str = ""
    status_artifact_written: bool = False
    status_artifact_size_bytes: int | None = None
    status_written_at: str = ""
    operator_acknowledged: bool = False
    status_artifact_write_requested: bool = False
    execute_status_artifact_write_requested: bool = False
    allow_guard_test_root: bool = False
    target_root_valid: bool = False
    ready_for_warroom_status_observation: bool = False
    ready_for_manual_bounded_refresh_slice: bool = False
    ready_for_scheduler_enablement: bool = False
    ready_for_latest_prediction_artifact_write_automation: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    producer_enabled: bool = False
    scheduler_enabled: bool = False
    runtime_artifact_write_enabled: bool = False
    latest_prediction_artifact_write_enabled: bool = False
    status_artifact_write_enabled: bool = False
    non_ui_runner_only: bool = True
    disabled_by_default: bool = True
    warroom_ui_trigger_enabled: bool = False
    ui_triggered_runner_execution: bool = False
    prediction_build_requested: bool = False
    actual_export_runner_invoked: bool = False
    latest_prediction_artifact_written: bool = False
    would_write_latest_prediction_artifact: bool = False
    would_write_status_artifact: bool = False
    would_write_collector_state: bool = False
    would_mutate_live_parameters: bool = False
    would_append_parameter_version: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    parameter_apply_allowed: bool = False
    parameter_staging_write_allowed: bool = False
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
            "contract_packet": dict(self.contract_packet),
            "status_payload": dict(self.status_payload),
            "status_artifact_path": self.status_artifact_path,
            "status_artifact_written": self.status_artifact_written,
            "status_artifact_size_bytes": self.status_artifact_size_bytes,
            "status_written_at": self.status_written_at,
            "operator_acknowledged": self.operator_acknowledged,
            "status_artifact_write_requested": self.status_artifact_write_requested,
            "execute_status_artifact_write_requested": self.execute_status_artifact_write_requested,
            "allow_guard_test_root": self.allow_guard_test_root,
            "target_root_valid": self.target_root_valid,
            "ready_for_warroom_status_observation": self.ready_for_warroom_status_observation,
            "ready_for_manual_bounded_refresh_slice": self.ready_for_manual_bounded_refresh_slice,
            "ready_for_scheduler_enablement": self.ready_for_scheduler_enablement,
            "ready_for_latest_prediction_artifact_write_automation": self.ready_for_latest_prediction_artifact_write_automation,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "producer_enabled": self.producer_enabled,
            "scheduler_enabled": self.scheduler_enabled,
            "runtime_artifact_write_enabled": self.runtime_artifact_write_enabled,
            "latest_prediction_artifact_write_enabled": self.latest_prediction_artifact_write_enabled,
            "status_artifact_write_enabled": self.status_artifact_write_enabled,
            "non_ui_runner_only": self.non_ui_runner_only,
            "disabled_by_default": self.disabled_by_default,
            "warroom_ui_trigger_enabled": self.warroom_ui_trigger_enabled,
            "ui_triggered_runner_execution": self.ui_triggered_runner_execution,
            "prediction_build_requested": self.prediction_build_requested,
            "actual_export_runner_invoked": self.actual_export_runner_invoked,
            "latest_prediction_artifact_written": self.latest_prediction_artifact_written,
            "would_write_latest_prediction_artifact": self.would_write_latest_prediction_artifact,
            "would_write_status_artifact": self.would_write_status_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_mutate_live_parameters": self.would_mutate_live_parameters,
            "would_append_parameter_version": self.would_append_parameter_version,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "parameter_apply_allowed": self.parameter_apply_allowed,
            "parameter_staging_write_allowed": self.parameter_staging_write_allowed,
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


def _hot_root_ok(root: str, *, allow_guard_test_root: bool = False) -> bool:
    normalized = str(root).rstrip("\\/").lower().replace("/", "\\")
    if normalized == "d:\\btc_ts_hot":
        return True
    return bool(allow_guard_test_root and normalized)


def _status_path(root: str) -> Path:
    return Path(str(root).rstrip("\\/")) / "prediction" / "status" / "non_ui_scheduled_producer_status.json"


def _safe_flags() -> Dict[str, bool]:
    return {key: True for key in SAFE_FLAG_KEYS}


def _status_payload(*, now: str, state: str, warnings: tuple[str, ...], blockers: tuple[str, ...]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "producer_version": PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION,
        "producer_state": state,
        "producer_enabled": False,
        "scheduler_enabled": False,
        "runtime_artifact_write_enabled": False,
        "latest_prediction_artifact_relative_path": LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
        "status_artifact_relative_path": PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
        "freshness_max_age_sec": FRESHNESS_MAX_AGE_SEC,
        "recommended_cadence_sec": RECOMMENDED_CADENCE_SEC,
        "last_run_started_at": now,
        "last_run_finished_at": now,
        "last_success_at": None,
        "last_failure_at": None if not blockers else now,
        "last_success_generated_at": None,
        "last_prediction_run_id": None,
        "last_target_file_size_bytes": None,
        "last_warning_count": len(warnings),
        "last_blocker_count": len(blockers),
        "consecutive_failure_count": 0 if not blockers else 1,
        "safe_flags": _safe_flags(),
        "warnings": list(warnings),
        "blockers": list(blockers),
        "disable_rollback_state": "disabled_by_default_no_scheduler_no_latest_prediction_write",
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


def build_prediction_warroom_non_ui_scheduled_producer_runner(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    operator_acknowledged: bool = False,
    allow_status_artifact_write: bool = False,
    execute_status_artifact_write: bool = False,
    allow_guard_test_root: bool = False,
    request_enable_producer: bool = False,
    request_scheduler_enable: bool = False,
    request_latest_prediction_artifact_write: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_parameter_staging_write: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomNonUiScheduledProducerRunnerPacket:
    """Return PS-Q16B disabled producer scaffold and optionally write its status artifact.

    This function is intentionally not a scheduler and does not refresh the latest prediction
    artifact. The only IO it can perform is writing the producer status artifact, and only
    when operator acknowledgement plus allow/execute status-write flags are all true.
    """
    blockers: list[str] = []
    warnings: list[str] = []
    if request_enable_producer:
        blockers.append("producer_enable_not_allowed_in_ps_q16b")
    if request_scheduler_enable:
        blockers.append("scheduler_enable_not_allowed_in_ps_q16b")
    if request_latest_prediction_artifact_write:
        blockers.append("latest_prediction_artifact_write_not_allowed_in_ps_q16b")
    if request_warroom_ui_trigger:
        blockers.append("warroom_ui_trigger_not_allowed_in_ps_q16b")
    if request_parameter_apply:
        blockers.append("parameter_apply_not_allowed_in_ps_q16b")
    if request_parameter_staging_write:
        blockers.append("parameter_staging_write_not_allowed_in_ps_q16b")
    if request_approval_or_ledger_or_autotrade_or_broker:
        blockers.append("approval_ledger_autotrade_broker_not_allowed_in_ps_q16b")
    target_root_valid = _hot_root_ok(str(hot_latest_root_hint), allow_guard_test_root=allow_guard_test_root)
    if not target_root_valid:
        blockers.append("target_root_invalid_for_non_ui_scheduled_producer_status")
    if execute_status_artifact_write and not allow_status_artifact_write:
        blockers.append("execute_status_artifact_write_without_allow_status_artifact_write")
    if execute_status_artifact_write and not operator_acknowledged:
        blockers.append("operator_acknowledgement_required_for_status_artifact_write")
    if not execute_status_artifact_write:
        warnings.append("status_artifact_write_not_executed")

    contract = build_prediction_warroom_non_ui_scheduled_producer_contract().to_dict()
    blockers.extend(str(item) for item in contract.get("blocked_reasons", []))
    warnings.extend(str(item) for item in contract.get("warning_reasons", []))
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    now = _iso_now()
    state = "producer_disabled_status_ready" if not unique_blockers else "producer_disabled_status_blocked"
    payload = _status_payload(now=now, state=state, warnings=unique_warnings, blockers=unique_blockers)
    status_path = _status_path(str(hot_latest_root_hint))
    written = False
    size: int | None = None
    written_at = ""
    write_blockers = unique_blockers
    write_warnings = unique_warnings
    if execute_status_artifact_write and allow_status_artifact_write and operator_acknowledged and not unique_blockers:
        try:
            size = _write_json_atomic(status_path, payload)
            written = True
            written_at = _iso_now()
        except Exception as exc:  # noqa: BLE001 - fail closed and return diagnostic
            write_blockers = tuple(dict.fromkeys(write_blockers + ("producer_status_artifact_write_failed:" + exc.__class__.__name__,)))
            write_warnings = tuple(dict.fromkeys(write_warnings + (str(exc),)))
            payload = _status_payload(now=now, state="producer_disabled_status_write_failed", warnings=write_warnings, blockers=write_blockers)
    final_state = "producer_disabled_status_written" if written else ("producer_disabled_status_ready" if not write_blockers else "producer_disabled_status_blocked")
    return PredictionWarRoomNonUiScheduledProducerRunnerPacket(
        runner_version=PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION,
        runner_id=f"{PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION}:{final_state}",
        runner_state=final_state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        contract_packet=contract,
        status_payload=payload,
        status_artifact_path=str(status_path),
        status_artifact_written=written,
        status_artifact_size_bytes=size,
        status_written_at=written_at,
        operator_acknowledged=operator_acknowledged,
        status_artifact_write_requested=allow_status_artifact_write,
        execute_status_artifact_write_requested=execute_status_artifact_write,
        allow_guard_test_root=allow_guard_test_root,
        target_root_valid=target_root_valid,
        ready_for_warroom_status_observation=bool(written or payload),
        ready_for_manual_bounded_refresh_slice=bool(not write_blockers),
        ready_for_scheduler_enablement=False,
        ready_for_latest_prediction_artifact_write_automation=False,
        blocker_count=len(write_blockers),
        warning_count=len(write_warnings),
        blocked_reasons=write_blockers,
        warning_reasons=write_warnings,
        status_artifact_write_enabled=bool(allow_status_artifact_write and execute_status_artifact_write and operator_acknowledged and not write_blockers),
        would_write_status_artifact=bool(allow_status_artifact_write and execute_status_artifact_write and operator_acknowledged),
    )
