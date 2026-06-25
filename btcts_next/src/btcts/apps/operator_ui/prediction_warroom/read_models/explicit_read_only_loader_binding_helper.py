# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/explicit_read_only_loader_binding_helper.py
# desc: PS-Q20I explicit read-only loader binding helper. Disabled by default; uses supplied mappings only and does not invoke runtime loaders.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

from btcts.apps.operator_ui.prediction_warroom.read_models.preferred_row_observation_section import (
    PREFERRED_ROW_OBSERVATION_SECTION_KEY,
    attach_preferred_row_observation_section,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.read_only_loader_binding_dry_run_contract import (
    READ_ONLY_LOADER_BINDING_DRY_RUN_VERSION,
    TARGET_LOADER_NAME,
    build_read_only_loader_binding_dry_run_contract,
)

EXPLICIT_READ_ONLY_LOADER_BINDING_HELPER_VERSION = "prediction_warroom.explicit_read_only_loader_binding_helper.ps_q20i.v1"
DEFAULT_ENABLE_EXPLICIT_READ_ONLY_LOADER_BINDING = False

HELPER_SEQUENCE: Tuple[str, ...] = (
    "default_disabled",
    "require_explicit_enable_true",
    "accept_supplied_read_model_mapping_only",
    "accept_supplied_preferred_row_adapter_packet_only",
    "evaluate_ps_q20h_dry_run_contract_first",
    "attach_optional_section_to_copy_only_when_enabled_and_dry_run_ready",
    "preserve_existing_market_snapshot",
    "do_not_invoke_target_loader",
    "do_not_read_prediction_artifact",
    "do_not_write_warroom_view_artifact",
    "do_not_enable_runtime_ui_or_component_binding",
    "return_helper_packet_only",
)


@dataclass(frozen=True)
class ExplicitReadOnlyLoaderBindingHelperPacket:
    helper_version: str
    helper_state: str
    target_loader_name: str
    dry_run_version: str
    helper_sequence: Tuple[str, ...]
    enable_explicit_read_only_loader_binding: bool
    read_model_supplied: bool
    adapter_packet_supplied: bool
    dry_run_state: str
    dry_run_ready: bool
    optional_section_key: str
    optional_section_attached: bool
    output_read_model: Mapping[str, Any]
    blocked_reasons: Tuple[str, ...]
    warning_reasons: Tuple[str, ...]
    explicit_helper_only: bool = True
    disabled_by_default: bool = True
    read_only: bool = True
    non_executing: bool = True
    supplied_mappings_only: bool = True
    target_loader_invoked: bool = False
    latest_prediction_artifact_read: bool = False
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
        data["helper_sequence"] = list(self.helper_sequence)
        data["output_read_model"] = dict(self.output_read_model)
        data["blocked_reasons"] = list(self.blocked_reasons)
        data["warning_reasons"] = list(self.warning_reasons)
        return data


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_explicit_read_only_loader_binding_helper(
    *,
    read_model: Mapping[str, Any] | None = None,
    preferred_row_adapter_packet: Mapping[str, Any] | None = None,
    enable_explicit_read_only_loader_binding: bool = DEFAULT_ENABLE_EXPLICIT_READ_ONLY_LOADER_BINDING,
) -> ExplicitReadOnlyLoaderBindingHelperPacket:
    """Optionally attach the PS-Q20G observation section to a supplied read model copy.

    The helper is disabled by default. It uses only caller-supplied mappings, never invokes
    the target loader, never reads prediction artifacts, and never writes view artifacts.
    """

    model = _as_mapping(read_model)
    adapter = _as_mapping(preferred_row_adapter_packet)
    dry_run = build_read_only_loader_binding_dry_run_contract(
        read_model=model,
        preferred_row_adapter_packet=adapter,
    ).to_dict()
    dry_run_state = str(dry_run.get("dry_run_state") or "")
    dry_run_ready = dry_run_state == "read_only_loader_binding_dry_run_ready"
    blocked: list[str] = []
    warnings: list[str] = []

    values = dry_run.get("blocked_reasons")
    if isinstance(values, list):
        blocked.extend(str(item) for item in values)
    values = dry_run.get("warning_reasons")
    if isinstance(values, list):
        warnings.extend(str(item) for item in values)

    output = dict(model)
    enabled = bool(enable_explicit_read_only_loader_binding)
    attached = False

    if not enabled:
        warnings.append("explicit_read_only_loader_binding_disabled_by_default")
        state = "explicit_read_only_loader_binding_helper_disabled"
    elif not dry_run_ready:
        blocked.append("read_only_loader_binding_dry_run_not_ready")
        state = "explicit_read_only_loader_binding_helper_blocked"
    else:
        output = attach_preferred_row_observation_section(
            model,
            preferred_row_adapter_packet=adapter,
        )
        attached = PREFERRED_ROW_OBSERVATION_SECTION_KEY in output
        state = "explicit_read_only_loader_binding_helper_attached" if attached else "explicit_read_only_loader_binding_helper_blocked"
        if not attached:
            blocked.append("preferred_row_observation_section_attach_failed")

    output["explicit_read_only_loader_binding_helper_version"] = EXPLICIT_READ_ONLY_LOADER_BINDING_HELPER_VERSION
    output["explicit_read_only_loader_binding_enable_requested"] = enabled
    output["explicit_read_only_loader_binding_helper_state"] = state
    output["explicit_read_only_loader_binding_runtime_wired"] = False
    output["explicit_read_only_loader_binding_target_loader_invoked"] = False
    output["explicit_read_only_loader_binding_would_write_artifact"] = False
    output["latest_prediction_warroom_read_model_loader_changed"] = False
    output["component_runtime_binding_allowed"] = False
    output["would_send_to_broker"] = False

    return ExplicitReadOnlyLoaderBindingHelperPacket(
        helper_version=EXPLICIT_READ_ONLY_LOADER_BINDING_HELPER_VERSION,
        helper_state=state,
        target_loader_name=TARGET_LOADER_NAME,
        dry_run_version=READ_ONLY_LOADER_BINDING_DRY_RUN_VERSION,
        helper_sequence=HELPER_SEQUENCE,
        enable_explicit_read_only_loader_binding=enabled,
        read_model_supplied=bool(model),
        adapter_packet_supplied=bool(adapter),
        dry_run_state=dry_run_state,
        dry_run_ready=bool(dry_run_ready),
        optional_section_key=PREFERRED_ROW_OBSERVATION_SECTION_KEY,
        optional_section_attached=bool(attached),
        output_read_model=output,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warning_reasons=tuple(dict.fromkeys(warnings)),
    )
