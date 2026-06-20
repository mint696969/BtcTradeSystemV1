# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_loader_authorization_registry_summary_panel.py
# desc: Display-only summary panel for Prediction WarRoom latest-payload loader authorization registry/catalog status. Metadata derivation only; no approval write, loader execution, file access, payload decode, Streamlit rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_handoff_catalog_visibility import (
    HANDOFF_CATALOG_VISIBILITY_VERSION,
    build_prediction_warroom_handoff_catalog_visibility_entry,
)
from .prediction_warroom_latest_payload_loader_authorization_widget_groups import AUTHORIZATION_WIDGET_GROUP_VERSION
from .prediction_warroom_supplemental_handoff_bundle import SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION
from .prediction_warroom_supplemental_widget_registry import SUPPLEMENTAL_WIDGET_REGISTRY_VERSION
from .prediction_warroom_supplemental_widget_registry_preflight import SUPPLEMENTAL_WIDGET_REGISTRY_PREFLIGHT_VERSION

AUTHORIZATION_REGISTRY_SUMMARY_PANEL_VERSION = "prediction_warroom_loader_authorization_registry_summary_panel.ps_q7d.v1"
AUTHORIZATION_REGISTRY_SUMMARY_PANEL_ID = "prediction_latest_payload_loader_authorization_registry_summary_panel"
AUTHORIZATION_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_widget"
AUTHORIZATION_VISIBILITY_GROUP_ID = "prediction_warroom_loader_authorization_visibility"
AUTHORIZATION_ATTACH_AFTER_WIDGET_GROUP_ID = "prediction_latest_payload_dry_run_status_widget"


@dataclass(frozen=True)
class PredictionWarRoomLoaderAuthorizationRegistrySummaryPanel:
    panel_version: str
    panel_id: str
    panel_kind: str
    panel_state: str
    visibility_state: str | None = None
    handoff_state: str | None = None
    prediction_run_id: str | None = None
    source_catalog_version: str = HANDOFF_CATALOG_VISIBILITY_VERSION
    source_handoff_bundle_version: str = SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION
    source_supplemental_registry_version: str = SUPPLEMENTAL_WIDGET_REGISTRY_VERSION
    source_supplemental_preflight_version: str = SUPPLEMENTAL_WIDGET_REGISTRY_PREFLIGHT_VERSION
    source_authorization_widget_version: str = AUTHORIZATION_WIDGET_GROUP_VERSION
    summary_metrics: Mapping[str, Any] = field(default_factory=dict)
    authorization_visibility_summary: Mapping[str, Any] = field(default_factory=dict)
    registry_path_summary: Mapping[str, Any] = field(default_factory=dict)
    operator_guidance_ja: Tuple[str, ...] = ()
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    summary_only: bool = True
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
            "panel_version": self.panel_version,
            "panel_id": self.panel_id,
            "panel_kind": self.panel_kind,
            "panel_state": self.panel_state,
            "visibility_state": self.visibility_state,
            "handoff_state": self.handoff_state,
            "prediction_run_id": self.prediction_run_id,
            "source_catalog_version": self.source_catalog_version,
            "source_handoff_bundle_version": self.source_handoff_bundle_version,
            "source_supplemental_registry_version": self.source_supplemental_registry_version,
            "source_supplemental_preflight_version": self.source_supplemental_preflight_version,
            "source_authorization_widget_version": self.source_authorization_widget_version,
            "summary_metrics": dict(self.summary_metrics),
            "authorization_visibility_summary": dict(self.authorization_visibility_summary),
            "registry_path_summary": dict(self.registry_path_summary),
            "operator_guidance_ja": list(self.operator_guidance_ja),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "summary_only": self.summary_only,
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


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _safe_flags() -> Dict[str, Any]:
    return {
        "read_only": True,
        "non_executing": True,
        "summary_only": True,
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


def _find_visibility_group(catalog_entry: Mapping[str, Any], visibility_group_id: str) -> Mapping[str, Any]:
    for raw in _list(catalog_entry.get("visibility_groups")):
        group = _as_mapping(raw)
        if group.get("visibility_group_id") == visibility_group_id:
            return group
    return {}


def _panel_state(*, visible: bool, auth_widget_present: bool, attach_ok: bool, total_count_ok: bool) -> str:
    if visible and auth_widget_present and attach_ok and total_count_ok:
        return "ready_authorization_widget_visible_loader_disabled"
    if not auth_widget_present:
        return "blocked_authorization_widget_missing_loader_disabled"
    if not attach_ok:
        return "blocked_authorization_widget_attach_mismatch_loader_disabled"
    if not total_count_ok:
        return "blocked_authorization_registry_count_mismatch_loader_disabled"
    return "hidden_or_blocked_authorization_widget_loader_disabled"


def build_prediction_warroom_loader_authorization_registry_summary_panel(
    *,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomLoaderAuthorizationRegistrySummaryPanel:
    """Build a display-only summary panel for Q7C authorization widget registry/catalog status."""
    entry = dict(_as_mapping(catalog_entry)) if catalog_entry is not None else build_prediction_warroom_handoff_catalog_visibility_entry(
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    auth_visibility = dict(_find_visibility_group(entry, AUTHORIZATION_VISIBILITY_GROUP_ID))
    handoff_index = dict(_as_mapping(entry.get("handoff_index")))
    widget_group_ids = [str(item) for item in _list(auth_visibility.get("widget_group_ids"))]
    combined_order = [str(item) for item in _list(entry.get("combined_widget_group_order"))]
    supplemental_order = [str(item) for item in _list(handoff_index.get("supplemental_widget_group_order"))]
    auth_widget_present = AUTHORIZATION_WIDGET_GROUP_ID in widget_group_ids and AUTHORIZATION_WIDGET_GROUP_ID in combined_order
    attach_ok = auth_visibility.get("attach_after_widget_group_id") == AUTHORIZATION_ATTACH_AFTER_WIDGET_GROUP_ID
    visible = entry.get("visibility_state") == "visible_read_only"
    total_count = int(entry.get("total_widget_group_count") or 0)
    supplemental_count = int(entry.get("supplemental_widget_group_count") or 0)
    visibility_count = int(entry.get("visibility_group_count") or 0)
    total_count_ok = total_count >= 9 and supplemental_count >= 3 and visibility_count >= 4
    state = _panel_state(visible=visible, auth_widget_present=auth_widget_present, attach_ok=attach_ok, total_count_ok=total_count_ok)
    metrics = {
        "base_widget_group_count": int(entry.get("base_widget_group_count") or 0),
        "supplemental_widget_group_count": supplemental_count,
        "total_widget_group_count": total_count,
        "visibility_group_count": visibility_count,
        "authorization_widget_present": auth_widget_present,
        "authorization_visibility_group_present": bool(auth_visibility),
        "authorization_attach_ok": attach_ok,
        "authorization_widget_order_index": combined_order.index(AUTHORIZATION_WIDGET_GROUP_ID) if AUTHORIZATION_WIDGET_GROUP_ID in combined_order else None,
        "preflight_valid": handoff_index.get("preflight_valid"),
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
    }
    auth_summary = {
        "visibility_group_id": auth_visibility.get("visibility_group_id"),
        "visibility_kind": auth_visibility.get("visibility_kind"),
        "widget_group_ids": widget_group_ids,
        "attach_after_widget_group_id": auth_visibility.get("attach_after_widget_group_id"),
        "ui_mount_hint": auth_visibility.get("ui_mount_hint"),
        "refresh_policy": auth_visibility.get("refresh_policy"),
        "order_strategy": auth_visibility.get("order_strategy"),
        "visibility_state_when_handoff_ready": auth_visibility.get("visibility_state_when_handoff_ready"),
        "visibility_state_when_handoff_blocked": auth_visibility.get("visibility_state_when_handoff_blocked"),
        **_safe_flags(),
    }
    registry_path = {
        "catalog_version": entry.get("catalog_version"),
        "handoff_bundle_version": entry.get("handoff_bundle_version"),
        "handoff_state": entry.get("handoff_state"),
        "preflight_state": handoff_index.get("preflight_state"),
        "base_widget_group_order": [str(item) for item in _list(handoff_index.get("base_widget_group_order"))],
        "supplemental_widget_group_order": supplemental_order,
        "combined_widget_group_order": combined_order,
        "expected_authorization_widget_group_id": AUTHORIZATION_WIDGET_GROUP_ID,
        "expected_authorization_attach_after_widget_group_id": AUTHORIZATION_ATTACH_AFTER_WIDGET_GROUP_ID,
        **_safe_flags(),
    }
    boundaries = _safe_flags()
    guidance = (
        "このpanelはQ7C registry/catalogの状態を要約するだけで、承認記録・loader実行・hot/latest読取・payload decodeは行いません。",
        "authorization widgetが visible_read_only でも、このcontractは approval_granted_by_this_contract=False のままです。",
        "実loaderや承認書込を進める場合は、別slice・別guard・別commitで扱ってください。",
    )
    return PredictionWarRoomLoaderAuthorizationRegistrySummaryPanel(
        panel_version=AUTHORIZATION_REGISTRY_SUMMARY_PANEL_VERSION,
        panel_id=AUTHORIZATION_REGISTRY_SUMMARY_PANEL_ID,
        panel_kind="latest_payload_loader_authorization_registry_summary",
        panel_state=state,
        visibility_state=str(entry.get("visibility_state")) if entry.get("visibility_state") else None,
        handoff_state=str(entry.get("handoff_state")) if entry.get("handoff_state") else None,
        prediction_run_id=str(entry.get("prediction_run_id")) if entry.get("prediction_run_id") else None,
        summary_metrics=metrics,
        authorization_visibility_summary=auth_summary,
        registry_path_summary=registry_path,
        operator_guidance_ja=guidance,
        boundaries=boundaries,
    )


def build_prediction_warroom_loader_authorization_registry_summary_panel_index(
    *,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> Dict[str, Any]:
    """Return compact display-only index for the Q7D authorization registry summary panel."""
    panel = build_prediction_warroom_loader_authorization_registry_summary_panel(
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    return {
        "panel_index_version": AUTHORIZATION_REGISTRY_SUMMARY_PANEL_VERSION,
        "panel_id": panel.get("panel_id"),
        "panel_kind": panel.get("panel_kind"),
        "panel_state": panel.get("panel_state"),
        "visibility_state": panel.get("visibility_state"),
        "handoff_state": panel.get("handoff_state"),
        "summary_metrics": dict(_as_mapping(panel.get("summary_metrics"))),
        "authorization_visibility_summary": dict(_as_mapping(panel.get("authorization_visibility_summary"))),
        "registry_path_summary": dict(_as_mapping(panel.get("registry_path_summary"))),
        "boundaries": dict(_as_mapping(panel.get("boundaries"))),
        **_safe_flags(),
    }
