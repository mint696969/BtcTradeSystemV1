# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_lowered_display_packet_visibility_review_contract.py
# desc: PS-Q9F visibility/mount-review contract for PS-Q9E lowered display packets. Builds review/readiness data and display-only widget-group metadata in memory; no file reads, payload decode, Streamlit rendering, WarRoom page mutation, runtime writes, Collector runtime, AutoTrade, broker, mode, approval/grant, or ledger append behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Tuple

from .prediction_warroom_actual_display_packet_lowering_adapter import ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION
from .prediction_warroom_payload_schema_validator import DISPLAY_PACKET_VERSION, VALIDATOR_VERSION
from .prediction_warroom_widget_groups import WIDGET_GROUP_PACKET_VERSION, build_prediction_warroom_widget_group_packet_index

LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION = "prediction_warroom_lowered_display_packet_visibility_review_contract.ps_q9f.v1"

VISIBILITY_REVIEW_SEQUENCE = (
    "consume_ps_q9e_lowering_result_packet_as_data_only",
    "verify_display_packet_generated_validated_and_valid",
    "build_display_only_widget_group_index_in_memory",
    "declare_warroom_visibility_review_readiness",
    "return_review_contract_packet_only",
    "do_not_render_streamlit_or_mutate_warroom_page",
    "ps_q9g_guarded_ui_mount_requires_separate_patch",
    "fail_closed_keep_runtime_and_execution_disconnected",
)

VISIBLE_WIDGET_GROUP_ORDER = (
    "primary_signal_widget",
    "horizon_scenario_widgets",
    "family_detail_widgets",
    "source_quality_widget",
    "evidence_ledger_widget",
    "warning_refresh_widget",
)

FAIL_CLOSED_BEHAVIOR = (
    "return_blocked_visibility_review_contract",
    "do_not_render_warroom_cards",
    "do_not_mutate_warroom_page",
    "do_not_read_hot_latest_file",
    "do_not_run_loader_from_ui",
    "do_not_write_runtime_artifact",
    "do_not_append_decision_or_command_ledger",
    "do_not_trigger_autotrade",
    "do_not_send_to_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLoweredDisplayPacketVisibilityWidgetCandidate:
    widget_group_id: str
    widget_group_label_ja: str
    widget_group_kind: str
    refresh_group_id: str
    refresh_interval_sec: int
    refresh_priority: int
    visible_in_review: bool = True
    ui_mount_hint: str = "warroom_prediction:lowered_display_packet_review"
    data_dependencies: Tuple[str, ...] = ()
    payload_key_count: int = 0
    payload_preview_keys: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    review_contract_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    streamlit_render_enabled: bool = False
    warroom_card_rendering_enabled: bool = False
    warroom_page_mutation_enabled: bool = False
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_decode_payload: bool = False
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
            "widget_group_id": self.widget_group_id,
            "widget_group_label_ja": self.widget_group_label_ja,
            "widget_group_kind": self.widget_group_kind,
            "refresh_group_id": self.refresh_group_id,
            "refresh_interval_sec": self.refresh_interval_sec,
            "refresh_priority": self.refresh_priority,
            "visible_in_review": self.visible_in_review,
            "ui_mount_hint": self.ui_mount_hint,
            "data_dependencies": list(self.data_dependencies),
            "payload_key_count": self.payload_key_count,
            "payload_preview_keys": list(self.payload_preview_keys),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "review_contract_only": self.review_contract_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "streamlit_render_enabled": self.streamlit_render_enabled,
            "warroom_card_rendering_enabled": self.warroom_card_rendering_enabled,
            "warroom_page_mutation_enabled": self.warroom_page_mutation_enabled,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_decode_payload": self.would_decode_payload,
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


@dataclass(frozen=True)
class PredictionWarRoomLoweredDisplayPacketVisibilityReviewContractPacket:
    contract_version: str
    contract_id: str
    contract_state: str
    lowering_adapter_version: str
    target_display_packet_version: str
    schema_validator_contract_version: str
    widget_group_contract_version: str
    display_packet_present: bool = False
    display_packet_generated: bool = False
    display_packet_validated: bool = False
    display_packet_valid: bool = False
    widget_group_index_built: bool = False
    widget_group_count: int = 0
    visible_widget_group_count: int = 0
    widget_group_order: Tuple[str, ...] = ()
    widget_candidates: Tuple[PredictionWarRoomLoweredDisplayPacketVisibilityWidgetCandidate, ...] = ()
    widget_group_index: Mapping[str, Any] = field(default_factory=dict)
    visibility_review_sequence: Tuple[str, ...] = VISIBILITY_REVIEW_SEQUENCE
    fail_closed_behavior: Tuple[str, ...] = FAIL_CLOSED_BEHAVIOR
    ready_for_ps_q9g_guarded_ui_mount: bool = False
    operator_visible_readiness_state: str = "blocked_waiting_for_lowered_display_packet"
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    handoff_summary: Mapping[str, Any] = field(default_factory=dict)
    read_only: bool = True
    non_executing: bool = True
    review_contract_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
    not_loaded_as_runtime_display_source: bool = True
    streamlit_render_enabled: bool = False
    warroom_card_rendering_enabled: bool = False
    warroom_page_mutation_enabled: bool = False
    ui_mount_patch_included: bool = False
    loader_execution_allowed_from_ui: bool = False
    would_load_hot_latest_artifacts: bool = False
    would_read_runtime_file: bool = False
    would_decode_payload: bool = False
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
            "lowering_adapter_version": self.lowering_adapter_version,
            "target_display_packet_version": self.target_display_packet_version,
            "schema_validator_contract_version": self.schema_validator_contract_version,
            "widget_group_contract_version": self.widget_group_contract_version,
            "display_packet_present": self.display_packet_present,
            "display_packet_generated": self.display_packet_generated,
            "display_packet_validated": self.display_packet_validated,
            "display_packet_valid": self.display_packet_valid,
            "widget_group_index_built": self.widget_group_index_built,
            "widget_group_count": self.widget_group_count,
            "visible_widget_group_count": self.visible_widget_group_count,
            "widget_group_order": list(self.widget_group_order),
            "widget_candidates": [item.to_dict() for item in self.widget_candidates],
            "widget_group_index": dict(self.widget_group_index),
            "visibility_review_sequence": list(self.visibility_review_sequence),
            "fail_closed_behavior": list(self.fail_closed_behavior),
            "ready_for_ps_q9g_guarded_ui_mount": self.ready_for_ps_q9g_guarded_ui_mount,
            "operator_visible_readiness_state": self.operator_visible_readiness_state,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "handoff_summary": dict(self.handoff_summary),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "review_contract_only": self.review_contract_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
            "not_loaded_as_runtime_display_source": self.not_loaded_as_runtime_display_source,
            "streamlit_render_enabled": self.streamlit_render_enabled,
            "warroom_card_rendering_enabled": self.warroom_card_rendering_enabled,
            "warroom_page_mutation_enabled": self.warroom_page_mutation_enabled,
            "ui_mount_patch_included": self.ui_mount_patch_included,
            "loader_execution_allowed_from_ui": self.loader_execution_allowed_from_ui,
            "would_load_hot_latest_artifacts": self.would_load_hot_latest_artifacts,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_decode_payload": self.would_decode_payload,
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


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _candidate_from_group(raw: Any) -> PredictionWarRoomLoweredDisplayPacketVisibilityWidgetCandidate:
    group = _as_mapping(raw)
    payload = _as_mapping(group.get("payload"))
    return PredictionWarRoomLoweredDisplayPacketVisibilityWidgetCandidate(
        widget_group_id=str(group.get("widget_group_id") or "unknown_widget_group"),
        widget_group_label_ja=str(group.get("widget_group_label_ja") or "未設定"),
        widget_group_kind=str(group.get("widget_group_kind") or "unknown"),
        refresh_group_id=str(group.get("refresh_group_id") or "unknown_refresh_group"),
        refresh_interval_sec=int(group.get("refresh_interval_sec") or 0),
        refresh_priority=int(group.get("refresh_priority") or 0),
        data_dependencies=tuple(str(item) for item in _list(group.get("data_dependencies"))),
        payload_key_count=len(payload),
        payload_preview_keys=tuple(str(key) for key in list(payload.keys())[:12]),
    )


def _blocked_packet(*, lowering: Mapping[str, Any], blocked_reasons: tuple[str, ...], warning_reasons: tuple[str, ...]) -> PredictionWarRoomLoweredDisplayPacketVisibilityReviewContractPacket:
    unique_blockers = tuple(dict.fromkeys(item for item in blocked_reasons if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warning_reasons if item))
    return PredictionWarRoomLoweredDisplayPacketVisibilityReviewContractPacket(
        contract_version=LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION,
        contract_id=f"{LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION}:latest:blocked",
        contract_state="blocked_visibility_review_contract",
        lowering_adapter_version=str(lowering.get("adapter_version") or ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION),
        target_display_packet_version=str(lowering.get("target_display_packet_version") or DISPLAY_PACKET_VERSION),
        schema_validator_contract_version=str(lowering.get("schema_validator_contract_version") or VALIDATOR_VERSION),
        widget_group_contract_version=WIDGET_GROUP_PACKET_VERSION,
        display_packet_present=bool(_as_mapping(lowering.get("display_packet"))),
        display_packet_generated=bool(lowering.get("display_packet_generated")),
        display_packet_validated=bool(lowering.get("display_packet_validated")),
        display_packet_valid=bool(lowering.get("display_packet_valid")),
        blocker_count=len(unique_blockers),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blockers,
        warning_reasons=unique_warnings,
        handoff_summary={
            "contract_boundary": "ps_q9f_lowered_display_packet_visibility_review_contract_only",
            "blocked_before_widget_group_index": True,
            "ps_q9g_guarded_ui_mount_required": True,
            "streamlit_render_enabled": False,
            "warroom_card_rendering_enabled": False,
            "warroom_page_mutation_enabled": False,
            "ui_mount_patch_included": False,
            "loader_execution_allowed_from_ui": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )


def build_prediction_warroom_lowered_display_packet_visibility_review_contract(
    *,
    lowering_result: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomLoweredDisplayPacketVisibilityReviewContractPacket:
    """Build PS-Q9F UI visibility/mount-review contract without rendering or mutating WarRoom page."""
    lowering = _as_mapping(lowering_result)
    blocked: list[str] = []
    warnings: list[str] = []
    if not lowering:
        blocked.append("lowering_result_not_supplied")
    warnings.extend(str(item) for item in _list(lowering.get("warning_reasons")))
    blocked.extend(str(item) for item in _list(lowering.get("blocked_reasons")))
    display_packet = _as_mapping(lowering.get("display_packet"))
    if not bool(lowering.get("display_packet_generated")):
        blocked.append("display_packet_not_generated_by_ps_q9e")
    if not bool(lowering.get("display_packet_validated")):
        blocked.append("display_packet_not_validated_by_ps_q9e")
    if not bool(lowering.get("display_packet_valid")):
        blocked.append("display_packet_not_valid_for_visibility_review")
    if not display_packet:
        blocked.append("display_packet_mapping_missing")
    if blocked:
        return _blocked_packet(lowering=lowering, blocked_reasons=tuple(blocked), warning_reasons=tuple(warnings))

    widget_index = build_prediction_warroom_widget_group_packet_index(display_packet)
    widget_groups = [_as_mapping(item) for item in _list(widget_index.get("widget_groups"))]
    candidates = tuple(_candidate_from_group(item) for item in widget_groups)
    order = tuple(str(item) for item in _list(widget_index.get("widget_group_order")))
    missing_expected = [item for item in VISIBLE_WIDGET_GROUP_ORDER if item not in order]
    if missing_expected:
        warnings.append("widget_group_order_missing_expected_groups:" + ",".join(missing_expected))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = not missing_expected
    state = "visibility_review_ready_for_ps_q9g_guarded_ui_mount_with_warnings" if unique_warnings else "visibility_review_ready_for_ps_q9g_guarded_ui_mount"
    if not ready:
        state = "visibility_review_ready_for_ps_q9g_guarded_ui_mount_with_warnings"
    return PredictionWarRoomLoweredDisplayPacketVisibilityReviewContractPacket(
        contract_version=LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION,
        contract_id=f"{LOWERED_DISPLAY_PACKET_VISIBILITY_REVIEW_CONTRACT_VERSION}:latest:{state}",
        contract_state=state,
        lowering_adapter_version=str(lowering.get("adapter_version") or ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION),
        target_display_packet_version=str(lowering.get("target_display_packet_version") or DISPLAY_PACKET_VERSION),
        schema_validator_contract_version=str(lowering.get("schema_validator_contract_version") or VALIDATOR_VERSION),
        widget_group_contract_version=WIDGET_GROUP_PACKET_VERSION,
        display_packet_present=True,
        display_packet_generated=True,
        display_packet_validated=True,
        display_packet_valid=True,
        widget_group_index_built=True,
        widget_group_count=int(widget_index.get("widget_group_count") or len(widget_groups)),
        visible_widget_group_count=len(candidates),
        widget_group_order=order,
        widget_candidates=candidates,
        widget_group_index=widget_index,
        ready_for_ps_q9g_guarded_ui_mount=ready,
        operator_visible_readiness_state="ready_for_ps_q9g_guarded_ui_mount_review" if ready else "ready_with_visibility_review_warnings",
        blocker_count=0,
        warning_count=len(unique_warnings),
        blocked_reasons=(),
        warning_reasons=unique_warnings,
        handoff_summary={
            "contract_boundary": "ps_q9f_lowered_display_packet_visibility_review_contract_only",
            "responsibility": "review lowered display packet visibility and widget-group readiness before PS-Q9G guarded UI mount",
            "lowering_adapter_version": str(lowering.get("adapter_version") or ACTUAL_DISPLAY_PACKET_LOWERING_ADAPTER_VERSION),
            "target_display_packet_version": DISPLAY_PACKET_VERSION,
            "schema_validator_contract_version": VALIDATOR_VERSION,
            "widget_group_contract_version": WIDGET_GROUP_PACKET_VERSION,
            "widget_group_index_built": True,
            "widget_group_count": int(widget_index.get("widget_group_count") or len(widget_groups)),
            "visible_widget_group_count": len(candidates),
            "streamlit_render_enabled": False,
            "warroom_card_rendering_enabled": False,
            "warroom_page_mutation_enabled": False,
            "ui_mount_patch_included": False,
            "loader_execution_allowed_from_ui": False,
            "runtime_file_read_enabled": False,
            "payload_decode_enabled_by_this_contract": False,
            "runtime_artifact_write_enabled": False,
            "autotrade_trigger_enabled": False,
            "broker_private_api_enabled": False,
        },
    )
