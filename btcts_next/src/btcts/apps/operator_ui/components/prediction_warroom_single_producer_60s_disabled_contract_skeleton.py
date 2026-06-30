# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_contract_skeleton.py
# desc: PS-Q25U disabled contract/skeleton for a future single non-UI WarRoom prediction producer targeting 60s cadence. Declares boundaries only; it never runs predictions, schedules, writes artifacts, triggers WarRoom UI, mutates parameters, appends ledgers, triggers AutoTrade, or calls broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_non_ui_scheduled_producer_contract import (
    LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
    MAXIMUM_CADENCE_SEC,
    MINIMUM_CADENCE_SEC,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
)

SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION = (
    "prediction_warroom.single_producer_60s_disabled_contract_skeleton.ps_q25u.v1"
)
SELECTED_CADENCE_OPTION_ID = "single_producer_60s_candidate"
SELECTED_TARGET_CADENCE_SEC = 60
LOCK_RELATIVE_PATH = "prediction/status/non_ui_scheduled_producer.lock"

SKELETON_SEQUENCE: Tuple[str, ...] = (
    "consume_ps_q25t_disabled_implementation_preflight_packet_only",
    "declare_single_producer_60s_candidate_contract_skeleton",
    "bind_existing_q16_disabled_runner_candidates_without_invoking_them",
    "declare_default_disabled_no_scheduler_no_loop",
    "declare_no_manual_one_shot_run_in_ps_q25u",
    "declare_no_runtime_or_status_or_prediction_or_view_artifact_writes",
    "declare_no_latest_manifest_or_sidecar_writes",
    "declare_single_run_lock_required_for_future_run_only",
    "declare_status_visibility_required_before_enablement",
    "declare_disable_rollback_required_before_enablement",
    "return_disabled_contract_skeleton_packet_only",
)

CANDIDATE_COMPONENTS: Tuple[str, ...] = (
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_runner.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_bounded_manual_refresh_runner.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_scheduler_wrapper_skeleton.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_disabled_once_run_checker.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_guarded_once_run_execution_plan_packet.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_status_panel.py",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_manual_one_shot_run",
    "request_scheduler_enable",
    "request_scheduler_action_change",
    "request_producer_enable",
    "request_runtime_artifact_write",
    "request_status_artifact_write",
    "request_prediction_artifact_write",
    "request_view_artifact_write",
    "request_latest_manifest_write",
    "request_run_sidecars_write",
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
class PredictionWarRoomSingleProducer60sDisabledContractSkeletonPacket:
    skeleton_version: str
    skeleton_id: str
    skeleton_state: str
    skeleton_sequence: Tuple[str, ...] = SKELETON_SEQUENCE
    selected_option_id: str = SELECTED_CADENCE_OPTION_ID
    selected_target_cadence_sec: int = SELECTED_TARGET_CADENCE_SEC
    minimum_cadence_sec: int = MINIMUM_CADENCE_SEC
    maximum_cadence_sec: int = MAXIMUM_CADENCE_SEC
    inherited_recommended_cadence_sec: int = RECOMMENDED_CADENCE_SEC
    latest_prediction_artifact_relative_path: str = LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH
    producer_status_artifact_relative_path: str = PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    lock_relative_path: str = LOCK_RELATIVE_PATH
    candidate_components: Tuple[str, ...] = CANDIDATE_COMPONENTS
    q25t_preflight_packet_supplied: bool = False
    q25t_preflight_ready: bool = False
    q25t_selected_option_id: str = ""
    q25t_selected_target_cadence_sec: int | None = None
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_future_disabled_single_producer_60s_skeleton_validation: bool = False
    ready_for_manual_one_shot_run: bool = False
    ready_for_scheduler_enablement: bool = False
    ready_for_producer_enablement: bool = False
    contract_skeleton_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    default_enabled: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    scheduled_loop_enabled: bool = False
    manual_one_shot_run_invoked_by_this_skeleton: bool = False
    prediction_build_requested: bool = False
    actual_export_runner_invoked: bool = False
    bounded_manual_refresh_invoked: bool = False
    runtime_artifact_write_enabled: bool = False
    status_artifact_write_enabled: bool = False
    latest_prediction_artifact_write_enabled: bool = False
    view_artifact_write_enabled: bool = False
    latest_manifest_write_enabled: bool = False
    run_sidecars_write_enabled: bool = False
    would_write_runtime_artifact: bool = False
    would_write_status_artifact: bool = False
    would_write_prediction_artifact: bool = False
    would_write_view_artifact: bool = False
    latest_manifest_written: bool = False
    run_sidecars_written: bool = False
    lock_file_created_by_this_skeleton: bool = False
    lock_file_deleted_by_this_skeleton: bool = False
    warroom_ui_trigger_enabled: bool = False
    ui_triggered_runner_execution: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    parameter_apply_allowed: bool = False
    parameter_staging_write_allowed: bool = False
    mode_apply_allowed: bool = False
    would_send_to_broker: bool = False
    freshness_bypass_added: bool = False
    force_ready_added: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_version": self.skeleton_version,
            "skeleton_id": self.skeleton_id,
            "skeleton_state": self.skeleton_state,
            "skeleton_sequence": list(self.skeleton_sequence),
            "selected_option_id": self.selected_option_id,
            "selected_target_cadence_sec": self.selected_target_cadence_sec,
            "minimum_cadence_sec": self.minimum_cadence_sec,
            "maximum_cadence_sec": self.maximum_cadence_sec,
            "inherited_recommended_cadence_sec": self.inherited_recommended_cadence_sec,
            "latest_prediction_artifact_relative_path": self.latest_prediction_artifact_relative_path,
            "producer_status_artifact_relative_path": self.producer_status_artifact_relative_path,
            "lock_relative_path": self.lock_relative_path,
            "candidate_components": list(self.candidate_components),
            "q25t_preflight_packet_supplied": self.q25t_preflight_packet_supplied,
            "q25t_preflight_ready": self.q25t_preflight_ready,
            "q25t_selected_option_id": self.q25t_selected_option_id,
            "q25t_selected_target_cadence_sec": self.q25t_selected_target_cadence_sec,
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_future_disabled_single_producer_60s_skeleton_validation": self.ready_for_future_disabled_single_producer_60s_skeleton_validation,
            "ready_for_manual_one_shot_run": self.ready_for_manual_one_shot_run,
            "ready_for_scheduler_enablement": self.ready_for_scheduler_enablement,
            "ready_for_producer_enablement": self.ready_for_producer_enablement,
            "contract_skeleton_only": self.contract_skeleton_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "default_enabled": self.default_enabled,
            "scheduler_enabled": self.scheduler_enabled,
            "producer_enabled": self.producer_enabled,
            "scheduled_loop_enabled": self.scheduled_loop_enabled,
            "manual_one_shot_run_invoked_by_this_skeleton": self.manual_one_shot_run_invoked_by_this_skeleton,
            "prediction_build_requested": self.prediction_build_requested,
            "actual_export_runner_invoked": self.actual_export_runner_invoked,
            "bounded_manual_refresh_invoked": self.bounded_manual_refresh_invoked,
            "runtime_artifact_write_enabled": self.runtime_artifact_write_enabled,
            "status_artifact_write_enabled": self.status_artifact_write_enabled,
            "latest_prediction_artifact_write_enabled": self.latest_prediction_artifact_write_enabled,
            "view_artifact_write_enabled": self.view_artifact_write_enabled,
            "latest_manifest_write_enabled": self.latest_manifest_write_enabled,
            "run_sidecars_write_enabled": self.run_sidecars_write_enabled,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_status_artifact": self.would_write_status_artifact,
            "would_write_prediction_artifact": self.would_write_prediction_artifact,
            "would_write_view_artifact": self.would_write_view_artifact,
            "latest_manifest_written": self.latest_manifest_written,
            "run_sidecars_written": self.run_sidecars_written,
            "lock_file_created_by_this_skeleton": self.lock_file_created_by_this_skeleton,
            "lock_file_deleted_by_this_skeleton": self.lock_file_deleted_by_this_skeleton,
            "warroom_ui_trigger_enabled": self.warroom_ui_trigger_enabled,
            "ui_triggered_runner_execution": self.ui_triggered_runner_execution,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "parameter_apply_allowed": self.parameter_apply_allowed,
            "parameter_staging_write_allowed": self.parameter_staging_write_allowed,
            "mode_apply_allowed": self.mode_apply_allowed,
            "would_send_to_broker": self.would_send_to_broker,
            "freshness_bypass_added": self.freshness_bypass_added,
            "force_ready_added": self.force_ready_added,
        }


def build_prediction_warroom_single_producer_60s_disabled_contract_skeleton(
    *,
    q25t_preflight_packet: Mapping[str, Any] | Any | None = None,
    request_manual_one_shot_run: bool = False,
    request_scheduler_enable: bool = False,
    request_scheduler_action_change: bool = False,
    request_producer_enable: bool = False,
    request_runtime_artifact_write: bool = False,
    request_status_artifact_write: bool = False,
    request_prediction_artifact_write: bool = False,
    request_view_artifact_write: bool = False,
    request_latest_manifest_write: bool = False,
    request_run_sidecars_write: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomSingleProducer60sDisabledContractSkeletonPacket:
    preflight = _as_mapping(q25t_preflight_packet)
    requested = _requested_flags(
        request_manual_one_shot_run=request_manual_one_shot_run,
        request_scheduler_enable=request_scheduler_enable,
        request_scheduler_action_change=request_scheduler_action_change,
        request_producer_enable=request_producer_enable,
        request_runtime_artifact_write=request_runtime_artifact_write,
        request_status_artifact_write=request_status_artifact_write,
        request_prediction_artifact_write=request_prediction_artifact_write,
        request_view_artifact_write=request_view_artifact_write,
        request_latest_manifest_write=request_latest_manifest_write,
        request_run_sidecars_write=request_run_sidecars_write,
        request_warroom_ui_trigger=request_warroom_ui_trigger,
        request_parameter_apply=request_parameter_apply,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    )
    blockers: list[str] = []
    warnings: list[str] = []
    if SELECTED_TARGET_CADENCE_SEC < MINIMUM_CADENCE_SEC or SELECTED_TARGET_CADENCE_SEC > MAXIMUM_CADENCE_SEC:
        blockers.append("selected_target_cadence_outside_contract_bounds")
    if not preflight:
        warnings.append("q25t_preflight_packet_not_supplied_skeleton_still_disabled")
    else:
        if preflight.get("selected_option_id") != SELECTED_CADENCE_OPTION_ID:
            blockers.append("q25t_selected_option_mismatch")
        if int(preflight.get("selected_target_cadence_sec") or 0) != SELECTED_TARGET_CADENCE_SEC:
            blockers.append("q25t_selected_target_cadence_mismatch")
        if preflight.get("preflight_only") is not True:
            blockers.append("q25t_preflight_only_required")
        if preflight.get("implementation_allowed_by_this_packet") is not False:
            blockers.append("q25t_must_not_allow_implementation")
        if preflight.get("manual_one_shot_run_allowed") is not False:
            blockers.append("q25t_must_not_allow_manual_one_shot")
        if preflight.get("scheduler_enablement_allowed") is not False:
            blockers.append("q25t_must_not_allow_scheduler_enablement")
    for flag in requested:
        blockers.append("forbidden_request_in_ps_q25u:" + flag)
    ready = bool(preflight) and not blockers
    state = "single_producer_60s_disabled_contract_skeleton_ready" if ready else "single_producer_60s_disabled_contract_skeleton_blocked_or_observation_only"
    return PredictionWarRoomSingleProducer60sDisabledContractSkeletonPacket(
        skeleton_version=SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION,
        skeleton_id=f"{SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION}:{SELECTED_CADENCE_OPTION_ID}:{state}",
        skeleton_state=state,
        q25t_preflight_packet_supplied=bool(preflight),
        q25t_preflight_ready=bool(preflight and not blockers),
        q25t_selected_option_id=str(preflight.get("selected_option_id") or ""),
        q25t_selected_target_cadence_sec=int(preflight.get("selected_target_cadence_sec") or 0) if preflight else None,
        requested_forbidden_flags=requested,
        blocker_count=len(blockers),
        warning_count=len(warnings),
        blocked_reasons=tuple(blockers),
        warning_reasons=tuple(warnings),
        ready_for_future_disabled_single_producer_60s_skeleton_validation=ready,
    )
