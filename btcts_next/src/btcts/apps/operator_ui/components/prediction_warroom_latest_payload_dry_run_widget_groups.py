# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_dry_run_widget_groups.py
# desc: Supplemental widget-group index for Prediction WarRoom latest-payload dry-run status panel. Display grouping only; no file access, payload decode, Streamlit rendering, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_latest_payload_dry_run_status_panel import (
    DRY_RUN_STATUS_PANEL_VERSION,
    build_prediction_warroom_latest_payload_dry_run_status_panel,
)
from .prediction_warroom_latest_payload_loader_dry_run_simulator import LOADER_DRY_RUN_SIMULATOR_VERSION
from .prediction_warroom_widget_groups import PredictionWarRoomWidgetGroupPacket

DRY_RUN_WIDGET_GROUP_VERSION = "prediction_warroom_latest_payload_dry_run_widget_groups.ps_q6e.v1"
DRY_RUN_WIDGET_GROUP_ID = "prediction_latest_payload_dry_run_status_widget"
ATTACH_AFTER_WIDGET_GROUP_ID = "warning_refresh_widget"


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadDryRunWidgetGroupIndex:
    index_version: str
    supplemental_widget_group_count: int = 0
    attach_after_widget_group_id: str = ATTACH_AFTER_WIDGET_GROUP_ID
    supplemental_widget_group_order: Tuple[str, ...] = ()
    auto_refresh_groups: Tuple[Mapping[str, Any], ...] = ()
    widget_groups: Tuple[Mapping[str, Any], ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    source_panel_version: str = DRY_RUN_STATUS_PANEL_VERSION
    source_simulation_version: str = LOADER_DRY_RUN_SIMULATOR_VERSION
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
            "index_version": self.index_version,
            "supplemental_widget_group_count": self.supplemental_widget_group_count,
            "attach_after_widget_group_id": self.attach_after_widget_group_id,
            "supplemental_widget_group_order": list(self.supplemental_widget_group_order),
            "auto_refresh_groups": [dict(item) for item in self.auto_refresh_groups],
            "widget_groups": [dict(item) for item in self.widget_groups],
            "integration_contract": dict(self.integration_contract),
            "source_panel_version": self.source_panel_version,
            "source_simulation_version": self.source_simulation_version,
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


def build_prediction_warroom_latest_payload_dry_run_widget_group_packet(
    *,
    simulation_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomWidgetGroupPacket:
    """Build a supplemental display-only widget group for the Q6D latest-payload dry-run status panel."""
    panel = build_prediction_warroom_latest_payload_dry_run_status_panel(
        simulation_packet=simulation_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    ).to_dict()
    payload = {
        "panel_version": panel.get("panel_version"),
        "panel_id": panel.get("panel_id"),
        "panel_state": panel.get("panel_state"),
        "headline_ja": panel.get("headline_ja"),
        "status_badge": dict(_as_mapping(panel.get("status_badge"))),
        "summary_metrics": dict(_as_mapping(panel.get("summary_metrics"))),
        "artifact_status_cards": list(panel.get("artifact_status_cards") or ()),
        "blocked_reason_cards": list(panel.get("blocked_reason_cards") or ()),
        "warning_reason_cards": list(panel.get("warning_reason_cards") or ()),
        "operator_guidance_ja": list(panel.get("operator_guidance_ja") or ()),
        "ui_contract": dict(_as_mapping(panel.get("ui_contract"))),
        "boundaries": dict(_as_mapping(panel.get("boundaries"))),
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        "source_panel_version": DRY_RUN_STATUS_PANEL_VERSION,
        "source_simulation_version": panel.get("source_simulation_version") or LOADER_DRY_RUN_SIMULATOR_VERSION,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "actual_payload_decode_allowed_by_this_contract": False,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
    }
    return PredictionWarRoomWidgetGroupPacket(
        packet_version=DRY_RUN_WIDGET_GROUP_VERSION,
        widget_group_id=DRY_RUN_WIDGET_GROUP_ID,
        widget_group_label_ja="最新payload dry-run状態",
        widget_group_kind="latest_payload_dry_run_status",
        refresh_group_id=f"prediction_warroom:{DRY_RUN_WIDGET_GROUP_ID}",
        refresh_interval_sec=int(panel.get("refresh_interval_sec") or 30),
        refresh_priority=int(panel.get("refresh_priority") or 55),
        payload=payload,
        data_dependencies=(
            "q6c.latest_payload_loader_dry_run_simulation",
            "q6d.latest_payload_dry_run_status_panel",
            "q6b.loader_permission_contract",
            "q6a.latest_payload_preflight_status",
        ),
        stale_behavior=str(panel.get("stale_behavior") or "show_blocked_or_stale_badge_keep_last_good_packet"),
        independent_refresh_allowed=True,
        ui_mount_hint="warroom_prediction:latest_payload_dry_run_status",
    )


def build_prediction_warroom_latest_payload_dry_run_widget_group_index(
    *,
    simulation_packet: Mapping[str, Any] | Any | None = None,
    artifact_metadata_inputs: Iterable[Mapping[str, Any]] | None = None,
    hot_latest_root_hint: str = "D:\\btc_ts_hot",
) -> PredictionWarRoomLatestPayloadDryRunWidgetGroupIndex:
    """Return supplemental widget-group metadata for the latest-payload dry-run panel without rendering or file reads."""
    group = build_prediction_warroom_latest_payload_dry_run_widget_group_packet(
        simulation_packet=simulation_packet,
        artifact_metadata_inputs=artifact_metadata_inputs,
        hot_latest_root_hint=hot_latest_root_hint,
    )
    group_dict = group.to_dict()
    group_dict.update(
        {
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
    payload = dict(group_dict.get("payload") or {})
    payload.update(
        {
            "actual_loader_execution_allowed": False,
            "actual_file_read_allowed_by_this_contract": False,
            "actual_payload_decode_allowed_by_this_contract": False,
            "would_load_hot_latest_artifacts": False,
            "would_read_runtime_file": False,
            "would_write_runtime_artifact": False,
            "would_send_to_broker": False,
        }
    )
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
        "actual_loader_execution_allowed": False,
        "would_read_runtime_file": False,
        "would_write_runtime_artifact": False,
    }
    integration_contract = {
        "contract_version": DRY_RUN_WIDGET_GROUP_VERSION,
        "dry_run_status_panel_contract": DRY_RUN_STATUS_PANEL_VERSION,
        "loader_dry_run_simulator_contract": LOADER_DRY_RUN_SIMULATOR_VERSION,
        "integration_kind": "supplemental_widget_group_append_after_warning_refresh",
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        "does_not_modify_base_q4b_group_order": True,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_payload_decode": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_without_side_effects": True,
        "actual_loader_execution_allowed": False,
        "actual_file_read_allowed_by_this_contract": False,
        "read_only": True,
        "non_executing": True,
    }
    return PredictionWarRoomLatestPayloadDryRunWidgetGroupIndex(
        index_version=DRY_RUN_WIDGET_GROUP_VERSION,
        supplemental_widget_group_count=1,
        attach_after_widget_group_id=ATTACH_AFTER_WIDGET_GROUP_ID,
        supplemental_widget_group_order=(group.widget_group_id,),
        auto_refresh_groups=(auto_refresh,),
        widget_groups=(group_dict,),
        integration_contract=integration_contract,
    )
