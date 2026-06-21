# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_adapter.py
# desc: PS-Q12A WarRoom read-only latest prediction source adapter. Bridges D-hot latest prediction artifact through existing Q9B/Q9O/Q10K contracts into an in-memory review packet; no Streamlit rendering, page mutation, runtime writes, AutoTrade, broker, mode, approval, or ledger behavior.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Tuple

from .prediction_warroom_actual_read_review_composition_harness import (
    ACTUAL_READ_REVIEW_COMPOSITION_HARNESS_VERSION,
    build_prediction_warroom_actual_read_review_composition_harness,
)
from .prediction_warroom_actual_review_packet_session_state_handoff_harness import (
    ACTUAL_REVIEW_PACKET_SESSION_STATE_HANDOFF_HARNESS_VERSION,
    DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
    build_prediction_warroom_actual_review_packet_session_state_handoff_harness,
)
from .prediction_warroom_latest_payload_read_only_loader import (
    DEFAULT_ALLOWED_ARTIFACT_ROLES,
    READ_ONLY_LOADER_VERSION,
    load_prediction_warroom_latest_payload_read_only,
)
from .prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT

LATEST_PREDICTION_SOURCE_ADAPTER_VERSION = "prediction_warroom_latest_prediction_source_adapter.ps_q12a.v1"

LATEST_PREDICTION_SOURCE_ADAPTER_SEQUENCE = (
    "require_explicit_allow_actual_read_before_q9b_loader_call",
    "call_q9b_read_only_loader_only_when_enabled",
    "compose_q9o_review_packet_in_memory",
    "optionally_store_q9f_review_packet_in_supplied_session_mapping_with_q10k",
    "return_source_adapter_packet_only",
    "do_not_render_streamlit",
    "do_not_mutate_warroom_page_or_panel",
    "do_not_write_runtime_artifact",
    "do_not_append_ledger_or_grant_approval",
    "do_not_trigger_autotrade_or_broker",
)


@dataclass(frozen=True)
class PredictionWarRoomLatestPredictionSourceAdapterPacket:
    adapter_version: str
    adapter_id: str
    adapter_state: str
    adapter_sequence: Tuple[str, ...] = LATEST_PREDICTION_SOURCE_ADAPTER_SEQUENCE
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT
    allowed_artifact_roles: Tuple[str, ...] = DEFAULT_ALLOWED_ARTIFACT_ROLES
    target_session_key: str = DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY
    loader_result: Mapping[str, Any] = field(default_factory=dict)
    composition_harness: Mapping[str, Any] = field(default_factory=dict)
    session_state_handoff: Mapping[str, Any] = field(default_factory=dict)
    review_packet: Mapping[str, Any] = field(default_factory=dict)
    source_summary: Mapping[str, Any] = field(default_factory=dict)
    allow_actual_read_requested: bool = False
    q9b_loader_called_by_this_adapter: bool = False
    q9o_composition_harness_called: bool = False
    q10k_session_state_handoff_called: bool = False
    session_state_mapping_supplied: bool = False
    store_in_session_state_requested: bool = False
    session_state_updated: bool = False
    review_packet_ready: bool = False
    ready_for_warroom_review_panel: bool = False
    ready_for_warroom_top_display: bool = False
    actual_file_read_attempted: bool = False
    actual_file_read_succeeded: bool = False
    payload_decode_attempted: bool = False
    payload_decode_succeeded: bool = False
    loaded_payload_count: int = 0
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    source_adapter_only: bool = True
    in_memory_result_only: bool = True
    display_only: bool = True
    render_intent_only: bool = True
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
            "adapter_version": self.adapter_version,
            "adapter_id": self.adapter_id,
            "adapter_state": self.adapter_state,
            "adapter_sequence": list(self.adapter_sequence),
            "hot_latest_root_hint": self.hot_latest_root_hint,
            "allowed_artifact_roles": list(self.allowed_artifact_roles),
            "target_session_key": self.target_session_key,
            "loader_result": dict(self.loader_result),
            "composition_harness": dict(self.composition_harness),
            "session_state_handoff": dict(self.session_state_handoff),
            "review_packet": dict(self.review_packet),
            "source_summary": dict(self.source_summary),
            "allow_actual_read_requested": self.allow_actual_read_requested,
            "q9b_loader_called_by_this_adapter": self.q9b_loader_called_by_this_adapter,
            "q9o_composition_harness_called": self.q9o_composition_harness_called,
            "q10k_session_state_handoff_called": self.q10k_session_state_handoff_called,
            "session_state_mapping_supplied": self.session_state_mapping_supplied,
            "store_in_session_state_requested": self.store_in_session_state_requested,
            "session_state_updated": self.session_state_updated,
            "review_packet_ready": self.review_packet_ready,
            "ready_for_warroom_review_panel": self.ready_for_warroom_review_panel,
            "ready_for_warroom_top_display": self.ready_for_warroom_top_display,
            "actual_file_read_attempted": self.actual_file_read_attempted,
            "actual_file_read_succeeded": self.actual_file_read_succeeded,
            "payload_decode_attempted": self.payload_decode_attempted,
            "payload_decode_succeeded": self.payload_decode_succeeded,
            "loaded_payload_count": self.loaded_payload_count,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "source_adapter_only": self.source_adapter_only,
            "in_memory_result_only": self.in_memory_result_only,
            "display_only": self.display_only,
            "render_intent_only": self.render_intent_only,
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


def _review_packet_from_composition(composition_harness: Mapping[str, Any]) -> Mapping[str, Any]:
    return _as_mapping(composition_harness.get("q9f_review_packet"))


def _summary_from_review_packet(review_packet: Mapping[str, Any]) -> Mapping[str, Any]:
    widget_index = _as_mapping(review_packet.get("widget_group_index"))
    primary_payload: Mapping[str, Any] = {}
    for raw in _list(widget_index.get("widget_groups")):
        group = _as_mapping(raw)
        if group.get("widget_group_id") == "primary_signal_widget":
            primary_payload = _as_mapping(group.get("payload"))
            break
    primary_signal = _as_mapping(primary_payload.get("primary_signal_summary"))
    return {
        "prediction_run_id": primary_payload.get("prediction_run_id"),
        "generated_at": primary_payload.get("generated_at"),
        "market_uid": primary_payload.get("market_uid"),
        "headline_ja": primary_payload.get("headline_ja"),
        "signal_strength_percent": primary_signal.get("estimated_signal_strength_percent"),
        "signal_strength_band": primary_signal.get("signal_strength_band"),
        "review_packet_contract_state": review_packet.get("contract_state"),
        "ready_for_ps_q9g_guarded_ui_mount": review_packet.get("ready_for_ps_q9g_guarded_ui_mount"),
        "visible_widget_group_count": review_packet.get("visible_widget_group_count"),
        "blocker_count": review_packet.get("blocker_count"),
        "warning_count": review_packet.get("warning_count"),
        "read_only": True,
        "non_executing": True,
        "would_send_to_broker": False,
        "would_write_runtime_artifact": False,
    }


def build_prediction_warroom_latest_prediction_source_adapter(
    *,
    hot_latest_root_hint: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    allowed_artifact_roles: Iterable[str] | None = None,
    allow_actual_read: bool = False,
    session_state: MutableMapping[str, Any] | None = None,
    store_in_session_state: bool = False,
    target_session_key: str = DEFAULT_ACTUAL_REVIEW_PACKET_SESSION_KEY,
) -> PredictionWarRoomLatestPredictionSourceAdapterPacket:
    """Read the latest PredictionSystemResult JSON through Q9B and compose a Q9F review packet for WarRoom review."""
    roles = _roles(allowed_artifact_roles)
    blocked: list[str] = []
    warnings: list[str] = []
    loader: Mapping[str, Any] = {}
    composition: Mapping[str, Any] = {}
    handoff: Mapping[str, Any] = {}
    q9b_called = False

    if not allow_actual_read:
        blocked.append("allow_actual_read_false")
        warnings.append("ps_q12a_requires_explicit_allow_actual_read_for_latest_prediction_source")
    else:
        loader = load_prediction_warroom_latest_payload_read_only(
            hot_latest_root_hint=hot_latest_root_hint,
            allowed_artifact_roles=roles,
            allow_actual_read=True,
        ).to_dict()
        q9b_called = True

    composition = build_prediction_warroom_actual_read_review_composition_harness(
        loader_result=loader,
    ).to_dict()
    review_packet = _review_packet_from_composition(composition)
    review_ready = bool(review_packet.get("ready_for_ps_q9g_guarded_ui_mount")) and int(review_packet.get("blocker_count") or 0) == 0
    if allow_actual_read and not review_ready:
        blocked.append("q9o_review_packet_not_ready")

    if store_in_session_state:
        handoff = build_prediction_warroom_actual_review_packet_session_state_handoff_harness(
            review_packet=review_packet,
            session_state=session_state,
            target_session_key=target_session_key,
            store_in_session_state=True,
        ).to_dict()
        if not bool(handoff.get("session_state_updated")):
            blocked.append("q10k_session_state_handoff_not_updated")
    elif session_state is not None:
        warnings.append("session_state_supplied_but_store_in_session_state_false")

    blocked.extend(str(item) for item in _list(loader.get("blocker_reasons")) if item)
    warnings.extend(str(item) for item in _list(loader.get("warning_reasons")) if item)
    blocked.extend(str(item) for item in _list(composition.get("blocked_reasons")) if item)
    warnings.extend(str(item) for item in _list(composition.get("warning_reasons")) if item)
    blocked.extend(str(item) for item in _list(handoff.get("blocked_reasons")) if item)
    warnings.extend(str(item) for item in _list(handoff.get("warning_reasons")) if item)

    unique_blocked = tuple(dict.fromkeys(item for item in blocked if item))
    unique_warnings = tuple(dict.fromkeys(item for item in warnings if item))
    ready = allow_actual_read and review_ready and not unique_blocked
    state = "latest_prediction_source_ready" if ready else "latest_prediction_source_blocked"
    return PredictionWarRoomLatestPredictionSourceAdapterPacket(
        adapter_version=LATEST_PREDICTION_SOURCE_ADAPTER_VERSION,
        adapter_id=f"{LATEST_PREDICTION_SOURCE_ADAPTER_VERSION}:latest:{state}",
        adapter_state=state,
        hot_latest_root_hint=str(hot_latest_root_hint),
        allowed_artifact_roles=roles,
        target_session_key=target_session_key,
        loader_result=loader,
        composition_harness=composition,
        session_state_handoff=handoff,
        review_packet=review_packet,
        source_summary=_summary_from_review_packet(review_packet) if review_packet else {},
        allow_actual_read_requested=allow_actual_read,
        q9b_loader_called_by_this_adapter=q9b_called,
        q9o_composition_harness_called=True,
        q10k_session_state_handoff_called=bool(store_in_session_state),
        session_state_mapping_supplied=session_state is not None,
        store_in_session_state_requested=store_in_session_state,
        session_state_updated=bool(handoff.get("session_state_updated")),
        review_packet_ready=review_ready,
        ready_for_warroom_review_panel=ready,
        ready_for_warroom_top_display=False,
        actual_file_read_attempted=bool(loader.get("actual_file_read_attempted")),
        actual_file_read_succeeded=bool(loader.get("actual_file_read_succeeded")),
        payload_decode_attempted=bool(loader.get("payload_decode_attempted")),
        payload_decode_succeeded=bool(loader.get("payload_decode_succeeded")),
        loaded_payload_count=int(loader.get("loaded_payload_count") or 0),
        blocker_count=len(unique_blocked),
        warning_count=len(unique_warnings),
        blocked_reasons=unique_blocked,
        warning_reasons=unique_warnings,
        source_adapter_only=True,
        in_memory_result_only=True,
        runtime_artifact_write_allowed=False,
        approval_or_authorization_allowed=False,
        ledger_append_allowed=False,
        autotrade_trigger_allowed=False,
        broker_private_api_allowed=False,
    )
