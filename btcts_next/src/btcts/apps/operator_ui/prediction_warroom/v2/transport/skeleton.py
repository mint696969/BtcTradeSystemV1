# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/skeleton.py
# desc: WarRoom v2 local-only disabled producer/consumer skeleton. Pure lifecycle shape only; no sockets, UI, IO, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .consumer_state import apply_warroom_v2_consumer_message, build_empty_warroom_v2_consumer_state
from .simulator import build_warroom_v2_disabled_transport_simulation_frame
from .topic_policy import build_warroom_v2_topic_policy_contract

WARROOM_V2_LOCAL_DISABLED_SKELETON_VERSION = "prediction_warroom.v2.transport.skeleton.ps_q31f.v1"


def build_warroom_v2_local_disabled_transport_flags(
    *,
    transport_enabled: bool = False,
    local_loop_enabled: bool = False,
    producer_enabled: bool = False,
    consumer_enabled: bool = False,
) -> dict[str, Any]:
    return {
        "ok": True,
        "skeleton_version": WARROOM_V2_LOCAL_DISABLED_SKELETON_VERSION,
        "requested_flags": {
            "transport_enabled": bool(transport_enabled),
            "local_loop_enabled": bool(local_loop_enabled),
            "producer_enabled": bool(producer_enabled),
            "consumer_enabled": bool(consumer_enabled),
        },
        "effective_flags": {
            "transport_enabled": False,
            "local_loop_enabled": False,
            "producer_enabled": False,
            "consumer_enabled": False,
            "message_emission_enabled": False,
            "websocket_enabled": False,
            "sse_enabled": False,
            "push_connected": False,
            "runtime_connected": False,
        },
        "operator_review_required_before_enable": True,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }


def build_warroom_v2_local_disabled_skeleton_contract() -> dict[str, Any]:
    flags = build_warroom_v2_local_disabled_transport_flags()
    return {
        "ok": True,
        "skeleton_version": WARROOM_V2_LOCAL_DISABLED_SKELETON_VERSION,
        "skeleton_kind": "local_only_disabled_producer_consumer_lifecycle_shape",
        "transport_kind": "local_only_disabled_in_process",
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "producer_shape": "disabled_shadow_frame_source",
        "consumer_shape": "disabled_shadow_consumer_state_projection",
        "topic_policy_scope": build_warroom_v2_topic_policy_contract()["policy_scope"],
        "flags": flags,
        "visible_ui_decoration_added": False,
        "fragment_refresh_replaced": False,
        "transport_enabled_default": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }


def build_warroom_v2_local_disabled_producer_packet(
    *,
    messages: Iterable[Mapping[str, Any]] | None = None,
    frame_id: str = "local-disabled-producer",
    max_messages: int = 32,
) -> dict[str, Any]:
    shadow_frame = build_warroom_v2_disabled_transport_simulation_frame(messages=messages, frame_id=frame_id, max_messages=max_messages)
    return {
        "ok": True,
        "skeleton_version": WARROOM_V2_LOCAL_DISABLED_SKELETON_VERSION,
        "packet_kind": "local_only_disabled_producer_packet",
        "producer_enabled_effective": False,
        "message_emission_enabled": False,
        "emitted_message_count": 0,
        "shadow_frame_message_count": int(shadow_frame.get("message_count") or 0),
        "shadow_frame": shadow_frame,
        "transport_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }


def build_warroom_v2_local_disabled_consumer_packet(
    *,
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    received_at: str = "",
) -> dict[str, Any]:
    state: Mapping[str, Any] = consumer_state or build_empty_warroom_v2_consumer_state()
    applied: list[dict[str, Any]] = []
    for message in messages or []:
        result = apply_warroom_v2_consumer_message(consumer_state=state, message=message, received_at=received_at)
        state = result["consumer_state"]
        applied.append({"applied": bool(result["applied"]), "reason": result["decision"].get("reason"), "topic": result["decision"].get("topic"), "sequence": result["decision"].get("sequence")})
    return {
        "ok": True,
        "skeleton_version": WARROOM_V2_LOCAL_DISABLED_SKELETON_VERSION,
        "packet_kind": "local_only_disabled_consumer_packet",
        "consumer_enabled_effective": False,
        "message_emission_enabled": False,
        "projected_message_count": len(applied),
        "projected_results": applied,
        "projected_consumer_state": state,
        "transport_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }


def build_warroom_v2_local_disabled_producer_consumer_cycle(
    *,
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    frame_id: str = "local-disabled-cycle",
    received_at: str = "",
) -> dict[str, Any]:
    message_list = [dict(item) for item in list(messages or [])]
    producer = build_warroom_v2_local_disabled_producer_packet(messages=message_list, frame_id=frame_id)
    consumer = build_warroom_v2_local_disabled_consumer_packet(messages=producer["shadow_frame"].get("messages") or [], consumer_state=consumer_state, received_at=received_at)
    return {
        "ok": True,
        "skeleton_version": WARROOM_V2_LOCAL_DISABLED_SKELETON_VERSION,
        "cycle_kind": "local_only_disabled_producer_consumer_shadow_cycle",
        "producer": producer,
        "consumer": consumer,
        "transport_enabled": False,
        "local_loop_enabled": False,
        "message_emission_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }
