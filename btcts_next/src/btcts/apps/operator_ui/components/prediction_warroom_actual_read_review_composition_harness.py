# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_read_review_composition_harness.py
# desc: PS-Q9O non-UI local/dev composition harness for supplied explicit Prediction WarRoom payload data through Q9C/Q9E/Q9F/Q9N. Does not read files, run loaders, decode payloads, render Streamlit, mutate WarRoom page/panel, write runtime artifacts, import Collector runtime, trigger AutoTrade, call broker/private APIs, grant approvals, or append ledgers.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_display_packet_lowering_adapter import build_prediction_warroom_actual_display_packet_lowering_result
from .prediction_warroom_actual_read_to_review_packet_handoff_preflight_contract import (
    ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_PREFLIGHT_VERSION,
    build_prediction_warroom_actual_read_to_review_packet_handoff_preflight,
)
from .prediction_warroom_latest_payload_read_only_loader import READ_ONLY_LOADER_VERSION
from .prediction_warroom_loaded_payload_schema_validation_result_panel import build_prediction_warroom_loaded_payload_schema_validation_result_panel
from .prediction_warroom_lowered_display_packet_visibility_review_contract import build_prediction_warroom_lowered_display_packet_visibility_review_contract

ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION = "prediction_warroom_actual_read_review_composition_harness.ps_q9o.v1"
DEFAULT_RESULT_ROLE = "prediction_system_result_snapshot"

ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_SEQUENCE = (
    "consume_supplied_explicit_payload_or_loader_result_mapping_only",
    "build_or_use_supplied_q9b_loader_result_mapping_without_running_loader",
    "build_q9c_validation_panel_from_loader_result_mapping_in_memory",
    "build_q9e_display_packet_lowering_result_in_memory",
    "build_q9f_review_packet_in_memory",
    "build_q9n_handoff_preflight_in_memory",
    "return_composition_harness_packet_only",
    "do_not_run_loader",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_mutate_warroom_page_or_panel",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReadReviewCompositionHarnessPacket:
    harness_version: str
    harness_id: str
    harness_state: str
    harness_sequence: Tuple[str, ...] = ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_SEQUENCE
    loader_result_source: str = "missing"
    payload_source: str = "missing"
    q9b_loader_result: Mapping[str, Any] = field(default_factory=dict)
    q9c_validation_panel: Mapping[str, Any] = field(default_factory=dict)
    q9e_lowering_result: Mapping[str, Any] = field(default_factory=dict)
    q9f_review_packet: Mapping[str, Any] = field(default_factory=dict)
    q9n_handoff_preflight: Mapping[str, Any] = field(default_factory=dict)
    q9c_validation_panel_built: bool = False
    q9e_lowering_result_built: bool = False
    q9f_review_packet_built: bool = False
    q9n_handoff_preflight_built: bool = False
    ready_for_real_payload_review_handoff: bool = False
    ready_for_future_top_default_expanded_ux: bool = False
    actual_q9b_loader_result_required_for_ready: bool = True
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    harness_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    local_dev_harness_only: bool = True
    in_memory_input_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
    loader_execution_requested: bool = False
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
            "harness_version": self.harness_version,
            "harness_id": self.harness_id,
            "harness_state": self.harness_state,
            "harness_sequence": list(self.harness_sequence),
            "loader_result_source": self.loader_result_source,
            "payload_source": self.payload_source,
            "q9b_loader_result": dict(self.q9b_loader_result),
            "q9c_validation_panel": dict(self.q9c_validation_panel),
            "q9e_lowering_result": dict(self.q9e_lowering_result),
            "q9f_review_packet": dict(self.q9f_review_packet),
            "q9n_handoff_preflight": dict(self.q9n_handoff_preflight),
            "q9c_validation_panel_built": self.q9c_validation_panel_built,
            "q9e_lowering_result_built": self.q9e_lowering_result_built,
            "q9f_review_packet_built": self.q9f_review_packet_built,
            "q9n_handoff_preflight_built": self.q9n_handoff_preflight_built,
            "ready_for_real_payload_review_handoff": self.ready_for_real_payload_review_handoff,
            "ready_for_future_top_default_expanded_ux": self.ready_for_future_top_default_expanded_ux,
            "actual_q9b_loader_result_required_for_ready": self.actual_q9b_loader_result_required_for_ready,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "harness_summary": dict(self.harness_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "local_dev_harness_only": self.local_dev_harness_only,
            "in_memory_input_only": self.in_memory_input_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
            "loader_execution_requested": self.loader_execution_requested,
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


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _loaded_payload_from_loader(loader_result: Mapping[str, Any], role: str) -> Mapping[str, Any]:
    loaded = _as_mapping(loader_result.get("loaded_payloads"))
    payload = _as_mapping(loaded.get(role))
    if payload:
        return payload
    for value in loaded.values():
        payload = _as_mapping(value)
        if payload:
            return payload
    return {}


def _explicit_payload_loader_surrogate(payload: Mapping[str, Any], role: str) -> Mapping[str, Any]:
    return {
        "loader_version": READ_ONLY_LOADER_VERSION,
        "loader_state": "explicit_payload_supplied_without_q9b_actual_read_result",
        "allowed_artifact_roles": [role],
        "loaded_payloads": {role: dict(payload)} if payload else {},
        "loaded_payload_count": 1 if payload else 0,
        "allow_actual_read_requested": False,
        "actual_file_read_attempted": False,
        "actual_file_read_succeeded": False,
        "payload_decode_attempted": False,
        "payload_decode_succeeded": False,
        "schema_validation_deferred_to_ps_q9c": True,
        "blocker_reasons": ["q9b_actual_read_result_not_supplied"],
        "warning_reasons": ["explicit_payload_supplied_as_in_memory_local_dev_harness_input"],
        "read_only": True,
        "non_executing": True,
        "guarded_loader_only": True,
        "display_only": True,
        "render_intent_only": True,
        "not_loaded_as_runtime_display_source": True,
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


def build_prediction_warroom_actual_read_review_composition_harness(
    *,
    prediction_result_payload: Mapping[str, Any] | Any | None = None,
    loader_result: Mapping[str, Any] | Any | None = None,
    artifact_role: str = DEFAULT_RESULT_ROLE,
) -> PredictionWarRoomActualReadReviewCompositionHarnessPacket:
    """Compose supplied in-memory payload/contract data through Q9C/Q9E/Q9F/Q9N without running loaders or reading files."""
    supplied_loader = _as_mapping(loader_result)
    supplied_payload = _as_mapping(prediction_result_payload)
    role = str(artifact_role or DEFAULT_RESULT_ROLE)
    warnings: list[str] = []
    blockers: list[str] = []
    loader_source = "supplied_q9b_loader_result_mapping" if supplied_loader else "explicit_payload_surrogate_loader_result"
    if not supplied_loader and not supplied_payload:
        loader_source = "missing"
        blockers.append("prediction_result_payload_or_loader_result_required")
    payload_source = "explicit_prediction_result_payload" if supplied_payload else "loader_result_loaded_payloads"
    effective_payload = supplied_payload or _loaded_payload_from_loader(supplied_loader, role)
    if not effective_payload:
        blockers.append("prediction_result_payload_mapping_missing")
    effective_loader = supplied_loader if supplied_loader else _explicit_payload_loader_surrogate(effective_payload, role)
    if not supplied_loader:
        warnings.append("q9b_actual_loader_result_not_supplied_handoff_will_fail_closed")

    validation_panel = build_prediction_warroom_loaded_payload_schema_validation_result_panel(
        loader_result=effective_loader,
    ).to_dict()
    lowering_result = build_prediction_warroom_actual_display_packet_lowering_result(
        prediction_result_payload=effective_payload,
        validation_panel=validation_panel,
    ).to_dict()
    review_packet = build_prediction_warroom_lowered_display_packet_visibility_review_contract(
        lowering_result=lowering_result,
    ).to_dict()
    handoff_preflight = build_prediction_warroom_actual_read_to_review_packet_handoff_preflight(
        loader_result=effective_loader,
        validation_panel=validation_panel,
        lowering_result=lowering_result,
        review_packet=review_packet,
    ).to_dict()
    blockers.extend(str(item) for item in handoff_preflight.get("blocked_reasons", ()) if item)
    warnings.extend(str(item) for item in handoff_preflight.get("warning_reasons", ()) if item)
    unique_blockers = tuple(dict.fromkeys(item for item in blockers if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = bool(handoff_preflight.get("ready_for_real_payload_review_handoff")) and not unique_blockers
    state = "actual_read_review_composition_ready" if ready else "actual_read_review_composition_blocked"
    return PredictionWarRoomActualReadReviewCompositionHarnessPacket(
        harness_version=ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION,
        harness_id=f"{ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION}:latest:{state}",
        harness_state=state,
        loader_result_source=loader_source,
        payload_source=payload_source,
        q9b_loader_result=effective_loader,
        q9c_validation_panel=validation_panel,
        q9e_lowering_result=lowering_result,
        q9f_review_packet=review_packet,
        q9n_handoff_preflight=handoff_preflight,
        q9c_validation_panel_built=True,
        q9e_lowering_result_built=True,
        q9f_review_packet_built=True,
        q9n_handoff_preflight_built=True,
        ready_for_real_payload_review_handoff=ready,
        ready_for_future_top_default_expanded_ux=False,
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        harness_summary={
            "harness_boundary": "ps_q9o_non_ui_local_dev_composition_harness_only",
            "q9n_handoff_preflight_version": ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_PREFLIGHT_VERSION,
            "loader_result_source": loader_source,
            "payload_source": payload_source,
            "ready_for_real_payload_review_handoff": ready,
            "ready_for_future_top_default_expanded_ux": False,
            "ui_triggered_loader_execution": False,
            "loader_execution_requested": False,
            "runtime_file_read_enabled_by_this_harness": False,
            "payload_decode_enabled_by_this_harness": False,
            "runtime_artifact_write_enabled": False,
            "warroom_page_mutation_enabled": False,
            "warroom_review_panel_mutation_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
