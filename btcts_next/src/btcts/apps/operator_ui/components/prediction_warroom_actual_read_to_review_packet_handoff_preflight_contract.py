# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_actual_read_to_review_packet_handoff_preflight_contract.py
# desc: PS-Q9N data-only preflight contract for handing an already-read real latest payload through Q9C/Q9E/Q9F/Q9H into a WarRoom review packet. Does not read files, run loaders from UI, decode payloads, render Streamlit, mutate WarRoom page, write runtime artifacts, import Collector runtime, trigger AutoTrade, call broker/private APIs, grant approvals, or append ledgers.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_display_packet_lowering_adapter import ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION
from .prediction_warroom_latest_payload_read_only_loader import READ_ONLY_LOADER_VERSION
from .prediction_warroom_loaded_payload_schema_validation_result_panel import LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION
from .prediction_warroom_lowered_display_packet_visibility_review_contract import LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION
from .prediction_warroom_lowered_display_packet_visibility_review_source_handoff import (
    LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
    resolve_prediction_warroom_lowered_display_packet_visibility_review_source,
)

ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_PREFLIGHT_VERSION = "prediction_warroom_actual_read_to_review_packet_handoff_preflight.ps_q9n.v1"

ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_SEQUENCE = (
    "consume_supplied_q9b_loader_result_mapping_only",
    "consume_supplied_q9c_validation_panel_mapping_only",
    "consume_supplied_q9e_lowering_result_mapping_only",
    "consume_supplied_q9f_review_packet_mapping_only",
    "verify_q9h_source_handoff_from_explicit_review_packet",
    "require_real_non_synthetic_payload_before_future_top_default_expanded_ux",
    "return_handoff_preflight_packet_only",
    "do_not_run_loader_from_ui",
    "do_not_read_runtime_file",
    "do_not_decode_payload",
    "do_not_write_runtime_artifact",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomActualReadToReviewPacketHandoffPreflightPacket:
    preflight_version: str
    preflight_id: str
    preflight_state: str
    handoff_sequence: Tuple[str, ...] = ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_SEQUENCE
    loader_result_present: bool = False
    loader_result_version_valid: bool = False
    q9b_actual_file_read_succeeded: bool = False
    q9b_payload_decode_succeeded: bool = False
    q9b_loaded_payload_count: int = 0
    validation_panel_present: bool = False
    validation_panel_version_valid: bool = False
    q9c_validation_panel_valid: bool = False
    q9c_valid_payload_count: int = 0
    lowering_result_present: bool = False
    lowering_result_version_valid: bool = False
    q9e_display_packet_valid: bool = False
    review_packet_present: bool = False
    review_packet_version_valid: bool = False
    q9f_review_packet_ready: bool = False
    q9h_source_handoff_ready: bool = False
    source_handoff: Mapping[str, Any] = field(default_factory=dict)
    synthetic_review_packet_detected: bool = False
    real_payload_required: bool = True
    ready_for_real_payload_review_handoff: bool = False
    ready_for_future_top_default_expanded_ux: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    preflight_contract_only: bool = True
    in_memory_input_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    streamlit_import_required: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
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
            "preflight_version": self.preflight_version,
            "preflight_id": self.preflight_id,
            "preflight_state": self.preflight_state,
            "handoff_sequence": list(self.handoff_sequence),
            "loader_result_present": self.loader_result_present,
            "loader_result_version_valid": self.loader_result_version_valid,
            "q9b_actual_file_read_succeeded": self.q9b_actual_file_read_succeeded,
            "q9b_payload_decode_succeeded": self.q9b_payload_decode_succeeded,
            "q9b_loaded_payload_count": self.q9b_loaded_payload_count,
            "validation_panel_present": self.validation_panel_present,
            "validation_panel_version_valid": self.validation_panel_version_valid,
            "q9c_validation_panel_valid": self.q9c_validation_panel_valid,
            "q9c_valid_payload_count": self.q9c_valid_payload_count,
            "lowering_result_present": self.lowering_result_present,
            "lowering_result_version_valid": self.lowering_result_version_valid,
            "q9e_display_packet_valid": self.q9e_display_packet_valid,
            "review_packet_present": self.review_packet_present,
            "review_packet_version_valid": self.review_packet_version_valid,
            "q9f_review_packet_ready": self.q9f_review_packet_ready,
            "q9h_source_handoff_ready": self.q9h_source_handoff_ready,
            "source_handoff": dict(self.source_handoff),
            "synthetic_review_packet_detected": self.synthetic_review_packet_detected,
            "real_payload_required": self.real_payload_required,
            "ready_for_real_payload_review_handoff": self.ready_for_real_payload_review_handoff,
            "ready_for_future_top_default_expanded_ux": self.ready_for_future_top_default_expanded_ux,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "preflight_contract_only": self.preflight_contract_only,
            "in_memory_input_only": self.in_memory_input_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "streamlit_import_required": self.streamlit_import_required,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
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


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _unsafe_true_flags(packet: Mapping[str, Any], *, prefix: str) -> tuple[str, ...]:
    blockers: list[str] = []
    for key in (
        "ui_mount_patch_included",
        "loader_execution_allowed_from_ui",
        "ui_triggered_loader_execution",
        "would_load_source_artifacts",
        "would_read_runtime_file",
        "would_decode_payload",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "authorization_grant_requested",
        "autotrade_trigger_enabled",
    ):
        if packet.get(key) is True:
            blockers.append(f"{prefix}_unsafe_true_flag:{key}")
    return tuple(blockers)


def _review_packet_is_synthetic(review_packet: Mapping[str, Any]) -> bool:
    widget_index = _as_mapping(review_packet.get("widget_group_index"))
    for raw in _list(widget_index.get("widget_groups")):
        group = _as_mapping(raw)
        payload = _as_mapping(group.get("payload"))
        primary = _as_mapping(payload.get("primary_signal_summary"))
        boundaries = _as_mapping(payload.get("boundaries"))
        run_id = str(payload.get("prediction_run_id") or "")
        if primary.get("synthetic_only") is True or boundaries.get("synthetic_only") is True or run_id.startswith("synthetic_"):
            return True
    return False


def build_prediction_warroom_actual_read_to_review_packet_handoff_preflight(
    *,
    loader_result: Mapping[str, Any] | Any | None = None,
    validation_panel: Mapping[str, Any] | Any | None = None,
    lowering_result: Mapping[str, Any] | Any | None = None,
    review_packet: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomActualReadToReviewPacketHandoffPreflightPacket:
    """Validate supplied in-memory Q9B/Q9C/Q9E/Q9F/Q9H handoff state without running loaders or reading files."""
    loader = _as_mapping(loader_result)
    validation = _as_mapping(validation_panel)
    lowering = _as_mapping(lowering_result)
    review = _as_mapping(review_packet)
    blocked: list[str] = []
    warnings: list[str] = []

    loader_version_ok = loader.get("loader_version") == READ_ONLY_LOADER_VERSION
    q9b_read_ok = loader.get("actual_file_read_succeeded") is True
    q9b_decode_ok = loader.get("payload_decode_succeeded") is True
    q9b_loaded_count = int(loader.get("loaded_payload_count") or 0)
    if not loader:
        blocked.append("q9b_loader_result_not_supplied")
    elif not loader_version_ok:
        blocked.append("q9b_loader_result_version_invalid")
    elif not (q9b_read_ok and q9b_decode_ok and q9b_loaded_count > 0):
        blocked.append("q9b_actual_read_decode_not_ready")
    blocked.extend(_unsafe_true_flags(loader, prefix="q9b_loader_result"))

    validation_version_ok = validation.get("panel_version") == LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION
    q9c_valid = validation.get("panel_state") in ("schema_validation_panel_valid", "schema_validation_panel_valid_with_warnings") and int(validation.get("blocker_count") or 0) == 0
    q9c_valid_count = int(validation.get("valid_payload_count") or 0)
    if not validation:
        blocked.append("q9c_validation_panel_not_supplied")
    elif not validation_version_ok:
        blocked.append("q9c_validation_panel_version_invalid")
    elif not (q9c_valid and q9c_valid_count > 0):
        blocked.append("q9c_validation_panel_not_ready")
    blocked.extend(_unsafe_true_flags(validation, prefix="q9c_validation_panel"))

    lowering_version_ok = lowering.get("adapter_version") == ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION
    q9e_valid = lowering.get("display_packet_valid") is True and lowering.get("adapter_state") == "display_packet_lowered_and_validated_in_memory"
    if not lowering:
        blocked.append("q9e_lowering_result_not_supplied")
    elif not lowering_version_ok:
        blocked.append("q9e_lowering_result_version_invalid")
    elif not q9e_valid:
        blocked.append("q9e_display_packet_not_ready")
    blocked.extend(_unsafe_true_flags(lowering, prefix="q9e_lowering_result"))

    review_version_ok = review.get("contract_version") == LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION
    q9f_ready = review.get("ready_for_ps_q9g_guarded_ui_mount") is True and int(review.get("blocker_count") or 0) == 0
    if not review:
        blocked.append("q9f_review_packet_not_supplied")
    elif not review_version_ok:
        blocked.append("q9f_review_packet_version_invalid")
    elif not q9f_ready:
        blocked.append("q9f_review_packet_not_ready")
    blocked.extend(_unsafe_true_flags(review, prefix="q9f_review_packet"))

    source_handoff = resolve_prediction_warroom_lowered_display_packet_visibility_review_source(
        explicit_review_packet=review,
    ).to_dict()
    q9h_ready = source_handoff.get("handoff_state") == "review_source_handoff_ready" and source_handoff.get("review_packet_ready") is True
    if not q9h_ready:
        blocked.append("q9h_source_handoff_not_ready")

    synthetic = _review_packet_is_synthetic(review)
    if synthetic:
        blocked.append("real_payload_required_but_synthetic_review_packet_detected")
    elif review:
        warnings.append("real_payload_review_packet_not_verified_by_ui_observation_yet")

    unique_blocked = tuple(dict.fromkeys(item for item in blocked if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not unique_blocked
    state = "actual_read_to_review_handoff_preflight_ready" if ready else "actual_read_to_review_handoff_preflight_blocked"
    return PredictionWarRoomActualReadToReviewPacketHandoffPreflightPacket(
        preflight_version=ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_PREFLIGHT_VERSION,
        preflight_id=f"{ACTUAL_READ_TO_REVIEW_PACKET_HANDOFF_PREFLIGHT_VERSION}:latest:{state}",
        preflight_state=state,
        loader_result_present=bool(loader),
        loader_result_version_valid=loader_version_ok,
        q9b_actual_file_read_succeeded=q9b_read_ok,
        q9b_payload_decode_succeeded=q9b_decode_ok,
        q9b_loaded_payload_count=q9b_loaded_count,
        validation_panel_present=bool(validation),
        validation_panel_version_valid=validation_version_ok,
        q9c_validation_panel_valid=q9c_valid,
        q9c_valid_payload_count=q9c_valid_count,
        lowering_result_present=bool(lowering),
        lowering_result_version_valid=lowering_version_ok,
        q9e_display_packet_valid=q9e_valid,
        review_packet_present=bool(review),
        review_packet_version_valid=review_version_ok,
        q9f_review_packet_ready=q9f_ready,
        q9h_source_handoff_ready=q9h_ready,
        source_handoff=source_handoff,
        synthetic_review_packet_detected=synthetic,
        ready_for_real_payload_review_handoff=ready,
        ready_for_future_top_default_expanded_ux=False,
        blocker_count=len(unique_blocked),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blocked,
        warning_reasons=unique_warnings,
        handoff_summary={
            "preflight_boundary": "ps_q9n_actual_read_to_review_packet_handoff_preflight_only",
            "q9b_loader_version": READ_ONLY_LOADER_VERSION,
            "q9c_validation_panel_version": LOADED_PAYLOAD_SCHEMA_VALIDATION_PANEL_VERSION,
            "q9e_lowering_adapter_version": ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION,
            "q9f_review_contract_version": LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION,
            "q9h_source_handoff_version": LOWERED_DISPLAY_PACKET_REVIEW_SOURCE_HANDOFF_VERSION,
            "ready_for_real_payload_review_handoff": ready,
            "ready_for_future_top_default_expanded_ux": False,
            "ui_triggered_loader_execution": False,
            "runtime_file_read_enabled_by_this_preflight": False,
            "payload_decode_enabled_by_this_preflight": False,
            "runtime_artifact_write_enabled": False,
            "warroom_page_mutation_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
