# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/local_event_queue.py
# desc: WarRoom v2 disabled local event queue/state holder. Pure functions only; no sockets, IO, runtime, or execution behavior.

from __future__ import annotations

from typing import Any, Iterable, Mapping

WARROOM_V2_LOCAL_EVENT_QUEUE_VERSION = "prediction_warroom.v2.local_event_queue.ps_q30f.v1"
DEFAULT_MAX_EVENTS = 32


def build_warroom_v2_local_event_queue_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "local_event_queue_version": WARROOM_V2_LOCAL_EVENT_QUEUE_VERSION,
        "queue_kind": "disabled_local_event_queue_state_holder",
        "input_kind": "read_model_event_bridge_packet",
        "event_filter": "changed_only",
        "fingerprint_state_unit": "widget_id",
        "bounded_max_events_default": DEFAULT_MAX_EVENTS,
        "transport_implemented_now": False,
        "queue_starts_transport": False,
        "queue_reads_dhot": False,
        "queue_writes_runtime_artifact": False,
        "queue_invokes_classifier": False,
        "future_websocket_compatible": True,
        "future_sse_compatible": True,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
    }


def extract_changed_event_packets(bridge_packet: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    packet = dict(bridge_packet or {})
    candidates = [packet.get("market_snapshot_event"), packet.get("chart_review_event")]
    if packet.get("event") and packet.get("envelope"):
        candidates.append(packet)
    events: list[dict[str, Any]] = []
    for item in candidates:
        event_packet = dict(item or {})
        if event_packet and bool(event_packet.get("changed")):
            events.append(event_packet)
    return events


def build_warroom_v2_local_event_queue_state(*, events: Iterable[Mapping[str, Any]] | None = None, fingerprints: Mapping[str, str] | None = None, max_events: int = DEFAULT_MAX_EVENTS) -> dict[str, Any]:
    bounded = max(1, int(max_events or DEFAULT_MAX_EVENTS))
    event_list = [dict(item) for item in list(events or [])][-bounded:]
    fp_state = dict(fingerprints or {})
    for event_packet in event_list:
        widget_id = str(event_packet.get("widget_id") or "")
        fingerprint = str(event_packet.get("current_fingerprint") or "")
        if widget_id and fingerprint:
            fp_state[widget_id] = fingerprint
    return {
        "ok": True,
        "local_event_queue_version": WARROOM_V2_LOCAL_EVENT_QUEUE_VERSION,
        "queue_kind": "disabled_local_event_queue_state_holder",
        "max_events": bounded,
        "event_count": len(event_list),
        "events": event_list,
        "fingerprints": fp_state,
        "topics": [str(item.get("topic") or "") for item in event_list],
        "transport_implemented_now": False,
        "queue_starts_transport": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
    }


def update_warroom_v2_local_event_queue_from_bridge(*, queue_state: Mapping[str, Any] | None = None, bridge_packet: Mapping[str, Any] | None = None, max_events: int = DEFAULT_MAX_EVENTS) -> dict[str, Any]:
    previous = dict(queue_state or {})
    existing_events = [dict(item) for item in list(previous.get("events") or [])]
    fingerprints = dict(previous.get("fingerprints") or {})
    new_events = extract_changed_event_packets(bridge_packet)
    return build_warroom_v2_local_event_queue_state(events=[*existing_events, *new_events], fingerprints=fingerprints, max_events=max_events)
