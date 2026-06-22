# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py
# desc: PS-Q16L guarded once-run execution plan packet. It converts a PS-Q16K checkpoint into an ordered future execution plan only; it never creates locks, invokes refresh runners, writes status/runtime artifacts, registers schedulers, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_once_run_execution_design_checkpoint import (
    ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
)
from .prediction_warroom_non_ui_scheduled_producer_contract import (
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
)

GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION = "prediction_warroom_guarded_once_run_execution_plan_packet.ps_q16l.v1"
LOCK_RELATIVE_PATH = "prediction/status/non_ui_scheduled_producer.lock"

PLAN_STEPS: Tuple[str, ...] = (
    "future_step_01_require_clean_tree",
    "future_step_02_require_fresh_ps_q16j_dry_run_success",
    "future_step_03_require_human_execution_plan_record",
    "future_step_04_check_lock_absent_before_start",
    "future_step_05_create_single_run_lock_in_future_slice_only",
    "future_step_06_invoke_bounded_manual_refresh_runner_in_future_slice_only",
    "future_step_07_write_status_artifact_via_bounded_runner_in_future_slice_only",
    "future_step_08_report_decision_stdout_only",
    "future_step_09_release_or_delete_lock_in_finally_future_slice_only",
    "future_step_10_do_not_register_scheduler_or_enable_loop",
    "future_step_11_do_not_trigger_warroom_ui_autotrade_broker_ledger_or_parameters",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_execute_plan",
    "request_execute_manual_refresh",
    "request_latest_prediction_refresh",
    "request_status_artifact_write",
    "request_runtime_artifact_write",
    "request_lock_file_create",
    "request_lock_file_delete",
    "request_scheduler_enable",
    "request_os_scheduler_registration",
    "request_scheduled_loop_enable",
    "request_generate_enablement_command",
    "request_warroom_ui_trigger",
    "request_parameter_apply",
    "request_parameter_staging_write",
    "request_approval_or_ledger_or_autotrade_or_broker",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _requested_flags(**flags: bool) -> tuple[str, ...]:
    return tuple(name for name, requested in flags.items() if requested)


@dataclass(frozen=True)
class PredictionWarRoomGuardedOnceRunExecutionPlanPacket:
    plan_version: str
    plan_id: str
    plan_state: str
    plan_steps: Tuple[str, ...] = PLAN_STEPS
    checkpoint_packet_supplied: bool = False
    checkpoint_version: str = ""
    checkpoint_ready: bool = False
    human_execution_plan_record_present: bool = False
    human_execution_plan_source: str = ""
    lock_relative_path: str = LOCK_RELATIVE_PATH
    status_artifact_relative_path: str = PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    recommended_cadence_sec: int = RECOMMENDED_CADENCE_SEC
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_future_guarded_once_run_execution_implementation_slice: bool = False
    ready_for_execution_enablement: bool = False
    execution_enabled: bool = False
    plan_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    manual_refresh_invoked_by_this_plan: bool = False
    latest_prediction_refresh_performed_by_this_plan: bool = False
    status_artifact_write_performed_by_this_plan: bool = False
    runtime_artifact_write_performed_by_this_plan: bool = False
    lock_file_created_by_this_plan: bool = False
    lock_file_deleted_by_this_plan: bool = False
    wrapper_enabled: bool = False
    scheduler_enabled: bool = False
    os_scheduler_registration_performed: bool = False
    scheduled_loop_enabled: bool = False
    enablement_command_generated: bool = False
    warroom_ui_trigger_enabled: bool = False
    ui_triggered_runner_execution: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    parameter_apply_allowed: bool = False
    parameter_staging_write_allowed: bool = False
    would_send_to_broker: bool = False
    would_write_collector_state: bool = False
    freshness_bypass_added: bool = False
    force_ready_added: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_version": self.plan_version,
            "plan_id": self.plan_id,
            "plan_state": self.plan_state,
            "plan_steps": list(self.plan_steps),
            "checkpoint_packet_supplied": self.checkpoint_packet_supplied,
            "checkpoint_version": self.checkpoint_version,
            "checkpoint_ready": self.checkpoint_ready,
            "human_execution_plan_record_present": self.human_execution_plan_record_present,
            "human_execution_plan_source": self.human_execution_plan_source,
            "lock_relative_path": self.lock_relative_path,
            "status_artifact_relative_path": self.status_artifact_relative_path,
            "recommended_cadence_sec": self.recommended_cadence_sec,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_future_guarded_once_run_execution_implementation_slice": self.ready_for_future_guarded_once_run_execution_implementation_slice,
            "ready_for_execution_enablement": self.ready_for_execution_enablement,
            "execution_enabled": self.execution_enabled,
            "plan_only": self.plan_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "manual_refresh_invoked_by_this_plan": self.manual_refresh_invoked_by_this_plan,
            "latest_prediction_refresh_performed_by_this_plan": self.latest_prediction_refresh_performed_by_this_plan,
            "status_artifact_write_performed_by_this_plan": self.status_artifact_write_performed_by_this_plan,
            "runtime_artifact_write_performed_by_this_plan": self.runtime_artifact_write_performed_by_this_plan,
            "lock_file_created_by_this_plan": self.lock_file_created_by_this_plan,
            "lock_file_deleted_by_this_plan": self.lock_file_deleted_by_this_plan,
            "wrapper_enabled": self.wrapper_enabled,
            "scheduler_enabled": self.scheduler_enabled,
            "os_scheduler_registration_performed": self.os_scheduler_registration_performed,
            "scheduled_loop_enabled": self.scheduled_loop_enabled,
            "enablement_command_generated": self.enablement_command_generated,
            "warroom_ui_trigger_enabled": self.warroom_ui_trigger_enabled,
            "ui_triggered_runner_execution": self.ui_triggered_runner_execution,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "parameter_apply_allowed": self.parameter_apply_allowed,
            "parameter_staging_write_allowed": self.parameter_staging_write_allowed,
            "would_send_to_broker": self.would_send_to_broker,
            "would_write_collector_state": self.would_write_collector_state,
            "freshness_bypass_added": self.freshness_bypass_added,
            "force_ready_added": self.force_ready_added,
        }


def build_prediction_warroom_guarded_once_run_execution_plan_packet(
    *,
    ps_q16k_checkpoint_packet: Mapping[str, Any] | Any | None = None,
    human_execution_plan_record_present: bool = False,
    human_execution_plan_source: str = "",
    request_execute_plan: bool = False,
    request_execute_manual_refresh: bool = False,
    request_latest_prediction_refresh: bool = False,
    request_status_artifact_write: bool = False,
    request_runtime_artifact_write: bool = False,
    request_lock_file_create: bool = False,
    request_lock_file_delete: bool = False,
    request_scheduler_enable: bool = False,
    request_os_scheduler_registration: bool = False,
    request_scheduled_loop_enable: bool = False,
    request_generate_enablement_command: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_parameter_staging_write: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomGuardedOnceRunExecutionPlanPacket:
    """Return an ordered guarded once-run execution plan packet without executing anything."""
    checkpoint = _as_mapping(ps_q16k_checkpoint_packet)
    requested = _requested_flags(
        request_execute_plan=request_execute_plan,
        request_execute_manual_refresh=request_execute_manual_refresh,
        request_latest_prediction_refresh=request_latest_prediction_refresh,
        request_status_artifact_write=request_status_artifact_write,
        request_runtime_artifact_write=request_runtime_artifact_write,
        request_lock_file_create=request_lock_file_create,
        request_lock_file_delete=request_lock_file_delete,
        request_scheduler_enable=request_scheduler_enable,
        request_os_scheduler_registration=request_os_scheduler_registration,
        request_scheduled_loop_enable=request_scheduled_loop_enable,
        request_generate_enablement_command=request_generate_enablement_command,
        request_warroom_ui_trigger=request_warroom_ui_trigger,
        request_parameter_apply=request_parameter_apply,
        request_parameter_staging_write=request_parameter_staging_write,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    )
    blockers: list[str] = ["forbidden_request_in_ps_q16l:" + item for item in requested]
    warnings: list[str] = []
    if not checkpoint:
        blockers.append("ps_q16k_checkpoint_packet_required")
    else:
        if checkpoint.get("checkpoint_version") != ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION:
            blockers.append("ps_q16k_checkpoint_version_mismatch")
        if checkpoint.get("ready_for_future_guarded_once_run_execution_design_slice") is not True:
            blockers.append("ps_q16k_checkpoint_not_ready_for_guarded_execution_plan")
        if checkpoint.get("checkpoint_only") is not True or checkpoint.get("read_only") is not True or checkpoint.get("non_executing") is not True:
            blockers.append("ps_q16k_checkpoint_safety_flags_missing")
        for key in (
            "ready_for_execution_enablement",
            "execution_enabled",
            "manual_refresh_invoked_by_this_checkpoint",
            "latest_prediction_refresh_performed_by_this_checkpoint",
            "status_artifact_write_performed_by_this_checkpoint",
            "runtime_artifact_write_performed_by_this_checkpoint",
            "lock_file_created_by_this_checkpoint",
            "lock_file_deleted_by_this_checkpoint",
            "scheduler_enabled",
            "os_scheduler_registration_performed",
            "scheduled_loop_enabled",
            "warroom_ui_trigger_enabled",
            "autotrade_trigger_allowed",
            "broker_private_api_allowed",
            "parameter_apply_allowed",
            "parameter_staging_write_allowed",
            "freshness_bypass_added",
            "force_ready_added",
        ):
            if checkpoint.get(key) is not False:
                blockers.append("ps_q16k_" + key + "_must_remain_false")
    if not human_execution_plan_record_present:
        blockers.append("human_execution_plan_record_required_for_ps_q16l")
    if human_execution_plan_record_present and not str(human_execution_plan_source or "").strip():
        warnings.append("human_execution_plan_source_not_supplied")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(not unique_blockers)
    state = "guarded_once_run_execution_plan_ready_for_future_implementation_slice" if ready else "guarded_once_run_execution_plan_blocked"
    return PredictionWarRoomGuardedOnceRunExecutionPlanPacket(
        plan_version=GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION,
        plan_id=f"{GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION}:{state}",
        plan_state=state,
        checkpoint_packet_supplied=bool(checkpoint),
        checkpoint_version=str(checkpoint.get("checkpoint_version") or ""),
        checkpoint_ready=bool(checkpoint.get("ready_for_future_guarded_once_run_execution_design_slice") is True),
        human_execution_plan_record_present=bool(human_execution_plan_record_present),
        human_execution_plan_source=str(human_execution_plan_source or ""),
        requested_forbidden_flags=requested,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        ready_for_future_guarded_once_run_execution_implementation_slice=ready,
    )
