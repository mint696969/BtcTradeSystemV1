# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_session_seed_gate.py
# desc: PS-Q10P guarded live-session seed gate for already-built actual Q9F review packets. Passive by default and unmounted; can delegate to PS-Q10N only when operator/local-only gates are explicit. No Streamlit import, UI controls, file reads, payload decode, runtime writes, approval, ledger, AutoTrade, or broker behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Tuple

from .prediction_warroom_actual_review_packet_local_observation_seed_hook import (
    ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
    ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION,
    build_prediction_warroom_actual_review_packet_local_observation_seed_hook,
)
from .prediction_warroom_actual_review_packet_session_state_handoff_harness import DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import (
    LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
    resolve_prediction_warroom_lowered_display_packet_visibility_review_source,
)

ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION = "prediction_warroom_actual_review_packet_live_session_seed_gate.ps_q10p.v1"
ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE = "local_only_actual_review_packet_seed"

ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_SEQUENCE = (
    "default_passive_no_seed_no_mutation",
    "read_existing_session_state_review_source_via_ps_q9h",
    "require_operator_acknowledgement",
    "require_local_only_observation_enabled",
    "require_explicit_live_session_seed_allowed",
    "require_allowed_gate_mode",
    "require_supplied_already_built_actual_q9f_review_packet_mapping",
    "delegate_to_ps_q10n_seed_hook_only_after_gates_pass",
    "verify_seeded_packet_with_ps_q9h",
    "return_gate_packet_only",
    "do_not_mount_warroom_page_in_this_slice",
    "do_not_add_ui_controls",
    "do_not_run_actual_read_loader_from_ui",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReviewPacketLiveSessionSeedGatePacket:
    gate_version: str
    gate_id: str
    gate_state: str
    target_session_key: str = DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
    gate_mode: str | None = None
    gate_sequence: Tuple[str, ...] = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_SEQUENCE
    source_handoff: Mapping[str, Any] = field(default_factory=dict)
    seed_hook_packet: Mapping[str, Any] = field(default_factory=dict)
    operator_acknowledged: bool = False
    local_only_observation_enabled: bool = False
    live_session_seed_allowed: bool = False
    supplied_review_packet_present: bool = False
    seed_attempted: bool = False
    seed_hook_delegated: bool = False
    session_state_mapping_supplied: bool = False
    session_state_updated: bool = False
    source_handoff_ready: bool = False
    fallback_used: bool = True
    ready_for_existing_q9g_panel_render: bool = False
    ready_for_live_warroom_mount: bool = False
    mounted_in_warroom_page_this_slice: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    gate_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    live_session_seed_gate_only: bool = True
    local_only: bool = True
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
            "gate_version": self.gate_version,
            "gate_id": self.gate_id,
            "gate_state": self.gate_state,
            "target_session_key": self.target_session_key,
            "gate_mode": self.gate_mode,
            "gate_sequence": list(self.gate_sequence),
            "source_handoff": dict(self.source_handoff),
            "seed_hook_packet": dict(self.seed_hook_packet),
            "operator_acknowledged": self.operator_acknowledged,
            "local_only_observation_enabled": self.local_only_observation_enabled,
            "live_session_seed_allowed": self.live_session_seed_allowed,
            "supplied_review_packet_present": self.supplied_review_packet_present,
            "seed_attempted": self.seed_attempted,
            "seed_hook_delegated": self.seed_hook_delegated,
            "session_state_mapping_supplied": self.session_state_mapping_supplied,
            "session_state_updated": self.session_state_updated,
            "source_handoff_ready": self.source_handoff_ready,
            "fallback_used": self.fallback_used,
            "ready_for_existing_q9g_panel_render": self.ready_for_existing_q9g_panel_render,
            "ready_for_live_warroom_mount": self.ready_for_live_warroom_mount,
            "mounted_in_warroom_page_this_slice": self.mounted_in_warroom_page_this_slice,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "gate_summary": dict(self.gate_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "live_session_seed_gate_only": self.live_session_seed_gate_only,
            "local_only": self.local_only,
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


def build_prediction_warroom_actual_review_packet_live_session_seed_gate(
    *,
    review_packet: Mapping[str, Any] | Any | None = None,
    session_state: MutableMapping[str, Any] | None = None,
    operator_acknowledged: bool = False,
    local_only_observation_enabled: bool = False,
    allow_live_session_seed: bool = False,
    gate_mode: str | None = None,
    target_session_key: str = DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
) -> PredictionWarRoomActualReviewPacketLiveSessionSeedGatePacket:
    """Gate a future live-session seed operation; delegates to PS-Q10N only after all local-only gates pass."""
    review = _as_mapping(review_packet)
    blockers: list[str] = []
    warnings: list[str] = []
    seed_hook_packet: Mapping[str, Any] = {}
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not local_only_observation_enabled:
        blockers.append("local_only_observation_not_enabled")
    if not allow_live_session_seed:
        blockers.append("live_session_seed_not_allowed")
    if gate_mode != ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_MODE:
        blockers.append("gate_mode_not_allowed")
    if session_state is None:
        blockers.append("session_state_mapping_not_supplied")
    if not review:
        blockers.append("supplied_actual_q9f_review_packet_required")
    seed_allowed = not blockers
    if seed_allowed and session_state is not None:
        seed_hook_packet = build_prediction_warroom_actual_review_packet_local_observation_seed_hook(
            review_packet=review,
            session_state=session_state,
            enable_actual_review_packet_seed=True,
            local_observation_mode=ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_ALLOWED_MODE,
            target_session_key=target_session_key,
        ).to_dict()
        if seed_hook_packet.get("hook_state") != "actual_review_packet_local_observation_seed_hook_actual_packet_installed":
            blockers.extend(str(item) for item in seed_hook_packet.get("blocked_reasons") or ())
            warnings.extend(str(item) for item in seed_hook_packet.get("warning_reasons") or ())
    else:
        warnings.append("live_session_seed_gate_passive_no_seed_attempted")
    source_handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        session_state=session_state,
    ).to_dict()
    source_ready = bool(source_handoff.get("review_packet_ready")) and source_handoff.get("fallback_used") is False
    fallback_used = source_handoff.get("fallback_used") is not False
    session_updated = bool(seed_hook_packet.get("session_state_updated"))
    delegated = bool(seed_hook_packet)
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    if unique_blockers:
        state = "actual_review_packet_live_session_seed_gate_blocked"
    elif session_updated and source_ready:
        state = "actual_review_packet_live_session_seed_gate_seeded_for_existing_q9g_panel"
    elif source_ready:
        state = "actual_review_packet_live_session_seed_gate_existing_packet_ready"
    else:
        state = "actual_review_packet_live_session_seed_gate_passive_waiting_for_packet"
    return PredictionWarRoomActualReviewPacketLiveSessionSeedGatePacket(
        gate_version=ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION,
        gate_id=f"{ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION}:latest:{state}",
        gate_state=state,
        target_session_key=target_session_key,
        gate_mode=gate_mode,
        source_handoff=source_handoff,
        seed_hook_packet=seed_hook_packet,
        operator_acknowledged=operator_acknowledged,
        local_only_observation_enabled=local_only_observation_enabled,
        live_session_seed_allowed=allow_live_session_seed,
        supplied_review_packet_present=bool(review),
        seed_attempted=seed_allowed,
        seed_hook_delegated=delegated,
        session_state_mapping_supplied=session_state is not None,
        session_state_updated=session_updated,
        source_handoff_ready=source_ready,
        fallback_used=fallback_used,
        ready_for_existing_q9g_panel_render=source_ready,
        ready_for_live_warroom_mount=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        gate_summary={
            "gate_boundary": "ps_q10p_local_only_live_session_seed_gate_unmounted",
            "q10n_seed_hook_version": ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION,
            "q9h_source_handoff_version": LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
            "target_session_key": target_session_key,
            "seed_attempted": seed_allowed,
            "seed_hook_delegated": delegated,
            "session_state_updated": session_updated,
            "source_handoff_ready": source_ready,
            "fallback_used": fallback_used,
            "ready_for_existing_q9g_panel_render": source_ready,
            "ready_for_live_warroom_mount": False,
            "mounted_in_warroom_page_this_slice": False,
            "ui_controls_added": False,
            "ui_triggered_loader_execution": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
