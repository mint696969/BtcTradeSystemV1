# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/consumer_state.py
# desc: WarRoom v2 transport consumer state and dedup helpers. Pure state transitions only; no sockets, UI, IO, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Mapping

from .schema import normalize_warroom_v2_transport_message, validate_warroom_v2_transport_message

WARROOM_V2_CONSUMER_STATE_VERSION = "prediction_warroom.v2.transport.consumer_state.ps_q31d.v1"


def _fingerprint(message: Mapping[str, Any] | None = None) -> str:
    raw = dict(message or {})
    envelope = dict(raw.get("envelope") or {})
    event = dict(envelope.get("event") or raw.get("event") or {})
    return str(raw.get("current_fingerprint") or event.get("current_fingerprint") or envelope.get("current_fingerprint") or "")


def build_warroom_v2_consumer_state_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "consumer_state_version": WARROOM_V2_CONSUMER_STATE_VERSION,
        "state_kind": "warroom_v2_display_consumer_sequence_fingerprint_state",
        "state_scope": "per_topic_and_widget",
        "patch_unit": "widget_dom_region",
        "broad_page_reload_required": False,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "transport_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
    }


def build_empty_warroom_v2_consumer_state() -> dict[str, Any]:
    return {
        "ok": True,
        "consumer_state_version": WARROOM_V2_CONSUMER_STATE_VERSION,
        "state_kind": "warroom_v2_display_consumer_sequence_fingerprint_state",
        "topics": {},
        "widgets": {},
        "applied_count": 0,
        "dropped_count": 0,
        "transport_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
    }


def decide_warroom_v2_consumer_message_action(*, consumer_state: Mapping[str, Any] | None = None, message: Mapping[str, Any] | None = None) -> dict[str, Any]:
    state = dict(consumer_state or build_empty_warroom_v2_consumer_state())
    validation = validate_warroom_v2_transport_message(message)
    normalized = dict(validation["message"])
    topic = normalized["topic"]
    widget_id = normalized["widget_id"]
    sequence = int(normalized["sequence"])
    fingerprint = _fingerprint(message)
    if not validation["ok"]:
        return {"ok": True, "apply": False, "reason": "invalid_message", "errors": validation["errors"], "message": normalized}
    topic_state = dict(dict(state.get("topics") or {}).get(topic) or {})
    widget_state = dict(dict(state.get("widgets") or {}).get(widget_id) or {})
    last_sequence = int(topic_state.get("last_sequence") if "last_sequence" in topic_state else -1)
    last_fingerprint = str(widget_state.get("last_fingerprint") or "")
    if sequence < last_sequence:
        reason = "stale_sequence"
        apply = False
    elif sequence == last_sequence and fingerprint and fingerprint == last_fingerprint:
        reason = "duplicate_fingerprint"
        apply = False
    elif sequence == last_sequence and fingerprint != last_fingerprint:
        reason = "same_sequence_changed_fingerprint"
        apply = True
    else:
        reason = "newer_sequence" if last_sequence >= 0 else "first_message"
        apply = True
    return {"ok": True, "apply": apply, "reason": reason, "topic": topic, "widget_id": widget_id, "sequence": sequence, "fingerprint": fingerprint, "last_sequence": last_sequence, "last_fingerprint": last_fingerprint, "message": normalized}


def apply_warroom_v2_consumer_message(*, consumer_state: Mapping[str, Any] | None = None, message: Mapping[str, Any] | None = None, received_at: str = "") -> dict[str, Any]:
    state = dict(consumer_state or build_empty_warroom_v2_consumer_state())
    state["topics"] = dict(state.get("topics") or {})
    state["widgets"] = dict(state.get("widgets") or {})
    decision = decide_warroom_v2_consumer_message_action(consumer_state=state, message=message)
    if not decision["apply"]:
        state["dropped_count"] = int(state.get("dropped_count") or 0) + 1
        return {"ok": True, "applied": False, "decision": decision, "consumer_state": state}
    topic = decision["topic"]
    widget_id = decision["widget_id"]
    sequence = int(decision["sequence"])
    fingerprint = str(decision.get("fingerprint") or "")
    state["topics"][topic] = {"last_sequence": sequence, "last_received_at": str(received_at)}
    state["widgets"][widget_id] = {"topic": topic, "last_sequence": sequence, "last_fingerprint": fingerprint, "last_received_at": str(received_at)}
    state["applied_count"] = int(state.get("applied_count") or 0) + 1
    return {"ok": True, "applied": True, "decision": decision, "consumer_state": state}


def build_warroom_v2_replay_cursor_from_consumer_state(consumer_state: Mapping[str, Any] | None = None) -> dict[str, int]:
    state = dict(consumer_state or {})
    cursor: dict[str, int] = {}
    for topic, topic_state in dict(state.get("topics") or {}).items():
        cursor[str(topic)] = int(dict(topic_state or {}).get("last_sequence") or 0)
    return cursor
