# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp1_completion.py
# desc: WarRoom v2 receiver-only CP1 completion packet. Declares safe receiver preparation complete; no page, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP1_COMPLETION_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp1_completion.ps_q35w.v1"
_GATE_KIND = "warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet"


def _status(*, allow_completion: bool, present: bool, mapping: bool, kind: str, gate_ready: bool) -> str:
    if not allow_completion:
        return "receiver_only_client_cp1_completion_blocked_allow_completion_required"
    if not present:
        return "receiver_only_client_cp1_completion_missing_gate"
    if not mapping:
        return "receiver_only_client_cp1_completion_invalid_gate"
    if kind != _GATE_KIND:
        return "receiver_only_client_cp1_completion_unrecognized_gate"
    if not gate_ready:
        return "receiver_only_client_cp1_completion_blocked_gate_not_ready"
    return "receiver_only_client_cp1_completion_complete_no_send"


def build_warroom_v2_ws_receiver_only_client_cp1_completion_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "cp1_completion_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP1_COMPLETION_VERSION,
        "cp1_completion_kind": "warroom_v2_ws_receiver_only_client_cp1_completion_metadata_only_no_send",
        "input_pipeline": ["q35v_cp1_readiness_gate", "q35w_cp1_completion"],
        "requires_cp1_readiness_gate_packet": True,
        "requires_allow_cp1_completion_flag": True,
        "read_only": True,
        "metadata_only": True,
        "cp1_completion_packet_available": True,
        "cp1_goal": "ws_receiver_safe_receiver_preparation_state_ready",
        "raw_cp1_readiness_gate_packet_returned": False,
        "raw_compact_hidden_health_packet_returned": False,
        "raw_hidden_record_value_returned": False,
        "raw_registry_surface_packet_returned": False,
        "session_state_keys_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "connect_fn_called_at_cp1_completion": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "global_registry_mutated": False,
        "warroom_page_modified": False,
        "warroom_page_visible_ui_modified": False,
        "visible_controls_added": False,
        "visible_information_added": False,
        "streamlit_imported": False,
        "streamlit_render_invoked": False,
        "aggregator_exports_added": False,
        "receiver_only": True,
        "send_disabled": True,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "order_intent_submitted": False,
        "broker_send_enabled": False,
        "would_send_to_broker": False,
        "ledger_append_allowed": False,
        "prediction_generation_invoked": False,
        "prediction_inference_invoked": False,
        "classifier_invoked": False,
    }


def build_warroom_v2_ws_receiver_only_client_cp1_completion_packet(
    cp1_readiness_gate_packet: Mapping[str, Any] | object | None = None,
    *,
    allow_cp1_completion: bool = False,
) -> dict[str, Any]:
    present = cp1_readiness_gate_packet is not None
    mapping = isinstance(cp1_readiness_gate_packet, Mapping)
    gate = dict(cp1_readiness_gate_packet) if mapping else {}
    kind = str(gate.get("packet_kind") or "")
    gate_ready = bool(gate.get("cp1_readiness_gate_ready")) and bool(gate.get("cp1_done_candidate"))
    status = _status(allow_completion=allow_cp1_completion, present=present, mapping=mapping, kind=kind, gate_ready=gate_ready)
    completed = status == "receiver_only_client_cp1_completion_complete_no_send"
    return {
        **build_warroom_v2_ws_receiver_only_client_cp1_completion_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp1_completion_packet",
        "cp1_readiness_gate_present": present,
        "cp1_readiness_gate_is_mapping": mapping,
        "cp1_readiness_gate_kind_recognized": (kind == _GATE_KIND) if mapping else False,
        "cp1_completion_status": status,
        "cp1_completed": completed,
        "cp1_completion_commit_ready": completed,
        "cp1_done_candidate": bool(gate.get("cp1_done_candidate")) if mapping else False,
        "receiver_health_status": str(gate.get("receiver_health_status") or "") if mapping else "",
        "cp1_checkpoint_label": "safe_receiver_preparation_state_ready" if completed else "safe_receiver_preparation_state_blocked",
        "operator_experience_after_cp1": "WarRoom receiver has safe no-send preparation state and hidden metadata health; live stream is not enabled yet.",
        "next_checkpoint": "CP2_fake_receive_loop_then_visible_readiness_and_live_receiver_mode" if completed else "CP1_readiness_gate",
        "read_only": True,
        "metadata_only": True,
        "raw_cp1_readiness_gate_packet_returned": False,
        "raw_compact_hidden_health_packet_returned": False,
        "session_state_keys_returned": False,
        "registry_values_returned": False,
        "registry_keys_returned": False,
        "runtime_config_values_returned": False,
        "runtime_config_keys_returned": False,
        "callable_values_returned": False,
        "registration_key_value_returned": False,
        "endpoint_value_returned": False,
        "token_value_returned": False,
        "connect_fn_called_at_cp1_completion": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "global_registry_mutated": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
