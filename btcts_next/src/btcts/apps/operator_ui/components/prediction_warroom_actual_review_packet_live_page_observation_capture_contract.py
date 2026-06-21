# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_observation_capture_contract.py
# desc: PS-Q10T contract for validating captured live/local observation markers from the already-mounted WarRoom actual review-packet page path. This slice does not mutate WarRoom page/panel, import Streamlit, render UI, seed session_state, run loaders, read files, decode payloads, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_actual_review_packet_live_page_observation_runbook_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
    PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS,
    SEEDED_LIVE_PAGE_OBSERVATION_MARKERS,
)
from .prediction_warroom_actual_review_packet_live_session_seed_page_mount import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION

ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION = "prediction_warroom_actual_review_packet_live_page_observation_capture_contract.ps_q10t.v1"

LIVE_PAGE_OBSERVATION_CAPTURE_SEQUENCE = (
    "declare_contract_only_live_page_observation_capture",
    "require_ps_q10s_runbook_ready",
    "require_ps_q10r_page_mount_guard_green",
    "require_passive_observation_markers_captured",
    "require_seeded_observation_markers_captured",
    "validate_passive_markers_against_ps_q10s",
    "validate_seeded_markers_against_ps_q10s",
    "validate_seeded_absent_markers_are_not_present",
    "forbid_ui_actual_read_controls",
    "forbid_ui_loader_execution",
    "forbid_ui_file_read_or_payload_decode",
    "forbid_ui_runtime_artifact_write",
    "forbid_approval_ledger_autotrade_broker",
    "return_observation_capture_contract_only",
)


def _unique_text_items(items: Iterable[Any] | None) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in (items or ()) if str(item)))


def _missing_markers(expected: Tuple[str, ...], observed: Tuple[str, ...]) -> Tuple[str, ...]:
    observed_set = set(observed)
    return tuple(item for item in expected if item not in observed_set)


def _absent_marker_violations(expected: Tuple[str, ...], observed: Tuple[str, ...]) -> Tuple[str, ...]:
    observed_set = set(observed)
    violations: list[str] = []
    for item in expected:
        if not item.endswith(":absent"):
            continue
        present_marker = item.removesuffix(":absent")
        present_variants = (present_marker, f"{present_marker}.")
        matched = next((marker for marker in present_variants if marker in observed_set), None)
        if matched is not None:
            violations.append(matched)
    return tuple(violations)


@dataclass(frozen=True)
class PredictionWarRoomActualReviewPacketLivePageObservationCaptureContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    capture_sequence: Tuple[str, ...] = LIVE_PAGE_OBSERVATION_CAPTURE_SEQUENCE
    q10s_runbook_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION
    q10r_page_mount_version: str = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION
    expected_passive_markers: Tuple[str, ...] = PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS
    expected_seeded_markers: Tuple[str, ...] = SEEDED_LIVE_PAGE_OBSERVATION_MARKERS
    passive_observed_markers: Tuple[str, ...] = ()
    seeded_observed_markers: Tuple[str, ...] = ()
    passive_missing_markers: Tuple[str, ...] = ()
    seeded_missing_markers: Tuple[str, ...] = ()
    seeded_absent_marker_violations: Tuple[str, ...] = ()
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    q10s_runbook_ready: bool = False
    q10r_guard_passed: bool = False
    passive_observation_captured: bool = False
    seeded_observation_captured: bool = False
    passive_observation_matches_runbook: bool = False
    seeded_observation_matches_runbook: bool = False
    ready_for_live_page_observation_acceptance: bool = False
    live_browser_observation_performed_by_this_contract: bool = False
    session_state_seed_performed_by_this_contract: bool = False
    warroom_page_patch_included_this_slice: bool = False
    warroom_panel_patch_included_this_slice: bool = False
    ui_actual_read_controls_allowed: bool = False
    ui_loader_execution_allowed: bool = False
    ui_file_read_allowed: bool = False
    ui_payload_decode_allowed: bool = False
    runtime_artifact_write_allowed_from_ui: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    capture_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    observation_capture_only: bool = True
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
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "contract_state": self.contract_state,
            "capture_sequence": list(self.capture_sequence),
            "q10s_runbook_contract_version": self.q10s_runbook_contract_version,
            "q10r_page_mount_version": self.q10r_page_mount_version,
            "expected_passive_markers": list(self.expected_passive_markers),
            "expected_seeded_markers": list(self.expected_seeded_markers),
            "passive_observed_markers": list(self.passive_observed_markers),
            "seeded_observed_markers": list(self.seeded_observed_markers),
            "passive_missing_markers": list(self.passive_missing_markers),
            "seeded_missing_markers": list(self.seeded_missing_markers),
            "seeded_absent_marker_violations": list(self.seeded_absent_marker_violations),
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "q10s_runbook_ready": self.q10s_runbook_ready,
            "q10r_guard_passed": self.q10r_guard_passed,
            "passive_observation_captured": self.passive_observation_captured,
            "seeded_observation_captured": self.seeded_observation_captured,
            "passive_observation_matches_runbook": self.passive_observation_matches_runbook,
            "seeded_observation_matches_runbook": self.seeded_observation_matches_runbook,
            "ready_for_live_page_observation_acceptance": self.ready_for_live_page_observation_acceptance,
            "live_browser_observation_performed_by_this_contract": self.live_browser_observation_performed_by_this_contract,
            "session_state_seed_performed_by_this_contract": self.session_state_seed_performed_by_this_contract,
            "warroom_page_patch_included_this_slice": self.warroom_page_patch_included_this_slice,
            "warroom_panel_patch_included_this_slice": self.warroom_panel_patch_included_this_slice,
            "ui_actual_read_controls_allowed": self.ui_actual_read_controls_allowed,
            "ui_loader_execution_allowed": self.ui_loader_execution_allowed,
            "ui_file_read_allowed": self.ui_file_read_allowed,
            "ui_payload_decode_allowed": self.ui_payload_decode_allowed,
            "runtime_artifact_write_allowed_from_ui": self.runtime_artifact_write_allowed_from_ui,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "capture_summary": dict(self.capture_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "observation_capture_only": self.observation_capture_only,
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
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


def build_prediction_warroom_actual_review_packet_live_page_observation_capture_contract(
    *,
    passive_observed_markers: Iterable[Any] | None = None,
    seeded_observed_markers: Iterable[Any] | None = None,
    operator_acknowledged: bool = False,
    q10s_runbook_ready: bool = False,
    q10r_guard_passed: bool = False,
    requested_warroom_page_patch_this_slice: bool = False,
    requested_warroom_panel_patch_this_slice: bool = False,
    requested_ui_actual_read_controls: bool = False,
    requested_ui_loader_execution: bool = False,
    requested_ui_file_read_or_decode: bool = False,
    requested_runtime_artifact_write_from_ui: bool = False,
    requested_approval_ledger_autotrade_or_broker: bool = False,
) -> PredictionWarRoomActualReviewPacketLivePageObservationCaptureContractPacket:
    """Validate passive/seeded observation markers against PS-Q10S acceptance markers."""
    passive_markers = _unique_text_items(passive_observed_markers)
    seeded_markers = _unique_text_items(seeded_observed_markers)
    passive_missing = _missing_markers(PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS, passive_markers)
    seeded_missing = _missing_markers(SEEDED_LIVE_PAGE_OBSERVATION_MARKERS, seeded_markers)
    absent_violations = _absent_marker_violations(SEEDED_LIVE_PAGE_OBSERVATION_MARKERS, seeded_markers)
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not q10s_runbook_ready:
        blockers.append("ps_q10s_runbook_ready_required")
    if not q10r_guard_passed:
        blockers.append("ps_q10r_live_page_mount_guard_required")
    if not passive_markers:
        blockers.append("passive_observation_markers_required")
    if not seeded_markers:
        blockers.append("seeded_observation_markers_required")
    if passive_missing:
        blockers.append("passive_observation_markers_missing")
    if seeded_missing:
        blockers.append("seeded_observation_markers_missing")
    if absent_violations:
        blockers.append("seeded_absent_marker_observed_as_present")
    if requested_warroom_page_patch_this_slice:
        blockers.append("warroom_page_patch_not_allowed_in_q10t")
    if requested_warroom_panel_patch_this_slice:
        blockers.append("warroom_panel_patch_not_allowed_in_q10t")
    if requested_ui_actual_read_controls:
        blockers.append("warroom_ui_actual_read_controls_not_allowed")
    if requested_ui_loader_execution:
        blockers.append("warroom_ui_loader_execution_not_allowed")
    if requested_ui_file_read_or_decode:
        blockers.append("warroom_ui_file_read_or_payload_decode_not_allowed")
    if requested_runtime_artifact_write_from_ui:
        blockers.append("runtime_artifact_write_from_warroom_ui_not_allowed")
    if requested_approval_ledger_autotrade_or_broker:
        blockers.append("approval_ledger_autotrade_broker_not_allowed")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    if not unique_blockers:
        warnings.append("live_local_observation_capture_accepted_contract_only")
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    passive_matches = bool(passive_markers) and not passive_missing
    seeded_matches = bool(seeded_markers) and not seeded_missing and not absent_violations
    ready = not unique_blockers
    state = "actual_review_packet_live_page_observation_capture_accepted" if ready else "actual_review_packet_live_page_observation_capture_blocked"
    return PredictionWarRoomActualReviewPacketLivePageObservationCaptureContractPacket(
        contract_version=ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        passive_observed_markers=passive_markers,
        seeded_observed_markers=seeded_markers,
        passive_missing_markers=passive_missing,
        seeded_missing_markers=seeded_missing,
        seeded_absent_marker_violations=absent_violations,
        operator_acknowledged=operator_acknowledged,
        q10s_runbook_ready=q10s_runbook_ready,
        q10r_guard_passed=q10r_guard_passed,
        passive_observation_captured=bool(passive_markers),
        seeded_observation_captured=bool(seeded_markers),
        passive_observation_matches_runbook=passive_matches,
        seeded_observation_matches_runbook=seeded_matches,
        ready_for_live_page_observation_acceptance=ready,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        capture_summary={
            "boundary": "ps_q10t_contract_only_live_page_observation_capture",
            "q10s_runbook_contract_version": ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
            "q10r_page_mount_version": ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION,
            "passive_observation_matches_runbook": passive_matches,
            "seeded_observation_matches_runbook": seeded_matches,
            "ready_for_live_page_observation_acceptance": ready,
            "live_browser_observation_performed_by_this_contract": False,
            "session_state_seed_performed_by_this_contract": False,
            "warroom_page_patch_included_this_slice": False,
            "warroom_panel_patch_included_this_slice": False,
            "ui_actual_read_controls_allowed": False,
            "ui_loader_execution_allowed": False,
            "ui_file_read_allowed": False,
            "ui_payload_decode_allowed": False,
            "runtime_artifact_write_allowed_from_ui": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )
