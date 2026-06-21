# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_observation_ui_handoff_readiness_contract.py
# desc: PS-Q9T contract-only readiness gate for considering a future WarRoom UI handoff after supplied PS-Q9S stdout parser output. Consumes supplied parser packets only; does not parse stdout, execute commands, run loaders, read files, decode payloads, render Streamlit, mutate WarRoom page/panel, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_observation_stdout_review_parser import ACTUAL_OBSERVATION_STDOUT_REVIEW_PARSER_VERSION

ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_CONTRACT_VERSION = "prediction_warroom_actual_observation_ui_handoff_readiness_contract.ps_q9t.v1"

ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_SEQUENCE = (
    "consume_supplied_ps_q9s_parser_packet_only",
    "verify_ps_q9s_parser_version",
    "verify_real_payload_stdout_review_ready",
    "verify_parser_safety_flags_all_false",
    "allow_future_layout_review_consideration_only",
    "keep_warroom_ui_mount_false",
    "keep_warroom_page_and_panel_mutation_false",
    "keep_top_default_expanded_application_false",
    "return_ui_handoff_readiness_contract_only",
    "do_not_parse_stdout_or_run_loader",
    "do_not_render_streamlit",
    "do_not_trigger_autotrade_or_broker",
)

_FORBIDDEN_TRUE_FLAGS = (
    "ready_for_warroom_ui_mount",
    "streamlit_import_required",
    "ui_controls_added",
    "ui_triggered_loader_execution",
    "observation_command_executed_by_this_parser",
    "loader_execution_requested",
    "actual_file_read_performed_by_this_parser",
    "payload_decode_performed_by_this_parser",
    "warroom_page_mutation_allowed",
    "warroom_panel_mutation_allowed",
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
class PredictionWarRoomActualObservationUiHandoffReadinessContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    readiness_sequence: Tuple[str, ...] = ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_SEQUENCE
    parser_version: str = ""
    parser_state: str = ""
    parser_packet_present: bool = False
    parser_packet_version_valid: bool = False
    parser_ready_for_real_payload_ui_handoff_consideration: bool = False
    parser_ready_for_real_payload_review_handoff: bool = False
    parser_safety_flags_all_false: bool = False
    parser_loaded_payload_count: int = 0
    parser_runner_state: str = ""
    parser_composition_state: str = ""
    ready_for_future_warroom_layout_review: bool = False
    ready_for_future_top_default_expanded_review: bool = False
    ready_for_warroom_ui_mount: bool = False
    top_default_expanded_application_allowed: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
    page_patch_included: bool = False
    panel_patch_included: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    readiness_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    supplied_parser_packet_only: bool = True
    ui_handoff_readiness_only: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
    observation_command_executed_by_this_contract: bool = False
    stdout_parser_executed_by_this_contract: bool = False
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
            "readiness_sequence": list(self.readiness_sequence),
            "parser_version": self.parser_version,
            "parser_state": self.parser_state,
            "parser_packet_present": self.parser_packet_present,
            "parser_packet_version_valid": self.parser_packet_version_valid,
            "parser_ready_for_real_payload_ui_handoff_consideration": self.parser_ready_for_real_payload_ui_handoff_consideration,
            "parser_ready_for_real_payload_review_handoff": self.parser_ready_for_real_payload_review_handoff,
            "parser_safety_flags_all_false": self.parser_safety_flags_all_false,
            "parser_loaded_payload_count": self.parser_loaded_payload_count,
            "parser_runner_state": self.parser_runner_state,
            "parser_composition_state": self.parser_composition_state,
            "ready_for_future_warroom_layout_review": self.ready_for_future_warroom_layout_review,
            "ready_for_future_top_default_expanded_review": self.ready_for_future_top_default_expanded_review,
            "ready_for_warroom_ui_mount": self.ready_for_warroom_ui_mount,
            "top_default_expanded_application_allowed": self.top_default_expanded_application_allowed,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
            "page_patch_included": self.page_patch_included,
            "panel_patch_included": self.panel_patch_included,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "readiness_summary": dict(self.readiness_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "supplied_parser_packet_only": self.supplied_parser_packet_only,
            "ui_handoff_readiness_only": self.ui_handoff_readiness_only,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
            "observation_command_executed_by_this_contract": self.observation_command_executed_by_this_contract,
            "stdout_parser_executed_by_this_contract": self.stdout_parser_executed_by_this_contract,
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


def build_prediction_warroom_actual_observation_ui_handoff_readiness_contract(
    *,
    parser_packet: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomActualObservationUiHandoffReadinessContractPacket:
    """Build PS-Q9T readiness data from a supplied PS-Q9S parser packet only."""
    parser = _as_mapping(parser_packet)
    blockers: list[str] = []
    warnings: list[str] = []
    if not parser:
        blockers.append("ps_q9s_parser_packet_required")
    version_valid = parser.get("parser_version") == ACTUAL_OBSERVATION_STDOUT_REVIEW_PARSER_VERSION
    if parser and not version_valid:
        blockers.append("ps_q9s_parser_version_invalid")
    unsafe_flags = _unsafe_true_flags(parser)
    blockers.extend("ps_q9s_parser_unsafe_true_flag:" + item for item in unsafe_flags)
    parser_blockers = parser.get("blocked_reasons") if isinstance(parser.get("blocked_reasons"), (list, tuple)) else ()
    parser_warnings = parser.get("warning_reasons") if isinstance(parser.get("warning_reasons"), (list, tuple)) else ()
    if parser_blockers:
        blockers.append("ps_q9s_parser_blockers_present")
    if parser_warnings:
        warnings.append("ps_q9s_parser_warnings_present")
    parser_state = str(parser.get("parser_state") or "")
    parser_ready_consideration = parser.get("ready_for_real_payload_ui_handoff_consideration") is True
    parser_real_ready = parser.get("ready_for_real_payload_review_handoff") is True
    parser_safety = parser.get("safety_flags_all_false") is True
    loaded_count = int(parser.get("loaded_payload_count") or 0)
    if parser and parser_state != "actual_observation_stdout_review_ready_for_ui_handoff_consideration":
        blockers.append("ps_q9s_parser_state_not_ready")
    if parser and not parser_ready_consideration:
        blockers.append("ps_q9s_parser_not_ready_for_ui_handoff_consideration")
    if parser and not parser_real_ready:
        blockers.append("ps_q9s_parser_real_payload_review_handoff_not_ready")
    if parser and not parser_safety:
        blockers.append("ps_q9s_parser_safety_flags_not_all_false")
    if parser and loaded_count <= 0:
        blockers.append("ps_q9s_parser_loaded_payload_count_not_positive")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(parser) and not unique_blockers
    state = "actual_observation_ui_handoff_ready_for_layout_review" if ready else "actual_observation_ui_handoff_readiness_blocked"
    return PredictionWarRoomActualObservationUiHandoffReadinessContractPacket(
        contract_version=ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_OBSERVATION_UI_HANDOFF_READINESS_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        parser_version=str(parser.get("parser_version") or ""),
        parser_state=parser_state,
        parser_packet_present=bool(parser),
        parser_packet_version_valid=version_valid,
        parser_ready_for_real_payload_ui_handoff_consideration=parser_ready_consideration,
        parser_ready_for_real_payload_review_handoff=parser_real_ready,
        parser_safety_flags_all_false=parser_safety,
        parser_loaded_payload_count=loaded_count,
        parser_runner_state=str(parser.get("runner_state") or ""),
        parser_composition_state=str(parser.get("composition_state") or ""),
        ready_for_future_warroom_layout_review=ready,
        ready_for_future_top_default_expanded_review=ready,
        ready_for_warroom_ui_mount=False,
        top_default_expanded_application_allowed=False,
        warroom_page_mutation_allowed=False,
        warroom_panel_mutation_allowed=False,
        page_patch_included=False,
        panel_patch_included=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        readiness_summary={
            "boundary": "ps_q9t_supplied_parser_packet_ui_handoff_readiness_contract_only",
            "ready_for_future_warroom_layout_review": ready,
            "ready_for_future_top_default_expanded_review": ready,
            "ready_for_warroom_ui_mount": False,
            "top_default_expanded_application_allowed": False,
            "warroom_page_mutation_allowed": False,
            "warroom_panel_mutation_allowed": False,
            "page_patch_included": False,
            "panel_patch_included": False,
            "stdout_parser_executed_by_this_contract": False,
            "loader_execution_requested": False,
            "runtime_artifact_write_allowed": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )
