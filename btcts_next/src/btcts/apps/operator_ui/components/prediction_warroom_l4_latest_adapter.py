# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_l4_latest_adapter.py
# desc: Contract-only adapter boundary from L4/latest Prediction artifacts to WarRoom display/widget packets. No filesystem reads, runtime loading, Streamlit rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_widget_groups import build_prediction_warroom_widget_group_packet_index

ADAPTER_VERSION = "prediction_warroom_l4_latest_adapter.ps_q4c.v1"
DEFAULT_HOT_LATEST_ROOT_HINT = "D:\\btc_ts_hot"


@dataclass(frozen=True)
class PredictionWarRoomL4LatestArtifactRef:
    artifact_role: str
    artifact_contract_id: str
    expected_path_hint: str | None = None
    required: bool = True
    freshness_group: str = "prediction_warroom"
    refresh_group_id: str | None = None
    description: str = ""
    read_by_this_adapter: bool = False
    loaded_in_this_slice: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_role": self.artifact_role,
            "artifact_contract_id": self.artifact_contract_id,
            "expected_path_hint": self.expected_path_hint,
            "required": self.required,
            "freshness_group": self.freshness_group,
            "refresh_group_id": self.refresh_group_id,
            "description": self.description,
            "read_by_this_adapter": self.read_by_this_adapter,
            "loaded_in_this_slice": self.loaded_in_this_slice,
        }


@dataclass(frozen=True)
class PredictionWarRoomL4LatestAdapterPacket:
    adapter_version: str
    adapter_id: str
    adapter_state: str
    hot_latest_root_hint: str
    expected_artifact_refs: Tuple[PredictionWarRoomL4LatestArtifactRef, ...] = ()
    supplied_artifact_refs: Tuple[Mapping[str, Any], ...] = ()
    display_packet_available: bool = False
    widget_group_index_available: bool = False
    display_packet_contract_version: str | None = None
    widget_group_index_version: str | None = None
    widget_group_count: int = 0
    widget_group_order: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    dry_run: bool = True
    contract_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
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
            "adapter_version": self.adapter_version,
            "adapter_id": self.adapter_id,
            "adapter_state": self.adapter_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "expected_artifact_refs": [item.to_dict() for item in self.expected_artifact_refs],
            "supplied_artifact_refs": [dict(item) for item in self.supplied_artifact_refs],
            "display_packet_available": self.display_packet_available,
            "widget_group_index_available": self.widget_group_index_available,
            "display_packet_contract_version": self.display_packet_contract_version,
            "widget_group_index_version": self.widget_group_index_version,
            "widget_group_count": self.widget_group_count,
            "widget_group_order": list(self.widget_group_order),
            "handoff_summary": dict(self.handoff_summary),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "dry_run": self.dry_run,
            "contract_only": self.contract_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
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


def build_prediction_warroom_l4_latest_expected_artifacts(*, hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT) -> Tuple[PredictionWarRoomL4LatestArtifactRef, ...]:
    """Return the expected L4/latest artifact boundary without touching the filesystem."""
    root = str(hot_latest_root_hint).rstrip("\\/")
    return (
        PredictionWarRoomL4LatestArtifactRef(
            artifact_role="prediction_system_result_snapshot",
            artifact_contract_id="l4.latest.prediction_system_result.v1",
            expected_path_hint=fr"{root}\prediction\latest_prediction_system_result.json",
            required=True,
            refresh_group_id="prediction_warroom:source_quality_widget",
            description="Latest standalone PredictionSystemResult payload or equivalent DTO. The future adapter may transform this into PredictionWarRoomDisplayPacket.",
        ),
        PredictionWarRoomL4LatestArtifactRef(
            artifact_role="prediction_warroom_display_packet",
            artifact_contract_id="l4.latest.prediction_warroom_display_packet.v1",
            expected_path_hint=fr"{root}\prediction\latest_warroom_display_packet.json",
            required=False,
            refresh_group_id="prediction_warroom:primary_signal_widget",
            description="Optional prebuilt PredictionWarRoomDisplayPacket. When supplied directly, widget groups can be built without re-running prediction inference.",
        ),
        PredictionWarRoomL4LatestArtifactRef(
            artifact_role="prediction_warroom_widget_group_index",
            artifact_contract_id="l4.latest.prediction_warroom_widget_group_index.v1",
            expected_path_hint=fr"{root}\prediction\latest_warroom_widget_group_index.json",
            required=False,
            refresh_group_id="prediction_warroom:warning_refresh_widget",
            description="Optional prebuilt widget group index for WarRoom auto-refresh orchestration.",
        ),
        PredictionWarRoomL4LatestArtifactRef(
            artifact_role="prediction_source_quality_snapshot",
            artifact_contract_id="l4.latest.prediction_source_quality.v1",
            expected_path_hint=fr"{root}\prediction\latest_source_quality.json",
            required=False,
            refresh_group_id="prediction_warroom:source_quality_widget",
            description="Optional latest source-quality/freshness panel payload used to refresh source quality widgets independently.",
        ),
    )


def build_prediction_warroom_l4_latest_adapter_contract(
    *,
    display_packet: Mapping[str, Any] | Any | None = None,
    widget_group_index: Mapping[str, Any] | None = None,
    supplied_artifact_refs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
) -> PredictionWarRoomL4LatestAdapterPacket:
    """Build a dry-run, contract-only L4/latest adapter packet without reading or writing runtime artifacts."""
    display_data = _as_mapping(display_packet)
    supplied_index = _as_mapping(widget_group_index)
    built_index = supplied_index
    if display_data and not built_index:
        built_index = build_prediction_warroom_widget_group_packet_index(display_data)
    display_available = bool(display_data)
    index_available = bool(built_index)
    widget_order = tuple(str(item) for item in _list(built_index.get("widget_group_order"))) if index_available else ()
    adapter_state = "display_packet_supplied_widget_index_ready" if display_available and index_available else "contract_only_waiting_for_latest_payload"
    boundaries = {
        "read_only": True,
        "non_executing": True,
        "dry_run": True,
        "contract_only": True,
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
    return PredictionWarRoomL4LatestAdapterPacket(
        adapter_version=ADAPTER_VERSION,
        adapter_id=f"{ADAPTER_VERSION}:latest:{display_data.get('prediction_run_id') or supplied_index.get('prediction_run_id') or 'pending'}",
        adapter_state=adapter_state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        expected_artifact_refs=build_prediction_warroom_l4_latest_expected_artifacts(hot_latest_root_hint=hot_latest_root_hint),
        supplied_artifact_refs=tuple(dict(item) for item in (supplied_artifact_refs or ())),
        display_packet_available=display_available,
        widget_group_index_available=index_available,
        display_packet_contract_version=str(display_data.get("packet_version")) if display_available and display_data.get("packet_version") else None,
        widget_group_index_version=str(built_index.get("index_version")) if index_available and built_index.get("index_version") else None,
        widget_group_count=int(built_index.get("widget_group_count", 0) or 0) if index_available else 0,
        widget_group_order=widget_order,
        handoff_summary={
            "adapter_boundary": "l4_latest_to_prediction_warroom_display",
            "latest_runtime_root_preference": str(hot_latest_root_hint),
            "display_packet_available": display_available,
            "widget_group_index_available": index_available,
            "future_loader_required": True,
            "loaded_in_this_slice": False,
            "runtime_artifact_write_enabled": False,
            "auto_refresh_ready_for_contract": index_available,
            "expected_widget_group_order": list(widget_order),
        },
        boundaries=boundaries,
    )
