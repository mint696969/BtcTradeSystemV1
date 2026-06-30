# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_single_producer_60s_disabled_validation_packet.py
# desc: PS-Q25V disabled validation packet for the Q25U single-producer 60s skeleton. In-memory validation only; no runner execution, scheduler, lock, artifact write, WarRoom UI trigger, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_non_ui_scheduled_producer_runner import (
    PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION,
    build_prediction_warroom_non_ui_scheduled_producer_runner,
)
from .prediction_warroom_single_producer_60s_disabled_contract_skeleton import (
    SELECTED_CADENCE_OPTION_ID,
    SELECTED_TARGET_CADENCE_SEC,
    SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION,
    build_prediction_warroom_single_producer_60s_disabled_contract_skeleton,
)

SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION = (
    "prediction_warroom.single_producer_60s_disabled_validation_packet.ps_q25v.v1"
)

VALIDATION_SEQUENCE: Tuple[str, ...] = (
    "build_q25u_disabled_skeleton_packet_in_memory",
    "build_q16b_disabled_runner_default_packet_in_memory",
    "compare_selected_60s_option_and_disabled_boundaries",
    "verify_runner_default_does_not_write_or_enable",
    "verify_no_manual_one_shot_scheduler_producer_or_artifact_write",
    "return_validation_packet_only",
)

FORBIDDEN_REQUEST_NAMES: Tuple[str, ...] = (
    "request_manual_one_shot_run",
    "request_scheduler_enable",
    "request_producer_enable",
    "request_status_artifact_write",
    "request_runtime_artifact_write",
    "request_prediction_artifact_write",
    "request_latest_manifest_write",
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
class PredictionWarRoomSingleProducer60sDisabledValidationPacket:
    validation_version: str
    validation_id: str
    validation_state: str
    validation_sequence: Tuple[str, ...] = VALIDATION_SEQUENCE
    selected_option_id: str = SELECTED_CADENCE_OPTION_ID
    selected_target_cadence_sec: int = SELECTED_TARGET_CADENCE_SEC
    q25u_skeleton_version: str = SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION
    q16b_runner_version: str = PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION
    q25u_skeleton_packet: Mapping[str, Any] | None = None
    q16b_default_runner_packet: Mapping[str, Any] | None = None
    requested_forbidden_flags: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    ready_for_disabled_dry_run_planning: bool = False
    validation_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    manual_one_shot_run_invoked_by_this_validation: bool = False
    q16b_runner_invoked_for_actual_refresh: bool = False
    q16b_status_artifact_written: bool = False
    q16b_latest_prediction_artifact_written: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    runtime_artifact_write_enabled: bool = False
    status_artifact_write_enabled: bool = False
    prediction_artifact_write_enabled: bool = False
    latest_manifest_written: bool = False
    run_sidecars_written: bool = False
    warroom_ui_trigger_enabled: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    ledger_append_allowed: bool = False
    mode_apply_allowed: bool = False
    parameter_apply_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_version": self.validation_version,
            "validation_id": self.validation_id,
            "validation_state": self.validation_state,
            "validation_sequence": list(self.validation_sequence),
            "selected_option_id": self.selected_option_id,
            "selected_target_cadence_sec": self.selected_target_cadence_sec,
            "q25u_skeleton_version": self.q25u_skeleton_version,
            "q16b_runner_version": self.q16b_runner_version,
            "q25u_skeleton_packet": dict(self.q25u_skeleton_packet or {}),
            "q16b_default_runner_packet": dict(self.q16b_default_runner_packet or {}),
            "requested_forbidden_flags": list(self.requested_forbidden_flags),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "ready_for_disabled_dry_run_planning": self.ready_for_disabled_dry_run_planning,
            "validation_only": self.validation_only,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "manual_one_shot_run_invoked_by_this_validation": self.manual_one_shot_run_invoked_by_this_validation,
            "q16b_runner_invoked_for_actual_refresh": self.q16b_runner_invoked_for_actual_refresh,
            "q16b_status_artifact_written": self.q16b_status_artifact_written,
            "q16b_latest_prediction_artifact_written": self.q16b_latest_prediction_artifact_written,
            "scheduler_enabled": self.scheduler_enabled,
            "producer_enabled": self.producer_enabled,
            "runtime_artifact_write_enabled": self.runtime_artifact_write_enabled,
            "status_artifact_write_enabled": self.status_artifact_write_enabled,
            "prediction_artifact_write_enabled": self.prediction_artifact_write_enabled,
            "latest_manifest_written": self.latest_manifest_written,
            "run_sidecars_written": self.run_sidecars_written,
            "warroom_ui_trigger_enabled": self.warroom_ui_trigger_enabled,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "mode_apply_allowed": self.mode_apply_allowed,
            "parameter_apply_allowed": self.parameter_apply_allowed,
            "would_send_to_broker": self.would_send_to_broker,
        }


def _q25t_packet() -> dict[str, Any]:
    return {
        "selected_option_id": SELECTED_CADENCE_OPTION_ID,
        "selected_target_cadence_sec": SELECTED_TARGET_CADENCE_SEC,
        "preflight_only": True,
        "implementation_allowed_by_this_packet": False,
        "manual_one_shot_run_allowed": False,
        "scheduler_enablement_allowed": False,
    }


def build_prediction_warroom_single_producer_60s_disabled_validation_packet(
    *,
    q25u_skeleton_packet: Mapping[str, Any] | Any | None = None,
    q16b_default_runner_packet: Mapping[str, Any] | Any | None = None,
    request_manual_one_shot_run: bool = False,
    request_scheduler_enable: bool = False,
    request_producer_enable: bool = False,
    request_status_artifact_write: bool = False,
    request_runtime_artifact_write: bool = False,
    request_prediction_artifact_write: bool = False,
    request_latest_manifest_write: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomSingleProducer60sDisabledValidationPacket:
    skeleton = _as_mapping(q25u_skeleton_packet) or build_prediction_warroom_single_producer_60s_disabled_contract_skeleton(
        q25t_preflight_packet=_q25t_packet()
    ).to_dict()
    runner = _as_mapping(q16b_default_runner_packet) or build_prediction_warroom_non_ui_scheduled_producer_runner().to_dict()
    requested = _requested_flags(
        request_manual_one_shot_run=request_manual_one_shot_run,
        request_scheduler_enable=request_scheduler_enable,
        request_producer_enable=request_producer_enable,
        request_status_artifact_write=request_status_artifact_write,
        request_runtime_artifact_write=request_runtime_artifact_write,
        request_prediction_artifact_write=request_prediction_artifact_write,
        request_latest_manifest_write=request_latest_manifest_write,
        request_warroom_ui_trigger=request_warroom_ui_trigger,
        request_parameter_apply=request_parameter_apply,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    )
    blockers: list[str] = []
    warnings: list[str] = []
    if skeleton.get("skeleton_version") != SINGLE_PRODUCER_60S_DISABLED_CONTRACT_SKELETON_VERSION:
        blockers.append("q25u_skeleton_version_mismatch")
    if skeleton.get("selected_option_id") != SELECTED_CADENCE_OPTION_ID:
        blockers.append("q25u_selected_option_mismatch")
    if int(skeleton.get("selected_target_cadence_sec") or 0) != SELECTED_TARGET_CADENCE_SEC:
        blockers.append("q25u_selected_target_cadence_mismatch")
    if skeleton.get("ready_for_future_disabled_single_producer_60s_skeleton_validation") is not True:
        blockers.append("q25u_skeleton_not_ready_for_validation")
    for key in (
        "ready_for_manual_one_shot_run",
        "ready_for_scheduler_enablement",
        "ready_for_producer_enablement",
        "scheduler_enabled",
        "producer_enabled",
        "would_write_runtime_artifact",
        "would_write_status_artifact",
        "would_write_prediction_artifact",
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
        if skeleton.get(key) is not False:
            blockers.append("q25u_false_required:" + key)
    if runner.get("runner_version") != PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_RUNNER_VERSION:
        blockers.append("q16b_runner_version_mismatch")
    for key in (
        "producer_enabled",
        "scheduler_enabled",
        "runtime_artifact_write_enabled",
        "latest_prediction_artifact_write_enabled",
        "status_artifact_written",
        "actual_export_runner_invoked",
        "prediction_build_requested",
        "latest_prediction_artifact_written",
        "warroom_ui_trigger_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_send_to_broker",
        "ready_for_scheduler_enablement",
        "ready_for_latest_prediction_artifact_write_automation",
    ):
        if runner.get(key) is not False:
            blockers.append("q16b_false_required:" + key)
    for flag in requested:
        blockers.append("forbidden_request_in_ps_q25v:" + flag)
    ready = not blockers
    state = "single_producer_60s_disabled_validation_ready" if ready else "single_producer_60s_disabled_validation_blocked"
    return PredictionWarRoomSingleProducer60sDisabledValidationPacket(
        validation_version=SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION,
        validation_id=f"{SINGLE_PRODUCER_60S_DISABLED_VALIDATION_PACKET_VERSION}:{SELECTED_CADENCE_OPTION_ID}:{state}",
        validation_state=state,
        q25u_skeleton_packet=skeleton,
        q16b_default_runner_packet=runner,
        requested_forbidden_flags=requested,
        blocker_count=len(blockers),
        warning_count=len(warnings),
        blocked_reasons=tuple(blockers),
        warning_reasons=tuple(warnings),
        ready_for_disabled_dry_run_planning=ready,
        q16b_status_artifact_written=bool(runner.get("status_artifact_written")),
        q16b_latest_prediction_artifact_written=bool(runner.get("latest_prediction_artifact_written")),
        scheduler_enabled=bool(skeleton.get("scheduler_enabled") or runner.get("scheduler_enabled")),
        producer_enabled=bool(skeleton.get("producer_enabled") or runner.get("producer_enabled")),
        runtime_artifact_write_enabled=bool(runner.get("runtime_artifact_write_enabled")),
        status_artifact_write_enabled=bool(runner.get("status_artifact_write_enabled")),
        prediction_artifact_write_enabled=bool(runner.get("latest_prediction_artifact_write_enabled")),
        warroom_ui_trigger_enabled=bool(skeleton.get("warroom_ui_trigger_enabled") or runner.get("warroom_ui_trigger_enabled")),
        autotrade_trigger_allowed=bool(skeleton.get("autotrade_trigger_allowed") or runner.get("autotrade_trigger_allowed")),
        broker_private_api_allowed=bool(skeleton.get("broker_private_api_allowed") or runner.get("broker_private_api_allowed")),
        ledger_append_allowed=bool(skeleton.get("ledger_append_allowed") or runner.get("ledger_append_allowed")),
        parameter_apply_allowed=bool(skeleton.get("parameter_apply_allowed") or runner.get("parameter_apply_allowed")),
        would_send_to_broker=bool(skeleton.get("would_send_to_broker") or runner.get("would_send_to_broker")),
    )
