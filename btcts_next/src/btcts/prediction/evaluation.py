# path: ./btcts_next/src/btcts/prediction/evaluation.py
# desc: Offline/replay-only Prediction System evaluation contracts and in-memory builders. No collection, writes, broker, mode, grant, or execution behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping, Tuple

from .forecast_ledger import ForecastLedgerBatch, ForecastLedgerRecord

LOGIC_VERSION = "prediction_evaluation.ps_p3.v1"


@dataclass(frozen=True)
class PredictionEvaluationRecord:
    evaluation_record_id: str
    evaluation_version: str
    generated_at: str
    prediction_run_id: str
    prediction_generated_at: str
    market_uid: str
    source_prediction_ref: str | None
    source_forecast_record_ref: str | None
    family: str
    horizon_sec: int
    horizon_label: str
    horizon_key: str
    predicted_label: str
    predicted_score: float | None
    predicted_confidence: str
    predicted_caution_level: str | None
    predicted_trigger_eligibility_state: str
    scenario_switch_hint: str | None
    refresh_required: bool | None
    evaluation_window_start: str
    evaluation_window_end: str
    outcome_source_ref: str | None
    outcome_available: bool
    observed_start_price: float | None
    observed_end_price: float | None
    observed_return_bps: float | None
    observed_direction: str
    adverse_excursion_bps: float | None
    favorable_excursion_bps: float | None
    hit_label: str
    timing_label: str
    confidence_bucket: str
    caution_bucket: str
    not_evaluable_reason: str | None
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    autotrade_decision_append_requested: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["usable"] = self.usable
        data["logic_version"] = LOGIC_VERSION
        return data


@dataclass(frozen=True)
class PredictionEvaluationReport:
    evaluation_report_id: str
    evaluation_version: str
    generated_at: str
    market_uid: str
    source_ref: str | None
    evaluation_window_start: str | None
    evaluation_window_end: str | None
    records: Tuple[PredictionEvaluationRecord, ...] = ()
    input_prediction_count: int = 0
    input_forecast_record_count: int = 0
    evaluated_record_count: int = 0
    skipped_record_count: int = 0
    not_evaluable_count: int = 0
    family_summary: Mapping[str, Any] = field(default_factory=dict)
    horizon_summary: Mapping[str, Any] = field(default_factory=dict)
    confidence_summary: Mapping[str, Any] = field(default_factory=dict)
    caution_summary: Mapping[str, Any] = field(default_factory=dict)
    scenario_switch_summary: Mapping[str, Any] = field(default_factory=dict)
    refresh_required_summary: Mapping[str, Any] = field(default_factory=dict)
    data_quality_notes: Tuple[str, ...] = ()
    calibration_candidate_notes: Tuple[str, ...] = ()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    autotrade_decision_append_requested: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evaluation_report_id": self.evaluation_report_id,
            "evaluation_version": self.evaluation_version,
            "generated_at": self.generated_at,
            "market_uid": self.market_uid,
            "source_ref": self.source_ref,
            "evaluation_window_start": self.evaluation_window_start,
            "evaluation_window_end": self.evaluation_window_end,
            "records": [record.to_dict() for record in self.records],
            "input_prediction_count": self.input_prediction_count,
            "input_forecast_record_count": self.input_forecast_record_count,
            "evaluated_record_count": self.evaluated_record_count,
            "skipped_record_count": self.skipped_record_count,
            "not_evaluable_count": self.not_evaluable_count,
            "family_summary": dict(self.family_summary),
            "horizon_summary": dict(self.horizon_summary),
            "confidence_summary": dict(self.confidence_summary),
            "caution_summary": dict(self.caution_summary),
            "scenario_switch_summary": dict(self.scenario_switch_summary),
            "refresh_required_summary": dict(self.refresh_required_summary),
            "data_quality_notes": list(self.data_quality_notes),
            "calibration_candidate_notes": list(self.calibration_candidate_notes),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "broker_execution_requested": self.broker_execution_requested,
            "mode_apply_requested": self.mode_apply_requested,
            "command_ledger_append_requested": self.command_ledger_append_requested,
            "autotrade_decision_append_requested": self.autotrade_decision_append_requested,
            "logic_version": LOGIC_VERSION,
        }


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _record_to_dict(record: ForecastLedgerRecord | Mapping[str, Any]) -> Dict[str, Any]:
    if isinstance(record, ForecastLedgerRecord):
        return record.to_dict()
    return dict(record)


def _forecast_records(forecast_batch: ForecastLedgerBatch | Mapping[str, Any] | Iterable[Mapping[str, Any]] | None) -> tuple[Dict[str, Any], ...]:
    if forecast_batch is None:
        return tuple()
    if isinstance(forecast_batch, ForecastLedgerBatch):
        return tuple(record.to_dict() for record in forecast_batch.records)
    if isinstance(forecast_batch, Mapping):
        records = forecast_batch.get("records")
        if isinstance(records, Iterable) and not isinstance(records, (str, bytes, Mapping)):
            return tuple(dict(item) for item in records if isinstance(item, Mapping))
        return (dict(forecast_batch),)
    return tuple(dict(item) for item in forecast_batch if isinstance(item, Mapping))


def _prediction_snapshot(snapshot: Mapping[str, Any] | None) -> Dict[str, Any]:
    return dict(snapshot or {})


def _market_uid(snapshot: Mapping[str, Any], default: str = "BTC_JPY:bitFlyer") -> str:
    system_input = dict(snapshot.get("system_input") or {})
    run_identity = dict(snapshot.get("run_identity") or {})
    return str(system_input.get("market_uid") or run_identity.get("market_uid") or default)


def _prediction_run_id(snapshot: Mapping[str, Any]) -> str:
    run_identity = dict(snapshot.get("run_identity") or {})
    return str(run_identity.get("prediction_run_id") or snapshot.get("prediction_run_id") or "unknown_prediction_run")


def _prediction_generated_at(snapshot: Mapping[str, Any], fallback: str) -> str:
    run_identity = dict(snapshot.get("run_identity") or {})
    return str(run_identity.get("generated_at") or snapshot.get("generated_at") or fallback)


def _outcome_key(family: str, horizon_sec: int) -> str:
    return f"{family}:{int(horizon_sec)}"


def _normalize_outcome_windows(outcome_windows: Mapping[str, Mapping[str, Any]] | Iterable[Mapping[str, Any]] | None) -> dict[str, Dict[str, Any]]:
    if outcome_windows is None:
        return {}
    out: dict[str, Dict[str, Any]] = {}
    if isinstance(outcome_windows, Mapping):
        for key, value in outcome_windows.items():
            if isinstance(value, Mapping):
                row = dict(value)
                out[str(key)] = row
                family = row.get("family")
                horizon = row.get("horizon_sec")
                if family is not None and horizon is not None:
                    out[_outcome_key(str(family), int(horizon))] = row
        return out
    for item in outcome_windows:
        if not isinstance(item, Mapping):
            continue
        row = dict(item)
        family = row.get("family")
        horizon = row.get("horizon_sec")
        if family is not None and horizon is not None:
            out[_outcome_key(str(family), int(horizon))] = row
        for key_name in ("prediction_id", "forecast_record_id", "record_id", "outcome_id"):
            key_value = row.get(key_name)
            if key_value:
                out[str(key_value)] = row
    return out


def _lookup_outcome(record: Mapping[str, Any], outcomes: Mapping[str, Dict[str, Any]]) -> Dict[str, Any] | None:
    keys = (
        str(record.get("record_id") or ""),
        str(record.get("forecast_record_id") or ""),
        str(record.get("prediction_id") or ""),
        _outcome_key(str(record.get("family") or "unknown"), int(record.get("horizon_sec") or 0)),
    )
    for key in keys:
        if key and key in outcomes:
            return dict(outcomes[key])
    return None


def _observed_return_bps(start: float | None, end: float | None) -> float | None:
    if start is None or end is None or start <= 0:
        return None
    return round(((end - start) / start) * 10_000.0, 6)


def _direction(return_bps: float | None, flat_threshold_bps: float) -> str:
    if return_bps is None:
        return "unknown"
    if return_bps > flat_threshold_bps:
        return "up"
    if return_bps < -flat_threshold_bps:
        return "down"
    return "flat"


def _predicted_direction(label: str) -> str:
    if label in ("long_bias", "breakout_candidate", "participation_candidate", "directional_algorithmic_flow_watch"):
        return "up"
    if label in ("short_bias",):
        return "down"
    if label in ("no_edge", "neutral_bias", "range_candidate", "normal_risk", "macro_context_neutral"):
        return "flat"
    return "unknown"


def _hit_label(predicted_label: str, observed_direction: str, not_evaluable_reason: str | None) -> str:
    if not_evaluable_reason is not None:
        return "not_evaluable"
    if observed_direction in ("unknown",):
        return "not_evaluable"
    if observed_direction == "flat":
        return "neutral_or_flat"
    predicted = _predicted_direction(predicted_label)
    if predicted == "unknown":
        return "wrong_direction"
    return "correct_direction" if predicted == observed_direction else "wrong_direction"


def _bucket(value: Any) -> str:
    text = str(value or "unknown").lower()
    if text in ("low", "medium", "high", "blocked"):
        return text
    return "unknown"


def _excursions(start: float | None, min_price: float | None, max_price: float | None, predicted_label: str) -> tuple[float | None, float | None]:
    if start is None or start <= 0:
        return None, None
    up_favorable = _observed_return_bps(start, max_price) if max_price is not None else None
    up_adverse = _observed_return_bps(start, min_price) if min_price is not None else None
    if _predicted_direction(predicted_label) == "down":
        favorable = -up_adverse if up_adverse is not None else None
        adverse = -up_favorable if up_favorable is not None else None
        return adverse, favorable
    return up_adverse, up_favorable


def _record_from_forecast(
    *,
    record: Mapping[str, Any],
    outcome: Mapping[str, Any] | None,
    generated_at: str,
    prediction_run_id: str,
    prediction_generated_at: str,
    market_uid: str,
    source_prediction_ref: str | None,
    flat_threshold_bps: float,
) -> PredictionEvaluationRecord:
    family = str(record.get("family") or "unknown")
    horizon_sec = int(record.get("horizon_sec") or 0)
    predicted_label = str(record.get("primary_label") or record.get("predicted_label") or "unknown")
    values = dict(record.get("values_snapshot") or record.get("values") or {})
    outcome_row = dict(outcome or {})
    start = _float_or_none(outcome_row.get("observed_start_price") or outcome_row.get("start_price"))
    end = _float_or_none(outcome_row.get("observed_end_price") or outcome_row.get("end_price"))
    min_price = _float_or_none(outcome_row.get("observed_min_price") or outcome_row.get("min_price") or start)
    max_price = _float_or_none(outcome_row.get("observed_max_price") or outcome_row.get("max_price") or end)
    return_bps = _observed_return_bps(start, end)
    outcome_available = outcome is not None
    blockers = list(record.get("blockers") or [])
    warnings = list(record.get("warnings") or [])
    not_evaluable_reason: str | None = None
    if not outcome_available:
        not_evaluable_reason = "outcome_window_missing"
    elif start is None or end is None or start <= 0:
        not_evaluable_reason = "outcome_price_invalid"
    elif predicted_label in ("", "unknown"):
        not_evaluable_reason = "prediction_label_missing"
    if not_evaluable_reason:
        blockers.append(not_evaluable_reason)
    trigger_state = str(values.get("trigger_eligibility_state") or values.get("predicted_trigger_eligibility_state") or "blocked")
    if trigger_state != "blocked":
        warnings.append("prediction_trigger_eligibility_state_not_blocked")
    observed_direction = _direction(return_bps, flat_threshold_bps)
    adverse, favorable = _excursions(start, min_price, max_price, predicted_label)
    hit = _hit_label(predicted_label, observed_direction, not_evaluable_reason)
    eval_start = str(outcome_row.get("evaluation_window_start") or outcome_row.get("window_start") or "")
    eval_end = str(outcome_row.get("evaluation_window_end") or outcome_row.get("window_end") or "")
    source_forecast_record_ref = str(record.get("record_id") or record.get("forecast_record_id") or "") or None
    evaluation_record_id = f"{LOGIC_VERSION}:{prediction_run_id}:{source_forecast_record_ref or family}:{horizon_sec}s"
    return PredictionEvaluationRecord(
        evaluation_record_id=evaluation_record_id,
        evaluation_version=LOGIC_VERSION,
        generated_at=generated_at,
        prediction_run_id=prediction_run_id,
        prediction_generated_at=prediction_generated_at,
        market_uid=market_uid,
        source_prediction_ref=source_prediction_ref,
        source_forecast_record_ref=source_forecast_record_ref,
        family=family,
        horizon_sec=horizon_sec,
        horizon_label=str(record.get("horizon_label") or f"{horizon_sec}s"),
        horizon_key=str(record.get("horizon_key") or f"{horizon_sec}s"),
        predicted_label=predicted_label,
        predicted_score=_float_or_none(record.get("score") if "score" in record else record.get("predicted_score")),
        predicted_confidence=str(record.get("confidence") or record.get("predicted_confidence") or "unknown"),
        predicted_caution_level=str(values.get("caution_level") or values.get("predicted_caution_level") or "unknown"),
        predicted_trigger_eligibility_state=trigger_state,
        scenario_switch_hint=str(values.get("scenario_switch_hint") or "") or None,
        refresh_required=bool(values.get("refresh_required")) if "refresh_required" in values else None,
        evaluation_window_start=eval_start,
        evaluation_window_end=eval_end,
        outcome_source_ref=str(outcome_row.get("outcome_source_ref") or outcome_row.get("source_ref") or "") or None,
        outcome_available=outcome_available,
        observed_start_price=start,
        observed_end_price=end,
        observed_return_bps=return_bps,
        observed_direction=observed_direction,
        adverse_excursion_bps=adverse,
        favorable_excursion_bps=favorable,
        hit_label=hit,
        timing_label="not_evaluable" if hit == "not_evaluable" else "timely",
        confidence_bucket=_bucket(record.get("confidence") or record.get("predicted_confidence")),
        caution_bucket="blocked" if blockers and not_evaluable_reason is None else _bucket(values.get("caution_level") or values.get("predicted_caution_level")),
        not_evaluable_reason=not_evaluable_reason,
        blockers=tuple(dict.fromkeys(str(item) for item in blockers)),
        warnings=tuple(dict.fromkeys(str(item) for item in warnings)),
    )


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator > 0 else None


def _avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 6) if values else None


def _summary_by_key(records: Tuple[PredictionEvaluationRecord, ...], key: str) -> Dict[str, Any]:
    values = tuple(dict.fromkeys(str(getattr(record, key)) for record in records))
    hit_rate: Dict[str, float | None] = {}
    avg_return: Dict[str, float | None] = {}
    adverse: Dict[str, float | None] = {}
    not_eval: Dict[str, int] = {}
    for value in values:
        group = [record for record in records if str(getattr(record, key)) == value]
        evaluable = [record for record in group if record.hit_label != "not_evaluable"]
        hit_rate[value] = _rate(sum(1 for record in evaluable if record.hit_label == "correct_direction"), len(evaluable))
        avg_return[value] = _avg([float(record.observed_return_bps) for record in group if record.observed_return_bps is not None])
        adverse[value] = _avg([float(record.adverse_excursion_bps) for record in group if record.adverse_excursion_bps is not None])
        not_eval[value] = sum(1 for record in group if record.hit_label == "not_evaluable")
    return {
        "directional_hit_rate": hit_rate,
        "average_return_bps": avg_return,
        "adverse_excursion_bps": adverse,
        "not_evaluable_count": not_eval,
    }


def _bucket_summary(records: Tuple[PredictionEvaluationRecord, ...], key: str) -> Dict[str, Any]:
    values = tuple(dict.fromkeys(str(getattr(record, key)) for record in records))
    hit_rate: Dict[str, float | None] = {}
    avg_return: Dict[str, float | None] = {}
    not_eval: Dict[str, int] = {}
    for value in values:
        group = [record for record in records if str(getattr(record, key)) == value]
        evaluable = [record for record in group if record.hit_label != "not_evaluable"]
        hit_rate[value] = _rate(sum(1 for record in evaluable if record.hit_label == "correct_direction"), len(evaluable))
        avg_return[value] = _avg([float(record.observed_return_bps) for record in group if record.observed_return_bps is not None])
        not_eval[value] = sum(1 for record in group if record.hit_label == "not_evaluable")
    return {"hit_rate": hit_rate, "average_return_bps": avg_return, "not_evaluable_count": not_eval}


def build_prediction_evaluation_records(
    *,
    forecast_batch: ForecastLedgerBatch | Mapping[str, Any] | Iterable[Mapping[str, Any]] | None,
    outcome_windows: Mapping[str, Mapping[str, Any]] | Iterable[Mapping[str, Any]] | None,
    prediction_snapshot: Mapping[str, Any] | None = None,
    now: datetime | None = None,
    source_prediction_ref: str | None = None,
    flat_threshold_bps: float = 1.0,
) -> Tuple[PredictionEvaluationRecord, ...]:
    generated_at = _generated_at(now)
    snapshot = _prediction_snapshot(prediction_snapshot)
    records = _forecast_records(forecast_batch)
    outcomes = _normalize_outcome_windows(outcome_windows)
    run_id = _prediction_run_id(snapshot)
    prediction_generated_at = _prediction_generated_at(snapshot, generated_at)
    market_uid = _market_uid(snapshot)
    return tuple(
        _record_from_forecast(
            record=record,
            outcome=_lookup_outcome(record, outcomes),
            generated_at=generated_at,
            prediction_run_id=run_id,
            prediction_generated_at=prediction_generated_at,
            market_uid=market_uid,
            source_prediction_ref=source_prediction_ref,
            flat_threshold_bps=flat_threshold_bps,
        )
        for record in records
    )


def build_prediction_evaluation_report(
    *,
    forecast_batch: ForecastLedgerBatch | Mapping[str, Any] | Iterable[Mapping[str, Any]] | None,
    outcome_windows: Mapping[str, Mapping[str, Any]] | Iterable[Mapping[str, Any]] | None,
    prediction_snapshot: Mapping[str, Any] | None = None,
    now: datetime | None = None,
    source_ref: str | None = None,
    flat_threshold_bps: float = 1.0,
) -> PredictionEvaluationReport:
    generated_at = _generated_at(now)
    snapshot = _prediction_snapshot(prediction_snapshot)
    forecast_records = _forecast_records(forecast_batch)
    blockers: list[str] = []
    warnings: list[str] = []
    if forecast_batch is None:
        blockers.append("forecast_batch_missing")
    if not forecast_records:
        blockers.append("forecast_records_missing")
    records = build_prediction_evaluation_records(
        forecast_batch=forecast_records,
        outcome_windows=outcome_windows,
        prediction_snapshot=snapshot,
        now=now,
        source_prediction_ref=source_ref,
        flat_threshold_bps=flat_threshold_bps,
    )
    if any(record.not_evaluable_reason == "outcome_window_missing" for record in records):
        warnings.append("evaluation_records_with_missing_outcome_window")
    eval_windows_start = [record.evaluation_window_start for record in records if record.evaluation_window_start]
    eval_windows_end = [record.evaluation_window_end for record in records if record.evaluation_window_end]
    family_summary = _summary_by_key(records, "family")
    horizon_summary = _summary_by_key(records, "horizon_sec")
    return PredictionEvaluationReport(
        evaluation_report_id=f"{LOGIC_VERSION}:{generated_at}:{_prediction_run_id(snapshot)}",
        evaluation_version=LOGIC_VERSION,
        generated_at=generated_at,
        market_uid=_market_uid(snapshot),
        source_ref=source_ref,
        evaluation_window_start=min(eval_windows_start) if eval_windows_start else None,
        evaluation_window_end=max(eval_windows_end) if eval_windows_end else None,
        records=records,
        input_prediction_count=1 if snapshot else 0,
        input_forecast_record_count=len(forecast_records),
        evaluated_record_count=sum(1 for record in records if record.hit_label != "not_evaluable"),
        skipped_record_count=0,
        not_evaluable_count=sum(1 for record in records if record.hit_label == "not_evaluable"),
        family_summary={
            "directional_hit_rate_by_family": family_summary["directional_hit_rate"],
            "average_return_bps_by_family": family_summary["average_return_bps"],
            "adverse_excursion_bps_by_family": family_summary["adverse_excursion_bps"],
            "not_evaluable_count_by_family": family_summary["not_evaluable_count"],
        },
        horizon_summary={
            "directional_hit_rate_by_horizon": horizon_summary["directional_hit_rate"],
            "average_return_bps_by_horizon": horizon_summary["average_return_bps"],
            "adverse_excursion_bps_by_horizon": horizon_summary["adverse_excursion_bps"],
            "not_evaluable_count_by_horizon": horizon_summary["not_evaluable_count"],
        },
        confidence_summary=_bucket_summary(records, "confidence_bucket"),
        caution_summary=_bucket_summary(records, "caution_bucket"),
        scenario_switch_summary={
            "scenario_switch_watch_follow_through_rate": None,
            "scenario_switch_watch_wrong_direction_rate": None,
        },
        refresh_required_summary={
            "refresh_required_follow_through_rate": None,
            "refresh_required_not_evaluable_count": sum(1 for record in records if record.refresh_required is True and record.hit_label == "not_evaluable"),
        },
        data_quality_notes=tuple(dict.fromkeys(record.not_evaluable_reason for record in records if record.not_evaluable_reason)),
        calibration_candidate_notes=("evaluation_report_in_memory_only",),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
