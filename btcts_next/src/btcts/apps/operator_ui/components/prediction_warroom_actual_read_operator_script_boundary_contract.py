# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_read_operator_script_boundary_contract.py
# desc: PS-Q9P contract-only boundary for a future non-UI operator script that may explicitly observe real hot/latest Prediction WarRoom payloads. This slice does not read files, run loaders, decode payloads, render Streamlit, mutate WarRoom page/panel, write runtime artifacts, import Collector runtime, trigger AutoTrade, call broker/private APIs, grant approvals, or append ledgers.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .prediction_warroom_actual_read_review_composition_harness import ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION
from .prediction_warroom_latest_payload_actual_read_preflight_contract import ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION
from .prediction_warroom_latest_payload_read_only_loader import DEFAULT_ALLOWED_ARTIFACT_ROLES, READ_ONLY_LOADER_VERSION
from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT

ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_CONTRACT_VERSION = "prediction_warroom_actual_read_operator_script_boundary_contract.ps_q9p.v1"

ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_SEQUENCE = (
    "declare_non_ui_operator_script_boundary_contract_only",
    "require_explicit_operator_acknowledgement_before_future_runner_slice",
    "limit_future_runner_to_q9b_read_only_loader_and_q9o_composition_harness",
    "require_hot_latest_root_under_d_btc_ts_hot",
    "require_stdout_only_or_in_memory_result_observation",
    "forbid_warroom_ui_triggered_actual_read",
    "forbid_warroom_page_or_panel_mutation",
    "forbid_runtime_artifact_write_and_ledger_append",
    "forbid_autotrade_and_broker_controls",
    "return_operator_script_boundary_contract_only",
)

REQUIRED_OPERATOR_STEPS = (
    "confirm_working_tree_clean_before_actual_observation",
    "run_non_ui_script_from_operator_shell_only",
    "use_hot_latest_root_D_btc_ts_hot_only",
    "observe_stdout_summary_before_any_ui_handoff",
    "keep_warroom_page_and_panel_unchanged",
    "do_not_grant_approval_or_authorization",
    "do_not_append_decision_or_command_ledger",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReadOperatorScriptBoundaryContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    hot_latest_root_hint: str
    allowed_artifact_roles: Tuple[str, ...]
    boundary_sequence: Tuple[str, ...] = ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_SEQUENCE
    required_operator_steps: Tuple[str, ...] = REQUIRED_OPERATOR_STEPS
    q9a_preflight_contract_version: str = ACTUAL_READ_PREFLIGHT_CONTRACT_VERSION
    q9b_loader_version: str = READ_ONLY_LOADER_VERSION
    q9o_composition_harness_version: str = ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    future_non_ui_runner_scaffold_allowed: bool = False
    future_runner_must_stay_non_ui: bool = True
    future_runner_must_use_q9b_loader: bool = True
    future_runner_must_use_q9o_harness: bool = True
    future_runner_output_mode: str = "stdout_or_in_memory_only"
    ready_for_ps_q9q_non_ui_runner_scaffold: bool = False
    ready_for_warroom_ui_mount: bool = False
    actual_runner_included: bool = False
    actual_observation_performed: bool = False
    actual_file_read_performed_by_this_contract: bool = False
    payload_decode_performed_by_this_contract: bool = False
    loader_execution_performed_by_this_contract: bool = False
    ui_triggered_loader_execution: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
    runtime_artifact_write_allowed: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    boundary_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    preflight_only: bool = True
    non_ui_operator_script_boundary_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
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
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "allowed_artifact_roles": list(self.allowed_artifact_roles),
            "boundary_sequence": list(self.boundary_sequence),
            "required_operator_steps": list(self.required_operator_steps),
            "q9a_preflight_contract_version": self.q9a_preflight_contract_version,
            "q9b_loader_version": self.q9b_loader_version,
            "q9o_composition_harness_version": self.q9o_composition_harness_version,
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "future_non_ui_runner_scaffold_allowed": self.future_non_ui_runner_scaffold_allowed,
            "future_runner_must_stay_non_ui": self.future_runner_must_stay_non_ui,
            "future_runner_must_use_q9b_loader": self.future_runner_must_use_q9b_loader,
            "future_runner_must_use_q9o_harness": self.future_runner_must_use_q9o_harness,
            "future_runner_output_mode": self.future_runner_output_mode,
            "ready_for_ps_q9q_non_ui_runner_scaffold": self.ready_for_ps_q9q_non_ui_runner_scaffold,
            "ready_for_warroom_ui_mount": self.ready_for_warroom_ui_mount,
            "actual_runner_included": self.actual_runner_included,
            "actual_observation_performed": self.actual_observation_performed,
            "actual_file_read_performed_by_this_contract": self.actual_file_read_performed_by_this_contract,
            "payload_decode_performed_by_this_contract": self.payload_decode_performed_by_this_contract,
            "loader_execution_performed_by_this_contract": self.loader_execution_performed_by_this_contract,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
            "runtime_artifact_write_allowed": self.runtime_artifact_write_allowed,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "boundary_summary": dict(self.boundary_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "preflight_only": self.preflight_only,
            "non_ui_operator_script_boundary_only": self.non_ui_operator_script_boundary_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
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


def _roles(value: Iterable[str] | None) -> tuple[str, ...]:
    roles = tuple(str(item) for item in (value or DEFAULT_ALLOWED_ARTIFACT_ROLES) if str(item))
    return roles or tuple(DEFAULT_ALLOWED_ARTIFACT_ROLES)


def _under_hot_root(value: str) -> bool:
    normalized = value.replace("/", "\\").rstrip("\\")
    root = DEFAULT_HOT_LATEST_ROOT_HINT.replace("/", "\\").rstrip("\\")
    return normalized == root or normalized.startswith(root + "\\")


def build_prediction_warroom_actual_read_operator_script_boundary_contract(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    allowed_artifact_roles: Iterable[str] | None = None,
    operator_acknowledged: bool = False,
    requested_output_mode: str = "stdout_or_in_memory_only",
    requested_ui_mount: bool = False,
    requested_warroom_page_mutation: bool = False,
    requested_warroom_panel_mutation: bool = False,
    requested_runtime_artifact_write: bool = False,
    requested_approval_or_authorization: bool = False,
    requested_ledger_append: bool = False,
    requested_autotrade_or_broker: bool = False,
) -> PredictionWarRoomActualReadOperatorScriptBoundaryContractPacket:
    """Build PS-Q9P boundary data for a future explicit non-UI actual-read runner slice."""
    blockers: list[str] = []
    warnings: list[str] = []
    root = str(hot_latest_root_hint or "")
    roles = _roles(allowed_artifact_roles)
    output_mode = str(requested_output_mode or "")
    if not _under_hot_root(root):
        blockers.append("hot_latest_root_must_stay_under_D_btc_ts_hot")
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required_before_non_ui_runner_scaffold")
    if output_mode not in {"stdout_or_in_memory_only", "stdout_only", "in_memory_only"}:
        blockers.append("future_runner_output_must_be_stdout_or_in_memory_only")
    if requested_ui_mount:
        blockers.append("warroom_ui_mount_not_allowed_for_actual_read_runner")
    if requested_warroom_page_mutation:
        blockers.append("warroom_page_mutation_not_allowed")
    if requested_warroom_panel_mutation:
        blockers.append("warroom_panel_mutation_not_allowed")
    if requested_runtime_artifact_write:
        blockers.append("runtime_artifact_write_not_allowed")
    if requested_approval_or_authorization:
        blockers.append("approval_or_authorization_not_allowed")
    if requested_ledger_append:
        blockers.append("decision_or_command_ledger_append_not_allowed")
    if requested_autotrade_or_broker:
        blockers.append("autotrade_or_broker_not_allowed")
    if roles != ("prediction_system_result_snapshot",):
        warnings.append("non_default_artifact_roles_require_extra_review_before_runner_scaffold")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not unique_blockers
    state = "operator_script_boundary_ready_for_ps_q9q_non_ui_runner_scaffold" if ready else "operator_script_boundary_blocked"
    return PredictionWarRoomActualReadOperatorScriptBoundaryContractPacket(
        contract_version=ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_CONTRACT_VERSION,
        contract_id=f"{ACTUAL_READ_OPERATOR_SCRIPT_BOUNDARY_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        hot_latest_root_hint=root,
        allowed_artifact_roles=roles,
        operator_acknowledged=operator_acknowledged,
        future_non_ui_runner_scaffold_allowed=ready,
        future_runner_output_mode=output_mode,
        ready_for_ps_q9q_non_ui_runner_scaffold=ready,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        boundary_summary={
            "boundary": "ps_q9p_non_ui_operator_script_contract_only",
            "future_runner_scaffold_allowed": ready,
            "future_runner_must_use_q9a_preflight": True,
            "future_runner_must_use_q9b_loader": True,
            "future_runner_must_use_q9o_harness": True,
            "future_runner_output_mode": output_mode,
            "actual_runner_included": False,
            "actual_observation_performed": False,
            "warroom_ui_mount_allowed": False,
            "warroom_page_mutation_allowed": False,
            "warroom_panel_mutation_allowed": False,
            "runtime_artifact_write_allowed": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )
