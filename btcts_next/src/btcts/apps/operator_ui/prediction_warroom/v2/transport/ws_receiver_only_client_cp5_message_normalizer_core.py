# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp5_message_normalizer_core.py
# desc: PS-Q36K CP5 message normalizer core. Pure metadata normalization only; no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp5_message_normalizer_core.ps_q36k.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_q36k"
_CONTRACT_KIND = "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_contract_packet"


def _int_value(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _message_kind(topic: str) -> str:
    lowered = topic.lower()
    if "heartbeat" in lowered:
        return "heartbeat"
    if "tick" in lowered:
        return "tick"
    if topic:
        return "unknown"
    return "missing_topic"


def normalize_warroom_v2_ws_receiver_only_client_cp5_message(
    message: Mapping[str, Any] | None,
    *,
    source_kind: str = "unknown",
    allow_normalize: bool = False,
) -> dict[str, Any]:
    item = dict(message or {})
    topic = str(item.get("topic") or "")
    symbol = str(item.get("symbol") or "")
    sequence = _int_value(item.get("sequence"))
    kind = _message_kind(topic)
    invalid_reason = ""
    if not allow_normalize:
        invalid_reason = "normalization_not_allowed"
    elif not topic:
        invalid_reason = "missing_topic"
    elif sequence <= 0:
        invalid_reason = "missing_or_invalid_sequence"
    normalized_ok = not invalid_reason
    return {
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_normalized_message_metadata",
        "normalizer_core_version": VERSION,
        "topic": topic,
        "symbol": symbol,
        "sequence": sequence,
        "source_kind": str(source_kind or "unknown"),
        "message_kind": kind,
        "normalized_ok": normalized_ok,
        "invalid_reason": invalid_reason,
        "dropped": False,
        "raw_payload_returned": False,
        "metadata_only": True,
        "external_network_used": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }


def build_warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet(
    contract_packet: Mapping[str, Any] | None = None,
    *,
    sample_message: Mapping[str, Any] | None = None,
    allow_core_normalization: bool = False,
) -> dict[str, Any]:
    contract = dict(contract_packet or {})
    recognized = contract.get("packet_kind") == _CONTRACT_KIND
    ready = bool(allow_core_normalization and recognized and contract.get("cp5_message_normalizer_contract_ready"))
    normalized = normalize_warroom_v2_ws_receiver_only_client_cp5_message(sample_message or {"topic": "fake.btc.tick", "symbol": "BTC", "sequence": 1}, source_kind="core_sample", allow_normalize=ready)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet",
        "state_key": STATE_KEY,
        "slice": "q36k_cp5_message_normalizer_core",
        "contract_kind_recognized": recognized,
        "cp5_message_normalizer_core_ready": ready,
        "sample_normalized_message": normalized,
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
