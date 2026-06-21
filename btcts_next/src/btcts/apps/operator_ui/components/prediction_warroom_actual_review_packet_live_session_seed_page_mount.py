# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_session_seed_page_mount.py
# desc: PS-Q10R page-mount adapter for the local-only actual review-packet live-session seed gate. Reads only already-supplied in-memory session_state values and delegates to PS-Q10P. No Streamlit import, UI controls, file reads, payload decode, runtime writes, approval, ledger, AutoTrade, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping, MutableMapping

from .prediction_warroom_actual_review_packet_live_session_seed_gate import (
    ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE,
    build_prediction_warroom_actual_review_packet_live_session_seed_gate,
)

ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION = "prediction_warroom_actual_review_packet_live_session_seed_page_mount.ps_q10r.v1"
ACTUAL_REVIEW_PACKET_LIVE_SESSION_SUPPLIED_REVIEW_PACKET_KEY = "warroom_prediction_actual_review_packet_live_session_supplied_review_packet"
ACTUAL_REVIEW_PACKET_LIVE_SESSION_OPERATOR_ACK_KEY = "warroom_prediction_actual_review_packet_live_session_operator_acknowledged"
ACTUAL_REVIEW_PACKET_LIVE_SESSION_LOCAL_ONLY_KEY = "warroom_prediction_actual_review_packet_live_session_local_only_observation_enabled"
ACTUAL_REVIEW_PACKET_LIVE_SESSION_ALLOW_SEED_KEY = "warroom_prediction_actual_review_packet_live_session_allow_seed"
ACTUAL_REVIEW_PACKET_LIVE_SESSION_GATE_MODE_KEY = "warroom_prediction_actual_review_packet_live_session_gate_mode"

ACTUAL_REVIEW_PACKET_LIVE_SESSION_PAGE_MOUNT_SEQUENCE = (
    "mounted_inside_prediction_warroom_real_payload_review_section",
    "called_before_existing_q9g_panel_render_only",
    "read_only_pre_supplied_in_memory_session_state_packet",
    "read_only_pre_supplied_operator_ack_flag",
    "read_only_pre_supplied_local_only_flag",
    "read_only_pre_supplied_allow_seed_flag",
    "read_only_pre_supplied_gate_mode",
    "delegate_to_ps_q10p_live_session_seed_gate",
    "passive_by_default_without_packet_or_gates",
    "preserve_existing_q9g_fallback_without_packet_or_gates",
    "do_not_add_ui_controls",
    "do_not_call_q9b_q9q_q10h_from_warroom_ui",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade_or_broker",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _bool_from_state(state: Mapping[str, Any], key: str) -> bool:
    return state.get(key) is True


def apply_prediction_warroom_actual_review_packet_live_session_seed_page_mount(
    *,
    session_state: MutableMapping[str, Any] | None,
) -> Mapping[str, Any]:
    """Apply the PS-Q10P gate from already-supplied in-memory session_state values only."""
    state = _as_mapping(session_state)
    gate_mode_raw = state.get(ACTUAL_REVIEW_PACKET_LIVE_SESSION_GATE_MODE_KEY)
    gate_mode = str(gate_mode_raw) if gate_mode_raw else None
    packet = build_prediction_warroom_actual_review_packet_live_session_seed_gate(
        review_packet=state.get(ACTUAL_REVIEW_PACKET_LIVE_SESSION_SUPPLIED_REVIEW_PACKET_KEY),
        session_state=session_state,
        operator_acknowledged=_bool_from_state(state, ACTUAL_REVIEW_PACKET_LIVE_SESSION_OPERATOR_ACK_KEY),
        local_only_observation_enabled=_bool_from_state(state, ACTUAL_REVIEW_PACKET_LIVE_SESSION_LOCAL_ONLY_KEY),
        allow_live_session_seed=_bool_from_state(state, ACTUAL_REVIEW_PACKET_LIVE_SESSION_ALLOW_SEED_KEY),
        gate_mode=gate_mode,
    ).to_dict()
    return {
        "page_mount_version": ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION,
        "page_mount_state": "actual_review_packet_live_session_seed_page_mount_applied",
        "page_mount_sequence": list(ACTUAL_REVIEW_PACKET_LIVE_SESSION_PAGE_MOUNT_SEQUENCE),
        "supplied_review_packet_key": ACTUAL_REVIEW_PACKET_LIVE_SESSION_SUPPLIED_REVIEW_PACKET_KEY,
        "operator_ack_key": ACTUAL_REVIEW_PACKET_LIVE_SESSION_OPERATOR_ACK_KEY,
        "local_only_key": ACTUAL_REVIEW_PACKET_LIVE_SESSION_LOCAL_ONLY_KEY,
        "allow_seed_key": ACTUAL_REVIEW_PACKET_LIVE_SESSION_ALLOW_SEED_KEY,
        "gate_mode_key": ACTUAL_REVIEW_PACKET_LIVE_SESSION_GATE_MODE_KEY,
        "expected_gate_mode": ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE,
        "gate_packet": packet,
        "read_only": True,
        "non_executing": True,
        "in_memory_input_only": True,
        "streamlit_import_required": False,
        "ui_controls_added": False,
        "ui_triggered_loader_execution": False,
        "would_load_source_artifacts": False,
        "would_read_runtime_file": False,
        "would_decode_payload": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "authorization_grant_requested": False,
        "autotrade_trigger_enabled": False,
    }
