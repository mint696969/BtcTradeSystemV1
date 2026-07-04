# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp6_no_connect_no_send_guard.py
# desc: PS-Q36X CP6 no-connect/no-send strict guard. Validates adapter readiness stays local metadata only; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp6_no_connect_no_send_guard.ps_q36x.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp6_no_connect_no_send_guard_q36x"
_READBACK_KIND = "warroom_v2_ws_receiver_only_client_cp6_adapter_readiness_readback_packet"


def build_warroom_v2_ws_receiver_only_client_cp6_no_connect_no_send_guard_packet(
    adapter_readiness_readback_packet: Mapping[str, Any] | None = None,
    *,
    allow_cp6_no_connect_no_send_guard: bool = False,
) -> dict[str, Any]:
    readback = dict(adapter_readiness_readback_packet or {})
    recognized = readback.get("packet_kind") == _READBACK_KIND
    safety_ok = bool(
        recognized
        and readback.get("adapter_readiness_readback_ready")
        and readback.get("endpoint_value_returned") is False
        and readback.get("token_value_returned") is False
        and readback.get("callable_values_returned") is False
        and readback.get("socket_opened") is False
        and readback.get("client_sends_messages") is False
        and readback.get("external_message_send_enabled") is False
        and readback.get("send_disabled") is True
    )
    ready = bool(allow_cp6_no_connect_no_send_guard and safety_ok)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp6_no_connect_no_send_guard_packet",
        "no_connect_no_send_guard_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36x_cp6_no_connect_no_send_guard",
        "readback_kind_recognized": recognized,
        "cp6_no_connect_no_send_guard_ready": ready,
        "buffer_count": int(readback.get("buffer_count") or 0) if ready else 0,
        "raw_payload_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "callable_values_returned": False,
        "secret_exposure": False,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
        "order_intent_submitted": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }
