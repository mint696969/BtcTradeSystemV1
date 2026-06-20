# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_handoff_bundle.py
# desc: Read-only handoff bundle for Prediction WarRoom sample/base/supplemental widget payloads. Pure packaging only; no rendering, file access, payload decode, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping

from .prediction_warroom_sample_packets import SAMPLE_PACKET_VERSION, build_prediction_warroom_sample_packet_bundle
from .prediction_warroom_supplemental_widget_registry import (
    SUPPLEMENTAL_WIDGET_REGISTRY_VERSION,
    build_prediction_warroom_supplemental_widget_registry,
)
from .prediction_warroom_supplemental_widget_registry_preflight import (
    SUPPLEMENTAL_WIDGET_REGISTRY_PREFLIGHT_VERSION,
    build_prediction_warroom_supplemental_widget_registry_preflight_report,
)
from .prediction_warroom_widget_groups import WIDGET_GROUP_PACKET_VERSION

SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION = "prediction_warroom_supplemental_handoff_bundle.ps_q6h.v1"


@dataclass(frozen=True)
class PredictionWarRoomSupplementalHandoffBundle:
    handoff_bundle_version: str
    handoff_bundle_id: str
    handoff_state: str
    handoff_kind: str
    prediction_run_id: str | None = None
    sample_bundle: Mapping[str, Any] = field(default_factory=dict)
    display_packet: Mapping[str, Any] = field(default_factory=dict)
    base_widget_group_index: Mapping[str, Any] = field(default_factory=dict)
    supplemental_widget_registry: Mapping[str, Any] = field(default_factory=dict)
    supplemental_registry_preflight_report: Mapping[str, Any] = field(default_factory=dict)
    handoff_index: Mapping[str, Any] = field(default_factory=dict)
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    synthetic_only: bool = True
    fixture_only: bool = True
    handoff_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    actual_loader_execution_allowed: bool = False
    actual_file_read_allowed_by_this_contract: bool = False
    actual_payload_decode_allowed_by_this_contract: bool = False
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "handoff_bundle_version": self.handoff_bundle_version,
            "handoff_bundle_id": self.handoff_bundle_id,
            "handoff_state": self.handoff_state,
            "handoff_kind": self.handoff_kind,
            "prediction_run_id": self.prediction_run_id,
            "sample_bundle": dict(self.sample_bundle),
            "display_packet": dict(self.display_packet),
            "base_widget_group_index": dict(self.base_widget_group_index),
            "supplemental_widget_registry": dict(self.supplemental_widget_registry),
            "supplemental_registry_preflight_report": dict(self.supplemental_registry_preflight_report),
            "handoff_index": dict(self.handoff_index),
            "integration_contract": dict(self.integration_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "synthetic_only": self.synthetic_only,
            "fixture_only": self.fixture_only,
            "handoff_only": self.handoff_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "actual_loader_execution_allowed": self.actual_loader_execution_allowed,
            "actual_file_read_allowed_by_this_contract": self.actual_file_read_allowed_by_this_contract,
            "actual_payload_decode_allowed_by_this_contract": self.actual_payload_decode_allowed_by_this_contract,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _bool(value: Any) -> bool:
    return value is True


def build_prediction_warroom_supplemental_handoff_bundle(
    *,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomSupplementalHandoffBundle:
    """Build a read-only handoff bundle for sample/base/supplemental WarRoom widget payloads."""
    sample_bundle = build_prediction_warroom_sample_packet_bundle().to_dict()
    packet = dict(_as_mapping(display_packet) or _as_mapping(sample_bundle.get("display_packet")))
    base_widget_index = dict(_as_mapping(sample_bundle.get("widget_group_index")))
    registry = build_prediction_warroom_supplemental_widget_registry(
        display_packet=packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    preflight = build_prediction_warroom_supplemental_widget_registry_preflight_report(
        display_packet=packet,
        registry_packet=registry,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    base_count = int(base_widget_index.get("widget_group_count") or len(_list(base_widget_index.get("widget_groups"))))
    supplemental_count = int(registry.get("supplemental_widget_group_count") or len(_list(registry.get("widget_groups"))))
    base_order = [str(item) for item in _list(base_widget_index.get("widget_group_order"))]
    supplemental_order = [str(item) for item in _list(registry.get("supplemental_widget_group_order"))]
    total_order = tuple(base_order + supplemental_order)
    preflight_valid = _bool(preflight.get("valid"))
    handoff_state = "ready_for_read_only_warroom_handoff" if preflight_valid else "blocked_before_read_only_warroom_handoff"
    prediction_run_id = str(packet.get("prediction_run_id")) if packet.get("prediction_run_id") else None
    boundaries = {
        "read_only": True,
        "non_executing": True,
        "synthetic_only": True,
        "fixture_only": True,
        "handoff_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_collect_public_source": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
    }
    handoff_index = {
        "handoff_index_version": SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION,
        "prediction_run_id": prediction_run_id,
        "display_packet_version": packet.get("packet_version"),
        "base_widget_group_index_version": base_widget_index.get("index_version"),
        "supplemental_widget_registry_version": registry.get("registry_version"),
        "supplemental_registry_preflight_report_version": preflight.get("report_version"),
        "base_widget_group_count": base_count,
        "supplemental_widget_group_count": supplemental_count,
        "total_widget_group_count": base_count + supplemental_count,
        "base_widget_group_order": base_order,
        "supplemental_widget_group_order": supplemental_order,
        "combined_widget_group_order": list(total_order),
        "preflight_state": preflight.get("preflight_state"),
        "preflight_valid": preflight_valid,
        "read_only": True,
        "non_executing": True,
        "synthetic_only": True,
        "fixture_only": True,
        "handoff_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
    }
    integration_contract = {
        "contract_version": SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION,
        "sample_packet_contract": SAMPLE_PACKET_VERSION,
        "base_widget_group_contract": WIDGET_GROUP_PACKET_VERSION,
        "supplemental_widget_registry_contract": SUPPLEMENTAL_WIDGET_REGISTRY_VERSION,
        "supplemental_registry_preflight_contract": SUPPLEMENTAL_WIDGET_REGISTRY_PREFLIGHT_VERSION,
        "integration_kind": "read_only_prediction_warroom_supplemental_handoff_bundle",
        "contains_display_packet": True,
        "contains_base_widget_group_index": True,
        "contains_supplemental_widget_registry": True,
        "contains_supplemental_registry_preflight_report": True,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_without_side_effects": True,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        "read_only": True,
        "non_executing": True,
        "synthetic_only": True,
        "fixture_only": True,
        "handoff_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_collect_public_source": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
    }
    return PredictionWarRoomSupplementalHandoffBundle(
        handoff_bundle_version=SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION,
        handoff_bundle_id=f"{SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION}:{prediction_run_id or 'synthetic'}",
        handoff_state=handoff_state,
        handoff_kind="prediction_warroom_read_only_supplemental_handoff_bundle",
        prediction_run_id=prediction_run_id,
        sample_bundle=sample_bundle,
        display_packet=packet,
        base_widget_group_index=base_widget_index,
        supplemental_widget_registry=registry,
        supplemental_registry_preflight_report=preflight,
        handoff_index=handoff_index,
        integration_contract=integration_contract,
        boundaries=boundaries,
    )


def build_prediction_warroom_supplemental_handoff_bundle_index(
    *,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> Dict[str, Any]:
    """Return a compact read-only handoff bundle index for WarRoom integration checks."""
    bundle = build_prediction_warroom_supplemental_handoff_bundle(
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    return {
        "handoff_index_version": SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION,
        "handoff_bundle_id": bundle.get("handoff_bundle_id"),
        "handoff_state": bundle.get("handoff_state"),
        "handoff_kind": bundle.get("handoff_kind"),
        "prediction_run_id": bundle.get("prediction_run_id"),
        "handoff_index": dict(_as_mapping(bundle.get("handoff_index"))),
        "integration_contract": dict(_as_mapping(bundle.get("integration_contract"))),
        "preflight_valid": _as_mapping(bundle.get("supplemental_registry_preflight_report")).get("valid"),
        "preflight_state": _as_mapping(bundle.get("supplemental_registry_preflight_report")).get("preflight_state"),
        "base_widget_group_count": _as_mapping(bundle.get("handoff_index")).get("base_widget_group_count"),
        "supplemental_widget_group_count": _as_mapping(bundle.get("handoff_index")).get("supplemental_widget_group_count"),
        "total_widget_group_count": _as_mapping(bundle.get("handoff_index")).get("total_widget_group_count"),
        "combined_widget_group_order": list(_as_mapping(bundle.get("handoff_index")).get("combined_widget_group_order") or ()),
        "read_only": True,
        "non_executing": True,
        "synthetic_only": True,
        "fixture_only": True,
        "handoff_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
    }
