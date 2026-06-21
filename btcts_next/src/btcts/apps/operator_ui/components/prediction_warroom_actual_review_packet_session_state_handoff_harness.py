# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_session_state_handoff_harness.py
# desc: PS-Q10K supplied-actual Q9F review-packet session-state handoff harness. Accepts an already-built actual review packet mapping and can place it into a provided in-memory session-state mapping; no file reads, payload decode, loader execution, Streamlit import, WarRoom page mutation, runtime writes, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Tuple

from .prediction_warroom_lowered_display_packet_visibility_review_contract import LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION
from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import (
    SESSION_REVIEW_PACKET_KEYS,
    resolve_prediction_warroom_lowered_display_packet_visibility_review_source,
)

ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION = "prediction_warroom_actual_review_packet_session_state_handoff_harness.ps_q10k.v1"
DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY = SESSION_REVIEW_PACKET_KEYS[0]

ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_SEQUENCE = (
    "consume_supplied_actual_q9f_review_packet_mapping_only",
    "validate_review_packet_contract_shape_with_q9h",
    "reject_missing_invalid_or_not_ready_review_packet",
    "reject_synthetic_or_fixture_review_packet",
    "optionally_store_review_packet_in_provided_mapping",
    "verify_stored_packet_with_q9h_source_handoff",
    "return_handoff_harness_packet_only",
    "do_not_run_loader_from_ui",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReviewPacketSessionStateHandoffHarnessPacket:
    harness_version: str
    harness_id: str
    harness_state: str
    target_session_key: str
    review_packet: Mapping[str, Any] = field(default_factory=dict)
    source_handoff: Mapping[str, Any] = field(default_factory=dict)
    candidate_keys: Tuple[str, ...] = SESSION_REVIEW_PACKET_KEYS
    handoff_sequence: Tuple[str, ...] = ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_SEQUENCE
    review_packet_present: bool = False
    review_packet_contract_version_valid: bool = False
    review_packet_ready: bool = False
    synthetic_review_packet_detected: bool = False
    fixture_review_packet_detected: bool = False
    store_requested: bool = False
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
    actual_review_packet_handoff_only: bool = True
    session_state_handoff_only: bool = True
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
            "harness_version": self.harness_version,
            "harness_id": self.harness_id,
            "harness_state": self.harness_state,
            "target_session_key": self.target_session_key,
            "review_packet": dict(self.review_packet),
            "source_handoff": dict(self.source_handoff),
            "candidate_keys": list(self.candidate_keys),
            "handoff_sequence": list(self.handoff_sequence),
            "review_packet_present": self.review_packet_present,
            "review_packet_contract_version_valid": self.review_packet_contract_version_valid,
            "review_packet_ready": self.review_packet_ready,
            "synthetic_review_packet_detected": self.synthetic_review_packet_detected,
            "fixture_review_packet_detected": self.fixture_review_packet_detected,
            "store_requested": self.store_requested,
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
            "actual_review_packet_handoff_only": self.actual_review_packet_handoff_only,
            "session_state_handoff_only": self.session_state_handoff_only,
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


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _payload_markers(payload: Mapping[str, Any]) -> tuple[bool, bool]:
    primary = _as_mapping(payload.get("primary_signal_summary"))
    boundaries = _as_mapping(payload.get("boundaries"))
    run_id = str(payload.get("prediction_run_id") or "")
    synthetic = bool(
        payload.get("synthetic_only") is True
        or primary.get("synthetic_only") is True
        or boundaries.get("synthetic_only") is True
        or run_id.startswith("synthetic_")
    )
    fixture = bool(
        payload.get("fixture_only") is True
        or primary.get("fixture_only") is True
        or boundaries.get("fixture_only") is True
        or "fixture" in run_id
    )
    return synthetic, fixture


def _review_packet_markers(review_packet: Mapping[str, Any]) -> tuple[bool, bool]:
    synthetic = False
    fixture = False
    widget_index = _as_mapping(review_packet.get("widget_group_index"))
    for raw in _list(widget_index.get("widget_groups")):
        group = _as_mapping(raw)
        payload = _as_mapping(group.get("payload"))
        payload_synthetic, payload_fixture = _payload_markers(payload)
        synthetic = synthetic or payload_synthetic
        fixture = fixture or payload_fixture
    return synthetic, fixture


def build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
    *,
    review_packet: Mapping[str, Any] | Any | None = None,
    session_state: MutableMapping[str, Any] | None = None,
    target_session_key: str = DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
    store_in_session_state: bool = False,
) -> PredictionWarRoomActualReviewPacketSessionStateHandoffHarnessPacket:
    """Validate and optionally store a supplied actual PS-Q9F review packet in a provided mapping only."""
    review = _as_mapping(review_packet)
    blocked: list[str] = []
    warnings: list[str] = []
    if target_session_key not in SESSION_REVIEW_PACKET_KEYS:
        blocked.append("target_session_key_not_allowed")
    if not review:
        blocked.append("actual_review_packet_mapping_required")
    version_ok = review.get("contract_version") == LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION
    ready = bool(review.get("ready_for_ps_q9g_guarded_ui_mount")) and int(review.get("blocker_count") or 0) == 0
    if review and not version_ok:
        blocked.append("actual_review_packet_contract_version_invalid")
    if review and not ready:
        blocked.append("actual_review_packet_not_ready_for_q9g")
    synthetic, fixture = _review_packet_markers(review)
    if synthetic:
        blocked.append("actual_review_packet_required_but_synthetic_detected")
    if fixture:
        blocked.append("actual_review_packet_required_but_fixture_detected")
    if store_in_session_state and session_state is None:
        blocked.append("session_state_mapping_not_supplied")
    elif session_state is not None and not store_in_session_state:
        warnings.append("session_state_mapping_supplied_but_store_disabled")

    updated = False
    if store_in_session_state and session_state is not None and not blocked:
        session_state[target_session_key] = review
        updated = True

    if updated:
        source_handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
            session_state=session_state,
        ).to_dict()
    else:
        source_handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
            explicit_review_packet=review if review and not blocked else None,
        ).to_dict()
    source_ready = bool(source_handoff.get("review_packet_ready")) and source_handoff.get("fallback_used") is False
    if store_in_session_state and updated and not source_ready:
        blocked.append("source_handoff_did_not_resolve_updated_actual_review_packet")

    unique_blocked = tuple(dict.fromkeys(item for item in blocked if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    state = "actual_review_packet_session_state_handoff_ready" if not unique_blocked and ready and source_ready else "actual_review_packet_session_state_handoff_blocked"
    return PredictionWarRoomActualReviewPacketSessionStateHandoffHarnessPacket(
        harness_version=ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION,
        harness_id=f"{ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION}:latest:{state}",
        harness_state=state,
        target_session_key=target_session_key,
        review_packet=review,
        source_handoff=source_handoff,
        review_packet_present=bool(review),
        review_packet_contract_version_valid=version_ok,
        review_packet_ready=ready,
        synthetic_review_packet_detected=synthetic,
        fixture_review_packet_detected=fixture,
        store_requested=store_in_session_state,
        session_state_mapping_supplied=session_state is not None,
        session_state_updated=updated,
        source_handoff_ready=source_ready,
        blocker_count=len(unique_blocked),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blocked,
        warning_reasons=unique_warnings,
        handoff_summary={
            "harness_boundary": "ps_q10k_supplied_actual_review_packet_session_state_handoff_only",
            "target_session_key": target_session_key,
            "review_packet_contract_version_valid": version_ok,
            "review_packet_ready": ready,
            "synthetic_review_packet_detected": synthetic,
            "fixture_review_packet_detected": fixture,
            "session_state_updated": updated,
            "source_handoff_ready": source_ready,
            "ui_controls_added": False,
            "ui_triggered_loader_execution": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
