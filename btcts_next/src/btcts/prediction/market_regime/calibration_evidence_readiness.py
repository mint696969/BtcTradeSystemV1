# path: ./btcts_next/src/btcts/prediction/market_regime/calibration_evidence_readiness.py
# desc: Pure MR-F7 calibration evidence/readiness classification. No runtime I/O, live fitting, UI mutation, D-hot writes, broker, AutoTrade, or parameter apply.

from __future__ import annotations

from collections import defaultdict
import math
from typing import Any, Iterable, Mapping

from .calibration_summary import PRIMARY_TRUSTED_OBSERVATION_SOURCE, REFERENCE_ONLY_OBSERVATION_SOURCE
from .trace_ledger import MARKET_REGIME_SOURCE_FLAG_CONTRIBUTION_LEDGER_VERSION

MARKET_REGIME_CALIBRATION_EVIDENCE_READINESS_VERSION = "prediction.market_regime.calibration_evidence_readiness.mr_f7.v1"

_EVALUABLE_LABELS = {"hit", "partial", "miss"}
_REQUIRED_DETAILED_CONTRIBUTION_FIELDS = {
    "source_id",
    "flag_id",
    "supports_regime",
    "parameter_id",
    "parameter_version",
    "base_reliability",
    "signed_contribution",
    "interaction_adjustment",
    "quality_adjustment",
    "freshness_adjustment",
    "final_contribution",
}


def _normalize_observation_source(row: Mapping[str, Any]) -> str:
    source = str(row.get("observation_source") or "").strip().lower()
    if source in {"candle", "candles", "candle_summary", "derived_candles"}:
        return PRIMARY_TRUSTED_OBSERVATION_SOURCE
    if source in {"latest_cards", "current", "latest_current", "latest_cards_current", ""}:
        return REFERENCE_ONLY_OBSERVATION_SOURCE
    return source


def _horizon_key(row: Mapping[str, Any]) -> str:
    value = str(row.get("horizon_key") or "").strip()
    if value:
        return value
    seconds = int(row.get("horizon_sec") or 0)
    return "current" if seconds == 0 else f"{seconds}s"


def _trace_index(trace_rows: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    index: dict[str, Mapping[str, Any]] = {}
    failures: list[str] = []
    for position, row in enumerate(trace_rows):
        if not isinstance(row, Mapping):
            failures.append(f"trace_{position}_not_mapping")
            continue
        run_id = str(row.get("run_id") or "").strip()
        if not run_id:
            failures.append(f"trace_{position}_run_id_missing")
            continue
        if run_id in index:
            failures.append(f"duplicate_trace_run_id:{run_id}")
            continue
        index[run_id] = row
    return index, failures


def _signal_horizon(trace_row: Mapping[str, Any], horizon_key: str) -> Mapping[str, Any] | None:
    summary = trace_row.get("signal_summary") if isinstance(trace_row.get("signal_summary"), Mapping) else {}
    horizons = summary.get("horizons") if isinstance(summary.get("horizons"), list) else []
    matches = [item for item in horizons if isinstance(item, Mapping) and str(item.get("horizon_key") or "") == horizon_key]
    if len(matches) > 1:
        raise ValueError(f"duplicate_signal_horizon:{horizon_key}")
    return matches[0] if matches else None


def _has_full_contribution_ledger(trace_row: Mapping[str, Any], horizon_key: str) -> tuple[bool, list[Mapping[str, Any]]]:
    summary = trace_row.get("signal_summary") if isinstance(trace_row.get("signal_summary"), Mapping) else {}
    if summary.get("source_flag_contribution_ledger_version") != MARKET_REGIME_SOURCE_FLAG_CONTRIBUTION_LEDGER_VERSION:
        return False, []
    horizon = _signal_horizon(trace_row, horizon_key)
    if horizon is None:
        return False, []
    contributions = horizon.get("source_flag_contributions")
    if not isinstance(contributions, list):
        return False, []
    return True, [item for item in contributions if isinstance(item, Mapping)]


def _detailed_semantics_ready(
    contributions: list[Mapping[str, Any]],
) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    if not contributions:
        return False, ("source_flag_contributions_empty",), ()
    missing: set[str] = set()
    invalid: set[str] = set()
    identity_fields = {"source_id", "flag_id", "supports_regime", "parameter_id", "parameter_version"}
    numeric_fields = {
        "base_reliability",
        "signed_contribution",
        "interaction_adjustment",
        "quality_adjustment",
        "freshness_adjustment",
        "final_contribution",
    }
    for contribution in contributions:
        missing.update(field for field in _REQUIRED_DETAILED_CONTRIBUTION_FIELDS if field not in contribution)
        for field in identity_fields:
            if field in contribution and not str(contribution.get(field) or "").strip():
                invalid.add(field)
        for field in numeric_fields:
            if field not in contribution:
                continue
            value = contribution.get(field)
            if isinstance(value, bool):
                invalid.add(field)
                continue
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                invalid.add(field)
                continue
            if not math.isfinite(numeric):
                invalid.add(field)
                continue
            if field == "base_reliability" and not 0.0 <= numeric <= 1.0:
                invalid.add(field)
    return not missing and not invalid, tuple(sorted(missing)), tuple(sorted(invalid))


def build_market_regime_calibration_evidence_readiness(
    *,
    outcome_rows: Iterable[Mapping[str, Any]],
    trace_rows: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    trace_by_run_id, failures = _trace_index(trace_rows)
    seen_outcomes: set[str] = set()
    counts: dict[str, int] = defaultdict(int)
    by_horizon: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    missing_detailed_fields: set[str] = set()
    invalid_detailed_fields: set[str] = set()
    sample_unmatched_outcome_ids: list[str] = []

    for position, row in enumerate(outcome_rows):
        if not isinstance(row, Mapping):
            failures.append(f"outcome_{position}_not_mapping")
            continue
        counts["outcome_row_count"] += 1
        outcome_id = str(row.get("outcome_id") or "").strip()
        if not outcome_id:
            failures.append(f"outcome_{position}_outcome_id_missing")
            continue
        if outcome_id in seen_outcomes:
            failures.append(f"duplicate_outcome_id:{outcome_id}")
            continue
        seen_outcomes.add(outcome_id)

        horizon_key = _horizon_key(row)
        horizon_counts = by_horizon[horizon_key]
        horizon_counts["outcome_row_count"] += 1
        label = str(row.get("outcome_label") or "unknown").strip().lower()
        evaluable = label in _EVALUABLE_LABELS
        if evaluable:
            counts["evaluable_outcome_count"] += 1
            horizon_counts["evaluable_outcome_count"] += 1
        else:
            counts["non_evaluable_outcome_count"] += 1
            horizon_counts["non_evaluable_outcome_count"] += 1

        observation_source = _normalize_observation_source(row)
        trusted = observation_source == PRIMARY_TRUSTED_OBSERVATION_SOURCE
        reference_only = observation_source == REFERENCE_ONLY_OBSERVATION_SOURCE
        if trusted:
            counts["trusted_outcome_count"] += 1
            horizon_counts["trusted_outcome_count"] += 1
        elif reference_only:
            counts["reference_only_outcome_count"] += 1
            horizon_counts["reference_only_outcome_count"] += 1
        else:
            counts["other_observation_source_count"] += 1
            horizon_counts["other_observation_source_count"] += 1

        run_id = str(row.get("run_id") or "").strip()
        trace_row = trace_by_run_id.get(run_id)
        if trace_row is None:
            counts["unmatched_trace_count"] += 1
            horizon_counts["unmatched_trace_count"] += 1
            if len(sample_unmatched_outcome_ids) < 10:
                sample_unmatched_outcome_ids.append(outcome_id)
            continue
        counts["matched_trace_count"] += 1
        horizon_counts["matched_trace_count"] += 1

        full_ledger, contributions = _has_full_contribution_ledger(trace_row, horizon_key)
        if full_ledger:
            counts["full_contribution_trace_count"] += 1
            horizon_counts["full_contribution_trace_count"] += 1
        else:
            counts["legacy_coarse_trace_count"] += 1
            horizon_counts["legacy_coarse_trace_count"] += 1

        coarse_eligible = evaluable and trusted
        if coarse_eligible:
            counts["coarse_calibration_eligible_count"] += 1
            horizon_counts["coarse_calibration_eligible_count"] += 1

        detailed_ready, missing, invalid = (
            _detailed_semantics_ready(contributions)
            if full_ledger
            else (False, ("full_contribution_ledger_missing",), ())
        )
        missing_detailed_fields.update(missing)
        invalid_detailed_fields.update(invalid)
        if coarse_eligible and full_ledger and detailed_ready:
            counts["detailed_calibration_eligible_count"] += 1
            horizon_counts["detailed_calibration_eligible_count"] += 1

    coarse_ready = counts["coarse_calibration_eligible_count"] > 0
    detailed_ready = counts["detailed_calibration_eligible_count"] > 0
    return {
        "schema_version": "market_regime_calibration_evidence_readiness.mr_f7.v1",
        "readiness_version": MARKET_REGIME_CALIBRATION_EVIDENCE_READINESS_VERSION,
        "prediction_family_id": "market_regime",
        "ok": not failures,
        "failure_count": len(failures),
        "failures": failures,
        "counts": dict(sorted(counts.items())),
        "by_horizon": [
            {"horizon_key": key, **dict(sorted(values.items()))}
            for key, values in sorted(by_horizon.items())
        ],
        "coarse_calibration_ready": coarse_ready,
        "detailed_source_flag_calibration_ready": detailed_ready,
        "missing_detailed_contribution_fields": sorted(missing_detailed_fields),
        "invalid_detailed_contribution_fields": sorted(invalid_detailed_fields),
        "sample_unmatched_outcome_ids": sample_unmatched_outcome_ids,
        "cohort_policy": {
            "trusted_observation_source": PRIMARY_TRUSTED_OBSERVATION_SOURCE,
            "reference_only_observation_source": REFERENCE_ONLY_OBSERVATION_SOURCE,
            "legacy_rows_may_enter_coarse_calibration": True,
            "legacy_rows_may_enter_detailed_source_flag_calibration": False,
            "missing_contribution_semantics_may_be_inferred": False,
            "random_split_allowed": False,
            "runtime_fit_enabled": False,
            "display_confidence_replacement_enabled": False,
        },
        "next_required_actions": (
            []
            if detailed_ready
            else [
                "persist versioned parameter_id and parameter_version per source flag",
                "persist base_reliability and signed/final contribution semantics",
                "persist explicit interaction, quality, and freshness adjustments",
                "accumulate trusted candle outcomes after the enriched trace schema is active",
            ]
        ),
        "safety": {
            "read_only": True,
            "writes_hot_data": False,
            "runtime_fit_enabled": False,
            "scheduler_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "parameter_auto_promotion_allowed": False,
            "would_send_to_broker": False,
        },
    }
