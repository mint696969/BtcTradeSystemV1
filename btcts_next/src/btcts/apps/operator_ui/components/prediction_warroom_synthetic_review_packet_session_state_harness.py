# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_synthetic_review_packet_session_state_harness.py
# desc: PS-Q9I controlled synthetic review-packet producer and in-memory session-state harness for local WarRoom observation. Builds a synthetic Q9E/Q9F review packet and can place it into a provided mutable mapping; no file reads, payload decode, UI controls, runtime writes, Streamlit import, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Tuple

from .prediction_warroom_actual_display_packet_lowering_adapter import build_prediction_warroom_actual_display_packet_lowering_result
from .prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract
from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import (
    SESSION_REVIEW_PACKET_KEYS,
    resolve_prediction_warroom_lowered_display_packet_visibility_review_source,
)
from .prediction_warroom_sample_packets import SAMPLE_PACKET_VERSION, build_prediction_warroom_sample_display_packet

SYNTHETIC_REVIEW_PACKET_SESSION_STATE_HARNESS_VERSION = "prediction_warroom_synthetic_review_packet_session_state_harness.ps_q9i.v1"
DEFAULT_SESSION_REVIEW_PACKET_KEY = SESSION_REVIEW_PACKET_KEYS[0]

HARNESS_SEQUENCE = (
    "build_synthetic_display_packet_fixture_in_memory",
    "lower_fixture_with_ps_q9e_adapter_in_memory",
    "build_ps_q9f_visibility_review_packet_in_memory",
    "optionally_store_review_packet_in_provided_mapping",
    "verify_with_ps_q9h_source_handoff",
    "return_harness_packet_only",
    "do_not_run_loader_from_ui",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomSyntheticReviewPacketSessionStateHarnessPacket:
    harness_version: str
    harness_id: str
    harness_state: str
    target_session_key: str
    synthetic_source_version: str = SAMPLE_PACKET_VERSION
    review_packet: Mapping[str, Any] = field(default_factory=dict)
    lowering_result: Mapping[str, Any] = field(default_factory=dict)
    source_handoff: Mapping[str, Any] = field(default_factory=dict)
    candidate_keys: Tuple[str, ...] = SESSION_REVIEW_PACKET_KEYS
    harness_sequence: Tuple[str, ...] = HARNESS_SEQUENCE
    review_packet_built: bool = False
    review_packet_ready: bool = False
    session_state_updated: bool = False
    source_handoff_ready: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    synthetic_only: bool = True
    fixture_only: bool = True
    session_state_harness_only: bool = True
    in_memory_input_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    streamlit_import_required: bool = False
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
            "harness_version": self.harness_version,
            "harness_id": self.harness_id,
            "harness_state": self.harness_state,
            "target_session_key": self.target_session_key,
            "synthetic_source_version": self.synthetic_source_version,
            "review_packet": dict(self.review_packet),
            "lowering_result": dict(self.lowering_result),
            "source_handoff": dict(self.source_handoff),
            "candidate_keys": list(self.candidate_keys),
            "harness_sequence": list(self.harness_sequence),
            "review_packet_built": self.review_packet_built,
            "review_packet_ready": self.review_packet_ready,
            "session_state_updated": self.session_state_updated,
            "source_handoff_ready": self.source_handoff_ready,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "synthetic_only": self.synthetic_only,
            "fixture_only": self.fixture_only,
            "session_state_harness_only": self.session_state_harness_only,
            "in_memory_input_only": self.in_memory_input_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "streamlit_import_required": self.streamlit_import_required,
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


def build_prediction_warroom_synthetic_lowered_display_packet_review_packet() -> Mapping[str, Any]:
    """Build a synthetic ready PS-Q9F review packet in memory only."""
    display_packet = build_prediction_warroom_sample_display_packet()
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=display_packet,
    ).to_dict()
    return build_prediction_warroom_lowered_display_packet_visibility_review_contract(
        lowering_result=lowering,
    ).to_dict()


def build_prediction_warroom_synthetic_review_packet_session_state_harness(
    *,
    session_state: MutableMapping[str, Any] | None = None,
    target_session_key: str = DEFAULT_SESSION_REVIEW_PACKET_KEY,
    store_in_session_state: bool = False,
) -> PredictionWarRoomSyntheticReviewPacketSessionStateHarnessPacket:
    """Build and optionally place a synthetic PS-Q9F review packet into a provided in-memory mapping."""
    blocked: list[str] = []
    warnings: list[str] = []
    if target_session_key not in SESSION_REVIEW_PACKET_KEYS:
        blocked.append("target_session_key_not_allowed")
    display_packet = build_prediction_warroom_sample_display_packet()
    lowering = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=display_packet,
    ).to_dict()
    review_packet = build_prediction_warroom_lowered_display_packet_visibility_review_contract(
        lowering_result=lowering,
    ).to_dict()
    review_ready = bool(review_packet.get("ready_for_ps_q9g_guarded_ui_mount"))
    if not review_ready:
        blocked.append("synthetic_review_packet_not_ready")
    updated = False
    if store_in_session_state:
        if session_state is None:
            blocked.append("session_state_mapping_not_supplied")
        elif not blocked:
            session_state[target_session_key] = review_packet
            updated = True
    elif session_state is not None:
        warnings.append("session_state_mapping_supplied_but_store_disabled")
    source_handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        explicit_review_packet=None,
        session_state=session_state if session_state is not None else ({target_session_key: review_packet} if not blocked else {}),
    ).to_dict()
    source_ready = bool(source_handoff.get("review_packet_ready"))
    if updated and not source_ready:
        blocked.append("source_handoff_did_not_resolve_updated_review_packet")
    unique_blocked = tuple(dict.fromkeys(item for item in blocked if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    state = "synthetic_review_packet_session_state_ready" if not unique_blocked and review_ready and source_ready else "synthetic_review_packet_session_state_blocked"
    return PredictionWarRoomSyntheticReviewPacketSessionStateHarnessPacket(
        harness_version=SYNTHETIC_REVIEW_PACKET_SESSION_STATE_HARNESS_VERSION,
        harness_id=f"{SYNTHETIC_REVIEW_PACKET_SESSION_STATE_HARNESS_VERSION}:latest:{state}",
        harness_state=state,
        target_session_key=target_session_key,
        review_packet=review_packet,
        lowering_result=lowering,
        source_handoff=source_handoff,
        review_packet_built=True,
        review_packet_ready=review_ready,
        session_state_updated=updated,
        source_handoff_ready=source_ready,
        blocker_count=len(unique_blocked),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blocked,
        warning_reasons=unique_warnings,
        handoff_summary={
            "harness_boundary": "ps_q9i_synthetic_review_packet_session_state_harness_only",
            "target_session_key": target_session_key,
            "synthetic_source_version": SAMPLE_PACKET_VERSION,
            "review_packet_ready": review_ready,
            "session_state_updated": updated,
            "source_handoff_ready": source_ready,
            "ui_triggered_loader_execution": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
