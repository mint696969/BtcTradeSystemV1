# path: ./btcts_next/src/btcts/prediction/calibration.py
# desc: Non-executing calibration and missed-opportunity report contracts over ForecastOutcomeBatch only. No report writes.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from .outcome_ledger import ForecastOutcomeBatch, ForecastOutcomeRecord

LOGIC_VERSION = "prediction_calibration_report.s132.v1"


@dataclass(frozen=True)
class PredictionCalibrationReport:
    report_id: str
    outcome_batch_id: str | None
    generated_at: str
    record_count: int = 0
    scored_record_count: int = 0
    average_score: float | None = None
    label_hit_rate: float | None = None
    direction_hit_rate: float | None = None
    score_by_family: Mapping[str, float | None] = field(default_factory=dict)
    score_by_horizon_sec: Mapping[int, float | None] = field(default_factory=dict)
    label_hit_rate_by_family: Mapping[str, float | None] = field(default_factory=dict)
    weak_families: Tuple[str, ...] = ()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_append_report: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "outcome_batch_id": self.outcome_batch_id,
            "generated_at": self.generated_at,
            "record_count": self.record_count,
            "scored_record_count": self.scored_record_count,
            "average_score": self.average_score,
            "label_hit_rate": self.label_hit_rate,
            "direction_hit_rate": self.direction_hit_rate,
            "score_by_family": dict(self.score_by_family),
            "score_by_horizon_sec": {str(key): value for key, value in self.score_by_horizon_sec.items()},
            "label_hit_rate_by_family": dict(self.label_hit_rate_by_family),
            "weak_families": list(self.weak_families),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_append_report": self.would_append_report,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "logic_version": LOGIC_VERSION,
        }


@dataclass(frozen=True)
class MissedOpportunityReport:
    report_id: str
    outcome_batch_id: str | None
    generated_at: str
    candidate_count: int = 0
    near_miss_count: int = 0
    wait_too_much_count: int = 0
    near_miss_records: Tuple[Mapping[str, Any], ...] = ()
    wait_too_much_records: Tuple[Mapping[str, Any], ...] = ()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_append_report: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "outcome_batch_id": self.outcome_batch_id,
            "generated_at": self.generated_at,
            "candidate_count": self.candidate_count,
            "near_miss_count": self.near_miss_count,
            "wait_too_much_count": self.wait_too_much_count,
            "near_miss_records": [dict(item) for item in self.near_miss_records],
            "wait_too_much_records": [dict(item) for item in self.wait_too_much_records],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_append_report": self.would_append_report,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "logic_version": LOGIC_VERSION,
        }


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 6) if values else None


def _rate(hits: int, total: int) -> float | None:
    return round(hits / total, 6) if total > 0 else None


def _score_by_family(records: Tuple[ForecastOutcomeRecord, ...]) -> Dict[str, float | None]:
    out: Dict[str, float | None] = {}
    for family in tuple(dict.fromkeys(record.family for record in records)):
        scores = [float(record.score) for record in records if record.family == family and record.score is not None]
        out[family] = _avg(scores)
    return out


def _score_by_horizon(records: Tuple[ForecastOutcomeRecord, ...]) -> Dict[int, float | None]:
    out: Dict[int, float | None] = {}
    for horizon in tuple(dict.fromkeys(int(record.horizon_sec) for record in records)):
        scores = [float(record.score) for record in records if int(record.horizon_sec) == horizon and record.score is not None]
        out[horizon] = _avg(scores)
    return out


def _label_hit_rate_by_family(records: Tuple[ForecastOutcomeRecord, ...]) -> Dict[str, float | None]:
    out: Dict[str, float | None] = {}
    for family in tuple(dict.fromkeys(record.family for record in records)):
        family_records = [record for record in records if record.family == family and record.label_hit is not None]
        out[family] = _rate(sum(1 for record in family_records if record.label_hit is True), len(family_records))
    return out


def build_prediction_calibration_report(
    outcome_batch: ForecastOutcomeBatch | None,
    *,
    now: datetime | None = None,
    weak_score_threshold: float = 0.60,
) -> PredictionCalibrationReport:
    generated_at = _generated_at(now)
    blockers: list[str] = []
    warnings: list[str] = []
    if outcome_batch is None:
        blockers.append("outcome_batch_missing")
        return PredictionCalibrationReport(
            report_id=f"{LOGIC_VERSION}:{generated_at}:missing_outcome_batch",
            outcome_batch_id=None,
            generated_at=generated_at,
            blockers=tuple(blockers),
        )
    records = tuple(outcome_batch.records)
    if not records:
        blockers.append("outcome_records_missing")
    scores = [float(record.score) for record in records if record.score is not None]
    scored_records = [record for record in records if record.score is not None]
    label_records = [record for record in records if record.label_hit is not None]
    direction_records = [record for record in records if record.direction_hit is not None]
    score_by_family = _score_by_family(records)
    weak_families = tuple(family for family, score in score_by_family.items() if score is not None and score < weak_score_threshold)
    warnings.extend(outcome_batch.warnings)
    if weak_families:
        warnings.append("weak_prediction_families_present")
    return PredictionCalibrationReport(
        report_id=f"{LOGIC_VERSION}:{generated_at}:{outcome_batch.batch_id}",
        outcome_batch_id=outcome_batch.batch_id,
        generated_at=generated_at,
        record_count=len(records),
        scored_record_count=len(scored_records),
        average_score=_avg(scores),
        label_hit_rate=_rate(sum(1 for record in label_records if record.label_hit is True), len(label_records)),
        direction_hit_rate=_rate(sum(1 for record in direction_records if record.direction_hit is True), len(direction_records)),
        score_by_family=score_by_family,
        score_by_horizon_sec=_score_by_horizon(records),
        label_hit_rate_by_family=_label_hit_rate_by_family(records),
        weak_families=weak_families,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def _near_miss_snapshot(record: ForecastOutcomeRecord) -> Dict[str, Any]:
    return {
        "forecast_record_id": record.forecast_record_id,
        "family": record.family,
        "horizon_sec": record.horizon_sec,
        "predicted_label": record.predicted_label,
        "predicted_score": record.predicted_score,
        "realized_label": record.realized_label,
        "realized_return": record.realized_return,
        "score": record.score,
        "reason": "high_confidence_or_positive_outcome_not_fully_hit",
    }


def _wait_snapshot(record: ForecastOutcomeRecord) -> Dict[str, Any]:
    return {
        "forecast_record_id": record.forecast_record_id,
        "family": record.family,
        "horizon_sec": record.horizon_sec,
        "predicted_label": record.predicted_label,
        "predicted_score": record.predicted_score,
        "blockers": list(record.blockers),
        "reason": "blocked_or_missing_outcome_candidate",
    }


def build_missed_opportunity_report(
    outcome_batch: ForecastOutcomeBatch | None,
    *,
    now: datetime | None = None,
    near_miss_predicted_score_min: float = 0.45,
    near_miss_score_max: float = 0.50,
) -> MissedOpportunityReport:
    generated_at = _generated_at(now)
    blockers: list[str] = []
    warnings: list[str] = []
    if outcome_batch is None:
        blockers.append("outcome_batch_missing")
        return MissedOpportunityReport(
            report_id=f"{LOGIC_VERSION}:missed:{generated_at}:missing_outcome_batch",
            outcome_batch_id=None,
            generated_at=generated_at,
            blockers=tuple(blockers),
        )
    records = tuple(outcome_batch.records)
    if not records:
        blockers.append("outcome_records_missing")
    near_miss: list[Mapping[str, Any]] = []
    wait_too_much: list[Mapping[str, Any]] = []
    for record in records:
        predicted_score = float(record.predicted_score) if record.predicted_score is not None else None
        score = float(record.score) if record.score is not None else None
        positive_realized = record.realized_return is not None and float(record.realized_return) > 0
        if predicted_score is not None and predicted_score >= near_miss_predicted_score_min and score is not None and score <= near_miss_score_max and positive_realized:
            near_miss.append(_near_miss_snapshot(record))
        if "realized_outcome_missing" in record.blockers or (record.blockers and record.score is None):
            wait_too_much.append(_wait_snapshot(record))
    if near_miss:
        warnings.append("near_miss_candidates_present")
    if wait_too_much:
        warnings.append("wait_too_much_candidates_present")
    warnings.extend(outcome_batch.warnings)
    return MissedOpportunityReport(
        report_id=f"{LOGIC_VERSION}:missed:{generated_at}:{outcome_batch.batch_id}",
        outcome_batch_id=outcome_batch.batch_id,
        generated_at=generated_at,
        candidate_count=len(records),
        near_miss_count=len(near_miss),
        wait_too_much_count=len(wait_too_much),
        near_miss_records=tuple(near_miss),
        wait_too_much_records=tuple(wait_too_much),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
