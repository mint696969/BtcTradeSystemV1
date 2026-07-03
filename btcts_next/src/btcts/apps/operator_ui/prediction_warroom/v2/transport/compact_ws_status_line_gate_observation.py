# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_gate_observation.py
# desc: WarRoom v2 hidden compact WS status line gate observation. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .compact_ws_status_line_gate import build_warroom_v2_compact_ws_status_line_gate_contract, build_warroom_v2_compact_ws_status_line_gate_packet

WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_VERSION = "prediction_warroom.v2.transport.compact_ws_status_line_gate_observation.ps_q32f.v1"
WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_STATE_KEY = "warroom_v2_compact_ws_status_line_gate_observation_q32f"


def build_warroom_v2_compact_ws_status_line_gate_observation_contract() -> dict[str, Any]:
    contract = build_warroom_v2_compact_ws_status_line_gate_contract()
    return {
        "ok": True,
        "observation_version": WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_COMPACT_WS_STATUS_LINE_GATE_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_compact_ws_status_line_gate_observation_packet",
        "input_pipeline": ["q32d_ws_display_connection_status_observation", "q32e_compact_ws_status_line_gate"],
        "current_small_goal": contract["current_small_goal"],
        "render_requested_default": False,
        "operator_read_only_ack_default": False,
        "default_gate_status": "compact_ws_status_line_hidden_default",
        "warroom_page_hidden_state_only": True,
        "warroom_visible_surface": "top_minimal_operator_status_line_later",
        "compact_status_only": True,
        "detailed_diagnostics_default_surface": "audit_or_diagnostics_tab",
        "websocket_display_push_required": True,
        "websocket_display_push_main_path": True,
        "ui_receiver_side": True,
        "server_to_warroom_ui": True,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "browser_timer_polling_is_legacy_compat_only": True,
        "browser_timer_refresh_replacement_target": True,
        "no_new_polling_fallback": True,
        "no_browser_timer_reload_introduced": True,
        "streamlit_render_allowed": False,
        "warroom_page_ui_switch": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_compact_ws_status_line_gate_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    render_requested: bool = False,
    operator_read_only_ack: bool = False,
) -> dict[str, Any]:
    gate_packet = build_warroom_v2_compact_ws_status_line_gate_packet(
        fragment_summary=fragment_summary,
        messages=list(messages or []),
        render_requested=render_requested,
        operator_read_only_ack=operator_read_only_ack,
    )
    return {
        **build_warroom_v2_compact_ws_status_line_gate_observation_contract(),
        "packet_kind": "warroom_v2_compact_ws_status_line_gate_observation_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "compact_ws_status_line_gate_packet": gate_packet,
        "gate_status": str(gate_packet.get("gate_status") or ""),
        "render_requested": bool(gate_packet.get("render_requested")),
        "operator_read_only_ack": bool(gate_packet.get("operator_read_only_ack")),
        "status_line_available": bool(gate_packet.get("status_line_available")),
        "status_line_ready_for_future_mount": bool(gate_packet.get("status_line_ready_for_future_mount")),
        "status_line_row": dict(gate_packet.get("status_line_row") or {}),
        "status_line_field_count": int(gate_packet.get("status_line_field_count") or 0),
        "status_line_visible_now": False,
        "status_line_mounted_now": False,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
    }
