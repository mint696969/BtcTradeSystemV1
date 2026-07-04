# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp5_invalid_message_handling.py
# desc: PS-Q36N CP5 invalid message handling. Invalid metadata normalization only; no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping, Sequence

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_message_normalizer_core import normalize_warroom_v2_ws_receiver_only_client_cp5_message

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp5_invalid_message_handling.ps_q36n.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp5_invalid_message_handling_q36n"
_CORE_KIND = "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet"


def _invalid_messages() -> list[dict[str, Any]]:
    return [
        {"symbol": "BTC", "sequence": 1},
        {"topic": "fake.btc.tick", "symbol": "BTC"},
        {"topic": "unknown.topic", "symbol": "BTC", "sequence": 2},
    ]


def build_warroom_v2_ws_receiver_only_client_cp5_invalid_message_handling_packet(
    normalizer_core_packet: Mapping[str, Any] | None = None,
    *,
    invalid_messages: Sequence[Mapping[str, Any]] | None = None,
    allow_invalid_message_handling: bool = False,
) -> dict[str, Any]:
    core = dict(normalizer_core_packet or {})
    core_ready = core.get("packet_kind") == _CORE_KIND and bool(core.get("cp5_message_normalizer_core_ready"))
    ready = bool(allow_invalid_message_handling and core_ready)
    source = list(invalid_messages) if invalid_messages is not None else _invalid_messages()
    normalized = [normalize_warroom_v2_ws_receiver_only_client_cp5_message(item, source_kind="invalid_fixture", allow_normalize=True) for item in source] if ready else []
    invalid = [item for item in normalized if not item.get("normalized_ok") or item.get("message_kind") == "unknown"]
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_invalid_message_handling_packet",
        "invalid_message_handling_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36n_cp5_invalid_message_handling",
        "normalizer_core_kind_recognized": core.get("packet_kind") == _CORE_KIND,
        "invalid_message_handling_ready": ready,
        "message_count": len(normalized),
        "invalid_message_count": len(invalid),
        "normalized_messages": normalized,
        "dropped_count": 0,
        "raw_payload_returned": False,
        "metadata_only": True,
        "external_network_used": False,
        "websocket_imported": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }
