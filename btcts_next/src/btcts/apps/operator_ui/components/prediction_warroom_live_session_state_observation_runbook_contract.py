# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_live_session_state_observation_runbook_contract.py
# desc: PS-Q10M contract-only runbook for future live WarRoom browser observation of an actual Q9F review packet already placed in Streamlit session_state. This slice does not render Streamlit, mutate WarRoom page/panel, seed live session_state, run loaders, read files, decode payloads, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_review_packet_session_state_handoff_harness import ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION, DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
from .prediction_warroom_lowered_display_packet_visibility_review_panel import PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION
from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION

LIVE_SESSION_STATE_OBSERVATION_RUNBOOK_CONTRACT_VERSION = "prediction_warroom_live_session_state_observation_runbook_contract.ps_q10m.v1"

LIVE_SESSION_STATE_OBSERVATION_SEQUENCE = (
    "declare_contract_only_live_browser_observation_runbook",
    "require_ps_q10k_actual_review_packet_session_handoff_ready",
    "require_ps_q10l_existing_q9g_panel_session_handoff_guard_green",
    "require_actual_review_packet_to_be_built_outside_warroom_ui",
    "declare_live_streamlit_session_state_seed_requires_future_reviewed_slice",
    "forbid_warroom_ui_actual_read_controls",
    "forbid_warroom_ui_loader_execution",
    "forbid_warroom_ui_file_read_or_payload_decode",
    "forbid_warroom_ui_runtime_artifact_write",
    "forbid_warroom_page_or_panel_mutation_in_this_slice",
    "forbid_approval_ledger_autotrade_broker",
    "return_runbook_contract_only",
)

LIVE_BROWSER_ACCEPTANCE_MARKERS = (
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

FUTURE_SEED_SLICE_REQUIREMENTS = (
    "must_use_already_built_actual_q9f_review_packet_mapping",
    "must_store_only_under_ps_q9h_allowed_session_state_key",
    "must_verify_with_ps_q9h_before_rendering",
    "must_not_run_q9b_q9q_q10h_from_warroom_ui",
    "must_not_add_button_toggle_form_for_actual_read",
    "must_not_read_files_from_warroom_ui",
    "must_not_decode_payloads_from_warroom_ui",
    "must_not_write_runtime_artifacts_from_warroom_ui",
    "must_not_append_approval_or_ledgers",
    "must_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLiveSessionStateObservationRunbookContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    target_session_key: str = DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
    runbook_sequence: Tuple[str, ...] = LIVE_SESSION_STATE_OBSERVATION_SEQUENCE
    live_browser_acceptance_markers: Tuple[str, ...] = LIVE_BROWSER_ACCEPTANCE_MARKERS
    future_seed_slice_requirements: Tuple[str, ...] = FUTURE_SEED_SLICE_REQUIREMENTS
    q10k_handoff_harness_version: str = ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION
    q9h_source_handoff_version: str = LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION
    q9g_panel_version: str = PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    q10k_guard_passed: bool = False
    q10l_guard_passed: bool = False
    actual_review_packet_available_outside_ui: bool = False
    ready_for_future_live_session_seed_slice: bool = False
    ready_for_live_browser_observation_now: bool = False
    live_session_state_seed_implemented_this_slice: bool = False
    live_session_state_seed_performed_by_this_contract: bool = False
    browser_observation_performed_by_this_contract: bool = False
    warroom_page_patch_included: bool = False
    warroom_panel_patch_included: bool = False
    warroom_local_observation_hook_patch_included: bool = False
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
    streamlit_render_performed_by_this_contract: bool = False
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
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "contract_state": self.contract_state,
            "target_session_key": self.target_session_key,
            "runbook_sequence": list(self.runbook_sequence),
            "live_browser_acceptance_markers": list(self.live_browser_acceptance_markers),
            "future_seed_slice_requirements": list(self.future_seed_slice_requirements),
            "q10k_handoff_harness_version": self.q10k_handoff_harness_version,
            "q9h_source_handoff_version": self.q9h_source_handoff_version,
            "q9g_panel_version": self.q9g_panel_version,
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "q10k_guard_passed": self.q10k_guard_passed,
            "q10l_guard_passed": self.q10l_guard_passed,
            "actual_review_packet_available_outside_ui": self.actual_review_packet_available_outside_ui,
            "ready_for_future_live_session_seed_slice": self.ready_for_future_live_session_seed_slice,
            "ready_for_live_browser_observation_now": self.ready_for_live_browser_observation_now,
            "live_session_state_seed_implemented_this_slice": self.live_session_state_seed_implemented_this_slice,
            "live_session_state_seed_performed_by_this_contract": self.live_session_state_seed_performed_by_this_contract,
            "browser_observation_performed_by_this_contract": self.browser_observation_performed_by_this_contract,
            "warroom_page_patch_included": self.warroom_page_patch_included,
            "warroom_panel_patch_included": self.warroom_panel_patch_included,
            "warroom_local_observation_hook_patch_included": self.warroom_local_observation_hook_patch_included,
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
            "streamlit_render_performed_by_this_contract": self.streamlit_render_performed_by_this_contract,
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


def build_prediction_warroom_live_session_state_observation_runbook_contract(
    *,
    operator_acknowledged: bool = False,
    q10k_guard_passed: bool = False,
    q10l_guard_passed: bool = False,
    actual_review_packet_available_outside_ui: bool = False,
    requested_page_or_panel_mutation: bool = False,
    requested_live_session_state_seed_this_slice: bool = False,
    requested_warroom_ui_actual_read_control: bool = False,
    requested_warroom_ui_loader_execution: bool = False,
    requested_warroom_ui_file_read_or_decode: bool = False,
    requested_runtime_artifact_write_from_ui: bool = False,
    requested_approval_ledger_autotrade_or_broker: bool = False,
) -> PredictionWarRoomLiveSessionStateObservationRunbookContractPacket:
    """Return a contract-only runbook for the next live session_state seed slice; this function performs no observation."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not q10k_guard_passed:
        blockers.append("ps_q10k_actual_session_handoff_guard_required")
    if not q10l_guard_passed:
        blockers.append("ps_q10l_panel_session_handoff_guard_required")
    if not actual_review_packet_available_outside_ui:
        blockers.append("actual_review_packet_must_be_available_outside_warroom_ui")
    if requested_page_or_panel_mutation:
        blockers.append("warroom_page_or_panel_mutation_not_allowed_in_q10m")
    if requested_live_session_state_seed_this_slice:
        blockers.append("live_session_state_seed_requires_future_reviewed_slice")
    if requested_warroom_ui_actual_read_control:
        blockers.append("warroom_ui_actual_read_control_not_allowed")
    if requested_warroom_ui_loader_execution:
        blockers.append("warroom_ui_loader_execution_not_allowed")
    if requested_warroom_ui_file_read_or_decode:
        blockers.append("warroom_ui_file_read_or_payload_decode_not_allowed")
    if requested_runtime_artifact_write_from_ui:
        blockers.append("runtime_artifact_write_from_warroom_ui_not_allowed")
    if requested_approval_ledger_autotrade_or_broker:
        blockers.append("approval_ledger_autotrade_broker_not_allowed")
    if operator_acknowledged and q10k_guard_passed and q10l_guard_passed and actual_review_packet_available_outside_ui:
        warnings.append("live_browser_observation_still_requires_future_session_state_seed_slice")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready_for_seed = not unique_blockers
    state = "live_session_state_observation_runbook_ready_for_future_seed_slice" if ready_for_seed else "live_session_state_observation_runbook_blocked"
    return PredictionWarRoomLiveSessionStateObservationRunbookContractPacket(
        contract_version=LIVE_SESSION_STATE_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
        contract_id=f"{LIVE_SESSION_STATE_OBSERVATION_RUNBOOK_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        operator_acknowledged=operator_acknowledged,
        q10k_guard_passed=q10k_guard_passed,
        q10l_guard_passed=q10l_guard_passed,
        actual_review_packet_available_outside_ui=actual_review_packet_available_outside_ui,
        ready_for_future_live_session_seed_slice=ready_for_seed,
        ready_for_live_browser_observation_now=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        runbook_summary={
            "boundary": "ps_q10m_contract_only_live_session_state_observation_runbook",
            "target_session_key": DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
            "q10k_handoff_harness_version": ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION,
            "q9h_source_handoff_version": LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
            "q9g_panel_version": PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION,
            "ready_for_future_live_session_seed_slice": ready_for_seed,
            "ready_for_live_browser_observation_now": False,
            "live_session_state_seed_implemented_this_slice": False,
            "warroom_page_patch_included": False,
            "warroom_panel_patch_included": False,
            "ui_actual_read_controls_allowed": False,
            "ui_loader_execution_allowed": False,
            "ui_file_read_allowed": False,
            "ui_payload_decode_allowed": False,
            "runtime_artifact_write_allowed_from_ui": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "acceptance_markers": list(LIVE_BROWSER_ACCEPTANCE_MARKERS),
            "future_seed_slice_requirements": list(FUTURE_SEED_SLICE_REQUIREMENTS),
        },
    )
