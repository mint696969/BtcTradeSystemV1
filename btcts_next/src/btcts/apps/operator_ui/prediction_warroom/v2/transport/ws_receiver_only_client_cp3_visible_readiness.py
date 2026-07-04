# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_visible_readiness.py
# desc: WarRoom v2 receiver-only CP3 visible readiness packet. Composes CP1 completion into existing compact badge; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness.ps_q35x.v1"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_STATE_KEY = "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_q35x"
WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_SOURCE_STATE_KEY = "warroom_v2_ws_receiver_only_client_cp1_completion_source_q35x"
_CP1_COMPLETION_KIND = "warroom_v2_ws_receiver_only_client_cp1_completion_packet"


def build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "cp3_visible_readiness_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_VERSION,
        "state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_STATE_KEY,
        "source_state_key": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP3_VISIBLE_READINESS_SOURCE_STATE_KEY,
        "input_pipeline": ["q35w_cp1_completion", "q35x_cp3_visible_readiness"],
        "selected_visible_surface": "compact_status_badge",
        "visible_surface_implemented_now": True,
        "visible_readiness_display_enabled": True,
        "visible_controls_added": False,
        "read_only": True,
        "metadata_only": True,
        "raw_cp1_completion_packet_returned": False,
        "session_state_keys_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "warroom_page_modified": True,
        "warroom_page_visible_ui_modified": True,
        "aggregator_exports_added": False,
        "receiver_only": True,
        "send_disabled": True,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "socket_opened": False,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet(
    *,
    compact_badge_packet: Mapping[str, Any] | None = None,
    cp1_completion_packet: Mapping[str, Any] | None = None,
    allow_visible_readiness: bool = False,
) -> dict[str, Any]:
    badge = dict(compact_badge_packet or {})
    cp1 = dict(cp1_completion_packet or {})
    cp1_ready = cp1.get("packet_kind") == _CP1_COMPLETION_KIND and bool(cp1.get("cp1_completed"))
    visible_badge_ready = bool(badge.get("compact_status_badge_visible_now"))
    visible_now = bool(allow_visible_readiness and visible_badge_ready)
    readiness_label = "cp1_ready" if cp1_ready else "cp1_pending"
    base_line = str(badge.get("compact_badge_markdown") or "`WS Receiver` no socket/send")
    line = base_line
    if visible_now:
        line = f"{base_line} · readiness={readiness_label} · live=off"
    return {
        **build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_packet",
        "allow_visible_readiness": bool(allow_visible_readiness),
        "compact_status_badge_visible_now": visible_badge_ready,
        "cp1_completion_present": bool(cp1_completion_packet),
        "cp1_completion_kind_recognized": cp1.get("packet_kind") == _CP1_COMPLETION_KIND,
        "cp1_completed": cp1_ready,
        "cp3_visible_readiness_visible_now": visible_now,
        "receiver_visible_readiness_label": readiness_label,
        "live_stream_enabled": False,
        "fake_receive_loop_enabled": False,
        "visible_readiness_markdown": line if visible_now else "",
        "read_only": True,
        "metadata_only": True,
        "raw_cp1_completion_packet_returned": False,
        "session_state_keys_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "visible_controls_added": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "socket_opened": False,
        "would_send_to_broker": False,
    }
