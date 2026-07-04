# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp5_normalized_state_readback.py
# desc: PS-Q36O CP5 normalized state write/readback. Writes normalized metadata to target state only; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp5_normalized_state_readback.ps_q36o.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp5_normalized_state_q36o"
_FAKE_KIND = "warroom_v2_ws_receiver_only_client_cp5_fake_source_normalization_packet"
_LIVE_KIND = "warroom_v2_ws_receiver_only_client_cp5_live_shaped_fixture_normalization_packet"
_INVALID_KIND = "warroom_v2_ws_receiver_only_client_cp5_invalid_message_handling_packet"
_RECORD_KIND = "warroom_v2_ws_receiver_only_client_cp5_normalized_state_record"


def _messages(packet: Mapping[str, Any], expected_kind: str) -> list[dict[str, Any]]:
    if packet.get("packet_kind") != expected_kind:
        return []
    return [dict(item) for item in list(packet.get("normalized_messages") or []) if isinstance(item, Mapping)]


def apply_warroom_v2_ws_receiver_only_client_cp5_normalized_state_write(
    target_state: MutableMapping[str, Any] | None,
    *,
    fake_source_normalization_packet: Mapping[str, Any] | None = None,
    live_shaped_fixture_normalization_packet: Mapping[str, Any] | None = None,
    invalid_message_handling_packet: Mapping[str, Any] | None = None,
    allow_normalized_state_write: bool = False,
    state_key: str = STATE_KEY,
) -> dict[str, Any]:
    fake = dict(fake_source_normalization_packet or {})
    live = dict(live_shaped_fixture_normalization_packet or {})
    invalid = dict(invalid_message_handling_packet or {})
    normalized = _messages(fake, _FAKE_KIND) + _messages(live, _LIVE_KIND) + _messages(invalid, _INVALID_KIND)
    ready = bool(allow_normalized_state_write and target_state is not None and normalized)
    invalid_count = sum(1 for item in normalized if not item.get("normalized_ok") or item.get("message_kind") == "unknown")
    record = {
        "packet_kind": _RECORD_KIND,
        "normalized_state_version": VERSION,
        "message_count": len(normalized),
        "invalid_message_count": invalid_count,
        "latest_normalized_message": normalized[-1] if normalized else {},
        "source_kinds": sorted({str(item.get("source_kind") or "") for item in normalized if item.get("source_kind")}),
        "normalized_messages": normalized,
        "raw_payload_returned": False,
        "metadata_only": True,
        "external_network_used": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "send_disabled": True,
    } if ready else {}
    if ready and target_state is not None:
        target_state[state_key] = record
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_normalized_state_write_packet",
        "state_key": state_key,
        "slice": "q36o_cp5_normalized_state_write",
        "normalized_state_write_ready": ready,
        "target_state_mutated": ready,
        "message_count": len(normalized) if ready else 0,
        "invalid_message_count": invalid_count if ready else 0,
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


def build_warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_packet(
    target_state: Mapping[str, Any] | None,
    *,
    state_key: str = STATE_KEY,
    allow_normalized_state_readback: bool = False,
) -> dict[str, Any]:
    state = dict(target_state or {})
    record = state.get(state_key)
    record = dict(record) if isinstance(record, Mapping) else {}
    recognized = record.get("packet_kind") == _RECORD_KIND
    ready = bool(allow_normalized_state_readback and recognized)
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_normalized_state_readback_packet",
        "state_key": state_key,
        "slice": "q36o_cp5_normalized_state_readback",
        "normalized_state_record_kind_recognized": recognized,
        "normalized_state_readback_ready": ready,
        "message_count": int(record.get("message_count") or 0) if ready else 0,
        "invalid_message_count": int(record.get("invalid_message_count") or 0) if ready else 0,
        "latest_normalized_message": dict(record.get("latest_normalized_message") or {}) if ready else {},
        "session_state_keys_returned": False,
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
