# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp9_read_only_render_packet.py
# desc: PS-Q39D CP9 read-only render packet. Builds render metadata only; no Streamlit import, no callable, no controls, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp9_read_only_render_packet.ps_q39d.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet_q39d"
_ROWS_KIND = "warroom_v2_ws_receiver_only_client_cp9_panel_row_shaping_packet"


def build_warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet(
    cp9_panel_row_shaping_packet: Mapping[str, Any] | None = None,
    *,
    allow_render_packet: bool = False,
) -> dict[str, Any]:
    rows_packet = dict(cp9_panel_row_shaping_packet or {})
    recognized = rows_packet.get("packet_kind") == _ROWS_KIND
    ready = bool(allow_render_packet and recognized and rows_packet.get("panel_row_shaping_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp9_read_only_render_packet",
        "cp9_read_only_render_packet_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q39d_cp9_read_only_render_packet",
        "panel_row_shaping_kind_recognized": recognized,
        "read_only_render_packet_ready": ready,
        "render_surface": "warroom_v2_visible_stream_panel_packet" if ready else "not_ready",
        "render_rows": list(rows_packet.get("panel_rows", [])) if ready else [],
        "render_row_count": int(rows_packet.get("panel_row_count", 0)) if ready else 0,
        "render_callable_returned": False,
        "streamlit_imported": False,
        "visible_stream_panel_ready": ready,
        "visible_stream_panel_read_only": True,
        "visible_stream_panel_default_off": True,
        "panel_mount_default_enabled": False,
        "operator_action_controls_added": False,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "secret_exposure": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "auto_start_added": False,
        "receive_loop_started": False,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "client_started": False,
        "connect_invoked": False,
        "receive_invoked": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
        "next_checkpoint": "CP9_default_off_mount_gate" if ready else "CP9_panel_row_shaping",
    }
