# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp5_live_shaped_fixture_normalization.py
# desc: PS-Q36M CP5 live-shaped fixture normalization. Local fixture normalization only; no network, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.prediction_warroom.v2.transport.ws_receiver_only_client_cp5_message_normalizer_core import normalize_warroom_v2_ws_receiver_only_client_cp5_message

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp5_live_shaped_fixture_normalization.ps_q36m.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp5_live_shaped_fixture_normalization_q36m"
_CORE_KIND = "warroom_v2_ws_receiver_only_client_cp5_message_normalizer_core_packet"


def _fixtures() -> list[dict[str, Any]]:
    return [
        {"topic": "live_shaped.btc.tick", "symbol": "BTC", "sequence": 10},
        {"topic": "live_shaped.heartbeat", "symbol": "BTC", "sequence": 11},
    ]


def build_warroom_v2_ws_receiver_only_client_cp5_live_shaped_fixture_normalization_packet(
    normalizer_core_packet: Mapping[str, Any] | None = None,
    *,
    allow_live_shaped_fixture_normalization: bool = False,
) -> dict[str, Any]:
    core = dict(normalizer_core_packet or {})
    core_ready = core.get("packet_kind") == _CORE_KIND and bool(core.get("cp5_message_normalizer_core_ready"))
    ready = bool(allow_live_shaped_fixture_normalization and core_ready)
    normalized = [normalize_warroom_v2_ws_receiver_only_client_cp5_message(item, source_kind="local_live_shaped_fixture", allow_normalize=True) for item in _fixtures()] if ready else []
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp5_live_shaped_fixture_normalization_packet",
        "live_shaped_fixture_normalization_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36m_cp5_live_shaped_fixture_normalization",
        "normalizer_core_kind_recognized": core.get("packet_kind") == _CORE_KIND,
        "live_shaped_fixture_normalization_ready": ready,
        "fixture_source": "local_only",
        "message_count": len(normalized),
        "normalized_messages": normalized,
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
