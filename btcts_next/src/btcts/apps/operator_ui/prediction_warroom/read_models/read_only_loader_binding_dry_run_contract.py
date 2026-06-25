# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/read_only_loader_binding_dry_run_contract.py
# desc: PS-Q20H read-only dry-run contract for a future latest prediction WarRoom loader binding. Pure mapping; invokes no runtime loader and writes no artifacts.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

from btcts.apps.operator_ui.prediction_warroom.read_models.preferred_row_observation_section import (
    PREFERRED_ROW_OBSERVATION_SECTION_KEY,
    PREFERRED_ROW_OBSERVATION_SECTION_VERSION,
    build_preferred_row_observation_section,
)

READ_ONLY_LOADER_BINDING_DRY_RUN_VERSION = "prediction_warroom.read_only_loader_binding_dry_run_contract.ps_q20h.v1"
TARGET_LOADER_NAME = "load_latest_prediction_warroom_read_model"

DRY_RUN_SEQUENCE: Tuple[str, ...] = (
    "declare_target_loader_without_invoking_it",
    "accept_supplied_read_model_mapping_only",
    "accept_supplied_preferred_row_adapter_packet_only",
    "build_optional_section_preview_from_supplied_mappings_only",
    "do_not_rewire_latest_prediction_warroom_read_model_loader",
    "do_not_change_market_state_service_selection",
    "do_not_read_prediction_artifact",
    "do_not_write_warroom_view_artifact",
    "do_not_enable_ui_component_runtime_binding",
    "do_not_enable_producer_or_scheduler",
    "return_dry_run_contract_packet_only",
)


@dataclass(frozen=True)
class ReadOnlyLoaderBindingDryRunContract:
    dry_run_version: str
    dry_run_state: str
    target_loader_name: str
    optional_section_key: str
    optional_section_version: str
    dry_run_sequence: Tuple[str, ...]
    read_model_supplied: bool
    adapter_packet_supplied: bool
    optional_section_preview_built: bool
    optional_section_preview_state: str
    optional_section_selected_row_available: bool
    would_attach_optional_section_in_future_slice: bool
    blocked_reasons: Tuple[str, ...]
    warning_reasons: Tuple[str, ...]
    dry_run_contract_only: bool = True
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
        data["dry_run_sequence"] = list(self.dry_run_sequence)
        data["blocked_reasons"] = list(self.blocked_reasons)
        data["warning_reasons"] = list(self.warning_reasons)
        return data


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_read_only_loader_binding_dry_run_contract(
    *,
    read_model: Mapping[str, Any] | None = None,
    preferred_row_adapter_packet: Mapping[str, Any] | None = None,
) -> ReadOnlyLoaderBindingDryRunContract:
    """Describe a safe future loader binding using only supplied mappings.

    This function does not call the target loader, read files, write artifacts, mutate UI,
    or connect runtime code. It only previews whether PS-Q20G's optional section would be
    attachable in a future explicit binding slice.
    """

    model = _as_mapping(read_model)
    adapter = _as_mapping(preferred_row_adapter_packet)
    blocked: list[str] = []
    warnings: list[str] = []

    if not model:
        warnings.append("read_model_mapping_not_supplied_for_dry_run")
    if not adapter:
        warnings.append("preferred_row_adapter_packet_not_supplied_for_dry_run")

    section_preview = build_preferred_row_observation_section(
        read_model=model,
        preferred_row_adapter_packet=adapter,
    ).to_dict()
    section_state = str(section_preview.get("section_state") or "")
    selected_available = section_preview.get("selected_row_available") is True
    preview_ready = section_state == "preferred_row_observation_section_ready" and selected_available

    for key in ("blocked_reasons", "warning_reasons"):
        values = section_preview.get(key)
        if isinstance(values, list):
            target = blocked if key == "blocked_reasons" else warnings
            target.extend(str(item) for item in values)

    if adapter and not preview_ready:
        blocked.append("optional_preferred_row_observation_section_not_ready_for_future_attach")

    state = "read_only_loader_binding_dry_run_ready" if model and adapter and preview_ready and not blocked else "read_only_loader_binding_dry_run_observe_only"
    would_attach = state == "read_only_loader_binding_dry_run_ready"

    return ReadOnlyLoaderBindingDryRunContract(
        dry_run_version=READ_ONLY_LOADER_BINDING_DRY_RUN_VERSION,
        dry_run_state=state,
        target_loader_name=TARGET_LOADER_NAME,
        optional_section_key=PREFERRED_ROW_OBSERVATION_SECTION_KEY,
        optional_section_version=PREFERRED_ROW_OBSERVATION_SECTION_VERSION,
        dry_run_sequence=DRY_RUN_SEQUENCE,
        read_model_supplied=bool(model),
        adapter_packet_supplied=bool(adapter),
        optional_section_preview_built=True,
        optional_section_preview_state=section_state,
        optional_section_selected_row_available=bool(selected_available),
        would_attach_optional_section_in_future_slice=bool(would_attach),
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warning_reasons=tuple(dict.fromkeys(warnings)),
    )
