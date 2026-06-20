# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_loader_authorization_registry_summary_widget_groups.py
# desc: Supplemental widget-group index for Prediction WarRoom latest-payload loader authorization registry summary panel. Display grouping only; no approval write, loader execution, file access, payload decode, Streamlit rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_loader_authorization_registry_summary_panel import (
    AUTHORIZATION_REGISTRY_SUMMARY_PANEL_VERSION,
    build_prediction_warroom_loader_authorization_registry_summary_panel,
)
from .prediction_warroom_widget_groups import PredictionWarRoomWidgetGroupPacket

AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_VERSION = "prediction_warroom_loader_authorization_registry_summary_widget_groups.ps_q7e.v1"
AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_registry_summary_widget"
ATTACH_AFTER_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_widget"


@dataclass(frozen=True)
class PredictionWarRoomLoaderAuthorizationRegistrySummaryWidgetGroupIndex:
    index_version: str
    supplemental_widget_group_count: int = 0
    attach_after_widget_group_id: str = ATTACH_AFTER_WIDGET_GROUP_ID
    supplemental_widget_group_order: Tuple[str, ...] = ()
    auto_refresh_groups: Tuple[Mapping[str, Any], ...] = ()
    widget_groups: Tuple[Mapping[str, Any], ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    source_summary_panel_version: str = AUTHORIZATION_REGISTRY_SUMMARY_PANEL_VERSION
    read_only: bool = True
    non_executing: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    approval_granted_by_this_contract: bool = False
    authorization_granted_by_this_contract: bool = False
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
            "index_version": self.index_version,
            "supplemental_widget_group_count": self.supplemental_widget_group_count,
            "attach_after_widget_group_id": self.attach_after_widget_group_id,
            "supplemental_widget_group_order": list(self.supplemental_widget_group_order),
            "auto_refresh_groups": [dict(item) for item in self.auto_refresh_groups],
            "widget_groups": [dict(item) for item in self.widget_groups],
            "integration_contract": dict(self.integration_contract),
            "source_summary_panel_version": self.source_summary_panel_version,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "approval_granted_by_this_contract": self.approval_granted_by_this_contract,
            "authorization_granted_by_this_contract": self.authorization_granted_by_this_contract,
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


def _safe_flags() -> Dict[str, Any]:
    return {
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
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


def _payload_from_panel(panel: Mapping[str, Any]) -> Dict[str, Any]:
    metrics = dict(_as_mapping(panel.get("summary_metrics")))
    return {
        "payload_version": AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_VERSION,
        "source_summary_panel_version": panel.get("panel_version") or AUTHORIZATION_REGISTRY_SUMMARY_PANEL_VERSION,
        "panel_id": panel.get("panel_id"),
        "panel_kind": panel.get("panel_kind"),
        "panel_state": panel.get("panel_state"),
        "visibility_state": panel.get("visibility_state"),
        "handoff_state": panel.get("handoff_state"),
        "prediction_run_id": panel.get("prediction_run_id"),
        "summary_metrics": metrics,
        "authorization_visibility_summary": dict(_as_mapping(panel.get("authorization_visibility_summary"))),
        "registry_path_summary": dict(_as_mapping(panel.get("registry_path_summary"))),
        "operator_guidance_ja": list(panel.get("operator_guidance_ja") or ()),
        "boundaries": dict(_as_mapping(panel.get("boundaries"))),
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        **_safe_flags(),
    }


def build_prediction_warroom_loader_authorization_registry_summary_widget_group_packet(
    *,
    summary_panel: Mapping[str, Any] | Any | None = None,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomWidgetGroupPacket:
    """Build a supplemental display-only widget group for the Q7D authorization registry summary panel."""
    panel = dict(_as_mapping(summary_panel)) if summary_panel is not None else build_prediction_warroom_loader_authorization_registry_summary_panel(
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    payload = _payload_from_panel(panel)
    return PredictionWarRoomWidgetGroupPacket(
        packet_version=AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_VERSION,
        widget_group_id=AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID,
        widget_group_label_ja="loader承認registry要約",
        widget_group_kind="latest_payload_loader_authorization_registry_summary",
        refresh_group_id=f"prediction_warroom:{AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID}",
        refresh_interval_sec=60,
        refresh_priority=59,
        payload=payload,
        data_dependencies=(
            "q7d.loader_authorization_registry_summary_panel",
            "q7c.authorization_widget_registry_registration",
            "q7b.latest_payload_loader_authorization_widget",
            "q6i.handoff_catalog_visibility",
        ),
        stale_behavior="show_authorization_registry_summary_stale_badge_keep_loader_disabled",
        independent_refresh_allowed=True,
        ui_mount_hint="warroom_prediction:latest_payload_loader_authorization_registry_summary",
    )


def build_prediction_warroom_loader_authorization_registry_summary_widget_group_index(
    *,
    summary_panel: Mapping[str, Any] | Any | None = None,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomLoaderAuthorizationRegistrySummaryWidgetGroupIndex:
    """Return supplemental widget-group metadata for the Q7D summary panel without rendering or file reads."""
    group = build_prediction_warroom_loader_authorization_registry_summary_widget_group_packet(
        summary_panel=summary_panel,
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    )
    group_dict = group.to_dict()
    group_dict.update({"attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID, **_safe_flags()})
    payload = dict(group_dict.get("payload") or {})
    payload.update(_safe_flags())
    group_dict["payload"] = payload
    auto_refresh = {
        "widget_group_id": group.widget_group_id,
        "refresh_group_id": group.refresh_group_id,
        "refresh_interval_sec": group.refresh_interval_sec,
        "refresh_priority": group.refresh_priority,
        "data_dependencies": list(group.data_dependencies),
        "independent_refresh_allowed": group.independent_refresh_allowed,
        "stale_behavior": group.stale_behavior,
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        **_safe_flags(),
    }
    integration_contract = {
        "contract_version": AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_VERSION,
        "summary_panel_contract": AUTHORIZATION_REGISTRY_SUMMARY_PANEL_VERSION,
        "integration_kind": "supplemental_widget_group_append_after_loader_authorization_widget",
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        "does_not_modify_base_q4b_group_order": True,
        "does_not_register_into_q6f_registry_in_this_slice": True,
        "does_not_grant_approval": True,
        "does_not_grant_authorization": True,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_without_side_effects": True,
        **_safe_flags(),
    }
    return PredictionWarRoomLoaderAuthorizationRegistrySummaryWidgetGroupIndex(
        index_version=AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_VERSION,
        supplemental_widget_group_count=1,
        attach_after_widget_group_id=ATTACH_AFTER_WIDGET_GROUP_ID,
        supplemental_widget_group_order=(group.widget_group_id,),
        auto_refresh_groups=(auto_refresh,),
        widget_groups=(group_dict,),
        integration_contract=integration_contract,
    )
