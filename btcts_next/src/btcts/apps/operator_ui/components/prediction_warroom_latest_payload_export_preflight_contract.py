# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_preflight_contract.py
# desc: PS-Q9X contract-only preflight for a future non-UI export of a supplied PredictionSystemResult mapping to the D:\btc_ts_hot Prediction WarRoom latest artifact path. Does not build predictions, write files, create directories, read hot files, decode payloads, render Streamlit, mutate WarRoom page/panel, grant approvals, append ledgers, trigger AutoTrade, or call broker/private APIs.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT

LATEST_PAYLOAD_EXPORT_PREFLIGHT_CONTRACT_VERSION = "prediction_warroom_latest_payload_export_preflight_contract.ps_q9x.v1"
TARGET_ARTIFACT_ROLE = "prediction_system_result_snapshot"
TARGET_ARTIFACT_RELATIVE_PATH = "prediction\\latest_prediction_system_result.json"
TARGET_ARTIFACT_PATH_HINT = DEFAULT_HOT_LATEST_ROOT_HINT + "\\" + TARGET_ARTIFACT_RELATIVE_PATH

LATEST_PAYLOAD_EXPORT_PREFLIGHT_SEQUENCE = (
    "consume_supplied_prediction_system_result_mapping_only",
    "verify_target_hot_root_under_d_btc_ts_hot",
    "verify_target_role_prediction_system_result_snapshot",
    "verify_required_result_identity_fields",
    "record_observed_missing_hot_prediction_directory_context",
    "declare_future_non_ui_export_runner_requirements",
    "keep_runtime_artifact_write_false_in_this_contract",
    "keep_warroom_ui_trigger_false",
    "keep_approval_ledger_autotrade_broker_false",
    "return_export_preflight_contract_only",
)

REQUIRED_RESULT_FIELDS = (
    "run_identity",
    "system_input",
    "outputs",
    "scenario_core",
    "gpt_review_digest",
)

REQUIRED_RUN_IDENTITY_FIELDS = (
    "prediction_run_id",
    "generated_at",
    "market_uid",
)

FUTURE_EXPORT_REQUIREMENTS = (
    "operator_acknowledged_non_ui_export",
    "working_tree_clean_before_export",
    "target_root_D_btc_ts_hot_only",
    "create_prediction_directory_only_in_future_export_runner",
    "write_latest_prediction_system_result_json_only_in_future_export_runner",
    "write_utf8_json_atomically_or_fail_closed_in_future_export_runner",
    "emit_stdout_summary_after_future_export_runner",
    "do_not_run_from_warroom_ui",
    "do_not_append_ledgers_or_grant_approval",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLatestPayloadExportPreflightContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    target_artifact_role: str = TARGET_ARTIFACT_ROLE
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT
    target_artifact_relative_path: str = TARGET_ARTIFACT_RELATIVE_PATH
    target_artifact_path_hint: str = TARGET_ARTIFACT_PATH_HINT
    preflight_sequence: Tuple[str, ...] = LATEST_PAYLOAD_EXPORT_PREFLIGHT_SEQUENCE
    required_result_fields: Tuple[str, ...] = REQUIRED_RESULT_FIELDS
    required_run_identity_fields: Tuple[str, ...] = REQUIRED_RUN_IDENTITY_FIELDS
    future_export_requirements: Tuple[str, ...] = FUTURE_EXPORT_REQUIREMENTS
    prediction_result_payload_present: bool = False
    prediction_result_payload_type: str = "missing"
    prediction_result_payload_key_count: int = 0
    prediction_run_id: str = ""
    generated_at: str = ""
    market_uid: str = ""
    observed_hot_prediction_dir_exists: bool | None = None
    observed_expected_artifact_exists: bool | None = None
    observed_candidate_json_count: int | None = None
    operator_acknowledgement_required: bool = True
    operator_acknowledged: bool = False
    ready_for_future_non_ui_export_runner: bool = False
    ready_for_warroom_ui_mount: bool = False
    future_export_runner_required: bool = True
    actual_export_runner_included: bool = False
    runtime_artifact_write_allowed_by_this_contract: bool = False
    runtime_artifact_write_performed_by_this_contract: bool = False
    target_directory_created_by_this_contract: bool = False
    target_file_written_by_this_contract: bool = False
    hot_file_read_performed_by_this_contract: bool = False
    payload_decode_performed_by_this_contract: bool = False
    prediction_system_result_built_by_this_contract: bool = False
    warroom_page_mutation_allowed: bool = False
    warroom_panel_mutation_allowed: bool = False
    approval_or_authorization_allowed: bool = False
    ledger_append_allowed: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    preflight_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    supplied_payload_only: bool = True
    export_preflight_only: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
    ui_triggered_export_execution: bool = False
    would_collect_public_source: bool = False
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
            "target_artifact_role": self.target_artifact_role,
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "target_artifact_relative_path": self.target_artifact_relative_path,
            "target_artifact_path_hint": self.target_artifact_path_hint,
            "preflight_sequence": list(self.preflight_sequence),
            "required_result_fields": list(self.required_result_fields),
            "required_run_identity_fields": list(self.required_run_identity_fields),
            "future_export_requirements": list(self.future_export_requirements),
            "prediction_result_payload_present": self.prediction_result_payload_present,
            "prediction_result_payload_type": self.prediction_result_payload_type,
            "prediction_result_payload_key_count": self.prediction_result_payload_key_count,
            "prediction_run_id": self.prediction_run_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "observed_hot_prediction_dir_exists": self.observed_hot_prediction_dir_exists,
            "observed_expected_artifact_exists": self.observed_expected_artifact_exists,
            "observed_candidate_json_count": self.observed_candidate_json_count,
            "operator_acknowledgement_required": self.operator_acknowledgement_required,
            "operator_acknowledged": self.operator_acknowledged,
            "ready_for_future_non_ui_export_runner": self.ready_for_future_non_ui_export_runner,
            "ready_for_warroom_ui_mount": self.ready_for_warroom_ui_mount,
            "future_export_runner_required": self.future_export_runner_required,
            "actual_export_runner_included": self.actual_export_runner_included,
            "runtime_artifact_write_allowed_by_this_contract": self.runtime_artifact_write_allowed_by_this_contract,
            "runtime_artifact_write_performed_by_this_contract": self.runtime_artifact_write_performed_by_this_contract,
            "target_directory_created_by_this_contract": self.target_directory_created_by_this_contract,
            "target_file_written_by_this_contract": self.target_file_written_by_this_contract,
            "hot_file_read_performed_by_this_contract": self.hot_file_read_performed_by_this_contract,
            "payload_decode_performed_by_this_contract": self.payload_decode_performed_by_this_contract,
            "prediction_system_result_built_by_this_contract": self.prediction_system_result_built_by_this_contract,
            "warroom_page_mutation_allowed": self.warroom_page_mutation_allowed,
            "warroom_panel_mutation_allowed": self.warroom_panel_mutation_allowed,
            "approval_or_authorization_allowed": self.approval_or_authorization_allowed,
            "ledger_append_allowed": self.ledger_append_allowed,
            "autotrade_trigger_allowed": self.autotrade_trigger_allowed,
            "broker_private_api_allowed": self.broker_private_api_allowed,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "preflight_summary": dict(self.preflight_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "supplied_payload_only": self.supplied_payload_only,
            "export_preflight_only": self.export_preflight_only,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
            "ui_triggered_export_execution": self.ui_triggered_export_execution,
            "would_collect_public_source": self.would_collect_public_source,
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


def _hot_root_ok(root: str) -> bool:
    normalized = str(root).rstrip("\\/").lower().replace("/", "\\")
    return normalized == "d:\\btc_ts_hot"


def _target_path(root: str) -> str:
    return str(root).rstrip("\\/") + "\\" + TARGET_ARTIFACT_RELATIVE_PATH


def build_prediction_warroom_latest_payload_export_preflight_contract(
    *,
    prediction_result_payload: Mapping[str, Any] | Any | None = None,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    operator_acknowledged: bool = False,
    observed_hot_prediction_dir_exists: bool | None = None,
    observed_expected_artifact_exists: bool | None = None,
    observed_candidate_json_count: int | None = None,
    requested_runtime_artifact_write: bool = False,
    requested_warroom_ui_trigger: bool = False,
    requested_approval_or_authorization: bool = False,
    requested_ledger_append: bool = False,
    requested_autotrade_or_broker: bool = False,
) -> PredictionWarRoomLatestPayloadExportPreflightContractPacket:
    """Return a contract-only preflight for a future non-UI latest payload export runner."""
    payload = _as_mapping(prediction_result_payload)
    run_identity = _as_mapping(payload.get("run_identity"))
    blockers: list[str] = []
    warnings: list[str] = []
    if not operator_acknowledged:
        blockers.append("operator_acknowledgement_required_before_future_non_ui_export_runner")
    if not _hot_root_ok(hot_latest_root_hint):
        blockers.append("hot_latest_root_must_stay_under_D_btc_ts_hot")
    if not payload:
        blockers.append("prediction_system_result_payload_required_for_future_export")
    missing_fields = tuple(field for field in REQUIRED_RESULT_FIELDS if field not in payload)
    if payload and missing_fields:
        blockers.append("prediction_system_result_required_fields_missing:" + ",".join(missing_fields))
    missing_identity = tuple(field for field in REQUIRED_RUN_IDENTITY_FIELDS if not run_identity.get(field))
    if payload and missing_identity:
        blockers.append("prediction_run_identity_required_fields_missing:" + ",".join(missing_identity))
    if requested_runtime_artifact_write:
        blockers.append("runtime_artifact_write_not_allowed_by_preflight_contract_slice")
    if requested_warroom_ui_trigger:
        blockers.append("warroom_ui_trigger_not_allowed_for_latest_payload_export")
    if requested_approval_or_authorization:
        blockers.append("approval_or_authorization_not_allowed_for_latest_payload_export_preflight")
    if requested_ledger_append:
        blockers.append("ledger_append_not_allowed_for_latest_payload_export_preflight")
    if requested_autotrade_or_broker:
        blockers.append("autotrade_or_broker_not_allowed_for_latest_payload_export_preflight")
    if observed_hot_prediction_dir_exists is False:
        warnings.append("observed_hot_prediction_directory_missing_future_export_runner_must_create_it")
    if observed_expected_artifact_exists is False:
        warnings.append("observed_expected_latest_prediction_result_artifact_missing")
    if observed_candidate_json_count == 0:
        warnings.append("observed_no_prediction_latest_json_candidates_under_hot_root")
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not unique_blockers
    state = "latest_payload_export_preflight_ready_for_future_non_ui_export_runner" if ready else "latest_payload_export_preflight_blocked"
    target = _target_path(str(hot_latest_root_hint))
    return PredictionWarRoomLatestPayloadExportPreflightContractPacket(
        contract_version=LATEST_PAYLOAD_EXPORT_PREFLIGHT_CONTRACT_VERSION,
        contract_id=f"{LATEST_PAYLOAD_EXPORT_PREFLIGHT_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        target_artifact_path_hint=target,
        prediction_result_payload_present=bool(payload),
        prediction_result_payload_type=type(prediction_result_payload).__name__ if prediction_result_payload is not None else "missing",
        prediction_result_payload_key_count=len(payload),
        prediction_run_id=str(run_identity.get("prediction_run_id") or ""),
        generated_at=str(run_identity.get("generated_at") or ""),
        market_uid=str(run_identity.get("market_uid") or ""),
        observed_hot_prediction_dir_exists=observed_hot_prediction_dir_exists,
        observed_expected_artifact_exists=observed_expected_artifact_exists,
        observed_candidate_json_count=observed_candidate_json_count,
        operator_acknowledged=operator_acknowledged,
        ready_for_future_non_ui_export_runner=ready,
        ready_for_warroom_ui_mount=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        preflight_summary={
            "boundary": "ps_q9x_latest_payload_export_preflight_contract_only",
            "target_artifact_role": TARGET_ARTIFACT_ROLE,
            "target_artifact_path_hint": target,
            "future_export_runner_required": True,
            "ready_for_future_non_ui_export_runner": ready,
            "runtime_artifact_write_allowed_by_this_contract": False,
            "runtime_artifact_write_performed_by_this_contract": False,
            "target_directory_created_by_this_contract": False,
            "target_file_written_by_this_contract": False,
            "warroom_ui_trigger_allowed": False,
            "ui_controls_added": False,
            "approval_or_authorization_allowed": False,
            "ledger_append_allowed": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
        },
    )
