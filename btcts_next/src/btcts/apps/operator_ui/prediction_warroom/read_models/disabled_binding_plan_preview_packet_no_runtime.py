# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/disabled_binding_plan_preview_packet_no_runtime.py
# desc: PS-Q20M supplied-mapping preview packet for the disabled binding plan. No runtime enablement, loader rewire, or artifact writes.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

from btcts.apps.operator_ui.prediction_warroom.read_models.disabled_binding_plan_no_runtime_enablement import (
    DISABLED_BINDING_PLAN_VERSION,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.explicit_read_only_loader_binding_helper import (
    EXPLICIT_READ_ONLY_LOADER_BINDING_HELPER_VERSION,
    build_explicit_read_only_loader_binding_helper,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.preferred_row_observation_section import (
    PREFERRED_ROW_OBSERVATION_SECTION_KEY,
)

DISABLED_BINDING_PLAN_PREVIEW_PACKET_VERSION = "prediction_warroom.disabled_binding_plan_preview_packet_no_runtime.ps_q20m.v1"

PREVIEW_SEQUENCE: Tuple[str, ...] = (
    "accept_disabled_binding_plan_mapping_only",
    "accept_supplied_read_model_mapping_only",
    "accept_supplied_preferred_row_adapter_packet_only",
    "require_ps_q20l_plan_ready",
    "evaluate_ps_q20i_helper_with_default_disabled_flag",
    "require_optional_section_not_attached",
    "preserve_supplied_read_model_market_snapshot",
    "produce_preview_packet_only",
    "keep_runtime_enablement_disallowed",
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
class DisabledBindingPlanPreviewPacketNoRuntime:
    preview_version: str
    preview_state: str
    preview_decision: str
    plan_version: str
    plan_state: str
    helper_version: str
    helper_state: str
    preview_sequence: Tuple[str, ...]
    plan_mapping_supplied: bool
    read_model_supplied: bool
    adapter_packet_supplied: bool
    plan_ready: bool
    helper_dry_run_ready: bool
    optional_section_attached: bool
    output_model_has_optional_section: bool
    preview_output_read_model: Mapping[str, Any]
    unsafe_true_fields: Tuple[str, ...]
    blocked_reasons: Tuple[str, ...]
    warning_reasons: Tuple[str, ...]
    preview_packet_only: bool = True
    supplied_mappings_only: bool = True
    default_disabled_preview: bool = True
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
        data["preview_sequence"] = list(self.preview_sequence)
        data["preview_output_read_model"] = dict(self.preview_output_read_model)
        data["unsafe_true_fields"] = list(self.unsafe_true_fields)
        data["blocked_reasons"] = list(self.blocked_reasons)
        data["warning_reasons"] = list(self.warning_reasons)
        return data


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _unsafe_true_fields(*mappings: Mapping[str, Any]) -> Tuple[str, ...]:
    found: list[str] = []
    for mapping in mappings:
        for name in UNSAFE_TRUE_FIELDS:
            if mapping.get(name) is True and name not in found:
                found.append(name)
    return tuple(found)


def build_disabled_binding_plan_preview_packet_no_runtime(
    *,
    disabled_binding_plan: Mapping[str, Any] | None = None,
    read_model: Mapping[str, Any] | None = None,
    preferred_row_adapter_packet: Mapping[str, Any] | None = None,
) -> DisabledBindingPlanPreviewPacketNoRuntime:
    """Build a supplied-mapping preview packet for the disabled binding plan.

    This function never invokes runtime loaders, never reads or writes artifacts, and never
    enables the PS-Q20I helper. The helper is evaluated with its default disabled flag so
    the optional observation section must remain unattached.
    """

    plan = _as_mapping(disabled_binding_plan)
    model = _as_mapping(read_model)
    adapter = _as_mapping(preferred_row_adapter_packet)
    helper = build_explicit_read_only_loader_binding_helper(
        read_model=model,
        preferred_row_adapter_packet=adapter,
    ).to_dict()
    helper_output = _as_mapping(helper.get("output_read_model"))

    blocked: list[str] = []
    warnings: list[str] = []

    plan_ready = (
        plan.get("plan_version") == DISABLED_BINDING_PLAN_VERSION
        and plan.get("plan_state") == "disabled_binding_plan_ready"
        and plan.get("plan_decision") == "plan_disabled_binding_without_runtime_enablement"
        and plan.get("runtime_enablement_allowed") is False
        and plan.get("loader_binding_runtime_allowed") is False
    )
    helper_disabled = helper.get("helper_state") == "explicit_read_only_loader_binding_helper_disabled"
    helper_dry_run_ready = helper.get("dry_run_ready") is True
    optional_attached = helper.get("optional_section_attached") is True
    output_has_optional = PREFERRED_ROW_OBSERVATION_SECTION_KEY in helper_output
    unsafe = _unsafe_true_fields(plan, helper, helper_output)

    if not plan:
        blocked.append("disabled_binding_plan_missing")
    if not model:
        blocked.append("read_model_missing")
    if not adapter:
        blocked.append("preferred_row_adapter_packet_missing")
    if not plan_ready:
        blocked.append("disabled_binding_plan_not_ready")
    if not helper_disabled:
        blocked.append("explicit_helper_not_disabled_by_default")
    if not helper_dry_run_ready:
        blocked.append("helper_dry_run_not_ready")
    if optional_attached or output_has_optional:
        blocked.append("optional_section_attached_in_disabled_preview")
    if unsafe:
        blocked.append("unsafe_runtime_or_execution_flag_true")

    values = helper.get("warning_reasons")
    if isinstance(values, list):
        warnings.extend(str(item) for item in values)
    if plan_ready:
        warnings.append("disabled_plan_ready_allows_preview_packet_only")
    if helper_dry_run_ready:
        warnings.append("helper_dry_run_ready_but_helper_remains_disabled")

    passed = not blocked
    output = dict(helper_output)
    output["disabled_binding_plan_preview_packet_version"] = DISABLED_BINDING_PLAN_PREVIEW_PACKET_VERSION
    output["disabled_binding_plan_preview_runtime_wired"] = False
    output["disabled_binding_plan_preview_would_write_artifact"] = False
    output["disabled_binding_plan_preview_optional_section_attached"] = False

    return DisabledBindingPlanPreviewPacketNoRuntime(
        preview_version=DISABLED_BINDING_PLAN_PREVIEW_PACKET_VERSION,
        preview_state="disabled_binding_plan_preview_packet_ready" if passed else "disabled_binding_plan_preview_packet_blocked",
        preview_decision="preview_packet_only_no_runtime" if passed else "block_preview_packet_until_inputs_are_safe",
        plan_version=str(plan.get("plan_version") or ""),
        plan_state=str(plan.get("plan_state") or ""),
        helper_version=EXPLICIT_READ_ONLY_LOADER_BINDING_HELPER_VERSION,
        helper_state=str(helper.get("helper_state") or ""),
        preview_sequence=PREVIEW_SEQUENCE,
        plan_mapping_supplied=bool(plan),
        read_model_supplied=bool(model),
        adapter_packet_supplied=bool(adapter),
        plan_ready=plan_ready,
        helper_dry_run_ready=helper_dry_run_ready,
        optional_section_attached=optional_attached,
        output_model_has_optional_section=output_has_optional,
        preview_output_read_model=output,
        unsafe_true_fields=unsafe,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warning_reasons=tuple(dict.fromkeys(warnings)),
    )
