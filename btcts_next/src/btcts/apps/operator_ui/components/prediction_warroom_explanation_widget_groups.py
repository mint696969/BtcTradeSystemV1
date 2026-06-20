# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_explanation_widget_groups.py
# desc: Supplemental widget-group metadata for Prediction WarRoom source-quality explanation panels. Display grouping only; no rendering, runtime reads, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_source_quality_explanations import build_prediction_warroom_source_quality_explanation_panel
from .prediction_warroom_widget_groups import PredictionWarRoomWidgetGroupPacket

EXPLANATION_WIDGET_GROUP_VERSION = "prediction_warroom_explanation_widget_groups.ps_q5b.v1"
EXPLANATION_WIDGET_GROUP_ID = "source_quality_explanation_widgets"
ATTACH_AFTER_WIDGET_GROUP_ID = "source_quality_widget"


@dataclass(frozen=True)
class PredictionWarRoomExplanationWidgetGroupIndex:
    index_version: str
    prediction_run_id: str | None = None
    packet_id: str | None = None
    generated_at: str | None = None
    market_uid: str | None = None
    supplemental_widget_group_count: int = 0
    attach_after_widget_group_id: str = ATTACH_AFTER_WIDGET_GROUP_ID
    supplemental_widget_group_order: Tuple[str, ...] = ()
    auto_refresh_groups: Tuple[Mapping[str, Any], ...] = ()
    widget_groups: Tuple[Mapping[str, Any], ...] = ()
    integration_contract: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index_version": self.index_version,
            "prediction_run_id": self.prediction_run_id,
            "packet_id": self.packet_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "supplemental_widget_group_count": self.supplemental_widget_group_count,
            "attach_after_widget_group_id": self.attach_after_widget_group_id,
            "supplemental_widget_group_order": list(self.supplemental_widget_group_order),
            "auto_refresh_groups": [dict(item) for item in self.auto_refresh_groups],
            "widget_groups": [dict(item) for item in self.widget_groups],
            "integration_contract": dict(self.integration_contract),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
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


def build_prediction_warroom_explanation_widget_group_packet(display_packet: Mapping[str, Any] | Any) -> PredictionWarRoomWidgetGroupPacket:
    """Build a supplemental display-only widget group for Q5A source-quality explanation cards."""
    packet = _as_mapping(display_packet)
    panel = build_prediction_warroom_source_quality_explanation_panel(packet).to_dict()
    signal_cap_count = len(_list(panel.get("signal_cap_explanations")))
    missing_source_card_count = len(_list(panel.get("missing_source_cards")))
    family_cap_count = len(_list(panel.get("family_cap_cards")))
    gate_card_count = len(_list(panel.get("source_quality_gate_cards")))
    watch_point_count = len(_list(panel.get("watch_points")))
    payload = {
        "prediction_run_id": packet.get("prediction_run_id"),
        "packet_id": packet.get("packet_id"),
        "generated_at": packet.get("generated_at"),
        "market_uid": packet.get("market_uid"),
        "explanation_panel": panel,
        "signal_cap_explanation_count": signal_cap_count,
        "missing_source_card_count": missing_source_card_count,
        "family_cap_card_count": family_cap_count,
        "source_quality_gate_card_count": gate_card_count,
        "watch_point_count": watch_point_count,
        "operator_summary_ja": panel.get("operator_summary_ja"),
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
    }
    return PredictionWarRoomWidgetGroupPacket(
        packet_version=EXPLANATION_WIDGET_GROUP_VERSION,
        widget_group_id=EXPLANATION_WIDGET_GROUP_ID,
        widget_group_label_ja="参考度・情報源説明",
        widget_group_kind="source_quality_explanations",
        refresh_group_id=f"prediction_warroom:{EXPLANATION_WIDGET_GROUP_ID}",
        refresh_interval_sec=30,
        refresh_priority=45,
        payload=payload,
        data_dependencies=(
            "display_packet.primary_signal_summary.signal_strength_cap_reasons",
            "display_packet.source_quality_panel.tier0_source_quality_gate",
            "display_packet.source_quality_panel.source_artifact_coverage",
            "display_packet.family_cards.context_profile_source_caps",
            "display_packet.warning_panel.signal_strength_cap_reasons",
        ),
        stale_behavior="show_stale_badge_keep_last_explanation_panel",
        independent_refresh_allowed=True,
        ui_mount_hint="warroom_prediction:source_quality_explanations",
    )


def build_prediction_warroom_explanation_widget_group_index(display_packet: Mapping[str, Any] | Any) -> PredictionWarRoomExplanationWidgetGroupIndex:
    """Return supplemental widget-group metadata for Q5A explanation cards without changing Q4B base group order."""
    packet = _as_mapping(display_packet)
    group = build_prediction_warroom_explanation_widget_group_packet(packet)
    group_dict = group.to_dict()
    # Q4B's base PredictionWarRoomWidgetGroupPacket predates explicit hot-loader flags.
    # Q5B is the supplemental integration boundary, so it makes those guarantees explicit
    # without changing the Q4B base widget packet contract/order.
    group_dict.update(
        {
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
    }
    integration_contract = {
        "contract_version": EXPLANATION_WIDGET_GROUP_VERSION,
        "base_widget_group_contract": "prediction_warroom_widget_groups.ps_q4b.v1",
        "explanation_panel_contract": "prediction_warroom_source_quality_explanations.ps_q5a.v1",
        "integration_kind": "supplemental_widget_group_append_after_source_quality",
        "does_not_modify_base_q4b_group_order": True,
        "attach_after_widget_group_id": ATTACH_AFTER_WIDGET_GROUP_ID,
        "requires_runtime_loader": False,
        "requires_hot_file_read": False,
        "requires_streamlit_rendering": False,
        "safe_to_render_without_side_effects": True,
        "read_only": True,
        "non_executing": True,
    }
    return PredictionWarRoomExplanationWidgetGroupIndex(
        index_version=EXPLANATION_WIDGET_GROUP_VERSION,
        prediction_run_id=str(packet.get("prediction_run_id")) if packet.get("prediction_run_id") else None,
        packet_id=str(packet.get("packet_id")) if packet.get("packet_id") else None,
        generated_at=str(packet.get("generated_at")) if packet.get("generated_at") else None,
        market_uid=str(packet.get("market_uid")) if packet.get("market_uid") else None,
        supplemental_widget_group_count=1,
        attach_after_widget_group_id=ATTACH_AFTER_WIDGET_GROUP_ID,
        supplemental_widget_group_order=(group.widget_group_id,),
        auto_refresh_groups=(auto_refresh,),
        widget_groups=(group_dict,),
        integration_contract=integration_contract,
    )
