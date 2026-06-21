# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_top_default_expanded_layout_preflight_contract.py
# desc: PS-Q9U contract-only final preflight for a future WarRoom top/default-expanded real prediction layout patch. Consumes supplied PS-Q9T readiness packets only; does not parse stdout, execute commands, run loaders, read files, decode payloads, render Streamlit, mutate WarRoom page/panel, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_observation_ui_handoff_readiness_contract import (
    ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_CONTRACT_VERSION,
)

TOP_DEFAULT_EXPANDED_LAYOUT_PREFLIGHT_CONTRACT_VERSION = "prediction_warroom_top_default_expanded_layout_preflight_contract.ps_q9u.v1"

TOP_DEFAULT_EXPANDED_LAYOUT_PREFLIGHT_SEQUENCE = (
    "consume_supplied_ps_q9t_readiness_packet_only",
    "verify_ps_q9t_contract_version",
    "verify_future_layout_review_ready",
    "verify_future_top_default_expanded_review_ready",
    "declare_target_warroom_top_section_plan",
    "declare_default_expanded_plan_without_applying_it",
    "require_next_slice_explicit_page_patch",
    "keep_warroom_page_and_panel_mutation_false",
    "keep_ui_controls_and_loader_execution_false",
    "return_layout_preflight_contract_only",
    "do_not_render_streamlit",
    "do_not_trigger_autotrade_or_broker",
)

TARGET_LAYOUT_PLAN_ROWS = (
    {
        "plan_id": "prediction_real_payload_top_section",
        "target_location": "warroom_top_before_overview_zone",
        "section_label": "Prediction WarRoom real payload review",
        "expanded_by_default_plan": "true_after_next_ui_patch_only",
        "applied_this_slice": "false",
        "read_only": "true",
        "execution": "false",
    },
    {
        "plan_id": "existing_folded_review_section_cleanup",
        "target_location": "operator_support_after_mount_review",
        "section_label": "Prediction WarRoom lowered display packet review",
        "expanded_by_default_plan": "false_or_removed_after_next_ui_patch_review",
        "applied_this_slice": "false",
        "read_only": "true",
        "execution": "false",
    },
)

_FORBIDDEN_TRUE_FLAGS = (
    "ready_for_warroom_ui_mount",
    "top_default_expanded_application_allowed",
    "warroom_page_mutation_allowed",
    "warroom_panel_mutation_allowed",
    "page_patch_included",
    "panel_patch_included",
    "streamlit_import_required",
    "ui_controls_added",
    "ui_triggered_loader_execution",
    "observation_command_executed_by_this_contract",
    "stdout_parser_executed_by_this_contract",
    "loader_execution_requested",
    "actual_file_read_performed_by_this_contract",
    "payload_decode_performed_by_this_contract",
    "runtime_artifact_write_allowed",
    "approval_or_authorization_allowed",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
    "would_write_runtime_artifact",
    "would_write_collector_state",
    "would_send_to_broker",
    "broker_execution_requested",
    "mode_apply_requested",
    "command_ledger_append_requested",
    "approval_append_requested",
    "authorization_grant_requested",
    "autotrade_trigger_enabled",
)


@dataclass(frozen=True)
class PredictionWarRoomTopDefaultExpandedLayoutPreflightContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    preflight_sequence: Tuple[str, ...] = TOP_DEFAULT_EXPANDED_LAYOUT_PREFLIGHT_SEQUENCE
    q9t_contract_version: str = ""
    q9t_contract_state: str = ""
    q9t_packet_present: bool = False
    q9t_packet_version_valid: bool = False
    q9t_ready_for_future_warroom_layout_review: bool = False
    q9t_ready_for_future_top_default_expanded_review: bool = False
    q9t_reported_warroom_ui_mount: bool = False
    q9t_reported_page_patch_included: bool = False
    q9t_reported_panel_patch_included: bool = False
    target_layout_plan_rows: Tuple[Mapping[str, Any], ...] = TARGET_LAYOUT_PLAN_ROWS
    ready_for_next_ui_patch_slice: bool = False
    ready_for_warroom_ui_mount: bool = False
    top_default_expanded_application_allowed: bool = False
    default_expanded_applied: bool = False
    page_patch_included: bool = False
    panel_patch_included: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    preflight_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    supplied_q9t_packet_only: bool = True
    layout_preflight_only: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
    stdout_parser_executed_by_this_contract: bool = False
    observation_command_executed_by_this_contract: bool = False
    loader_execution_requested: bool = False
    actual_file_read_performed_by_this_contract: bool = False
    payload_decode_performed_by_this_contract: bool = False
    runtime_artifact_write_allowed: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
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
            "preflight_sequence": list(self.preflight_sequence),
            "q9t_contract_version": self.q9t_contract_version,
            "q9t_contract_state": self.q9t_contract_state,
            "q9t_packet_present": self.q9t_packet_present,
            "q9t_packet_version_valid": self.q9t_packet_version_valid,
            "q9t_ready_for_future_warroom_layout_review": self.q9t_ready_for_future_warroom_layout_review,
            "q9t_ready_for_future_top_default_expanded_review": self.q9t_ready_for_future_top_default_expanded_review,
            "q9t_reported_warroom_ui_mount": self.q9t_reported_warroom_ui_mount,
            "q9t_reported_page_patch_included": self.q9t_reported_page_patch_included,
            "q9t_reported_panel_patch_included": self.q9t_reported_panel_patch_included,
            "target_layout_plan_rows": [dict(row) for row in self.target_layout_plan_rows],
            "ready_for_next_ui_patch_slice": self.ready_for_next_ui_patch_slice,
            "ready_for_warroom_ui_mount": self.ready_for_warroom_ui_mount,
            "top_default_expanded_application_allowed": self.top_default_expanded_application_allowed,
            "default_expanded_applied": self.default_expanded_applied,
            "page_patch_included": self.page_patch_included,
            "panel_patch_included": self.panel_patch_included,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "preflight_summary": dict(self.preflight_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "supplied_q9t_packet_only": self.supplied_q9t_packet_only,
            "layout_preflight_only": self.layout_preflight_only,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
            "stdout_parser_executed_by_this_contract": self.stdout_parser_executed_by_this_contract,
            "observation_command_executed_by_this_contract": self.observation_command_executed_by_this_contract,
            "loader_execution_requested": self.loader_execution_requested,
            "actual_file_read_performed_by_this_contract": self.actual_file_read_performed_by_this_contract,
            "payload_decode_performed_by_this_contract": self.payload_decode_performed_by_this_contract,
            "runtime_artifact_write_allowed": self.runtime_artifact_write_allowed,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
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


def _unsafe_true_flags(packet: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(key for key in _FORBIDDEN_TRUE_FLAGS if packet.get(key) is True)


def build_prediction_warroom_top_default_expanded_layout_preflight_contract(
    *,
    ui_handoff_readiness_packet: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomTopDefaultExpandedLayoutPreflightContractPacket:
    """Build the final contract-only preflight for a future WarRoom top/default-expanded UI patch."""
    q9t = _as_mapping(ui_handoff_readiness_packet)
    blockers: list[str] = []
    warnings: list[str] = []
    if not q9t:
        blockers.append("ps_q9t_ui_handoff_readiness_packet_required")
    version_valid = q9t.get("contract_version") == ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_CONTRACT_VERSION
    if q9t and not version_valid:
        blockers.append("ps_q9t_contract_version_invalid")
    unsafe_flags = _unsafe_true_flags(q9t)
    blockers.extend("ps_q9t_unsafe_true_flag:" + item for item in unsafe_flags)
    q9t_blockers = q9t.get("blocked_reasons") if isinstance(q9t.get("blocked_reasons"), (list, tuple)) else ()
    q9t_warnings = q9t.get("warning_reasons") if isinstance(q9t.get("warning_reasons"), (list, tuple)) else ()
    if q9t_blockers:
        blockers.append("ps_q9t_blockers_present")
    if q9t_warnings:
        warnings.append("ps_q9t_warnings_present")
    q9t_state = str(q9t.get("contract_state") or "")
    layout_ready = q9t.get("ready_for_future_warroom_layout_review") is True
    top_ready = q9t.get("ready_for_future_top_default_expanded_review") is True
    if q9t and q9t_state != "actual_observation_ui_handoff_ready_for_layout_review":
        blockers.append("ps_q9t_contract_state_not_ready")
    if q9t and not layout_ready:
        blockers.append("ps_q9t_future_layout_review_not_ready")
    if q9t and not top_ready:
        blockers.append("ps_q9t_future_top_default_expanded_review_not_ready")
    if q9t and q9t.get("ready_for_warroom_ui_mount") is True:
        blockers.append("ps_q9t_must_not_already_allow_warroom_ui_mount")
    if q9t and q9t.get("page_patch_included") is True:
        blockers.append("ps_q9t_page_patch_must_not_already_be_included")
    if q9t and q9t.get("panel_patch_included") is True:
        blockers.append("ps_q9t_panel_patch_must_not_already_be_included")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(q9t) and not unique_blockers
    state = "top_default_expanded_layout_preflight_ready_for_next_ui_patch_slice" if ready else "top_default_expanded_layout_preflight_blocked"
    return PredictionWarRoomTopDefaultExpandedLayoutPreflightContractPacket(
        contract_version=TOP_DEFAULT_EXPANDED_LAYOUT_PREFLIGHT_CONTRACT_VERSION,
        contract_id=f"{TOP_DEFAULT_EXPANDED_LAYOUT_PREFLIGHT_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        q9t_contract_version=str(q9t.get("contract_version") or ""),
        q9t_contract_state=q9t_state,
        q9t_packet_present=bool(q9t),
        q9t_packet_version_valid=version_valid,
        q9t_ready_for_future_warroom_layout_review=layout_ready,
        q9t_ready_for_future_top_default_expanded_review=top_ready,
        q9t_reported_warroom_ui_mount=q9t.get("ready_for_warroom_ui_mount") is True,
        q9t_reported_page_patch_included=q9t.get("page_patch_included") is True,
        q9t_reported_panel_patch_included=q9t.get("panel_patch_included") is True,
        ready_for_next_ui_patch_slice=ready,
        ready_for_warroom_ui_mount=False,
        top_default_expanded_application_allowed=False,
        default_expanded_applied=False,
        page_patch_included=False,
        panel_patch_included=False,
        warroom_page_mutation_allowed=False,
        warroom_panel_mutation_allowed=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        preflight_summary={
            "boundary": "ps_q9u_top_default_expanded_layout_preflight_contract_only",
            "ready_for_next_ui_patch_slice": ready,
            "target_location": "warroom_top_before_overview_zone",
            "target_section_label": "Prediction WarRoom real payload review",
            "target_expanded_by_default_after_next_ui_patch": ready,
            "page_patch_included": False,
            "panel_patch_included": False,
            "warroom_page_mutation_allowed": False,
            "warroom_panel_mutation_allowed": False,
            "ui_controls_added": False,
            "loader_execution_requested": False,
            "runtime_artifact_write_allowed": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )
