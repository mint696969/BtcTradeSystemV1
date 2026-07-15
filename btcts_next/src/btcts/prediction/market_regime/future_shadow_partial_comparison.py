# path: ./btcts_next/src/btcts/prediction/market_regime/future_shadow_partial_comparison.py
# desc: MR-F8.13 honest partial same-window comparison for paired runtime outcomes when full probability and multi-origin evidence is unavailable.

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping as MappingABC, Sequence
from types import MappingProxyType
from typing import Any, Mapping

VERSION = "prediction.market_regime.future_shadow_partial_comparison.mr_f8_13.v1"


def build_future_shadow_partial_comparison(
    *,
    runtime_preflight_result: Mapping[str, Any],
    outcome_intake_report: Mapping[str, Any],
    evaluated_at: str,
) -> Mapping[str, Any]:
    preflight = runtime_preflight_result.get("preflight_report")
    if not isinstance(preflight, MappingABC):
        raise ValueError("partial_comparison_preflight_invalid")
    pairs = preflight.get("pairs")
    if not isinstance(pairs, Sequence) or isinstance(pairs, (str, bytes)) or len(pairs) != 7:
        raise ValueError("partial_comparison_pairs_invalid")
    rows = outcome_intake_report.get("outcome_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or len(rows) != 14:
        raise ValueError("partial_comparison_outcome_rows_invalid")

    pair_origins = {str(pair.get("slot_identity", {}).get("origin_timestamp") or "") for pair in pairs if isinstance(pair, MappingABC)}
    pair_snapshots = {str(pair.get("slot_identity", {}).get("feature_snapshot_ref") or "") for pair in pairs if isinstance(pair, MappingABC)}
    if len(pair_origins) != 1 or "" in pair_origins:
        raise ValueError("partial_comparison_origin_mismatch")
    if len(pair_snapshots) != 1 or "" in pair_snapshots:
        raise ValueError("partial_comparison_snapshot_mismatch")

    candidate_slots: dict[str, str] = {}
    trace_candidates: dict[str, str] = {}
    for pair in pairs:
        if not isinstance(pair, MappingABC):
            raise ValueError("partial_comparison_pair_invalid")
        identities = pair.get("candidate_identities")
        forecasts = pair.get("forecasts")
        if (
            not isinstance(identities, Sequence)
            or isinstance(identities, (str, bytes))
            or len(identities) != 2
        ):
            raise ValueError("partial_comparison_candidate_identities_invalid")
        if (
            not isinstance(forecasts, Sequence)
            or isinstance(forecasts, (str, bytes))
            or len(forecasts) != 2
        ):
            raise ValueError("partial_comparison_forecasts_invalid")
        for identity in identities:
            if not isinstance(identity, MappingABC):
                raise ValueError("partial_comparison_candidate_identity_invalid")
            candidate_id = str(identity.get("parameter_set_id") or "")
            slot = str(identity.get("registry_role") or "")
            if not candidate_id or slot not in {"active", "shadow"}:
                raise ValueError("partial_comparison_candidate_identity_invalid")
            existing = candidate_slots.get(candidate_id)
            if existing is not None and existing != slot:
                raise ValueError("partial_comparison_candidate_role_mismatch")
            candidate_slots[candidate_id] = slot
        for forecast in forecasts:
            if not isinstance(forecast, MappingABC):
                raise ValueError("partial_comparison_forecast_invalid")
            trace_id = str(forecast.get("trace_id") or "")
            candidate_id = str(forecast.get("parameter_set_id") or "")
            if not trace_id or candidate_id not in candidate_slots:
                raise ValueError("partial_comparison_forecast_identity_invalid")
            existing = trace_candidates.get(trace_id)
            if existing is not None and existing != candidate_id:
                raise ValueError("partial_comparison_trace_candidate_mismatch")
            trace_candidates[trace_id] = candidate_id

    if set(candidate_slots.values()) != {"active", "shadow"} or len(candidate_slots) != 2:
        raise ValueError("partial_comparison_candidate_set_invalid")
    if len(trace_candidates) != 14:
        raise ValueError("partial_comparison_trace_set_invalid")

    by_candidate: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        if not isinstance(row, MappingABC):
            raise ValueError("partial_comparison_outcome_row_invalid")
        candidate_id = str(row.get("parameter_set_id") or "")
        trace_id = str(row.get("trace_id") or "")
        if candidate_id not in candidate_slots or trace_candidates.get(trace_id) != candidate_id:
            raise ValueError("partial_comparison_candidate_identity_invalid")
        by_candidate[candidate_id].append(row)

    if len(by_candidate) != 2 or sorted(len(items) for items in by_candidate.values()) != [7, 7]:
        raise ValueError("partial_comparison_candidate_row_count_invalid")

    summaries = []
    for candidate_id, candidate_rows in sorted(by_candidate.items(), key=lambda item: candidate_slots[item[0]]):
        counts = Counter(str(row.get("outcome_status") or "") for row in candidate_rows)
        resolved = sum(
            value
            for key, value in counts.items()
            if key not in {"UNRESOLVED", "INVALIDATED"}
        )
        resolved_non_abstained = counts.get("CORRECT", 0) + counts.get("INCORRECT", 0)
        correct = counts.get("CORRECT", 0)
        summaries.append(MappingProxyType({
            "candidate_id": candidate_id,
            "candidate_slot": candidate_slots[candidate_id],
            "slot_count": len(candidate_rows),
            "resolved_slot_count": resolved,
            "coverage_rate": resolved_non_abstained / len(candidate_rows),
            "abstention_rate": counts.get("ABSTAINED", 0) / len(candidate_rows),
            "unresolved_rate": counts.get("UNRESOLVED", 0) / len(candidate_rows),
            "accuracy_on_resolved_non_abstained": (
                correct / resolved_non_abstained if resolved_non_abstained else None
            ),
            "status_counts": MappingProxyType(dict(sorted(counts.items()))),
        }))

    unavailable_metrics = MappingProxyType({
        "balanced_accuracy": "unavailable_insufficient_class_support",
        "macro_f1": "unavailable_insufficient_class_support",
        "brier_score": "unavailable_probability_distribution_not_persisted_in_legacy_runtime_artifact",
        "log_loss": "unavailable_probability_distribution_not_persisted_in_legacy_runtime_artifact",
        "expected_calibration_error": "unavailable_probability_distribution_not_persisted_in_legacy_runtime_artifact",
        "state_churn": "unavailable_single_origin",
        "transition_detection_delay": "unavailable_single_origin",
        "condition_specific_performance": "partial_horizon_only",
    })
    blockers = (
        "minimum_observed_slots_not_met",
        "full_horizon_window_incomplete",
        "probability_metrics_unavailable_for_legacy_origin",
        "multi_origin_churn_and_transition_delay_unavailable",
    )
    return MappingProxyType({
        "schema_version": VERSION,
        "artifact_kind": "future_shadow_partial_comparison_report",
        "evaluated_at": evaluated_at,
        "prediction_origin": next(iter(pair_origins)),
        "feature_snapshot_ref": next(iter(pair_snapshots)),
        "same_window_comparison": True,
        "same_source_snapshot": True,
        "candidate_count": 2,
        "pair_count": 7,
        "outcome_row_count": 14,
        "candidate_summaries": tuple(summaries),
        "unavailable_metrics": unavailable_metrics,
        "decision": "insufficient_evidence",
        "selected_candidate_id": None,
        "rollback_candidate_id": next(
            summary["candidate_id"] for summary in summaries if summary["candidate_slot"] == "active"
        ),
        "comparison_blockers": blockers,
        "human_approval_required": True,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
        "proposal_is_not_runtime_activation": True,
        "read_only_inputs": True,
        "writes_dhot": False,
    })
