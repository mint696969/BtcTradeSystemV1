# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_page_readiness_exit_contract.py
# desc: PS-Q10V consolidated readiness/exit contract for the already-mounted WarRoom actual review-packet live/local observation lane. This contract is read-only and does not mutate WarRoom page/panel, import Streamlit, render UI, seed session_state, run loaders, read files, decode payloads, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_review_packet_live_page_observation_capture_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
from .prediction_warroom_actual_review_packet_live_page_observation_runbook_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION
from .prediction_warroom_actual_review_packet_live_page_operator_handoff_checklist_contract import ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION
from .prediction_warroom_actual_review_packet_live_session_seed_page_mount import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION

ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION = "prediction_warroom_actual_review_packet_live_page_readiness_exit_contract.ps_q10v.v1"

MOUNTED_OBSERVATION_LANE_COMMIT_LINEAGE = (
    "3043f12e feat: mount actual review packet live session seed gate",
    "60bd0d43 docs: add actual review packet live page observation runbook",
    "21c60169 test: capture actual review packet live page observation",
    "52db4fd7 docs: add actual review packet live page operator handoff checklist",
)

MOUNTED_OBSERVATION_LANE_READY_CAPABILITIES = (
    "q10r_minimal_warroom_page_mount_q10p_gate_before_existing_q9g_panel",
    "q10s_passive_and_seeded_acceptance_markers_fixed",
    "q10t_passive_and_seeded_marker_capture_validated",
    "q10u_operator_handoff_checklist_packaged",
    "ready_for_human_live_local_confirmation",
)

MOUNTED_OBSERVATION_LANE_NOT_DONE_ITEMS = (
    "production_ui_actual_read_trigger_not_added",
    "browser_automation_artifact_not_added",
    "broker_or_autotrade_execution_path_not_added",
    "q9b_q9q_q10h_not_called_from_warroom_ui",
    "runtime_file_read_not_enabled_from_warroom_ui",
    "payload_decode_not_enabled_from_warroom_ui",
    "runtime_artifact_write_not_enabled_from_warroom_ui",
    "approval_ledger_not_enabled_from_warroom_ui",
)

READINESS_EXIT_SEQUENCE = (
    "declare_consolidated_readiness_exit_contract_only",
    "require_q10r_page_mount_guard_green",
    "require_q10s_runbook_guard_green",
    "require_q10t_capture_guard_green",
    "require_q10u_operator_handoff_guard_green",
    "require_all_close_guards_green",
    "require_working_tree_clean",
    "declare_ready_for_human_live_local_confirmation",
    "declare_not_an_execution_path",
    "declare_production_ui_actual_read_trigger_not_added",
    "declare_browser_automation_artifact_not_added",
    "declare_broker_autotrade_execution_path_not_added",
    "forbid_warroom_page_patch",
    "forbid_warroom_panel_patch",
    "forbid_ui_actual_read_controls",
    "forbid_q9b_q9q_q10h_from_warroom_ui",
    "forbid_ui_file_read_payload_decode_runtime_write",
    "forbid_approval_ledger_autotrade_broker",
    "return_readiness_exit_contract_only",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReviewPacketLivePageReadinessExitContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    readiness_exit_sequence: Tuple[str, ...] = READINESS_EXIT_SEQUENCE
    commit_lineage: Tuple[str, ...] = MOUNTED_OBSERVATION_LANE_COMMIT_LINEAGE
    ready_capabilities: Tuple[str, ...] = MOUNTED_OBSERVATION_LANE_READY_CAPABILITIES
    not_done_items: Tuple[str, ...] = MOUNTED_OBSERVATION_LANE_NOT_DONE_ITEMS
    q10r_page_mount_version: str = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION
    q10s_runbook_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION
    q10t_capture_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION
    q10u_operator_handoff_contract_version: str = ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    q10r_guard_passed: bool = False
    q10s_guard_passed: bool = False
    q10t_guard_passed: bool = False
    q10u_guard_passed: bool = False
    all_close_guards_passed: bool = False
    working_tree_clean: bool = False
    ready_for_human_live_local_confirmation: bool = False
    execution_path_enabled: bool = False
    production_ui_actual_read_trigger_added: bool = False
    browser_automation_artifact_added: bool = False
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
    readiness_exit_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    readiness_exit_only: bool = True
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
            "readiness_exit_sequence": list(self.readiness_exit_sequence),
            "commit_lineage": list(self.commit_lineage),
            "ready_capabilities": list(self.ready_capabilities),
            "not_done_items": list(self.not_done_items),
            "q10r_page_mount_version": self.q10r_page_mount_version,
            "q10s_runbook_contract_version": self.q10s_runbook_contract_version,
            "q10t_capture_contract_version": self.q10t_capture_contract_version,
            "q10u_operator_handoff_contract_version": self.q10u_operator_handoff_contract_version,
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "q10r_guard_passed": self.q10r_guard_passed,
            "q10s_guard_passed": self.q10s_guard_passed,
            "q10t_guard_passed": self.q10t_guard_passed,
            "q10u_guard_passed": self.q10u_guard_passed,
            "all_close_guards_passed": self.all_close_guards_passed,
            "working_tree_clean": self.working_tree_clean,
            "ready_for_human_live_local_confirmation": self.ready_for_human_live_local_confirmation,
            "execution_path_enabled": self.execution_path_enabled,
            "production_ui_actual_read_trigger_added": self.production_ui_actual_read_trigger_added,
            "browser_automation_artifact_added": self.browser_automation_artifact_added,
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
            "readiness_exit_summary": dict(self.readiness_exit_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "readiness_exit_only": self.readiness_exit_only,
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


def build_prediction_warroom_actual_review_packet_live_page_readiness_exit_contract(
    *,
    operator_acknowledged: bool = False,
    q10r_guard_passed: bool = False,
    q10s_guard_passed: bool = False,
    q10t_guard_passed: bool = False,
    q10u_guard_passed: bool = False,
    all_close_guards_passed: bool = False,
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
) -> PredictionWarRoomActualReviewPacketLivePageReadinessExitContractPacket:
    """Return a consolidated readiness/exit contract for the mounted observation lane."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not q10r_guard_passed:
        blockers.append("ps_q10r_page_mount_guard_required")
    if not q10s_guard_passed:
        blockers.append("ps_q10s_runbook_guard_required")
    if not q10t_guard_passed:
        blockers.append("ps_q10t_capture_guard_required")
    if not q10u_guard_passed:
        blockers.append("ps_q10u_operator_handoff_guard_required")
    if not all_close_guards_passed:
        blockers.append("all_close_guards_green_required")
    if not working_tree_clean:
        blockers.append("working_tree_clean_required")
    if requested_warroom_page_patch_this_slice:
        blockers.append("warroom_page_patch_not_allowed_in_q10v")
    if requested_warroom_panel_patch_this_slice:
        blockers.append("warroom_panel_patch_not_allowed_in_q10v")
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
        blockers.append("production_ui_actual_read_trigger_not_allowed_in_q10v")
    if requested_browser_automation_artifact:
        blockers.append("browser_automation_artifact_not_allowed_in_q10v")
    if requested_execution_path:
        blockers.append("execution_path_not_allowed_in_q10v")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    if not unique_blockers:
        warnings.append("mounted_observation_lane_ready_for_human_confirmation_not_execution")
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not unique_blockers
    state = "actual_review_packet_live_page_readiness_exit_ready" if ready else "actual_review_packet_live_page_readiness_exit_blocked"
    return PredictionWarRoomActualReviewPacketLivePageReadinessExitContractPacket(
        contract_version=ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_REVIEW_PACKET_LIVE_PAGE_READINESS_EXIT_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        operator_acknowledged=operator_acknowledged,
        q10r_guard_passed=q10r_guard_passed,
        q10s_guard_passed=q10s_guard_passed,
        q10t_guard_passed=q10t_guard_passed,
        q10u_guard_passed=q10u_guard_passed,
        all_close_guards_passed=all_close_guards_passed,
        working_tree_clean=working_tree_clean,
        ready_for_human_live_local_confirmation=ready,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        readiness_exit_summary={
            "boundary": "ps_q10v_contract_only_mounted_observation_lane_readiness_exit",
            "q10r_page_mount_version": ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_PAGE_MOUNT_VERSION,
            "q10s_runbook_contract_version": ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
            "q10t_capture_contract_version": ACTUAL_REVIEW_PACKET_LIVE_PAGE_OBSERVATION_CAPTURE_CONTRACT_VERSION,
            "q10u_operator_handoff_contract_version": ACTUAL_REVIEW_PACKET_LIVE_PAGE_OPERATOR_HANDOFF_CHECKLIST_CONTRACT_VERSION,
            "ready_for_human_live_local_confirmation": ready,
            "execution_path_enabled": False,
            "production_ui_actual_read_trigger_added": False,
            "browser_automation_artifact_added": False,
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
