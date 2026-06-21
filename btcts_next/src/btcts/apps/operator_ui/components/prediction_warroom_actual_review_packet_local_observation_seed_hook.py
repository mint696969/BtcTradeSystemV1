# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_local_observation_seed_hook.py
# desc: PS-Q10N guarded local/session seed hook for supplied actual Q9F review packets. Passive by default; only an explicit caller can ask it to place an already-built actual review packet into a provided in-memory mapping. No UI controls, file reads, payload decode, runtime writes, Streamlit import, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Tuple

from .prediction_warroom_actual_review_packet_session_state_handoff_harness import (
    ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION,
    DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
    build_prediction_warroom_actual_review_packet_session_state_handoff_harness,
)
from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import (
    LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
    SESSION_REVIEW_PACKET_KEYS,
    resolve_prediction_warroom_lowered_display_packet_visibility_review_source,
)

ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION = "prediction_warroom_actual_review_packet_local_observation_seed_hook.ps_q10n.v1"
ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ENABLE_KEY = "warroom_prediction_actual_review_packet_local_observation_enabled"
ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_MODE_KEY = "warroom_prediction_actual_review_packet_local_observation_mode"
ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE = "actual_review_packet_only"

ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_SEQUENCE = (
    "default_passive_no_mutation",
    "read_existing_in_memory_review_packet_via_ps_q9h",
    "require_explicit_enable_for_actual_seed",
    "require_allowed_actual_local_observation_mode",
    "require_supplied_already_built_actual_q9f_review_packet_mapping",
    "call_ps_q10k_harness_only_when_enabled",
    "store_only_under_ps_q9h_allowed_candidate_key",
    "verify_with_ps_q9h_source_handoff",
    "return_seed_hook_packet_only",
    "do_not_add_ui_controls",
    "do_not_run_loader_from_ui",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReviewPacketLocalObservationSeedHookPacket:
    hook_version: str
    hook_id: str
    hook_state: str
    mode: str | None
    target_session_key: str
    source_handoff: Mapping[str, Any] = field(default_factory=dict)
    handoff_harness_packet: Mapping[str, Any] = field(default_factory=dict)
    candidate_keys: Tuple[str, ...] = SESSION_REVIEW_PACKET_KEYS
    seed_sequence: Tuple[str, ...] = ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_SEQUENCE
    actual_seed_requested: bool = False
    actual_seed_enabled: bool = False
    actual_review_packet_present: bool = False
    actual_review_packet_ready: bool = False
    synthetic_review_packet_detected: bool = False
    fixture_review_packet_detected: bool = False
    session_state_mapping_supplied: bool = False
    session_state_updated: bool = False
    source_handoff_ready: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    actual_review_packet_seed_hook_only: bool = True
    actual_review_packet_only: bool = True
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
            "handoff_harness_packet": dict(self.handoff_harness_packet),
            "candidate_keys": list(self.candidate_keys),
            "seed_sequence": list(self.seed_sequence),
            "actual_seed_requested": self.actual_seed_requested,
            "actual_seed_enabled": self.actual_seed_enabled,
            "actual_review_packet_present": self.actual_review_packet_present,
            "actual_review_packet_ready": self.actual_review_packet_ready,
            "synthetic_review_packet_detected": self.synthetic_review_packet_detected,
            "fixture_review_packet_detected": self.fixture_review_packet_detected,
            "session_state_mapping_supplied": self.session_state_mapping_supplied,
            "session_state_updated": self.session_state_updated,
            "source_handoff_ready": self.source_handoff_ready,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "actual_review_packet_seed_hook_only": self.actual_review_packet_seed_hook_only,
            "actual_review_packet_only": self.actual_review_packet_only,
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
    raw = state.get(ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_MODE_KEY)
    return str(raw) if raw else None


def _enabled_from_state(session_state: Mapping[str, Any] | Any | None, explicit_enable: bool) -> bool:
    if explicit_enable:
        return True
    state = _as_mapping(session_state)
    return state.get(ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ENABLE_KEY) is True


def build_prediction_warroom_actual_review_packet_local_observation_seed_hook(
    *,
    review_packet: Mapping[str, Any] | Any | None = None,
    session_state: MutableMapping[str, Any] | None = None,
    enable_actual_review_packet_seed: bool = False,
    local_observation_mode: str | None = None,
    target_session_key: str = DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
) -> PredictionWarRoomActualReviewPacketLocalObservationSeedHookPacket:
    """Optionally seed a supplied actual Q9F review packet into an in-memory mapping for local/live observation."""
    review = _as_mapping(review_packet)
    mode = _mode_from_state(session_state, local_observation_mode)
    seed_requested = _enabled_from_state(session_state, enable_actual_review_packet_seed)
    blocked: list[str] = []
    warnings: list[str] = []
    handoff_packet: Mapping[str, Any] = {}
    session_mapping_supplied = session_state is not None
    if target_session_key not in SESSION_REVIEW_PACKET_KEYS:
        blocked.append("target_session_key_not_allowed")
    if seed_requested and mode != ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE:
        blocked.append("actual_local_observation_mode_not_allowed")
    if seed_requested and session_state is None:
        blocked.append("session_state_mapping_not_supplied")
    if seed_requested and not review:
        blocked.append("actual_review_packet_mapping_required")
    enabled = seed_requested and not blocked
    if enabled and session_state is not None:
        handoff_packet = build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
            review_packet=review,
            session_state=session_state,
            target_session_key=target_session_key,
            store_in_session_state=True,
        ).to_dict()
        if handoff_packet.get("harness_state") != "actual_review_packet_session_state_handoff_ready":
            blocked.extend(str(item) for item in handoff_packet.get("blocked_reasons") or [])
            warnings.extend(str(item) for item in handoff_packet.get("warning_reasons") or [])
    elif not seed_requested:
        warnings.append("actual_review_packet_seed_hook_passive_no_seed_requested")
    source_handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        session_state=session_state,
    ).to_dict()
    source_ready = bool(source_handoff.get("review_packet_ready")) and source_handoff.get("fallback_used") is False
    session_updated = bool(handoff_packet.get("session_state_updated"))
    review_ready = bool(handoff_packet.get("review_packet_ready")) or source_ready
    synthetic = bool(handoff_packet.get("synthetic_review_packet_detected"))
    fixture = bool(handoff_packet.get("fixture_review_packet_detected"))
    unique_blocked = tuple(dict.fromkeys(item for item in blocked if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    if unique_blocked:
        state = "actual_review_packet_local_observation_seed_hook_blocked"
    elif enabled and session_updated and source_ready:
        state = "actual_review_packet_local_observation_seed_hook_actual_packet_installed"
    elif source_ready:
        state = "actual_review_packet_local_observation_seed_hook_existing_review_packet_ready"
    else:
        state = "actual_review_packet_local_observation_seed_hook_passive_waiting_for_review_packet"
    return PredictionWarRoomActualReviewPacketLocalObservationSeedHookPacket(
        hook_version=ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION,
        hook_id=f"{ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION}:latest:{state}",
        hook_state=state,
        mode=mode,
        target_session_key=target_session_key,
        source_handoff=source_handoff,
        handoff_harness_packet=handoff_packet,
        actual_seed_requested=seed_requested,
        actual_seed_enabled=enabled,
        actual_review_packet_present=bool(review),
        actual_review_packet_ready=review_ready,
        synthetic_review_packet_detected=synthetic,
        fixture_review_packet_detected=fixture,
        session_state_mapping_supplied=session_mapping_supplied,
        session_state_updated=session_updated,
        source_handoff_ready=source_ready,
        blocker_count=len(unique_blocked),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blocked,
        warning_reasons=unique_warnings,
        handoff_summary={
            "hook_boundary": "ps_q10n_guarded_actual_review_packet_local_observation_seed_hook_only",
            "q10k_handoff_harness_version": ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION,
            "q9h_source_handoff_version": LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
            "target_session_key": target_session_key,
            "actual_seed_requested": seed_requested,
            "actual_seed_enabled": enabled,
            "session_state_updated": session_updated,
            "source_handoff_ready": source_ready,
            "synthetic_review_packet_detected": synthetic,
            "fixture_review_packet_detected": fixture,
            "ui_controls_added": False,
            "ui_triggered_loader_execution": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled": False,
            "runtime_artifact_write_enabled": False,
            "warroom_page_mutation_enabled": False,
            "warroom_panel_mutation_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
