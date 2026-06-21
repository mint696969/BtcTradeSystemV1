# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_local_observation_hook.py
# desc: PS-Q9J guarded local WarRoom observation hook for synthetic lowered display-packet review packets. Passive by default; only an explicit caller can ask it to place a synthetic review packet into a provided in-memory mapping. No UI controls, file reads, payload decode, runtime writes, Streamlit import, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Tuple

from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import (
    SESSION_REVIEW_PACKET_KEYS,
    resolve_prediction_warroom_lowered_display_packet_visibility_review_source,
)
from .prediction_warroom_synthetic_review_packet_session_state_harness import (
    DEFAULT_SESSION_REVIEW_PACKET_KEY,
    SYNTHETIC_REVIEW_PACKET_SESSION_STATE_HARNESS_VERSION,
    build_prediction_warroom_synthetic_review_packet_session_state_harness,
)

LOCAL_OBSERVATION_HOOK_VERSION = "prediction_warroom_local_observation_hook.ps_q9j.v1"
LOCAL_OBSERVATION_ENABLE_KEY = "warroom_prediction_local_synthetic_review_enabled"
LOCAL_OBSERVATION_MODE_KEY = "warroom_prediction_local_observation_mode"
LOCAL_OBSERVATION_ALLOWED_MODE = "synthetic_review_packet_only"

LOCAL_OBSERVATION_SEQUENCE = (
    "default_passive_no_mutation",
    "read_existing_in_memory_review_packet_via_ps_q9h",
    "require_explicit_enable_for_synthetic_injection",
    "require_allowed_local_observation_mode",
    "call_ps_q9i_harness_only_when_enabled",
    "store_only_under_ps_q9h_allowed_candidate_key",
    "verify_with_ps_q9h_source_handoff",
    "return_hook_packet_only",
    "do_not_add_ui_controls",
    "do_not_run_loader_from_ui",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLocalObservationHookPacket:
    hook_version: str
    hook_id: str
    hook_state: str
    mode: str | None
    target_session_key: str
    source_handoff: Mapping[str, Any] = field(default_factory=dict)
    harness_packet: Mapping[str, Any] = field(default_factory=dict)
    candidate_keys: Tuple[str, ...] = SESSION_REVIEW_PACKET_KEYS
    local_observation_sequence: Tuple[str, ...] = LOCAL_OBSERVATION_SEQUENCE
    synthetic_injection_requested: bool = False
    synthetic_injection_enabled: bool = False
    session_state_mapping_supplied: bool = False
    session_state_updated: bool = False
    review_packet_ready: bool = False
    source_handoff_ready: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    local_observation_hook_only: bool = True
    synthetic_only: bool = True
    in_memory_input_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
    would_load_source_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_decode_payload: bool = False
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hook_version": self.hook_version,
            "hook_id": self.hook_id,
            "hook_state": self.hook_state,
            "mode": self.mode,
            "target_session_key": self.target_session_key,
            "source_handoff": dict(self.source_handoff),
            "harness_packet": dict(self.harness_packet),
            "candidate_keys": list(self.candidate_keys),
            "local_observation_sequence": list(self.local_observation_sequence),
            "synthetic_injection_requested": self.synthetic_injection_requested,
            "synthetic_injection_enabled": self.synthetic_injection_enabled,
            "session_state_mapping_supplied": self.session_state_mapping_supplied,
            "session_state_updated": self.session_state_updated,
            "review_packet_ready": self.review_packet_ready,
            "source_handoff_ready": self.source_handoff_ready,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "local_observation_hook_only": self.local_observation_hook_only,
            "synthetic_only": self.synthetic_only,
            "in_memory_input_only": self.in_memory_input_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
            "would_load_source_artifacts": self.would_load_source_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_decode_payload": self.would_decode_payload,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _mode_from_state(session_state: Mapping[str, Any] | Any | None, explicit_mode: str | None) -> str | None:
    if explicit_mode:
        return explicit_mode
    state = _as_mapping(session_state)
    raw = state.get(LOCAL_OBSERVATION_MODE_KEY)
    return str(raw) if raw else None


def _enabled_from_state(session_state: Mapping[str, Any] | Any | None, explicit_enable: bool) -> bool:
    if explicit_enable:
        return True
    state = _as_mapping(session_state)
    return state.get(LOCAL_OBSERVATION_ENABLE_KEY) is True


def build_prediction_warroom_local_observation_hook(
    *,
    session_state: MutableMapping[str, Any] | None = None,
    enable_synthetic_review_packet: bool = False,
    local_observation_mode: str | None = None,
    target_session_key: str = DEFAULT_SESSION_REVIEW_PACKET_KEY,
) -> PredictionWarRoomLocalObservationHookPacket:
    """Optionally inject a synthetic ready review packet into an in-memory mapping for local observation only."""
    mode = _mode_from_state(session_state, local_observation_mode)
    injection_requested = _enabled_from_state(session_state, enable_synthetic_review_packet)
    blocked: list[str] = []
    warnings: list[str] = []
    harness_packet: Mapping[str, Any] = {}
    session_mapping_supplied = session_state is not None
    if target_session_key not in SESSION_REVIEW_PACKET_KEYS:
        blocked.append("target_session_key_not_allowed")
    if injection_requested and mode != LOCAL_OBSERVATION_ALLOWED_MODE:
        blocked.append("local_observation_mode_not_allowed")
    if injection_requested and session_state is None:
        blocked.append("session_state_mapping_not_supplied")
    enabled = injection_requested and not blocked
    if enabled and session_state is not None:
        harness_packet = build_prediction_warroom_synthetic_review_packet_session_state_harness(
            session_state=session_state,
            target_session_key=target_session_key,
            store_in_session_state=True,
        ).to_dict()
        if harness_packet.get("harness_state") != "synthetic_review_packet_session_state_ready":
            blocked.extend(str(item) for item in harness_packet.get("blocked_reasons") or [])
            warnings.extend(str(item) for item in harness_packet.get("warning_reasons") or [])
    elif not injection_requested:
        warnings.append("local_observation_hook_passive_no_synthetic_injection_requested")
    source_handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        session_state=session_state,
    ).to_dict()
    source_ready = bool(source_handoff.get("review_packet_ready"))
    session_updated = bool(harness_packet.get("session_state_updated"))
    review_ready = bool(harness_packet.get("review_packet_ready")) or source_ready
    unique_blocked = tuple(dict.fromkeys(item for item in blocked if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    if unique_blocked:
        state = "local_observation_hook_blocked"
    elif enabled and session_updated and source_ready:
        state = "local_observation_hook_synthetic_ready_packet_installed"
    elif source_ready:
        state = "local_observation_hook_existing_review_packet_ready"
    else:
        state = "local_observation_hook_passive_waiting_for_review_packet"
    return PredictionWarRoomLocalObservationHookPacket(
        hook_version=LOCAL_OBSERVATION_HOOK_VERSION,
        hook_id=f"{LOCAL_OBSERVATION_HOOK_VERSION}:latest:{state}",
        hook_state=state,
        mode=mode,
        target_session_key=target_session_key,
        source_handoff=source_handoff,
        harness_packet=harness_packet,
        synthetic_injection_requested=injection_requested,
        synthetic_injection_enabled=enabled,
        session_state_mapping_supplied=session_mapping_supplied,
        session_state_updated=session_updated,
        review_packet_ready=review_ready,
        source_handoff_ready=source_ready,
        blocker_count=len(unique_blocked),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blocked,
        warning_reasons=unique_warnings,
        handoff_summary={
            "hook_boundary": "ps_q9j_guarded_local_observation_hook_only",
            "source_handoff_version": "prediction_warroom_lowered_display_packet_review_source_handoff.ps_q9h.v1",
            "synthetic_harness_version": SYNTHETIC_REVIEW_PACKET_SESSION_STATE_HARNESS_VERSION,
            "target_session_key": target_session_key,
            "synthetic_injection_requested": injection_requested,
            "synthetic_injection_enabled": enabled,
            "session_state_updated": session_updated,
            "source_handoff_ready": source_ready,
            "ui_controls_added": False,
            "ui_triggered_loader_execution": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled": False,
            "runtime_artifact_write_enabled": False,
            "warroom_page_mutation_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
