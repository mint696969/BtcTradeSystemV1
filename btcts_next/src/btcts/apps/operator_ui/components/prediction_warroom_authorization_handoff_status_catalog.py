# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_authorization_handoff_status_catalog.py
# desc: Display-only consolidated status catalog for Prediction WarRoom authorization/supplemental handoff visibility. Metadata derivation only; no approval write, loader execution, file access, payload decode, Streamlit rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_handoff_catalog_visibility import (
    HANDOFF_CATALOG_VISIBILITY_VERSION,
    build_prediction_warroom_handoff_catalog_visibility_entry,
)

AUTHORIZATION_HANDOFF_STATUS_CATALOG_VERSION = "prediction_warroom_authorization_handoff_status_catalog.ps_q7g.v1"
AUTHORIZATION_HANDOFF_STATUS_CATALOG_ID = "prediction_warroom_authorization_handoff_status_catalog"
AUTHORIZATION_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_widget"
AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_registry_summary_widget"
AUTHORIZATION_VISIBILITY_GROUP_ID = "prediction_warroom_loader_authorization_visibility"
AUTHORIZATION_REGISTRY_SUMMARY_VISIBILITY_GROUP_ID = "prediction_warroom_loader_authorization_registry_summary_visibility"
AUTHORIZATION_EXPECTED_ATTACH_AFTER_WIDGET_GROUP_ID = "prediction_latest_payload_dry_run_status_widget"
AUTHORIZATION_REGISTRY_SUMMARY_EXPECTED_ATTACH_AFTER_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_widget"
EXPECTED_BASE_WIDGET_GROUP_COUNT = 6
EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_COUNT = 6
EXPECTED_TOTAL_WIDGET_GROUP_COUNT = 12
EXPECTED_VISIBILITY_GROUP_COUNT = 7


@dataclass(frozen=True)
class PredictionWarRoomAuthorizationHandoffStatusCatalog:
    catalog_version: str
    catalog_id: str
    catalog_kind: str
    status_state: str
    visibility_state: str | None = None
    handoff_state: str | None = None
    prediction_run_id: str | None = None
    source_handoff_catalog_version: str = HANDOFF_CATALOG_VISIBILITY_VERSION
    summary_metrics: Mapping[str, Any] = field(default_factory=dict)
    authorization_chain: Mapping[str, Any] = field(default_factory=dict)
    visibility_group_summaries: Tuple[Mapping[str, Any], ...] = ()
    operator_guidance_ja: Tuple[str, ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    catalog_only: bool = True
    status_only: bool = True
    visibility_metadata_only: bool = True
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
            "catalog_version": self.catalog_version,
            "catalog_id": self.catalog_id,
            "catalog_kind": self.catalog_kind,
            "status_state": self.status_state,
            "visibility_state": self.visibility_state,
            "handoff_state": self.handoff_state,
            "prediction_run_id": self.prediction_run_id,
            "source_handoff_catalog_version": self.source_handoff_catalog_version,
            "summary_metrics": dict(self.summary_metrics),
            "authorization_chain": dict(self.authorization_chain),
            "visibility_group_summaries": [dict(item) for item in self.visibility_group_summaries],
            "operator_guidance_ja": list(self.operator_guidance_ja),
            "integration_contract": dict(self.integration_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "catalog_only": self.catalog_only,
            "status_only": self.status_only,
            "visibility_metadata_only": self.visibility_metadata_only,
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
        "catalog_only": True,
        "status_only": True,
        "visibility_metadata_only": True,
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


def _visibility_groups_by_id(catalog_entry: Mapping[str, Any]) -> Dict[str, Mapping[str, Any]]:
    groups: Dict[str, Mapping[str, Any]] = {}
    for raw in _list(catalog_entry.get("visibility_groups")):
        group = _as_mapping(raw)
        group_id = str(group.get("visibility_group_id") or "")
        if group_id:
            groups[group_id] = group
    return groups


def _status_state(*, visible: bool, counts_ok: bool, authorization_present: bool, summary_present: bool, attach_ok: bool) -> str:
    if visible and counts_ok and authorization_present and summary_present and attach_ok:
        return "ready_authorization_handoff_status_visible_loader_disabled"
    if not visible:
        return "hidden_or_blocked_authorization_handoff_status_loader_disabled"
    if not counts_ok:
        return "blocked_authorization_handoff_count_mismatch_loader_disabled"
    if not authorization_present:
        return "blocked_authorization_widget_missing_loader_disabled"
    if not summary_present:
        return "blocked_authorization_summary_widget_missing_loader_disabled"
    if not attach_ok:
        return "blocked_authorization_widget_chain_attach_mismatch_loader_disabled"
    return "blocked_authorization_handoff_status_loader_disabled"


def _visibility_summary(group: Mapping[str, Any], *, expected_attach_after: str | None) -> Mapping[str, Any]:
    widget_group_ids = [str(item) for item in _list(group.get("widget_group_ids"))]
    attach_after = group.get("attach_after_widget_group_id")
    return {
        "visibility_group_id": group.get("visibility_group_id"),
        "visibility_kind": group.get("visibility_kind"),
        "visibility_label_ja": group.get("visibility_label_ja"),
        "widget_group_ids": widget_group_ids,
        "widget_group_count": len(widget_group_ids),
        "attach_after_widget_group_id": attach_after,
        "expected_attach_after_widget_group_id": expected_attach_after,
        "attach_after_ok": attach_after == expected_attach_after,
        "ui_mount_hint": group.get("ui_mount_hint"),
        "refresh_policy": group.get("refresh_policy"),
        "order_strategy": group.get("order_strategy"),
        **_safe_flags(),
    }


def build_prediction_warroom_authorization_handoff_status_catalog(
    *,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomAuthorizationHandoffStatusCatalog:
    """Build a display-only consolidated status catalog for the Q7F authorization/supplemental handoff path."""
    entry = dict(_as_mapping(catalog_entry)) if catalog_entry is not None else build_prediction_warroom_handoff_catalog_visibility_entry(
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    groups_by_id = _visibility_groups_by_id(entry)
    authorization_group = groups_by_id.get(AUTHORIZATION_VISIBILITY_GROUP_ID, {})
    summary_group = groups_by_id.get(AUTHORIZATION_REGISTRY_SUMMARY_VISIBILITY_GROUP_ID, {})
    combined_order = [str(item) for item in _list(entry.get("combined_widget_group_order"))]
    authorization_present = AUTHORIZATION_WIDGET_GROUP_ID in combined_order and AUTHORIZATION_WIDGET_GROUP_ID in _list(authorization_group.get("widget_group_ids"))
    summary_present = AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID in combined_order and AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID in _list(summary_group.get("widget_group_ids"))
    authorization_attach_ok = authorization_group.get("attach_after_widget_group_id") == AUTHORIZATION_EXPECTED_ATTACH_AFTER_WIDGET_GROUP_ID
    summary_attach_ok = summary_group.get("attach_after_widget_group_id") == AUTHORIZATION_REGISTRY_SUMMARY_EXPECTED_ATTACH_AFTER_WIDGET_GROUP_ID
    attach_ok = authorization_attach_ok and summary_attach_ok
    counts = {
        "base_widget_group_count": int(entry.get("base_widget_group_count") or 0),
        "supplemental_widget_group_count": int(entry.get("supplemental_widget_group_count") or 0),
        "total_widget_group_count": int(entry.get("total_widget_group_count") or 0),
        "visibility_group_count": int(entry.get("visibility_group_count") or 0),
    }
    counts_ok = counts == {
        "base_widget_group_count": EXPECTED_BASE_WIDGET_GROUP_COUNT,
        "supplemental_widget_group_count": EXPECTED_SUPPLEMENTAL_WIDGET_GROUP_COUNT,
        "total_widget_group_count": EXPECTED_TOTAL_WIDGET_GROUP_COUNT,
        "visibility_group_count": EXPECTED_VISIBILITY_GROUP_COUNT,
    }
    visible = entry.get("visibility_state") == "visible_read_only" and entry.get("handoff_state") == "ready_for_read_only_warroom_handoff"
    state = _status_state(
        visible=visible,
        counts_ok=counts_ok,
        authorization_present=authorization_present,
        summary_present=summary_present,
        attach_ok=attach_ok,
    )
    authorization_index = combined_order.index(AUTHORIZATION_WIDGET_GROUP_ID) if AUTHORIZATION_WIDGET_GROUP_ID in combined_order else None
    summary_index = combined_order.index(AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID) if AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID in combined_order else None
    metrics = {
        **counts,
        "counts_ok": counts_ok,
        "authorization_widget_present": authorization_present,
        "authorization_registry_summary_widget_present": summary_present,
        "authorization_attach_ok": authorization_attach_ok,
        "authorization_registry_summary_attach_ok": summary_attach_ok,
        "authorization_widget_order_index": authorization_index,
        "authorization_registry_summary_widget_order_index": summary_index,
        "authorization_chain_order_ok": authorization_index is not None and summary_index is not None and authorization_index < summary_index,
        "preflight_visible_read_only": visible,
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
    }
    visibility_summaries = (
        _visibility_summary(authorization_group, expected_attach_after=AUTHORIZATION_EXPECTED_ATTACH_AFTER_WIDGET_GROUP_ID),
        _visibility_summary(summary_group, expected_attach_after=AUTHORIZATION_REGISTRY_SUMMARY_EXPECTED_ATTACH_AFTER_WIDGET_GROUP_ID),
    )
    chain = {
        "authorization_widget_group_id": AUTHORIZATION_WIDGET_GROUP_ID,
        "authorization_registry_summary_widget_group_id": AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID,
        "authorization_visibility_group_id": AUTHORIZATION_VISIBILITY_GROUP_ID,
        "authorization_registry_summary_visibility_group_id": AUTHORIZATION_REGISTRY_SUMMARY_VISIBILITY_GROUP_ID,
        "authorization_attach_after_widget_group_id": authorization_group.get("attach_after_widget_group_id"),
        "authorization_registry_summary_attach_after_widget_group_id": summary_group.get("attach_after_widget_group_id"),
        "expected_authorization_attach_after_widget_group_id": AUTHORIZATION_EXPECTED_ATTACH_AFTER_WIDGET_GROUP_ID,
        "expected_authorization_registry_summary_attach_after_widget_group_id": AUTHORIZATION_REGISTRY_SUMMARY_EXPECTED_ATTACH_AFTER_WIDGET_GROUP_ID,
        "combined_widget_group_order_tail": combined_order[-6:],
        "authorization_chain_ready": visible and counts_ok and authorization_present and summary_present and attach_ok,
        **_safe_flags(),
    }
    integration_contract = {
        "contract_version": AUTHORIZATION_HANDOFF_STATUS_CATALOG_VERSION,
        "source_handoff_catalog_contract": HANDOFF_CATALOG_VISIBILITY_VERSION,
        "integration_kind": "display_only_authorization_handoff_status_catalog",
        "does_not_modify_handoff_catalog": True,
        "does_not_register_widgets": True,
        "does_not_grant_approval": True,
        "does_not_grant_authorization": True,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_without_side_effects": True,
        **_safe_flags(),
    }
    guidance = (
        "このcatalogはQ7F後のauthorization/supplemental handoff状態を要約するだけで、承認記録・loader実行・hot/latest読取・payload decodeは行いません。",
        "ready状態でも approval_granted_by_this_contract=False / actual_loader_execution_allowed=False のままです。",
        "実loaderや承認書込を進める場合は、別slice・別guard・別commitで扱ってください。",
    )
    return PredictionWarRoomAuthorizationHandoffStatusCatalog(
        catalog_version=AUTHORIZATION_HANDOFF_STATUS_CATALOG_VERSION,
        catalog_id=AUTHORIZATION_HANDOFF_STATUS_CATALOG_ID,
        catalog_kind="prediction_warroom_authorization_supplemental_handoff_status_catalog",
        status_state=state,
        visibility_state=str(entry.get("visibility_state")) if entry.get("visibility_state") else None,
        handoff_state=str(entry.get("handoff_state")) if entry.get("handoff_state") else None,
        prediction_run_id=str(entry.get("prediction_run_id")) if entry.get("prediction_run_id") else None,
        summary_metrics=metrics,
        authorization_chain=chain,
        visibility_group_summaries=visibility_summaries,
        operator_guidance_ja=guidance,
        integration_contract=integration_contract,
        boundaries=_safe_flags(),
    )


def build_prediction_warroom_authorization_handoff_status_catalog_index(
    *,
    catalog_entry: Mapping[str, Any] | Any | None = None,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> Dict[str, Any]:
    """Return a compact display-only index for the Q7G authorization handoff status catalog."""
    catalog = build_prediction_warroom_authorization_handoff_status_catalog(
        catalog_entry=catalog_entry,
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    return {
        "catalog_index_version": AUTHORIZATION_HANDOFF_STATUS_CATALOG_VERSION,
        "catalog_id": catalog.get("catalog_id"),
        "catalog_kind": catalog.get("catalog_kind"),
        "status_state": catalog.get("status_state"),
        "visibility_state": catalog.get("visibility_state"),
        "handoff_state": catalog.get("handoff_state"),
        "summary_metrics": dict(_as_mapping(catalog.get("summary_metrics"))),
        "authorization_chain": dict(_as_mapping(catalog.get("authorization_chain"))),
        "visibility_group_summaries": [dict(item) for item in _list(catalog.get("visibility_group_summaries"))],
        "integration_contract": dict(_as_mapping(catalog.get("integration_contract"))),
        "boundaries": dict(_as_mapping(catalog.get("boundaries"))),
        **_safe_flags(),
    }
