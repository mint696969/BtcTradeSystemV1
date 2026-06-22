# path: ./btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_realtime_review_preflight_contract.py
# desc: PS-Q13A contract-only preflight for WarRoom real-time prediction review, GPT-assisted explanation, and parameter-adjustment review surfaces. No rendering, runtime writes, AutoTrade, broker, mode/order, approval, or ledger behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Tuple

PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION = "prediction_warroom_realtime_review_preflight.ps_q13a.v1"

REVIEW_SURFACE_SEQUENCE: Tuple[str, ...] = (
    "consume_latest_prediction_source_review_panel_packet_as_data_only",
    "consume_prediction_system_result_or_scenario_core_summary_as_data_only",
    "declare_realtime_prediction_delta_review_surface",
    "declare_gpt_assisted_explanation_context_surface",
    "declare_parameter_adjustment_candidate_review_surface",
    "declare_source_quality_warning_and_blocker_review_surface",
    "declare_responsibility_separation_boundaries",
    "return_preflight_packet_only",
    "do_not_render_streamlit_ui_in_this_slice",
    "do_not_write_runtime_artifacts",
    "do_not_mutate_live_parameters",
    "do_not_append_approval_decision_or_command_ledgers",
    "do_not_trigger_autotrade_or_broker",
)

REVIEW_SURFACE_IDS: Tuple[str, ...] = (
    "latest_prediction_source",
    "realtime_prediction_delta_review",
    "scenario_trace_review",
    "gpt_assisted_explanation_context",
    "parameter_adjustment_candidate_review",
    "source_quality_warning_review",
    "responsibility_boundary_review",
)

RESPONSIBILITY_BOUNDARY: Mapping[str, str] = {
    "prediction_system": "prediction contracts, evidence, scenario traces, explanation packets, parameter-adjustment proposal data",
    "warroom": "display, operator review, GPT-assisted explanation surfaces, check-only UI snapshots",
    "collector": "collection and hot/latest runtime data production",
    "autotrade": "deferred future owner of trigger consumption/readiness/risk/approval/ledger/mode/order/broker after explicit scope only",
}

PARAMETER_REVIEW_STATES: Tuple[str, ...] = (
    "no_live_mutation",
    "proposal_only",
    "staging_required_later",
    "human_review_required",
    "gpt_assisted_explanation_allowed",
    "versioned_policy_required_before_apply",
)

FORBIDDEN_NEXT_BEHAVIOR: Tuple[str, ...] = (
    "autotrade_trigger_consumption",
    "prediction_to_autotrade_bridge_execution",
    "approval_decision_command_ledger_append",
    "broker_private_api",
    "mode_apply_or_order_placement",
    "warroom_runtime_artifact_write",
    "freshness_bypass",
    "silent_live_parameter_mutation",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, Mapping) else {}
    return value if isinstance(value, Mapping) else {}


def _as_tuple(value: Any) -> Tuple[Any, ...]:
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return ()


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _bool_at(mapping: Mapping[str, Any], key: str, default: bool = False) -> bool:
    return bool(mapping.get(key, default))


def _nested(mapping: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = mapping.get(key)
    return value if isinstance(value, Mapping) else {}


@dataclass(frozen=True)
class PredictionWarRoomReviewSurfacePreflightRow:
    surface_id: str
    label_ja: str
    state: str
    source: str
    operator_note_ja: str
    read_only: bool = True
    execution: bool = False
    autotrade: bool = False
    broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionWarRoomRealtimeReviewPreflightPacket:
    preflight_version: str
    preflight_id: str
    preflight_state: str
    surface_sequence: Tuple[str, ...] = REVIEW_SURFACE_SEQUENCE
    surface_ids: Tuple[str, ...] = REVIEW_SURFACE_IDS
    review_surfaces: Tuple[PredictionWarRoomReviewSurfacePreflightRow, ...] = ()
    responsibility_boundary: Mapping[str, str] = field(default_factory=lambda: dict(RESPONSIBILITY_BOUNDARY))
    parameter_review_states: Tuple[str, ...] = PARAMETER_REVIEW_STATES
    forbidden_next_behavior: Tuple[str, ...] = FORBIDDEN_NEXT_BEHAVIOR
    latest_prediction_source_panel_present: bool = False
    latest_prediction_review_ready: bool = False
    latest_prediction_blocker_count: int = 0
    latest_prediction_warning_count: int = 0
    prediction_run_id: str = ""
    generated_at: str = ""
    market_uid: str = ""
    signal_strength_percent: int | None = None
    signal_strength_band: str = "unknown"
    scenario_trace_present: bool = False
    gpt_review_digest_present: bool = False
    realtime_delta_review_surface_declared: bool = True
    parameter_adjustment_candidate_review_surface_declared: bool = True
    gpt_assisted_explanation_surface_declared: bool = True
    ready_for_future_warroom_ui_slice: bool = False
    blocker_count: int = 0
    warning_count: int = 0
    blocked_reasons: Tuple[str, ...] = ()
    warning_reasons: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    contract_only: bool = True
    preflight_only: bool = True
    display_only: bool = True
    streamlit_import_required: bool = False
    streamlit_render_performed_by_this_contract: bool = False
    ui_controls_added: bool = False
    ui_triggered_loader_execution: bool = False
    would_read_runtime_file: bool = False
    would_decode_payload: bool = False
    would_write_runtime_artifact: bool = False
    would_write_collector_state: bool = False
    would_mutate_live_parameters: bool = False
    would_append_parameter_version: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    decision_ledger_append_requested: bool = False
    approval_append_requested: bool = False
    authorization_grant_requested: bool = False
    autotrade_trigger_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preflight_version": self.preflight_version,
            "preflight_id": self.preflight_id,
            "preflight_state": self.preflight_state,
            "surface_sequence": list(self.surface_sequence),
            "surface_ids": list(self.surface_ids),
            "review_surfaces": [row.to_dict() for row in self.review_surfaces],
            "responsibility_boundary": dict(self.responsibility_boundary),
            "parameter_review_states": list(self.parameter_review_states),
            "forbidden_next_behavior": list(self.forbidden_next_behavior),
            "latest_prediction_source_panel_present": self.latest_prediction_source_panel_present,
            "latest_prediction_review_ready": self.latest_prediction_review_ready,
            "latest_prediction_blocker_count": self.latest_prediction_blocker_count,
            "latest_prediction_warning_count": self.latest_prediction_warning_count,
            "prediction_run_id": self.prediction_run_id,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "signal_strength_percent": self.signal_strength_percent,
            "signal_strength_band": self.signal_strength_band,
            "scenario_trace_present": self.scenario_trace_present,
            "gpt_review_digest_present": self.gpt_review_digest_present,
            "realtime_delta_review_surface_declared": self.realtime_delta_review_surface_declared,
            "parameter_adjustment_candidate_review_surface_declared": self.parameter_adjustment_candidate_review_surface_declared,
            "gpt_assisted_explanation_surface_declared": self.gpt_assisted_explanation_surface_declared,
            "ready_for_future_warroom_ui_slice": self.ready_for_future_warroom_ui_slice,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "blocked_reasons": list(self.blocked_reasons),
            "warning_reasons": list(self.warning_reasons),
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "contract_only": self.contract_only,
            "preflight_only": self.preflight_only,
            "display_only": self.display_only,
            "streamlit_import_required": self.streamlit_import_required,
            "streamlit_render_performed_by_this_contract": self.streamlit_render_performed_by_this_contract,
            "ui_controls_added": self.ui_controls_added,
            "ui_triggered_loader_execution": self.ui_triggered_loader_execution,
            "would_read_runtime_file": self.would_read_runtime_file,
            "would_decode_payload": self.would_decode_payload,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_write_collector_state": self.would_write_collector_state,
            "would_mutate_live_parameters": self.would_mutate_live_parameters,
            "would_append_parameter_version": self.would_append_parameter_version,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "decision_ledger_append_requested": self.decision_ledger_append_requested,
            "approval_append_requested": self.approval_append_requested,
            "authorization_grant_requested": self.authorization_grant_requested,
            "autotrade_trigger_enabled": self.autotrade_trigger_enabled,
        }


def _latest_source_summary(latest_prediction_source_panel: Mapping[str, Any]) -> Mapping[str, Any]:
    adapter = _nested(latest_prediction_source_panel, "adapter_packet") or latest_prediction_source_panel
    summary = _nested(adapter, "source_summary")
    return summary


def _surface_rows(
    *,
    latest_present: bool,
    latest_ready: bool,
    blocker_count: int,
    warning_count: int,
    scenario_trace_present: bool,
    gpt_review_digest_present: bool,
) -> Tuple[PredictionWarRoomReviewSurfacePreflightRow, ...]:
    source_state = "ready" if latest_ready else "not_ready"
    if not latest_present:
        source_state = "missing"
    return (
        PredictionWarRoomReviewSurfacePreflightRow(
            surface_id="latest_prediction_source",
            label_ja="最新推論ソース",
            state=source_state,
            source="prediction_warroom_latest_prediction_source_review_panel",
            operator_note_ja="D-hot latest PredictionSystemResult の表示準備状態を確認する。実行許可ではない。",
        ),
        PredictionWarRoomReviewSurfacePreflightRow(
            surface_id="realtime_prediction_delta_review",
            label_ja="リアルタイム変動レビュー",
            state="declared_check_only",
            source="future_warroom_display_surface",
            operator_note_ja="推論 run / signal / warning / blocker の変化を人間が追うための表示面。runtime write ではない。",
        ),
        PredictionWarRoomReviewSurfacePreflightRow(
            surface_id="scenario_trace_review",
            label_ja="シナリオ trace レビュー",
            state="present" if scenario_trace_present else "declared_waiting_for_source",
            source="PredictionSystemResult.scenario_core / PredictionScenarioOutput",
            operator_note_ja="evidence_weighting / invalidation / switch trace を確認する表示面。売買判断の自動実行ではない。",
        ),
        PredictionWarRoomReviewSurfacePreflightRow(
            surface_id="gpt_assisted_explanation_context",
            label_ja="GPT支援説明コンテキスト",
            state="present" if gpt_review_digest_present else "declared_waiting_for_digest",
            source="gpt_review_digest / advisory_output_packet_candidate",
            operator_note_ja="GPT と一緒に説明・矛盾・注意点を確認するための context。自動パラメーター変更ではない。",
        ),
        PredictionWarRoomReviewSurfacePreflightRow(
            surface_id="parameter_adjustment_candidate_review",
            label_ja="パラメーター調整候補レビュー",
            state="proposal_only_declared",
            source="future_prediction_system_parameter_proposal_data",
            operator_note_ja="候補の確認・提案・staging まで。silent live mutation と apply は禁止。",
        ),
        PredictionWarRoomReviewSurfacePreflightRow(
            surface_id="source_quality_warning_review",
            label_ja="情報品質 warning / blocker",
            state=f"blockers={blocker_count}; warnings={warning_count}",
            source="latest_prediction_source_panel / source_quality_panel",
            operator_note_ja="情報品質と警告を確認する。freshness bypass や実行許可ではない。",
        ),
        PredictionWarRoomReviewSurfacePreflightRow(
            surface_id="responsibility_boundary_review",
            label_ja="責務境界レビュー",
            state="declared_guarded",
            source="ps_q13_mainline_alignment",
            operator_note_ja="Prediction System / WarRoom / Collector / AutoTrade の責務分離を守る確認面。",
        ),
    )


def build_prediction_warroom_realtime_review_preflight(
    *,
    latest_prediction_source_panel: Mapping[str, Any] | Any | None = None,
    prediction_system_result: Mapping[str, Any] | Any | None = None,
    scenario_core_output: Mapping[str, Any] | Any | None = None,
) -> PredictionWarRoomRealtimeReviewPreflightPacket:
    """Build a PS-Q13A data-only preflight packet for future WarRoom review UX.

    The packet is intentionally contract/preflight only. It never imports Streamlit,
    reads hot files, decodes payloads, writes runtime artifacts, appends ledgers,
    mutates parameters, triggers AutoTrade, or calls broker/private APIs.
    """
    latest = _as_mapping(latest_prediction_source_panel)
    result = _as_mapping(prediction_system_result)
    scenario = _as_mapping(scenario_core_output) or _nested(result, "scenario_core")
    latest_present = bool(latest)
    adapter = _nested(latest, "adapter_packet") or latest
    summary = _latest_source_summary(latest)
    latest_ready = _bool_at(adapter, "review_packet_ready") and _bool_at(adapter, "session_state_updated")
    latest_blockers = _int(adapter.get("blocker_count")) or len(_as_tuple(adapter.get("blocked_reasons")))
    latest_warnings = _int(adapter.get("warning_count")) or len(_as_tuple(adapter.get("warning_reasons")))

    scenario_trace = _nested(scenario, "scenario_trace")
    if not scenario_trace:
        scenario_trace = _nested(result, "scenario_trace")
    gpt_review_digest = _nested(scenario, "gpt_review_digest")
    if not gpt_review_digest:
        gpt_review_digest = _nested(result, "gpt_review_digest")

    blocked: list[str] = []
    warnings: list[str] = []
    if not latest_present:
        blocked.append("latest_prediction_source_panel_missing")
    if latest_present and not latest_ready:
        warnings.append("latest_prediction_source_not_review_ready_yet")
    if latest_blockers:
        warnings.append("latest_prediction_source_has_blockers_for_review")
    if not scenario_trace:
        warnings.append("scenario_trace_not_supplied_to_preflight")
    if not gpt_review_digest:
        warnings.append("gpt_review_digest_not_supplied_to_preflight")

    ready_for_future_ui = latest_present and not blocked

    return PredictionWarRoomRealtimeReviewPreflightPacket(
        preflight_version=PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION,
        preflight_id="prediction_warroom_realtime_review_preflight:ps_q13a",
        preflight_state="ready_for_future_warroom_ui_slice" if ready_for_future_ui else "blocked_waiting_for_latest_prediction_source",
        review_surfaces=_surface_rows(
            latest_present=latest_present,
            latest_ready=latest_ready,
            blocker_count=latest_blockers,
            warning_count=latest_warnings,
            scenario_trace_present=bool(scenario_trace),
            gpt_review_digest_present=bool(gpt_review_digest),
        ),
        latest_prediction_source_panel_present=latest_present,
        latest_prediction_review_ready=latest_ready,
        latest_prediction_blocker_count=latest_blockers,
        latest_prediction_warning_count=latest_warnings,
        prediction_run_id=str(summary.get("prediction_run_id") or result.get("prediction_run_id") or ""),
        generated_at=str(summary.get("generated_at") or result.get("generated_at") or ""),
        market_uid=str(summary.get("market_uid") or result.get("market_uid") or ""),
        signal_strength_percent=summary.get("signal_strength_percent"),
        signal_strength_band=str(summary.get("signal_strength_band") or "unknown"),
        scenario_trace_present=bool(scenario_trace),
        gpt_review_digest_present=bool(gpt_review_digest),
        ready_for_future_warroom_ui_slice=ready_for_future_ui,
        blocker_count=len(blocked),
        warning_count=len(warnings),
        blocked_reasons=tuple(blocked),
        warning_reasons=tuple(warnings),
    )
