# path: ./btcts_next/src/btcts/replay/replay_prediction_artifacts.py
# desc: Thin replay-side owner that builds minimal prediction artifacts and emits evaluation entries into ReplaySession.

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from btcts.processing.l4_consumer_models.shared import (
    MarketSummaryBuildInput,
    PredictionCalibrationBuildInput,
    PredictionScenarioBuildInput,
    PredictionSystemBuildInput,
    PredictionTacticBuildInput,
    PredictionTacticOperationBuildInput,
    PredictionTacticReviewBuildInput,
    build_market_summary,
    build_prediction_calibration_hint,
    build_prediction_scenario_output,
    build_prediction_system_input,
    build_prediction_tactic_operation_record,
    build_prediction_tactic_proposal_output,
    build_prediction_tactic_review_record,
)
from btcts.processing.l4_consumer_models.shared._value_utils import safe_float

from .prediction_calibration_review import (
    PredictionCalibrationReviewBuildInput,
    build_prediction_calibration_review,
)
from .prediction_evaluation_entry import (
    PredictionEvaluationBuildInput,
    build_prediction_evaluation_entry,
)
from .prediction_evaluation_report import build_prediction_evaluation_report
from .prediction_realized_outcome import (
    PredictionRealizedOutcomeBuildInput,
    build_prediction_realized_outcome,
)


def _normalize_dict(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return dict(value)


def _materialize_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if is_dataclass(value):
        return dict(asdict(value))
    return {}


def _collect_event_names(events: Any) -> list[str]:
    if not isinstance(events, list):
        return []

    out: list[str] = []
    for item in events:
        if not isinstance(item, dict):
            continue
        event_name = str(item.get("event_name") or "").strip()
        if event_name:
            out.append(event_name)
    return out


def _collect_summary_slots(event_names: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []

    for event_name in event_names:
        lower_name = event_name.lower()

        if "support" in lower_name and "support" not in seen:
            seen.add("support")
            out.append("support")

        if "resistance" in lower_name and "resistance" not in seen:
            seen.add("resistance")
            out.append("resistance")

        if "persistence" in lower_name and "persistence" not in seen:
            seen.add("persistence")
            out.append("persistence")

        if "wall" in lower_name and "near_wall" not in seen:
            seen.add("near_wall")
            out.append("near_wall")

    return out


def _resolve_market_uid(exchange: str, symbol_raw: str) -> str:
    return f"{exchange}.spot.{symbol_raw}"


def _resolve_mid_price(result: dict[str, Any]) -> float | None:
    best_bid = safe_float(result.get("best_bid"))
    best_ask = safe_float(result.get("best_ask"))

    if best_bid is not None and best_ask is not None:
        return round((best_bid + best_ask) / 2.0, 2)
    if best_bid is not None:
        return round(best_bid, 2)
    if best_ask is not None:
        return round(best_ask, 2)
    return None


def _price_to_bp(
    *,
    anchor_price: float | None,
    observed_price: float | None,
) -> float | None:
    if anchor_price is None or observed_price is None or anchor_price <= 0.0:
        return None
    return round(((observed_price - anchor_price) / anchor_price) * 10000.0, 2)


def _resolve_realized_excursions(
    *,
    anchor_mid_price: float | None,
    current_prediction_state: dict[str, Any],
) -> tuple[float | None, float | None]:
    if anchor_mid_price is None or anchor_mid_price <= 0.0:
        return None, None

    candidate_moves: list[float] = []

    current_mid_price = safe_float(current_prediction_state.get("mid_price"))
    if current_mid_price is not None:
        mid_move = _price_to_bp(
            anchor_price=anchor_mid_price,
            observed_price=current_mid_price,
        )
        if mid_move is not None:
            candidate_moves.append(mid_move)

    current_best_bid = safe_float(current_prediction_state.get("best_bid"))
    if current_best_bid is not None:
        bid_move = _price_to_bp(
            anchor_price=anchor_mid_price,
            observed_price=current_best_bid,
        )
        if bid_move is not None:
            candidate_moves.append(bid_move)

    current_best_ask = safe_float(current_prediction_state.get("best_ask"))
    if current_best_ask is not None:
        ask_move = _price_to_bp(
            anchor_price=anchor_mid_price,
            observed_price=current_best_ask,
        )
        if ask_move is not None:
            candidate_moves.append(ask_move)

    if not candidate_moves:
        return None, None

    realized_max_adverse_bp = round(min(min(candidate_moves), 0.0), 2)
    realized_max_favorable_bp = round(max(max(candidate_moves), 0.0), 2)
    return realized_max_adverse_bp, realized_max_favorable_bp


def _build_replay_market_summary(
    result: dict[str, Any],
    *,
    exchange: str,
    symbol_raw: str,
):
    event_names = _collect_event_names(result.get("events"))
    event_count = len(event_names)

    return build_market_summary(
        MarketSummaryBuildInput(
            market_state_row={
                "exchange": exchange,
                "symbol": symbol_raw,
                "market_uid": _resolve_market_uid(exchange, symbol_raw),
                "collector_ts": result.get("event_ts"),
                "trust_state": "trusted",
                "continuity_state": "continuous",
                "interpretation_bucket": "allow_structural_use",
                "interpretation_reason": "replay_prediction_artifact_builder",
                "semantic_observer_status": "healthy",
                "semantic_usage_summary": {
                    "source_kind": "replay_prediction_artifact",
                    "contract_source": "replay_prediction_artifact_builder",
                    "meaning_version": "phase3.v1alpha1",
                    "observer_status": "healthy",
                    "total_rows": event_count,
                    "active_event_count": event_count,
                    "mapped_event_count": event_count,
                    "unknown_event_count": 0,
                },
                "orderbook_semantics_summary": {
                    "summary_slots_present": _collect_summary_slots(event_names),
                    "active_event_count": event_count,
                    "active_event_names": event_names,
                    "active_event_contracts": [],
                },
                "orderbook_persistence_observable": True,
            },
            diagnostics={
                "source_kind": "replay_prediction_artifact",
                "preferred_row_age_sec": 0.0,
                "preferred_row_freshness": "LIVE",
                "builder_type": "replay_prediction_artifact_builder",
                "record_id": result.get("record_id"),
                "record_type": result.get("record_type"),
            },
            source_kind="replay_prediction_artifact",
        )
    )


def build_prediction_state_from_replay_result(
    result: dict[str, Any],
    *,
    exchange: str,
    symbol_raw: str,
    replay_feedback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    market_summary = _build_replay_market_summary(
        result,
        exchange=exchange,
        symbol_raw=symbol_raw,
    )
    prediction_input = build_prediction_system_input(
        PredictionSystemBuildInput(
            market_summary=market_summary,
            replay_feedback=_normalize_dict(replay_feedback),
            source_kind="replay_prediction_artifact",
            diagnostics={
                "builder_type": "replay_prediction_artifact_builder",
                "record_id": result.get("record_id"),
                "record_type": result.get("record_type"),
            },
        )
    )
    scenario_output = build_prediction_scenario_output(
        PredictionScenarioBuildInput(
            prediction_input=prediction_input,
            diagnostics={
                "builder_type": "replay_prediction_artifact_builder",
                "record_id": result.get("record_id"),
                "record_type": result.get("record_type"),
            },
        )
    )
    tactic_proposal_output = build_prediction_tactic_proposal_output(
        PredictionTacticBuildInput(
            scenario_output=scenario_output,
            diagnostics={
                "builder_type": "replay_prediction_artifact_builder",
                "record_id": result.get("record_id"),
                "record_type": result.get("record_type"),
            },
        )
    )
    calibration_hint = build_prediction_calibration_hint(
        PredictionCalibrationBuildInput(
            prediction_input=prediction_input,
            scenario_output=scenario_output,
            diagnostics={
                "builder_type": "replay_prediction_artifact_builder",
                "record_id": result.get("record_id"),
                "record_type": result.get("record_type"),
            },
        )
    )

    return {
        "market_summary": market_summary,
        "prediction_input": prediction_input,
        "scenario_output": scenario_output,
        "tactic_proposal_output": tactic_proposal_output,
        "calibration_hint": calibration_hint,
        "mid_price": _resolve_mid_price(result),
        "best_bid": safe_float(result.get("best_bid")),
        "best_ask": safe_float(result.get("best_ask")),
    }


def _build_proxy_realized_outcome(
    *,
    current_prediction_state: dict[str, Any],
    previous_mid_price: float | None,
    realized_horizon: str,
) -> dict[str, Any]:
    scenario_output = current_prediction_state["scenario_output"]
    current_mid_price = safe_float(current_prediction_state.get("mid_price"))

    realized_return_bp = _price_to_bp(
        anchor_price=previous_mid_price,
        observed_price=current_mid_price,
    )
    (
        realized_max_adverse_bp,
        realized_max_favorable_bp,
    ) = _resolve_realized_excursions(
        anchor_mid_price=previous_mid_price,
        current_prediction_state=current_prediction_state,
    )

    return build_prediction_realized_outcome(
        PredictionRealizedOutcomeBuildInput(
            market_uid=scenario_output.market_uid,
            event_ts=scenario_output.event_ts,
            realized_horizon=realized_horizon,
            realized_regime_state=scenario_output.current_regime_state,
            realized_confidence=scenario_output.current_confidence,
            realized_caution_level=scenario_output.current_caution_level,
            realized_return_bp=realized_return_bp,
            realized_max_adverse_bp=realized_max_adverse_bp,
            realized_max_favorable_bp=realized_max_favorable_bp,
            diagnostics={
                "builder_type": "replay_prediction_artifact_builder",
                "realized_outcome_source": "next_step_proxy",
                "anchor_mid_price": previous_mid_price,
                "current_mid_price": current_mid_price,
                "current_best_bid": safe_float(current_prediction_state.get("best_bid")),
                "current_best_ask": safe_float(current_prediction_state.get("best_ask")),
                "realized_window_mode": "single_step_quote_envelope",
            },
        )
    )


def _build_prediction_calibration_review_artifact(
    *,
    calibration_hint: Any,
    evaluation_entries: list[dict[str, Any]],
) -> dict[str, Any]:
    evaluation_report = build_prediction_evaluation_report(
        name="replay_prediction_artifact_builder",
        entries=evaluation_entries,
    )
    return build_prediction_calibration_review(
        PredictionCalibrationReviewBuildInput(
            calibration_hint=calibration_hint,
            evaluation_report=evaluation_report,
            diagnostics={
                "caller": "replay_prediction_artifact_builder",
                "review_source": "cumulative_evaluation_entries",
            },
        )
    )


class ReplayPredictionArtifactBuilder:
    def __init__(
        self,
        *,
        exchange: str = "bitflyer",
        symbol_raw: str = "BTC_JPY",
        realized_horizon: str = "5m",
    ) -> None:
        self.exchange = exchange
        self.symbol_raw = symbol_raw
        self.realized_horizon = realized_horizon
        self._pending_prediction_state: dict[str, Any] | None = None
        self._evaluation_entries: list[dict[str, Any]] = []

    def consume_result_artifacts(
        self,
        result: dict[str, Any],
    ) -> dict[str, dict[str, Any] | None]:
        current_prediction_state = build_prediction_state_from_replay_result(
            result,
            exchange=self.exchange,
            symbol_raw=self.symbol_raw,
        )

        evaluation_entry = None
        calibration_review = None
        tactic_proposal_output = None
        tactic_review_record = None
        tactic_operation_record = None

        if self._pending_prediction_state is not None:
            realized_outcome = _build_proxy_realized_outcome(
                current_prediction_state=current_prediction_state,
                previous_mid_price=self._pending_prediction_state.get("mid_price"),
                realized_horizon=self.realized_horizon,
            )
            evaluation_entry = build_prediction_evaluation_entry(
                PredictionEvaluationBuildInput(
                    scenario_output=self._pending_prediction_state["scenario_output"],
                    calibration_hint=self._pending_prediction_state["calibration_hint"],
                    realized_outcome=realized_outcome,
                    diagnostics={
                        "caller": "replay_prediction_artifact_builder",
                        "realized_outcome_source": "next_step_proxy",
                    },
                )
            )
            self._evaluation_entries.append(evaluation_entry)
            calibration_review = _build_prediction_calibration_review_artifact(
                calibration_hint=self._pending_prediction_state["calibration_hint"],
                evaluation_entries=self._evaluation_entries,
            )

            pending_tactic_proposal_output = self._pending_prediction_state[
                "tactic_proposal_output"
            ]
            tactic_proposal_output = _materialize_payload(
                pending_tactic_proposal_output
            )
            pending_tactic_review_record = build_prediction_tactic_review_record(
                PredictionTacticReviewBuildInput(
                    proposal_output=pending_tactic_proposal_output,
                    review_ts=current_prediction_state["scenario_output"].event_ts,
                    decision_state="proposed",
                    decision_reason="replay_compare_capture",
                    operator_note="auto_generated_by_replay_prediction_artifact_builder",
                    diagnostics={
                        "caller": "replay_prediction_artifact_builder",
                        "review_source": "pending_tactic_proposal_output",
                    },
                )
            )
            tactic_review_record = _materialize_payload(pending_tactic_review_record)
            tactic_operation_record = _materialize_payload(
                build_prediction_tactic_operation_record(
                    PredictionTacticOperationBuildInput(
                        review_record=pending_tactic_review_record,
                        operation_ts=current_prediction_state["scenario_output"].event_ts,
                        diagnostics={
                            "caller": "replay_prediction_artifact_builder",
                            "operation_source": "pending_tactic_review_record",
                        },
                    )
                )
            )

        self._pending_prediction_state = current_prediction_state
        return {
            "evaluation_entry": evaluation_entry,
            "calibration_review": calibration_review,
            "tactic_proposal_output": tactic_proposal_output,
            "tactic_review_record": tactic_review_record,
            "tactic_operation_record": tactic_operation_record,
        }

    def consume_result(self, result: dict[str, Any]) -> dict[str, Any] | None:
        artifacts = self.consume_result_artifacts(result)
        return artifacts["evaluation_entry"]