# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_visible_readiness_readback.py
# desc: PS-Q36A CP3 visible readiness readback. Reads visible readiness metadata only; no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp3_visible_readiness_readback.ps_q36a.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_q36a"
_SURFACE_KIND = "warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_packet"


def build_warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_packet(
    surface_packet: Mapping[str, Any] | None = None,
    *,
    allow_visible_readiness_readback: bool = False,
) -> dict[str, Any]:
    surface = dict(surface_packet or {})
    recognized = surface.get("packet_kind") == _SURFACE_KIND
    ready = bool(allow_visible_readiness_readback and recognized and surface.get("cp3_visible_readiness_visible_now"))
    return {
        "ok": True,
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_readback_packet",
        "cp3_visible_readiness_readback_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q36a_cp3_visible_readiness_readback",
        "surface_kind_recognized": recognized,
        "cp3_visible_readiness_readback_ready": ready,
        "visible_readiness_markdown_present": bool(surface.get("visible_readiness_markdown")) if ready else False,
        "receiver_visible_readiness_label": str(surface.get("receiver_visible_readiness_label") or "") if ready else "",
        "read_only": True,
        "metadata_only": True,
        "raw_surface_packet_returned": False,
        "session_state_keys_returned": False,
        "visible_controls_added": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }
