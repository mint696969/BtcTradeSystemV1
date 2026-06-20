# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_authorization_handoff_status_widget_groups.py
# desc: Supplemental widget-group wrapper for Prediction WarRoom authorization handoff status catalog. Display grouping only; no registry mutation, approval write, loader execution, file access, payload decode, Streamlit rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_authorization_handoff_status_catalog import (
    AUTHORIZATION_HANDOFF_STATUS_CATALOG_VERSION,
    build_prediction_warroom_authorization_handoff_status_catalog,
)
from .prediction_warroom_widget_groups import PredictionWarRoomWidgetGroupPacket

AUTHORIZATION_HANDOFF_STATUS_WIDGET_GROUP_VERSION = "prediction_warroom_authorization_handoff_status_widget_groups.ps_q7h.v1"
AUTHORIZATION_HANDOFF_STATUS_WIDGET_GROUP_ID = "prediction_authorization_handoff_status_widget"
ATTACH_AFTER_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_registry_summary_widget"


@dataclass(frozen=True)
class PredictionWarRoomAuthorizationHandoffStatusWidgetGroupIndex:
    index_version: str
    supplemental_widget_group_count: int = 0
    attach_after_widget_group_id: str = ATTACH_AFTER_WIDGET_GROUP_ID
    supplemental_widget_group_order: Tuple[str, ...] = ()
    auto_refresh_groups: Tuple[Mapping[str, Any], ...] = ()
    widget_groups: Tuple[Mapping[str, Any], ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    source_authorization_handoff_status_catalog_version: str = AUTHORIZATION_HANDOFF_STATUS_CATALOG_VERSION
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
            "source_authorization_handoff_status_catalog_version": self.source_authorization_handoff_status_catalog_version,
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


def _payload_from_catalog(catalog: Mapping[str, Any]) -> Dict[str, Any]:
    summary_metrics = dict(_as_mapping(catalog.get("summary_metrics")))
    authorization_chain = dict(_as_mapping(catalog.get("authorization_chain")))
    return {
        "payload_version": AUTHORIZATION_HANDOFF_STATUS_WIDGET_GROUP_VERSION,
        "source_authorization_handoff_status_catalog_version": catalog.get("catalog_version") or AUTHORIZATION_HANDOFF_STATUS_CATALOG_VERSION,
        "catalog_id": catalog.get("catalog_id"),
        "catalog_kind": catalog.get("catalog_kind"),
        "status_state": catalog.get("status_state"),
        "visibility_state": catalog.get("visibility_state"),
        "handoff_state": catalog.get("handoff_state"),
        "prediction_run_id": catalog.get("prediction_run_id"),
        "summary_metrics": summary_metrics,
        "authorization_chain": authorization_chain,
        "visibility_group_summaries": [dict(_as_mapping(item)) for item in list(catalog.get("visibility_group_summaries") or ())],
        "operator_guidance_ja": list(catalog.get("operator_guidance_ja") or ()),
        "boundaries": dict(_as_mapping(catalog.get("boundaries"))),
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        **_safe_flags(),
    }


def build_prediction_warroom_authorization_handoff_status_widget_group_packet(
    *,
    status_catalog: Mapping[str, Any] | Any | None = None,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomWidgetGroupPacket:
    """Build a supplemental display-only widget group for the Q7G authorization handoff status catalog."""
    catalog = dict(_as_mapping(status_catalog)) if status_catalog is not None else build_prediction_warroom_authorization_handoff_status_catalog(
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    payload = _payload_from_catalog(catalog)
    return PredictionWarRoomWidgetGroupPacket(
        packet_version=AUTHORIZATION_HANDOFF_STATUS_WIDGET_GROUP_VERSION,
        widget_group_id=AUTHORIZATION_HANDOFF_STATUS_WIDGET_GROUP_ID,
        widget_group_label_ja="authorization handoff状態",
        widget_group_kind="authorization_handoff_status",
        refresh_group_id=f"prediction_warroom:{AUTHORIZATION_HANDOFF_STATUS_WIDGET_GROUP_ID}",
        refresh_interval_sec=60,
        refresh_priority=61,
        payload=payload,
        data_dependencies=(
            "q7g.authorization_handoff_status_catalog",
            "q7f.summary_widget_registry_registration",
            "q6i.handoff_catalog_visibility",
        ),
        stale_behavior="show_authorization_handoff_status_stale_badge_keep_loader_disabled",
        independent_refresh_allowed=True,
        ui_mount_hint="warroom_prediction:authorization_handoff_status",
    )


def build_prediction_warroom_authorization_handoff_status_widget_group_index(
    *,
    status_catalog: Mapping[str, Any] | Any | None = None,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomAuthorizationHandoffStatusWidgetGroupIndex:
    """Return supplemental widget-group metadata for the Q7G status catalog without registry mutation, rendering, or file reads."""
    group = build_prediction_warroom_authorization_handoff_status_widget_group_packet(
        status_catalog=status_catalog,
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
        "contract_version": AUTHORIZATION_HANDOFF_STATUS_WIDGET_GROUP_VERSION,
        "authorization_handoff_status_catalog_contract": AUTHORIZATION_HANDOFF_STATUS_CATALOG_VERSION,
        "integration_kind": "supplemental_widget_group_append_after_authorization_registry_summary_widget",
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
    return PredictionWarRoomAuthorizationHandoffStatusWidgetGroupIndex(
        index_version=AUTHORIZATION_HANDOFF_STATUS_WIDGET_GROUP_VERSION,
        supplemental_widget_group_count=1,
        attach_after_widget_group_id=ATTACH_AFTER_WIDGET_GROUP_ID,
        supplemental_widget_group_order=(group.widget_group_id,),
        auto_refresh_groups=(auto_refresh,),
        widget_groups=(group_dict,),
        integration_contract=integration_contract,
    )
