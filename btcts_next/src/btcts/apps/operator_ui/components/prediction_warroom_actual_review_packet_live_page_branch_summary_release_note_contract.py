# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract.py
# desc: PS-Q10W branch summary/release note contract for Q10R-Q10V actual review-packet mounted observation lane. This contract is read-only and does not mutate WarRoom page/panel, import Streamlit, render UI, seed session_state, run loaders, read files, decode payloads, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_review_packet_live_page_observation_capture_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
from .prediction_warroom_actual_review_packet_live_page_observation_runbook_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION
from .prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION
from .prediction_warroom_actual_review_packet_live_page_readiness_exit_contract import (
    ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION,
    MOUNTED_OBSERVATION_LANE_COMMIT_LINEAGE,
    MOUNTED_OBSERVATION_LANE_NOT_DONE_ITEMS,
    MOUNTED_OBSERVATION_LANE_READY_CAPABILITIES,
)
from .prediction_warroom_actual_review_packet_live_session_seed_page_mount import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION

ACTUAL_REVIEW_PACKET_LIVE_PAGE_BRANCH_SUMMARY_RELEASE_NOTE_CONTRACT_VERSION = "prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract.ps_q10w.v1"

BRANCH_SUMMARY_RELEASE_NOTE_SEQUENCE = (
    "declare_branch_summary_release_note_contract_only",
    "summarize_q10r_through_q10v_lineage",
    "summarize_ready_capabilities",
    "summarize_not_done_items",
    "require_q10v_readiness_exit_ready",
    "require_all_lane_guards_green",
    "require_working_tree_clean",
    "declare_ready_for_operator_review_handoff_not_execution",
    "forbid_warroom_page_patch",
    "forbid_warroom_panel_patch",
    "forbid_ui_actual_read_controls",
    "forbid_ui_file_read_payload_decode_runtime_write",
    "forbid_approval_ledger_autotrade_broker",
    "return_branch_summary_release_note_contract_only",
)

BRANCH_SUMMARY_RELEASE_NOTE_TITLE = "Prediction WarRoom actual review-packet mounted observation lane Q10R-Q10V"
BRANCH_SUMMARY_RELEASE_NOTE_STATUS = "ready_for_operator_review_handoff_not_execution"

BRANCH_SUMMARY_RELEASE_NOTE_COMMIT_LINEAGE = MOUNTED_OBSERVATION_LANE_COMMIT_LINEAGE + (
    "1ad3bef0 docs: add actual review packet live page readiness exit contract",
)

BRANCH_SUMMARY_RELEASE_NOTE_COMPLETED_ITEMS = (
    "Q10R mounted the local-only Q10P seed gate before the existing Q9G WarRoom panel.",
    "Q10S fixed passive and seeded live/local observation acceptance markers.",
    "Q10T validated passive and seeded local observation marker capture.",
    "Q10U packaged the operator passive/seeded/boundary handoff checklist.",
    "Q10V declared the mounted observation lane ready for human live/local confirmation and not an execution path.",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReviewPacketLivePageBranchSummaryReleaseNoteContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    release_note_title: str = BRANCH_SUMMARY_RELEASE_NOTE_TITLE
    release_note_status: str = BRANCH_SUMMARY_RELEASE_NOTE_STATUS
    release_note_sequence: Tuple[str, ...] = BRANCH_SUMMARY_RELEASE_NOTE_SEQUENCE
    completed_items: Tuple[str, ...] = BRANCH_SUMMARY_RELEASE_NOTE_COMPLETED_ITEMS
    commit_lineage: Tuple[str, ...] = BRANCH_SUMMARY_RELEASE_NOTE_COMMIT_LINEAGE
    ready_capabilities: Tuple[str, ...] = MOUNTED_OBSERVATION_LANE_READY_CAPABILITIES
    not_done_items: Tuple[str, ...] = MOUNTED_OBSERVATION_LANE_NOT_DONE_ITEMS
    q10r_page_mount_version: str = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION
    q10s_runbook_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION
    q10t_capture_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
    q10u_operator_handoff_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION
    q10v_readiness_exit_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    q10v_readiness_exit_ready: bool = False
    all_lane_guards_green: bool = False
    working_tree_clean: bool = False
    ready_for_operator_review_handoff: bool = False
    execution_path_enabled: bool = False
    production_ui_actual_read_trigger_added: bool = False
    browser_automation_artifact_added: bool = False
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
    release_note_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    release_note_only: bool = True
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
            "release_note_title": self.release_note_title,
            "release_note_status": self.release_note_status,
            "release_note_sequence": list(self.release_note_sequence),
            "completed_items": list(self.completed_items),
            "commit_lineage": list(self.commit_lineage),
            "ready_capabilities": list(self.ready_capabilities),
            "not_done_items": list(self.not_done_items),
            "q10r_page_mount_version": self.q10r_page_mount_version,
            "q10s_runbook_contract_version": self.q10s_runbook_contract_version,
            "q10t_capture_contract_version": self.q10t_capture_contract_version,
            "q10u_operator_handoff_contract_version": self.q10u_operator_handoff_contract_version,
            "q10v_readiness_exit_contract_version": self.q10v_readiness_exit_contract_version,
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "q10v_readiness_exit_ready": self.q10v_readiness_exit_ready,
            "all_lane_guards_green": self.all_lane_guards_green,
            "working_tree_clean": self.working_tree_clean,
            "ready_for_operator_review_handoff": self.ready_for_operator_review_handoff,
            "execution_path_enabled": self.execution_path_enabled,
            "production_ui_actual_read_trigger_added": self.production_ui_actual_read_trigger_added,
            "browser_automation_artifact_added": self.browser_automation_artifact_added,
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
            "release_note_summary": dict(self.release_note_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "release_note_only": self.release_note_only,
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


def build_prediction_warroom_actual_review_packet_live_page_branch_summary_release_note_contract(
    *,
    operator_acknowledged: bool = False,
    q10v_readiness_exit_ready: bool = False,
    all_lane_guards_green: bool = False,
    working_tree_clean: bool = False,
    requested_warroom_page_patch_this_slice: bool = False,
    requested_warroom_panel_patch_this_slice: bool = False,
    requested_ui_actual_read_controls: bool = False,
    requested_ui_loader_execution: bool = False,
    requested_ui_file_read_or_decode: bool = False,
    requested_runtime_artifact_write_from_ui: bool = False,
    requested_approval_ledger_autotrade_or_broker: bool = False,
    requested_production_ui_actual_read_trigger: bool = False,
    requested_browser_automation_artifact: bool = False,
    requested_execution_path: bool = False,
) -> PredictionWarRoomActualReviewPacketLivePageBranchSummaryReleaseNoteContractPacket:
    """Return a branch summary/release-note contract for Q10R-Q10V mounted observation lane."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not q10v_readiness_exit_ready:
        blockers.append("ps_q10v_readiness_exit_ready_required")
    if not all_lane_guards_green:
        blockers.append("all_lane_guards_green_required")
    if not working_tree_clean:
        blockers.append("working_tree_clean_required")
    if requested_warroom_page_patch_this_slice:
        blockers.append("warroom_page_patch_not_allowed_in_q10w")
    if requested_warroom_panel_patch_this_slice:
        blockers.append("warroom_panel_patch_not_allowed_in_q10w")
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
    if requested_production_ui_actual_read_trigger:
        blockers.append("production_ui_actual_read_trigger_not_allowed_in_q10w")
    if requested_browser_automation_artifact:
        blockers.append("browser_automation_artifact_not_allowed_in_q10w")
    if requested_execution_path:
        blockers.append("execution_path_not_allowed_in_q10w")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    if not unique_blockers:
        warnings.append("release_note_ready_for_operator_review_handoff_not_execution")
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not unique_blockers
    state = "actual_review_packet_live_page_branch_summary_release_note_ready" if ready else "actual_review_packet_live_page_branch_summary_release_note_blocked"
    return PredictionWarRoomActualReviewPacketLivePageBranchSummaryReleaseNoteContractPacket(
        contract_version=ACTUAL_REVIEW_PACKET_LIVE_PAGE_BRANCH_SUMMARY_RELEASE_NOTE_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_REVIEW_PACKET_LIVE_PAGE_BRANCH_SUMMARY_RELEASE_NOTE_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        operator_acknowledged=operator_acknowledged,
        q10v_readiness_exit_ready=q10v_readiness_exit_ready,
        all_lane_guards_green=all_lane_guards_green,
        working_tree_clean=working_tree_clean,
        ready_for_operator_review_handoff=ready,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        release_note_summary={
            "boundary": "ps_q10w_contract_only_branch_summary_release_note",
            "release_note_title": BRANCH_SUMMARY_RELEASE_NOTE_TITLE,
            "release_note_status": BRANCH_SUMMARY_RELEASE_NOTE_STATUS,
            "q10v_readiness_exit_contract_version": ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION,
            "ready_for_operator_review_handoff": ready,
            "execution_path_enabled": False,
            "production_ui_actual_read_trigger_added": False,
            "browser_automation_artifact_added": False,
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
