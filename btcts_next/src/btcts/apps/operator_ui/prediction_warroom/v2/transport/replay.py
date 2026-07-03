# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/replay.py
# desc: WarRoom v2 transport replay and reconnect helpers. Pure cursor/event selection only; no sockets, UI, IO, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .consumer_state import build_warroom_v2_replay_cursor_from_consumer_state
from .schema import normalize_warroom_v2_transport_message, validate_warroom_v2_transport_message
from .topic_policy import is_warroom_v2_display_topic

WARROOM_V2_REPLAY_VERSION = "prediction_warroom.v2.transport.replay.ps_q31d.v1"
DEFAULT_REPLAY_BOUND = 32


def build_warroom_v2_replay_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "replay_version": WARROOM_V2_REPLAY_VERSION,
        "replay_kind": "warroom_v2_display_reconnect_replay_helpers",
        "cursor_scope": "topic_to_last_sequence",
        "replay_bound_default": DEFAULT_REPLAY_BOUND,
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


def build_warroom_v2_reconnect_request(*, consumer_state: Mapping[str, Any] | None = None, subscribed_topics: Iterable[str] | None = None) -> dict[str, Any]:
    cursor = build_warroom_v2_replay_cursor_from_consumer_state(consumer_state)
    topics = [str(topic) for topic in (subscribed_topics or cursor.keys()) if is_warroom_v2_display_topic(str(topic))]
    return {"ok": True, "replay_version": WARROOM_V2_REPLAY_VERSION, "request_kind": "warroom_v2_reconnect_replay_request", "topics": topics, "cursor": {topic: int(cursor.get(topic, 0)) for topic in topics}, "transport_enabled": False, "websocket_enabled": False, "sse_enabled": False}


def select_warroom_v2_replay_events_after_cursor(*, messages: Iterable[Mapping[str, Any]] | None = None, cursor: Mapping[str, int] | None = None, max_events: int = DEFAULT_REPLAY_BOUND) -> list[dict[str, Any]]:
    limit = max(1, int(max_events or DEFAULT_REPLAY_BOUND))
    topic_cursor = {str(topic): int(sequence) for topic, sequence in dict(cursor or {}).items()}
    selected: list[dict[str, Any]] = []
    for item in messages or []:
        if not validate_warroom_v2_transport_message(item)["ok"]:
            continue
        message = normalize_warroom_v2_transport_message(item)
        topic = message["topic"]
        if is_warroom_v2_display_topic(topic) and int(message["sequence"]) > int(topic_cursor.get(topic, 0)):
            selected.append(message)
    return selected[:limit]


def build_warroom_v2_latest_snapshot_by_topic(messages: Iterable[Mapping[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    snapshots: dict[str, dict[str, Any]] = {}
    for item in messages or []:
        if not validate_warroom_v2_transport_message(item)["ok"]:
            continue
        message = normalize_warroom_v2_transport_message(item)
        topic = message["topic"]
        if not is_warroom_v2_display_topic(topic):
            continue
        if topic not in snapshots or int(message["sequence"]) >= int(snapshots[topic].get("sequence") or 0):
            snapshots[topic] = message
    return snapshots


def build_warroom_v2_replay_response(*, messages: Iterable[Mapping[str, Any]] | None = None, cursor: Mapping[str, int] | None = None, max_events: int = DEFAULT_REPLAY_BOUND) -> dict[str, Any]:
    message_list = [dict(item) for item in list(messages or [])]
    replay_events = select_warroom_v2_replay_events_after_cursor(messages=message_list, cursor=cursor, max_events=max_events)
    latest_snapshots = build_warroom_v2_latest_snapshot_by_topic(message_list)
    total_after_cursor = len(select_warroom_v2_replay_events_after_cursor(messages=message_list, cursor=cursor, max_events=max(len(message_list), 1)))
    gap_marker = total_after_cursor > len(replay_events)
    return {"ok": True, "replay_version": WARROOM_V2_REPLAY_VERSION, "response_kind": "warroom_v2_reconnect_replay_response", "replay_events": replay_events, "replay_event_count": len(replay_events), "latest_snapshots": latest_snapshots, "latest_snapshot_topics": sorted(latest_snapshots), "gap_marker": gap_marker, "max_events": max(1, int(max_events or DEFAULT_REPLAY_BOUND)), "transport_enabled": False, "websocket_enabled": False, "sse_enabled": False, "runtime_connected": False, "would_send_to_broker": False}
