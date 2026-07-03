# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_connection_status_observation.py
# desc: WarRoom v2 hidden WS display connection status observation. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .ws_display_connection_status import build_warroom_v2_ws_display_connection_status_contract, build_warroom_v2_ws_display_connection_status_packet

WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_VERSION = "prediction_warroom.v2.transport.ws_display_connection_status_observation.ps_q32d.v1"
WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_STATE_KEY = "warroom_v2_ws_display_connection_status_observation_q32d"


def build_warroom_v2_ws_display_connection_status_observation_contract() -> dict[str, Any]:
    contract = build_warroom_v2_ws_display_connection_status_contract()
    return {
        "ok": True,
        "observation_version": WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_WS_DISPLAY_CONNECTION_STATUS_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_ws_display_connection_status_observation_packet",
        "input_pipeline": ["q32b_ws_display_client_observation", "q32c_ws_display_connection_status_contract"],
        "current_small_goal": contract["current_small_goal"],
        "warroom_status_line_allowed_later": True,
        "warroom_status_line_visible_now": False,
        "warroom_status_line_mounted_now": False,
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


def build_warroom_v2_ws_display_connection_status_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    now_label: str = "not-connected",
) -> dict[str, Any]:
    status_packet = build_warroom_v2_ws_display_connection_status_packet(
        fragment_summary=fragment_summary,
        messages=list(messages or []),
        now_label=now_label,
    )
    status_line = dict(status_packet.get("status_line") or {})
    return {
        **build_warroom_v2_ws_display_connection_status_observation_contract(),
        "packet_kind": "warroom_v2_ws_display_connection_status_observation_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "ws_display_connection_status_packet": status_packet,
        "status_code": str(status_packet.get("status_code") or ""),
        "transport_state_ja": str(status_line.get("transport_state_ja") or ""),
        "data_freshness_ja": str(status_line.get("data_freshness_ja") or ""),
        "last_update_age_ja": str(status_line.get("last_update_age_ja") or ""),
        "operator_guidance_ja": str(status_line.get("operator_guidance_ja") or ""),
        "received_message_count": int(status_packet.get("received_message_count") or 0),
        "dropped_count": int(status_packet.get("dropped_count") or 0),
        "status_line": status_line,
        "status_line_field_count": int(status_packet.get("status_line_field_count") or 0),
        "status_line_compact": True,
        "status_line_allowed_in_warroom_later": True,
        "status_line_visible_now": False,
        "status_line_mounted_now": False,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
    }
