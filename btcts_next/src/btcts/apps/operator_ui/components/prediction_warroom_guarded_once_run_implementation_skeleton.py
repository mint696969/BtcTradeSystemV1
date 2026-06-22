# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_implementation_skeleton.py
# desc: PS-Q16M disabled guarded once-run implementation skeleton. It validates a PS-Q16L plan packet and declares disabled-by-default future implementation boundaries only; it never creates locks, invokes refresh runners, writes status/runtime artifacts, registers schedulers, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_guarded_once_run_execution_plan_packet import (
    GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION,
    LOCK_RELATIVE_PATH,
)
from .prediction_warroom_non_ui_scheduled_producer_contract import (
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
)

GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION = "prediction_warroom_guarded_once_run_implementation_skeleton.ps_q16m.v1"

IMPLEMENTATION_SKELETON_SEQUENCE: Tuple[str, ...] = (
    "consume_ps_q16l_plan_packet_only",
    "require_ps_q16l_plan_ready",
    "require_explicit_human_implementation_skeleton_record",
    "declare_disabled_operator_shell_entrypoint_contract_only",
    "declare_single_run_lock_lifecycle_contract_without_io",
    "declare_bounded_manual_refresh_adapter_boundary_without_invocation",
    "declare_status_write_boundary_without_write",
    "declare_stdout_report_boundary_without_execution",
    "declare_no_scheduler_no_loop_no_warroom_ui_trigger",
    "return_disabled_implementation_skeleton_packet_only",
)

FUTURE_ENTRYPOINT_CONTRACT: Tuple[str, ...] = (
    "future_entrypoint_name=check_phase4a_prediction_system_ps_q16m_guarded_once_run_disabled.py",
    "future_entrypoint_default=disabled",
    "future_entrypoint_operator_shell_only=true",
    "future_entrypoint_requires_clean_tree=true",
    "future_entrypoint_requires_fresh_ps_q16j_dry_run=true",
    "future_entrypoint_requires_ps_q16l_plan_ready=true",
    "future_entrypoint_requires_no_existing_lock=true",
    "future_entrypoint_requires_explicit_execution_approval=false_in_ps_q16m",
    "future_entrypoint_must_not_register_scheduler=true",
    "future_entrypoint_must_not_be_invoked_from_warroom_ui=true",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_enable_implementation",
    "request_execute_once_run",
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
class PredictionWarRoomGuardedOnceRunImplementationSkeletonPacket:
    skeleton_version: str
    skeleton_id: str
    skeleton_state: str
    skeleton_sequence: Tuple[str, ...] = IMPLEMENTATION_SKELETON_SEQUENCE
    future_entrypoint_contract: Tuple[str, ...] = FUTURE_ENTRYPOINT_CONTRACT
    plan_packet_supplied: bool = False
    plan_version: str = ""
    plan_ready: bool = False
    human_implementation_skeleton_record_present: bool = False
    human_implementation_skeleton_source: str = ""
    lock_relative_path: str = LOCK_RELATIVE_PATH
    status_artifact_relative_path: str = PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    recommended_cadence_sec: int = RECOMMENDED_CADENCE_SEC
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_future_disabled_once_run_operator_shell_cli_slice: bool = False
    ready_for_execution_enablement: bool = False
    implementation_enabled: bool = False
    execution_enabled: bool = False
    skeleton_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    manual_refresh_invoked_by_this_skeleton: bool = False
    latest_prediction_refresh_performed_by_this_skeleton: bool = False
    status_artifact_write_performed_by_this_skeleton: bool = False
    runtime_artifact_write_performed_by_this_skeleton: bool = False
    lock_file_created_by_this_skeleton: bool = False
    lock_file_deleted_by_this_skeleton: bool = False
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
            "skeleton_version": self.skeleton_version,
            "skeleton_id": self.skeleton_id,
            "skeleton_state": self.skeleton_state,
            "skeleton_sequence": list(self.skeleton_sequence),
            "future_entrypoint_contract": list(self.future_entrypoint_contract),
            "plan_packet_supplied": self.plan_packet_supplied,
            "plan_version": self.plan_version,
            "plan_ready": self.plan_ready,
            "human_implementation_skeleton_record_present": self.human_implementation_skeleton_record_present,
            "human_implementation_skeleton_source": self.human_implementation_skeleton_source,
            "lock_relative_path": self.lock_relative_path,
            "status_artifact_relative_path": self.status_artifact_relative_path,
            "recommended_cadence_sec": self.recommended_cadence_sec,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_future_disabled_once_run_operator_shell_cli_slice": self.ready_for_future_disabled_once_run_operator_shell_cli_slice,
            "ready_for_execution_enablement": self.ready_for_execution_enablement,
            "implementation_enabled": self.implementation_enabled,
            "execution_enabled": self.execution_enabled,
            "skeleton_only": self.skeleton_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "manual_refresh_invoked_by_this_skeleton": self.manual_refresh_invoked_by_this_skeleton,
            "latest_prediction_refresh_performed_by_this_skeleton": self.latest_prediction_refresh_performed_by_this_skeleton,
            "status_artifact_write_performed_by_this_skeleton": self.status_artifact_write_performed_by_this_skeleton,
            "runtime_artifact_write_performed_by_this_skeleton": self.runtime_artifact_write_performed_by_this_skeleton,
            "lock_file_created_by_this_skeleton": self.lock_file_created_by_this_skeleton,
            "lock_file_deleted_by_this_skeleton": self.lock_file_deleted_by_this_skeleton,
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


def build_prediction_warroom_guarded_once_run_implementation_skeleton(
    *,
    ps_q16l_plan_packet: Mapping[str, Any] | Any | None = None,
    human_implementation_skeleton_record_present: bool = False,
    human_implementation_skeleton_source: str = "",
    request_enable_implementation: bool = False,
    request_execute_once_run: bool = False,
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
) -> PredictionWarRoomGuardedOnceRunImplementationSkeletonPacket:
    """Return a disabled implementation skeleton packet without executing or writing anything."""
    plan = _as_mapping(ps_q16l_plan_packet)
    requested = _requested_flags(
        request_enable_implementation=request_enable_implementation,
        request_execute_once_run=request_execute_once_run,
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
    blockers: list[str] = ["forbidden_request_in_ps_q16m:" + item for item in requested]
    warnings: list[str] = []
    if not plan:
        blockers.append("ps_q16l_plan_packet_required")
    else:
        if plan.get("plan_version") != GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION:
            blockers.append("ps_q16l_plan_version_mismatch")
        if plan.get("ready_for_future_guarded_once_run_execution_implementation_slice") is not True:
            blockers.append("ps_q16l_plan_not_ready_for_disabled_implementation_skeleton")
        if plan.get("plan_only") is not True or plan.get("read_only") is not True or plan.get("non_executing") is not True:
            blockers.append("ps_q16l_plan_safety_flags_missing")
        if plan.get("lock_relative_path") != LOCK_RELATIVE_PATH:
            blockers.append("ps_q16l_lock_relative_path_mismatch")
        for key in (
            "ready_for_execution_enablement",
            "execution_enabled",
            "manual_refresh_invoked_by_this_plan",
            "latest_prediction_refresh_performed_by_this_plan",
            "status_artifact_write_performed_by_this_plan",
            "runtime_artifact_write_performed_by_this_plan",
            "lock_file_created_by_this_plan",
            "lock_file_deleted_by_this_plan",
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
            if plan.get(key) is not False:
                blockers.append("ps_q16l_" + key + "_must_remain_false")
    if not human_implementation_skeleton_record_present:
        blockers.append("human_implementation_skeleton_record_required_for_ps_q16m")
    if human_implementation_skeleton_record_present and not str(human_implementation_skeleton_source or "").strip():
        warnings.append("human_implementation_skeleton_source_not_supplied")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(not unique_blockers)
    state = "guarded_once_run_implementation_skeleton_ready_for_future_disabled_cli_slice" if ready else "guarded_once_run_implementation_skeleton_blocked"
    return PredictionWarRoomGuardedOnceRunImplementationSkeletonPacket(
        skeleton_version=GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION,
        skeleton_id=f"{GUARDED_ONCE_RUN_IMPLEMENTATION_SKELETON_VERSION}:{state}",
        skeleton_state=state,
        plan_packet_supplied=bool(plan),
        plan_version=str(plan.get("plan_version") or ""),
        plan_ready=bool(plan.get("ready_for_future_guarded_once_run_execution_implementation_slice") is True),
        human_implementation_skeleton_record_present=bool(human_implementation_skeleton_record_present),
        human_implementation_skeleton_source=str(human_implementation_skeleton_source or ""),
        requested_forbidden_flags=requested,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        ready_for_future_disabled_once_run_operator_shell_cli_slice=ready,
    )
