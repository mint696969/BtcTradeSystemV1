# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py
# desc: PS-Q9G guarded Streamlit review panel for lowered Prediction WarRoom display-packet visibility. Renders a read-only review surface from supplied/in-memory contract data only; no file reads, payload decode, loader execution, runtime writes, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from typing import Any, Mapping

import streamlit as st

from .prediction_warroom_lowered_display_packet_visibility_review_contract import (
    LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION,
    build_prediction_warroom_lowered_display_packet_visibility_review_contract,
)

PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION = "prediction_warroom_lowered_display_packet_visibility_review_panel.ps_q9g.v1"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _widget_candidate_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in _list(packet.get("widget_candidates")):
        item = _as_mapping(raw)
        rows.append(
            {
                "widget_group_id": item.get("widget_group_id"),
                "label_ja": item.get("widget_group_label_ja"),
                "kind": item.get("widget_group_kind"),
                "refresh_sec": item.get("refresh_interval_sec"),
                "priority": item.get("refresh_priority"),
                "visible": item.get("visible_in_review"),
                "render": "review_only",
                "page_mutation": "false",
                "loader": "false",
                "autotrade": "false",
                "broker": "false",
            }
        )
    return rows


def _metric_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"name": "contract_state", "value": packet.get("contract_state")},
        {"name": "operator_visible_readiness_state", "value": packet.get("operator_visible_readiness_state")},
        {"name": "ready_for_ps_q9g_guarded_ui_mount", "value": packet.get("ready_for_ps_q9g_guarded_ui_mount")},
        {"name": "display_packet_present", "value": packet.get("display_packet_present")},
        {"name": "display_packet_valid", "value": packet.get("display_packet_valid")},
        {"name": "widget_group_index_built", "value": packet.get("widget_group_index_built")},
        {"name": "widget_group_count", "value": packet.get("widget_group_count")},
        {"name": "visible_widget_group_count", "value": packet.get("visible_widget_group_count")},
        {"name": "blocker_count", "value": packet.get("blocker_count")},
        {"name": "warning_count", "value": packet.get("warning_count")},
    ]


def _boundary_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"boundary": "streamlit_review_panel", "enabled": True},
        {"boundary": "warroom_card_rendering", "enabled": False},
        {"boundary": "warroom_page_mutation_after_this_mount", "enabled": False},
        {"boundary": "ui_triggered_loader_execution", "enabled": False},
        {"boundary": "runtime_file_read", "enabled": False},
        {"boundary": "payload_decode", "enabled": False},
        {"boundary": "runtime_artifact_write", "enabled": False},
        {"boundary": "approval_or_authorization_grant", "enabled": False},
        {"boundary": "decision_or_command_ledger_append", "enabled": False},
        {"boundary": "autotrade_trigger", "enabled": False},
        {"boundary": "broker_private_api", "enabled": False},
        {"boundary": "contract_version", "enabled": packet.get("contract_version") == LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION},
    ]


def render_prediction_warroom_lowered_display_packet_visibility_review_panel(
    *,
    review_packet: Mapping[str, Any] | Any | None = None,
) -> None:
    """Render a guarded read-only PS-Q9G review panel without loader/runtime side effects."""
    packet = _as_mapping(review_packet)
    if not packet:
        packet = build_prediction_warroom_lowered_display_packet_visibility_review_contract().to_dict()
    st.caption(
        "Lowered display-packet visibility review is read-only: "
        "no loader, no file read, no payload decode, no approval, no AutoTrade, no broker."
    )
    st.caption(
        "panel_version={panel}; contract_state={state}; ready_for_ui_mount={ready}; widgets={widgets}; blockers={blockers}; warnings={warnings}".format(
            panel=PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION,
            state=packet.get("contract_state"),
            ready=packet.get("ready_for_ps_q9g_guarded_ui_mount"),
            widgets=packet.get("visible_widget_group_count"),
            blockers=packet.get("blocker_count"),
            warnings=packet.get("warning_count"),
        )
    )
    metric_rows = _metric_rows(packet)
    if metric_rows:
        st.dataframe(metric_rows, width="stretch", hide_index=True)
    widget_rows = _widget_candidate_rows(packet)
    if widget_rows:
        st.dataframe(widget_rows, width="stretch", hide_index=True)
    else:
        st.info("No lowered display-packet widget candidates are available for review yet.")
    blocked = _list(packet.get("blocked_reasons"))
    warnings = _list(packet.get("warning_reasons"))
    if blocked:
        st.caption("blocked_reasons=" + ", ".join(str(item) for item in blocked))
    if warnings:
        st.caption("warning_reasons=" + ", ".join(str(item) for item in warnings))
    st.dataframe(_boundary_rows(packet), width="stretch", hide_index=True)
