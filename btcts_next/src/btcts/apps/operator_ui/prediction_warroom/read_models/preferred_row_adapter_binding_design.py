# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/preferred_row_adapter_binding_design.py
# desc: PS-Q20F design-only binding contract for adding preferred-row adapter output to the latest prediction WarRoom read model without rewiring runtime behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

from btcts.apps.operator_ui.components.prediction_warroom_preferred_row_adapter import (
    PREFERRED_ROW_ADAPTER_VERSION,
)
from btcts.apps.operator_ui.prediction_warroom.read_models.latest_prediction_warroom_read_model import (
    LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION,
)

PREFERRED_ROW_BINDING_DESIGN_VERSION = "prediction_warroom.preferred_row_adapter_binding_design.ps_q20f.v1"

BINDING_SEQUENCE: Tuple[str, ...] = (
    "keep_existing_latest_prediction_warroom_read_model_unchanged",
    "observe_preferred_row_adapter_packet_as_optional_read_only_section",
    "do_not_replace_market_snapshot_in_ps_q20f",
    "do_not_change_market_state_service_selection_in_ps_q20f",
    "do_not_enable_component_runtime_binding_in_ps_q20f",
    "do_not_write_warroom_view_artifact_in_ps_q20f",
    "do_not_enable_producer_or_scheduler_in_ps_q20f",
    "do_not_change_ps_q19r_scoring_policy_in_ps_q20f",
    "return_binding_design_packet_only",
)


@dataclass(frozen=True)
class PredictionWarRoomPreferredRowBindingDesignPacket:
    binding_version: str
    binding_state: str
    source_read_model_version: str
    preferred_row_adapter_version: str
    binding_sequence: Tuple[str, ...]
    read_model_present: bool
    adapter_packet_present: bool
    adapter_allowed_for_warroom: bool
    selected_row_available: bool
    proposed_read_model_section_key: str
    proposed_market_snapshot_source_kind: str
    blocked_reasons: Tuple[str, ...]
    warning_reasons: Tuple[str, ...]
    binding_design_only: bool = True
    read_only: bool = True
    non_executing: bool = True
    existing_warroom_read_model_changed: bool = False
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
        data["binding_sequence"] = list(self.binding_sequence)
        data["blocked_reasons"] = list(self.blocked_reasons)
        data["warning_reasons"] = list(self.warning_reasons)
        return data


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_preferred_row_adapter_binding_design(
    *,
    read_model: Mapping[str, Any] | None = None,
    preferred_row_adapter_packet: Mapping[str, Any] | None = None,
) -> PredictionWarRoomPreferredRowBindingDesignPacket:
    """Return a design-only packet for future WarRoom read-model binding.

    This function intentionally performs no file IO and does not mutate the existing
    WarRoom read model. It only describes a safe future section that can expose the
    preferred-row adapter packet next to the current market snapshot.
    """

    model = _as_mapping(read_model)
    adapter = _as_mapping(preferred_row_adapter_packet)
    blocked: list[str] = []
    warnings: list[str] = []

    model_present = bool(model)
    adapter_present = bool(adapter)
    adapter_allowed = adapter.get("allowed_for_requested_lane") is True and adapter.get("adapter_state") == "preferred_row_adapter_ready"
    selected_row_available = isinstance(adapter.get("selected_row"), Mapping)

    if not model_present:
        warnings.append("latest_prediction_warroom_read_model_not_supplied_for_design_context")
    if not adapter_present:
        warnings.append("preferred_row_adapter_packet_not_supplied_for_design_context")
    if adapter_present and not adapter_allowed:
        blocked.append("preferred_row_adapter_not_allowed_for_warroom_read")
    if adapter_present and not selected_row_available:
        blocked.append("preferred_row_adapter_selected_row_missing")

    state = "preferred_row_binding_design_ready" if adapter_allowed and selected_row_available else "preferred_row_binding_design_observe_only"
    source_kind = "market_state_preferred_row_adapter_observed" if adapter_allowed else "market_state_existing_snapshot_preserved"

    return PredictionWarRoomPreferredRowBindingDesignPacket(
        binding_version=PREFERRED_ROW_BINDING_DESIGN_VERSION,
        binding_state=state,
        source_read_model_version=str(model.get("read_model_version") or LATEST_PREDICTION_WARROOM_READ_MODEL_VERSION),
        preferred_row_adapter_version=str(adapter.get("adapter_version") or PREFERRED_ROW_ADAPTER_VERSION),
        binding_sequence=BINDING_SEQUENCE,
        read_model_present=model_present,
        adapter_packet_present=adapter_present,
        adapter_allowed_for_warroom=bool(adapter_allowed),
        selected_row_available=bool(selected_row_available),
        proposed_read_model_section_key="preferred_row_adapter_observation",
        proposed_market_snapshot_source_kind=source_kind,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warning_reasons=tuple(dict.fromkeys(warnings)),
    )
