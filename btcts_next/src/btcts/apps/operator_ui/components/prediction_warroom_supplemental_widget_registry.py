# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_supplemental_widget_registry.py
# desc: Composite supplemental widget registry for Prediction WarRoom. Combines explanation and latest-payload dry-run supplemental widget groups without rendering, file access, payload decode, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_explanation_widget_groups import (
    EXPLANATION_WIDGET_GROUP_VERSION,
    build_prediction_warroom_explanation_widget_group_index,
)
from .prediction_warroom_latest_payload_dry_run_widget_groups import (
    DRY_RUN_WIDGET_GROUP_VERSION,
    build_prediction_warroom_latest_payload_dry_run_widget_group_index,
)
from .prediction_warroom_latest_payload_loader_authorization_widget_groups import (
    AUTHORIZATION_WIDGET_GROUP_VERSION,
    build_prediction_warroom_latest_payload_loader_authorization_widget_group_index,
)
from .prediction_warroom_widget_groups import WIDGET_GROUP_PACKET_VERSION

SUPPLEMENTAL_WIDGET_REGISTRY_VERSION = "prediction_warroom_supplemental_widget_registry.ps_q6f.v1"
AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_VERSION = "prediction_warroom_loader_authorization_registry_summary_widget_groups.ps_q7e.v1"
AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_registry_summary_widget"
AUTHORIZATION_REGISTRY_SUMMARY_ATTACH_AFTER_WIDGET_GROUP_ID = "prediction_latest_payload_loader_authorization_widget"
AUTHORIZATION_REGISTRY_SUMMARY_PANEL_VERSION = "prediction_warroom_loader_authorization_registry_summary_panel.ps_q7d.v1"
BASE_WIDGET_GROUP_COUNT = 6


@dataclass(frozen=True)
class PredictionWarRoomSupplementalWidgetRegistryPacket:
    registry_version: str
    registry_id: str
    registry_kind: str
    base_widget_group_contract: str
    prediction_run_id: str | None = None
    packet_id: str | None = None
    generated_at: str | None = None
    market_uid: str | None = None
    supplemental_index_count: int = 0
    supplemental_widget_group_count: int = 0
    supplemental_widget_group_order: Tuple[str, ...] = ()
    supplemental_indexes: Tuple[Mapping[str, Any], ...] = ()
    auto_refresh_groups: Tuple[Mapping[str, Any], ...] = ()
    widget_groups: Tuple[Mapping[str, Any], ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
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
            "registry_version": self.registry_version,
            "registry_id": self.registry_id,
            "registry_kind": self.registry_kind,
            "base_widget_group_contract": self.base_widget_group_contract,
            "prediction_run_id": self.prediction_run_id,
            "packet_id": self.packet_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "supplemental_index_count": self.supplemental_index_count,
            "supplemental_widget_group_count": self.supplemental_widget_group_count,
            "supplemental_widget_group_order": list(self.supplemental_widget_group_order),
            "supplemental_indexes": [dict(item) for item in self.supplemental_indexes],
            "auto_refresh_groups": [dict(item) for item in self.auto_refresh_groups],
            "widget_groups": [dict(item) for item in self.widget_groups],
            "integration_contract": dict(self.integration_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
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


def _text_or_none(value: Any) -> str | None:
    return str(value) if value else None


def _safe_index_dict(index: Mapping[str, Any], *, source_kind: str, attach_default: str) -> Mapping[str, Any]:
    index_dict = dict(index)
    index_dict.update(
        {
            "source_kind": source_kind,
            "attach_after_widget_group_id": index.get("attach_after_widget_group_id") or attach_default,
            "read_only": True,
            "non_executing": True,
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
    )
    return index_dict


def _safe_widget_group(group: Mapping[str, Any], *, source_kind: str, attach_after: str) -> Mapping[str, Any]:
    group_dict = dict(group)
    payload = dict(_as_mapping(group_dict.get("payload")))
    payload.update(
        {
            "source_kind": source_kind,
            "attach_after_widget_group_id": payload.get("attach_after_widget_group_id") or attach_after,
            "actual_loader_execution_allowed": False,
            "actual_file_read_allowed_by_this_contract": False,
            "actual_payload_decode_allowed_by_this_contract": False,
            "would_load_hot_latest_artifacts": False,
            "would_read_runtime_file": False,
            "would_write_runtime_artifact": False,
            "would_send_to_broker": False,
            "display_only": True,
            "render_intent_only": True,
            "not_loaded_as_runtime_display_source": True,
        }
    )
    group_dict.update(
        {
            "source_kind": source_kind,
            "attach_after_widget_group_id": attach_after,
            "payload": payload,
            "read_only": True,
            "non_executing": True,
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
    )
    return group_dict


def _safe_auto_refresh_group(item: Mapping[str, Any], *, source_kind: str, attach_after: str) -> Mapping[str, Any]:
    group = dict(item)
    group.update(
        {
            "source_kind": source_kind,
            "attach_after_widget_group_id": group.get("attach_after_widget_group_id") or attach_after,
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
    )
    return group


def _append_index(
    *,
    index: Mapping[str, Any],
    source_kind: str,
    attach_default: str,
    indexes: list[Mapping[str, Any]],
    groups: list[Mapping[str, Any]],
    refresh_groups: list[Mapping[str, Any]],
) -> None:
    index_map = _safe_index_dict(index, source_kind=source_kind, attach_default=attach_default)
    indexes.append(index_map)
    attach_after = str(index_map.get("attach_after_widget_group_id") or attach_default)
    for group in _list(index_map.get("widget_groups")):
        groups.append(_safe_widget_group(_as_mapping(group), source_kind=source_kind, attach_after=attach_after))
    for refresh in _list(index_map.get("auto_refresh_groups")):
        refresh_groups.append(_safe_auto_refresh_group(_as_mapping(refresh), source_kind=source_kind, attach_after=attach_after))


def _authorization_registry_summary_panel_stub(*, packet: Mapping[str, Any], groups: list[Mapping[str, Any]]) -> Mapping[str, Any]:
    current_order = [str(group.get("widget_group_id") or "") for group in groups]
    order_with_summary = [*current_order, AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_ID]
    authorization_present = "prediction_latest_payload_loader_authorization_widget" in current_order
    source_present = "source_quality_explanation_widgets" in order_with_summary
    dry_run_present = "prediction_latest_payload_dry_run_status_widget" in order_with_summary
    visibility_count = 1 + sum(1 for present in (source_present, dry_run_present, authorization_present, True) if present)
    total_count = BASE_WIDGET_GROUP_COUNT + len(order_with_summary)
    panel_state = "ready_authorization_widget_visible_loader_disabled" if authorization_present else "blocked_authorization_widget_missing_loader_disabled"
    safe = {
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
    summary_metrics = {
        "base_widget_group_count": BASE_WIDGET_GROUP_COUNT,
        "supplemental_widget_group_count": len(order_with_summary),
        "total_widget_group_count": total_count,
        "visibility_group_count": visibility_count,
        "authorization_widget_present": authorization_present,
        "authorization_visibility_group_present": authorization_present,
        "authorization_attach_ok": authorization_present,
        "authorization_widget_order_index": order_with_summary.index("prediction_latest_payload_loader_authorization_widget") + BASE_WIDGET_GROUP_COUNT if authorization_present else None,
        "authorization_registry_summary_widget_present": True,
        "authorization_registry_summary_widget_order_index": len(order_with_summary) - 1 + BASE_WIDGET_GROUP_COUNT,
        "preflight_valid": True,
        "approval_granted_by_this_contract": False,
        "authorization_granted_by_this_contract": False,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
    }
    return {
        "panel_version": AUTHORIZATION_REGISTRY_SUMMARY_PANEL_VERSION,
        "panel_id": "prediction_latest_payload_loader_authorization_registry_summary_panel",
        "panel_kind": "latest_payload_loader_authorization_registry_summary",
        "panel_state": panel_state,
        "visibility_state": "visible_read_only" if authorization_present else "hidden_blocked_by_preflight",
        "handoff_state": "ready_for_read_only_warroom_handoff",
        "prediction_run_id": _text_or_none(packet.get("prediction_run_id")),
        "summary_metrics": summary_metrics,
        "authorization_visibility_summary": {
            "visibility_group_id": "prediction_warroom_loader_authorization_visibility",
            "visibility_kind": "supplemental_latest_payload_loader_authorization_status",
            "widget_group_ids": ["prediction_latest_payload_loader_authorization_widget"] if authorization_present else [],
            "attach_after_widget_group_id": "prediction_latest_payload_dry_run_status_widget",
            "ui_mount_hint": "warroom_prediction:supplemental:latest_payload_loader_authorization_status",
            "refresh_policy": "use_q6f_supplemental_auto_refresh_group",
            "order_strategy": "append_after_latest_payload_dry_run_status_widget",
            **safe,
        },
        "registry_path_summary": {
            "catalog_version": "prediction_warroom_handoff_catalog_visibility.ps_q6i.v1",
            "handoff_bundle_version": "prediction_warroom_supplemental_handoff_bundle.ps_q6h.v1",
            "handoff_state": "ready_for_read_only_warroom_handoff",
            "preflight_state": "ready_for_warroom_supplemental_handoff",
            "base_widget_group_order": [],
            "supplemental_widget_group_order": order_with_summary,
            "combined_widget_group_order": order_with_summary,
            "expected_authorization_widget_group_id": "prediction_latest_payload_loader_authorization_widget",
            "expected_authorization_attach_after_widget_group_id": "prediction_latest_payload_dry_run_status_widget",
            **safe,
        },
        "operator_guidance_ja": (
            "このpanelはQ7F registry登録用の表示要約で、承認記録・loader実行・hot/latest読取・payload decodeは行いません。",
            "実loaderや承認書込を進める場合は、別slice・別guard・別commitで扱ってください。",
        ),
        "boundaries": safe,
        **safe,
    }


def build_prediction_warroom_supplemental_widget_registry(
    *,
    display_packet: Mapping[str, Any] | Any | None = None,
    simulation_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
    latest_payload_loader_authorization_request: Mapping[str, Any] | Any | None = None,
    latest_payload_loader_permission_contract: Mapping[str, Any] | Any | None = None,
    include_source_quality_explanations: bool = True,
    include_latest_payload_dry_run: bool = True,
    include_latest_payload_loader_authorization: bool = True,
    include_latest_payload_loader_authorization_registry_summary: bool = True,
) -> PredictionWarRoomSupplementalWidgetRegistryPacket:
    """Build a composite supplemental widget registry without rendering, filesystem reads, or runtime side effects."""
    packet = _as_mapping(display_packet)
    indexes: list[Mapping[str, Any]] = []
    groups: list[Mapping[str, Any]] = []
    refresh_groups: list[Mapping[str, Any]] = []
    if include_source_quality_explanations:
        explanation_index = build_prediction_warroom_explanation_widget_group_index(packet).to_dict()
        _append_index(
            index=explanation_index,
            source_kind="source_quality_explanation_widget_group",
            attach_default="source_quality_widget",
            indexes=indexes,
            groups=groups,
            refresh_groups=refresh_groups,
        )
    if include_latest_payload_dry_run:
        dry_run_index = build_prediction_warroom_latest_payload_dry_run_widget_group_index(
            simulation_packet=simulation_packet,
            artifact_metadata_inputs=artifact_metadata_inputs,
            hot_latest_root_hint=hot_latest_root_hint,
        ).to_dict()
        _append_index(
            index=dry_run_index,
            source_kind="latest_payload_dry_run_widget_group",
            attach_default="warning_refresh_widget",
            indexes=indexes,
            groups=groups,
            refresh_groups=refresh_groups,
        )
    if include_latest_payload_loader_authorization:
        authorization_index = build_prediction_warroom_latest_payload_loader_authorization_widget_group_index(
            authorization_request=latest_payload_loader_authorization_request,
            permission_contract=latest_payload_loader_permission_contract,
            hot_latest_root_hint=hot_latest_root_hint,
        ).to_dict()
        _append_index(
            index=authorization_index,
            source_kind="latest_payload_loader_authorization_widget_group",
            attach_default="prediction_latest_payload_dry_run_status_widget",
            indexes=indexes,
            groups=groups,
            refresh_groups=refresh_groups,
        )
    if include_latest_payload_loader_authorization_registry_summary:
        from .prediction_warroom_loader_authorization_registry_summary_widget_groups import (
            build_prediction_warroom_loader_authorization_registry_summary_widget_group_index,
        )

        summary_index = build_prediction_warroom_loader_authorization_registry_summary_widget_group_index(
            summary_panel=_authorization_registry_summary_panel_stub(packet=packet, groups=groups),
            hot_latest_root_hint=hot_latest_root_hint,
        ).to_dict()
        _append_index(
            index=summary_index,
            source_kind="latest_payload_loader_authorization_registry_summary_widget_group",
            attach_default=AUTHORIZATION_REGISTRY_SUMMARY_ATTACH_AFTER_WIDGET_GROUP_ID,
            indexes=indexes,
            groups=groups,
            refresh_groups=refresh_groups,
        )
    order = tuple(str(group.get("widget_group_id") or "unknown") for group in groups)
    boundaries = {
        "read_only": True,
        "non_executing": True,
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
    integration_contract = {
        "contract_version": SUPPLEMENTAL_WIDGET_REGISTRY_VERSION,
        "base_widget_group_contract": WIDGET_GROUP_PACKET_VERSION,
        "source_quality_explanation_widget_contract": EXPLANATION_WIDGET_GROUP_VERSION,
        "latest_payload_dry_run_widget_contract": DRY_RUN_WIDGET_GROUP_VERSION,
        "latest_payload_loader_authorization_widget_contract": AUTHORIZATION_WIDGET_GROUP_VERSION,
        "latest_payload_loader_authorization_registry_summary_widget_contract": AUTHORIZATION_REGISTRY_SUMMARY_WIDGET_GROUP_VERSION,
        "integration_kind": "composite_supplemental_widget_registry",
        "supplemental_index_count": len(indexes),
        "supplemental_widget_group_count": len(groups),
        "does_not_modify_base_q4b_group_order": True,
        "append_strategy": "honor_each_supplemental_attach_after_widget_group_id",
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_without_side_effects": True,
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
    return PredictionWarRoomSupplementalWidgetRegistryPacket(
        registry_version=SUPPLEMENTAL_WIDGET_REGISTRY_VERSION,
        registry_id=f"{SUPPLEMENTAL_WIDGET_REGISTRY_VERSION}:supplemental:{len(groups)}",
        registry_kind="prediction_warroom_composite_supplemental_widget_registry",
        base_widget_group_contract=WIDGET_GROUP_PACKET_VERSION,
        prediction_run_id=_text_or_none(packet.get("prediction_run_id")),
        packet_id=_text_or_none(packet.get("packet_id")),
        generated_at=_text_or_none(packet.get("generated_at")),
        market_uid=_text_or_none(packet.get("market_uid")),
        supplemental_index_count=len(indexes),
        supplemental_widget_group_count=len(groups),
        supplemental_widget_group_order=order,
        supplemental_indexes=tuple(indexes),
        auto_refresh_groups=tuple(refresh_groups),
        widget_groups=tuple(groups),
        integration_contract=integration_contract,
        boundaries=boundaries,
    )
