# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_handoff_catalog_visibility.py
# desc: Read-only catalog/visibility contract for Prediction WarRoom handoff bundles. Discovery metadata only; no rendering, file access, payload decode, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_supplemental_handoff_bundle import (
    SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION,
    build_prediction_warroom_supplemental_handoff_bundle,
)

HANDOFF_CATALOG_VISIBILITY_VERSION = "prediction_warroom_handoff_catalog_visibility.ps_q6i.v1"
BASE_WIDGET_GROUP_VISIBILITY_ID = "prediction_warroom_base_widget_groups_visibility"
SOURCE_EXPLANATION_VISIBILITY_ID = "prediction_warroom_source_explanation_visibility"
LATEST_PAYLOAD_DRY_RUN_VISIBILITY_ID = "prediction_warroom_latest_payload_dry_run_visibility"
LOADER_AUTHORIZATION_VISIBILITY_ID = "prediction_warroom_loader_authorization_visibility"
LOADER_AUTHORIZATION_REGISTRY_SUMMARY_VISIBILITY_ID = "prediction_warroom_loader_authorization_registry_summary_visibility"
AUTHORIZATION_HANDOFF_STATUS_VISIBILITY_ID = "prediction_warroom_authorization_handoff_status_visibility"


@dataclass(frozen=True)
class PredictionWarRoomHandoffCatalogVisibilityEntry:
    catalog_version: str
    catalog_entry_id: str
    catalog_entry_kind: str
    visibility_state: str
    handoff_bundle_version: str
    handoff_bundle_id: str | None = None
    handoff_state: str | None = None
    prediction_run_id: str | None = None
    consumer_hint: str = "WarRoom"
    handoff_index: Mapping[str, Any] = field(default_factory=dict)
    visibility_groups: Tuple[Mapping[str, Any], ...] = ()
    visibility_group_count: int = 0
    base_widget_group_count: int = 0
    supplemental_widget_group_count: int = 0
    total_widget_group_count: int = 0
    combined_widget_group_order: Tuple[str, ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    boundaries: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    catalog_only: bool = True
    visibility_metadata_only: bool = True
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
            "catalog_version": self.catalog_version,
            "catalog_entry_id": self.catalog_entry_id,
            "catalog_entry_kind": self.catalog_entry_kind,
            "visibility_state": self.visibility_state,
            "handoff_bundle_version": self.handoff_bundle_version,
            "handoff_bundle_id": self.handoff_bundle_id,
            "handoff_state": self.handoff_state,
            "prediction_run_id": self.prediction_run_id,
            "consumer_hint": self.consumer_hint,
            "handoff_index": dict(self.handoff_index),
            "visibility_groups": [dict(item) for item in self.visibility_groups],
            "visibility_group_count": self.visibility_group_count,
            "base_widget_group_count": self.base_widget_group_count,
            "supplemental_widget_group_count": self.supplemental_widget_group_count,
            "total_widget_group_count": self.total_widget_group_count,
            "combined_widget_group_order": list(self.combined_widget_group_order),
            "integration_contract": dict(self.integration_contract),
            "boundaries": dict(self.boundaries),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "catalog_only": self.catalog_only,
            "visibility_metadata_only": self.visibility_metadata_only,
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


def _safe_flags() -> Dict[str, Any]:
    return {
        "read_only": True,
        "non_executing": True,
        "catalog_only": True,
        "visibility_metadata_only": True,
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


def _visibility_group(
    *,
    visibility_group_id: str,
    visibility_label_ja: str,
    visibility_kind: str,
    widget_group_ids: tuple[str, ...],
    attach_after_widget_group_id: str | None,
    ui_mount_hint: str,
    refresh_policy: str,
    order_strategy: str,
) -> Mapping[str, Any]:
    return {
        "visibility_group_id": visibility_group_id,
        "visibility_label_ja": visibility_label_ja,
        "visibility_kind": visibility_kind,
        "widget_group_ids": list(widget_group_ids),
        "widget_group_count": len(widget_group_ids),
        "attach_after_widget_group_id": attach_after_widget_group_id,
        "ui_mount_hint": ui_mount_hint,
        "refresh_policy": refresh_policy,
        "order_strategy": order_strategy,
        "visibility_state_when_handoff_ready": "visible_read_only",
        "visibility_state_when_handoff_blocked": "hidden_blocked_by_preflight",
        **_safe_flags(),
    }


def _build_visibility_groups(handoff_index: Mapping[str, Any]) -> Tuple[Mapping[str, Any], ...]:
    base_order = tuple(str(item) for item in _list(handoff_index.get("base_widget_group_order")))
    supplemental_order = tuple(str(item) for item in _list(handoff_index.get("supplemental_widget_group_order")))
    source_explanation = tuple(item for item in supplemental_order if item == "source_quality_explanation_widgets")
    latest_payload = tuple(item for item in supplemental_order if item == "prediction_latest_payload_dry_run_status_widget")
    loader_authorization = tuple(item for item in supplemental_order if item == "prediction_latest_payload_loader_authorization_widget")
    loader_authorization_summary = tuple(item for item in supplemental_order if item == "prediction_latest_payload_loader_authorization_registry_summary_widget")
    authorization_handoff_status = tuple(item for item in supplemental_order if item == "prediction_authorization_handoff_status_widget")
    return (
        _visibility_group(
            visibility_group_id=BASE_WIDGET_GROUP_VISIBILITY_ID,
            visibility_label_ja="予測WarRoom基本widget群",
            visibility_kind="base_prediction_widget_groups",
            widget_group_ids=base_order,
            attach_after_widget_group_id=None,
            ui_mount_hint="warroom_prediction:base_widget_groups",
            refresh_policy="use_q4b_auto_refresh_groups",
            order_strategy="render_in_q4b_base_widget_group_order",
        ),
        _visibility_group(
            visibility_group_id=SOURCE_EXPLANATION_VISIBILITY_ID,
            visibility_label_ja="情報源品質説明widget",
            visibility_kind="supplemental_source_quality_explanation",
            widget_group_ids=source_explanation,
            attach_after_widget_group_id="source_quality_widget",
            ui_mount_hint="warroom_prediction:supplemental:source_quality_explanation",
            refresh_policy="use_q6f_supplemental_auto_refresh_group",
            order_strategy="append_after_source_quality_widget",
        ),
        _visibility_group(
            visibility_group_id=LATEST_PAYLOAD_DRY_RUN_VISIBILITY_ID,
            visibility_label_ja="最新payload dry-run状態widget",
            visibility_kind="supplemental_latest_payload_dry_run_status",
            widget_group_ids=latest_payload,
            attach_after_widget_group_id="warning_refresh_widget",
            ui_mount_hint="warroom_prediction:supplemental:latest_payload_dry_run_status",
            refresh_policy="use_q6f_supplemental_auto_refresh_group",
            order_strategy="append_after_warning_refresh_widget",
        ),
        _visibility_group(
            visibility_group_id=LOADER_AUTHORIZATION_VISIBILITY_ID,
            visibility_label_ja="最新payload loader承認状態widget",
            visibility_kind="supplemental_latest_payload_loader_authorization_status",
            widget_group_ids=loader_authorization,
            attach_after_widget_group_id="prediction_latest_payload_dry_run_status_widget",
            ui_mount_hint="warroom_prediction:supplemental:latest_payload_loader_authorization_status",
            refresh_policy="use_q6f_supplemental_auto_refresh_group",
            order_strategy="append_after_latest_payload_dry_run_status_widget",
        ),
        _visibility_group(
            visibility_group_id=LOADER_AUTHORIZATION_REGISTRY_SUMMARY_VISIBILITY_ID,
            visibility_label_ja="loader承認registry要約widget",
            visibility_kind="supplemental_latest_payload_loader_authorization_registry_summary",
            widget_group_ids=loader_authorization_summary,
            attach_after_widget_group_id="prediction_latest_payload_loader_authorization_widget",
            ui_mount_hint="warroom_prediction:supplemental:latest_payload_loader_authorization_registry_summary",
            refresh_policy="use_q6f_supplemental_auto_refresh_group",
            order_strategy="append_after_latest_payload_loader_authorization_widget",
        ),
        _visibility_group(
            visibility_group_id=AUTHORIZATION_HANDOFF_STATUS_VISIBILITY_ID,
            visibility_label_ja="authorization handoff状態widget",
            visibility_kind="supplemental_authorization_handoff_status",
            widget_group_ids=authorization_handoff_status,
            attach_after_widget_group_id="prediction_latest_payload_loader_authorization_registry_summary_widget",
            ui_mount_hint="warroom_prediction:supplemental:authorization_handoff_status",
            refresh_policy="use_q6f_supplemental_auto_refresh_group",
            order_strategy="append_after_authorization_registry_summary_widget",
        ),
    )


def build_prediction_warroom_handoff_catalog_visibility_entry(
    *,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomHandoffCatalogVisibilityEntry:
    """Build a read-only catalog entry describing WarRoom handoff bundle visibility."""
    bundle = dict(_as_mapping(handoff_bundle)) if handoff_bundle is not None else build_prediction_warroom_supplemental_handoff_bundle(
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    handoff_index = dict(_as_mapping(bundle.get("handoff_index")))
    preflight = _as_mapping(bundle.get("supplemental_registry_preflight_report"))
    ready = bundle.get("handoff_state") == "ready_for_read_only_warroom_handoff" and preflight.get("valid") is True
    visibility_state = "visible_read_only" if ready else "hidden_blocked_by_preflight"
    visibility_groups = _build_visibility_groups(handoff_index)
    combined_order = tuple(str(item) for item in _list(handoff_index.get("combined_widget_group_order")))
    boundaries = _safe_flags()
    integration_contract = {
        "contract_version": HANDOFF_CATALOG_VISIBILITY_VERSION,
        "handoff_bundle_contract": SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION,
        "integration_kind": "prediction_warroom_read_only_handoff_catalog_visibility",
        "consumer_hint": "WarRoom",
        "catalog_entry_discovery_only": True,
        "visibility_metadata_only": True,
        "does_not_modify_handoff_bundle_payloads": True,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_without_side_effects": True,
        **_safe_flags(),
    }
    return PredictionWarRoomHandoffCatalogVisibilityEntry(
        catalog_version=HANDOFF_CATALOG_VISIBILITY_VERSION,
        catalog_entry_id=f"{HANDOFF_CATALOG_VISIBILITY_VERSION}:{bundle.get('handoff_bundle_id') or 'unknown'}",
        catalog_entry_kind="prediction_warroom_read_only_handoff_visibility_contract",
        visibility_state=visibility_state,
        handoff_bundle_version=str(bundle.get("handoff_bundle_version") or SUPPLEMENTAL_HANDOFF_BUNDLE_VERSION),
        handoff_bundle_id=str(bundle.get("handoff_bundle_id")) if bundle.get("handoff_bundle_id") else None,
        handoff_state=str(bundle.get("handoff_state")) if bundle.get("handoff_state") else None,
        prediction_run_id=str(bundle.get("prediction_run_id")) if bundle.get("prediction_run_id") else None,
        handoff_index=handoff_index,
        visibility_groups=visibility_groups,
        visibility_group_count=len(visibility_groups),
        base_widget_group_count=int(handoff_index.get("base_widget_group_count") or 0),
        supplemental_widget_group_count=int(handoff_index.get("supplemental_widget_group_count") or 0),
        total_widget_group_count=int(handoff_index.get("total_widget_group_count") or len(combined_order)),
        combined_widget_group_order=combined_order,
        integration_contract=integration_contract,
        boundaries=boundaries,
    )


def build_prediction_warroom_handoff_catalog_visibility_index(
    *,
    handoff_bundle: Mapping[str, Any] | Any | None = None,
    display_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> Dict[str, Any]:
    """Return a compact catalog/visibility index for Prediction WarRoom handoff discovery."""
    entry = build_prediction_warroom_handoff_catalog_visibility_entry(
        handoff_bundle=handoff_bundle,
        display_packet=display_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    return {
        "catalog_index_version": HANDOFF_CATALOG_VISIBILITY_VERSION,
        "catalog_entry_id": entry.get("catalog_entry_id"),
        "catalog_entry_kind": entry.get("catalog_entry_kind"),
        "visibility_state": entry.get("visibility_state"),
        "handoff_bundle_id": entry.get("handoff_bundle_id"),
        "handoff_bundle_version": entry.get("handoff_bundle_version"),
        "handoff_state": entry.get("handoff_state"),
        "prediction_run_id": entry.get("prediction_run_id"),
        "consumer_hint": entry.get("consumer_hint"),
        "visibility_group_count": entry.get("visibility_group_count"),
        "base_widget_group_count": entry.get("base_widget_group_count"),
        "supplemental_widget_group_count": entry.get("supplemental_widget_group_count"),
        "total_widget_group_count": entry.get("total_widget_group_count"),
        "combined_widget_group_order": list(entry.get("combined_widget_group_order") or ()),
        "visibility_groups": [dict(item) for item in _list(entry.get("visibility_groups"))],
        "integration_contract": dict(_as_mapping(entry.get("integration_contract"))),
        "boundaries": dict(_as_mapping(entry.get("boundaries"))),
        **_safe_flags(),
    }
