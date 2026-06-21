# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_panel.py
# desc: PS-Q9G guarded Streamlit review panel for lowered Prediction WarRoom display-packet visibility. Renders a read-only review surface from supplied/in-memory contract data only; no file reads, payload decode, loader execution, runtime writes, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from typing import Any, Mapping

import streamlit as st

from .prediction_warroom_lowered_display_packet_visibility_review_contract import (
    LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION,
)
from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import (
    resolve_prediction_warroom_lowered_display_packet_visibility_review_source,
)

PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION = "prediction_warroom_lowered_display_packet_visibility_review_panel.ps_q9g.v1"
PANEL_OPERATOR_READABILITY_VERSION = "prediction_warroom_lowered_display_packet_visibility_readability.ps_q9k.v1"


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


def _operator_focus_ja(widget_group_id: Any) -> str:
    focus_by_id = {
        "primary_signal_widget": "主要シグナルを最初に確認",
        "horizon_scenario_widgets": "時間軸ごとのシナリオを確認",
        "family_detail_widgets": "根拠ファミリーの内訳を確認",
        "source_quality_widget": "ソース品質と制約を確認",
        "evidence_ledger_widget": "証拠と寄与の流れを確認",
        "warning_refresh_widget": "警告と更新要否を確認",
    }
    return focus_by_id.get(str(widget_group_id), "表示候補を確認")


def _operator_readiness_card_rows(packet: Mapping[str, Any], source_handoff: Mapping[str, Any]) -> list[dict[str, Any]]:
    blocker_count = int(packet.get("blocker_count") or 0)
    warning_count = int(packet.get("warning_count") or 0)
    visible_count = int(packet.get("visible_widget_group_count") or 0)
    widget_count = int(packet.get("widget_group_count") or 0)
    display_state = "valid" if packet.get("display_packet_valid") is True else "blocked"
    return [
        {
            "card_id": "source_handoff",
            "label_ja": "入力ソース",
            "state": source_handoff.get("handoff_state"),
            "summary_ja": "in-memory review packet を表示対象として確認",
            "read_only": True,
            "execution": "false",
        },
        {
            "card_id": "display_packet",
            "label_ja": "表示パケット",
            "state": display_state,
            "summary_ja": "表示パケットの生成・検証状態を確認",
            "read_only": True,
            "execution": "false",
        },
        {
            "card_id": "widget_visibility",
            "label_ja": "表示候補ウィジェット",
            "state": f"{visible_count}/{widget_count}",
            "summary_ja": "WarRoom 表示候補の数と順序を確認",
            "read_only": True,
            "execution": "false",
        },
        {
            "card_id": "blockers_and_warnings",
            "label_ja": "ブロッカー / 警告",
            "state": f"blockers={blocker_count};warnings={warning_count}",
            "summary_ja": "表示前に止める理由と注意点を確認",
            "read_only": True,
            "execution": "false",
        },
        {
            "card_id": "next_operator_action",
            "label_ja": "次の操作",
            "state": "review_only_no_execution",
            "summary_ja": "確認のみ。承認・台帳追記・AutoTrade・broker 操作はしない",
            "read_only": True,
            "execution": "false",
        },
    ]


def _operator_widget_card_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in _list(packet.get("widget_candidates")):
        item = _as_mapping(raw)
        widget_group_id = item.get("widget_group_id")
        rows.append(
            {
                "widget_group_id": widget_group_id,
                "label_ja": item.get("widget_group_label_ja"),
                "operator_focus_ja": _operator_focus_ja(widget_group_id),
                "kind": item.get("widget_group_kind"),
                "visible": item.get("visible_in_review"),
                "refresh_sec": item.get("refresh_interval_sec"),
                "render": "review_only",
                "execution": "false",
                "autotrade": "false",
                "broker": "false",
            }
        )
    return rows


def render_prediction_warroom_lowered_display_packet_visibility_review_panel(
    *,
    review_packet: Mapping[str, Any] | Any | None = None,
) -> None:
    """Render a guarded read-only PS-Q9G review panel without loader/runtime side effects."""
    source_handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        explicit_review_packet=review_packet,
        session_state=st.session_state,
    ).to_dict()
    packet = _as_mapping(source_handoff.get("review_packet"))
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
    st.caption(
        "source_handoff={state}; source_kind={kind}; matched_key={key}; fallback={fallback}".format(
            state=source_handoff.get("handoff_state"),
            kind=source_handoff.get("source_kind"),
            key=source_handoff.get("matched_key"),
            fallback=source_handoff.get("fallback_used"),
        )
    )
    operator_rows = _operator_readiness_card_rows(packet, source_handoff)
    if operator_rows:
        st.caption("operator_readability_cards=" + PANEL_OPERATOR_READABILITY_VERSION)
        st.dataframe(operator_rows, width="stretch", hide_index=True)
    operator_widget_rows = _operator_widget_card_rows(packet)
    if operator_widget_rows:
        st.caption("operator_widget_cards=review_only_no_execution")
        st.dataframe(operator_widget_rows, width="stretch", hide_index=True)
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
