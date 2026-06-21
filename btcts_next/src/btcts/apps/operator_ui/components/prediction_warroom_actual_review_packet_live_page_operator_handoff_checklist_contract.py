# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract.py
# desc: PS-Q10U operator-facing handoff/checklist contract for the already-mounted WarRoom actual review-packet live/local observation path. This contract is read-only and does not mutate WarRoom page/panel, import Streamlit, render UI, seed session_state, run loaders, read files, decode payloads, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_review_packet_live_page_observation_capture_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
from .prediction_warroom_actual_review_packet_live_page_observation_runbook_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
    PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS,
    SEEDED_LIVE_PAGE_OBSERVATION_MARKERS,
)
from .prediction_warroom_actual_review_packet_live_session_seed_page_mount import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION

ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION = "prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract.ps_q10u.v1"

OPERATOR_HANDOFF_CHECKLIST_SEQUENCE = (
    "declare_operator_handoff_checklist_contract_only",
    "require_ps_q10r_page_mount_guard_green",
    "require_ps_q10s_runbook_ready",
    "require_ps_q10t_capture_accepted",
    "confirm_passive_no_packet_browser_check_first",
    "confirm_seeded_prebuilt_in_memory_packet_check_second",
    "confirm_boundary_checklist_no_ui_runtime_actions",
    "forbid_warroom_page_patch",
    "forbid_warroom_panel_patch",
    "forbid_ui_actual_read_controls",
    "forbid_q9b_q9q_q10h_from_warroom_ui",
    "forbid_ui_file_read_payload_decode_runtime_write",
    "forbid_approval_ledger_autotrade_broker",
    "return_operator_handoff_checklist_contract_only",
)

PASSIVE_OPERATOR_CONFIRMATION_CHECKLIST = (
    "Open WarRoom page without supplying actual review packet or local-only seed gates.",
    "Confirm Prediction WarRoom real payload review remains top/default-expanded.",
    "Confirm source_handoff=review_source_handoff_fallback_blocked.",
    "Confirm source_kind=blocked_fallback_contract.",
    "Confirm fallback=True.",
    "Confirm No lowered display-packet widget candidates are available for review yet.",
)

SEEDED_OPERATOR_CONFIRMATION_CHECKLIST = (
    "Use only a pre-built actual Q9F review packet supplied in memory/session_state.",
    "Set explicit local-only seed gates before WarRoom panel render.",
    "Do not call Q9B/Q9Q/Q10H from WarRoom UI.",
    "Confirm source_handoff=review_source_handoff_ready.",
    "Confirm source_kind=session_state_in_memory_mapping.",
    "Confirm fallback=False.",
    "Confirm ready_for_ui_mount=True.",
    "Confirm widgets=6.",
    "Confirm fallback info message is absent.",
)

BOUNDARY_OPERATOR_CONFIRMATION_CHECKLIST = (
    "Confirm no UI actual-read button/form/toggle was added.",
    "Confirm no UI loader execution occurred.",
    "Confirm no file read from WarRoom UI occurred.",
    "Confirm no payload decode from WarRoom UI occurred.",
    "Confirm no runtime artifact write from WarRoom UI occurred.",
    "Confirm no approval or authorization grant occurred.",
    "Confirm no decision or command ledger append occurred.",
    "Confirm no AutoTrade trigger occurred.",
    "Confirm no broker/private API call occurred.",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReviewPacketLivePageOperatorHandoffChecklistContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    checklist_sequence: Tuple[str, ...] = OPERATOR_HANDOFF_CHECKLIST_SEQUENCE
    passive_operator_confirmation_checklist: Tuple[str, ...] = PASSIVE_OPERATOR_CONFIRMATION_CHECKLIST
    seeded_operator_confirmation_checklist: Tuple[str, ...] = SEEDED_OPERATOR_CONFIRMATION_CHECKLIST
    boundary_operator_confirmation_checklist: Tuple[str, ...] = BOUNDARY_OPERATOR_CONFIRMATION_CHECKLIST
    expected_passive_markers: Tuple[str, ...] = PASSIVE_LIVE_PAGE_OBSERVATION_MARKERS
    expected_seeded_markers: Tuple[str, ...] = SEEDED_LIVE_PAGE_OBSERVATION_MARKERS
    q10r_page_mount_version: str = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION
    q10s_runbook_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION
    q10t_capture_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    q10r_guard_passed: bool = False
    q10s_runbook_ready: bool = False
    q10t_capture_accepted: bool = False
    passive_checklist_confirmed: bool = False
    seeded_checklist_confirmed: bool = False
    boundary_checklist_confirmed: bool = False
    ready_for_operator_live_local_handoff: bool = False
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
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    operator_handoff_only: bool = True
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
            "checklist_sequence": list(self.checklist_sequence),
            "passive_operator_confirmation_checklist": list(self.passive_operator_confirmation_checklist),
            "seeded_operator_confirmation_checklist": list(self.seeded_operator_confirmation_checklist),
            "boundary_operator_confirmation_checklist": list(self.boundary_operator_confirmation_checklist),
            "expected_passive_markers": list(self.expected_passive_markers),
            "expected_seeded_markers": list(self.expected_seeded_markers),
            "q10r_page_mount_version": self.q10r_page_mount_version,
            "q10s_runbook_contract_version": self.q10s_runbook_contract_version,
            "q10t_capture_contract_version": self.q10t_capture_contract_version,
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "q10r_guard_passed": self.q10r_guard_passed,
            "q10s_runbook_ready": self.q10s_runbook_ready,
            "q10t_capture_accepted": self.q10t_capture_accepted,
            "passive_checklist_confirmed": self.passive_checklist_confirmed,
            "seeded_checklist_confirmed": self.seeded_checklist_confirmed,
            "boundary_checklist_confirmed": self.boundary_checklist_confirmed,
            "ready_for_operator_live_local_handoff": self.ready_for_operator_live_local_handoff,
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
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "operator_handoff_only": self.operator_handoff_only,
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


def build_prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract(
    *,
    operator_acknowledged: bool = False,
    q10r_guard_passed: bool = False,
    q10s_runbook_ready: bool = False,
    q10t_capture_accepted: bool = False,
    passive_checklist_confirmed: bool = False,
    seeded_checklist_confirmed: bool = False,
    boundary_checklist_confirmed: bool = False,
    requested_warroom_page_patch_this_slice: bool = False,
    requested_warroom_panel_patch_this_slice: bool = False,
    requested_ui_actual_read_controls: bool = False,
    requested_ui_loader_execution: bool = False,
    requested_ui_file_read_or_decode: bool = False,
    requested_runtime_artifact_write_from_ui: bool = False,
    requested_approval_ledger_autotrade_or_broker: bool = False,
) -> PredictionWarRoomActualReviewPacketLivePageOperatorHandoffChecklistContractPacket:
    """Return an operator handoff/checklist contract for the already-mounted live/local observation path."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not q10r_guard_passed:
        blockers.append("ps_q10r_live_page_mount_guard_required")
    if not q10s_runbook_ready:
        blockers.append("ps_q10s_runbook_ready_required")
    if not q10t_capture_accepted:
        blockers.append("ps_q10t_capture_acceptance_required")
    if not passive_checklist_confirmed:
        blockers.append("passive_operator_checklist_confirmation_required")
    if not seeded_checklist_confirmed:
        blockers.append("seeded_operator_checklist_confirmation_required")
    if not boundary_checklist_confirmed:
        blockers.append("boundary_operator_checklist_confirmation_required")
    if requested_warroom_page_patch_this_slice:
        blockers.append("warroom_page_patch_not_allowed_in_q10u")
    if requested_warroom_panel_patch_this_slice:
        blockers.append("warroom_panel_patch_not_allowed_in_q10u")
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
        warnings.append("operator_handoff_checklist_ready_contract_only")
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not unique_blockers
    state = "actual_review_packet_live_page_operator_handoff_checklist_ready" if ready else "actual_review_packet_live_page_operator_handoff_checklist_blocked"
    return PredictionWarRoomActualReviewPacketLivePageOperatorHandoffChecklistContractPacket(
        contract_version=ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        operator_acknowledged=operator_acknowledged,
        q10r_guard_passed=q10r_guard_passed,
        q10s_runbook_ready=q10s_runbook_ready,
        q10t_capture_accepted=q10t_capture_accepted,
        passive_checklist_confirmed=passive_checklist_confirmed,
        seeded_checklist_confirmed=seeded_checklist_confirmed,
        boundary_checklist_confirmed=boundary_checklist_confirmed,
        ready_for_operator_live_local_handoff=ready,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        handoff_summary={
            "boundary": "ps_q10u_contract_only_operator_live_local_handoff_checklist",
            "q10r_page_mount_version": ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION,
            "q10s_runbook_contract_version": ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
            "q10t_capture_contract_version": ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION,
            "ready_for_operator_live_local_handoff": ready,
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
