# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_start_preflight.py
# desc: WarRoom v2 receiver-only client start preflight. Metadata-only boundary before guarded socket open; no socket, no client start, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_START_PREFLIGHT_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_start_preflight.ps_q35k.v1"


def _badge_ready(packet: Mapping[str, Any]) -> bool:
    return (
        bool(packet.get("compact_status_badge_visible_now"))
        and str(packet.get("receiver_state_presence_label") or "") == "present"
        and str(packet.get("receiver_readback_label") or "") == "ready"
        and int(packet.get("receiver_state_message_count") or 0) > 0
    )


def _preflight_status(*, operator_scope_ack: bool, badge_ready: bool) -> str:
    if not badge_ready:
        return "receiver_only_client_start_preflight_blocked_badge_readback_ready_required"
    if not operator_scope_ack:
        return "receiver_only_client_start_preflight_waiting_operator_scope_ack"
    return "receiver_only_client_start_preflight_ready_for_guarded_socket_open_next_slice"


def build_warroom_v2_ws_receiver_only_client_start_preflight_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "receiver_only_client_start_preflight_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_START_PREFLIGHT_VERSION,
        "preflight_kind": "warroom_v2_ws_receiver_only_client_start_preflight_metadata_only_no_socket_no_send",
        "input_pipeline": ["q35j_compact_status_badge_state_presence"],
        "requires_compact_badge_visible": True,
        "requires_receiver_state_presence_label_present": True,
        "requires_receiver_readback_label_ready": True,
        "requires_receiver_state_message_count_positive": True,
        "requires_operator_scope_ack": True,
        "operator_scope_ack_default": False,
        "metadata_only": True,
        "preflight_only": True,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "renders_badge_now": False,
        "renders_card_now": False,
        "renders_balloon_now": False,
        "renders_warning_now": False,
        "renders_help_text_now": False,
        "streamlit_imported": False,
        "streamlit_render_allowed": False,
        "streamlit_render_invoked": False,
        "receiver_only": True,
        "send_disabled": True,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "socket_open_allowed_now": False,
        "client_start_allowed_now": False,
        "socket_open_allowed_for_future_slice": False,
        "client_start_allowed_for_future_slice": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
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


def build_warroom_v2_ws_receiver_only_client_start_preflight_packet(
    *,
    compact_status_badge_packet: Mapping[str, Any] | None = None,
    operator_scope_ack: bool = False,
) -> dict[str, Any]:
    badge = dict(compact_status_badge_packet or {})
    badge_ready = _badge_ready(badge)
    status = _preflight_status(operator_scope_ack=bool(operator_scope_ack), badge_ready=badge_ready)
    future_allowed = status == "receiver_only_client_start_preflight_ready_for_guarded_socket_open_next_slice"
    return {
        **build_warroom_v2_ws_receiver_only_client_start_preflight_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_start_preflight_packet",
        "compact_status_badge_packet": badge,
        "operator_scope_ack": bool(operator_scope_ack),
        "compact_status_badge_visible_now": bool(badge.get("compact_status_badge_visible_now")),
        "receiver_state_presence_label": str(badge.get("receiver_state_presence_label") or ""),
        "receiver_readback_label": str(badge.get("receiver_readback_label") or ""),
        "receiver_state_message_count": int(badge.get("receiver_state_message_count") or 0),
        "badge_ready_for_receiver_client_preflight": badge_ready,
        "receiver_only_client_start_preflight_status": status,
        "ready_for_guarded_socket_open_next_slice": future_allowed,
        "socket_open_allowed_for_future_slice": future_allowed,
        "client_start_allowed_for_future_slice": future_allowed,
        "socket_open_allowed_now": False,
        "client_start_allowed_now": False,
        "socket_opened": False,
        "client_started": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "would_send_to_broker": False,
    }
