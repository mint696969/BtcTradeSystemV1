# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet.py
# desc: PS-Q25Y explicit human gate packet for a future disabled/manual single-producer 60s dry-run. Gate marker only; it never executes dry-run, invokes manual one-shot, creates/deletes locks, writes artifacts, enables scheduler/producer, triggers UI/AutoTrade/broker/ledger/mode/parameter behavior, or grants execution by itself.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint import (
    SELECTED_CADENCE_OPTION_ID,
    SELECTED_TARGET_CADENCE_SEC,
    SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint,
)

SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_HUMAN_GATE_PACKET_VERSION = (
    "prediction_warroom.single_producer_60s_disabled_dry_run_human_gate_packet.ps_q25y.v1"
)
DRY_RUN_HUMAN_GATE_TOKEN = "GRANT_Q25Y_DISABLED_SINGLE_PRODUCER_60S_DRY_RUN_PLANNING_ONLY"

HUMAN_GATE_SEQUENCE: Tuple[str, ...] = (
    "consume_q25x_disabled_dry_run_design_checkpoint_only",
    "declare_future_disabled_manual_dry_run_requires_explicit_human_gate",
    "publish_planning_only_gate_token_candidate",
    "record_no_human_gate_granted_in_ps_q25y",
    "declare_separate_execution_slice_required_even_if_token_is_supplied",
    "declare_no_dry_run_execution_in_ps_q25y",
    "declare_no_lock_create_or_delete_in_ps_q25y",
    "declare_no_artifact_writes_in_ps_q25y",
    "return_human_gate_marker_packet_only",
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
class PredictionWarRoomSingleProducer60sDisabledDryRunHumanGatePacket:
    gate_version: str
    gate_id: str
    gate_state: str
    gate_sequence: Tuple[str, ...] = HUMAN_GATE_SEQUENCE
    selected_option_id: str = SELECTED_CADENCE_OPTION_ID
    selected_target_cadence_sec: int = SELECTED_TARGET_CADENCE_SEC
    q25x_checkpoint_packet_supplied: bool = False
    q25x_checkpoint_version: str = ""
    q25x_checkpoint_ready: bool = False
    gate_token_candidate: str = DRY_RUN_HUMAN_GATE_TOKEN
    supplied_gate_token: str = ""
    gate_token_detected: bool = False
    human_gate_required_before_any_dry_run: bool = True
    human_gate_granted_by_this_packet: bool = False
    separate_execution_slice_required: bool = True
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_future_disabled_manual_dry_run_gate_decision: bool = False
    gate_marker_only: bool = True
    decision_packet_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    execute_dry_run_allowed_by_this_packet: bool = False
    execute_dry_run_enabled: bool = False
    manual_one_shot_run_invoked_by_this_gate: bool = False
    future_dry_run_invoked_by_this_gate: bool = False
    status_artifact_write_performed_by_this_gate: bool = False
    runtime_artifact_write_performed_by_this_gate: bool = False
    prediction_artifact_write_performed_by_this_gate: bool = False
    latest_manifest_written: bool = False
    run_sidecars_written: bool = False
    lock_file_created_by_this_gate: bool = False
    lock_file_deleted_by_this_gate: bool = False
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
            "gate_version": self.gate_version,
            "gate_id": self.gate_id,
            "gate_state": self.gate_state,
            "gate_sequence": list(self.gate_sequence),
            "selected_option_id": self.selected_option_id,
            "selected_target_cadence_sec": self.selected_target_cadence_sec,
            "q25x_checkpoint_packet_supplied": self.q25x_checkpoint_packet_supplied,
            "q25x_checkpoint_version": self.q25x_checkpoint_version,
            "q25x_checkpoint_ready": self.q25x_checkpoint_ready,
            "gate_token_candidate": self.gate_token_candidate,
            "supplied_gate_token": self.supplied_gate_token,
            "gate_token_detected": self.gate_token_detected,
            "human_gate_required_before_any_dry_run": self.human_gate_required_before_any_dry_run,
            "human_gate_granted_by_this_packet": self.human_gate_granted_by_this_packet,
            "separate_execution_slice_required": self.separate_execution_slice_required,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_future_disabled_manual_dry_run_gate_decision": self.ready_for_future_disabled_manual_dry_run_gate_decision,
            "gate_marker_only": self.gate_marker_only,
            "decision_packet_only": self.decision_packet_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "execute_dry_run_allowed_by_this_packet": self.execute_dry_run_allowed_by_this_packet,
            "execute_dry_run_enabled": self.execute_dry_run_enabled,
            "manual_one_shot_run_invoked_by_this_gate": self.manual_one_shot_run_invoked_by_this_gate,
            "future_dry_run_invoked_by_this_gate": self.future_dry_run_invoked_by_this_gate,
            "status_artifact_write_performed_by_this_gate": self.status_artifact_write_performed_by_this_gate,
            "runtime_artifact_write_performed_by_this_gate": self.runtime_artifact_write_performed_by_this_gate,
            "prediction_artifact_write_performed_by_this_gate": self.prediction_artifact_write_performed_by_this_gate,
            "latest_manifest_written": self.latest_manifest_written,
            "run_sidecars_written": self.run_sidecars_written,
            "lock_file_created_by_this_gate": self.lock_file_created_by_this_gate,
            "lock_file_deleted_by_this_gate": self.lock_file_deleted_by_this_gate,
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


def build_prediction_warroom_single_producer_60s_disabled_dry_run_human_gate_packet(
    *,
    q25x_checkpoint_packet: Mapping[str, Any] | Any | None = None,
    supplied_gate_token: str = "",
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
) -> PredictionWarRoomSingleProducer60sDisabledDryRunHumanGatePacket:
    checkpoint = _as_mapping(q25x_checkpoint_packet) or build_prediction_warroom_single_producer_60s_disabled_dry_run_design_checkpoint().to_dict()
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
    if checkpoint.get("checkpoint_version") != SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_DESIGN_CHECKPOINT_VERSION:
        blockers.append("q25x_checkpoint_version_mismatch")
    if checkpoint.get("selected_option_id") != SELECTED_CADENCE_OPTION_ID:
        blockers.append("q25x_selected_option_mismatch")
    if int(checkpoint.get("selected_target_cadence_sec") or 0) != SELECTED_TARGET_CADENCE_SEC:
        blockers.append("q25x_selected_target_cadence_mismatch")
    if checkpoint.get("ready_for_future_disabled_dry_run_execution_gate_planning") is not True:
        blockers.append("q25x_not_ready_for_disabled_dry_run_execution_gate_planning")
    for key in (
        "execute_dry_run_enabled",
        "manual_one_shot_run_invoked_by_this_checkpoint",
        "future_dry_run_invoked_by_this_checkpoint",
        "q16k_checkpoint_invoked_by_this_checkpoint",
        "status_artifact_write_performed_by_this_checkpoint",
        "runtime_artifact_write_performed_by_this_checkpoint",
        "prediction_artifact_write_performed_by_this_checkpoint",
        "latest_manifest_written",
        "run_sidecars_written",
        "lock_file_created_by_this_checkpoint",
        "lock_file_deleted_by_this_checkpoint",
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
        if checkpoint.get(key) is not False:
            blockers.append("q25x_false_required:" + key)
    gate_token_detected = supplied_gate_token == DRY_RUN_HUMAN_GATE_TOKEN
    if supplied_gate_token and not gate_token_detected:
        warnings.append("supplied_gate_token_unrecognized_ignored")
    if gate_token_detected:
        blockers.append("gate_token_detected_but_execution_requires_separate_future_slice")
    for flag in requested:
        blockers.append("forbidden_request_in_ps_q25y:" + flag)
    ready = not blockers or (blockers == ["gate_token_detected_but_execution_requires_separate_future_slice"])
    state = "awaiting_human_dry_run_gate_decision" if not gate_token_detected else "human_gate_intent_detected_separate_execution_slice_required"
    if requested or any(item.startswith("q25x_") for item in blockers):
        state = "disabled_dry_run_human_gate_packet_blocked"
    return PredictionWarRoomSingleProducer60sDisabledDryRunHumanGatePacket(
        gate_version=SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_HUMAN_GATE_PACKET_VERSION,
        gate_id=f"{SINGLE_PRODUCER_60S_DISABLED_DRY_RUN_HUMAN_GATE_PACKET_VERSION}:{SELECTED_CADENCE_OPTION_ID}:{state}",
        gate_state=state,
        q25x_checkpoint_packet_supplied=bool(checkpoint),
        q25x_checkpoint_version=str(checkpoint.get("checkpoint_version") or ""),
        q25x_checkpoint_ready=bool(checkpoint.get("ready_for_future_disabled_dry_run_execution_gate_planning") is True and not any(item.startswith("q25x_") for item in blockers)),
        supplied_gate_token=supplied_gate_token,
        gate_token_detected=gate_token_detected,
        requested_forbidden_flags=requested,
        blocker_count=len(blockers),
        warning_count=len(warnings),
        blocked_reasons=tuple(blockers),
        warning_reasons=tuple(warnings),
        ready_for_future_disabled_manual_dry_run_gate_decision=ready,
    )
