# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_ui_mount_presenter.py
# desc: Display-only presenter packet adapter for Prediction WarRoom UI mount catalog. Presentation metadata only; no Streamlit rendering, page mutation, runtime loader, file access, payload decode, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_ui_mount_catalog import (
    PREDICTION_WARROOM_UI_MOUNT_CATALOG_VERSION,
    build_prediction_warroom_ui_mount_catalog,
)

PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION = "prediction_warroom_ui_mount_presenter.ps_q8b.v1"
PREDICTION_WARROOM_UI_MOUNT_PRESENTER_ID = "prediction_warroom_ui_mount_presenter"
ZONE_ORDER = ("overview", "primary_live", "operator_support")
EXPECTED_MOUNT_ENTRY_COUNT = 12
EXPECTED_ZONE_SECTION_COUNT = 3


@dataclass(frozen=True)
class PredictionWarRoomUIMountPresenterPacket:
    presenter_version: str
    presenter_id: str
    presenter_kind: str
    display_state: str
    mount_catalog_version: str = PREDICTION_WARROOM_UI_MOUNT_CATALOG_VERSION
    mount_state: str | None = None
    visibility_state: str | None = None
    handoff_state: str | None = None
    compact_line: str = "prediction_warroom_mount_presenter unavailable"
    zone_sections: Tuple[Mapping[str, Any], ...] = ()
    zone_section_count: int = 0
    mount_entry_rows: Tuple[Mapping[str, Any], ...] = ()
    mount_entry_row_count: int = 0
    blocked_entry_rows: Tuple[Mapping[str, Any], ...] = ()
    blocked_entry_row_count: int = 0
    presenter_metrics: Mapping[str, Any] = field(default_factory=dict)
    operator_guidance_ja: Tuple[str, ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    presenter_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    ui_rendering_allowed: bool = False
    streamlit_render_allowed: bool = False
    page_mutation_allowed: bool = False
    app_routing_mutation_allowed: bool = False
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
            "presenter_version": self.presenter_version,
            "presenter_id": self.presenter_id,
            "presenter_kind": self.presenter_kind,
            "display_state": self.display_state,
            "mount_catalog_version": self.mount_catalog_version,
            "mount_state": self.mount_state,
            "visibility_state": self.visibility_state,
            "handoff_state": self.handoff_state,
            "compact_line": self.compact_line,
            "zone_sections": [dict(item) for item in self.zone_sections],
            "zone_section_count": self.zone_section_count,
            "mount_entry_rows": [dict(item) for item in self.mount_entry_rows],
            "mount_entry_row_count": self.mount_entry_row_count,
            "blocked_entry_rows": [dict(item) for item in self.blocked_entry_rows],
            "blocked_entry_row_count": self.blocked_entry_row_count,
            "presenter_metrics": dict(self.presenter_metrics),
            "operator_guidance_ja": list(self.operator_guidance_ja),
            "integration_contract": dict(self.integration_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "presenter_only": self.presenter_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "ui_rendering_allowed": self.ui_rendering_allowed,
            "streamlit_render_allowed": self.streamlit_render_allowed,
            "page_mutation_allowed": self.page_mutation_allowed,
            "app_routing_mutation_allowed": self.app_routing_mutation_allowed,
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


def _safe_flags() -> Dict[str, Any]:
    return {
        "read_only": True,
        "non_executing": True,
        "presenter_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "ui_rendering_allowed": False,
        "streamlit_render_allowed": False,
        "page_mutation_allowed": False,
        "app_routing_mutation_allowed": False,
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


def _entry_row(entry: Mapping[str, Any]) -> Mapping[str, Any]:
    row = {
        "widget_group_id": str(entry.get("widget_group_id") or "unknown"),
        "mount_zone_id": str(entry.get("mount_zone_id") or "unknown"),
        "mount_slot_id": str(entry.get("mount_slot_id") or "unknown"),
        "mount_surface_id": str(entry.get("mount_surface_id") or "warroom_page"),
        "mount_order_index": int(entry.get("mount_order_index") or 0),
        "widget_group_kind": str(entry.get("widget_group_kind") or "unknown"),
        "visibility_group_id": str(entry.get("visibility_group_id") or "unknown"),
        "visibility_kind": entry.get("visibility_kind"),
        "ui_mount_hint": str(entry.get("ui_mount_hint") or "unknown"),
        "attach_after_widget_group_id": entry.get("attach_after_widget_group_id"),
        "attach_after_present": bool(entry.get("attach_after_present")),
        "mount_state": str(entry.get("mount_state") or "unknown"),
        "refresh_policy": str(entry.get("refresh_policy") or "unknown"),
        "order_strategy": str(entry.get("order_strategy") or "unknown"),
        "render_call_allowed_in_this_slice": False,
        "streamlit_render_allowed": False,
        "page_mutation_allowed": False,
        "app_routing_mutation_allowed": False,
        **_safe_flags(),
    }
    return row


def _zone_sections(rows: list[Mapping[str, Any]]) -> Tuple[Mapping[str, Any], ...]:
    sections: list[Mapping[str, Any]] = []
    zones = [zone for zone in ZONE_ORDER if any(row.get("mount_zone_id") == zone for row in rows)]
    zones.extend(
        sorted(
            {
                str(row.get("mount_zone_id") or "unknown")
                for row in rows
                if str(row.get("mount_zone_id") or "unknown") not in ZONE_ORDER
            }
        )
    )
    for zone in zones:
        zone_rows = [row for row in rows if row.get("mount_zone_id") == zone]
        ready = [row for row in zone_rows if row.get("mount_state") == "mount_ready_read_only"]
        blocked = [row for row in zone_rows if row.get("mount_state") != "mount_ready_read_only"]
        section = {
            "zone_id": zone,
            "zone_label_ja": {
                "overview": "概要",
                "primary_live": "主要ライブ判断",
                "operator_support": "operator支援",
            }.get(zone, zone),
            "entry_count": len(zone_rows),
            "ready_entry_count": len(ready),
            "blocked_entry_count": len(blocked),
            "widget_group_ids": [str(row.get("widget_group_id")) for row in zone_rows],
            "supplemental_widget_group_ids": [str(row.get("widget_group_id")) for row in zone_rows if row.get("widget_group_kind") == "supplemental"],
            "base_widget_group_ids": [str(row.get("widget_group_id")) for row in zone_rows if row.get("widget_group_kind") == "base"],
            "section_state": "ready_read_only" if not blocked else "blocked_read_only",
            "compact_line": f"zone={zone};entries={len(zone_rows)};ready={len(ready)};blocked={len(blocked)};render=false",
            "render_call_allowed_in_this_slice": False,
            "streamlit_render_allowed": False,
            "page_mutation_allowed": False,
            **_safe_flags(),
        }
        sections.append(section)
    return tuple(sections)


def _compact_line(*, ready: bool, mount_entry_count: int, zone_section_count: int, blocked_count: int) -> str:
    return (
        "prediction_warroom_ui_mount_presenter="
        f"ready:{str(ready).lower()};"
        f"entries:{mount_entry_count};"
        f"zones:{zone_section_count};"
        f"blocked:{blocked_count};"
        "render:false;page_mutation:false"
    )


def build_prediction_warroom_ui_mount_presenter_packet(
    *,
    mount_catalog: Mapping[str, Any] | Any | None = None,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomUIMountPresenterPacket:
    """Build a display-only presenter packet from the Q8A UI mount catalog without rendering."""
    catalog = dict(_as_mapping(mount_catalog)) if mount_catalog is not None else build_prediction_warroom_ui_mount_catalog(
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    rows = [_entry_row(_as_mapping(item)) for item in _list(catalog.get("mount_entries"))]
    blocked_rows = [row for row in rows if row.get("mount_state") != "mount_ready_read_only"]
    sections = _zone_sections(rows)
    ready = (
        catalog.get("mount_state") == "ready_for_ui_mount_catalog_connection_render_disabled"
        and len(rows) == EXPECTED_MOUNT_ENTRY_COUNT
        and len(sections) == EXPECTED_ZONE_SECTION_COUNT
        and not blocked_rows
    )
    display_state = "ready_for_operator_review_render_disabled" if ready else "blocked_for_operator_review_render_disabled"
    metrics = {
        "mount_entry_row_count": len(rows),
        "expected_mount_entry_count": EXPECTED_MOUNT_ENTRY_COUNT,
        "zone_section_count": len(sections),
        "expected_zone_section_count": EXPECTED_ZONE_SECTION_COUNT,
        "blocked_entry_row_count": len(blocked_rows),
        "ready_entry_row_count": len(rows) - len(blocked_rows),
        "base_entry_row_count": sum(1 for row in rows if row.get("widget_group_kind") == "base"),
        "supplemental_entry_row_count": sum(1 for row in rows if row.get("widget_group_kind") == "supplemental"),
        "catalog_mount_state_ready": catalog.get("mount_state") == "ready_for_ui_mount_catalog_connection_render_disabled",
        "presenter_ready": ready,
        "ui_rendering_allowed": False,
        "streamlit_render_allowed": False,
        "page_mutation_allowed": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
    }
    integration_contract = {
        "contract_version": PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION,
        "source_mount_catalog_contract": PREDICTION_WARROOM_UI_MOUNT_CATALOG_VERSION,
        "integration_kind": "display_only_prediction_warroom_ui_mount_presenter_packet",
        "presenter_packet_only": True,
        "does_not_call_streamlit": True,
        "does_not_mutate_warroom_page": True,
        "does_not_register_widgets": True,
        "does_not_grant_approval": True,
        "does_not_grant_authorization": True,
        "safe_to_render_in_future_slice_without_side_effects": True,
        "requires_streamlit_rendering": False,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        **_safe_flags(),
    }
    return PredictionWarRoomUIMountPresenterPacket(
        presenter_version=PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION,
        presenter_id=PREDICTION_WARROOM_UI_MOUNT_PRESENTER_ID,
        presenter_kind="prediction_warroom_display_only_ui_mount_presenter_packet",
        display_state=display_state,
        mount_state=str(catalog.get("mount_state")) if catalog.get("mount_state") else None,
        visibility_state=str(catalog.get("visibility_state")) if catalog.get("visibility_state") else None,
        handoff_state=str(catalog.get("handoff_state")) if catalog.get("handoff_state") else None,
        compact_line=_compact_line(
            ready=ready,
            mount_entry_count=len(rows),
            zone_section_count=len(sections),
            blocked_count=len(blocked_rows),
        ),
        zone_sections=sections,
        zone_section_count=len(sections),
        mount_entry_rows=tuple(rows),
        mount_entry_row_count=len(rows),
        blocked_entry_rows=tuple(blocked_rows),
        blocked_entry_row_count=len(blocked_rows),
        presenter_metrics=metrics,
        operator_guidance_ja=(
            "このpresenter packetはUI mount catalogを表示しやすい行とzoneへ整形するだけです。",
            "このsliceではStreamlit描画・warroom_page.py変更・承認・loader・file read・payload decodeは行いません。",
        ),
        integration_contract=integration_contract,
        boundaries=_safe_flags(),
    )


def build_prediction_warroom_ui_mount_presenter_index(
    *,
    mount_catalog: Mapping[str, Any] | Any | None = None,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> Dict[str, Any]:
    """Return a compact index for future UI insertion planning without rendering."""
    packet = build_prediction_warroom_ui_mount_presenter_packet(
        mount_catalog=mount_catalog,
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    return {
        "presenter_index_version": PREDICTION_WARROOM_UI_MOUNT_PRESENTER_VERSION,
        "presenter_id": packet.get("presenter_id"),
        "presenter_kind": packet.get("presenter_kind"),
        "display_state": packet.get("display_state"),
        "mount_state": packet.get("mount_state"),
        "compact_line": packet.get("compact_line"),
        "zone_section_count": packet.get("zone_section_count"),
        "mount_entry_row_count": packet.get("mount_entry_row_count"),
        "blocked_entry_row_count": packet.get("blocked_entry_row_count"),
        "zone_sections": [dict(item) for item in _list(packet.get("zone_sections"))],
        "mount_entry_rows": [dict(item) for item in _list(packet.get("mount_entry_rows"))],
        "presenter_metrics": dict(_as_mapping(packet.get("presenter_metrics"))),
        "integration_contract": dict(_as_mapping(packet.get("integration_contract"))),
        "boundaries": dict(_as_mapping(packet.get("boundaries"))),
        **_safe_flags(),
    }
