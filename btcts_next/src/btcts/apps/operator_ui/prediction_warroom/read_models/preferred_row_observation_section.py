# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/read_models/preferred_row_observation_section.py
# desc: PS-Q20G optional read-only preferred-row observation section for latest prediction WarRoom read models. Pure mapping helper; not wired into runtime loaders.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple

from btcts.apps.operator_ui.prediction_warroom.read_models.preferred_row_adapter_binding_design import (
    PREFERRED_ROW_BINDING_DESIGN_VERSION,
    build_preferred_row_adapter_binding_design,
)

PREFERRED_ROW_OBSERVATION_SECTION_VERSION = "prediction_warroom.preferred_row_observation_section.ps_q20g.v1"
PREFERRED_ROW_OBSERVATION_SECTION_KEY = "preferred_row_adapter_observation"


@dataclass(frozen=True)
class PreferredRowObservationSection:
    section_version: str
    section_key: str
    section_state: str
    binding_version: str
    adapter_packet_present: bool
    adapter_allowed_for_warroom: bool
    selected_row_available: bool
    selected_row_summary: Mapping[str, Any]
    diagnostic_rows_retained: bool
    consumer_preferred_count: int
    diagnostic_transition_count: int
    blocked_reasons: Tuple[str, ...]
    warning_reasons: Tuple[str, ...]
    read_only_section: bool = True
    optional_section: bool = True
    additive_only: bool = True
    explicit_attach_required: bool = True
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
        data["selected_row_summary"] = dict(self.selected_row_summary)
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


def _selected_row_summary(row: Mapping[str, Any], *, market_snapshot: Mapping[str, Any] | None = None) -> dict[str, Any]:
    snapshot = _as_mapping(market_snapshot)
    return {
        "market_uid": str(
            row.get("market_uid")
            or row.get("symbol_raw")
            or row.get("symbol")
            or snapshot.get("market_uid")
            or snapshot.get("symbol_raw")
            or snapshot.get("symbol")
            or ""
        ),
        "collector_ts": str(row.get("collector_ts") or row.get("exchange_ts") or ""),
        "trust_state": str(row.get("trust_state") or ""),
        "interpretation_bucket": str(row.get("interpretation_bucket") or ""),
        "semantic_observer_status": str(row.get("semantic_observer_status") or ""),
        "best_bid": row.get("best_bid"),
        "best_ask": row.get("best_ask"),
        "spread": row.get("spread"),
        "mid_price": row.get("mid_price"),
        "source_series_id": str(row.get("source_series_id") or ""),
        "source_stream_session_id": str(row.get("source_stream_session_id") or ""),
    }


def build_preferred_row_observation_section(
    *,
    read_model: Mapping[str, Any] | None = None,
    preferred_row_adapter_packet: Mapping[str, Any] | None = None,
) -> PreferredRowObservationSection:
    """Build an optional read-only section from a preferred-row adapter packet.

    This helper performs no runtime reads or writes. It does not replace the existing
    market_snapshot; callers must explicitly attach the returned section to a read model copy.
    """

    model = _as_mapping(read_model)
    adapter = _as_mapping(preferred_row_adapter_packet)
    binding = build_preferred_row_adapter_binding_design(
        read_model=model,
        preferred_row_adapter_packet=adapter,
    ).to_dict()
    selected = _as_mapping(adapter.get("selected_row"))
    market_snapshot = _as_mapping(model.get("market_snapshot"))
    adapter_present = bool(adapter)
    adapter_allowed = binding.get("adapter_allowed_for_warroom") is True
    selected_available = bool(selected)

    blocked: list[str] = []
    warnings: list[str] = []
    for key in ("blocked_reasons", "warning_reasons"):
        values = binding.get(key)
        if isinstance(values, list):
            target = blocked if key == "blocked_reasons" else warnings
            target.extend(str(item) for item in values)
    values = adapter.get("blocked_reasons")
    if isinstance(values, list):
        blocked.extend(str(item) for item in values)
    values = adapter.get("warning_reasons")
    if isinstance(values, list):
        warnings.extend(str(item) for item in values)

    if not adapter_present:
        state = "preferred_row_observation_section_not_attached"
    elif adapter_allowed and selected_available:
        state = "preferred_row_observation_section_ready"
    else:
        state = "preferred_row_observation_section_blocked"

    return PreferredRowObservationSection(
        section_version=PREFERRED_ROW_OBSERVATION_SECTION_VERSION,
        section_key=PREFERRED_ROW_OBSERVATION_SECTION_KEY,
        section_state=state,
        binding_version=PREFERRED_ROW_BINDING_DESIGN_VERSION,
        adapter_packet_present=adapter_present,
        adapter_allowed_for_warroom=bool(adapter_allowed),
        selected_row_available=selected_available,
        selected_row_summary=_selected_row_summary(selected, market_snapshot=market_snapshot) if selected_available else {},
        diagnostic_rows_retained=bool(adapter.get("diagnostic_rows_retained") is True),
        consumer_preferred_count=_as_int(adapter.get("consumer_preferred_count")),
        diagnostic_transition_count=_as_int(adapter.get("diagnostic_transition_count")),
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warning_reasons=tuple(dict.fromkeys(warnings)),
    )


def attach_preferred_row_observation_section(
    read_model: Mapping[str, Any],
    *,
    preferred_row_adapter_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a copy of read_model with the optional observation section attached.

    The original mapping is not mutated. Existing market_snapshot content is preserved.
    """

    result = dict(read_model)
    result[PREFERRED_ROW_OBSERVATION_SECTION_KEY] = build_preferred_row_observation_section(
        read_model=read_model,
        preferred_row_adapter_packet=preferred_row_adapter_packet,
    ).to_dict()
    result["preferred_row_observation_section_attached"] = True
    result["preferred_row_observation_section_optional"] = True
    result["preferred_row_observation_section_runtime_wired"] = False
    result["preferred_row_observation_section_would_write_artifact"] = False
    result["market_snapshot_replaced_by_preferred_row_observation"] = False
    result["latest_prediction_warroom_read_model_loader_changed"] = False
    result["component_runtime_binding_allowed"] = False
    result["warroom_ui_trigger_enabled"] = False
    result["would_send_to_broker"] = False
    return result
