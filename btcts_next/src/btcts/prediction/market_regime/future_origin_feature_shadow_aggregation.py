# path: ./btcts_next/src/btcts/prediction/market_regime/future_origin_feature_shadow_aggregation.py
# desc: MR-F6.12 pure multi-slot aggregation for origin-feature shadow candidates and mandatory baselines.

from __future__ import annotations

from collections import defaultdict
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from .contracts import MarketRegimeCode
from .features.current_l4_origin_feature_shadow_registry import (
    build_default_current_l4_origin_feature_shadow_registry,
)
from .future_mandatory_baseline_comparison import MANDATORY_BASELINE_IDS
from .future_origin_feature_shadow_evaluation import (
    MARKET_REGIME_ORIGIN_FEATURE_SHADOW_EVALUATION_VERSION,
)

MARKET_REGIME_ORIGIN_FEATURE_SHADOW_AGGREGATION_VERSION = (
    "prediction.market_regime.origin_feature_shadow_aggregation.mr_f6_12.v1"
)


def _safe_div(numerator: int, denominator: int) -> float | None:
    return None if denominator <= 0 else round(numerator / denominator, 6)


def _required_text(mapping: Mapping[str, Any], key: str, prefix: str) -> str:
    value = str(mapping.get(key) or "").strip()
    if not value:
        raise ValueError(f"{prefix}_missing:{key}")
    return value


def _comparison_contract(comparison_key: Any) -> tuple[str, int, str, str]:
    if not isinstance(comparison_key, (tuple, list)) or len(comparison_key) != 6:
        raise ValueError("origin_feature_shadow_aggregation_comparison_key_invalid")
    evaluation_window_ref = str(comparison_key[1] or "").strip()
    target_horizon_sec = int(comparison_key[3])
    target_definition_version = str(comparison_key[4] or "").strip()
    outcome_resolver_version = str(comparison_key[5] or "").strip()
    if not evaluation_window_ref or not target_definition_version or not outcome_resolver_version:
        raise ValueError("origin_feature_shadow_aggregation_comparison_contract_missing")
    if target_definition_version != f"market_regime_target.{target_horizon_sec}s.v1":
        raise ValueError("origin_feature_shadow_aggregation_target_definition_mismatch")
    return (
        evaluation_window_ref,
        target_horizon_sec,
        target_definition_version,
        outcome_resolver_version,
    )


def _summary(
    *,
    candidate_id: str,
    baseline_id: str,
    rows: tuple[Mapping[str, Any], ...],
) -> Mapping[str, Any]:
    observed_rows = tuple(row for row in rows if bool(row["observation_available"]))
    scored_rows = tuple(row for row in observed_rows if bool(row["prediction_available"]))
    hits = sum(1 for row in scored_rows if row["hit"] is True)
    unknown_rows = len(observed_rows) - len(scored_rows)
    return MappingProxyType({
        "candidate_id": candidate_id,
        "baseline_id": baseline_id,
        "slot_count": len(rows),
        "observed_slot_count": len(observed_rows),
        "scored_slot_count": len(scored_rows),
        "hit_count": hits,
        "unknown_count": unknown_rows,
        "coverage_rate": _safe_div(len(scored_rows), len(observed_rows)),
        "accuracy": _safe_div(hits, len(scored_rows)),
        "unknown_rate": _safe_div(unknown_rows, len(observed_rows)),
    })


def build_origin_feature_shadow_aggregation(
    *,
    evaluations: Iterable[Mapping[str, Any]],
) -> Mapping[str, Any]:
    safe_evaluations = tuple(evaluations)
    if not safe_evaluations:
        raise ValueError("origin_feature_shadow_aggregation_evaluations_empty")

    seen_slot_ids: set[str] = set()
    seen_comparison_keys: set[tuple[Any, ...]] = set()
    reference_contract: tuple[str, int, str, str] | None = None
    reference_candidate_ids: tuple[str, ...] | None = None
    canonical_candidates = build_default_current_l4_origin_feature_shadow_registry()
    canonical_candidate_ids = tuple(item.candidate_id for item in canonical_candidates)
    canonical_candidate_by_id = {item.candidate_id: item for item in canonical_candidates}
    by_candidate_baseline: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)

    for evaluation in safe_evaluations:
        if not isinstance(evaluation, Mapping):
            raise ValueError("origin_feature_shadow_aggregation_evaluation_type_invalid")
        if evaluation.get("schema_version") != MARKET_REGIME_ORIGIN_FEATURE_SHADOW_EVALUATION_VERSION:
            raise ValueError("origin_feature_shadow_aggregation_evaluation_schema_mismatch")
        if evaluation.get("artifact_kind") != "origin_feature_shadow_same_slot_evaluation":
            raise ValueError("origin_feature_shadow_aggregation_artifact_kind_mismatch")
        if evaluation.get("evaluation_ready") is not True:
            raise ValueError("origin_feature_shadow_aggregation_evaluation_not_ready")
        if evaluation.get("candidate_count") != 8:
            raise ValueError("origin_feature_shadow_aggregation_candidate_count_mismatch")
        if evaluation.get("selection_performed") is not False or evaluation.get("selected_candidate_id") is not None:
            raise ValueError("origin_feature_shadow_aggregation_selected_input_not_allowed")
        for field in (
            "writes_dhot",
            "scheduler_enabled",
            "live_parameter_apply_allowed",
            "auto_promotion_allowed",
            "canonical_replacement_allowed",
        ):
            if evaluation.get(field) is not False:
                raise ValueError(f"origin_feature_shadow_aggregation_unsafe_evaluation_flag:{field}")

        slot_id = _required_text(evaluation, "slot_id", "origin_feature_shadow_aggregation")
        if slot_id in seen_slot_ids:
            raise ValueError(f"origin_feature_shadow_aggregation_duplicate_slot_id:{slot_id}")
        seen_slot_ids.add(slot_id)

        raw_comparison_key = evaluation.get("comparison_key")
        if not isinstance(raw_comparison_key, (tuple, list)):
            raise ValueError("origin_feature_shadow_aggregation_comparison_key_invalid")
        comparison_key = tuple(raw_comparison_key)
        if comparison_key in seen_comparison_keys:
            raise ValueError("origin_feature_shadow_aggregation_duplicate_comparison_key")
        seen_comparison_keys.add(comparison_key)
        contract = _comparison_contract(comparison_key)
        if reference_contract is None:
            reference_contract = contract
        elif contract != reference_contract:
            raise ValueError("origin_feature_shadow_aggregation_mixed_comparison_contract")

        projections = evaluation.get("candidate_projections")
        if not isinstance(projections, (tuple, list)) or len(projections) != 8:
            raise ValueError("origin_feature_shadow_aggregation_candidate_projection_count_invalid")
        candidate_ids = tuple(str(item.get("candidate_id") or "").strip() for item in projections)
        if any(not item for item in candidate_ids) or len(set(candidate_ids)) != 8:
            raise ValueError("origin_feature_shadow_aggregation_candidate_ids_invalid")
        if candidate_ids != canonical_candidate_ids:
            raise ValueError("origin_feature_shadow_aggregation_candidate_registry_not_canonical")
        if reference_candidate_ids is None:
            reference_candidate_ids = candidate_ids
        elif candidate_ids != reference_candidate_ids:
            raise ValueError("origin_feature_shadow_aggregation_candidate_registry_mismatch")

        observed_state = evaluation.get("observed_state")
        observation_available = evaluation.get("observation_available")
        if not isinstance(observed_state, MarketRegimeCode):
            raise ValueError("origin_feature_shadow_aggregation_observed_state_invalid")
        if not isinstance(observation_available, bool):
            raise ValueError("origin_feature_shadow_aggregation_observation_availability_invalid")
        if observation_available and observed_state is MarketRegimeCode.UNKNOWN:
            raise ValueError("origin_feature_shadow_aggregation_available_observation_unknown")
        if not observation_available and observed_state is not MarketRegimeCode.UNKNOWN:
            raise ValueError("origin_feature_shadow_aggregation_unavailable_observation_not_unknown")

        for projection in projections:
            candidate_id = _required_text(projection, "candidate_id", "origin_feature_shadow_aggregation")
            canonical_candidate = canonical_candidate_by_id[candidate_id]
            if projection.get("parameter_set_id") != canonical_candidate.parameters.parameter_set_id:
                raise ValueError("origin_feature_shadow_aggregation_parameter_set_identity_mismatch")
            calculated_features = projection.get("calculated_features")
            if not isinstance(calculated_features, Mapping):
                raise ValueError("origin_feature_shadow_aggregation_calculated_features_invalid")
            expected_parameters = canonical_candidate.parameters
            expected_feature_contract = {
                "parameter_set_id": expected_parameters.parameter_set_id,
                "fast_ma_window_rows": expected_parameters.fast_ma_window_rows,
                "slow_ma_window_rows": expected_parameters.slow_ma_window_rows,
                "low_volatility_threshold_bps": expected_parameters.low_volatility_threshold_bps,
                "high_volatility_threshold_bps": expected_parameters.high_volatility_threshold_bps,
            }
            for field, expected in expected_feature_contract.items():
                if calculated_features.get(field) != expected:
                    raise ValueError(
                        f"origin_feature_shadow_aggregation_calculated_feature_contract_mismatch:{field}"
                    )
            for field in (
                "selected_for_runtime",
                "live_parameter_apply_allowed",
                "auto_promotion_allowed",
                "canonical_replacement_allowed",
            ):
                if projection.get(field) is not False:
                    raise ValueError(f"origin_feature_shadow_aggregation_unsafe_projection_flag:{field}")
            if tuple(projection.get("comparison_key") or ()) != comparison_key:
                raise ValueError("origin_feature_shadow_aggregation_projection_key_mismatch")
            predictions = projection.get("baseline_predictions")
            if not isinstance(predictions, (tuple, list)) or len(predictions) != len(MANDATORY_BASELINE_IDS):
                raise ValueError("origin_feature_shadow_aggregation_baseline_count_invalid")
            baseline_ids = tuple(str(row.get("baseline_id") or "").strip() for row in predictions)
            if baseline_ids != MANDATORY_BASELINE_IDS:
                raise ValueError("origin_feature_shadow_aggregation_baseline_order_or_identity_mismatch")

            for row in predictions:
                if row.get("observed_state") is not observed_state:
                    raise ValueError("origin_feature_shadow_aggregation_observed_state_mismatch")
                row_observation_available = row.get("observation_available")
                if not isinstance(row_observation_available, bool):
                    raise ValueError("origin_feature_shadow_aggregation_row_observation_availability_invalid")
                if row_observation_available is not observation_available:
                    raise ValueError("origin_feature_shadow_aggregation_observation_availability_mismatch")
                prediction_available = row.get("prediction_available")
                if not isinstance(prediction_available, bool):
                    raise ValueError("origin_feature_shadow_aggregation_prediction_availability_invalid")
                predicted_state = row.get("predicted_state")
                if not isinstance(predicted_state, MarketRegimeCode):
                    raise ValueError("origin_feature_shadow_aggregation_predicted_state_invalid")
                hit = row.get("hit")
                if observation_available and prediction_available:
                    expected_hit = predicted_state is observed_state
                    if hit is not expected_hit:
                        raise ValueError("origin_feature_shadow_aggregation_hit_mismatch")
                elif hit is not None:
                    raise ValueError("origin_feature_shadow_aggregation_hit_present_when_unscored")
                baseline_id = str(row["baseline_id"])
                by_candidate_baseline[(candidate_id, baseline_id)].append(row)

    assert reference_contract is not None
    assert reference_candidate_ids is not None
    expected_pairs = {
        (candidate_id, baseline_id)
        for candidate_id in reference_candidate_ids
        for baseline_id in MANDATORY_BASELINE_IDS
    }
    if set(by_candidate_baseline) != expected_pairs:
        raise RuntimeError("origin_feature_shadow_aggregation_pair_matrix_incomplete")

    summaries = tuple(
        _summary(
            candidate_id=candidate_id,
            baseline_id=baseline_id,
            rows=tuple(by_candidate_baseline[(candidate_id, baseline_id)]),
        )
        for candidate_id in reference_candidate_ids
        for baseline_id in MANDATORY_BASELINE_IDS
    )
    candidate_summaries = tuple(MappingProxyType({
        "candidate_id": candidate_id,
        "baseline_summaries": tuple(
            item for item in summaries if item["candidate_id"] == candidate_id
        ),
    }) for candidate_id in reference_candidate_ids)

    return MappingProxyType({
        "schema_version": MARKET_REGIME_ORIGIN_FEATURE_SHADOW_AGGREGATION_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "origin_feature_shadow_multi_slot_aggregation",
        "evaluation_slot_count": len(safe_evaluations),
        "candidate_count": len(reference_candidate_ids),
        "baseline_count": len(MANDATORY_BASELINE_IDS),
        "candidate_baseline_pair_count": len(summaries),
        "comparison_contract": MappingProxyType({
            "evaluation_window_ref": reference_contract[0],
            "target_horizon_sec": reference_contract[1],
            "target_definition_version": reference_contract[2],
            "outcome_resolver_version": reference_contract[3],
        }),
        "candidate_ids": reference_candidate_ids,
        "baseline_ids": MANDATORY_BASELINE_IDS,
        "candidate_summaries": candidate_summaries,
        "pair_summaries": summaries,
        "aggregation_ready": True,
        "ranking_performed": False,
        "selection_performed": False,
        "selected_candidate_id": None,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
    })
