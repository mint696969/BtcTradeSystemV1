# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py
# desc: PS-Q16H disabled-by-default non-UI scheduler wrapper skeleton. It declares wrapper boundaries, lock policy, and future operator-shell entrypoint shape only; it never registers OS schedulers, starts loops, refreshes artifacts, writes files, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_disabled_scheduler_design_packet import (
    DISABLED_SCHEDULER_DESIGN_PACKET_VERSION,
)
from .prediction_warroom_non_ui_scheduled_producer_contract import (
    FRESHNESS_MAX_AGE_SEC,
    MAXIMUM_CADENCE_SEC,
    MINIMUM_CADENCE_SEC,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
)

DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION = "prediction_warroom_disabled_scheduler_wrapper_skeleton.ps_q16h.v1"

WRAPPER_SKELETON_SEQUENCE: Tuple[str, ...] = (
    "consume_ps_q16g_disabled_scheduler_design_packet_only",
    "require_design_ready_for_disabled_scheduler_wrapper_slice",
    "require_explicit_human_wrapper_skeleton_record",
    "declare_disabled_by_default_operator_shell_wrapper",
    "declare_no_os_scheduler_registration",
    "declare_no_automatic_loop",
    "declare_no_enablement_command_generation",
    "declare_single_run_lock_policy_without_creating_lock_file",
    "declare_manual_refresh_invocation_boundary_without_invoking_it",
    "declare_status_visibility_contract_without_writing_status",
    "declare_disable_rollback_before_future_enablement",
    "return_wrapper_skeleton_packet_only",
)

FUTURE_ENTRYPOINT_CONTRACT: Tuple[str, ...] = (
    "future_entrypoint_name=check_phase4a_prediction_system_ps_q16h_disabled_scheduler_wrapper_once.py",
    "future_entrypoint_invocation=operator_shell_only",
    "future_entrypoint_default=disabled",
    "future_entrypoint_requires_clean_tree=true",
    "future_entrypoint_requires_ps_q16f_preflight=true",
    "future_entrypoint_requires_no_overlap_lock=true",
    "future_entrypoint_requires_explicit_enablement_record=false_in_ps_q16h",
)

LOCK_POLICY: Tuple[str, ...] = (
    "lock_policy_declared_only=true",
    "lock_file_created_by_this_skeleton=false",
    "lock_relative_path=prediction/status/non_ui_scheduled_producer.lock",
    "on_existing_lock=skip_and_report_status_in_future_slice",
    "overlap_policy=never_overlap_runs",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_scheduler_enable",
    "request_os_scheduler_registration",
    "request_scheduled_loop_enable",
    "request_runtime_artifact_write_automation_enable",
    "request_generate_enablement_command",
    "request_execute_manual_refresh",
    "request_status_artifact_write",
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
class PredictionWarRoomDisabledSchedulerWrapperSkeletonPacket:
    skeleton_version: str
    skeleton_id: str
    skeleton_state: str
    skeleton_sequence: Tuple[str, ...] = WRAPPER_SKELETON_SEQUENCE
    future_entrypoint_contract: Tuple[str, ...] = FUTURE_ENTRYPOINT_CONTRACT
    lock_policy: Tuple[str, ...] = LOCK_POLICY
    design_packet_supplied: bool = False
    design_packet_version: str = ""
    design_ready_for_disabled_scheduler_wrapper_slice: bool = False
    human_wrapper_skeleton_record_present: bool = False
    human_wrapper_skeleton_source: str = ""
    recommended_cadence_sec: int = RECOMMENDED_CADENCE_SEC
    minimum_cadence_sec: int = MINIMUM_CADENCE_SEC
    maximum_cadence_sec: int = MAXIMUM_CADENCE_SEC
    freshness_max_age_sec: int = FRESHNESS_MAX_AGE_SEC
    status_artifact_relative_path: str = PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    lock_relative_path: str = "prediction/status/non_ui_scheduled_producer.lock"
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_future_disabled_operator_shell_wrapper_implementation: bool = False
    ready_for_scheduler_enablement: bool = False
    ready_for_runtime_artifact_write_automation: bool = False
    wrapper_enabled: bool = False
    scheduler_enabled: bool = False
    os_scheduler_registration_performed: bool = False
    scheduled_loop_enabled: bool = False
    enablement_command_generated: bool = False
    manual_refresh_invoked_by_this_skeleton: bool = False
    latest_prediction_refresh_performed_by_this_skeleton: bool = False
    status_artifact_write_performed_by_this_skeleton: bool = False
    lock_file_created_by_this_skeleton: bool = False
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
    skeleton_only: bool = True
    read_only: bool = True
    non_executing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_version": self.skeleton_version,
            "skeleton_id": self.skeleton_id,
            "skeleton_state": self.skeleton_state,
            "skeleton_sequence": list(self.skeleton_sequence),
            "future_entrypoint_contract": list(self.future_entrypoint_contract),
            "lock_policy": list(self.lock_policy),
            "design_packet_supplied": self.design_packet_supplied,
            "design_packet_version": self.design_packet_version,
            "design_ready_for_disabled_scheduler_wrapper_slice": self.design_ready_for_disabled_scheduler_wrapper_slice,
            "human_wrapper_skeleton_record_present": self.human_wrapper_skeleton_record_present,
            "human_wrapper_skeleton_source": self.human_wrapper_skeleton_source,
            "recommended_cadence_sec": self.recommended_cadence_sec,
            "minimum_cadence_sec": self.minimum_cadence_sec,
            "maximum_cadence_sec": self.maximum_cadence_sec,
            "freshness_max_age_sec": self.freshness_max_age_sec,
            "status_artifact_relative_path": self.status_artifact_relative_path,
            "lock_relative_path": self.lock_relative_path,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_future_disabled_operator_shell_wrapper_implementation": self.ready_for_future_disabled_operator_shell_wrapper_implementation,
            "ready_for_scheduler_enablement": self.ready_for_scheduler_enablement,
            "ready_for_runtime_artifact_write_automation": self.ready_for_runtime_artifact_write_automation,
            "wrapper_enabled": self.wrapper_enabled,
            "scheduler_enabled": self.scheduler_enabled,
            "os_scheduler_registration_performed": self.os_scheduler_registration_performed,
            "scheduled_loop_enabled": self.scheduled_loop_enabled,
            "enablement_command_generated": self.enablement_command_generated,
            "manual_refresh_invoked_by_this_skeleton": self.manual_refresh_invoked_by_this_skeleton,
            "latest_prediction_refresh_performed_by_this_skeleton": self.latest_prediction_refresh_performed_by_this_skeleton,
            "status_artifact_write_performed_by_this_skeleton": self.status_artifact_write_performed_by_this_skeleton,
            "lock_file_created_by_this_skeleton": self.lock_file_created_by_this_skeleton,
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
            "skeleton_only": self.skeleton_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
        }


def build_prediction_warroom_disabled_scheduler_wrapper_skeleton(
    *,
    ps_q16g_design_packet: Mapping[str, Any] | Any | None = None,
    human_wrapper_skeleton_record_present: bool = False,
    human_wrapper_skeleton_source: str = "",
    request_scheduler_enable: bool = False,
    request_os_scheduler_registration: bool = False,
    request_scheduled_loop_enable: bool = False,
    request_runtime_artifact_write_automation_enable: bool = False,
    request_generate_enablement_command: bool = False,
    request_execute_manual_refresh: bool = False,
    request_status_artifact_write: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_parameter_staging_write: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomDisabledSchedulerWrapperSkeletonPacket:
    """Return a disabled scheduler wrapper skeleton packet without executing anything."""
    design = _as_mapping(ps_q16g_design_packet)
    requested = _requested_flags(
        request_scheduler_enable=request_scheduler_enable,
        request_os_scheduler_registration=request_os_scheduler_registration,
        request_scheduled_loop_enable=request_scheduled_loop_enable,
        request_runtime_artifact_write_automation_enable=request_runtime_artifact_write_automation_enable,
        request_generate_enablement_command=request_generate_enablement_command,
        request_execute_manual_refresh=request_execute_manual_refresh,
        request_status_artifact_write=request_status_artifact_write,
        request_warroom_ui_trigger=request_warroom_ui_trigger,
        request_parameter_apply=request_parameter_apply,
        request_parameter_staging_write=request_parameter_staging_write,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    )
    blockers: list[str] = ["forbidden_request_in_ps_q16h:" + item for item in requested]
    warnings: list[str] = []
    if not design:
        blockers.append("ps_q16g_design_packet_required")
    else:
        if design.get("design_version") != DISABLED_SCHEDULER_DESIGN_PACKET_VERSION:
            blockers.append("ps_q16g_design_packet_version_mismatch")
        if design.get("ready_for_disabled_scheduler_wrapper_slice") is not True:
            blockers.append("ps_q16g_design_not_ready_for_disabled_scheduler_wrapper_slice")
        for key in (
            "ready_for_scheduler_enablement",
            "scheduler_registration_performed",
            "scheduled_loop_enabled",
            "scheduler_enablement_command_generated",
        ):
            if design.get(key) is not False:
                blockers.append("ps_q16g_" + key + "_must_remain_false")
    if not human_wrapper_skeleton_record_present:
        blockers.append("human_wrapper_skeleton_record_required_for_ps_q16h")
    if human_wrapper_skeleton_record_present and not str(human_wrapper_skeleton_source or "").strip():
        warnings.append("human_wrapper_skeleton_source_not_supplied")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(not unique_blockers)
    state = "disabled_scheduler_wrapper_skeleton_ready_for_future_disabled_implementation" if ready else "disabled_scheduler_wrapper_skeleton_blocked"
    return PredictionWarRoomDisabledSchedulerWrapperSkeletonPacket(
        skeleton_version=DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION,
        skeleton_id=f"{DISABLED_SCHEDULER_WRAPPER_SKELETON_VERSION}:{state}",
        skeleton_state=state,
        design_packet_supplied=bool(design),
        design_packet_version=str(design.get("design_version") or ""),
        design_ready_for_disabled_scheduler_wrapper_slice=bool(design.get("ready_for_disabled_scheduler_wrapper_slice") is True),
        human_wrapper_skeleton_record_present=bool(human_wrapper_skeleton_record_present),
        human_wrapper_skeleton_source=str(human_wrapper_skeleton_source or ""),
        requested_forbidden_flags=requested,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        ready_for_future_disabled_operator_shell_wrapper_implementation=ready,
    )
