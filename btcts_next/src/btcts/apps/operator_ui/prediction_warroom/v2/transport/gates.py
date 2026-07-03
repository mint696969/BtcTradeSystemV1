# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/gates.py
# desc: WarRoom v2 operator-reviewed local transport enablement gate. Pure decision packets only; no sockets, UI, IO, prediction inference, or execution.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_OPERATOR_GATE_VERSION = "prediction_warroom.v2.transport.gates.ps_q31g.v1"
WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN = "APPROVE_Q31G_LOCAL_ONLY_SHADOW_EXPERIMENT"
REQUIRED_PREVIOUS_GUARDS: tuple[str, ...] = (
    "q31f_focused_guard",
    "q31f_close_guard",
    "q31f_py_compile",
    "q31e_focused_guard",
    "q31d_focused_guard",
    "q31c_focused_guard",
    "q31b_focused_guard",
    "q31a_focused_guard",
)


def build_warroom_v2_operator_reviewed_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "gate_version": WARROOM_V2_OPERATOR_GATE_VERSION,
        "gate_kind": "operator_reviewed_local_transport_enablement_decision_contract",
        "approval_token_required": WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN,
        "candidate_transport_path_default": "local_only_in_process",
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "approval_required_before_enable": True,
        "approval_recorded_default": False,
        "ready_for_next_slice_default": False,
        "transport_enabled_effective": False,
        "local_loop_enabled_effective": False,
        "producer_enabled_effective": False,
        "consumer_enabled_effective": False,
        "message_emission_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "push_connected": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
    }


def _truthy_guard(value: Any) -> bool:
    raw = str(value or "").strip().lower()
    return raw in {"passed", "pass", "ok", "true", "1"} or raw.endswith("_passed")


def build_warroom_v2_operator_gate_evidence_snapshot(evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source = dict(evidence or {})
    guard_results = {name: _truthy_guard(source.get(name)) for name in REQUIRED_PREVIOUS_GUARDS}
    missing = [name for name, passed in guard_results.items() if not passed]
    return {
        "ok": not missing,
        "gate_version": WARROOM_V2_OPERATOR_GATE_VERSION,
        "required_guards": list(REQUIRED_PREVIOUS_GUARDS),
        "guard_results": guard_results,
        "missing_or_failed_guards": missing,
        "focused_guard_count": sum(1 for key in guard_results if key.endswith("focused_guard") and guard_results[key]),
        "close_guard_recorded": guard_results.get("q31f_close_guard", False),
        "py_compile_recorded": guard_results.get("q31f_py_compile", False),
    }


def evaluate_warroom_v2_operator_reviewed_gate(
    *,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str = "",
    requested_transport_path: str = "local_only_in_process",
) -> dict[str, Any]:
    snapshot = build_warroom_v2_operator_gate_evidence_snapshot(evidence)
    requested_path = str(requested_transport_path or "local_only_in_process")
    approved = str(operator_approval_token or "") == WARROOM_V2_LOCAL_ONLY_APPROVAL_TOKEN
    path_allowed = requested_path == "local_only_in_process"
    if not snapshot["ok"]:
        status = "blocked_missing_guard_evidence"
    elif not path_allowed:
        status = "blocked_unsupported_transport_path"
    elif not approved:
        status = "blocked_waiting_for_operator_approval"
    else:
        status = "ready_for_next_slice_not_enabled_here"
    ready = status == "ready_for_next_slice_not_enabled_here"
    return {
        "ok": True,
        "gate_version": WARROOM_V2_OPERATOR_GATE_VERSION,
        "gate_status": status,
        "ready_for_next_slice": ready,
        "next_slice_after_approval": "PS-Q31H_LOCAL_ONLY_TRUE_TRANSPORT_EXPERIMENT" if ready else "",
        "operator_approval_recorded": approved,
        "requested_transport_path": requested_path,
        "candidate_transport_path": "local_only_in_process",
        "unsupported_live_transport_paths": ["websocket", "sse"],
        "evidence_snapshot": snapshot,
        "not_enabled_here": True,
        "transport_enabled_effective": False,
        "local_loop_enabled_effective": False,
        "producer_enabled_effective": False,
        "consumer_enabled_effective": False,
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


def build_warroom_v2_operator_gate_review_packet(
    *,
    evidence: Mapping[str, Any] | None = None,
    operator_approval_token: str = "",
    requested_transport_path: str = "local_only_in_process",
) -> dict[str, Any]:
    contract = build_warroom_v2_operator_reviewed_gate_contract()
    evaluation = evaluate_warroom_v2_operator_reviewed_gate(evidence=evidence, operator_approval_token=operator_approval_token, requested_transport_path=requested_transport_path)
    return {
        "ok": True,
        "gate_version": WARROOM_V2_OPERATOR_GATE_VERSION,
        "packet_kind": "operator_reviewed_local_transport_gate_review_packet",
        "contract": contract,
        "evaluation": evaluation,
        "whole_warroom_display_update_target": True,
        "prediction_cards_display_update_target": True,
        "visible_ui_decoration_added": False,
        "fragment_refresh_replaced": False,
        "transport_enabled_effective": False,
        "local_loop_enabled_effective": False,
        "producer_enabled_effective": False,
        "consumer_enabled_effective": False,
        "message_emission_enabled": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "runtime_connected": False,
        "would_send_to_broker": False,
        "classifier_invoked": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
    }
