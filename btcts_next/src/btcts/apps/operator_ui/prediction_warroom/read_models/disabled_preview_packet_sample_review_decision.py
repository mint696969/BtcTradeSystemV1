# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/disabled_preview_packet_sample_review_decision.py
# desc: PS-Q20O review-only decision for the PS-Q20N disabled preview packet real-data sample. Stop recommended; no runtime enablement.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

DISABLED_PREVIEW_PACKET_SAMPLE_REVIEW_DECISION_VERSION = "prediction_warroom.disabled_preview_packet_sample_review_decision.ps_q20o.v1"

REVIEW_SEQUENCE: Tuple[str, ...] = (
    "review_ps_q20n_sample_result_mapping_only",
    "require_sample_ready_and_stdout_only",
    "require_hot_data_read_only",
    "require_preview_packet_ready",
    "require_helper_disabled_and_optional_section_unattached",
    "require_plan_ready_and_no_runtime_enablement",
    "require_all_runtime_execution_and_artifact_flags_false",
    "recommend_stop_after_successful_sample",
    "allow_only_handoff_or_review_only_next_slice_if_continuing",
)

UNSAFE_TRUE_FIELDS: Tuple[str, ...] = (
    "runtime_enablement_allowed",
    "loader_binding_runtime_allowed",
    "target_loader_invoked",
    "runtime_loader_invoked",
    "latest_prediction_warroom_read_model_loader_changed",
    "existing_market_snapshot_replaced",
    "existing_market_state_service_changed",
    "existing_warroom_runtime_rewired",
    "component_runtime_binding_allowed",
    "ui_code_changed",
    "warroom_ui_trigger_enabled",
    "scheduler_enabled",
    "producer_enabled",
    "runtime_artifact_write_allowed",
    "prediction_artifact_write_allowed",
    "status_artifact_write_allowed",
    "view_artifact_write_allowed",
    "would_write_warroom_view_artifact",
    "ps_q19r_scoring_policy_changed",
    "collector_runtime_behavior_changed",
    "market_state_writer_changed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "parameter_apply_allowed",
    "parameter_staging_write_allowed",
    "would_send_to_broker",
)


@dataclass(frozen=True)
class DisabledPreviewPacketSampleReviewDecision:
    review_version: str
    review_state: str
    stop_or_next_decision: str
    runtime_enablement_decision: str
    next_allowed_lane: str
    next_slice_candidate: str
    review_sequence: Tuple[str, ...]
    sample_ok: bool
    sample_ready: bool
    hot_data_read_only: bool
    stdout_only: bool
    preview_ready: bool
    preview_packet_only: bool
    supplied_mappings_only: bool
    default_disabled_preview: bool
    plan_ready: bool
    helper_disabled: bool
    helper_dry_run_ready: bool
    optional_section_attached: bool
    output_model_has_optional_section: bool
    adapter_ready: bool
    adapter_consumer_preferred_count: int
    adapter_diagnostic_transition_count: int
    selected_row_trust_state: str
    selected_row_interpretation_bucket: str
    selected_row_semantic_observer_status: str
    selected_row_spread: Any
    unsafe_true_fields: Tuple[str, ...]
    blocked_reasons: Tuple[str, ...]
    warning_reasons: Tuple[str, ...]
    review_only: bool = True
    sample_review_only: bool = True
    stop_recommended: bool = True
    continue_only_as_handoff_or_review: bool = True
    runtime_enablement_allowed: bool = False
    loader_binding_runtime_allowed: bool = False
    target_loader_invoked: bool = False
    runtime_loader_invoked: bool = False
    latest_prediction_warroom_read_model_loader_changed: bool = False
    existing_market_snapshot_replaced: bool = False
    existing_market_state_service_changed: bool = False
    existing_warroom_runtime_rewired: bool = False
    component_runtime_binding_allowed: bool = False
    ui_code_changed: bool = False
    warroom_ui_trigger_enabled: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    runtime_artifact_write_allowed: bool = False
    prediction_artifact_write_allowed: bool = False
    status_artifact_write_allowed: bool = False
    view_artifact_write_allowed: bool = False
    would_write_warroom_view_artifact: bool = False
    ps_q19r_scoring_policy_changed: bool = False
    collector_runtime_behavior_changed: bool = False
    market_state_writer_changed: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    parameter_apply_allowed: bool = False
    parameter_staging_write_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["review_sequence"] = list(self.review_sequence)
        data["unsafe_true_fields"] = list(self.unsafe_true_fields)
        data["blocked_reasons"] = list(self.blocked_reasons)
        data["warning_reasons"] = list(self.warning_reasons)
        return data


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def build_disabled_preview_packet_sample_review_decision(
    *,
    sample_result: Mapping[str, Any] | None = None,
) -> DisabledPreviewPacketSampleReviewDecision:
    """Return a review-only stop-or-next decision for a PS-Q20N sample result.

    A passing review recommends stopping after the successful disabled preview sample. If work
    continues, only handoff/review-only slices are allowed; runtime binding remains disallowed.
    """

    sample = _as_mapping(sample_result)
    selected = _as_mapping(sample.get("selected_row_summary"))
    blocked: list[str] = []
    warnings: list[str] = []

    sample_ok = sample.get("ok") is True
    sample_ready = sample.get("sample_state") == "disabled_preview_packet_real_data_sample_ready"
    hot_data_read_only = sample.get("hot_data_read_only") is True
    stdout_only = sample.get("stdout_only") is True
    preview_ready = sample.get("preview_state") == "disabled_binding_plan_preview_packet_ready"
    preview_packet_only = sample.get("preview_packet_only") is True
    supplied_mappings_only = sample.get("supplied_mappings_only") is True
    default_disabled_preview = sample.get("default_disabled_preview") is True
    plan_ready = sample.get("plan_ready") is True and sample.get("plan_state") == "disabled_binding_plan_ready"
    helper_disabled = sample.get("helper_state") == "explicit_read_only_loader_binding_helper_disabled"
    helper_dry_run_ready = sample.get("helper_dry_run_ready") is True
    optional_attached = sample.get("optional_section_attached") is True
    output_has_optional = sample.get("output_model_has_optional_section") is True
    adapter_ready = sample.get("adapter_state") == "preferred_row_adapter_ready" and sample.get("adapter_allowed_for_requested_lane") is True and sample.get("adapter_selected_row_available") is True
    unsafe = tuple(name for name in UNSAFE_TRUE_FIELDS if sample.get(name) is True)

    if not sample:
        blocked.append("sample_result_missing")
    if not sample_ok or not sample_ready:
        blocked.append("sample_result_not_ready")
    if not hot_data_read_only:
        blocked.append("sample_not_hot_data_read_only")
    if not stdout_only:
        blocked.append("sample_not_stdout_only")
    if not preview_ready or not preview_packet_only:
        blocked.append("preview_packet_not_ready")
    if not supplied_mappings_only:
        blocked.append("preview_not_supplied_mappings_only")
    if not default_disabled_preview:
        blocked.append("preview_not_default_disabled")
    if not plan_ready:
        blocked.append("disabled_plan_not_ready")
    if not helper_disabled:
        blocked.append("helper_not_disabled")
    if not helper_dry_run_ready:
        blocked.append("helper_dry_run_not_ready")
    if optional_attached or output_has_optional:
        blocked.append("optional_section_attached_in_sample")
    if not adapter_ready:
        blocked.append("adapter_not_ready")
    if unsafe:
        blocked.append("unsafe_runtime_or_execution_flag_true")

    values = sample.get("warning_reasons")
    if isinstance(values, list):
        warnings.extend(str(item) for item in values)
    if adapter_ready and _as_int(sample.get("adapter_diagnostic_transition_count")) > 0:
        warnings.append("diagnostic_transition_rows_present_but_review_only")
    if preview_ready:
        warnings.append("preview_ready_does_not_permit_runtime_enablement")
    if sample_ok:
        warnings.append("successful_sample_recommends_stop_or_handoff_only")

    passed = not blocked
    return DisabledPreviewPacketSampleReviewDecision(
        review_version=DISABLED_PREVIEW_PACKET_SAMPLE_REVIEW_DECISION_VERSION,
        review_state="disabled_preview_packet_sample_review_passed" if passed else "disabled_preview_packet_sample_review_blocked",
        stop_or_next_decision="stop_recommended_or_continue_handoff_review_only" if passed else "block_until_sample_review_passes",
        runtime_enablement_decision="runtime_enablement_disallowed",
        next_allowed_lane="handoff_or_review_only" if passed else "blocked",
        next_slice_candidate="PS-Q20P_DISABLED_PREVIEW_PACKET_HANDOFF_SUMMARY_NO_RUNTIME" if passed else "PS-Q20N_SAMPLE_REPAIR_OR_RERUN",
        review_sequence=REVIEW_SEQUENCE,
        sample_ok=sample_ok,
        sample_ready=sample_ready,
        hot_data_read_only=hot_data_read_only,
        stdout_only=stdout_only,
        preview_ready=preview_ready,
        preview_packet_only=preview_packet_only,
        supplied_mappings_only=supplied_mappings_only,
        default_disabled_preview=default_disabled_preview,
        plan_ready=plan_ready,
        helper_disabled=helper_disabled,
        helper_dry_run_ready=helper_dry_run_ready,
        optional_section_attached=optional_attached,
        output_model_has_optional_section=output_has_optional,
        adapter_ready=adapter_ready,
        adapter_consumer_preferred_count=_as_int(sample.get("adapter_consumer_preferred_count")),
        adapter_diagnostic_transition_count=_as_int(sample.get("adapter_diagnostic_transition_count")),
        selected_row_trust_state=str(selected.get("trust_state") or ""),
        selected_row_interpretation_bucket=str(selected.get("interpretation_bucket") or ""),
        selected_row_semantic_observer_status=str(selected.get("semantic_observer_status") or ""),
        selected_row_spread=selected.get("spread"),
        unsafe_true_fields=unsafe,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warning_reasons=tuple(dict.fromkeys(warnings)),
    )
