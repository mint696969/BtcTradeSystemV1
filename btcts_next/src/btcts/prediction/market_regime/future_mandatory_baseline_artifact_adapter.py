# path: ./btcts_next/src/btcts/prediction/market_regime/future_mandatory_baseline_artifact_adapter.py
# desc: Read-only MR-F6.4 adapter auditing MR-F5 evidence rows before same-window baseline comparison.

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence, Tuple

from .contracts import MarketRegimeCode
from .future_mandatory_baseline_runner import MandatoryBaselineEvaluationSlot

MARKET_REGIME_MANDATORY_BASELINE_ARTIFACT_ADAPTER_VERSION = (
    "prediction.market_regime.mandatory_baseline_artifact_adapter.mr_f6_4.v1"
)

_REQUIRED_FEATURE_FIELDS: Tuple[str, ...] = (
    "source_timestamp",
    "current_state",
    "previous_state",
    "recent_return",
    "fast_ma",
    "slow_ma",
    "realized_volatility",
    "low_volatility_threshold",
    "high_volatility_threshold",
    "current_forecast_label_selection",
)


def _parse_epoch(value: Any, *, field: str) -> float:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"mandatory_baseline_artifact_timestamp_missing:{field}")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"mandatory_baseline_artifact_timestamp_invalid:{field}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def _regime(value: Any, *, field: str) -> MarketRegimeCode:
    text = str(value or "").strip().upper()
    try:
        return MarketRegimeCode(text)
    except ValueError as exc:
        raise ValueError(f"mandatory_baseline_artifact_regime_invalid:{field}:{text}") from exc


def _probabilities(payload: Any) -> Mapping[MarketRegimeCode, float]:
    if not isinstance(payload, Mapping):
        raise ValueError("mandatory_baseline_artifact_candidate_probability_missing")
    result: dict[MarketRegimeCode, float] = {}
    for raw_state, raw_value in payload.items():
        state = _regime(raw_state, field="candidate_probability_by_state")
        result[state] = float(raw_value)
    return MappingProxyType(result)


def _slot_id(row: Mapping[str, Any], parameter_set_id: str) -> str:
    basis = "|".join((
        str(row.get("origin_timestamp") or ""),
        str(row.get("feature_snapshot_ref") or ""),
        str(row.get("target_horizon_sec") or ""),
        parameter_set_id,
    ))
    return "market_regime_mr_f6_slot:" + sha256(basis.encode("utf-8")).hexdigest()


def _row_blockers(
    row: Mapping[str, Any],
    *,
    feature_snapshots: Mapping[str, Mapping[str, Any]],
    candidate_probabilities_by_trace: Mapping[str, Mapping[str, float]],
) -> Tuple[str, ...]:
    blockers: list[str] = []
    trace_id = str(row.get("trace_id") or "").strip()
    feature_ref = str(row.get("feature_snapshot_ref") or "").strip()
    for field in (
        "trace_id",
        "model_id",
        "parameter_set_id",
        "origin_timestamp",
        "feature_snapshot_ref",
        "target_horizon_sec",
        "target_definition_version",
        "schema_version",
        "predicted_future_state",
        "observed_future_state",
    ):
        if row.get(field) in (None, ""):
            blockers.append(f"evaluation_row_missing:{field}")
    if trace_id and trace_id not in candidate_probabilities_by_trace:
        blockers.append("candidate_probability_by_trace_missing")
    snapshot = feature_snapshots.get(feature_ref) if feature_ref else None
    if snapshot is None:
        blockers.append("feature_snapshot_payload_missing")
    else:
        for field in _REQUIRED_FEATURE_FIELDS:
            if field not in snapshot:
                blockers.append(f"feature_snapshot_field_missing:{field}")
    return tuple(dict.fromkeys(blockers))


def adapt_mr_f5_evidence_batch(
    *,
    batch: Mapping[str, Any],
    evaluation_window_ref: str,
    accepted_parameter_set_id: str,
    feature_snapshots: Mapping[str, Mapping[str, Any]] | None = None,
    candidate_probabilities_by_trace: Mapping[str, Mapping[str, float]] | None = None,
) -> Mapping[str, Any]:
    if not isinstance(batch, Mapping):
        raise ValueError("mandatory_baseline_artifact_batch_type_invalid")
    evaluation_window_ref = str(evaluation_window_ref).strip()
    accepted_parameter_set_id = str(accepted_parameter_set_id).strip()
    if not evaluation_window_ref:
        raise ValueError("mandatory_baseline_artifact_window_ref_missing")
    if not accepted_parameter_set_id:
        raise ValueError("mandatory_baseline_artifact_parameter_set_missing")
    if batch.get("artifact_kind") != "future_shadow_evidence_batch":
        raise ValueError("mandatory_baseline_artifact_kind_invalid")
    if batch.get("canonical_isolated") is not True or batch.get("append_only") is not True:
        raise ValueError("mandatory_baseline_artifact_safety_contract_invalid")
    rows_payload = batch.get("rows")
    if not isinstance(rows_payload, Sequence) or isinstance(rows_payload, (str, bytes)):
        raise ValueError("mandatory_baseline_artifact_rows_invalid")

    snapshots = feature_snapshots or {}
    probabilities = candidate_probabilities_by_trace or {}
    accepted_rows = [
        row for row in rows_payload
        if isinstance(row, Mapping) and str(row.get("parameter_set_id") or "") == accepted_parameter_set_id
    ]
    row_audits = []
    slots = []
    seen_trace_ids: set[str] = set()
    for row in accepted_rows:
        trace_id = str(row.get("trace_id") or "").strip()
        blockers = list(_row_blockers(
            row,
            feature_snapshots=snapshots,
            candidate_probabilities_by_trace=probabilities,
        ))
        if trace_id in seen_trace_ids:
            blockers.append("duplicate_trace_id")
        if trace_id:
            seen_trace_ids.add(trace_id)
        blockers = list(dict.fromkeys(blockers))
        row_audits.append(MappingProxyType({
            "trace_id": trace_id,
            "feature_snapshot_ref": str(row.get("feature_snapshot_ref") or ""),
            "target_horizon_sec": row.get("target_horizon_sec"),
            "adaptable": not blockers,
            "blockers": tuple(blockers),
        }))
        if blockers:
            continue

        feature_ref = str(row["feature_snapshot_ref"])
        feature = snapshots[feature_ref]
        origin_epoch = _parse_epoch(row["origin_timestamp"], field="origin_timestamp")
        source_epoch = _parse_epoch(feature["source_timestamp"], field="source_timestamp")
        slots.append(MandatoryBaselineEvaluationSlot(
            slot_id=_slot_id(row, accepted_parameter_set_id),
            candidate_trace_id=trace_id,
            candidate_model_id=str(row["model_id"]),
            prediction_origin=str(row["origin_timestamp"]),
            prediction_origin_epoch_sec=origin_epoch,
            evaluation_window_ref=evaluation_window_ref,
            source_snapshot_ref=feature_ref,
            source_timestamp_epoch_sec=source_epoch,
            target_horizon_sec=int(row["target_horizon_sec"]),
            target_definition_version=str(row["target_definition_version"]),
            outcome_resolver_version=str(row["schema_version"]),
            candidate_predicted_state=_regime(row["predicted_future_state"], field="predicted_future_state"),
            candidate_probability_by_state=_probabilities(probabilities[trace_id]),
            candidate_prediction_available=str(row.get("forecast_status") or "").upper() == "FORECAST",
            observed_state=_regime(row["observed_future_state"], field="observed_future_state"),
            observation_available=True,
            current_state=_regime(feature["current_state"], field="current_state"),
            previous_state=_regime(feature["previous_state"], field="previous_state"),
            recent_return=None if feature["recent_return"] is None else float(feature["recent_return"]),
            fast_ma=None if feature["fast_ma"] is None else float(feature["fast_ma"]),
            slow_ma=None if feature["slow_ma"] is None else float(feature["slow_ma"]),
            realized_volatility=None if feature["realized_volatility"] is None else float(feature["realized_volatility"]),
            low_volatility_threshold=None if feature["low_volatility_threshold"] is None else float(feature["low_volatility_threshold"]),
            high_volatility_threshold=None if feature["high_volatility_threshold"] is None else float(feature["high_volatility_threshold"]),
            current_forecast_label_selection=_regime(
                feature["current_forecast_label_selection"],
                field="current_forecast_label_selection",
            ),
        ))

    blocker_counts: dict[str, int] = {}
    for audit in row_audits:
        for blocker in audit["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
    batch_blockers = []
    if not accepted_rows:
        batch_blockers.append("accepted_parameter_set_rows_missing")
    if len(slots) != len(accepted_rows):
        batch_blockers.append("one_or_more_rows_not_adaptable")

    return MappingProxyType({
        "schema_version": MARKET_REGIME_MANDATORY_BASELINE_ARTIFACT_ADAPTER_VERSION,
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "mandatory_baseline_artifact_adaptation_audit",
        "evaluation_window_ref": evaluation_window_ref,
        "accepted_parameter_set_id": accepted_parameter_set_id,
        "input_row_count": len(rows_payload),
        "accepted_parameter_set_row_count": len(accepted_rows),
        "adapted_slot_count": len(slots),
        "adaptation_ready": bool(accepted_rows) and len(slots) == len(accepted_rows),
        "batch_blockers": tuple(batch_blockers),
        "blocker_counts": MappingProxyType(dict(sorted(blocker_counts.items()))),
        "row_audits": tuple(row_audits),
        "slots": tuple(slots),
        "safety": MappingProxyType({
            "read_only": True,
            "writes_dhot": False,
            "canonical_replacement": False,
            "parameter_auto_promotion_allowed": False,
            "live_parameter_apply_allowed": False,
        }),
    })
