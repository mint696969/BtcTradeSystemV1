# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/read_model_event_bridge.py
# desc: WarRoom v2 read-model event bridge prototype. No Streamlit, D-hot reads, sockets, runtime, or execution behavior.

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .contracts import build_widget_update_event
from .transport_ownership import build_warroom_v2_transport_event_envelope

WARROOM_V2_READ_MODEL_EVENT_BRIDGE_VERSION = "prediction_warroom.v2.read_model_event_bridge.ps_q30d.v1"
MARKET_SNAPSHOT_WIDGET_ID = "market_snapshot_strip"
MARKET_SNAPSHOT_TOPIC = "warroom.market.snapshot"
CHART_REVIEW_WIDGET_ID = "chart_review_panel"
CHART_REVIEW_TOPIC = "warroom.chart.review"


def stable_payload_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    encoded = json.dumps(dict(payload or {}), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:24]


def build_warroom_v2_read_model_event_bridge_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "read_model_event_bridge_version": WARROOM_V2_READ_MODEL_EVENT_BRIDGE_VERSION,
        "bridge_kind": "local_read_model_event_bridge_prototype",
        "input_kind": "prebuilt_read_model_payload",
        "output_kind": "widget_update_event_envelope",
        "fingerprint_algorithm": "sha256_json_sort_keys_24",
        "supported_topics": [MARKET_SNAPSHOT_TOPIC, CHART_REVIEW_TOPIC],
        "transport_implemented_now": False,
        "bridge_starts_transport": False,
        "bridge_reads_dhot": False,
        "bridge_invokes_classifier": False,
        "bridge_writes_runtime_artifact": False,
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


def build_warroom_v2_read_model_update_event(
    *,
    widget_id: str,
    topic: str,
    payload: Mapping[str, Any] | None = None,
    generated_at: str = "",
    previous_fingerprint: str = "",
    sequence: int = 0,
    title: str = "",
    channel: str = "local_bridge_disabled_transport",
) -> dict[str, Any]:
    current_fingerprint = stable_payload_fingerprint(payload)
    event = build_widget_update_event(
        widget_id=str(widget_id),
        topic=str(topic),
        generated_at=str(generated_at),
        previous_fingerprint=str(previous_fingerprint),
        current_fingerprint=current_fingerprint,
        sequence=int(sequence),
        title=str(title),
        payload=dict(payload or {}),
        source_kind="local_read_model_event_bridge_prototype",
    )
    envelope = build_warroom_v2_transport_event_envelope(widget_update_event=event, channel=channel)
    return {
        "ok": True,
        "read_model_event_bridge_version": WARROOM_V2_READ_MODEL_EVENT_BRIDGE_VERSION,
        "widget_id": str(widget_id),
        "topic": str(topic),
        "generated_at": str(generated_at),
        "previous_fingerprint": str(previous_fingerprint),
        "current_fingerprint": current_fingerprint,
        "changed": bool(event["changed"]),
        "event": event,
        "envelope": envelope,
        "transport_implemented_now": False,
        "bridge_starts_transport": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "push_connected": False,
        "read_only": True,
        "display_only": True,
        "would_send_to_broker": False,
    }


def build_warroom_v2_market_snapshot_update_event(*, snapshot_payload: Mapping[str, Any] | None = None, generated_at: str = "", previous_fingerprint: str = "", sequence: int = 0) -> dict[str, Any]:
    return build_warroom_v2_read_model_update_event(widget_id=MARKET_SNAPSHOT_WIDGET_ID, topic=MARKET_SNAPSHOT_TOPIC, payload=snapshot_payload, generated_at=generated_at, previous_fingerprint=previous_fingerprint, sequence=sequence, title="Market Snapshot")


def build_warroom_v2_chart_review_update_event(*, chart_payload: Mapping[str, Any] | None = None, generated_at: str = "", previous_fingerprint: str = "", sequence: int = 0) -> dict[str, Any]:
    return build_warroom_v2_read_model_update_event(widget_id=CHART_REVIEW_WIDGET_ID, topic=CHART_REVIEW_TOPIC, payload=chart_payload, generated_at=generated_at, previous_fingerprint=previous_fingerprint, sequence=sequence, title="Chart Review")
