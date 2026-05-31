# path: ./btcts_next/src/btcts/processing/l4_consumer_models/operator_ui/real_data_validation_evidence_presentation_upstream.py
# desc: Pure upstream payload producer for Health/WarRoom evidence presentation surfaces.

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from btcts.processing.l4_consumer_models.operator_ui.real_data_validation_evidence_consumption import (
    HealthWarRoomEvidenceConsumptionModel,
    HealthWarRoomEvidencePresentationModel,
    health_warroom_evidence_presentation_payload,
)
from btcts.processing.l4_consumer_models.shared.real_data_validation_evidence import (
    RealDataValidationEvidenceSummary,
)

_HEALTH_KEYS: tuple[str, ...] = (
    "evidence_presentation_payload",
    "health_warroom_evidence_presentation_payload",
    "real_data_validation_evidence_presentation",
)

_WARROOM_KEYS: tuple[str, ...] = (
    "warroom_evidence_presentation_payload",
    "health_warroom_evidence_presentation_payload",
    "real_data_validation_evidence_presentation",
    "evidence_presentation_payload",
)

_REQUIRED_BOUNDARY_KEYS: tuple[str, ...] = (
    "read_only_consumption",
    "diagnostic_evidence_only",
    "operator_support_only",
    "not_runtime_signal",
    "not_runtime_wiring",
    "not_ui_rendering",
    "not_market_engine_input",
    "not_collector_writer",
    "not_broker_or_order_automation",
    "not_inference_or_training",
)

EvidencePresentationSource = (
    HealthWarRoomEvidencePresentationModel
    | HealthWarRoomEvidenceConsumptionModel
    | RealDataValidationEvidenceSummary
    | Mapping[str, Any]
    | None
)


def _ensure_boundary(payload: Mapping[str, Any]) -> dict[str, bool]:
    boundary = dict(payload.get("boundary") or {})
    for key in _REQUIRED_BOUNDARY_KEYS:
        boundary[key] = True if boundary.get(key) is not False else False
    return {key: bool(boundary.get(key)) for key in _REQUIRED_BOUNDARY_KEYS}


def build_health_warroom_evidence_presentation_upstream_payload(
    source: EvidencePresentationSource,
) -> dict[str, Any]:
    """Build a render-ready, still-disconnected presentation payload from an already-provided source."""
    payload = health_warroom_evidence_presentation_payload(source)
    boundary = _ensure_boundary(payload)
    normalized = dict(payload)
    normalized["boundary"] = boundary
    normalized["upstream_payload_kind"] = "health_warroom_evidence_presentation_upstream_payload"
    normalized["upstream_payload_version"] = "phase4a.health_warroom_evidence_presentation_upstream.v1"
    normalized["producer_stage"] = "pure_l4_operator_ui_payload_producer"
    normalized["read_only_consumption"] = True
    normalized["diagnostic_evidence_only"] = True
    normalized["operator_support_only"] = True
    normalized["not_runtime_signal"] = True
    normalized["not_runtime_wiring"] = True
    normalized["not_market_engine_input"] = True
    normalized["not_collector_writer"] = True
    normalized["not_broker_or_order_automation"] = True
    normalized["not_inference_or_training"] = True
    return normalized


def health_snapshot_evidence_presentation_payload_fields(
    payload: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Return fields that may be merged into a Health snapshot/current_state_bundle by a later slice."""
    value = dict(payload)
    return {key: dict(value) for key in _HEALTH_KEYS}


def warroom_session_state_evidence_presentation_payload_fields(
    payload: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Return fields that may be placed into WarRoom session_state by a later slice."""
    value = dict(payload)
    return {key: dict(value) for key in _WARROOM_KEYS}


def lower_health_warroom_evidence_presentation_payload(
    source: EvidencePresentationSource,
) -> dict[str, Any]:
    """Lower a source into canonical Health snapshot and WarRoom session_state payload fields."""
    payload = build_health_warroom_evidence_presentation_upstream_payload(source)
    return {
        "payload": dict(payload),
        "health_snapshot_fields": health_snapshot_evidence_presentation_payload_fields(payload),
        "warroom_session_state_fields": warroom_session_state_evidence_presentation_payload_fields(payload),
        "boundary": dict(payload.get("boundary") or {}),
        "lowering_kind": "health_warroom_evidence_presentation_payload_lowering",
        "lowering_version": "phase4a.health_warroom_evidence_presentation_lowering.v1",
        "not_runtime_wiring": True,
        "not_runtime_signal": True,
        "not_market_engine_input": True,
        "not_collector_writer": True,
        "not_broker_or_order_automation": True,
        "not_inference_or_training": True,
    }


def _evidence_presentation_payload_from_source(
    source: EvidencePresentationSource | Mapping[str, Any],
) -> dict[str, Any]:
    """Return an upstream presentation payload without mutating the provided source."""
    if isinstance(source, Mapping) and str(source.get("upstream_payload_kind") or "") == "health_warroom_evidence_presentation_upstream_payload":
        return dict(source)
    return build_health_warroom_evidence_presentation_upstream_payload(source)


def lower_health_snapshot_evidence_presentation_fields(
    existing_snapshot: Mapping[str, Any] | None,
    source: EvidencePresentationSource | Mapping[str, Any],
) -> dict[str, Any]:
    """Return a copied Health snapshot with read-only evidence presentation fields added.

    Pure lowering only: no filesystem reads, no state writes, no Streamlit calls,
    no runtime wiring, and no mutation of the input mapping.
    """
    out = dict(existing_snapshot or {})
    payload = _evidence_presentation_payload_from_source(source)
    out.update(health_snapshot_evidence_presentation_payload_fields(payload))
    out["evidence_presentation_lowering_channel"] = "health_snapshot_fields"
    out["evidence_presentation_lowering_version"] = "phase4a.health_snapshot_evidence_presentation_fields.v1"
    out["not_runtime_wiring"] = True
    out["not_runtime_signal"] = True
    out["not_market_engine_input"] = True
    out["not_collector_writer"] = True
    out["not_broker_or_order_automation"] = True
    out["not_inference_or_training"] = True
    return out


def lower_warroom_session_state_evidence_presentation_fields(
    existing_session_state: Mapping[str, Any] | None,
    source: EvidencePresentationSource | Mapping[str, Any],
) -> dict[str, Any]:
    """Return a copied WarRoom session-state mapping with evidence presentation fields added.

    Pure lowering only: no Streamlit mutation, no page rendering, no route wiring,
    no runtime wiring, and no mutation of the input mapping.
    """
    out = dict(existing_session_state or {})
    payload = _evidence_presentation_payload_from_source(source)
    out.update(warroom_session_state_evidence_presentation_payload_fields(payload))
    out["evidence_presentation_lowering_channel"] = "warroom_session_state_fields"
    out["evidence_presentation_lowering_version"] = "phase4a.warroom_session_state_evidence_presentation_fields.v1"
    out["not_runtime_wiring"] = True
    out["not_runtime_signal"] = True
    out["not_market_engine_input"] = True
    out["not_collector_writer"] = True
    out["not_broker_or_order_automation"] = True
    out["not_inference_or_training"] = True
    return out

