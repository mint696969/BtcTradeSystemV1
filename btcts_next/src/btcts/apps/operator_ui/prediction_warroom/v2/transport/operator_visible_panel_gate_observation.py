# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/operator_visible_panel_gate_observation.py
# desc: WarRoom v2 hidden visible panel gate observation. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .operator_visible_panel_gate import build_warroom_v2_operator_visible_panel_gate_packet
from .operator_visible_panel_observation import build_warroom_v2_operator_visible_panel_observation_packet

WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_VERSION = "prediction_warroom.v2.transport.operator_visible_panel_gate_observation.ps_q31w.v1"
WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY = "warroom_v2_operator_visible_panel_gate_observation_q31w"


def build_warroom_v2_operator_visible_panel_gate_observation_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "observation_version": WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_operator_visible_panel_gate_observation_packet",
        "input_pipeline": ["q31u_operator_visible_panel_observation", "q31v_operator_visible_panel_gate"],
        "websocket_first_future_transport": True,
        "bidirectional_websocket_premise": True,
        "no_polling_fallback_introduced": True,
        "no_browser_timer_reload_introduced": True,
        "visible_panel_gate_requested_default": False,
        "visible_panel_gate_read_only_ack_default": False,
        "visible_panel_gate_allowed_default": False,
        "gate_packet_only": True,
        "gate_mounts_into_warroom": False,
        "gate_renders_ui": False,
        "gate_visible_now": False,
        "panel_read_only": True,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "websocket_enabled": False,
        "socket_opened": False,
        "external_message_send_enabled": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_operator_visible_panel_gate_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str | None = None,
    visible_diagnostic_requested: bool = False,
    diagnostic_read_only_ack: bool = False,
    operator_visible_panel_requested: bool = False,
    operator_visible_panel_read_only_ack: bool = False,
    visible_panel_gate_requested: bool = False,
    visible_panel_gate_read_only_ack: bool = False,
    received_at: str = "streamlit-operator-visible-panel-gate-observation",
) -> dict[str, Any]:
    visible_panel_observation = build_warroom_v2_operator_visible_panel_observation_packet(
        fragment_summary=fragment_summary,
        messages=messages or [],
        consumer_state=consumer_state,
        evidence=evidence,
        operator_approval_token=operator_approval_token,
        visible_diagnostic_requested=visible_diagnostic_requested,
        diagnostic_read_only_ack=diagnostic_read_only_ack,
        operator_visible_panel_requested=operator_visible_panel_requested,
        operator_read_only_ack=operator_visible_panel_read_only_ack,
        received_at=received_at,
    )
    gate_packet = build_warroom_v2_operator_visible_panel_gate_packet(
        visible_panel_observation,
        visible_panel_gate_requested=visible_panel_gate_requested,
        operator_read_only_ack=visible_panel_gate_read_only_ack,
    )
    return {
        "ok": True,
        "observation_version": WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_OPERATOR_VISIBLE_PANEL_GATE_OBSERVATION_STATE_KEY,
        "packet_kind": "warroom_v2_operator_visible_panel_gate_observation_packet",
        "fragment_summary": dict(visible_panel_observation.get("fragment_summary") or {}),
        "operator_visible_panel_observation_packet": visible_panel_observation,
        "operator_visible_panel_gate_packet": gate_packet,
        "default_streamlit_message_count": len(list(messages or [])),
        "visible_panel_gate_status": str(gate_packet.get("visible_panel_gate_status") or ""),
        "visible_panel_gate_requested": bool(visible_panel_gate_requested),
        "visible_panel_gate_read_only_ack": bool(visible_panel_gate_read_only_ack),
        "visible_panel_gate_allowed": bool(gate_packet.get("visible_panel_gate_allowed", False)),
        "gate_row_count": int(gate_packet.get("gate_row_count") or 0),
        "websocket_first_future_transport": True,
        "bidirectional_websocket_premise": True,
        "no_polling_fallback_introduced": True,
        "no_browser_timer_reload_introduced": True,
        "gate_packet_only": True,
        "gate_mounts_into_warroom": False,
        "gate_renders_ui": False,
        "gate_visible_now": False,
        "panel_read_only": True,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
        "websocket_enabled": False,
        "socket_opened": False,
        "external_message_send_enabled": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "runtime_connected": False,
        "push_connected": False,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }
