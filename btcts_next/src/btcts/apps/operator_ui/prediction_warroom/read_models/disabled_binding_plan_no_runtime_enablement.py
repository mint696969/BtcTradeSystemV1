# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/disabled_binding_plan_no_runtime_enablement.py
# desc: PS-Q20L plan-only disabled binding plan. No runtime enablement, loader rewire, UI binding, or artifact writes.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

DISABLED_BINDING_PLAN_VERSION = "prediction_warroom.disabled_binding_plan_no_runtime_enablement.ps_q20l.v1"

PLAN_SEQUENCE: Tuple[str, ...] = (
    "accept_ps_q20k_review_decision_mapping_only",
    "require_review_passed",
    "require_design_review_only_lane",
    "require_runtime_enablement_disallowed",
    "plan_disabled_binding_contract_only",
    "preserve_existing_latest_prediction_warroom_loader",
    "preserve_existing_market_snapshot_and_market_state_service",
    "preserve_ui_producer_scheduler_artifact_and_execution_boundaries",
    "return_plan_packet_only",
)

PLAN_ITEMS: Tuple[str, ...] = (
    "keep_latest_prediction_warroom_read_model_loader_unchanged",
    "keep_explicit_read_only_loader_binding_helper_disabled_by_default",
    "permit_only_manual_supplied_mapping_preview_in_future_slice",
    "require_future_runtime_binding_slice_to_start_from_new_explicit_approval",
    "require_close_guard_before_any_runtime_design_change",
    "keep_prediction_artifact_and_warroom_view_artifact_write_disallowed",
    "keep_ps_q19r_scoring_and_autotrade_broker_paths_disallowed",
)

UNSAFE_TRUE_FIELDS: Tuple[str, ...] = (
    "runtime_enablement_allowed",
    "loader_binding_runtime_allowed",
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
class DisabledBindingPlanNoRuntimeEnablement:
    plan_version: str
    plan_state: str
    plan_decision: str
    review_state: str
    binding_decision: str
    runtime_enablement_decision: str
    next_allowed_lane: str
    next_slice_candidate: str
    plan_sequence: Tuple[str, ...]
    plan_items: Tuple[str, ...]
    review_passed: bool
    design_review_only_lane: bool
    runtime_enablement_disallowed: bool
    loader_binding_runtime_disallowed: bool
    unsafe_true_fields: Tuple[str, ...]
    blocked_reasons: Tuple[str, ...]
    warning_reasons: Tuple[str, ...]
    plan_only: bool = True
    disabled_binding_plan_only: bool = True
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
        data["plan_sequence"] = list(self.plan_sequence)
        data["plan_items"] = list(self.plan_items)
        data["unsafe_true_fields"] = list(self.unsafe_true_fields)
        data["blocked_reasons"] = list(self.blocked_reasons)
        data["warning_reasons"] = list(self.warning_reasons)
        return data


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_disabled_binding_plan_no_runtime_enablement(
    *,
    review_decision: Mapping[str, Any] | None = None,
) -> DisabledBindingPlanNoRuntimeEnablement:
    """Build a plan-only packet from the PS-Q20K review decision mapping.

    The plan does not call loaders, read/write files, mutate UI, or enable runtime binding.
    It only records a disabled binding plan and preserves all execution boundaries.
    """

    decision = _as_mapping(review_decision)
    blocked: list[str] = []
    warnings: list[str] = []

    review_state = str(decision.get("review_state") or "")
    binding_decision = str(decision.get("binding_decision") or "")
    runtime_decision = str(decision.get("runtime_enablement_decision") or "")
    next_lane = str(decision.get("next_allowed_lane") or "")
    review_passed = review_state == "disabled_helper_sample_review_passed"
    design_review_only = next_lane == "design_review_only"
    runtime_disallowed = runtime_decision == "runtime_enablement_disallowed" and decision.get("runtime_enablement_allowed") is False
    loader_runtime_disallowed = decision.get("loader_binding_runtime_allowed") is False
    unsafe = tuple(name for name in UNSAFE_TRUE_FIELDS if decision.get(name) is True)

    if not decision:
        blocked.append("review_decision_missing")
    if not review_passed:
        blocked.append("review_decision_not_passed")
    if binding_decision != "allow_design_only_disabled_binding_plan":
        blocked.append("binding_decision_does_not_allow_disabled_plan")
    if not design_review_only:
        blocked.append("next_lane_not_design_review_only")
    if not runtime_disallowed:
        blocked.append("runtime_enablement_not_disallowed")
    if not loader_runtime_disallowed:
        blocked.append("loader_binding_runtime_not_disallowed")
    if unsafe:
        blocked.append("unsafe_runtime_or_execution_flag_true")

    if review_passed:
        warnings.append("review_passed_allows_plan_only_not_runtime_enablement")
    if design_review_only:
        warnings.append("next_lane_design_review_only_keeps_runtime_disabled")

    passed = not blocked
    return DisabledBindingPlanNoRuntimeEnablement(
        plan_version=DISABLED_BINDING_PLAN_VERSION,
        plan_state="disabled_binding_plan_ready" if passed else "disabled_binding_plan_blocked",
        plan_decision="plan_disabled_binding_without_runtime_enablement" if passed else "block_disabled_binding_plan_until_review_decision_is_safe",
        review_state=review_state,
        binding_decision=binding_decision,
        runtime_enablement_decision=runtime_decision,
        next_allowed_lane=next_lane,
        next_slice_candidate="PS-Q20M_DISABLED_BINDING_PLAN_PREVIEW_PACKET_NO_RUNTIME" if passed else "PS-Q20K_REVIEW_DECISION_REPAIR_OR_RERUN",
        plan_sequence=PLAN_SEQUENCE,
        plan_items=PLAN_ITEMS,
        review_passed=review_passed,
        design_review_only_lane=design_review_only,
        runtime_enablement_disallowed=runtime_disallowed,
        loader_binding_runtime_disallowed=loader_runtime_disallowed,
        unsafe_true_fields=unsafe,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warning_reasons=tuple(dict.fromkeys(warnings)),
    )
