# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp5_fake_source_normalization.py
# desc: PS-Q36L CP5 fake source normalization. Normalizes CP4 fake summaries only; no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_message_normalizer_core import normalize_warroom_v2_ws_receiver_only_client_cp5_message

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp5_fake_source_normalization.ps_q36l.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_q36l"
_CORE_KIND = "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet"
_SOURCE_KIND = "warroom_v2_ws_receiver_only_client_cp4_fake_message_source_packet"


def build_warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_packet(
    fake_message_source_packet: Mapping[str, Any] | None = None,
    *,
    normalizer_core_packet: Mapping[str, Any] | None = None,
    allow_fake_source_normalization: bool = False,
) -> dict[str, Any]:
    source = dict(fake_message_source_packet or {})
    core = dict(normalizer_core_packet or {})
    source_ready = source.get("packet_kind") == _SOURCE_KIND and bool(source.get("fake_message_source_ready"))
    core_ready = core.get("packet_kind") == _CORE_KIND and bool(core.get("cp5_message_normalizer_core_ready"))
    ready = bool(allow_fake_source_normalization and source_ready and core_ready)
    summaries = list(source.get("fake_message_summaries") or []) if ready else []
    normalized = [normalize_warroom_v2_ws_receiver_only_client_cp5_message(item, source_kind="cp4_fake_source", allow_normalize=True) for item in summaries]
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_packet",
        "fake_source_normalization_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36l_cp5_fake_source_normalization",
        "fake_source_kind_recognized": source.get("packet_kind") == _SOURCE_KIND,
        "normalizer_core_kind_recognized": core.get("packet_kind") == _CORE_KIND,
        "fake_source_normalization_ready": ready,
        "message_count": len(normalized),
        "normalized_messages": normalized,
        "normalized_ok_count": sum(1 for item in normalized if item.get("normalized_ok")),
        "fake_messages_only": True,
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
