# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/local_loop.py
# desc: WarRoom v2 local-only true transport experiment. Pure in-process packet handoff only; no sockets, UI, IO, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .consumer_state import apply_warroom_v2_consumer_message, build_empty_warroom_v2_consumer_state
from .gates import evaluate_warroom_v2_operator_reviewed_gate
from .schema import normalize_warroom_v2_transport_message, validate_warroom_v2_transport_message
from .topic_policy import is_warroom_v2_display_topic

WARROOM_V2_LOCAL_ONLY_TRANSPORT_EXPERIMENT_VERSION = "prediction_warroom.v2.transport.local_loop.ps_q31h.v1"


def build_warroom_v2_local_only_transport_experiment_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "local_loop_version": WARROOM_V2_LOCAL_ONLY_TRANSPORT_EXPERIMENT_VERSION,
        "experiment_kind": "local_only_in_process_true_transport_experiment",
        "transport_kind": "local_only_in_process",
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "operator_review_required": True,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }


def build_warroom_v2_local_only_transport_session(
    *,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str = "",
    requested_transport_path: str = "local_only_in_process",
) -> dict[str, Any]:
    gate = evaluate_warroom_v2_operator_reviewed_gate(evidence=evidence, operator_approval_token=operator_approval_token, requested_transport_path=requested_transport_path)
    enabled = bool(gate.get("ready_for_next_slice") and gate.get("gate_status") == "ready_for_next_slice_not_enabled_here")
    return {
        "ok": True,
        "local_loop_version": WARROOM_V2_LOCAL_ONLY_TRANSPORT_EXPERIMENT_VERSION,
        "session_kind": "local_only_in_process_transport_session",
        "gate": gate,
        "transport_enabled_effective": enabled,
        "local_loop_enabled_effective": enabled,
        "producer_enabled_effective": enabled,
        "consumer_enabled_effective": enabled,
        "message_emission_enabled": enabled,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }


def _display_messages(messages: Iterable[Mapping[str, Any]] | None = None, max_messages: int = 32) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in messages or []:
        validation = validate_warroom_v2_transport_message(item)
        if not validation["ok"]:
            continue
        message = normalize_warroom_v2_transport_message(item)
        if is_warroom_v2_display_topic(message["topic"]):
            normalized.append(message)
    return normalized[: max(0, int(max_messages or 0))]


def build_warroom_v2_local_only_transport_outbox(
    *,
    messages: Iterable[Mapping[str, Any]] | None = None,
    session: Mapping[str, Any] | None = None,
    max_messages: int = 32,
) -> dict[str, Any]:
    active = bool(dict(session or {}).get("message_emission_enabled", False))
    outbox = _display_messages(messages, max_messages=max_messages) if active else []
    return {
        "ok": True,
        "local_loop_version": WARROOM_V2_LOCAL_ONLY_TRANSPORT_EXPERIMENT_VERSION,
        "packet_kind": "local_only_transport_outbox",
        "outbox": outbox,
        "emitted_message_count": len(outbox),
        "blocked_reason": "" if active else "local_only_transport_session_not_enabled",
        "transport_enabled_effective": active,
        "local_loop_enabled_effective": active,
        "producer_enabled_effective": active,
        "message_emission_enabled": active,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }


def apply_warroom_v2_local_only_transport_outbox(
    *,
    outbox: Mapping[str, Any] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    received_at: str = "",
) -> dict[str, Any]:
    packet = dict(outbox or {})
    active = bool(packet.get("message_emission_enabled", False))
    state: Mapping[str, Any] = consumer_state or build_empty_warroom_v2_consumer_state()
    results: list[dict[str, Any]] = []
    if active:
        for message in packet.get("outbox") or []:
            applied = apply_warroom_v2_consumer_message(consumer_state=state, message=message, received_at=received_at)
            state = applied["consumer_state"]
            results.append({"applied": bool(applied["applied"]), "reason": applied["decision"].get("reason"), "topic": applied["decision"].get("topic"), "sequence": applied["decision"].get("sequence")})
    return {
        "ok": True,
        "local_loop_version": WARROOM_V2_LOCAL_ONLY_TRANSPORT_EXPERIMENT_VERSION,
        "packet_kind": "local_only_transport_consumer_application",
        "applied_message_count": sum(1 for item in results if item.get("applied")),
        "projected_result_count": len(results),
        "projected_results": results,
        "projected_consumer_state": state,
        "blocked_reason": "" if active else "local_only_transport_outbox_not_enabled",
        "transport_enabled_effective": active,
        "local_loop_enabled_effective": active,
        "consumer_enabled_effective": active,
        "message_emission_enabled": active,
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }


def run_warroom_v2_local_only_transport_experiment(
    *,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str = "",
    messages: Iterable[Mapping[str, Any]] | None = None,
    consumer_state: Mapping[str, Any] | None = None,
    received_at: str = "",
) -> dict[str, Any]:
    message_list = [dict(item) for item in list(messages or [])]
    session = build_warroom_v2_local_only_transport_session(evidence=evidence, operator_approval_token=operator_approval_token)
    outbox = build_warroom_v2_local_only_transport_outbox(messages=message_list, session=session)
    consumer = apply_warroom_v2_local_only_transport_outbox(outbox=outbox, consumer_state=consumer_state, received_at=received_at)
    return {
        "ok": True,
        "local_loop_version": WARROOM_V2_LOCAL_ONLY_TRANSPORT_EXPERIMENT_VERSION,
        "experiment_kind": "local_only_true_transport_experiment_result",
        "session": session,
        "outbox": outbox,
        "consumer": consumer,
        "transport_enabled_effective": bool(session["transport_enabled_effective"]),
        "local_loop_enabled_effective": bool(session["local_loop_enabled_effective"]),
        "message_emission_enabled": bool(session["message_emission_enabled"]),
        "external_message_send_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }
