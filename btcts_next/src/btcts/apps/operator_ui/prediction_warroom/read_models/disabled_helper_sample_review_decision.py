# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/disabled_helper_sample_review_decision.py
# desc: PS-Q20K review-only decision contract for PS-Q20J disabled helper real-data dry-run sample. No runtime enablement.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

DISABLED_HELPER_SAMPLE_REVIEW_DECISION_VERSION = "prediction_warroom.disabled_helper_sample_review_decision.ps_q20k.v1"

REVIEW_SEQUENCE: Tuple[str, ...] = (
    "review_ps_q20j_sample_result_mapping_only",
    "require_sample_ready_and_hot_data_read_only",
    "require_helper_disabled_by_default",
    "require_optional_section_not_attached_by_default",
    "require_adapter_preferred_row_ready",
    "require_all_runtime_and_execution_flags_false",
    "allow_design_only_next_slice_when_review_passes",
    "keep_runtime_enablement_disallowed",
)

UNSAFE_TRUE_FIELDS: Tuple[str, ...] = (
    "target_loader_invoked",
    "runtime_loader_invoked",
    "latest_prediction_warroom_read_model_loader_changed",
    "existing_market_snapshot_replaced",
    "existing_market_state_service_changed",
    "existing_warroom_runtime_rewired",
    "component_runtime_binding_allowed",
    "ui_code_changed",
    "scheduler_enabled",
    "producer_enabled",
    "warroom_ui_trigger_enabled",
    "runtime_artifact_write_allowed",
    "prediction_artifact_write_allowed",
    "status_artifact_write_allowed",
    "view_artifact_write_allowed",
    "would_write_warroom_view_artifact",
    "ps_q19r_scoring_policy_changed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_send_to_broker",
)


@dataclass(frozen=True)
class DisabledHelperSampleReviewDecision:
    review_version: str
    review_state: str
    binding_decision: str
    runtime_enablement_decision: str
    next_allowed_lane: str
    next_slice_candidate: str
    review_sequence: Tuple[str, ...]
    sample_ok: bool
    sample_ready: bool
    hot_data_read_only: bool
    stdout_only: bool
    helper_disabled_by_default: bool
    dry_run_ready: bool
    optional_section_attached_by_default: bool
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
    decision_contract_only: bool = True
    runtime_enablement_allowed: bool = False
    loader_binding_runtime_allowed: bool = False
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


def build_disabled_helper_sample_review_decision(*, sample_result: Mapping[str, Any] | None = None) -> DisabledHelperSampleReviewDecision:
    """Return a review-only decision for a PS-Q20J sample result mapping.

    This contract never enables runtime binding. A passing review only allows another
    design/review slice; runtime UI, loader rewiring, artifact writes, AutoTrade, broker,
    and PS-Q19R changes remain disallowed.
    """

    sample = _as_mapping(sample_result)
    selected = _as_mapping(sample.get("selected_row_summary"))
    blocked: list[str] = []
    warnings: list[str] = []

    sample_ok = sample.get("ok") is True
    sample_ready = sample.get("sample_state") == "disabled_helper_real_data_dry_run_sample_ready"
    hot_data_read_only = sample.get("hot_data_read_only") is True
    stdout_only = sample.get("stdout_only") is True
    helper_disabled = sample.get("helper_disabled_by_default") is True and sample.get("helper_state") == "explicit_read_only_loader_binding_helper_disabled"
    dry_run_ready = sample.get("dry_run_ready") is True
    optional_attached = sample.get("optional_section_attached") is True or sample.get("output_model_has_optional_section") is True
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
    if not helper_disabled:
        blocked.append("helper_not_disabled_by_default_in_sample")
    if not dry_run_ready:
        blocked.append("dry_run_not_ready")
    if optional_attached:
        blocked.append("optional_section_attached_in_default_sample")
    if not adapter_ready:
        blocked.append("adapter_not_ready_for_warroom_read")
    if unsafe:
        blocked.append("unsafe_runtime_or_execution_flag_true")

    warnings.extend(str(item) for item in sample.get("warning_reasons", []) if isinstance(sample.get("warning_reasons"), list))
    if adapter_ready and _as_int(sample.get("adapter_diagnostic_transition_count")) > 0:
        warnings.append("diagnostic_transition_rows_present_but_review_only")
    if dry_run_ready:
        warnings.append("dry_run_ready_does_not_permit_runtime_enablement")

    passed = not blocked
    review_state = "disabled_helper_sample_review_passed" if passed else "disabled_helper_sample_review_blocked"
    binding_decision = "allow_design_only_disabled_binding_plan" if passed else "block_binding_plan_until_sample_review_passes"

    return DisabledHelperSampleReviewDecision(
        review_version=DISABLED_HELPER_SAMPLE_REVIEW_DECISION_VERSION,
        review_state=review_state,
        binding_decision=binding_decision,
        runtime_enablement_decision="runtime_enablement_disallowed",
        next_allowed_lane="design_review_only" if passed else "blocked",
        next_slice_candidate="PS-Q20L_DISABLED_BINDING_PLAN_NO_RUNTIME_ENABLEMENT" if passed else "PS-Q20J_SAMPLE_REPAIR_OR_RERUN",
        review_sequence=REVIEW_SEQUENCE,
        sample_ok=sample_ok,
        sample_ready=sample_ready,
        hot_data_read_only=hot_data_read_only,
        stdout_only=stdout_only,
        helper_disabled_by_default=helper_disabled,
        dry_run_ready=dry_run_ready,
        optional_section_attached_by_default=optional_attached,
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
