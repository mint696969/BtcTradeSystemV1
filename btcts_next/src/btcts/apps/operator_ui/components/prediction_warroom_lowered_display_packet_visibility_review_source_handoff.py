# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_source_handoff.py
# desc: PS-Q9H in-memory source handoff for lowered display-packet visibility review packets. Resolves explicit or session-state mappings only; no file reads, payload decode, loader execution, runtime writes, Streamlit import, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_lowered_display_packet_visibility_review_contract import (
    LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION,
    build_prediction_warroom_lowered_display_packet_visibility_review_contract,
)

LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION = "prediction_warroom_lowered_display_packet_review_source_handoff.ps_q9h.v1"

SESSION_REVIEW_PACKET_KEYS = (
    "warroom_prediction_lowered_display_packet_visibility_review_packet",
    "prediction_warroom_lowered_display_packet_visibility_review_packet",
    "warroom_prediction_ps_q9f_review_packet",
)

SOURCE_HANDOFF_SEQUENCE = (
    "prefer_explicit_in_memory_review_packet",
    "scan_session_state_candidate_keys_read_only",
    "validate_review_packet_contract_shape",
    "fallback_to_blocked_review_contract_when_missing_or_invalid",
    "return_source_handoff_packet_only",
    "do_not_run_loader_from_ui",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLoweredDisplayPacketReviewSourceHandoffPacket:
    handoff_version: str
    handoff_id: str
    handoff_state: str
    source_kind: str
    review_packet: Mapping[str, Any] = field(default_factory=dict)
    candidate_keys: Tuple[str, ...] = SESSION_REVIEW_PACKET_KEYS
    matched_key: str | None = None
    review_packet_present: bool = False
    review_packet_contract_version_valid: bool = False
    review_packet_ready: bool = False
    fallback_used: bool = False
    source_handoff_sequence: Tuple[str, ...] = SOURCE_HANDOFF_SEQUENCE
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    source_handoff_only: bool = True
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
            "handoff_version": self.handoff_version,
            "handoff_id": self.handoff_id,
            "handoff_state": self.handoff_state,
            "source_kind": self.source_kind,
            "review_packet": dict(self.review_packet),
            "candidate_keys": list(self.candidate_keys),
            "matched_key": self.matched_key,
            "review_packet_present": self.review_packet_present,
            "review_packet_contract_version_valid": self.review_packet_contract_version_valid,
            "review_packet_ready": self.review_packet_ready,
            "fallback_used": self.fallback_used,
            "source_handoff_sequence": list(self.source_handoff_sequence),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "source_handoff_only": self.source_handoff_only,
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


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _blocked_fallback_review_packet() -> Mapping[str, Any]:
    return build_prediction_warroom_lowered_display_packet_visibility_review_contract().to_dict()


def _packet_blockers(packet: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if not packet:
        blockers.append("review_packet_mapping_missing")
    if packet.get("contract_version") != LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION:
        blockers.append("review_packet_contract_version_invalid")
    if "contract_state" not in packet:
        blockers.append("review_packet_contract_state_missing")
    if "ready_for_ps_q9g_guarded_ui_mount" not in packet:
        blockers.append("review_packet_readiness_flag_missing")
    for unsafe_key in (
        "ui_mount_patch_included",
        "loader_execution_allowed_from_ui",
        "would_read_runtime_file",
        "would_decode_payload",
        "would_write_runtime_artifact",
        "would_send_to_broker",
        "broker_execution_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "authorization_grant_requested",
        "autotrade_trigger_enabled",
    ):
        if packet.get(unsafe_key) is True:
            blockers.append(f"review_packet_unsafe_true_flag:{unsafe_key}")
    return tuple(dict.fromkeys(blockers))


def _first_session_candidate(session_state: Mapping[str, Any] | Any | None) -> tuple[str | None, Mapping[str, Any]]:
    state = _as_mapping(session_state)
    for key in SESSION_REVIEW_PACKET_KEYS:
        packet = _as_mapping(state.get(key))
        if packet:
            return key, packet
    return None, {}


def resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
    *,
    explicit_review_packet: Mapping[str, Any] | Any | None = None,
    session_state: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomLoweredDisplayPacketReviewSourceHandoffPacket:
    """Resolve an in-memory PS-Q9F review packet without running loaders or reading runtime files."""
    explicit = _as_mapping(explicit_review_packet)
    matched_key: str | None = None
    source_kind = "missing"
    candidate = explicit
    if explicit:
        source_kind = "explicit_in_memory_argument"
    else:
        matched_key, candidate = _first_session_candidate(session_state)
        if candidate:
            source_kind = "session_state_in_memory_mapping"
    blockers = _packet_blockers(candidate)
    warnings: list[str] = []
    fallback_used = False
    if not candidate:
        warnings.append("review_packet_not_supplied_using_blocked_fallback")
        candidate = _blocked_fallback_review_packet()
        fallback_used = True
        source_kind = "blocked_fallback_contract"
        blockers = ()
    elif blockers:
        warnings.append("invalid_review_packet_using_blocked_fallback")
        candidate = _blocked_fallback_review_packet()
        fallback_used = True
    version_ok = candidate.get("contract_version") == LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION
    ready = bool(candidate.get("ready_for_ps_q9g_guarded_ui_mount"))
    state = "review_source_handoff_ready" if version_ok and not blockers and not fallback_used else "review_source_handoff_fallback_blocked"
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    return PredictionWarRoomLoweredDisplayPacketReviewSourceHandoffPacket(
        handoff_version=LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
        handoff_id=f"{LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION}:latest:{state}",
        handoff_state=state,
        source_kind=source_kind,
        review_packet=candidate,
        matched_key=matched_key,
        review_packet_present=bool(candidate),
        review_packet_contract_version_valid=version_ok,
        review_packet_ready=ready,
        fallback_used=fallback_used,
        blocker_count=len(blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=blockers,
        warning_reasons=unique_warnings,
        handoff_summary={
            "handoff_boundary": "ps_q9h_in_memory_review_packet_source_handoff_only",
            "source_kind": source_kind,
            "matched_key": matched_key,
            "candidate_keys": list(SESSION_REVIEW_PACKET_KEYS),
            "review_packet_contract_version_valid": version_ok,
            "review_packet_ready": ready,
            "fallback_used": fallback_used,
            "ui_triggered_loader_execution": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
