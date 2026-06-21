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
PANEL_PREDICTION_COMPACT_SUMMARY_VERSION = "prediction_warroom_prediction_compact_summary.ps_q9l.v1"
PANEL_FUTURE_TOP_UX_GATE_VERSION = "prediction_warroom_future_top_default_expanded_gate.ps_q9m.v1"


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


def _widget_payload_by_id(packet: Mapping[str, Any], widget_group_id: str) -> Mapping[str, Any]:
    widget_index = _as_mapping(packet.get("widget_group_index"))
    for raw in _list(widget_index.get("widget_groups")):
        group = _as_mapping(raw)
        if group.get("widget_group_id") == widget_group_id:
            return _as_mapping(group.get("payload"))
    return {}


def _first_mapping_item(value: Any) -> Mapping[str, Any]:
    items = _list(value)
    if not items:
        return {}
    return _as_mapping(items[0])


def _prediction_compact_summary_card_rows(packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    primary_payload = _widget_payload_by_id(packet, "primary_signal_widget")
    horizon_payload = _widget_payload_by_id(packet, "horizon_scenario_widgets")
    source_payload = _widget_payload_by_id(packet, "source_quality_widget")
    warning_payload = _widget_payload_by_id(packet, "warning_refresh_widget")
    primary = _as_mapping(primary_payload.get("primary_signal_summary"))
    horizon = _first_mapping_item(horizon_payload.get("horizon_cards"))
    source_quality = _as_mapping(source_payload.get("source_quality_panel"))
    quality_gate = _as_mapping(source_quality.get("tier0_source_quality_gate"))
    source_coverage = _as_mapping(source_quality.get("source_artifact_coverage"))
    warning_panel = _as_mapping(warning_payload.get("warning_panel"))
    headline = str(primary_payload.get("headline_ja") or "not_available")
    signal_percent = int(primary.get("estimated_signal_strength_percent") or 0)
    signal_label = str(primary.get("signal_strength_band_label_ja") or primary.get("signal_strength_band") or "unknown")
    gate_state = str(quality_gate.get("gate_state") or source_quality.get("source_quality_gate_state") or "unknown")
    coverage_state = str(source_coverage.get("input_coverage_state") or source_quality.get("source_artifact_input_coverage_state") or "unknown")
    scenario_lite = _as_mapping(horizon.get("scenario_lite"))
    horizon_group = str(horizon.get("horizon_group") or "unknown")
    primary_label = str(
        horizon.get("primary_label")
        or horizon.get("trend_bias")
        or scenario_lite.get("scenario_balance_state")
        or "unknown"
    )
    confidence = str(
        horizon.get("confidence")
        or horizon.get("caution_level")
        or scenario_lite.get("turning_point_risk")
        or "unknown"
    )
    warning_count = len(_list(warning_panel.get("warnings")))
    blocker_count = len(_list(warning_panel.get("blockers")))
    base = {
        "read_only": True,
        "execution": "false",
        "autotrade": "false",
        "broker": "false",
        "source": "already_lowered_review_payload_only",
    }
    return [
        {
            **base,
            "card_id": "prediction_headline",
            "label_ja": "予測ヘッドライン",
            "state": headline,
            "operator_note_ja": "最初に読む短い予測要約",
            "market_uid": primary_payload.get("market_uid"),
            "prediction_run_id": primary_payload.get("prediction_run_id"),
            "generated_at": primary_payload.get("generated_at"),
        },
        {
            **base,
            "card_id": "signal_strength",
            "label_ja": "シグナル強度",
            "state": f"{signal_percent}% / {signal_label}",
            "operator_note_ja": "主要シグナルの強さと参考度を確認",
            "market_uid": primary_payload.get("market_uid"),
            "prediction_run_id": primary_payload.get("prediction_run_id"),
            "generated_at": primary_payload.get("generated_at"),
        },
        {
            **base,
            "card_id": "source_quality",
            "label_ja": "情報源品質",
            "state": f"{gate_state} / {coverage_state}",
            "operator_note_ja": "ソース品質ゲートと入力カバー率を確認",
            "market_uid": primary_payload.get("market_uid"),
            "prediction_run_id": primary_payload.get("prediction_run_id"),
            "generated_at": primary_payload.get("generated_at"),
        },
        {
            **base,
            "card_id": "horizon_scenario",
            "label_ja": "時間軸シナリオ",
            "state": f"{horizon_group} / {primary_label} / {confidence}",
            "operator_note_ja": "時間軸・方向・確信度を確認",
            "market_uid": primary_payload.get("market_uid"),
            "prediction_run_id": primary_payload.get("prediction_run_id"),
            "generated_at": primary_payload.get("generated_at"),
        },
        {
            **base,
            "card_id": "warning_state",
            "label_ja": "警告状態",
            "state": f"warnings={warning_count};blockers={blocker_count}",
            "operator_note_ja": "参考度を制限する警告を確認",
            "market_uid": primary_payload.get("market_uid"),
            "prediction_run_id": primary_payload.get("prediction_run_id"),
            "generated_at": primary_payload.get("generated_at"),
        },
        {
            **base,
            "card_id": "execution_boundary",
            "label_ja": "実行境界",
            "state": "review_only_no_execution",
            "operator_note_ja": "確認のみ。承認・台帳追記・AutoTrade・broker 操作はしない",
            "market_uid": primary_payload.get("market_uid"),
            "prediction_run_id": primary_payload.get("prediction_run_id"),
            "generated_at": primary_payload.get("generated_at"),
        },
    ]


def _prediction_review_payload_is_synthetic(packet: Mapping[str, Any]) -> bool:
    primary_payload = _widget_payload_by_id(packet, "primary_signal_widget")
    primary = _as_mapping(primary_payload.get("primary_signal_summary"))
    boundaries = _as_mapping(primary_payload.get("boundaries"))
    run_id = str(primary_payload.get("prediction_run_id") or "")
    return bool(
        primary.get("synthetic_only") is True
        or boundaries.get("synthetic_only") is True
        or run_id.startswith("synthetic_")
    )


def _prediction_future_top_default_expanded_gate_rows(packet: Mapping[str, Any], source_handoff: Mapping[str, Any]) -> list[dict[str, Any]]:
    compact_rows = _prediction_compact_summary_card_rows(packet)
    compact_ready = bool(compact_rows and compact_rows[0].get("state") != "not_available" and compact_rows[1].get("state") != "0% / unknown")
    source_ready = bool(source_handoff.get("review_packet_ready")) and source_handoff.get("handoff_state") == "review_source_handoff_ready"
    display_ready = packet.get("display_packet_valid") is True and packet.get("ready_for_ps_q9g_guarded_ui_mount") is True
    execution_clean = (
        int(packet.get("blocker_count") or 0) == 0
        and packet.get("would_send_to_broker") is not True
        and packet.get("broker_execution_requested") is not True
        and packet.get("command_ledger_append_requested") is not True
        and packet.get("approval_append_requested") is not True
        and packet.get("authorization_grant_requested") is not True
        and packet.get("autotrade_trigger_enabled") is not True
    )
    synthetic_payload = _prediction_review_payload_is_synthetic(packet)
    real_payload_state = "blocked_synthetic_fixture" if synthetic_payload and compact_ready else ("ready" if compact_ready else "blocked_missing_real_payload")
    base = {
        "read_only": True,
        "execution": "false",
        "warroom_page_mutation": "false",
        "default_expanded_applied": "false",
        "source": "already_lowered_review_payload_only",
    }
    return [
        {
            **base,
            "gate_id": "compact_summary_ready",
            "state": "ready" if compact_ready else "not_ready",
            "operator_note_ja": "compact summary が最初に読める状態か確認",
        },
        {
            **base,
            "gate_id": "source_handoff_ready",
            "state": "ready" if source_ready else "blocked",
            "operator_note_ja": "in-memory source handoff が ready か確認",
        },
        {
            **base,
            "gate_id": "display_packet_ready",
            "state": "ready" if display_ready else "blocked",
            "operator_note_ja": "表示パケットが valid か確認",
        },
        {
            **base,
            "gate_id": "execution_boundary_clean",
            "state": "ready" if execution_clean and compact_ready else "blocked",
            "operator_note_ja": "承認・台帳追記・AutoTrade・broker が無効のままか確認",
        },
        {
            **base,
            "gate_id": "real_payload_required_for_top_default",
            "state": real_payload_state,
            "operator_note_ja": "top/default-expanded UX は real payload 観測後に検討",
        },
        {
            **base,
            "gate_id": "warroom_layout_change",
            "state": "deferred_no_page_mutation",
            "layout_change_status": "layout_change_not_applied",
            "operator_note_ja": "この slice では WarRoom top 移動も default-expanded 化もしない",
        },
    ]


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
    compact_summary_rows = _prediction_compact_summary_card_rows(packet)
    if compact_summary_rows:
        st.caption("prediction_compact_summary_cards=" + PANEL_PREDICTION_COMPACT_SUMMARY_VERSION)
        st.dataframe(compact_summary_rows, width="stretch", hide_index=True)
    top_gate_rows = _prediction_future_top_default_expanded_gate_rows(packet, source_handoff)
    if top_gate_rows:
        st.caption("future_top_default_expanded_gate=" + PANEL_FUTURE_TOP_UX_GATE_VERSION)
        st.dataframe(top_gate_rows, width="stretch", hide_index=True)
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
