# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp9_completion.py
# desc: PS-Q39H CP9 completion packet. Closes visible stream panel and hands off to CP10 reconnect/heartbeat/backpressure danger-zone.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp9_completion.ps_q39h.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp9_completion_q39h"
_GUARD_KIND = "warroom_v2_ws_receiver_only_client_cp9_no_control_visible_guard_packet"


def build_warroom_v2_ws_receiver_only_client_cp9_completion_packet(
    cp9_no_control_visible_guard_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp9_completion: bool = False,
) -> dict[str, Any]:
    guard = dict(cp9_no_control_visible_guard_packet or {})
    recognized = guard.get("packet_kind") == _GUARD_KIND
    completed = bool(allow_cp9_completion and recognized and guard.get("cp9_no_control_visible_guard_ready"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp9_completion_packet",
        "cp9_completion_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q39h_cp9_completion_close",
        "cp9_no_control_visible_guard_kind_recognized": recognized,
        "cp9_completed": completed,
        "cp9_completion_commit_ready": completed,
        "next_checkpoint": "CP10_reconnect_heartbeat_backpressure" if completed else "CP9_no_control_visible_guard",
        "visible_stream_panel_ready": completed,
        "visible_stream_panel_read_only": True,
        "visible_stream_panel_default_off": True,
        "panel_rows_metadata_only": True,
        "panel_mount_default_enabled": False,
        "operator_action_controls_added": False,
        "cp10_is_danger_zone": completed,
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
    }
