# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/disabled_transport_adapter.py
# desc: WarRoom v2 disabled transport adapter payload contract. Pure functions only; does not open sockets or send events.

from __future__ import annotations

import json
from typing import Any, Mapping

WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_VERSION = "prediction_warroom.v2.disabled_transport_adapter.ps_q30g.v1"


def build_warroom_v2_disabled_transport_adapter_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "disabled_transport_adapter_version": WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_VERSION,
        "adapter_kind": "disabled_outbound_transport_payload_adapter",
        "input_kind": "local_event_queue_state",
        "output_kind": "outbound_message_payload_contract",
        "message_unit": "widget_update_event_envelope",
        "transport_implemented_now": False,
        "adapter_sends_messages": False,
        "adapter_opens_socket": False,
        "adapter_reads_dhot": False,
        "adapter_writes_runtime_artifact": False,
        "adapter_invokes_classifier": False,
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


def build_warroom_v2_outbound_message_payload(*, event_packet: Mapping[str, Any], transport_kind: str = "disabled_future_stream") -> dict[str, Any]:
    event_data = dict(event_packet)
    envelope = dict(event_data.get("envelope") or {})
    event = dict(event_data.get("event") or envelope.get("event") or {})
    topic = str(event_data.get("topic") or envelope.get("topic") or event.get("topic") or "")
    widget_id = str(event_data.get("widget_id") or envelope.get("widget_id") or dict(event.get("read_model") or {}).get("widget_id") or "")
    payload = {
        "adapter_version": WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_VERSION,
        "transport_kind": str(transport_kind),
        "topic": topic,
        "widget_id": widget_id,
        "sequence": int(envelope.get("sequence") or event.get("sequence") or 0),
        "changed": bool(event_data.get("changed") if "changed" in event_data else envelope.get("changed")),
        "message_type": "warroom_v2_widget_update",
        "payload_kind": "widget_update_event_envelope",
        "envelope": envelope or event_data,
        "ui_patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "transport_implemented_now": False,
        "adapter_sends_messages": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
    }
    payload["json_payload"] = json.dumps(payload["envelope"], ensure_ascii=False, sort_keys=True, default=str)
    return payload


def build_warroom_v2_disabled_transport_outbox(*, queue_state: Mapping[str, Any] | None = None, transport_kind: str = "disabled_future_stream", max_messages: int = 32) -> dict[str, Any]:
    state = dict(queue_state or {})
    bounded = max(1, int(max_messages or 32))
    messages = [build_warroom_v2_outbound_message_payload(event_packet=dict(item), transport_kind=transport_kind) for item in list(state.get("events") or [])[-bounded:]]
    return {
        "ok": True,
        "disabled_transport_adapter_version": WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_VERSION,
        "adapter_kind": "disabled_outbound_transport_payload_adapter",
        "transport_kind": str(transport_kind),
        "max_messages": bounded,
        "message_count": len(messages),
        "messages": messages,
        "topics": [message["topic"] for message in messages],
        "widget_ids": [message["widget_id"] for message in messages],
        "transport_implemented_now": False,
        "adapter_sends_messages": False,
        "adapter_opens_socket": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
    }
