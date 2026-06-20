# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_ui_mount_catalog.py
# desc: Display-only UI mount catalog for Prediction WarRoom widget groups. Mount planning metadata only; no Streamlit rendering, page mutation, runtime loader, file access, payload decode, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_handoff_catalog_visibility import (
    HANDOFF_CATALOG_VISIBILITY_VERSION,
    build_prediction_warroom_handoff_catalog_visibility_entry,
)

PREDICTION_WARROOM_UI_MOUNT_CATALOG_VERSION = "prediction_warroom_ui_mount_catalog.ps_q8a.v1"
PREDICTION_WARROOM_UI_MOUNT_CATALOG_ID = "prediction_warroom_ui_mount_catalog"
EXPECTED_BASE_WIDGET_GROUP_COUNT = 6
EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_COUNT = 6
EXPECTED_TOTAL_WIDGET_GROUP_COUNT = 12
EXPECTED_VISIBILITY_GROUP_COUNT = 7

BASE_WIDGET_MOUNT_ZONES = {
    "primary_signal_widget": "overview",
    "horizon_scenario_widgets": "primary_live",
    "family_detail_widgets": "primary_live",
    "source_quality_widget": "primary_live",
    "evidence_ledger_widget": "operator_support",
    "warning_refresh_widget": "operator_support",
}
SUPPLEMENTAL_WIDGET_MOUNT_ZONES = {
    "source_quality_explanation_widgets": "primary_live",
    "prediction_latest_payload_dry_run_status_widget": "operator_support",
    "prediction_latest_payload_loader_authorization_widget": "operator_support",
    "prediction_latest_payload_loader_authorization_registry_summary_widget": "operator_support",
    "prediction_authorization_handoff_status_widget": "operator_support",
    "prediction_supplemental_handoff_readiness_summary_widget": "operator_support",
}


@dataclass(frozen=True)
class PredictionWarRoomUIMountCatalog:
    catalog_version: str
    catalog_id: str
    catalog_kind: str
    mount_state: str
    source_handoff_catalog_version: str = HANDOFF_CATALOG_VISIBILITY_VERSION
    prediction_run_id: str | None = None
    visibility_state: str | None = None
    handoff_state: str | None = None
    mount_entries: Tuple[Mapping[str, Any], ...] = ()
    mount_entry_count: int = 0
    visibility_group_count: int = 0
    base_widget_group_count: int = 0
    supplemental_widget_group_count: int = 0
    total_widget_group_count: int = 0
    mount_blockers: Tuple[Mapping[str, Any], ...] = ()
    mount_warnings: Tuple[Mapping[str, Any], ...] = ()
    mount_metrics: Mapping[str, Any] = field(default_factory=dict)
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    catalog_only: bool = True
    mount_metadata_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
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
            "catalog_version": self.catalog_version,
            "catalog_id": self.catalog_id,
            "catalog_kind": self.catalog_kind,
            "mount_state": self.mount_state,
            "source_handoff_catalog_version": self.source_handoff_catalog_version,
            "prediction_run_id": self.prediction_run_id,
            "visibility_state": self.visibility_state,
            "handoff_state": self.handoff_state,
            "mount_entries": [dict(item) for item in self.mount_entries],
            "mount_entry_count": self.mount_entry_count,
            "visibility_group_count": self.visibility_group_count,
            "base_widget_group_count": self.base_widget_group_count,
            "supplemental_widget_group_count": self.supplemental_widget_group_count,
            "total_widget_group_count": self.total_widget_group_count,
            "mount_blockers": [dict(item) for item in self.mount_blockers],
            "mount_warnings": [dict(item) for item in self.mount_warnings],
            "mount_metrics": dict(self.mount_metrics),
            "integration_contract": dict(self.integration_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "catalog_only": self.catalog_only,
            "mount_metadata_only": self.mount_metadata_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
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
        "catalog_only": True,
        "mount_metadata_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
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


def _visibility_groups_by_widget(entry: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    by_widget: Dict[str, Mapping[str, Any]] = {}
    for raw in _list(entry.get("visibility_groups")):
        group = _as_mapping(raw)
        for widget_group_id in _list(group.get("widget_group_ids")):
            widget_id = str(widget_group_id or "")
            if widget_id:
                by_widget[widget_id] = group
    return by_widget


def _mount_zone(widget_group_id: str, *, supplemental: bool) -> str:
    if supplemental:
        return SUPPLEMENTAL_WIDGET_MOUNT_ZONES.get(widget_group_id, "operator_support")
    return BASE_WIDGET_MOUNT_ZONES.get(widget_group_id, "primary_live")


def _mount_entry(
    *,
    widget_group_id: str,
    order_index: int,
    supplemental: bool,
    visibility_group: Mapping[str, Any] | None,
    combined_order: list[str],
) -> Mapping[str, Any]:
    group = visibility_group or {}
    visibility_group_id = str(group.get("visibility_group_id") or "missing_visibility_group")
    attach_after = group.get("attach_after_widget_group_id")
    if not supplemental:
        attach_after = None
    attach_after_present = attach_after is None or str(attach_after) in combined_order
    return {
        "mount_catalog_version": PREDICTION_WARROOM_UI_MOUNT_CATALOG_VERSION,
        "widget_group_id": widget_group_id,
        "visibility_group_id": visibility_group_id,
        "visibility_kind": group.get("visibility_kind"),
        "ui_mount_hint": group.get("ui_mount_hint") or f"warroom_prediction:base:{widget_group_id}",
        "mount_slot_id": f"warroom_prediction_mount:{widget_group_id}",
        "mount_zone_id": _mount_zone(widget_group_id, supplemental=supplemental),
        "mount_surface_id": "warroom_page",
        "mount_order_index": order_index,
        "widget_group_kind": "supplemental" if supplemental else "base",
        "attach_after_widget_group_id": attach_after,
        "attach_after_present": attach_after_present,
        "refresh_policy": group.get("refresh_policy") or "use_q4b_auto_refresh_groups",
        "order_strategy": group.get("order_strategy") or "render_in_q4b_base_widget_group_order",
        "mount_state": "mount_ready_read_only" if attach_after_present and visibility_group else "mount_blocked_missing_visibility_or_attach_target",
        "can_render_in_future_slice": True,
        "render_call_allowed_in_this_slice": False,
        "streamlit_render_allowed": False,
        "page_mutation_allowed": False,
        "app_routing_mutation_allowed": False,
        **_safe_flags(),
    }


def _blocker(*, issue_code: str, widget_group_id: str, visibility_group_id: str | None = None) -> Mapping[str, Any]:
    return {
        "issue_code": issue_code,
        "severity": "blocker",
        "widget_group_id": widget_group_id,
        "visibility_group_id": visibility_group_id,
        **_safe_flags(),
    }


def build_prediction_warroom_ui_mount_catalog(
    *,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomUIMountCatalog:
    """Build a display-only mount catalog for Prediction WarRoom widget groups without rendering or page mutation."""
    entry = dict(_as_mapping(catalog_entry)) if catalog_entry is not None else build_prediction_warroom_handoff_catalog_visibility_entry(
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    combined_order = [str(item) for item in _list(entry.get("combined_widget_group_order"))]
    handoff_index = _as_mapping(entry.get("handoff_index"))
    base_order = [str(item) for item in _list(handoff_index.get("base_widget_group_order"))]
    supplemental_order = [str(item) for item in _list(handoff_index.get("supplemental_widget_group_order"))]
    visibility_by_widget = _visibility_groups_by_widget(entry)
    entries: list[Mapping[str, Any]] = []
    blockers: list[Mapping[str, Any]] = []
    for idx, widget_group_id in enumerate(combined_order):
        supplemental = widget_group_id in supplemental_order
        visibility_group = visibility_by_widget.get(widget_group_id)
        row = _mount_entry(
            widget_group_id=widget_group_id,
            order_index=idx,
            supplemental=supplemental,
            visibility_group=visibility_group,
            combined_order=combined_order,
        )
        entries.append(row)
        if visibility_group is None:
            blockers.append(_blocker(issue_code="widget_missing_visibility_group", widget_group_id=widget_group_id))
        elif row.get("attach_after_present") is not True:
            blockers.append(
                _blocker(
                    issue_code="attach_after_widget_group_missing_from_combined_order",
                    widget_group_id=widget_group_id,
                    visibility_group_id=str(visibility_group.get("visibility_group_id") or ""),
                )
            )
    counts = {
        "base_widget_group_count": int(entry.get("base_widget_group_count") or 0),
        "supplemental_widget_group_count": int(entry.get("supplemental_widget_group_count") or 0),
        "total_widget_group_count": int(entry.get("total_widget_group_count") or len(combined_order)),
        "visibility_group_count": int(entry.get("visibility_group_count") or 0),
        "mount_entry_count": len(entries),
    }
    counts_ok = counts == {
        "base_widget_group_count": EXPECTED_BASE_WIDGET_GROUP_COUNT,
        "supplemental_widget_group_count": EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_COUNT,
        "total_widget_group_count": EXPECTED_TOTAL_WIDGET_GROUP_COUNT,
        "visibility_group_count": EXPECTED_VISIBILITY_GROUP_COUNT,
        "mount_entry_count": EXPECTED_TOTAL_WIDGET_GROUP_COUNT,
    }
    visible = entry.get("visibility_state") == "visible_read_only" and entry.get("handoff_state") == "ready_for_read_only_warroom_handoff"
    entries_ready = all(row.get("mount_state") == "mount_ready_read_only" for row in entries)
    mount_state = (
        "ready_for_ui_mount_catalog_connection_render_disabled"
        if visible and counts_ok and entries_ready and not blockers
        else "blocked_before_ui_mount_catalog_connection_render_disabled"
    )
    metrics = {
        **counts,
        "expected_base_widget_group_count": EXPECTED_BASE_WIDGET_GROUP_COUNT,
        "expected_supplemental_widget_group_count": EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_COUNT,
        "expected_total_widget_group_count": EXPECTED_TOTAL_WIDGET_GROUP_COUNT,
        "expected_visibility_group_count": EXPECTED_VISIBILITY_GROUP_COUNT,
        "expected_mount_entry_count": EXPECTED_TOTAL_WIDGET_GROUP_COUNT,
        "counts_ok": counts_ok,
        "visible_read_only": visible,
        "mount_entries_ready": entries_ready,
        "mount_blocker_count": len(blockers),
        "mount_warning_count": 0,
        "base_mount_entry_count": sum(1 for row in entries if row.get("widget_group_kind") == "base"),
        "supplemental_mount_entry_count": sum(1 for row in entries if row.get("widget_group_kind") == "supplemental"),
        "streamlit_render_allowed": False,
        "page_mutation_allowed": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
    }
    integration_contract = {
        "contract_version": PREDICTION_WARROOM_UI_MOUNT_CATALOG_VERSION,
        "source_handoff_catalog_contract": HANDOFF_CATALOG_VISIBILITY_VERSION,
        "integration_kind": "display_only_prediction_warroom_ui_mount_catalog",
        "catalog_derivation_only": True,
        "does_not_modify_handoff_catalog": True,
        "does_not_register_widgets": True,
        "does_not_call_streamlit": True,
        "does_not_mutate_warroom_page": True,
        "does_not_grant_approval": True,
        "does_not_grant_authorization": True,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_in_future_slice_without_side_effects": True,
        **_safe_flags(),
    }
    return PredictionWarRoomUIMountCatalog(
        catalog_version=PREDICTION_WARROOM_UI_MOUNT_CATALOG_VERSION,
        catalog_id=PREDICTION_WARROOM_UI_MOUNT_CATALOG_ID,
        catalog_kind="prediction_warroom_display_only_ui_mount_catalog",
        mount_state=mount_state,
        prediction_run_id=str(entry.get("prediction_run_id")) if entry.get("prediction_run_id") else None,
        visibility_state=str(entry.get("visibility_state")) if entry.get("visibility_state") else None,
        handoff_state=str(entry.get("handoff_state")) if entry.get("handoff_state") else None,
        mount_entries=tuple(entries),
        mount_entry_count=len(entries),
        visibility_group_count=counts["visibility_group_count"],
        base_widget_group_count=counts["base_widget_group_count"],
        supplemental_widget_group_count=counts["supplemental_widget_group_count"],
        total_widget_group_count=counts["total_widget_group_count"],
        mount_blockers=tuple(blockers),
        mount_warnings=(),
        mount_metrics=metrics,
        integration_contract=integration_contract,
        boundaries=_safe_flags(),
    )


def build_prediction_warroom_ui_mount_catalog_index(
    *,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> Dict[str, Any]:
    """Return a compact display-only mount index for future Prediction WarRoom UI connection."""
    catalog = build_prediction_warroom_ui_mount_catalog(
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    return {
        "mount_catalog_index_version": PREDICTION_WARROOM_UI_MOUNT_CATALOG_VERSION,
        "catalog_id": catalog.get("catalog_id"),
        "catalog_kind": catalog.get("catalog_kind"),
        "mount_state": catalog.get("mount_state"),
        "visibility_state": catalog.get("visibility_state"),
        "handoff_state": catalog.get("handoff_state"),
        "mount_entry_count": catalog.get("mount_entry_count"),
        "visibility_group_count": catalog.get("visibility_group_count"),
        "base_widget_group_count": catalog.get("base_widget_group_count"),
        "supplemental_widget_group_count": catalog.get("supplemental_widget_group_count"),
        "total_widget_group_count": catalog.get("total_widget_group_count"),
        "mount_entries": [dict(item) for item in _list(catalog.get("mount_entries"))],
        "mount_blockers": [dict(item) for item in _list(catalog.get("mount_blockers"))],
        "mount_metrics": dict(_as_mapping(catalog.get("mount_metrics"))),
        "integration_contract": dict(_as_mapping(catalog.get("integration_contract"))),
        "boundaries": dict(_as_mapping(catalog.get("boundaries"))),
        **_safe_flags(),
    }
