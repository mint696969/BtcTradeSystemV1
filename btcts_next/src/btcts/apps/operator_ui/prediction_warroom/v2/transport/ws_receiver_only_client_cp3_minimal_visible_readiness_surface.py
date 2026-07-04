# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp3_minimal_visible_readiness_surface.py
# desc: PS-Q35Z CP3 minimal visible readiness surface. Existing compact badge only; no controls, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp3_minimal_visible_readiness_surface.ps_q35z.v1"
STATE_KEY = "warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_q35z"
_GATE_KIND = "warroom_v2_ws_receiver_only_client_cp3_visible_readiness_implementation_gate_packet"


def build_warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "cp3_minimal_visible_readiness_surface_version": VERSION,
        "state_key": STATE_KEY,
        "slice": "q35z_cp3_minimal_visible_readiness_surface",
        "selected_visible_surface": "existing_compact_status_badge",
        "requires_q35y_gate_packet": True,
        "requires_compact_badge_packet": True,
        "requires_allow_minimal_surface_flag": True,
        "warroom_page_modified": True,
        "warroom_page_visible_ui_modified": True,
        "visible_controls_added": False,
        "additional_markdown_calls_added": False,
        "read_only": True,
        "metadata_only": True,
        "raw_gate_packet_returned": False,
        "raw_badge_packet_returned": False,
        "aggregator_exports_added": False,
        "live_stream_enabled": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
        "would_send_to_broker": False,
    }


def build_warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_packet(
    *,
    compact_badge_packet: Mapping[str, Any] | None = None,
    implementation_gate_packet: Mapping[str, Any] | None = None,
    allow_minimal_surface: bool = False,
) -> dict[str, Any]:
    badge = dict(compact_badge_packet or {})
    gate = dict(implementation_gate_packet or {})
    gate_ready = gate.get("packet_kind") == _GATE_KIND and bool(gate.get("cp3_visible_readiness_implementation_gate_ready"))
    badge_visible = bool(badge.get("compact_status_badge_visible_now") or badge.get("streamlit_markdown_allowed"))
    visible_now = bool(allow_minimal_surface and gate_ready and badge_visible)
    base_line = str(badge.get("compact_badge_markdown") or "`WS Receiver` no socket/send")
    label = str(gate.get("receiver_visible_readiness_label") or "cp1_pending")
    line = f"{base_line} · readiness={label} · live=off" if visible_now else ""
    return {
        **build_warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp3_minimal_visible_readiness_surface_packet",
        "allow_minimal_surface": bool(allow_minimal_surface),
        "implementation_gate_ready": gate_ready,
        "compact_badge_visible_now": badge_visible,
        "cp3_minimal_visible_readiness_surface_visible_now": visible_now,
        "cp3_visible_readiness_visible_now": visible_now,
        "receiver_visible_readiness_label": label,
        "visible_readiness_markdown": line,
        "visible_controls_added": False,
        "live_stream_enabled": False,
        "socket_opened": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "not_sending_external_messages": True,
        "send_disabled": True,
    }
