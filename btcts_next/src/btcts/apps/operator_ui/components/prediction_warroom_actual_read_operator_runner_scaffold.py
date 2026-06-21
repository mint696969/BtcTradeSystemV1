# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_read_operator_runner_scaffold.py
# desc: PS-Q9Q non-UI operator actual-read runner scaffold for Prediction WarRoom real latest payload observation. Uses PS-Q9P boundary, Q9B read-only loader, and Q9O composition harness; no Streamlit UI, WarRoom page/panel mutation, runtime artifact writes, Collector runtime, AutoTrade, broker/private API, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_actual_read_operator_script_boundary_contract import (
    ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_CONTRACT_VERSION,
    build_prediction_warroom_actual_read_operator_script_boundary_contract,
)
from .prediction_warroom_actual_read_review_composition_harness import (
    ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION,
    build_prediction_warroom_actual_read_review_composition_harness,
)
from .prediction_warroom_latest_payload_read_only_loader import (
    DEFAULT_ALLOWED_ARTIFACT_ROLES,
    READ_ONLY_LOADER_VERSION,
    load_prediction_warroom_latest_payload_read_only,
)
from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT

ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION = "prediction_warroom_actual_read_operator_runner_scaffold.ps_q9q.v1"

ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_SEQUENCE = (
    "build_ps_q9p_operator_script_boundary_contract",
    "require_operator_acknowledged_before_actual_read_request",
    "block_when_execute_actual_read_false",
    "use_supplied_loader_result_or_call_q9b_read_only_loader_non_ui",
    "compose_q9o_review_harness_in_memory",
    "format_stdout_only_summary",
    "return_runner_scaffold_packet_only",
    "do_not_render_streamlit",
    "do_not_mutate_warroom_page_or_panel",
    "do_not_write_runtime_artifact",
    "do_not_append_ledger_or_grant_approval",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReadOperatorRunnerScaffoldPacket:
    runner_version: str
    runner_id: str
    runner_state: str
    runner_sequence: Tuple[str, ...] = ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_SEQUENCE
    boundary_contract: Mapping[str, Any] = field(default_factory=dict)
    loader_result: Mapping[str, Any] = field(default_factory=dict)
    composition_harness: Mapping[str, Any] = field(default_factory=dict)
    stdout_summary_lines: Tuple[str, ...] = ()
    operator_acknowledged: bool = False
    execute_actual_read_requested: bool = False
    supplied_loader_result_used: bool = False
    q9b_loader_called_by_this_scaffold: bool = False
    q9o_composition_harness_called: bool = False
    ready_for_real_payload_review_handoff: bool = False
    ready_for_future_top_default_expanded_ux: bool = False
    actual_file_read_attempted: bool = False
    actual_file_read_succeeded: bool = False
    payload_decode_attempted: bool = False
    payload_decode_succeeded: bool = False
    loaded_payload_count: int = 0
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    runner_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing_trade: bool = True
    non_ui_operator_runner_scaffold_only: bool = True
    stdout_only: bool = True
    in_memory_result_only: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
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
            "runner_version": self.runner_version,
            "runner_id": self.runner_id,
            "runner_state": self.runner_state,
            "runner_sequence": list(self.runner_sequence),
            "boundary_contract": dict(self.boundary_contract),
            "loader_result": dict(self.loader_result),
            "composition_harness": dict(self.composition_harness),
            "stdout_summary_lines": list(self.stdout_summary_lines),
            "operator_acknowledged": self.operator_acknowledged,
            "execute_actual_read_requested": self.execute_actual_read_requested,
            "supplied_loader_result_used": self.supplied_loader_result_used,
            "q9b_loader_called_by_this_scaffold": self.q9b_loader_called_by_this_scaffold,
            "q9o_composition_harness_called": self.q9o_composition_harness_called,
            "ready_for_real_payload_review_handoff": self.ready_for_real_payload_review_handoff,
            "ready_for_future_top_default_expanded_ux": self.ready_for_future_top_default_expanded_ux,
            "actual_file_read_attempted": self.actual_file_read_attempted,
            "actual_file_read_succeeded": self.actual_file_read_succeeded,
            "payload_decode_attempted": self.payload_decode_attempted,
            "payload_decode_succeeded": self.payload_decode_succeeded,
            "loaded_payload_count": self.loaded_payload_count,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "runner_summary": dict(self.runner_summary),
            "read_only": self.read_only,
            "non_executing_trade": self.non_executing_trade,
            "non_ui_operator_runner_scaffold_only": self.non_ui_operator_runner_scaffold_only,
            "stdout_only": self.stdout_only,
            "in_memory_result_only": self.in_memory_result_only,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
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


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _roles(value: Iterable[str] | None) -> tuple[str, ...]:
    roles = tuple(str(item) for item in (value or DEFAULT_ALLOWED_ARTIFACT_ROLES) if str(item))
    return roles or tuple(DEFAULT_ALLOWED_ARTIFACT_ROLES)


def _stdout_lines(*, state: str, boundary: Mapping[str, Any], loader: Mapping[str, Any], harness: Mapping[str, Any], blockers: tuple[str, ...], warnings: tuple[str, ...]) -> tuple[str, ...]:
    return (
        "prediction_actual_read_runner=" + ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION,
        "state=" + state,
        "boundary_state=" + str(boundary.get("contract_state")),
        "loader_state=" + str(loader.get("loader_state")),
        "loaded_payload_count=" + str(loader.get("loaded_payload_count") or 0),
        "composition_state=" + str(harness.get("harness_state")),
        "ready_for_real_payload_review_handoff=" + str(harness.get("ready_for_real_payload_review_handoff") is True),
        "ready_for_future_top_default_expanded_ux=False",
        "blockers=" + ",".join(blockers),
        "warnings=" + ",".join(warnings),
        "ui=false;warroom_page_mutation=false;runtime_write=false;approval=false;ledger=false;autotrade=false;broker=false",
    )


def build_prediction_warroom_actual_read_operator_runner_scaffold(
    *,
    operator_acknowledged: bool = False,
    execute_actual_read: bool = False,
    supplied_loader_result: Mapping[str, Any] | Any | None = None,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    allowed_artifact_roles: Iterable[str] | None = None,
) -> PredictionWarRoomActualReadOperatorRunnerScaffoldPacket:
    """Run or dry-run a non-UI actual-read observation scaffold without UI/runtime/execution side effects."""
    roles = _roles(allowed_artifact_roles)
    boundary = build_prediction_warroom_actual_read_operator_script_boundary_contract(
        hot_latest_root_hint=hot_latest_root_hint,
        allowed_artifact_roles=roles,
        operator_acknowledged=operator_acknowledged,
        requested_output_mode="stdout_or_in_memory_only",
    ).to_dict()
    blockers: list[str] = [str(item) for item in _list(boundary.get("blocked_reasons"))]
    warnings: list[str] = [str(item) for item in _list(boundary.get("warning_reasons"))]
    supplied = _as_mapping(supplied_loader_result)
    q9b_called = False
    if not boundary.get("ready_for_ps_q9q_non_ui_runner_scaffold"):
        loader = supplied
        if not loader:
            blockers.append("ps_q9p_boundary_not_ready_no_loader_call")
    elif supplied:
        loader = supplied
        warnings.append("supplied_loader_result_used_no_actual_read_called_by_scaffold")
    elif not execute_actual_read:
        loader = {}
        blockers.append("execute_actual_read_false")
    else:
        loader = load_prediction_warroom_latest_payload_read_only(
            hot_latest_root_hint=hot_latest_root_hint,
            allowed_artifact_roles=roles,
            allow_actual_read=execute_actual_read,
        ).to_dict()
        q9b_called = True
    harness = build_prediction_warroom_actual_read_review_composition_harness(
        loader_result=loader,
    ).to_dict()
    blockers.extend(str(item) for item in _list(harness.get("blocked_reasons")) if item)
    warnings.extend(str(item) for item in _list(harness.get("warning_reasons")) if item)
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(harness.get("ready_for_real_payload_review_handoff")) and not unique_blockers
    state = "actual_read_operator_runner_scaffold_ready" if ready else "actual_read_operator_runner_scaffold_blocked"
    stdout = _stdout_lines(state=state, boundary=boundary, loader=loader, harness=harness, blockers=unique_blockers, warnings=unique_warnings)
    return PredictionWarRoomActualReadOperatorRunnerScaffoldPacket(
        runner_version=ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION,
        runner_id=f"{ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION}:latest:{state}",
        runner_state=state,
        boundary_contract=boundary,
        loader_result=loader,
        composition_harness=harness,
        stdout_summary_lines=stdout,
        operator_acknowledged=operator_acknowledged,
        execute_actual_read_requested=execute_actual_read,
        supplied_loader_result_used=bool(supplied),
        q9b_loader_called_by_this_scaffold=q9b_called,
        q9o_composition_harness_called=True,
        ready_for_real_payload_review_handoff=ready,
        ready_for_future_top_default_expanded_ux=False,
        actual_file_read_attempted=bool(loader.get("actual_file_read_attempted")),
        actual_file_read_succeeded=bool(loader.get("actual_file_read_succeeded")),
        payload_decode_attempted=bool(loader.get("payload_decode_attempted")),
        payload_decode_succeeded=bool(loader.get("payload_decode_succeeded")),
        loaded_payload_count=int(loader.get("loaded_payload_count") or 0),
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        runner_summary={
            "runner_boundary": "ps_q9q_non_ui_operator_actual_read_runner_scaffold_only",
            "q9p_boundary_contract_version": ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_CONTRACT_VERSION,
            "q9b_loader_version": READ_ONLY_LOADER_VERSION,
            "q9o_composition_harness_version": ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION,
            "q9b_loader_called_by_this_scaffold": q9b_called,
            "supplied_loader_result_used": bool(supplied),
            "stdout_only": True,
            "in_memory_result_only": True,
            "ready_for_real_payload_review_handoff": ready,
            "ready_for_future_top_default_expanded_ux": False,
            "ui_triggered_loader_execution": False,
            "warroom_page_mutation_allowed": False,
            "warroom_panel_mutation_allowed": False,
            "runtime_artifact_write_allowed": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )


def format_prediction_warroom_actual_read_operator_runner_stdout_summary(packet: Mapping[str, Any] | Any) -> str:
    """Return the PS-Q9Q stdout-only summary string without writing files or rendering UI."""
    data = _as_mapping(packet)
    lines = [str(item) for item in _list(data.get("stdout_summary_lines"))]
    if lines:
        return "\n".join(lines)
    return "prediction_actual_read_runner=" + ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION + "\nstate=missing_packet"
