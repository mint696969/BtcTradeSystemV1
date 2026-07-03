# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/compact_ws_status_line_visible_render_adapter_observation.py
# desc: WarRoom v2 hidden compact WS status line visible render adapter observation. Pure packet only; no UI, sockets, IO, order send, or polling fallback.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .compact_ws_status_line_visible_render_adapter import build_warroom_v2_compact_ws_status_line_visible_render_adapter_contract, build_warroom_v2_compact_ws_status_line_visible_render_adapter_packet

WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_ADAPTER_OBSERVATION_VERSION = "prediction_warroom.v2.transport.compact_ws_status_line_visible_render_adapter_observation.ps_q32j.v1"
WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_ADAPTER_OBSERVATION_STATE_KEY = "warroom_v2_compact_ws_status_line_visible_render_adapter_observation_q32j"


def build_warroom_v2_compact_ws_status_line_visible_render_adapter_observation_contract() -> dict[str, Any]:
    contract = build_warroom_v2_compact_ws_status_line_visible_render_adapter_contract()
    return {
        "ok": True,
        "observation_version": WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_ADAPTER_OBSERVATION_VERSION,
        "state_key": WARROOM_V2_COMPACT_WS_STATUS_LINE_VISIBLE_RENDER_ADAPTER_OBSERVATION_STATE_KEY,
        "observation_kind": "warroom_v2_hidden_compact_ws_status_line_visible_render_adapter_observation_packet",
        "input_pipeline": ["q32h_compact_ws_status_line_visible_mount_gate_observation", "q32i_compact_ws_status_line_visible_render_adapter"],
        "current_small_goal": contract["current_small_goal"],
        "visible_render_adapter_requested_default": False,
        "operator_visible_render_ack_default": False,
        "visible_mount_requested_default": False,
        "operator_visible_mount_ack_default": False,
        "status_gate_render_requested_default": False,
        "status_gate_read_only_ack_default": False,
        "default_adapter_status": "compact_ws_status_line_visible_render_hidden_default",
        "warroom_page_hidden_state_only": True,
        "warroom_mount_surface": "top_minimal_operator_status_line",
        "warroom_mount_position": "after_header_before_focus_nav_later",
        "display_item_labels_ja": ["WS状態", "データ鮮度", "最終更新", "受信数", "破棄数", "案内"],
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
        "streamlit_render_invoked": False,
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


def build_warroom_v2_compact_ws_status_line_visible_render_adapter_observation_packet(
    *,
    fragment_summary: Mapping[str, Any] | None = None,
    messages: Iterable[Mapping[str, Any]] | None = None,
    visible_render_adapter_requested: bool = False,
    operator_visible_render_ack: bool = False,
    visible_mount_requested: bool = False,
    operator_visible_mount_ack: bool = False,
    status_gate_render_requested: bool = False,
    status_gate_read_only_ack: bool = False,
) -> dict[str, Any]:
    adapter_packet = build_warroom_v2_compact_ws_status_line_visible_render_adapter_packet(
        fragment_summary=fragment_summary,
        messages=list(messages or []),
        visible_render_adapter_requested=visible_render_adapter_requested,
        operator_visible_render_ack=operator_visible_render_ack,
        visible_mount_requested=visible_mount_requested,
        operator_visible_mount_ack=operator_visible_mount_ack,
        status_gate_render_requested=status_gate_render_requested,
        status_gate_read_only_ack=status_gate_read_only_ack,
    )
    return {
        **build_warroom_v2_compact_ws_status_line_visible_render_adapter_observation_contract(),
        "packet_kind": "warroom_v2_compact_ws_status_line_visible_render_adapter_observation_packet",
        "fragment_summary": dict(fragment_summary or {}),
        "compact_ws_status_line_visible_render_adapter_packet": adapter_packet,
        "adapter_status": str(adapter_packet.get("adapter_status") or ""),
        "visible_render_adapter_requested": bool(adapter_packet.get("visible_render_adapter_requested")),
        "operator_visible_render_ack": bool(adapter_packet.get("operator_visible_render_ack")),
        "visible_mount_requested": bool(adapter_packet.get("visible_mount_requested")),
        "operator_visible_mount_ack": bool(adapter_packet.get("operator_visible_mount_ack")),
        "status_gate_render_requested": bool(adapter_packet.get("status_gate_render_requested")),
        "status_gate_read_only_ack": bool(adapter_packet.get("status_gate_read_only_ack")),
        "upstream_visible_mount_ready": bool(adapter_packet.get("upstream_visible_mount_ready")),
        "render_payload_ready_for_future_streamlit_mount": bool(adapter_packet.get("render_payload_ready_for_future_streamlit_mount")),
        "display_items": list(adapter_packet.get("display_items") or []),
        "display_item_count": int(adapter_packet.get("display_item_count") or 0),
        "compact_line_ja": str(adapter_packet.get("compact_line_ja") or ""),
        "status_line_visible_now": False,
        "status_line_mounted_now": False,
        "streamlit_render_invoked": False,
        "visible_ui_decoration_added": False,
        "streamlit_component_added": False,
        "button_added": False,
        "checkbox_added": False,
        "metric_added": False,
        "caption_added": False,
    }
