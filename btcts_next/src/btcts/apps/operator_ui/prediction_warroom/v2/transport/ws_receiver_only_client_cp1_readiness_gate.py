# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport/ws_receiver_only_client_cp1_readiness_gate.py
# desc: WarRoom v2 receiver-only CP1 readiness gate. Consumes compact hidden health metadata; no page, no socket, no send.

from __future__ import annotations

from typing import Any, Mapping

WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP1_READINESS_GATE_VERSION = "prediction_warroom.v2.transport.ws_receiver_only_client_cp1_readiness_gate.ps_q35v.v1"
_HEALTH_KIND = "warroom_v2_ws_receiver_only_client_registry_surface_compact_hidden_health_packet"
_READY_HEALTH_STATUSES = {"waiting_socket_guards", "attempted_not_open_no_send", "opened_no_send"}


def _status(*, allow_gate: bool, present: bool, mapping: bool, kind: str, candidate: bool) -> str:
    if not allow_gate:
        return "receiver_only_client_cp1_readiness_gate_blocked_allow_gate_required"
    if not present:
        return "receiver_only_client_cp1_readiness_gate_missing_health"
    if not mapping:
        return "receiver_only_client_cp1_readiness_gate_invalid_health"
    if kind != _HEALTH_KIND:
        return "receiver_only_client_cp1_readiness_gate_unrecognized_health"
    if not candidate:
        return "receiver_only_client_cp1_readiness_gate_blocked_health_not_ready"
    return "receiver_only_client_cp1_readiness_gate_ready_no_send"


def build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_contract() -> dict[str, Any]:
    return {
        "ok": True,
        "cp1_readiness_gate_version": WARROOM_V2_WS_RECEIVER_ONLY_CLIENT_CP1_READINESS_GATE_VERSION,
        "cp1_readiness_gate_kind": "warroom_v2_ws_receiver_only_client_cp1_readiness_gate_metadata_only_no_send",
        "input_pipeline": ["q35u_compact_hidden_health", "q35v_cp1_readiness_gate"],
        "requires_compact_hidden_health_packet": True,
        "requires_allow_cp1_readiness_gate_flag": True,
        "read_only": True,
        "metadata_only": True,
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
        "connect_fn_called_at_cp1_gate": False,
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


def build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet(
    compact_hidden_health_packet: Mapping[str, Any] | object | None = None,
    *,
    allow_cp1_readiness_gate: bool = False,
) -> dict[str, Any]:
    present = compact_hidden_health_packet is not None
    mapping = isinstance(compact_hidden_health_packet, Mapping)
    health = dict(compact_hidden_health_packet) if mapping else {}
    kind = str(health.get("packet_kind") or "")
    health_status = str(health.get("receiver_health_status") or "")
    safety_ok = (
        bool(health.get("compact_hidden_health_ready"))
        and bool(health.get("cp1_health_summary_ready"))
        and bool(health.get("receiver_safe_to_remain_idle"))
        and bool(health.get("send_disabled"))
        and not bool(health.get("client_sends_messages"))
        and not bool(health.get("external_message_send_enabled"))
        and health_status in _READY_HEALTH_STATUSES
    )
    status = _status(allow_gate=allow_cp1_readiness_gate, present=present, mapping=mapping, kind=kind, candidate=safety_ok)
    ready = status == "receiver_only_client_cp1_readiness_gate_ready_no_send"
    blockers = [] if ready else ["compact_hidden_health_not_ready_or_not_allowed"]
    return {
        **build_warroom_v2_ws_receiver_only_client_cp1_readiness_gate_contract(),
        "packet_kind": "warroom_v2_ws_receiver_only_client_cp1_readiness_gate_packet",
        "compact_hidden_health_present": present,
        "compact_hidden_health_is_mapping": mapping,
        "compact_hidden_health_kind_recognized": (kind == _HEALTH_KIND) if mapping else False,
        "cp1_readiness_gate_status": status,
        "cp1_readiness_gate_ready": ready,
        "cp1_done_candidate": ready,
        "cp1_blockers": blockers,
        "receiver_health_status": health_status if mapping else "",
        "registry_surface_ready": bool(health.get("registry_surface_ready")) if mapping else False,
        "connect_fn_source_ready": bool(health.get("connect_fn_source_ready")) if mapping else False,
        "socket_opened": bool(health.get("socket_opened")) if mapping else False,
        "receiver_safe_to_remain_idle": bool(health.get("receiver_safe_to_remain_idle")) if mapping else False,
        "cp1_checkpoint_label": "safe_receiver_preparation_state_ready" if ready else "safe_receiver_preparation_state_blocked",
        "next_checkpoint": "cp2_fake_receive_loop_after_cp1_completion" if ready else "cp1_health_summary",
        "read_only": True,
        "metadata_only": True,
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
        "connect_fn_called_at_cp1_gate": False,
        "target_session_state_mutated": False,
        "state_mutated": False,
        "global_registry_mutated": False,
        "client_sends_messages": False,
        "external_message_send_enabled": False,
        "send_disabled": True,
        "order_intent_submitted": False,
        "would_send_to_broker": False,
    }
