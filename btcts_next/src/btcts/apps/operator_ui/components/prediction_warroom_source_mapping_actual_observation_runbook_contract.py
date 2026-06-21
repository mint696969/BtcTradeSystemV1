# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_source_mapping_actual_observation_runbook_contract.py
# desc: PS-Q10C contract-only operator-shell runbook for observing PS-Q10B source mapping probe stdout against D-hot. It generates a stdout-only manual command and does not run reads, build predictions, export artifacts, mutate UI/runtime state, approve, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT
from .prediction_warroom_source_mapping_probe_runner import SOURCE_MAPPING_PROBE_RUNNER_VERSION

SOURCE_MAPPING_ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION = "prediction_warroom_source_mapping_actual_observation_runbook_contract.ps_q10c.v1"
EXPECTED_STDOUT_MARKERS = (
    "prediction_source_mapping_probe_runner=",
    "state=",
    "market_overview_tail_rows=",
    "market_trade_tail_rows=",
    "orderbook_snapshot_tail_rows=",
    "normalized_ohlcv_rows=",
    "ready_for_future_prediction_system_result_builder=",
    "ready_for_latest_payload_export=False",
    "ui=false;runtime_write=false;prediction_build=false;export=false;approval=false;ledger=false;autotrade=false;broker=false",
)
REQUIRED_OPERATOR_REVIEW_ITEMS = (
    "runner_version_marker",
    "runner_state",
    "market_overview_tail_rows",
    "market_trade_tail_rows",
    "normalized_ohlcv_rows",
    "ready_for_future_prediction_system_result_builder",
    "blockers",
    "warnings",
    "safety_flags_all_false",
)
SOURCE_MAPPING_ACTUAL_OBSERVATION_RUNBOOK_SEQUENCE = (
    "declare_contract_only_non_ui_source_mapping_observation_runbook",
    "require_operator_acknowledgement_before_command_use",
    "generate_stdout_only_python_command_for_ps_q10b_runner",
    "include_pythonpath_for_btcts_next_src",
    "require_clean_working_tree_before_manual_observation",
    "require_hot_latest_root_under_d_btc_ts_hot",
    "require_operator_to_paste_stdout_back_for_review",
    "forbid_prediction_build_and_latest_payload_export",
    "forbid_warroom_ui_mount_or_page_panel_mutation",
    "forbid_runtime_artifact_write_and_ledger_append",
    "forbid_autotrade_and_broker_controls",
    "return_runbook_contract_only",
)


@dataclass(frozen=True)
class PredictionWarRoomSourceMappingActualObservationRunbookContract:
    contract_version: str
    contract_id: str
    contract_state: str
    hot_latest_root_hint: str
    runner_version_expected: str = SOURCE_MAPPING_PROBE_RUNNER_VERSION
    runbook_sequence: Tuple[str, ...] = SOURCE_MAPPING_ACTUAL_OBSERVATION_RUNBOOK_SEQUENCE
    expected_stdout_markers: Tuple[str, ...] = EXPECTED_STDOUT_MARKERS
    required_operator_review_items: Tuple[str, ...] = REQUIRED_OPERATOR_REVIEW_ITEMS
    operator_acknowledged: bool = False
    command_generated: bool = False
    command_allowed_for_manual_shell_use: bool = False
    ready_for_manual_non_ui_observation: bool = False
    generated_powershell_lines: Tuple[str, ...] = ()
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    runbook_only: bool = True
    stdout_capture_contract_only: bool = True
    command_must_be_run_from_operator_shell: bool = True
    command_must_not_be_run_from_warroom_ui: bool = True
    command_must_remain_stdout_only: bool = True
    command_must_not_write_files: bool = True
    command_must_not_append_ledgers: bool = True
    command_must_not_trigger_trade: bool = True
    actual_runner_executed_by_this_contract: bool = False
    actual_observation_performed_by_this_contract: bool = False
    actual_file_read_performed_by_this_contract: bool = False
    payload_decode_performed_by_this_contract: bool = False
    prediction_system_result_built_by_this_contract: bool = False
    latest_prediction_artifact_exported_by_this_contract: bool = False
    runtime_artifact_write_allowed: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_runner_execution: bool = False
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
    runbook_summary: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "contract_id": self.contract_id,
            "contract_state": self.contract_state,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "runner_version_expected": self.runner_version_expected,
            "runbook_sequence": list(self.runbook_sequence),
            "expected_stdout_markers": list(self.expected_stdout_markers),
            "required_operator_review_items": list(self.required_operator_review_items),
            "operator_acknowledged": self.operator_acknowledged,
            "command_generated": self.command_generated,
            "command_allowed_for_manual_shell_use": self.command_allowed_for_manual_shell_use,
            "ready_for_manual_non_ui_observation": self.ready_for_manual_non_ui_observation,
            "generated_powershell_lines": list(self.generated_powershell_lines),
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "runbook_only": self.runbook_only,
            "stdout_capture_contract_only": self.stdout_capture_contract_only,
            "command_must_be_run_from_operator_shell": self.command_must_be_run_from_operator_shell,
            "command_must_not_be_run_from_warroom_ui": self.command_must_not_be_run_from_warroom_ui,
            "command_must_remain_stdout_only": self.command_must_remain_stdout_only,
            "command_must_not_write_files": self.command_must_not_write_files,
            "command_must_not_append_ledgers": self.command_must_not_append_ledgers,
            "command_must_not_trigger_trade": self.command_must_not_trigger_trade,
            "actual_runner_executed_by_this_contract": self.actual_runner_executed_by_this_contract,
            "actual_observation_performed_by_this_contract": self.actual_observation_performed_by_this_contract,
            "actual_file_read_performed_by_this_contract": self.actual_file_read_performed_by_this_contract,
            "payload_decode_performed_by_this_contract": self.payload_decode_performed_by_this_contract,
            "prediction_system_result_built_by_this_contract": self.prediction_system_result_built_by_this_contract,
            "latest_prediction_artifact_exported_by_this_contract": self.latest_prediction_artifact_exported_by_this_contract,
            "runtime_artifact_write_allowed": self.runtime_artifact_write_allowed,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_runner_execution": self.ui_triggered_runner_execution,
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
            "runbook_summary": dict(self.runbook_summary),
        }


def _root_ok(root: str) -> bool:
    normalized = str(root).rstrip("\\/").lower().replace("/", "\\")
    return normalized == "d:\\btc_ts_hot"


def _generated_command(root: str) -> tuple[str, ...]:
    return (
        "cd C:\\BtcTradeSystem",
        "$env:PYTHONPATH = \"$PWD\\btcts_next\\src\"",
        "@'",
        "from btcts.apps.operator_ui.components.prediction_warroom_source_mapping_probe_runner import (",
        "    build_prediction_warroom_source_mapping_probe_runner,",
        "    format_prediction_warroom_source_mapping_probe_runner_stdout_summary,",
        ")",
        "packet = build_prediction_warroom_source_mapping_probe_runner(",
        f"    hot_latest_root_hint=r\"{root}\",",
        "    operator_acknowledged=True,",
        "    allow_actual_read=True,",
        ")",
        "print(format_prediction_warroom_source_mapping_probe_runner_stdout_summary(packet))",
        "'@ | python -",
    )


def build_prediction_warroom_source_mapping_actual_observation_runbook_contract(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    operator_acknowledged: bool = False,
    requested_prediction_build: bool = False,
    requested_latest_payload_export: bool = False,
    requested_warroom_ui_mount: bool = False,
    requested_runtime_artifact_write: bool = False,
    requested_ledger_append: bool = False,
    requested_autotrade_or_broker: bool = False,
) -> PredictionWarRoomSourceMappingActualObservationRunbookContract:
    """Return a contract-only manual observation runbook for PS-Q10B stdout."""
    blockers: list[str] = []
    warnings: list[str] = []
    root = str(hot_latest_root_hint)
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required_before_generating_source_mapping_observation_command")
    if not _root_ok(root):
        blockers.append("hot_latest_root_must_stay_under_D_btc_ts_hot")
    if requested_prediction_build:
        blockers.append("prediction_build_not_allowed_for_source_mapping_observation")
    if requested_latest_payload_export:
        blockers.append("latest_payload_export_not_allowed_for_source_mapping_observation")
    if requested_warroom_ui_mount:
        blockers.append("warroom_ui_mount_not_allowed_for_source_mapping_observation")
    if requested_runtime_artifact_write:
        blockers.append("runtime_artifact_write_not_allowed")
    if requested_ledger_append:
        blockers.append("decision_or_command_ledger_append_not_allowed")
    if requested_autotrade_or_broker:
        blockers.append("autotrade_or_broker_not_allowed")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not unique_blockers
    command = _generated_command(root) if ready else tuple()
    state = "source_mapping_actual_observation_runbook_ready_for_manual_non_ui_shell" if ready else "source_mapping_actual_observation_runbook_blocked"
    return PredictionWarRoomSourceMappingActualObservationRunbookContract(
        contract_version=SOURCE_MAPPING_ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION,
        contract_id=f"{SOURCE_MAPPING_ACTUAL_OBSERVATION_RUNBOOK_CONTRACT_VERSION}:{state}",
        contract_state=state,
        hot_latest_root_hint=root,
        operator_acknowledged=operator_acknowledged,
        command_generated=bool(command),
        command_allowed_for_manual_shell_use=ready,
        ready_for_manual_non_ui_observation=ready,
        generated_powershell_lines=command,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        runbook_summary={
            "boundary": "ps_q10c_source_mapping_actual_observation_runbook_contract_only",
            "manual_shell_only": True,
            "generated_command_sets_pythonpath": True,
            "expected_runner_version": SOURCE_MAPPING_PROBE_RUNNER_VERSION,
            "prediction_system_result_built_by_this_contract": False,
            "latest_prediction_artifact_exported_by_this_contract": False,
            "runtime_artifact_write_allowed": False,
            "warroom_ui_mount_allowed": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )
