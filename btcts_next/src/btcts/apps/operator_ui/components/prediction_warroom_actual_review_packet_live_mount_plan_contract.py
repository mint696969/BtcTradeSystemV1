# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_review_packet_live_mount_plan_contract.py
# desc: PS-Q10Q contract-only plan for a future local-only WarRoom page mount of the actual review-packet live-session seed gate. This slice does not mutate WarRoom page/panel, import Streamlit, render UI, seed session_state, run loaders, read files, decode payloads, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_review_packet_live_session_seed_gate import ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION
from .prediction_warroom_actual_review_packet_local_observation_seed_hook import ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION
from .prediction_warroom_lowered_display_packet_visibility_review_panel import PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION
from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION

ACTUAL_REVIEW_PACKET_LIVE_MOUNT_PLAN_CONTRACT_VERSION = "prediction_warroom_actual_review_packet_live_mount_plan_contract.ps_q10q.v1"

LIVE_MOUNT_PLAN_TARGET_SECTION_LABEL = "Prediction WarRoom real payload review"
LIVE_MOUNT_PLAN_INSERTION_ANCHOR = "before_existing_q9g_panel_render_call"
LIVE_MOUNT_PLAN_EXISTING_PANEL_CALL = "render_prediction_warroom_lowered_display_packet_visibility_review_panel()"
LIVE_MOUNT_PLAN_GATE_CALL = "build_prediction_warroom_actual_review_packet_live_session_seed_gate(...)"

ACTUAL_REVIEW_PACKET_LIVE_MOUNT_PLAN_SEQUENCE = (
    "declare_contract_only_future_warroom_mount_plan",
    "require_ps_q10p_live_session_seed_gate_guard_green",
    "require_ps_q10o_seed_to_panel_integration_guard_green",
    "require_top_real_payload_review_section_present",
    "require_existing_q9g_panel_call_present",
    "plan_gate_call_before_existing_q9g_panel_render_only",
    "gate_must_be_passive_by_default",
    "gate_must_accept_only_supplied_in_memory_actual_q9f_review_packet",
    "gate_must_not_build_or_read_actual_packet_from_warroom_ui",
    "fallback_must_remain_unchanged_without_packet_or_gates",
    "forbid_ui_actual_read_controls",
    "forbid_ui_loader_execution",
    "forbid_ui_file_read_or_payload_decode",
    "forbid_ui_runtime_artifact_write",
    "forbid_approval_ledger_autotrade_broker",
    "do_not_mount_warroom_page_in_this_slice",
    "forbid_page_patch_in_this_slice",
    "return_mount_plan_contract_only",
)

FUTURE_PAGE_PATCH_REQUIREMENTS = (
    "must_mount_inside_prediction_warroom_real_payload_review_section",
    "must_call_gate_before_existing_q9g_panel_render_only",
    "must_leave_existing_q9g_panel_call_in_place",
    "must_be_passive_by_default_without_packet_or_gates",
    "must_preserve_fallback_message_without_packet",
    "must_not_add_button_toggle_form_for_actual_read",
    "must_not_call_q9b_q9q_q10h_from_warroom_ui",
    "must_not_read_files_from_warroom_ui",
    "must_not_decode_payloads_from_warroom_ui",
    "must_not_write_runtime_artifacts_from_warroom_ui",
    "must_not_append_approval_or_ledgers",
    "must_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReviewPacketLiveMountPlanContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    target_section_label: str = LIVE_MOUNT_PLAN_TARGET_SECTION_LABEL
    insertion_anchor: str = LIVE_MOUNT_PLAN_INSERTION_ANCHOR
    existing_panel_call: str = LIVE_MOUNT_PLAN_EXISTING_PANEL_CALL
    planned_gate_call: str = LIVE_MOUNT_PLAN_GATE_CALL
    plan_sequence: Tuple[str, ...] = ACTUAL_REVIEW_PACKET_LIVE_MOUNT_PLAN_SEQUENCE
    future_page_patch_requirements: Tuple[str, ...] = FUTURE_PAGE_PATCH_REQUIREMENTS
    q10p_live_session_seed_gate_version: str = ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION
    q10n_seed_hook_version: str = ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION
    q9h_source_handoff_version: str = LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION
    q9g_panel_version: str = PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    q10p_guard_passed: bool = False
    q10o_guard_passed: bool = False
    top_real_payload_review_section_present: bool = False
    existing_q9g_panel_call_present: bool = False
    actual_review_packet_available_in_process_memory: bool = False
    ready_for_future_page_patch_slice: bool = False
    ready_for_live_warroom_mount_now: bool = False
    page_patch_included_this_slice: bool = False
    panel_patch_included_this_slice: bool = False
    gate_mount_performed_this_slice: bool = False
    streamlit_render_performed_by_this_contract: bool = False
    live_session_state_seed_performed_by_this_contract: bool = False
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
    plan_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    mount_plan_only: bool = True
    local_only: bool = True
    in_memory_input_only: bool = True
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
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "contract_state": self.contract_state,
            "target_section_label": self.target_section_label,
            "insertion_anchor": self.insertion_anchor,
            "existing_panel_call": self.existing_panel_call,
            "planned_gate_call": self.planned_gate_call,
            "plan_sequence": list(self.plan_sequence),
            "future_page_patch_requirements": list(self.future_page_patch_requirements),
            "q10p_live_session_seed_gate_version": self.q10p_live_session_seed_gate_version,
            "q10n_seed_hook_version": self.q10n_seed_hook_version,
            "q9h_source_handoff_version": self.q9h_source_handoff_version,
            "q9g_panel_version": self.q9g_panel_version,
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "q10p_guard_passed": self.q10p_guard_passed,
            "q10o_guard_passed": self.q10o_guard_passed,
            "top_real_payload_review_section_present": self.top_real_payload_review_section_present,
            "existing_q9g_panel_call_present": self.existing_q9g_panel_call_present,
            "actual_review_packet_available_in_process_memory": self.actual_review_packet_available_in_process_memory,
            "ready_for_future_page_patch_slice": self.ready_for_future_page_patch_slice,
            "ready_for_live_warroom_mount_now": self.ready_for_live_warroom_mount_now,
            "page_patch_included_this_slice": self.page_patch_included_this_slice,
            "panel_patch_included_this_slice": self.panel_patch_included_this_slice,
            "gate_mount_performed_this_slice": self.gate_mount_performed_this_slice,
            "streamlit_render_performed_by_this_contract": self.streamlit_render_performed_by_this_contract,
            "live_session_state_seed_performed_by_this_contract": self.live_session_state_seed_performed_by_this_contract,
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
            "plan_summary": dict(self.plan_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "mount_plan_only": self.mount_plan_only,
            "local_only": self.local_only,
            "in_memory_input_only": self.in_memory_input_only,
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


def build_prediction_warroom_actual_review_packet_live_mount_plan_contract(
    *,
    operator_acknowledged: bool = False,
    q10p_guard_passed: bool = False,
    q10o_guard_passed: bool = False,
    top_real_payload_review_section_present: bool = False,
    existing_q9g_panel_call_present: bool = False,
    actual_review_packet_available_in_process_memory: bool = False,
    requested_page_patch_this_slice: bool = False,
    requested_panel_patch_this_slice: bool = False,
    requested_gate_mount_this_slice: bool = False,
    requested_ui_actual_read_controls: bool = False,
    requested_ui_loader_execution: bool = False,
    requested_ui_file_read_or_decode: bool = False,
    requested_runtime_artifact_write_from_ui: bool = False,
    requested_approval_ledger_autotrade_or_broker: bool = False,
) -> PredictionWarRoomActualReviewPacketLiveMountPlanContractPacket:
    """Return a contract-only future mount plan; this function performs no page patch or seed."""
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required")
    if not q10p_guard_passed:
        blockers.append("ps_q10p_live_session_seed_gate_guard_required")
    if not q10o_guard_passed:
        blockers.append("ps_q10o_seed_to_panel_integration_guard_required")
    if not top_real_payload_review_section_present:
        blockers.append("warroom_top_real_payload_review_section_required")
    if not existing_q9g_panel_call_present:
        blockers.append("existing_q9g_panel_call_required")
    if not actual_review_packet_available_in_process_memory:
        blockers.append("actual_review_packet_must_be_available_in_process_memory")
    if requested_page_patch_this_slice:
        blockers.append("warroom_page_patch_not_allowed_in_q10q")
    if requested_panel_patch_this_slice:
        blockers.append("warroom_panel_patch_not_allowed_in_q10q")
    if requested_gate_mount_this_slice:
        blockers.append("gate_mount_not_allowed_in_q10q")
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
        warnings.append("future_page_patch_slice_still_required_before_live_browser_mount")
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready_for_future_patch = not unique_blockers
    state = "actual_review_packet_live_mount_plan_ready_for_future_page_patch" if ready_for_future_patch else "actual_review_packet_live_mount_plan_blocked"
    return PredictionWarRoomActualReviewPacketLiveMountPlanContractPacket(
        contract_version=ACTUAL_REVIEW_PACKET_LIVE_MOUNT_PLAN_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_REVIEW_PACKET_LIVE_MOUNT_PLAN_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        operator_acknowledged=operator_acknowledged,
        q10p_guard_passed=q10p_guard_passed,
        q10o_guard_passed=q10o_guard_passed,
        top_real_payload_review_section_present=top_real_payload_review_section_present,
        existing_q9g_panel_call_present=existing_q9g_panel_call_present,
        actual_review_packet_available_in_process_memory=actual_review_packet_available_in_process_memory,
        ready_for_future_page_patch_slice=ready_for_future_patch,
        ready_for_live_warroom_mount_now=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        plan_summary={
            "boundary": "ps_q10q_contract_only_future_warroom_mount_plan",
            "target_section_label": LIVE_MOUNT_PLAN_TARGET_SECTION_LABEL,
            "insertion_anchor": LIVE_MOUNT_PLAN_INSERTION_ANCHOR,
            "existing_panel_call": LIVE_MOUNT_PLAN_EXISTING_PANEL_CALL,
            "planned_gate_call": LIVE_MOUNT_PLAN_GATE_CALL,
            "q10p_live_session_seed_gate_version": ACTUAL_REVIEW_PACKET_LIVE_SESSION_SEED_GATE_VERSION,
            "q10n_seed_hook_version": ACTUAL_REVIEW_PACKET_LOCAL_OBSERVATION_SEED_HOOK_VERSION,
            "q9h_source_handoff_version": LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
            "q9g_panel_version": PREDICTION_WARROOM_LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_PANEL_VERSION,
            "ready_for_future_page_patch_slice": ready_for_future_patch,
            "ready_for_live_warroom_mount_now": False,
            "page_patch_included_this_slice": False,
            "panel_patch_included_this_slice": False,
            "gate_mount_performed_this_slice": False,
            "fallback_must_remain_unchanged_without_packet_or_gates": True,
            "ui_actual_read_controls_allowed": False,
            "ui_loader_execution_allowed": False,
            "ui_file_read_allowed": False,
            "ui_payload_decode_allowed": False,
            "runtime_artifact_write_allowed_from_ui": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "future_page_patch_requirements": list(FUTURE_PAGE_PATCH_REQUIREMENTS),
        },
    )
