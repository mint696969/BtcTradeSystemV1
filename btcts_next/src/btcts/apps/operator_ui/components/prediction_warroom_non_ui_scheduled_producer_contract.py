# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py
# desc: PS-Q16A contract-only design packet for a future disabled-by-default non-UI scheduled Prediction producer. Declares cadence, status visibility, accuracy review, and disable/rollback boundaries; performs no IO, scheduling, runtime writes, parameter mutation, AutoTrade, broker, approval, or ledger behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Tuple

PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_CONTRACT_VERSION = (
    "prediction_warroom_non_ui_scheduled_producer_contract.ps_q16a.v1"
)

LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH = "prediction/latest_prediction_system_result.json"
PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH = "prediction/status/non_ui_scheduled_producer_status.json"
FRESHNESS_MAX_AGE_SEC = 3600
FRESHNESS_WARNING_AGE_SEC = 900
RECOMMENDED_CADENCE_SEC = 300
MINIMUM_CADENCE_SEC = 60
MAXIMUM_CADENCE_SEC = 900

PRODUCER_CONTRACT_SEQUENCE: Tuple[str, ...] = (
    "declare_disabled_by_default_non_ui_prediction_producer_contract",
    "declare_latest_prediction_artifact_target_without_writing_it",
    "declare_status_artifact_schema_without_writing_it",
    "declare_freshness_policy_for_warroom_realtime_observation",
    "declare_operator_visibility_for_last_run_last_success_last_failure_warnings_safe_flags",
    "declare_accuracy_adjustment_review_surface_as_proposal_only",
    "declare_rollback_disable_path_before_scheduler_enablement",
    "return_contract_packet_only",
    "do_not_enable_scheduler_in_ps_q16a",
    "do_not_enable_runtime_artifact_write_automation_in_ps_q16a",
    "do_not_trigger_from_warroom_ui",
    "do_not_apply_or_stage_parameters",
    "do_not_append_approval_decision_or_command_ledgers",
    "do_not_trigger_autotrade_or_broker",
)

REQUIRED_STATUS_FIELDS: Tuple[str, ...] = (
    "producer_version",
    "producer_state",
    "producer_enabled",
    "scheduler_enabled",
    "runtime_artifact_write_enabled",
    "latest_prediction_artifact_relative_path",
    "status_artifact_relative_path",
    "freshness_max_age_sec",
    "recommended_cadence_sec",
    "last_run_started_at",
    "last_run_finished_at",
    "last_success_at",
    "last_failure_at",
    "last_success_generated_at",
    "last_prediction_run_id",
    "last_target_file_size_bytes",
    "last_warning_count",
    "last_blocker_count",
    "consecutive_failure_count",
    "safe_flags",
    "warnings",
    "blockers",
    "disable_rollback_state",
)

FORBIDDEN_ENABLEMENT_REQUESTS: Tuple[str, ...] = (
    "request_scheduler_enable",
    "request_runtime_artifact_write_enable",
    "request_producer_enable",
    "request_warroom_ui_trigger",
    "request_parameter_apply",
    "request_parameter_staging_write",
    "request_approval_or_ledger_or_autotrade_or_broker",
)

SAFE_FLAG_KEYS: Tuple[str, ...] = (
    "non_ui_only_true",
    "warroom_ui_trigger_false",
    "scheduler_enabled_false",
    "runtime_artifact_write_enabled_false",
    "producer_enabled_false",
    "approval_or_authorization_allowed_false",
    "ledger_append_allowed_false",
    "autotrade_trigger_allowed_false",
    "broker_private_api_allowed_false",
    "parameter_apply_allowed_false",
    "parameter_staging_write_allowed_false",
    "would_send_to_broker_false",
    "would_write_collector_state_false",
)

ACCURACY_REVIEW_CANDIDATES: Tuple[str, ...] = (
    "source_quality_cap_review",
    "signal_strength_band_calibration_review",
    "warning_to_blocker_threshold_review",
    "horizon_family_weight_review",
    "replay_outcome_calibration_review",
)


@dataclass(frozen=True)
class PredictionProducerCadencePolicy:
    freshness_max_age_sec: int = FRESHNESS_MAX_AGE_SEC
    freshness_warning_age_sec: int = FRESHNESS_WARNING_AGE_SEC
    recommended_cadence_sec: int = RECOMMENDED_CADENCE_SEC
    minimum_cadence_sec: int = MINIMUM_CADENCE_SEC
    maximum_cadence_sec: int = MAXIMUM_CADENCE_SEC
    cadence_policy_state: str = "declared_not_enabled"
    overrun_policy: str = "skip_or_fail_closed; never_overlap_runs"
    stale_policy: str = "WarRoom must show stale/blocker instead of force-ready"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionProducerStatusVisibilityContract:
    status_artifact_relative_path: str = PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    latest_prediction_artifact_relative_path: str = LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH
    required_status_fields: Tuple[str, ...] = REQUIRED_STATUS_FIELDS
    safe_flag_keys: Tuple[str, ...] = SAFE_FLAG_KEYS
    visibility_state: str = "status_schema_declared_not_written"
    warroom_observation_mode: str = "read_only_status_and_latest_prediction_observation"
    missing_status_behavior: str = "show_not_configured; do_not_block_existing_latest_prediction_read"
    failure_visibility_required: bool = True
    warnings_visible: bool = True
    blockers_visible: bool = True
    safe_flags_visible: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status_artifact_relative_path": self.status_artifact_relative_path,
            "latest_prediction_artifact_relative_path": self.latest_prediction_artifact_relative_path,
            "required_status_fields": list(self.required_status_fields),
            "safe_flag_keys": list(self.safe_flag_keys),
            "visibility_state": self.visibility_state,
            "warroom_observation_mode": self.warroom_observation_mode,
            "missing_status_behavior": self.missing_status_behavior,
            "failure_visibility_required": self.failure_visibility_required,
            "warnings_visible": self.warnings_visible,
            "blockers_visible": self.blockers_visible,
            "safe_flags_visible": self.safe_flags_visible,
        }


@dataclass(frozen=True)
class PredictionAccuracyAdjustmentReviewContract:
    review_state: str = "proposal_only_no_apply_no_staging_write"
    review_candidates: Tuple[str, ...] = ACCURACY_REVIEW_CANDIDATES
    warroom_display_purpose: str = "operator can review accuracy/calibration candidates while predictions update"
    apply_allowed: bool = False
    staging_write_allowed: bool = False
    live_parameter_mutation_allowed: bool = False
    parameter_version_append_allowed: bool = False
    human_review_required_before_any_future_apply: bool = True
    replay_or_shadow_evidence_required_before_any_future_apply: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "review_state": self.review_state,
            "review_candidates": list(self.review_candidates),
            "warroom_display_purpose": self.warroom_display_purpose,
            "apply_allowed": self.apply_allowed,
            "staging_write_allowed": self.staging_write_allowed,
            "live_parameter_mutation_allowed": self.live_parameter_mutation_allowed,
            "parameter_version_append_allowed": self.parameter_version_append_allowed,
            "human_review_required_before_any_future_apply": self.human_review_required_before_any_future_apply,
            "replay_or_shadow_evidence_required_before_any_future_apply": self.replay_or_shadow_evidence_required_before_any_future_apply,
        }


@dataclass(frozen=True)
class PredictionProducerDisableRollbackContract:
    disable_state: str = "disable_path_required_before_enablement"
    default_enabled: bool = False
    rollback_action: str = "disable_scheduler_or_runner; WarRoom continues read-only observation of last artifact/status"
    rollback_does_not_delete_latest_prediction_artifact: bool = True
    rollback_does_not_force_ready: bool = True
    rollback_does_not_mutate_parameters: bool = True
    rollback_requires_operator_visibility: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionWarRoomNonUiScheduledProducerContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    contract_sequence: Tuple[str, ...] = PRODUCER_CONTRACT_SEQUENCE
    latest_prediction_artifact_relative_path: str = LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH
    status_artifact_relative_path: str = PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH
    cadence_policy: Mapping[str, Any] = field(default_factory=dict)
    status_visibility_contract: Mapping[str, Any] = field(default_factory=dict)
    accuracy_adjustment_review_contract: Mapping[str, Any] = field(default_factory=dict)
    disable_rollback_contract: Mapping[str, Any] = field(default_factory=dict)
    latest_prediction_source_adapter_present: bool = False
    latest_prediction_review_ready: bool = False
    latest_prediction_generated_at: str = ""
    latest_prediction_run_id: str = ""
    latest_prediction_warning_count: int = 0
    latest_prediction_blocker_count: int = 0
    producer_status_artifact_supplied: bool = False
    producer_status_required_field_count: int = 0
    producer_status_missing_fields: Tuple[str, ...] = ()
    producer_status_extra_fields: Tuple[str, ...] = ()
    human_approval_record_present: bool = False
    ready_for_next_disabled_runner_slice: bool = False
    ready_for_scheduler_enablement: bool = False
    ready_for_runtime_artifact_write_automation_enablement: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    requested_enablement_flags: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    guard_only: bool = True
    visibility_design_required: bool = True
    non_ui_only: bool = True
    producer_enabled: bool = False
    scheduler_enabled: bool = False
    runtime_artifact_write_enabled: bool = False
    warroom_ui_trigger_enabled: bool = False
    warroom_status_display_allowed_future_slice: bool = True
    streamlit_import_required: bool = False
    streamlit_render_performed_by_this_contract: bool = False
    ui_controls_added: bool = False
    ui_triggered_runner_execution: bool = False
    would_read_runtime_file: bool = False
    would_decode_payload: bool = False
    would_write_runtime_artifact: bool = False
    would_write_status_artifact: bool = False
    would_write_collector_state: bool = False
    would_mutate_live_parameters: bool = False
    would_append_parameter_version: bool = False
    would_append_ledger: bool = False
    would_send_to_broker: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    parameter_apply_allowed: bool = False
    parameter_staging_write_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "contract_state": self.contract_state,
            "contract_sequence": list(self.contract_sequence),
            "latest_prediction_artifact_relative_path": self.latest_prediction_artifact_relative_path,
            "status_artifact_relative_path": self.status_artifact_relative_path,
            "cadence_policy": dict(self.cadence_policy),
            "status_visibility_contract": dict(self.status_visibility_contract),
            "accuracy_adjustment_review_contract": dict(self.accuracy_adjustment_review_contract),
            "disable_rollback_contract": dict(self.disable_rollback_contract),
            "latest_prediction_source_adapter_present": self.latest_prediction_source_adapter_present,
            "latest_prediction_review_ready": self.latest_prediction_review_ready,
            "latest_prediction_generated_at": self.latest_prediction_generated_at,
            "latest_prediction_run_id": self.latest_prediction_run_id,
            "latest_prediction_warning_count": self.latest_prediction_warning_count,
            "latest_prediction_blocker_count": self.latest_prediction_blocker_count,
            "producer_status_artifact_supplied": self.producer_status_artifact_supplied,
            "producer_status_required_field_count": self.producer_status_required_field_count,
            "producer_status_missing_fields": list(self.producer_status_missing_fields),
            "producer_status_extra_fields": list(self.producer_status_extra_fields),
            "human_approval_record_present": self.human_approval_record_present,
            "ready_for_next_disabled_runner_slice": self.ready_for_next_disabled_runner_slice,
            "ready_for_scheduler_enablement": self.ready_for_scheduler_enablement,
            "ready_for_runtime_artifact_write_automation_enablement": self.ready_for_runtime_artifact_write_automation_enablement,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "requested_enablement_flags": list(self.requested_enablement_flags),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "guard_only": self.guard_only,
            "visibility_design_required": self.visibility_design_required,
            "non_ui_only": self.non_ui_only,
            "producer_enabled": self.producer_enabled,
            "scheduler_enabled": self.scheduler_enabled,
            "runtime_artifact_write_enabled": self.runtime_artifact_write_enabled,
            "warroom_ui_trigger_enabled": self.warroom_ui_trigger_enabled,
            "warroom_status_display_allowed_future_slice": self.warroom_status_display_allowed_future_slice,
            "streamlit_import_required": self.streamlit_import_required,
            "streamlit_render_performed_by_this_contract": self.streamlit_render_performed_by_this_contract,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_runner_execution": self.ui_triggered_runner_execution,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_decode_payload": self.would_decode_payload,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_status_artifact": self.would_write_status_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_mutate_live_parameters": self.would_mutate_live_parameters,
            "would_append_parameter_version": self.would_append_parameter_version,
            "would_append_ledger": self.would_append_ledger,
            "would_send_to_broker": self.would_send_to_broker,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "parameter_apply_allowed": self.parameter_apply_allowed,
            "parameter_staging_write_allowed": self.parameter_staging_write_allowed,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _nested(mapping: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = mapping.get(key)
    return value if isinstance(value, Mapping) else {}


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _requested_flags(**flags: bool) -> tuple[str, ...]:
    return tuple(name for name, requested in flags.items() if requested)


def _status_missing_fields(status: Mapping[str, Any]) -> tuple[str, ...]:
    if not status:
        return tuple()
    return tuple(field for field in REQUIRED_STATUS_FIELDS if field not in status)


def _status_extra_fields(status: Mapping[str, Any]) -> tuple[str, ...]:
    if not status:
        return tuple()
    required = set(REQUIRED_STATUS_FIELDS)
    return tuple(str(field) for field in status.keys() if str(field) not in required)


def _latest_source(adapter_packet: Mapping[str, Any]) -> tuple[bool, bool, str, str, int, int]:
    if not adapter_packet:
        return False, False, "", "", 0, 0
    summary = _nested(adapter_packet, "source_summary")
    return (
        True,
        adapter_packet.get("adapter_state") == "latest_prediction_source_ready"
        and adapter_packet.get("review_packet_ready") is True,
        str(summary.get("generated_at") or adapter_packet.get("generated_at") or ""),
        str(summary.get("prediction_run_id") or adapter_packet.get("prediction_run_id") or ""),
        _int(adapter_packet.get("warning_count")),
        _int(adapter_packet.get("blocker_count")),
    )


def build_prediction_warroom_non_ui_scheduled_producer_contract(
    *,
    latest_prediction_source_adapter_packet: Mapping[str, Any] | Any | None = None,
    producer_status_artifact: Mapping[str, Any] | Any | None = None,
    human_approval_record_present: bool = False,
    request_scheduler_enable: bool = False,
    request_runtime_artifact_write_enable: bool = False,
    request_producer_enable: bool = False,
    request_warroom_ui_trigger: bool = False,
    request_parameter_apply: bool = False,
    request_parameter_staging_write: bool = False,
    request_approval_or_ledger_or_autotrade_or_broker: bool = False,
) -> PredictionWarRoomNonUiScheduledProducerContractPacket:
    """Return the PS-Q16A design contract for future realtime WarRoom observation.

    This function intentionally performs no IO and never enables scheduling, producer loops,
    runtime artifact writes, parameter application/staging, AutoTrade, broker/private API,
    approvals, or ledger append behavior.
    """
    requested = _requested_flags(
        request_scheduler_enable=request_scheduler_enable,
        request_runtime_artifact_write_enable=request_runtime_artifact_write_enable,
        request_producer_enable=request_producer_enable,
        request_warroom_ui_trigger=request_warroom_ui_trigger,
        request_parameter_apply=request_parameter_apply,
        request_parameter_staging_write=request_parameter_staging_write,
        request_approval_or_ledger_or_autotrade_or_broker=request_approval_or_ledger_or_autotrade_or_broker,
    )
    blockers = [f"forbidden_enablement_in_ps_q16a:{item}" for item in requested]
    warnings: list[str] = []
    adapter = _as_mapping(latest_prediction_source_adapter_packet)
    status = _as_mapping(producer_status_artifact)
    latest_present, latest_ready, generated_at, run_id, warning_count, blocker_count = _latest_source(adapter)
    if not latest_present:
        warnings.append("latest_prediction_source_adapter_not_supplied_for_design_context")
    elif not latest_ready:
        warnings.append("latest_prediction_source_not_ready_in_design_context")
    missing_fields = _status_missing_fields(status)
    extra_fields = _status_extra_fields(status)
    if not status:
        warnings.append("producer_status_artifact_not_supplied_yet_expected_before_warroom_status_display")
    elif missing_fields:
        blockers.append("producer_status_artifact_missing_required_fields")

    cadence = PredictionProducerCadencePolicy().to_dict()
    visibility = PredictionProducerStatusVisibilityContract().to_dict()
    accuracy = PredictionAccuracyAdjustmentReviewContract().to_dict()
    rollback = PredictionProducerDisableRollbackContract().to_dict()
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    state = (
        "non_ui_scheduled_producer_contract_ready_for_disabled_runner_slice"
        if not unique_blockers
        else "non_ui_scheduled_producer_contract_blocked"
    )
    return PredictionWarRoomNonUiScheduledProducerContractPacket(
        contract_version=PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_CONTRACT_VERSION,
        contract_id=f"{PREDICTION_WARROOM_NON_UI_SCHEDULED_PRODUCER_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        cadence_policy=cadence,
        status_visibility_contract=visibility,
        accuracy_adjustment_review_contract=accuracy,
        disable_rollback_contract=rollback,
        latest_prediction_source_adapter_present=latest_present,
        latest_prediction_review_ready=latest_ready,
        latest_prediction_generated_at=generated_at,
        latest_prediction_run_id=run_id,
        latest_prediction_warning_count=warning_count,
        latest_prediction_blocker_count=blocker_count,
        producer_status_artifact_supplied=bool(status),
        producer_status_required_field_count=len(REQUIRED_STATUS_FIELDS),
        producer_status_missing_fields=missing_fields,
        producer_status_extra_fields=extra_fields,
        human_approval_record_present=human_approval_record_present,
        ready_for_next_disabled_runner_slice=not unique_blockers,
        ready_for_scheduler_enablement=False,
        ready_for_runtime_artifact_write_automation_enablement=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        requested_enablement_flags=requested,
    )

# PS-Q25K planning-only cadence/freshness gap packet. This is intentionally appended
# to the PS-Q16A contract module without enabling producer cadence, scheduler, or writes.
PREDICTION_WARROOM_PRODUCER_CADENCE_GAP_PLAN_VERSION = (
    "prediction_warroom.producer_cadence_gap_planning.ps_q25k.v1"
)

HORIZON_CADENCE_PLANNING_TARGETS: Tuple[Mapping[str, Any], ...] = (
    {"horizon_label": "15s", "horizon_sec": 15, "desired_max_age_sec": 15, "candidate_generation_cadence_sec": 15, "purpose": "micro tactical visibility"},
    {"horizon_label": "60s", "horizon_sec": 60, "desired_max_age_sec": 30, "candidate_generation_cadence_sec": 30, "purpose": "short tactical visibility"},
    {"horizon_label": "300s", "horizon_sec": 300, "desired_max_age_sec": 90, "candidate_generation_cadence_sec": 60, "purpose": "5m tactical visibility"},
    {"horizon_label": "900s", "horizon_sec": 900, "desired_max_age_sec": 300, "candidate_generation_cadence_sec": 300, "purpose": "15m tactical/context visibility"},
    {"horizon_label": "1800s", "horizon_sec": 1800, "desired_max_age_sec": 600, "candidate_generation_cadence_sec": 600, "purpose": "30m context visibility"},
    {"horizon_label": "3600s", "horizon_sec": 3600, "desired_max_age_sec": 900, "candidate_generation_cadence_sec": 900, "purpose": "1h context visibility"},
)


def _cadence_gap_row(target: Mapping[str, Any], *, baseline_cadence_sec: int) -> dict[str, Any]:
    horizon_sec = _int(target.get("horizon_sec"))
    desired_age = _int(target.get("desired_max_age_sec"))
    candidate = _int(target.get("candidate_generation_cadence_sec"))
    baseline_supports = bool(baseline_cadence_sec <= desired_age)
    needs_faster = bool(not baseline_supports)
    return {
        "horizon_label": str(target.get("horizon_label") or f"{horizon_sec}s"),
        "horizon_sec": horizon_sec,
        "purpose": str(target.get("purpose") or ""),
        "desired_max_age_sec": desired_age,
        "current_contract_recommended_cadence_sec": baseline_cadence_sec,
        "candidate_generation_cadence_sec": candidate,
        "baseline_supports_horizon_freshness": baseline_supports,
        "needs_faster_than_current_contract": needs_faster,
        "planning_note": (
            "current_contract_cadence_too_slow_for_this_horizon" if needs_faster else "current_contract_cadence_can_support_this_horizon"
        ),
    }


def build_prediction_warroom_producer_cadence_gap_plan(
    *,
    baseline_cadence_sec: int = RECOMMENDED_CADENCE_SEC,
    request_producer_cadence_change: bool = False,
    request_scheduler_action_change: bool = False,
    request_runtime_artifact_write_enable: bool = False,
    request_status_artifact_write_enable: bool = False,
    request_prediction_artifact_write_enable: bool = False,
    explicit_human_gate_granted: bool = False,
) -> dict[str, Any]:
    """Return a planning-only cadence/freshness gap packet for WarRoom prediction display.

    The packet does not change scheduler actions, producer cadence, or artifacts. It only
    documents which horizons would require a future explicitly gated cadence discussion.
    """
    baseline = max(1, _int(baseline_cadence_sec) or RECOMMENDED_CADENCE_SEC)
    rows = [_cadence_gap_row(target, baseline_cadence_sec=baseline) for target in HORIZON_CADENCE_PLANNING_TARGETS]
    short_horizon_gap_count = sum(1 for row in rows if row["horizon_sec"] <= 300 and row["needs_faster_than_current_contract"] is True)
    requested_dangerous = {
        "request_producer_cadence_change": bool(request_producer_cadence_change),
        "request_scheduler_action_change": bool(request_scheduler_action_change),
        "request_runtime_artifact_write_enable": bool(request_runtime_artifact_write_enable),
        "request_status_artifact_write_enable": bool(request_status_artifact_write_enable),
        "request_prediction_artifact_write_enable": bool(request_prediction_artifact_write_enable),
    }
    requested_flags = [name for name, value in requested_dangerous.items() if value]
    blocked_reasons = [f"explicit_gate_required_before:{name}" for name in requested_flags]
    if requested_flags and not explicit_human_gate_granted:
        planning_state = "blocked_dangerous_request_without_explicit_gate"
    else:
        planning_state = "planning_only_ready"
    return {
        "cadence_gap_plan_version": PREDICTION_WARROOM_PRODUCER_CADENCE_GAP_PLAN_VERSION,
        "planning_state": planning_state,
        "planning_only": True,
        "read_only": True,
        "non_executing": True,
        "contract_only": True,
        "display_only": True,
        "human_gate_required_before_any_change": True,
        "explicit_human_gate_granted": bool(explicit_human_gate_granted),
        "current_contract_recommended_cadence_sec": baseline,
        "current_contract_minimum_cadence_sec": MINIMUM_CADENCE_SEC,
        "current_contract_maximum_cadence_sec": MAXIMUM_CADENCE_SEC,
        "freshness_warning_age_sec": FRESHNESS_WARNING_AGE_SEC,
        "freshness_max_age_sec": FRESHNESS_MAX_AGE_SEC,
        "horizon_cadence_gap_rows": rows,
        "horizon_cadence_gap_row_count": len(rows),
        "short_horizon_gap_count": short_horizon_gap_count,
        "short_horizon_freshness_gap_present": short_horizon_gap_count > 0,
        "recommended_next_step": "operator_review_then_explicit_gate_before_any_producer_or_scheduler_change",
        "requested_dangerous_flags": requested_flags,
        "blocked_reasons": blocked_reasons,
        "blocker_count": len(blocked_reasons),
        "producer_cadence_changed": False,
        "scheduler_action_changed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "latest_manifest_written": False,
        "run_sidecars_written": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }

