# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint.py
# desc: PS-Q25X disabled dry-run design checkpoint for the single-producer 60s WarRoom prediction path. Checkpoint only; no dry-run execution, manual one-shot, locks, scheduler, producer, artifact writes, WarRoom UI trigger, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_once_run_execution_design_checkpoint import (
    FUTURE_EXECUTION_BOUNDARY,
    ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION,
)
from .prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet import (
    SELECTED_CADENCE_OPTION_ID,
    SELECTED_TARGET_CADENCE_SEC,
    SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet,
)

SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION = (
    "prediction_warroom.single_producer_60s_disabled_dry_run_design_checkpoint.ps_q25x.v1"
)

CHECKPOINT_SEQUENCE: Tuple[str, ...] = (
    "consume_q25w_disabled_dry_run_planning_packet_only",
    "require_q25w_ready_for_future_disabled_dry_run_design_checkpoint",
    "record_disabled_dry_run_design_checkpoint_without_execution",
    "declare_future_execution_still_requires_separate_human_gate",
    "declare_future_lock_status_prediction_refresh_sequence_by_reference_only",
    "declare_no_dry_run_execution_in_ps_q25x",
    "declare_no_lock_create_or_delete_in_ps_q25x",
    "declare_no_artifact_writes_in_ps_q25x",
    "return_disabled_dry_run_design_checkpoint_packet_only",
)

FUTURE_DRY_RUN_EXECUTION_GATE: Tuple[str, ...] = (
    "future_execution_gate_required=true",
    "future_gate_must_be_explicit_human_command=true",
    "future_execution_must_start_disabled=false_until_gate",
    "future_must_check_clean_tree=true",
    "future_must_check_lock_absent=true",
    "future_must_write_status_only_after_gate=true",
    "future_scheduler_enablement_allowed=false",
    "future_autotrade_broker_ledger_parameter_allowed=false",
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


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _requested_flags(**flags: bool) -> tuple[str, ...]:
    return tuple(name for name, requested in flags.items() if requested)


@dataclass(frozen=True)
class PredictionWarRoomSingleProducer60sDisabledDryRunDesignCheckpointPacket:
    checkpoint_version: str
    checkpoint_id: str
    checkpoint_state: str
    checkpoint_sequence: Tuple[str, ...] = CHECKPOINT_SEQUENCE
    future_dry_run_execution_gate: Tuple[str, ...] = FUTURE_DRY_RUN_EXECUTION_GATE
    referenced_q16k_checkpoint_version: str = ONCE_RUN_EXECUTION_DESIGN_CHECKPOINT_VERSION
    referenced_q16k_future_execution_boundary: Tuple[str, ...] = FUTURE_EXECUTION_BOUNDARY
    selected_option_id: str = SELECTED_CADENCE_OPTION_ID
    selected_target_cadence_sec: int = SELECTED_TARGET_CADENCE_SEC
    q25w_planning_packet_supplied: bool = False
    q25w_planning_version: str = ""
    q25w_planning_ready: bool = False
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_future_disabled_dry_run_execution_gate_planning: bool = False
    checkpoint_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    execute_dry_run_enabled: bool = False
    manual_one_shot_run_invoked_by_this_checkpoint: bool = False
    future_dry_run_invoked_by_this_checkpoint: bool = False
    q16k_checkpoint_invoked_by_this_checkpoint: bool = False
    status_artifact_write_performed_by_this_checkpoint: bool = False
    runtime_artifact_write_performed_by_this_checkpoint: bool = False
    prediction_artifact_write_performed_by_this_checkpoint: bool = False
    latest_manifest_written: bool = False
    run_sidecars_written: bool = False
    lock_file_created_by_this_checkpoint: bool = False
    lock_file_deleted_by_this_checkpoint: bool = False
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
            "checkpoint_version": self.checkpoint_version,
            "checkpoint_id": self.checkpoint_id,
            "checkpoint_state": self.checkpoint_state,
            "checkpoint_sequence": list(self.checkpoint_sequence),
            "future_dry_run_execution_gate": list(self.future_dry_run_execution_gate),
            "referenced_q16k_checkpoint_version": self.referenced_q16k_checkpoint_version,
            "referenced_q16k_future_execution_boundary": list(self.referenced_q16k_future_execution_boundary),
            "selected_option_id": self.selected_option_id,
            "selected_target_cadence_sec": self.selected_target_cadence_sec,
            "q25w_planning_packet_supplied": self.q25w_planning_packet_supplied,
            "q25w_planning_version": self.q25w_planning_version,
            "q25w_planning_ready": self.q25w_planning_ready,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_future_disabled_dry_run_execution_gate_planning": self.ready_for_future_disabled_dry_run_execution_gate_planning,
            "checkpoint_only": self.checkpoint_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "execute_dry_run_enabled": self.execute_dry_run_enabled,
            "manual_one_shot_run_invoked_by_this_checkpoint": self.manual_one_shot_run_invoked_by_this_checkpoint,
            "future_dry_run_invoked_by_this_checkpoint": self.future_dry_run_invoked_by_this_checkpoint,
            "q16k_checkpoint_invoked_by_this_checkpoint": self.q16k_checkpoint_invoked_by_this_checkpoint,
            "status_artifact_write_performed_by_this_checkpoint": self.status_artifact_write_performed_by_this_checkpoint,
            "runtime_artifact_write_performed_by_this_checkpoint": self.runtime_artifact_write_performed_by_this_checkpoint,
            "prediction_artifact_write_performed_by_this_checkpoint": self.prediction_artifact_write_performed_by_this_checkpoint,
            "latest_manifest_written": self.latest_manifest_written,
            "run_sidecars_written": self.run_sidecars_written,
            "lock_file_created_by_this_checkpoint": self.lock_file_created_by_this_checkpoint,
            "lock_file_deleted_by_this_checkpoint": self.lock_file_deleted_by_this_checkpoint,
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


def build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint(
    *,
    q25w_planning_packet: Mapping[str, Any] | Any | None = None,
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
) -> PredictionWarRoomSingleProducer60sDisabledDryRunDesignCheckpointPacket:
    planning = _as_mapping(q25w_planning_packet) or build_prediction_warroom_single_producer_60s_disabled_dry_run_planning_packet().to_dict()
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
    if planning.get("planning_version") != SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_PLANNING_PACKET_VERSION:
        blockers.append("q25w_planning_version_mismatch")
    if planning.get("selected_option_id") != SELECTED_CADENCE_OPTION_ID:
        blockers.append("q25w_selected_option_mismatch")
    if int(planning.get("selected_target_cadence_sec") or 0) != SELECTED_TARGET_CADENCE_SEC:
        blockers.append("q25w_selected_target_cadence_mismatch")
    if planning.get("ready_for_future_disabled_dry_run_design_checkpoint") is not True:
        blockers.append("q25w_not_ready_for_disabled_dry_run_design_checkpoint")
    for key in (
        "execute_dry_run_enabled",
        "manual_one_shot_run_invoked_by_this_planning",
        "future_dry_run_invoked_by_this_planning",
        "q16l_execution_plan_invoked_by_this_planning",
        "status_artifact_write_performed_by_this_planning",
        "runtime_artifact_write_performed_by_this_planning",
        "prediction_artifact_write_performed_by_this_planning",
        "latest_manifest_written",
        "run_sidecars_written",
        "lock_file_created_by_this_planning",
        "lock_file_deleted_by_this_planning",
        "scheduler_enabled",
        "producer_enabled",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        if planning.get(key) is not False:
            blockers.append("q25w_false_required:" + key)
    for flag in requested:
        blockers.append("forbidden_request_in_ps_q25x:" + flag)
    ready = not blockers
    state = "single_producer_60s_disabled_dry_run_design_checkpoint_ready" if ready else "single_producer_60s_disabled_dry_run_design_checkpoint_blocked"
    return PredictionWarRoomSingleProducer60sDisabledDryRunDesignCheckpointPacket(
        checkpoint_version=SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION,
        checkpoint_id=f"{SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION}:{SELECTED_CADENCE_OPTION_ID}:{state}",
        checkpoint_state=state,
        q25w_planning_packet_supplied=bool(planning),
        q25w_planning_version=str(planning.get("planning_version") or ""),
        q25w_planning_ready=bool(planning.get("ready_for_future_disabled_dry_run_design_checkpoint") is True and not blockers),
        requested_forbidden_flags=requested,
        blocker_count=len(blockers),
        warning_count=len(warnings),
        blocked_reasons=tuple(blockers),
        warning_reasons=tuple(warnings),
        ready_for_future_disabled_dry_run_execution_gate_planning=ready,
    )
