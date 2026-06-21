# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_prediction_result_display_packet_lowering_contract.py
# desc: PS-Q9D PredictionSystemResult-to-WarRoom-display-packet lowering contract/readiness. Declares source-to-display field mapping and readiness only; no file reads, payload decode, actual display packet generation, rendering, WarRoom mutation, runtime writes, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_loaded_payload_schema_validation_result_panel import LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION
from .prediction_warroom_payload_schema_validator import DISPLAY_PACKET_VERSION, VALIDATOR_VERSION

PREDICTION_RESULT_DISPLAY_PACKET_LOWERING_CONTRACT_VERSION = "prediction_warroom_prediction_result_display_packet_lowering_contract.ps_q9d.v1"

DISPLAY_PACKET_REQUIRED_SECTIONS = (
    "packet_version",
    "packet_id",
    "generated_at",
    "market_uid",
    "prediction_run_id",
    "primary_signal_summary",
    "horizon_cards",
    "family_cards",
    "source_quality_panel",
    "warning_panel",
    "ui_contract",
    "boundaries",
)

LOWERING_SEQUENCE = (
    "consume_ps_q9c_validation_panel_result_as_data_only",
    "consume_prediction_system_result_snapshot_mapping_as_data_only",
    "declare_source_to_display_field_rules",
    "check_required_display_packet_sections_without_generating_packet",
    "check_primary_signal_summary_candidate",
    "check_horizon_and_family_card_candidate_sources",
    "check_source_quality_and_warning_panel_candidates",
    "return_lowering_readiness_contract_only",
    "ps_q9e_actual_lowering_requires_separate_guard",
    "fail_closed_keep_warroom_and_runtime_disconnected",
)

FIELD_MAPPING_RULES = (
    {
        "display_field": "prediction_run_id",
        "source_paths": ("prediction_run_id", "run_id", "metadata.prediction_run_id", "run_identity.prediction_run_id"),
        "required": True,
    },
    {
        "display_field": "generated_at",
        "source_paths": ("generated_at", "created_at", "metadata.generated_at", "as_of", "run_identity.generated_at", "scenario_core.generated_at"),
        "required": True,
    },
    {
        "display_field": "market_uid",
        "source_paths": ("market_uid", "market.market_uid", "symbol", "instrument", "run_identity.market_uid", "system_input.market_uid"),
        "required": True,
    },
    {
        "display_field": "primary_signal_summary",
        "source_paths": ("primary_signal_summary", "signal_strength_summary", "summary.primary_signal_summary", "gpt_review_digest", "scenario_core.gpt_review_digest", "scenario_core"),
        "required": True,
    },
    {
        "display_field": "horizon_cards",
        "source_paths": ("horizon_cards", "horizons", "horizon_predictions", "scenario_core.outlooks"),
        "required": True,
    },
    {
        "display_field": "family_cards",
        "source_paths": ("family_cards", "family_predictions", "predictions", "outputs", "inference_bundle.outputs"),
        "required": True,
    },
    {
        "display_field": "source_quality_panel",
        "source_paths": ("source_quality_panel", "source_quality", "quality", "system_input.source_artifact_coverage_summary", "system_input.provider_quality_summary", "system_input.diagnostics"),
        "required": True,
    },
    {
        "display_field": "warning_panel",
        "source_paths": ("warning_panel", "warnings", "risk_warnings", "blockers", "scenario_core.warnings", "scenario_core.blockers"),
        "required": True,
    },
)

FAIL_CLOSED_BEHAVIOR = (
    "return_blocked_lowering_contract",
    "do_not_generate_display_packet",
    "do_not_render_warroom_cards",
    "do_not_mutate_warroom_page",
    "do_not_write_runtime_artifact",
    "do_not_append_decision_or_command_ledger",
    "do_not_trigger_autotrade",
    "do_not_send_to_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomPredictionResultLoweringFieldCheck:
    display_field: str
    required: bool
    source_paths: Tuple[str, ...]
    matched_source_path: str | None = None
    source_value_type: str | None = None
    source_value_present: bool = False
    field_ready_for_lowering: bool = False
    blocker_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    lowering_readiness_only: bool = True
    actual_display_packet_generation_enabled: bool = False
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_decode_payload: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "display_field": self.display_field,
            "required": self.required,
            "source_paths": list(self.source_paths),
            "matched_source_path": self.matched_source_path,
            "source_value_type": self.source_value_type,
            "source_value_present": self.source_value_present,
            "field_ready_for_lowering": self.field_ready_for_lowering,
            "blocker_reasons": list(self.blocker_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "lowering_readiness_only": self.lowering_readiness_only,
            "actual_display_packet_generation_enabled": self.actual_display_packet_generation_enabled,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_decode_payload": self.would_decode_payload,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


@dataclass(frozen=True)
class PredictionWarRoomPredictionResultDisplayPacketLoweringContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    target_display_packet_version: str
    schema_validator_contract_version: str
    validation_panel_contract_version: str
    field_checks: Tuple[PredictionWarRoomPredictionResultLoweringFieldCheck, ...] = ()
    lowering_sequence: Tuple[str, ...] = LOWERING_SEQUENCE
    display_packet_required_sections: Tuple[str, ...] = DISPLAY_PACKET_REQUIRED_SECTIONS
    fail_closed_behavior: Tuple[str, ...] = FAIL_CLOSED_BEHAVIOR
    required_field_count: int = 0
    ready_field_count: int = 0
    blocker_count: int = 0
    warning_count: int = 0
    ready_for_ps_q9e_actual_display_packet_lowering: bool = False
    operator_visible_readiness_state: str = "blocked_waiting_for_prediction_result_payload"
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    candidate_display_packet_contract: Mapping[str, Any] = field(default_factory=dict)
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    lowering_readiness_only: bool = True
    actual_display_packet_generation_enabled: bool = False
    display_packet_validation_run_by_this_contract: bool = False
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_decode_payload: bool = False
    would_write_runtime_artifact: bool = False
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
            "target_display_packet_version": self.target_display_packet_version,
            "schema_validator_contract_version": self.schema_validator_contract_version,
            "validation_panel_contract_version": self.validation_panel_contract_version,
            "field_checks": [item.to_dict() for item in self.field_checks],
            "lowering_sequence": list(self.lowering_sequence),
            "display_packet_required_sections": list(self.display_packet_required_sections),
            "fail_closed_behavior": list(self.fail_closed_behavior),
            "required_field_count": self.required_field_count,
            "ready_field_count": self.ready_field_count,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "ready_for_ps_q9e_actual_display_packet_lowering": self.ready_for_ps_q9e_actual_display_packet_lowering,
            "operator_visible_readiness_state": self.operator_visible_readiness_state,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "candidate_display_packet_contract": dict(self.candidate_display_packet_contract),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "lowering_readiness_only": self.lowering_readiness_only,
            "actual_display_packet_generation_enabled": self.actual_display_packet_generation_enabled,
            "display_packet_validation_run_by_this_contract": self.display_packet_validation_run_by_this_contract,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_decode_payload": self.would_decode_payload,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
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


def _get_path(payload: Mapping[str, Any], dotted_path: str) -> Any:
    current: Any = payload
    for part in dotted_path.split("."):
        current_map = _as_mapping(current)
        if not current_map or part not in current_map:
            return None
        current = current_map.get(part)
    return current


def _is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return True


def _signal_percent_ready(value: Any) -> bool:
    if isinstance(value, Mapping):
        raw = value.get("estimated_signal_strength_percent")
        if isinstance(raw, int):
            return 0 <= raw <= 99
        # Actual PredictionSystemResult payloads may expose primary display context
        # through scenario_core / gpt_review_digest without a display-percent yet.
        # PS-Q9E is responsible for clamping/synthesizing a safe display percent.
        return bool(value)
    return False


def _field_check(rule: Mapping[str, Any], payload: Mapping[str, Any]) -> PredictionWarRoomPredictionResultLoweringFieldCheck:
    display_field = str(rule.get("display_field") or "unknown")
    required = bool(rule.get("required", True))
    source_paths = tuple(str(item) for item in _list(rule.get("source_paths")))
    matched_path: str | None = None
    matched_value: Any = None
    for path in source_paths:
        value = _get_path(payload, path)
        if _is_non_empty(value):
            matched_path = path
            matched_value = value
            break
    blockers: list[str] = []
    warnings: list[str] = []
    if matched_path is None:
        if required:
            blockers.append(f"required_lowering_source_missing:{display_field}")
        else:
            warnings.append(f"optional_lowering_source_missing:{display_field}")
    if display_field == "primary_signal_summary" and matched_path is not None and not _signal_percent_ready(matched_value):
        blockers.append("primary_signal_summary_missing_valid_estimated_signal_strength_percent")
    if display_field in {"horizon_cards", "family_cards"} and matched_path is not None and not isinstance(matched_value, (list, tuple)):
        blockers.append(f"{display_field}_must_be_list_before_display_packet_lowering")
    ready = matched_path is not None and not blockers
    return PredictionWarRoomPredictionResultLoweringFieldCheck(
        display_field=display_field,
        required=required,
        source_paths=source_paths,
        matched_source_path=matched_path,
        source_value_type=type(matched_value).__name__ if matched_path is not None else None,
        source_value_present=matched_path is not None,
        field_ready_for_lowering=ready,
        blocker_reasons=tuple(blockers),
        warning_reasons=tuple(warnings),
    )


def _validation_panel_allows_lowering(validation_panel: Mapping[str, Any]) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    if not validation_panel:
        return True, (), ("validation_panel_not_supplied_ps_q9d_uses_payload_shape_only",)
    if validation_panel.get("panel_version") != LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION:
        return False, ("validation_panel_version_mismatch",), ()
    if int(validation_panel.get("blocker_count") or 0) > 0:
        return False, ("validation_panel_has_schema_blockers",), ()
    return True, (), tuple(str(item) for item in _list(validation_panel.get("warning_reasons")))


def build_prediction_warroom_prediction_result_display_packet_lowering_contract(
    *,
    prediction_result_payload: Mapping[str, Any] | Any | None = None,
    validation_panel: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomPredictionResultDisplayPacketLoweringContractPacket:
    """Build a PS-Q9D lowering readiness contract without generating or rendering a display packet."""
    payload = _as_mapping(prediction_result_payload)
    panel = _as_mapping(validation_panel)
    blocked: list[str] = []
    warnings: list[str] = []
    if not payload:
        blocked.append("prediction_result_payload_not_supplied")
    panel_ok, panel_blockers, panel_warnings = _validation_panel_allows_lowering(panel)
    blocked.extend(panel_blockers)
    warnings.extend(panel_warnings)
    field_checks = tuple(_field_check(rule, payload) for rule in FIELD_MAPPING_RULES)
    for check in field_checks:
        blocked.extend(check.blocker_reasons)
        warnings.extend(check.warning_reasons)
    required_count = sum(1 for check in field_checks if check.required)
    ready_count = sum(1 for check in field_checks if check.field_ready_for_lowering)
    unique_blockers = tuple(dict.fromkeys(item for item in blocked if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(payload) and panel_ok and not unique_blockers and ready_count == required_count
    state = "ready_for_ps_q9e_actual_display_packet_lowering_contract_handoff" if ready else "blocked_display_packet_lowering_contract"
    operator_state = "ready_for_ps_q9e_actual_display_packet_lowering" if ready else "blocked_waiting_for_lowering_inputs"
    candidate_contract = {
        "target_display_packet_version": DISPLAY_PACKET_VERSION,
        "required_sections": list(DISPLAY_PACKET_REQUIRED_SECTIONS),
        "field_mapping_rules": [dict(rule) for rule in FIELD_MAPPING_RULES],
        "actual_display_packet_generation_enabled": False,
        "display_packet_validation_deferred_to_ps_q9e_or_later": True,
        "warroom_card_rendering_enabled": False,
    }
    return PredictionWarRoomPredictionResultDisplayPacketLoweringContractPacket(
        contract_version=PREDICTION_RESULT_DISPLAY_PACKET_LOWERING_CONTRACT_VERSION,
        contract_id=f"{PREDICTION_RESULT_DISPLAY_PACKET_LOWERING_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        target_display_packet_version=DISPLAY_PACKET_VERSION,
        schema_validator_contract_version=VALIDATOR_VERSION,
        validation_panel_contract_version=LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION,
        field_checks=field_checks,
        required_field_count=required_count,
        ready_field_count=ready_count,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        ready_for_ps_q9e_actual_display_packet_lowering=ready,
        operator_visible_readiness_state=operator_state,
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        candidate_display_packet_contract=candidate_contract,
        handoff_summary={
            "contract_boundary": "ps_q9d_prediction_result_display_packet_lowering_contract_only",
            "responsibility": "declare and check PredictionSystemResult-like payload fields before PS-Q9E actual display-packet lowering",
            "target_display_packet_version": DISPLAY_PACKET_VERSION,
            "schema_validator_contract_version": VALIDATOR_VERSION,
            "validation_panel_contract_version": LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION,
            "required_field_count": required_count,
            "ready_field_count": ready_count,
            "actual_display_packet_generation_enabled": False,
            "display_packet_validation_run_by_this_contract": False,
            "warroom_card_rendering_enabled": False,
            "warroom_page_mutation_enabled": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled_by_this_contract": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
