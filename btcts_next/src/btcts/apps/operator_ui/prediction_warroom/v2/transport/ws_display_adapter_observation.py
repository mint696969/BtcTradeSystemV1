# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_display_adapter_observation.py
# desc: WarRoom v2 hidden WS display adapter observation. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .ws_display_adapter import build_warroom_v2_ws_display_push_adapter_contract, build_warroom_v2_ws_display_push_outbox

WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_VERSION = "prediction_warroom.v2.transport.ws_display_adapter_observation.ps_q31z.v1"
WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_STATE_KEY = "warroom_v2_ws_display_adapter_observation_q31z"


def build_warroom_v2_ws_display_adapter_observation_contract() -> dict[str, Any]:
    contract = build_warroom_v2_ws_display_push_adapter_contract()
    return {
        "ok": True,
        "observation_version": WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_WS_DISPLAY_ADAPTER_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_ws_display_adapter_observation_packet",
        "input_pipeline": ["q31x_realtime_japanese_read_surface", "q31y_ws_display_adapter_contract"],
        "current_small_goal": contract["current_small_goal"],
        "websocket_display_push_required": True,
        "websocket_display_push_main_path": True,
        "bidirectional_websocket_premise": True,
        "read_model_push_plane": "server_to_warroom_ui",
        "browser_timer_polling_is_legacy_compat_only": True,
        "browser_timer_refresh_replacement_target": True,
        "no_new_polling_fallback": True,
        "no_browser_timer_reload_introduced": True,
        "warroom_diagnostic_policy": "minimal_status_only",
        "detailed_diagnostics_default_surface": "audit_or_diagnostics_tab",
        "diagnostic_minimal_summary_allowed_in_warroom": True,
        "warroom_visible_diagnostic_panel_default": False,
        "visible_panel_render_plan_deprioritized": True,
        "socket_opened": False,
        "adapter_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
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


def build_warroom_v2_ws_display_adapter_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    max_messages: int = 64,
) -> dict[str, Any]:
    raw_messages = list(messages or [])
    outbox = build_warroom_v2_ws_display_push_outbox(messages=raw_messages, max_messages=max_messages)
    return {
        **build_warroom_v2_ws_display_adapter_observation_contract(),
        "packet_kind": "warroom_v2_ws_display_adapter_observation_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "default_streamlit_message_count": len(raw_messages),
        "ws_display_adapter_outbox_packet": outbox,
        "outbox_message_count": int(outbox.get("message_count") or 0),
        "outbox_dropped_count": int(outbox.get("dropped_count") or 0),
        "outbox_normalizes_display_targets_only": True,
        "outbox_drops_non_display_topics": True,
        "all_messages_are_display_targets": bool(outbox.get("all_messages_are_display_targets", True)),
        "all_messages_no_broad_page_reload": bool(outbox.get("all_messages_no_broad_page_reload", True)),
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
    }
