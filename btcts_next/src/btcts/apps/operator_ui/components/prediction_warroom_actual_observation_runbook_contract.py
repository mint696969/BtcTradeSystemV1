# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_observation_runbook_contract.py
# desc: PS-Q9R contract-only runbook for a future local non-UI stdout observation of real D:\btc_ts_hot Prediction WarRoom latest payloads. This slice does not execute the runner, read files, decode payloads, render Streamlit, mutate WarRoom page/panel, write artifacts, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_actual_read_operator_runner_scaffold import ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION
from .prediction_warroom_actual_read_operator_script_boundary_contract import ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_CONTRACT_VERSION
from .prediction_warroom_latest_payload_read_only_loader import DEFAULT_ALLOWED_ARTIFACT_ROLES, READ_ONLY_LOADER_VERSION
from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT

ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION = "prediction_warroom_actual_observation_runbook_contract.ps_q9r.v1"

ACTUAL_OBSERVATION_RUNBOOK_SEQUENCE = (
    "declare_contract_only_non_ui_actual_observation_runbook",
    "require_operator_acknowledgement_before_command_use",
    "generate_stdout_only_python_command_for_ps_q9q_runner",
    "require_clean_working_tree_before_manual_observation",
    "require_hot_latest_root_under_d_btc_ts_hot",
    "require_operator_to_paste_stdout_back_for_review",
    "forbid_warroom_ui_mount_or_page_panel_mutation",
    "forbid_runtime_artifact_write_and_ledger_append",
    "forbid_autotrade_and_broker_controls",
    "return_runbook_contract_only",
)

EXPECTED_STDOUT_MARKERS = (
    "prediction_actual_read_runner=prediction_warroom_actual_read_operator_runner_scaffold.ps_q9q.v1",
    "state=",
    "boundary_state=",
    "loader_state=",
    "loaded_payload_count=",
    "composition_state=",
    "ready_for_real_payload_review_handoff=",
    "ready_for_future_top_default_expanded_ux=False",
    "ui=false;warroom_page_mutation=false;runtime_write=false;approval=false;ledger=false;autotrade=false;broker=false",
)

REQUIRED_OPERATOR_REVIEW_ITEMS = (
    "runner_state",
    "boundary_state",
    "loader_state",
    "loaded_payload_count",
    "composition_state",
    "ready_for_real_payload_review_handoff",
    "blockers",
    "warnings",
    "safety_flags_all_false",
)


@dataclass(frozen=True)
class PredictionWarRoomActualObservationRunbookContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    hot_latest_root_hint: str
    allowed_artifact_roles: Tuple[str, ...]
    runbook_sequence: Tuple[str, ...] = ACTUAL_OBSERVATION_RUNBOOK_SEQUENCE
    expected_stdout_markers: Tuple[str, ...] = EXPECTED_STDOUT_MARKERS
    required_operator_review_items: Tuple[str, ...] = REQUIRED_OPERATOR_REVIEW_ITEMS
    q9p_boundary_contract_version: str = ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_CONTRACT_VERSION
    q9q_runner_scaffold_version: str = ACTUAL_READ_OPERATOR_RUNNER_SCAFFOLD_VERSION
    q9b_loader_version: str = READ_ONLY_LOADER_VERSION
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    command_generated: bool = False
    command_allowed_for_manual_shell_use: bool = False
    command_must_be_run_from_operator_shell: bool = True
    command_must_not_be_run_from_warroom_ui: bool = True
    command_must_remain_stdout_only: bool = True
    command_must_not_write_files: bool = True
    command_must_not_append_ledgers: bool = True
    command_must_not_trigger_trade: bool = True
    generated_powershell_lines: Tuple[str, ...] = ()
    generated_python_snippet: Tuple[str, ...] = ()
    ready_for_manual_non_ui_observation: bool = False
    ready_for_warroom_ui_mount: bool = False
    actual_runner_executed_by_this_contract: bool = False
    actual_observation_performed_by_this_contract: bool = False
    actual_file_read_performed_by_this_contract: bool = False
    payload_decode_performed_by_this_contract: bool = False
    runtime_artifact_write_allowed: bool = False
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
    stdout_capture_contract_only: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
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
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "allowed_artifact_roles": list(self.allowed_artifact_roles),
            "runbook_sequence": list(self.runbook_sequence),
            "expected_stdout_markers": list(self.expected_stdout_markers),
            "required_operator_review_items": list(self.required_operator_review_items),
            "q9p_boundary_contract_version": self.q9p_boundary_contract_version,
            "q9q_runner_scaffold_version": self.q9q_runner_scaffold_version,
            "q9b_loader_version": self.q9b_loader_version,
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "command_generated": self.command_generated,
            "command_allowed_for_manual_shell_use": self.command_allowed_for_manual_shell_use,
            "command_must_be_run_from_operator_shell": self.command_must_be_run_from_operator_shell,
            "command_must_not_be_run_from_warroom_ui": self.command_must_not_be_run_from_warroom_ui,
            "command_must_remain_stdout_only": self.command_must_remain_stdout_only,
            "command_must_not_write_files": self.command_must_not_write_files,
            "command_must_not_append_ledgers": self.command_must_not_append_ledgers,
            "command_must_not_trigger_trade": self.command_must_not_trigger_trade,
            "generated_powershell_lines": list(self.generated_powershell_lines),
            "generated_python_snippet": list(self.generated_python_snippet),
            "ready_for_manual_non_ui_observation": self.ready_for_manual_non_ui_observation,
            "ready_for_warroom_ui_mount": self.ready_for_warroom_ui_mount,
            "actual_runner_executed_by_this_contract": self.actual_runner_executed_by_this_contract,
            "actual_observation_performed_by_this_contract": self.actual_observation_performed_by_this_contract,
            "actual_file_read_performed_by_this_contract": self.actual_file_read_performed_by_this_contract,
            "payload_decode_performed_by_this_contract": self.payload_decode_performed_by_this_contract,
            "runtime_artifact_write_allowed": self.runtime_artifact_write_allowed,
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
            "stdout_capture_contract_only": self.stdout_capture_contract_only,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
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


def _roles(value: Iterable[str] | None) -> tuple[str, ...]:
    roles = tuple(str(item) for item in (value or DEFAULT_ALLOWED_ARTIFACT_ROLES) if str(item))
    return roles or tuple(DEFAULT_ALLOWED_ARTIFACT_ROLES)


def _under_hot_root(value: str) -> bool:
    normalized = value.replace("/", "\\").rstrip("\\")
    root = DEFAULT_HOT_LATEST_ROOT_HINT.replace("/", "\\").rstrip("\\")
    return normalized == root or normalized.startswith(root + "\\")


def _python_snippet(root: str, roles: tuple[str, ...]) -> tuple[str, ...]:
    role_literal = "(" + ", ".join(repr(item) for item in roles) + ("," if len(roles) == 1 else "") + ")"
    return (
        "from btcts.apps.operator_ui.components.prediction_warroom_actual_read_operator_runner_scaffold import build_prediction_warroom_actual_read_operator_runner_scaffold, format_prediction_warroom_actual_read_operator_runner_stdout_summary",
        "packet = build_prediction_warroom_actual_read_operator_runner_scaffold(operator_acknowledged=True, execute_actual_read=True, hot_latest_root_hint=" + repr(root) + ", allowed_artifact_roles=" + role_literal + ")",
        "print(format_prediction_warroom_actual_read_operator_runner_stdout_summary(packet.to_dict()))",
    )


def _powershell_lines(root: str, roles: tuple[str, ...]) -> tuple[str, ...]:
    snippet = "; ".join(_python_snippet(root, roles))
    return (
        "cd C:\\BtcTradeSystem",
        "# hot_latest_root_hint=" + root,
        "python -c " + repr(snippet),
    )


def build_prediction_warroom_actual_observation_runbook_contract(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    allowed_artifact_roles: Iterable[str] | None = None,
    operator_acknowledged: bool = False,
    requested_warroom_ui_mount: bool = False,
    requested_runtime_artifact_write: bool = False,
    requested_ledger_append: bool = False,
    requested_autotrade_or_broker: bool = False,
) -> PredictionWarRoomActualObservationRunbookContractPacket:
    """Build a contract-only non-UI runbook for manual stdout observation; does not execute the command."""
    root = str(hot_latest_root_hint or "")
    roles = _roles(allowed_artifact_roles)
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required_before_generating_manual_observation_command")
    if not _under_hot_root(root):
        blockers.append("hot_latest_root_must_stay_under_D_btc_ts_hot")
    if requested_warroom_ui_mount:
        blockers.append("warroom_ui_mount_not_allowed_for_actual_observation")
    if requested_runtime_artifact_write:
        blockers.append("runtime_artifact_write_not_allowed")
    if requested_ledger_append:
        blockers.append("decision_or_command_ledger_append_not_allowed")
    if requested_autotrade_or_broker:
        blockers.append("autotrade_or_broker_not_allowed")
    if roles != ("prediction_system_result_snapshot",):
        warnings.append("non_default_artifact_roles_require_extra_review_before_manual_observation")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not unique_blockers
    state = "actual_observation_runbook_ready_for_manual_non_ui_shell" if ready else "actual_observation_runbook_blocked"
    powershell = _powershell_lines(root, roles) if ready else ()
    python_lines = _python_snippet(root, roles) if ready else ()
    return PredictionWarRoomActualObservationRunbookContractPacket(
        contract_version=ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        hot_latest_root_hint=root,
        allowed_artifact_roles=roles,
        operator_acknowledged=operator_acknowledged,
        command_generated=ready,
        command_allowed_for_manual_shell_use=ready,
        generated_powershell_lines=powershell,
        generated_python_snippet=python_lines,
        ready_for_manual_non_ui_observation=ready,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        runbook_summary={
            "boundary": "ps_q9r_contract_only_manual_non_ui_actual_observation_runbook",
            "command_generated": ready,
            "command_execution_performed_by_this_contract": False,
            "operator_must_paste_stdout_back_for_review": True,
            "expected_stdout_markers": list(EXPECTED_STDOUT_MARKERS),
            "ready_for_warroom_ui_mount": False,
            "warroom_page_mutation_allowed": False,
            "warroom_panel_mutation_allowed": False,
            "runtime_artifact_write_allowed": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )
