# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_observation_stdout_review_parser.py
# desc: PS-Q9S parser/review contract for supplied PS-Q9Q stdout text from a manual non-UI actual observation. Parses supplied text only; does not execute commands, run loaders, read files, decode payloads, render Streamlit, mutate WarRoom page/panel, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_observation_runbook_contract import (
    ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
    EXPECTED_STDOUT_MARKERS,
    REQUIRED_OPERATOR_REVIEW_ITEMS,
)
from .prediction_warroom_actual_read_operator_runner_scaffold import ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION

ACTUAL_OBSERVATION_STDOUT_REVIEW_PARSER_VERSION = "prediction_warroom_actual_observation_stdout_review_parser.ps_q9s.v1"

ACTUAL_OBSERVATION_STDOUT_REVIEW_SEQUENCE = (
    "consume_supplied_stdout_text_only",
    "parse_key_value_stdout_lines_without_running_command",
    "verify_ps_q9q_runner_version_marker",
    "verify_expected_stdout_markers",
    "verify_safety_boundary_line_all_false",
    "verify_real_payload_review_handoff_ready_before_ui_consideration",
    "return_stdout_review_packet_only",
    "do_not_run_loader_or_observation_command",
    "do_not_read_runtime_file",
    "do_not_write_runtime_artifact",
    "do_not_mutate_warroom_page_or_panel",
    "do_not_trigger_autotrade_or_broker",
)

SAFETY_BOUNDARY_LINE = "ui=false;warroom_page_mutation=false;runtime_write=false;approval=false;ledger=false;autotrade=false;broker=false"


@dataclass(frozen=True)
class PredictionWarRoomActualObservationStdoutReviewParserPacket:
    parser_version: str
    parser_id: str
    parser_state: str
    review_sequence: Tuple[str, ...] = ACTUAL_OBSERVATION_STDOUT_REVIEW_SEQUENCE
    expected_stdout_markers: Tuple[str, ...] = EXPECTED_STDOUT_MARKERS
    required_operator_review_items: Tuple[str, ...] = REQUIRED_OPERATOR_REVIEW_ITEMS
    runbook_contract_version: str = ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION
    q9q_runner_scaffold_version: str = ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION
    supplied_stdout_present: bool = False
    parsed_stdout_fields: Mapping[str, str] = field(default_factory=dict)
    stdout_line_count: int = 0
    expected_marker_count: int = 0
    observed_marker_count: int = 0
    missing_stdout_markers: Tuple[str, ...] = ()
    runner_version_marker_valid: bool = False
    runner_state: str = ""
    boundary_state: str = ""
    loader_state: str = ""
    loaded_payload_count: int = 0
    composition_state: str = ""
    ready_for_real_payload_review_handoff: bool = False
    ready_for_future_top_default_expanded_ux: bool = False
    safety_boundary_line_present: bool = False
    safety_flags_all_false: bool = False
    ready_for_real_payload_ui_handoff_consideration: bool = False
    ready_for_warroom_ui_mount: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    review_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    parser_only: bool = True
    supplied_text_only: bool = True
    stdout_review_only: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
    observation_command_executed_by_this_parser: bool = False
    loader_execution_requested: bool = False
    actual_file_read_performed_by_this_parser: bool = False
    payload_decode_performed_by_this_parser: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
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
            "parser_version": self.parser_version,
            "parser_id": self.parser_id,
            "parser_state": self.parser_state,
            "review_sequence": list(self.review_sequence),
            "expected_stdout_markers": list(self.expected_stdout_markers),
            "required_operator_review_items": list(self.required_operator_review_items),
            "runbook_contract_version": self.runbook_contract_version,
            "q9q_runner_scaffold_version": self.q9q_runner_scaffold_version,
            "supplied_stdout_present": self.supplied_stdout_present,
            "parsed_stdout_fields": dict(self.parsed_stdout_fields),
            "stdout_line_count": self.stdout_line_count,
            "expected_marker_count": self.expected_marker_count,
            "observed_marker_count": self.observed_marker_count,
            "missing_stdout_markers": list(self.missing_stdout_markers),
            "runner_version_marker_valid": self.runner_version_marker_valid,
            "runner_state": self.runner_state,
            "boundary_state": self.boundary_state,
            "loader_state": self.loader_state,
            "loaded_payload_count": self.loaded_payload_count,
            "composition_state": self.composition_state,
            "ready_for_real_payload_review_handoff": self.ready_for_real_payload_review_handoff,
            "ready_for_future_top_default_expanded_ux": self.ready_for_future_top_default_expanded_ux,
            "safety_boundary_line_present": self.safety_boundary_line_present,
            "safety_flags_all_false": self.safety_flags_all_false,
            "ready_for_real_payload_ui_handoff_consideration": self.ready_for_real_payload_ui_handoff_consideration,
            "ready_for_warroom_ui_mount": self.ready_for_warroom_ui_mount,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "review_summary": dict(self.review_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "parser_only": self.parser_only,
            "supplied_text_only": self.supplied_text_only,
            "stdout_review_only": self.stdout_review_only,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
            "observation_command_executed_by_this_parser": self.observation_command_executed_by_this_parser,
            "loader_execution_requested": self.loader_execution_requested,
            "actual_file_read_performed_by_this_parser": self.actual_file_read_performed_by_this_parser,
            "payload_decode_performed_by_this_parser": self.payload_decode_performed_by_this_parser,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
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


def _lines(stdout_text: str | None) -> tuple[str, ...]:
    if stdout_text is None:
        return ()
    return tuple(line.strip() for line in str(stdout_text).splitlines() if line.strip())


def _parse_fields(lines: tuple[str, ...]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        if "=" in line and not line.startswith("ui=false;"):
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def _bool(value: str) -> bool:
    return value.strip().lower() == "true"


def _int(value: str) -> int:
    try:
        return int(value.strip())
    except Exception:
        return 0


def _missing_markers(text: str) -> tuple[str, ...]:
    missing: list[str] = []
    for marker in EXPECTED_STDOUT_MARKERS:
        if marker.endswith("="):
            if marker not in text:
                missing.append(marker)
        elif marker not in text:
            missing.append(marker)
    return tuple(missing)


def build_prediction_warroom_actual_observation_stdout_review_parser(
    *,
    stdout_text: str | None = None,
) -> PredictionWarRoomActualObservationStdoutReviewParserPacket:
    """Parse supplied PS-Q9Q stdout text only; does not execute observation commands or read files."""
    lines = _lines(stdout_text)
    text = "\n".join(lines)
    fields = _parse_fields(lines)
    blockers: list[str] = []
    warnings: list[str] = []
    if not lines:
        blockers.append("supplied_stdout_text_required")
    missing = _missing_markers(text)
    if missing:
        blockers.append("expected_stdout_markers_missing")
    runner_marker_valid = fields.get("prediction_actual_read_runner") == ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION
    if lines and not runner_marker_valid:
        blockers.append("ps_q9q_runner_version_marker_invalid")
    safety_line_present = SAFETY_BOUNDARY_LINE in text
    if lines and not safety_line_present:
        blockers.append("safety_boundary_line_missing_or_not_all_false")
    runner_state = fields.get("state", "")
    boundary_state = fields.get("boundary_state", "")
    loader_state = fields.get("loader_state", "")
    loaded_payload_count = _int(fields.get("loaded_payload_count", "0"))
    composition_state = fields.get("composition_state", "")
    real_ready = _bool(fields.get("ready_for_real_payload_review_handoff", "False"))
    future_top_ready = _bool(fields.get("ready_for_future_top_default_expanded_ux", "False"))
    if lines and runner_state != "actual_read_operator_runner_scaffold_ready":
        blockers.append("runner_state_not_ready")
    if lines and not boundary_state.endswith("ready_for_ps_q9q_non_ui_runner_scaffold"):
        blockers.append("boundary_state_not_ready")
    if lines and loaded_payload_count <= 0:
        blockers.append("loaded_payload_count_not_positive")
    if lines and composition_state != "actual_read_review_composition_ready":
        blockers.append("composition_state_not_ready")
    if lines and not real_ready:
        blockers.append("real_payload_review_handoff_not_ready")
    if future_top_ready:
        blockers.append("future_top_default_expanded_ux_should_remain_false")
    if lines and fields.get("blockers", ""):
        blockers.append("stdout_reported_blockers_present")
    if lines and fields.get("warnings", ""):
        warnings.append("stdout_reported_warnings_present")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(lines) and not unique_blockers
    state = "actual_observation_stdout_review_ready_for_ui_handoff_consideration" if ready else "actual_observation_stdout_review_blocked"
    return PredictionWarRoomActualObservationStdoutReviewParserPacket(
        parser_version=ACTUAL_OBSERVATION_STDOUT_REVIEW_PARSER_VERSION,
        parser_id=f"{ACTUAL_OBSERVATION_STDOUT_REVIEW_PARSER_VERSION}:latest:{state}",
        parser_state=state,
        supplied_stdout_present=bool(lines),
        parsed_stdout_fields=fields,
        stdout_line_count=len(lines),
        expected_marker_count=len(EXPECTED_STDOUT_MARKERS),
        observed_marker_count=len(EXPECTED_STDOUT_MARKERS) - len(missing),
        missing_stdout_markers=missing,
        runner_version_marker_valid=runner_marker_valid,
        runner_state=runner_state,
        boundary_state=boundary_state,
        loader_state=loader_state,
        loaded_payload_count=loaded_payload_count,
        composition_state=composition_state,
        ready_for_real_payload_review_handoff=real_ready,
        ready_for_future_top_default_expanded_ux=False,
        safety_boundary_line_present=safety_line_present,
        safety_flags_all_false=safety_line_present,
        ready_for_real_payload_ui_handoff_consideration=ready,
        ready_for_warroom_ui_mount=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        review_summary={
            "boundary": "ps_q9s_supplied_stdout_review_parser_only",
            "supplied_stdout_present": bool(lines),
            "runner_version_marker_valid": runner_marker_valid,
            "safety_flags_all_false": safety_line_present,
            "ready_for_real_payload_review_handoff": real_ready,
            "ready_for_real_payload_ui_handoff_consideration": ready,
            "ready_for_warroom_ui_mount": False,
            "parser_executed_observation_command": False,
            "loader_execution_requested": False,
            "runtime_artifact_write_allowed": False,
            "warroom_page_mutation_allowed": False,
            "warroom_panel_mutation_allowed": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )
