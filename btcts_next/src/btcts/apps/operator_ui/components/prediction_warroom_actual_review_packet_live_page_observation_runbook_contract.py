# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_observation_runbook_contract.py
# desc: PS-Q10S contract-only runbook for live/local observation of the mounted WarRoom actual review-packet page path. This slice does not mutate WarRoom page/panel, import Streamlit, render UI, seed session_state, run loaders, read files, decode payloads, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_review_packet_live_session_seed_page_mount import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION
from .prediction_warroom_actual_review_packet_live_session_seed_gate import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION
from .prediction_warroom_lowered_display_packet_visibility_review_panel import PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION
from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION

ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION = "prediction_warroom_actual_review_packet_live_page_observation_runbook_contract.ps_q10s.v1"

PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS = (
    "Prediction WarRoom real payload review",
    "top/default-expanded",
    "source_handoff=review_source_handoff_fallback_blocked",
    "source_kind=blocked_fallback_contract",
    "fallback=True",
    "No lowered display-packet widget candidates are available for review yet.",
    "ui_triggered_loader_execution:false",
    "runtime_file_read:false",
    "payload_decode:false",
    "runtime_artifact_write:false",
    "approval_or_authorization_grant:false",
    "decision_or_command_ledger_append:false",
    "autotrade_trigger:false",
    "broker_private_api:false",
)

SEEDED_LIVE_PAGE_OBSERVATION_MARKERS = (
    "Prediction WarRoom real payload review",
    "source_handoff=review_source_handoff_ready",
    "source_kind=session_state_in_memory_mapping",
    "fallback=False",
    "ready_for_ui_mount=True",
    "widgets=6",
    "No lowered display-packet widget candidates are available for review yet:absent",
    "ui_triggered_loader_execution:false",
    "runtime_file_read:false",
    "payload_decode:false",
    "runtime_artifact_write:false",
    "approval_or_authorization_grant:false",
    "decision_or_command_ledger_append:false",
    "autotrade_trigger:false",
    "broker_private_api:false",
)

LIVE_PAGE_OBSERVATION_RUNBOOK_SEQUENCE = (
    "declare_contract_only_live_page_observation_runbook",
    "require_ps_q10r_page_mount_guard_green",
    "require_warroom_page_already_mounted_by_ps_q10r",
    "observe_passive_browser_path_first",
    "passive_path_requires_no_supplied_packet_or_gates",
    "passive_path_must_preserve_existing_q9g_fallback",
    "observe_seeded_path_second_only_with_prebuilt_actual_q9f_review_packet",
    "seeded_path_must_use_pre_supplied_in_memory_session_state_values_only",
    "seeded_path_must_not_call_q9b_q9q_q10h_from_warroom_ui",
    "capture_passive_and_seeded_acceptance_markers",
    "forbid_ui_actual_read_controls",
    "forbid_ui_loader_execution",
    "forbid_ui_file_read_or_payload_decode",
    "forbid_ui_runtime_artifact_write",
    "forbid_approval_ledger_autotrade_broker",
    "return_runbook_contract_only",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReviewPacketLivePageObservationRunbookContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    runbook_sequence: Tuple[str, ...] = LIVE_PAGE_OBSERVATION_RUNBOOK_SEQUENCE
    passive_live_page_observation_markers: Tuple[str, ...] = PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS
    seeded_live_page_observation_markers: Tuple[str, ...] = SEEDED_LIVE_PAGE_OBSERVATION_MARKERS
    q10r_page_mount_version: str = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION
    q10p_live_session_seed_gate_version: str = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION
    q9h_source_handoff_version: str = LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION
    q9g_panel_version: str = PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    q10r_guard_passed: bool = False
    warroom_page_mounted_by_q10r: bool = False
    passive_browser_observation_planned: bool = False
    seeded_browser_observation_planned: bool = False
    supplied_actual_q9f_review_packet_available: bool = False
    ready_for_live_local_observation_runbook: bool = False
    live_observation_performed_by_this_contract: bool = False
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
    runbook_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    runbook_only: bool = True
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
            "runbook_sequence": list(self.runbook_sequence),
            "passive_live_page_observation_markers": list(self.passive_live_page_observation_markers),
            "seeded_live_page_observation_markers": list(self.seeded_live_page_observation_markers),
            "q10r_page_mount_version": self.q10r_page_mount_version,
            "q10p_live_session_seed_gate_version": self.q10p_live_session_seed_gate_version,
            "q9h_source_handoff_version": self.q9h_source_handoff_version,
            "q9g_panel_version": self.q9g_panel_version,
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "q10r_guard_passed": self.q10r_guard_passed,
            "warroom_page_mounted_by_q10r": self.warroom_page_mounted_by_q10r,
            "passive_browser_observation_planned": self.passive_browser_observation_planned,
            "seeded_browser_observation_planned": self.seeded_browser_observation_planned,
            "supplied_actual_q9f_review_packet_available": self.supplied_actual_q9f_review_packet_available,
            "ready_for_live_local_observation_runbook": self.ready_for_live_local_observation_runbook,
            "live_observation_performed_by_this_contract": self.live_observation_performed_by_this_contract,
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
            "runbook_summary": dict(self.runbook_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "runbook_only": self.runbook_only,
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


def build_prediction_warroom_actual_review_packet_live_page_observation_runbook_contract(
    *,
    operator_acknowledged: bool = False,
    q10r_guard_passed: bool = False,
    warroom_page_mounted_by_q10r: bool = False,
    passive_browser_observation_planned: bool = False,
    seeded_browser_observation_planned: bool = False,
    supplied_actual_q9f_review_packet_available: bool = False,
    requested_warroom_page_patch_this_slice: bool = False,
    requested_warroom_panel_patch_this_slice: bool = False,
    requested_ui_actual_read_controls: bool = False,
    requested_ui_loader_execution: bool = False,
    requested_ui_file_read_or_decode: bool = False,
    requested_runtime_artifact_write_from_ui: bool = False,
    requested_approval_ledger_autotrade_or_broker: bool = False,
) -> PredictionWarRoomActualReviewPacketLivePageObservationRunbookContractPacket:
    """Return a contract-only runbook for observing the already-mounted Q10R WarRoom path."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not q10r_guard_passed:
        blockers.append("ps_q10r_live_page_mount_guard_required")
    if not warroom_page_mounted_by_q10r:
        blockers.append("warroom_page_must_already_be_mounted_by_ps_q10r")
    if not passive_browser_observation_planned:
        blockers.append("passive_browser_observation_must_be_planned_first")
    if not seeded_browser_observation_planned:
        blockers.append("seeded_browser_observation_must_be_planned_second")
    if seeded_browser_observation_planned and not supplied_actual_q9f_review_packet_available:
        blockers.append("supplied_actual_q9f_review_packet_required_for_seeded_observation")
    if requested_warroom_page_patch_this_slice:
        blockers.append("warroom_page_patch_not_allowed_in_q10s")
    if requested_warroom_panel_patch_this_slice:
        blockers.append("warroom_panel_patch_not_allowed_in_q10s")
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
        warnings.append("runbook_ready_observation_not_performed_by_contract")
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not unique_blockers
    state = "actual_review_packet_live_page_observation_runbook_ready" if ready else "actual_review_packet_live_page_observation_runbook_blocked"
    return PredictionWarRoomActualReviewPacketLivePageObservationRunbookContractPacket(
        contract_version=ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        operator_acknowledged=operator_acknowledged,
        q10r_guard_passed=q10r_guard_passed,
        warroom_page_mounted_by_q10r=warroom_page_mounted_by_q10r,
        passive_browser_observation_planned=passive_browser_observation_planned,
        seeded_browser_observation_planned=seeded_browser_observation_planned,
        supplied_actual_q9f_review_packet_available=supplied_actual_q9f_review_packet_available,
        ready_for_live_local_observation_runbook=ready,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        runbook_summary={
            "boundary": "ps_q10s_contract_only_live_page_observation_runbook",
            "q10r_page_mount_version": ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION,
            "q10p_live_session_seed_gate_version": ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION,
            "q9h_source_handoff_version": LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
            "q9g_panel_version": PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION,
            "ready_for_live_local_observation_runbook": ready,
            "live_observation_performed_by_this_contract": False,
            "session_state_seed_performed_by_this_contract": False,
            "warroom_page_patch_included_this_slice": False,
            "warroom_panel_patch_included_this_slice": False,
            "passive_live_page_observation_markers": list(PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS),
            "seeded_live_page_observation_markers": list(SEEDED_LIVE_PAGE_OBSERVATION_MARKERS),
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
