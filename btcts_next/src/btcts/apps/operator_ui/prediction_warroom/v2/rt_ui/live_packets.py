# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/live_packets.py
# desc: WarRoom v2 RT live packet selection policy. Uses live packets first, retained packets second, and waiting packets instead of WP sample fallback.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp9_warroom_page_mount import WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp11_top_layout_push_widget_polish import WARROOM_WP11_TOP_LAYOUT_SESSION_STATE_KEY
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp12_bottom_chart_layout import WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY
from btcts.apps.operator_ui.prediction_warroom.v2.push_widgets.wp13_prediction_card_connection import WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY

RETAINED_PAGE_KEY = "warroom_v2_rt_retained_wp9_page_mount_packet"
RETAINED_TOP_KEY = "warroom_v2_rt_retained_wp11_top_layout_packet"
RETAINED_CHART_KEY = "warroom_v2_rt_retained_wp12_bottom_chart_packet"
RETAINED_CARDS_KEY = "warroom_v2_rt_retained_wp13_prediction_card_packet"
DISPLAY_SOURCE_KEY = "warroom_v2_rt_display_packet_source"
RT_VERSION_PREFIX = "warroom.manual_trade_support.push_widgets.rt0_rt6"


def _is_rt_live_packet(packet: object) -> bool:
    if not isinstance(packet, Mapping):
        return False
    return str(packet.get("version") or "").startswith(RT_VERSION_PREFIX) or str(packet.get("packet_kind") or "").startswith("warroom_push_widget_rt_live")


def _base_flags() -> dict[str, Any]:
    return {"websocket_send_enabled": False, "broker_send_enabled": False, "order_intent_submitted": False, "ledger_append_allowed": False, "auto_trading_enabled": False, "prediction_invoked": False, "classifier_invoked": False, "manual_trade_support_read_only": True}


def _waiting_widgets_packet() -> dict[str, Any]:
    packet = {"ok": True, "packet_kind": "warroom_v2_rt_waiting_page_mount_packet", "version": "warroom.v2.rt.waiting.v1", "display_source": "waiting", "live_receiver_bridge_used": False, "messages_applied": 0, "widget_count": 0, "render_packet_count": 0, "live_widget_count": 0, "widget_ids": [], "live_widget_ids": [], "render_packets": {}, "health_packets": {}, "waiting_for_live_packet": True, "fallback_sample_suppressed": True}
    packet.update(_base_flags())
    return packet


def _waiting_top_packet() -> dict[str, Any]:
    packet = {"ok": True, "packet_kind": "warroom_v2_rt_waiting_top_layout_packet", "version": "warroom.v2.rt.waiting.v1", "display_source": "waiting", "top_information_groups_ready": True, "group_count": 4, "base_widget_count": 0, "live_widget_count": 0, "groups": [
        {"group_id": "market_status", "title": "Market status", "priority": 10, "widget_ids": [], "primary_state": "waiting", "status_label": "waiting for live market data", "cues": ["depth", "trades", "spread"], "read_only": True, "controls_added": False},
        {"group_id": "trade_status", "title": "Trade / position", "priority": 15, "widget_ids": [], "primary_state": "waiting", "status_label": "orders and positions not connected", "cues": ["orders", "position", "pnl"], "read_only": True, "controls_added": False},
        {"group_id": "inference_guidance", "title": "Scenario guidance", "priority": 20, "widget_ids": [], "primary_state": "waiting", "status_label": "waiting for observation signals", "cues": ["liquidity", "trades", "stale guard"], "read_only": True, "controls_added": False},
        {"group_id": "risk_cues", "title": "Risk cues", "priority": 30, "widget_ids": [], "primary_state": "waiting", "status_label": "no live risk cues yet", "cues": ["spread", "liquidity", "alerts"], "read_only": True, "controls_added": False},
    ], "waiting_for_live_packet": True, "fallback_sample_suppressed": True}
    packet.update(_base_flags())
    return packet


def _waiting_chart_packet() -> dict[str, Any]:
    packet = {"ok": True, "packet_kind": "warroom_v2_rt_waiting_bottom_chart_packet", "version": "warroom.v2.rt.waiting.v1", "display_source": "waiting", "bottom_chart_data_adapter_ready": True, "chart_row_count": 0, "overlay_count": 0, "stale_row_count": 0, "refresh_cadence_ms": 1000, "chart_rows": [], "overlays": [], "waiting_for_live_packet": True, "fallback_sample_suppressed": True}
    packet.update(_base_flags())
    return packet


def _waiting_cards_packet() -> dict[str, Any]:
    cards = [
        {"context_id": "market_context_card", "title": "Market context", "market_state": "waiting", "chart_summary": "waiting for live chart", "widget_summary": "live widgets not ready yet", "operator_note": "observe only; no action", "stale_guard": "waiting", "read_only": True, "prediction_invoked": False, "classifier_invoked": False, "broker_action_allowed": False},
        {"context_id": "scenario_guidance_card", "title": "Scenario guidance", "market_state": "waiting", "chart_summary": "waiting for liquidity/trade context", "widget_summary": "scenario will update from observations", "operator_note": "observational scenario, not prophecy", "stale_guard": "waiting", "read_only": True, "prediction_invoked": False, "classifier_invoked": False, "broker_action_allowed": False},
        {"context_id": "manual_review_card", "title": "Manual review", "market_state": "waiting", "chart_summary": "waiting for live packet", "widget_summary": "manual decision remains separate", "operator_note": "no broker/order/auto-trade action is connected", "stale_guard": "waiting", "read_only": True, "prediction_invoked": False, "classifier_invoked": False, "broker_action_allowed": False},
    ]
    packet = {"ok": True, "packet_kind": "warroom_v2_rt_waiting_prediction_card_packet", "version": "warroom.v2.rt.waiting.v1", "display_source": "waiting", "prediction_card_connection_ready": True, "prediction_card_update_ready": False, "prediction_card_no_action_boundary_ready": True, "prediction_card_count": len(cards), "bottom_chart_row_count": 0, "bottom_chart_overlay_count": 0, "cards": cards, "waiting_for_live_packet": True, "fallback_sample_suppressed": True}
    packet.update(_base_flags())
    return packet


def _display_from(source: str, page: Mapping[str, Any], top: Mapping[str, Any], chart: Mapping[str, Any], cards: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {"source": {"display_source": source, "fallback_sample_suppressed": True}, "widgets": dict(page), "top": dict(top), "chart": dict(chart), "cards": dict(cards)}


def select_or_build_rt_display_packets(session_state: MutableMapping[str, Any], bridge_packet: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    current = {
        "widgets": session_state.get(WARROOM_WP9_PAGE_MOUNT_SESSION_STATE_KEY),
        "top": session_state.get(WARROOM_WP11_TOP_LAYOUT_SESSION_STATE_KEY),
        "chart": session_state.get(WARROOM_WP12_BOTTOM_CHART_SESSION_STATE_KEY),
        "cards": session_state.get(WARROOM_WP13_PREDICTION_CARD_SESSION_STATE_KEY),
    }
    has_live = all(_is_rt_live_packet(value) for value in current.values())
    messages_applied = int(bridge_packet.get("messages_applied") or 0)
    if has_live and (messages_applied > 0 or not bridge_packet.get("live_receiver_bridge_idle")):
        session_state[RETAINED_PAGE_KEY] = dict(current["widgets"])
        session_state[RETAINED_TOP_KEY] = dict(current["top"])
        session_state[RETAINED_CHART_KEY] = dict(current["chart"])
        session_state[RETAINED_CARDS_KEY] = dict(current["cards"])
        session_state[DISPLAY_SOURCE_KEY] = "live"
        return _display_from("live", current["widgets"], current["top"], current["chart"], current["cards"])
    retained = {
        "widgets": session_state.get(RETAINED_PAGE_KEY),
        "top": session_state.get(RETAINED_TOP_KEY),
        "chart": session_state.get(RETAINED_CHART_KEY),
        "cards": session_state.get(RETAINED_CARDS_KEY),
    }
    if all(isinstance(value, Mapping) for value in retained.values()):
        session_state[DISPLAY_SOURCE_KEY] = "retained"
        return _display_from("retained", retained["widgets"], retained["top"], retained["chart"], retained["cards"])
    session_state[DISPLAY_SOURCE_KEY] = "waiting"
    return _display_from("waiting", _waiting_widgets_packet(), _waiting_top_packet(), _waiting_chart_packet(), _waiting_cards_packet())
