# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet.py
# desc: PS-Q25W disabled dry-run planning packet for the single-producer 60s WarRoom prediction path. Planning only; no one-shot execution, locks, scheduler, producer, artifact writes, WarRoom UI trigger, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_guarded_once_run_execution_plan_packet import (
    GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION,
    LOCK_RELATIVE_PATH,
    PLAN_STEPS,
)
from .prediction_warroom_single_producer_60s_disabled_validation_packet import (
    SELECTED_CADENCE_OPTION_ID,
    SELECTED_TARGET_CADENCE_SEC,
    SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_validation_packet,
)

SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION = (
    "prediction_warroom.single_producer_60s_disabled_dry_run_planning.ps_q25w.v1"
)

DRY_RUN_PLANNING_SEQUENCE: Tuple[str, ...] = (
    "consume_q25v_disabled_validation_packet_only",
    "declare_future_disabled_dry_run_intent_without_execution",
    "declare_clean_tree_required_before_future_dry_run",
    "declare_lock_absent_check_required_before_future_dry_run",
    "declare_status_visibility_required_before_future_dry_run",
    "declare_future_steps_reuse_q16l_guarded_plan_steps_by_reference_only",
    "declare_no_manual_one_shot_run_in_ps_q25w",
    "declare_no_lock_create_or_delete_in_ps_q25w",
    "declare_no_artifact_writes_in_ps_q25w",
    "return_disabled_dry_run_planning_packet_only",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_execute_dry_run",
    "request_manual_one_shot_run",
    "request_scheduler_enable",
    "request_producer_enable",
    "request_status_artifact_write",
    "request_runtime_artifact_write",
    "request_prediction_artifact_write",
    "request_latest_manifest_write",
    "request_run_sidecars_write",
    "request_lock_file_create",
    "request_lock_file_delete",
    "request_warroom_ui_trigger",
    "request_parameter_apply",
    "request_approval_or_ledger_or_autotrade_or_broker",
)

FUTURE_DRY_RUN_REQUIREMENTS: Tuple[str, ...] = (
    "future_requires_explicit_human_dry_run_gate=true",
    "future_requires_clean_tree=true",
    "future_requires_lock_absent=true",
    "future_requires_status_visibility=true",
    "future_requires_no_scheduler_enablement=true",
    "future_requires_no_autotrade_broker_ledger_parameter=true",
    "future_default_action=plan_only_no_execution",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _requested_flags(**flags: bool) -> tuple[str, ...]:
    return tuple(name for name, requested in flags.items() if requested)


@dataclass(frozen=True)
class PredictionWarRoomSingleProducer60sDisabledDryRunPlanningPacket:
    planning_version: str
    planning_id: str
    planning_state: str
    planning_sequence: Tuple[str, ...] = DRY_RUN_PLANNING_SEQUENCE
    future_dry_run_requirements: Tuple[str, ...] = FUTURE_DRY_RUN_REQUIREMENTS
    referenced_q16l_plan_version: str = GUARDED_ONCE_RUN_EXECUTION_PLAN_PACKET_VERSION
    referenced_q16l_plan_steps: Tuple[str, ...] = PLAN_STEPS
    selected_option_id: str = SELECTED_CADENCE_OPTION_ID
    selected_target_cadence_sec: int = SELECTED_TARGET_CADENCE_SEC
    lock_relative_path: str = LOCK_RELATIVE_PATH
    q25v_validation_packet_supplied: bool = False
    q25v_validation_version: str = ""
    q25v_validation_ready: bool = False
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_future_disabled_dry_run_design_checkpoint: bool = False
    dry_run_planning_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    execute_dry_run_enabled: bool = False
    manual_one_shot_run_invoked_by_this_planning: bool = False
    future_dry_run_invoked_by_this_planning: bool = False
    q16l_execution_plan_invoked_by_this_planning: bool = False
    status_artifact_write_performed_by_this_planning: bool = False
    runtime_artifact_write_performed_by_this_planning: bool = False
    prediction_artifact_write_performed_by_this_planning: bool = False
    latest_manifest_written: bool = False
    run_sidecars_written: bool = False
    lock_file_created_by_this_planning: bool = False
    lock_file_deleted_by_this_planning: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    scheduled_loop_enabled: bool = False
    warroom_ui_trigger_enabled: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    ledger_append_allowed: bool = False
    mode_apply_allowed: bool = False
    parameter_apply_allowed: bool = False
    would_send_to_broker: bool = False
    freshness_bypass_added: bool = False
    force_ready_added: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "planning_version": self.planning_version,
            "planning_id": self.planning_id,
            "planning_state": self.planning_state,
            "planning_sequence": list(self.planning_sequence),
            "future_dry_run_requirements": list(self.future_dry_run_requirements),
            "referenced_q16l_plan_version": self.referenced_q16l_plan_version,
            "referenced_q16l_plan_steps": list(self.referenced_q16l_plan_steps),
            "selected_option_id": self.selected_option_id,
            "selected_target_cadence_sec": self.selected_target_cadence_sec,
            "lock_relative_path": self.lock_relative_path,
            "q25v_validation_packet_supplied": self.q25v_validation_packet_supplied,
            "q25v_validation_version": self.q25v_validation_version,
            "q25v_validation_ready": self.q25v_validation_ready,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_future_disabled_dry_run_design_checkpoint": self.ready_for_future_disabled_dry_run_design_checkpoint,
            "dry_run_planning_only": self.dry_run_planning_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "execute_dry_run_enabled": self.execute_dry_run_enabled,
            "manual_one_shot_run_invoked_by_this_planning": self.manual_one_shot_run_invoked_by_this_planning,
            "future_dry_run_invoked_by_this_planning": self.future_dry_run_invoked_by_this_planning,
            "q16l_execution_plan_invoked_by_this_planning": self.q16l_execution_plan_invoked_by_this_planning,
            "status_artifact_write_performed_by_this_planning": self.status_artifact_write_performed_by_this_planning,
            "runtime_artifact_write_performed_by_this_planning": self.runtime_artifact_write_performed_by_this_planning,
            "prediction_artifact_write_performed_by_this_planning": self.prediction_artifact_write_performed_by_this_planning,
            "latest_manifest_written": self.latest_manifest_written,
            "run_sidecars_written": self.run_sidecars_written,
            "lock_file_created_by_this_planning": self.lock_file_created_by_this_planning,
            "lock_file_deleted_by_this_planning": self.lock_file_deleted_by_this_planning,
            "scheduler_enabled": self.scheduler_enabled,
            "producer_enabled": self.producer_enabled,
            "scheduled_loop_enabled": self.scheduled_loop_enabled,
            "warroom_ui_trigger_enabled": self.warroom_ui_trigger_enabled,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "mode_apply_allowed": self.mode_apply_allowed,
            "parameter_apply_allowed": self.parameter_apply_allowed,
            "would_send_to_broker": self.would_send_to_broker,
            "freshness_bypass_added": self.freshness_bypass_added,
            "force_ready_added": self.force_ready_added,
        }


def build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet(
    *,
    q25v_validation_packet: Mapping[str, Any] | Any | None = None,
    request_execute_dry_run: bool = False,
    request_manual_one_shot_run: bool = False,
    request_scheduler_enable: bool = False,
    request_producer_enable: bool = False,
    request_status_artifact_write: bool = False,
    request_runtime_artifact_write: bool = False,
    request_prediction_artifact_write: bool = False,
    request_latest_manifest_write: bool = False,
    request_run_sidecars_write: bool = False,
    request_lock_file_create: bool = False,
    request_lock_file_delete: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomSingleProducer60sDisabledDryRunPlanningPacket:
    validation = _as_mapping(q25v_validation_packet) or build_prediction_warroom_single_producer_60s_disabled_validation_packet().to_dict()
    requested = _requested_flags(
        request_execute_dry_run=request_execute_dry_run,
        request_manual_one_shot_run=request_manual_one_shot_run,
        request_scheduler_enable=request_scheduler_enable,
        request_producer_enable=request_producer_enable,
        request_status_artifact_write=request_status_artifact_write,
        request_runtime_artifact_write=request_runtime_artifact_write,
        request_prediction_artifact_write=request_prediction_artifact_write,
        request_latest_manifest_write=request_latest_manifest_write,
        request_run_sidecars_write=request_run_sidecars_write,
        request_lock_file_create=request_lock_file_create,
        request_lock_file_delete=request_lock_file_delete,
        request_warroom_ui_trigger=request_warroom_ui_trigger,
        request_parameter_apply=request_parameter_apply,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    )
    blockers: list[str] = []
    warnings: list[str] = []
    if validation.get("validation_version") != SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION:
        blockers.append("q25v_validation_version_mismatch")
    if validation.get("selected_option_id") != SELECTED_CADENCE_OPTION_ID:
        blockers.append("q25v_selected_option_mismatch")
    if int(validation.get("selected_target_cadence_sec") or 0) != SELECTED_TARGET_CADENCE_SEC:
        blockers.append("q25v_selected_target_cadence_mismatch")
    if validation.get("ready_for_disabled_dry_run_planning") is not True:
        blockers.append("q25v_not_ready_for_disabled_dry_run_planning")
    for key in (
        "manual_one_shot_run_invoked_by_this_validation",
        "q16b_runner_invoked_for_actual_refresh",
        "q16b_status_artifact_written",
        "q16b_latest_prediction_artifact_written",
        "scheduler_enabled",
        "producer_enabled",
        "runtime_artifact_write_enabled",
        "status_artifact_write_enabled",
        "prediction_artifact_write_enabled",
        "latest_manifest_written",
        "run_sidecars_written",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "parameter_apply_allowed",
        "mode_apply_allowed",
        "would_send_to_broker",
    ):
        if validation.get(key) is not False:
            blockers.append("q25v_false_required:" + key)
    for flag in requested:
        blockers.append("forbidden_request_in_ps_q25w:" + flag)
    ready = not blockers
    state = "single_producer_60s_disabled_dry_run_planning_ready" if ready else "single_producer_60s_disabled_dry_run_planning_blocked"
    return PredictionWarRoomSingleProducer60sDisabledDryRunPlanningPacket(
        planning_version=SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION,
        planning_id=f"{SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION}:{SELECTED_CADENCE_OPTION_ID}:{state}",
        planning_state=state,
        q25v_validation_packet_supplied=bool(validation),
        q25v_validation_version=str(validation.get("validation_version") or ""),
        q25v_validation_ready=bool(validation.get("ready_for_disabled_dry_run_planning") is True and not blockers),
        requested_forbidden_flags=requested,
        blocker_count=len(blockers),
        warning_count=len(warnings),
        blocked_reasons=tuple(blockers),
        warning_reasons=tuple(warnings),
        ready_for_future_disabled_dry_run_design_checkpoint=ready,
    )
