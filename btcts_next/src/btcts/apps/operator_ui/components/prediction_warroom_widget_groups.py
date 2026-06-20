# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_widget_groups.py
# desc: Prediction WarRoom widget-group packet builder. Display grouping only; no Streamlit rendering, runtime loading, Collector, AutoTrade, broker, mode, or append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

WIDGET_GROUP_PACKET_VERSION = "prediction_warroom_widget_groups.ps_q4b.v1"


@dataclass(frozen=True)
class PredictionWarRoomWidgetGroupPacket:
    packet_version: str
    widget_group_id: str
    widget_group_label_ja: str
    widget_group_kind: str
    refresh_group_id: str
    refresh_interval_sec: int
    refresh_priority: int
    payload: Mapping[str, Any] = field(default_factory=dict)
    data_dependencies: Tuple[str, ...] = ()
    stale_behavior: str = "show_stale_badge_keep_last_packet"
    independent_refresh_allowed: bool = True
    ui_mount_hint: str = "warroom_prediction"
    read_only: bool = True
    non_executing: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packet_version": self.packet_version,
            "widget_group_id": self.widget_group_id,
            "widget_group_label_ja": self.widget_group_label_ja,
            "widget_group_kind": self.widget_group_kind,
            "refresh_group_id": self.refresh_group_id,
            "refresh_interval_sec": self.refresh_interval_sec,
            "refresh_priority": self.refresh_priority,
            "payload": dict(self.payload),
            "data_dependencies": list(self.data_dependencies),
            "stale_behavior": self.stale_behavior,
            "independent_refresh_allowed": self.independent_refresh_allowed,
            "ui_mount_hint": self.ui_mount_hint,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
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


def _cards_by_group(cards: list[Mapping[str, Any]], key: str) -> dict[str, list[Mapping[str, Any]]]:
    out: dict[str, list[Mapping[str, Any]]] = {}
    for raw in cards:
        card = _as_mapping(raw)
        group_key = str(card.get(key) or "unknown")
        out.setdefault(group_key, []).append(card)
    return out


def _group(
    *,
    widget_group_id: str,
    widget_group_label_ja: str,
    widget_group_kind: str,
    refresh_interval_sec: int,
    refresh_priority: int,
    payload: Mapping[str, Any],
    data_dependencies: Tuple[str, ...],
) -> PredictionWarRoomWidgetGroupPacket:
    return PredictionWarRoomWidgetGroupPacket(
        packet_version=WIDGET_GROUP_PACKET_VERSION,
        widget_group_id=widget_group_id,
        widget_group_label_ja=widget_group_label_ja,
        widget_group_kind=widget_group_kind,
        refresh_group_id=f"prediction_warroom:{widget_group_id}",
        refresh_interval_sec=refresh_interval_sec,
        refresh_priority=refresh_priority,
        payload=dict(payload),
        data_dependencies=data_dependencies,
    )


def build_prediction_warroom_widget_group_packets(display_packet: Mapping[str, Any] | Any) -> Tuple[PredictionWarRoomWidgetGroupPacket, ...]:
    """Split a PredictionWarRoomDisplayPacket into display-only widget group packets for future WarRoom auto-refresh."""
    packet = _as_mapping(display_packet)
    horizon_cards = [_as_mapping(item) for item in _list(packet.get("horizon_cards"))]
    family_cards = [_as_mapping(item) for item in _list(packet.get("family_cards"))]
    primary_signal = _as_mapping(packet.get("primary_signal_summary"))
    source_quality = _as_mapping(packet.get("source_quality_panel"))
    evidence = _as_mapping(packet.get("evidence_panel"))
    warnings = _as_mapping(packet.get("warning_panel"))
    ui_contract = _as_mapping(packet.get("ui_contract"))
    boundaries = _as_mapping(packet.get("boundaries"))
    base_context = {
        "prediction_run_id": packet.get("prediction_run_id"),
        "packet_id": packet.get("packet_id"),
        "generated_at": packet.get("generated_at"),
        "market_uid": packet.get("market_uid"),
        "headline_ja": packet.get("headline_ja"),
        "ui_contract": dict(ui_contract),
        "boundaries": dict(boundaries),
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
    }
    by_horizon = _cards_by_group(horizon_cards, "horizon_group")
    by_family = _cards_by_group(family_cards, "family")
    groups = (
        _group(
            widget_group_id="primary_signal_widget",
            widget_group_label_ja="予測シグナル",
            widget_group_kind="primary_signal",
            refresh_interval_sec=15,
            refresh_priority=10,
            data_dependencies=("display_packet.primary_signal_summary", "display_packet.headline_ja", "display_packet.boundaries"),
            payload={**base_context, "primary_signal_summary": dict(primary_signal)},
        ),
        _group(
            widget_group_id="horizon_scenario_widgets",
            widget_group_label_ja="時間軸別シナリオ",
            widget_group_kind="horizon_scenarios",
            refresh_interval_sec=30,
            refresh_priority=20,
            data_dependencies=("display_packet.horizon_cards", "scenario_lite", "signal_strength_summary"),
            payload={**base_context, "horizon_cards": [dict(item) for item in horizon_cards], "horizon_cards_by_group": {key: [dict(item) for item in value] for key, value in by_horizon.items()}},
        ),
        _group(
            widget_group_id="family_detail_widgets",
            widget_group_label_ja="推論ファミリー詳細",
            widget_group_kind="family_details",
            refresh_interval_sec=30,
            refresh_priority=30,
            data_dependencies=("display_packet.family_cards", "source_contribution_ledger", "context_profile_source_caps"),
            payload={**base_context, "family_cards": [dict(item) for item in family_cards], "family_cards_by_family": {key: [dict(item) for item in value] for key, value in by_family.items()}},
        ),
        _group(
            widget_group_id="source_quality_widget",
            widget_group_label_ja="情報源品質",
            widget_group_kind="source_quality",
            refresh_interval_sec=30,
            refresh_priority=40,
            data_dependencies=("display_packet.source_quality_panel", "tier0_source_quality_gate", "source_artifact_coverage"),
            payload={**base_context, "source_quality_panel": dict(source_quality)},
        ),
        _group(
            widget_group_id="evidence_ledger_widget",
            widget_group_label_ja="根拠・寄与台帳",
            widget_group_kind="evidence_ledger",
            refresh_interval_sec=60,
            refresh_priority=50,
            data_dependencies=("display_packet.evidence_panel", "source_contribution_ledger", "scenario_trace"),
            payload={**base_context, "evidence_panel": dict(evidence), "source_contribution_ledger_count": evidence.get("source_contribution_ledger_count")},
        ),
        _group(
            widget_group_id="warning_refresh_widget",
            widget_group_label_ja="警告・更新監視",
            widget_group_kind="warning_refresh",
            refresh_interval_sec=15,
            refresh_priority=60,
            data_dependencies=("display_packet.warning_panel", "prediction_unavailable_reasons", "signal_strength_cap_reasons"),
            payload={**base_context, "warning_panel": dict(warnings)},
        ),
    )
    return groups


def build_prediction_warroom_widget_group_packet_index(display_packet: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Return a serializable index for all display-only Prediction WarRoom widget groups."""
    groups = build_prediction_warroom_widget_group_packets(display_packet)
    packet = _as_mapping(display_packet)
    return {
        "index_version": WIDGET_GROUP_PACKET_VERSION,
        "prediction_run_id": packet.get("prediction_run_id"),
        "packet_id": packet.get("packet_id"),
        "generated_at": packet.get("generated_at"),
        "market_uid": packet.get("market_uid"),
        "widget_group_count": len(groups),
        "widget_group_order": [group.widget_group_id for group in groups],
        "auto_refresh_groups": [
            {
                "widget_group_id": group.widget_group_id,
                "refresh_group_id": group.refresh_group_id,
                "refresh_interval_sec": group.refresh_interval_sec,
                "refresh_priority": group.refresh_priority,
                "data_dependencies": list(group.data_dependencies),
                "independent_refresh_allowed": group.independent_refresh_allowed,
                "stale_behavior": group.stale_behavior,
            }
            for group in groups
        ],
        "widget_groups": [group.to_dict() for group in groups],
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_collect_public_source": False,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
    }
