# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_display_packet_lowering_adapter.py
# desc: PS-Q9E in-memory PredictionSystemResult-like payload to Q4A-compatible WarRoom display-packet lowering adapter. Builds and validates a display packet mapping in memory only; no file reads, payload decode, rendering, WarRoom mutation, runtime writes, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_payload_schema_validator import (
    DISPLAY_PACKET_VERSION,
    VALIDATOR_VERSION,
    validate_prediction_warroom_display_packet_schema,
)
from .prediction_warroom_prediction_result_display_packet_lowering_contract import (
    PREDICTION_RESULT_DISPLAY_PACKET_LOWERING_CONTRACT_VERSION,
    build_prediction_warroom_prediction_result_display_packet_lowering_contract,
)

ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION = "prediction_warroom_actual_display_packet_lowering_adapter.ps_q9e.v1"

LOWERING_ADAPTER_SEQUENCE = (
    "consume_prediction_system_result_snapshot_mapping_as_in_memory_data_only",
    "run_ps_q9d_lowering_contract_readiness",
    "build_q4a_compatible_display_packet_mapping_in_memory",
    "validate_display_packet_mapping_with_q5c",
    "return_lowering_result_packet_only",
    "do_not_mount_or_render_warroom_cards",
    "ps_q9f_ui_mount_requires_separate_guard",
    "fail_closed_keep_runtime_disconnected",
)


@dataclass(frozen=True)
class PredictionWarRoomActualDisplayPacketLoweringResult:
    adapter_version: str
    adapter_id: str
    adapter_state: str
    source_contract_version: str
    target_display_packet_version: str
    schema_validator_contract_version: str
    display_packet: Mapping[str, Any] = field(default_factory=dict)
    validation_report: Mapping[str, Any] = field(default_factory=dict)
    lowering_contract: Mapping[str, Any] = field(default_factory=dict)
    lowering_adapter_sequence: Tuple[str, ...] = LOWERING_ADAPTER_SEQUENCE
    display_packet_generated: bool = False
    display_packet_validated: bool = False
    display_packet_valid: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    in_memory_lowering_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    warroom_card_rendering_enabled: bool = False
    warroom_page_mutation_enabled: bool = False
    would_load_hot_latest_artifacts: bool = False
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
            "adapter_version": self.adapter_version,
            "adapter_id": self.adapter_id,
            "adapter_state": self.adapter_state,
            "source_contract_version": self.source_contract_version,
            "target_display_packet_version": self.target_display_packet_version,
            "schema_validator_contract_version": self.schema_validator_contract_version,
            "display_packet": dict(self.display_packet),
            "validation_report": dict(self.validation_report),
            "lowering_contract": dict(self.lowering_contract),
            "lowering_adapter_sequence": list(self.lowering_adapter_sequence),
            "display_packet_generated": self.display_packet_generated,
            "display_packet_validated": self.display_packet_validated,
            "display_packet_valid": self.display_packet_valid,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "in_memory_lowering_only": self.in_memory_lowering_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "warroom_card_rendering_enabled": self.warroom_card_rendering_enabled,
            "warroom_page_mutation_enabled": self.warroom_page_mutation_enabled,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
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


def _first_mapping(payload: Mapping[str, Any], *keys: str) -> Mapping[str, Any]:
    for key in keys:
        value = _as_mapping(_get_path(payload, key))
        if value:
            return value
    return {}


def _first_list(payload: Mapping[str, Any], *keys: str) -> list[Any]:
    for key in keys:
        value = _list(_get_path(payload, key))
        if value:
            return value
    return []


def _first_value(payload: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = _get_path(payload, key)
        if value is not None:
            return value
    return default


def _percent_from_any(value: Any, *, default: int = 0) -> int:
    if isinstance(value, int):
        return max(0, min(99, value))
    if isinstance(value, float):
        return max(0, min(99, int(round(value * 100 if 0 <= value <= 1 else value))))
    return max(0, min(99, default))


def _safe_boundaries() -> dict[str, Any]:
    return {
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_decode_payload": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "authorization_grant_requested": False,
        "trigger_enabled": False,
        "autotrade_trigger_enabled": False,
    }


def _ui_contract() -> dict[str, Any]:
    return {
        "contract_version": "prediction_warroom_ui_contract.ps_q9e.v1",
        "intended_consumer": "WarRoom",
        "packet_kind": "prediction_system_display_packet",
        "display_only": True,
        "render_intent_only": True,
        "safe_to_render_without_side_effects": True,
        "requires_runtime_artifact_write": False,
        "requires_collector_runtime": False,
        "requires_autotrade_runtime": False,
        "trigger_buttons_allowed": False,
        "mode_controls_allowed": False,
        "broker_controls_allowed": False,
        "not_loaded_as_runtime_display_source": True,
        "generated_by_ps_q9e_lowering_adapter": True,
    }


def _normalize_signal_summary(value: Mapping[str, Any]) -> dict[str, Any]:
    percent = _percent_from_any(value.get("estimated_signal_strength_percent", value.get("score", 0)))
    ref_percent = _percent_from_any(value.get("estimated_reference_hit_rate_percent", percent), default=percent)
    band = str(value.get("signal_strength_band") or value.get("confidence") or value.get("current_hypothesis_health") or "unknown")
    return {
        "summary_version": str(value.get("summary_version") or "prediction_signal_strength_bands.ps_q9e.v1"),
        "estimated_signal_strength_percent": max(0, min(99, int(percent))),
        "estimated_reference_hit_rate_percent": max(0, min(99, int(ref_percent))),
        "signal_strength_band": band,
        "signal_strength_band_label_ja": str(value.get("signal_strength_band_label_ja") or band),
        "signal_strength_cap_reasons": _list(value.get("signal_strength_cap_reasons")),
        "prediction_unavailable_reasons": _list(value.get("prediction_unavailable_reasons")),
        "read_only": True,
        "non_executing": True,
    }


def _normalize_horizon_card(raw: Any, primary: Mapping[str, Any]) -> dict[str, Any]:
    item = _as_mapping(raw)
    percent = _percent_from_any(item.get("estimated_signal_strength_percent", item.get("score", primary.get("estimated_signal_strength_percent", 0))))
    band = str(item.get("signal_strength_band") or item.get("confidence") or primary.get("signal_strength_band") or "unknown")
    return {
        "card_version": str(item.get("card_version") or "prediction_warroom_horizon_card.ps_q9e.v1"),
        "horizon_group": str(item.get("horizon_group") or item.get("group") or "unknown"),
        "display_label_ja": str(item.get("display_label_ja") or item.get("horizon_group") or "unknown"),
        "estimated_signal_strength_percent": max(0, min(99, int(percent))),
        "signal_strength_band": band,
        "signal_strength_band_label_ja": str(item.get("signal_strength_band_label_ja") or band),
        "scenario_lite": dict(_as_mapping(item.get("scenario_lite"))),
        "blockers": _list(item.get("blockers")),
        "warnings": _list(item.get("warnings")),
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
    }


def _normalize_family_card(raw: Any, primary: Mapping[str, Any]) -> dict[str, Any]:
    item = _as_mapping(raw)
    horizon = _as_mapping(item.get("horizon"))
    percent = _percent_from_any(item.get("estimated_signal_strength_percent", item.get("score", primary.get("estimated_signal_strength_percent", 0))))
    return {
        "card_version": str(item.get("card_version") or "prediction_warroom_family_card.ps_q9e.v1"),
        "family": str(item.get("family") or "unknown"),
        "horizon_sec": int(item.get("horizon_sec") or horizon.get("horizon_sec") or 0),
        "primary_label": str(item.get("primary_label") or item.get("label") or "unknown"),
        "estimated_signal_strength_percent": percent,
        "source_quality_gate_state": str(item.get("source_quality_gate_state") or "unknown"),
        "context_profile_source_caps": _list(item.get("context_profile_source_caps")),
        "source_contribution_ledger": _list(item.get("source_contribution_ledger")),
        "blockers": _list(item.get("blockers")),
        "warnings": _list(item.get("warnings")),
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
    }


def _normalize_source_quality_panel(raw: Mapping[str, Any]) -> dict[str, Any]:
    gate = raw.get("tier0_source_quality_gate")
    gate_map = _as_mapping(gate)
    if not gate_map:
        gate_map = {"gate_state": str(gate or "unknown")}
    panel = dict(raw)
    panel.update(
        {
            "panel_version": str(raw.get("panel_version") or "prediction_warroom_source_quality_panel.ps_q9e.v1"),
            "tier0_source_quality_gate": dict(gate_map),
            "read_only": True,
            "non_executing": True,
        }
    )
    return panel


def _normalize_warning_panel(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "panel_version": str(raw.get("panel_version") or "prediction_warroom_warning_panel.ps_q9e.v1"),
        "blockers": _list(raw.get("blockers")),
        "warnings": _list(raw.get("warnings")),
        "scenario_blockers": _list(raw.get("scenario_blockers")),
        "scenario_warnings": _list(raw.get("scenario_warnings")),
        "signal_strength_cap_reasons": _list(raw.get("signal_strength_cap_reasons")),
        "prediction_unavailable_reasons": _list(raw.get("prediction_unavailable_reasons")),
        "read_only": True,
        "non_executing": True,
    }


def _warning_panel_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    explicit = _first_mapping(payload, "warning_panel", "risk_warnings")
    if explicit:
        return _normalize_warning_panel(explicit)
    return _normalize_warning_panel(
        {
            "blockers": _list(payload.get("blockers")),
            "warnings": _list(payload.get("warnings")),
            "scenario_blockers": _list(_get_path(payload, "scenario_core.blockers")),
            "scenario_warnings": _list(_get_path(payload, "scenario_core.warnings")),
        }
    )


def _build_display_packet(payload: Mapping[str, Any]) -> dict[str, Any]:
    prediction_run_id = str(_first_value(payload, "prediction_run_id", "run_id", "metadata.prediction_run_id", "run_identity.prediction_run_id", default="unknown_prediction_run"))
    generated_at = str(_first_value(payload, "generated_at", "created_at", "metadata.generated_at", "as_of", "run_identity.generated_at", "scenario_core.generated_at", default="unknown_generated_at"))
    market_uid = str(_first_value(payload, "market_uid", "market.market_uid", "symbol", "instrument", "run_identity.market_uid", "system_input.market_uid", default="unknown_market"))
    primary = _normalize_signal_summary(_first_mapping(payload, "primary_signal_summary", "signal_strength_summary", "summary.primary_signal_summary", "gpt_review_digest", "scenario_core.gpt_review_digest", "scenario_core"))
    horizon_cards = [_normalize_horizon_card(item, primary) for item in _first_list(payload, "horizon_cards", "horizons", "horizon_predictions", "scenario_core.outlooks")]
    family_cards = [_normalize_family_card(item, primary) for item in _first_list(payload, "family_cards", "family_predictions", "predictions", "outputs", "inference_bundle.outputs")]
    source_quality_panel = _normalize_source_quality_panel(_first_mapping(payload, "source_quality_panel", "source_quality", "quality", "system_input.source_artifact_coverage_summary", "system_input.provider_quality_summary", "system_input.diagnostics"))
    warning_panel = _warning_panel_from_payload(payload)
    return {
        "packet_version": DISPLAY_PACKET_VERSION,
        "packet_id": f"{DISPLAY_PACKET_VERSION}:{prediction_run_id}",
        "generated_at": generated_at,
        "market_uid": market_uid,
        "prediction_run_id": prediction_run_id,
        "headline_ja": str(payload.get("headline_ja") or "Prediction WarRoom display packet lowered in memory."),
        "primary_signal_summary": primary,
        "horizon_cards": horizon_cards,
        "family_cards": family_cards,
        "source_quality_panel": source_quality_panel,
        "warning_panel": warning_panel,
        "ui_contract": _ui_contract(),
        "boundaries": _safe_boundaries(),
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
        "would_load_hot_latest_artifacts": False,
        "would_read_runtime_file": False,
        "would_decode_payload": False,
        "would_write_runtime_artifact": False,
        "would_write_collector_state": False,
        "would_send_to_broker": False,
        "broker_execution_requested": False,
        "mode_apply_requested": False,
        "command_ledger_append_requested": False,
        "approval_append_requested": False,
        "authorization_grant_requested": False,
        "autotrade_trigger_enabled": False,
    }


def build_prediction_warroom_actual_display_packet_lowering_result(
    *,
    prediction_result_payload: Mapping[str, Any] | Any | None = None,
    validation_panel: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomActualDisplayPacketLoweringResult:
    """Build and validate a Q4A-compatible display packet mapping in memory only."""
    payload = _as_mapping(prediction_result_payload)
    lowering_contract = build_prediction_warroom_prediction_result_display_packet_lowering_contract(
        prediction_result_payload=payload,
        validation_panel=validation_panel,
    ).to_dict()
    blocked = [str(item) for item in _list(lowering_contract.get("blocked_reasons"))]
    warnings = [str(item) for item in _list(lowering_contract.get("warning_reasons"))]
    if not bool(lowering_contract.get("ready_for_ps_q9e_actual_display_packet_lowering")):
        return PredictionWarRoomActualDisplayPacketLoweringResult(
            adapter_version=ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION,
            adapter_id=f"{ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION}:latest:blocked",
            adapter_state="blocked_by_ps_q9d_lowering_contract",
            source_contract_version=PREDICTION_RESULT_DISPLAY_PACKET_LOWERING_CONTRACT_VERSION,
            target_display_packet_version=DISPLAY_PACKET_VERSION,
            schema_validator_contract_version=VALIDATOR_VERSION,
            lowering_contract=lowering_contract,
            blocker_count=len(tuple(dict.fromkeys(blocked))),
            warning_count=len(tuple(dict.fromkeys(warnings))),
            blocked_reasons=tuple(dict.fromkeys(blocked)),
            warning_reasons=tuple(dict.fromkeys(warnings)),
            handoff_summary={
                "adapter_boundary": "ps_q9e_actual_display_packet_lowering_adapter_in_memory_only",
                "blocked_before_display_packet_generation": True,
                "warroom_card_rendering_enabled": False,
                "warroom_page_mutation_enabled": False,
                "runtime_artifact_write_enabled": False,
                "autotrade_trigger_enabled": False,
                "broker_private_api_enabled": False,
            },
        )
    display_packet = _build_display_packet(payload)
    validation_report = validate_prediction_warroom_display_packet_schema(display_packet).to_dict()
    validation_blockers = int(validation_report.get("blocker_count") or 0)
    validation_warnings = int(validation_report.get("warning_count") or 0)
    if validation_blockers:
        blocked.append("q5c_display_packet_schema_validation_blocked")
    if validation_warnings:
        warnings.append("q5c_display_packet_schema_validation_warning")
    unique_blocked = tuple(dict.fromkeys(item for item in blocked if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    valid = bool(validation_report.get("valid")) and not unique_blocked
    state = "display_packet_lowered_and_validated_in_memory" if valid else "blocked_after_display_packet_validation"
    return PredictionWarRoomActualDisplayPacketLoweringResult(
        adapter_version=ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION,
        adapter_id=f"{ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION}:latest:{state}",
        adapter_state=state,
        source_contract_version=PREDICTION_RESULT_DISPLAY_PACKET_LOWERING_CONTRACT_VERSION,
        target_display_packet_version=DISPLAY_PACKET_VERSION,
        schema_validator_contract_version=VALIDATOR_VERSION,
        display_packet=display_packet,
        validation_report=validation_report,
        lowering_contract=lowering_contract,
        display_packet_generated=True,
        display_packet_validated=True,
        display_packet_valid=valid,
        blocker_count=len(unique_blocked),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blocked,
        warning_reasons=unique_warnings,
        handoff_summary={
            "adapter_boundary": "ps_q9e_actual_display_packet_lowering_adapter_in_memory_only",
            "responsibility": "build and validate Q4A-compatible display packet mapping from in-memory PredictionSystemResult-like payload",
            "target_display_packet_version": DISPLAY_PACKET_VERSION,
            "schema_validator_contract_version": VALIDATOR_VERSION,
            "display_packet_generated": True,
            "display_packet_validated": True,
            "display_packet_valid": valid,
            "warroom_card_rendering_enabled": False,
            "warroom_page_mutation_enabled": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled_by_this_adapter": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
