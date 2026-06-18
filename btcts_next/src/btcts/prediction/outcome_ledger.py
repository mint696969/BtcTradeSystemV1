# path: ./btcts_next/src/btcts/prediction/outcome_ledger.py
# desc: Non-executing forecast outcome and scoring contracts. Builds in-memory outcome records only; no append/write behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from .forecast_ledger import ForecastLedgerBatch, ForecastLedgerRecord

LOGIC_VERSION = "prediction_outcome_ledger.s131.v1"


@dataclass(frozen=True)
class RealizedOutcome:
    outcome_id: str
    family: str
    horizon_sec: int
    realized_label: str
    realized_direction: str = "unknown"
    realized_return: float | None = None
    realized_score: float | None = None
    observed_at: str | None = None
    notes: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["notes"] = list(self.notes)
        return data


@dataclass(frozen=True)
class ForecastOutcomeRecord:
    outcome_record_id: str
    forecast_record_id: str
    prediction_id: str
    family: str
    horizon_sec: int
    predicted_label: str
    predicted_score: float | None
    realized_label: str | None = None
    realized_direction: str = "unknown"
    realized_return: float | None = None
    label_hit: bool | None = None
    direction_hit: bool | None = None
    score: float | None = None
    scoring_state: str = "unknown"
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_append_ledger: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False

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
class ForecastOutcomeBatch:
    batch_id: str
    forecast_batch_id: str | None
    generated_at: str
    records: Tuple[ForecastOutcomeRecord, ...] = ()
    record_count: int = 0
    scored_record_count: int = 0
    label_hit_count: int = 0
    direction_hit_count: int = 0
    average_score: float | None = None
    score_by_family: Mapping[str, float | None] = field(default_factory=dict)
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_append_ledger: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "forecast_batch_id": self.forecast_batch_id,
            "generated_at": self.generated_at,
            "records": [record.to_dict() for record in self.records],
            "record_count": self.record_count,
            "scored_record_count": self.scored_record_count,
            "label_hit_count": self.label_hit_count,
            "direction_hit_count": self.direction_hit_count,
            "average_score": self.average_score,
            "score_by_family": dict(self.score_by_family),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_append_ledger": self.would_append_ledger,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
            "logic_version": LOGIC_VERSION,
        }


def _generated_at(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _outcome_key(family: str, horizon_sec: int) -> str:
    return f"{family}:{int(horizon_sec)}"


def _prediction_direction(label: str) -> str:
    if label in ("long_bias", "trend_candidate", "confirmed", "directional_structure"):
        return "up"
    if label in ("short_bias",):
        return "down"
    if label in ("elevated_risk", "divergent_warning", "volatile_or_divergent", "compression_watch", "rejection_structure"):
        return "risk"
    if label in ("range_candidate", "range_boundary_structure", "neutral_bias", "normal_risk", "neutral_structure"):
        return "neutral"
    return "unknown"


def _normalize_realized(realized_outcomes: Mapping[str, RealizedOutcome] | Tuple[RealizedOutcome, ...] | None) -> dict[str, RealizedOutcome]:
    if realized_outcomes is None:
        return {}
    if isinstance(realized_outcomes, Mapping):
        return dict(realized_outcomes)
    return {_outcome_key(item.family, item.horizon_sec): item for item in realized_outcomes}


def _score_record(record: ForecastLedgerRecord, realized: RealizedOutcome | None) -> ForecastOutcomeRecord:
    blockers: list[str] = []
    warnings: list[str] = []
    if realized is None:
        blockers.append("realized_outcome_missing")
        return ForecastOutcomeRecord(
            outcome_record_id=f"{LOGIC_VERSION}:{record.record_id}:missing",
            forecast_record_id=record.record_id,
            prediction_id=record.prediction_id,
            family=record.family,
            horizon_sec=record.horizon_sec,
            predicted_label=record.primary_label,
            predicted_score=record.score,
            blockers=tuple(blockers),
        )
    label_hit = record.primary_label == realized.realized_label
    predicted_direction = _prediction_direction(record.primary_label)
    direction_hit = predicted_direction != "unknown" and realized.realized_direction != "unknown" and predicted_direction == realized.realized_direction
    if predicted_direction == "unknown":
        warnings.append("predicted_direction_unknown")
    score = 1.0 if label_hit else 0.0
    if not label_hit and direction_hit:
        score = 0.5
    if record.blockers:
        blockers.extend(record.blockers)
    return ForecastOutcomeRecord(
        outcome_record_id=f"{LOGIC_VERSION}:{record.record_id}:{realized.outcome_id}",
        forecast_record_id=record.record_id,
        prediction_id=record.prediction_id,
        family=record.family,
        horizon_sec=record.horizon_sec,
        predicted_label=record.primary_label,
        predicted_score=record.score,
        realized_label=realized.realized_label,
        realized_direction=realized.realized_direction,
        realized_return=realized.realized_return,
        label_hit=label_hit,
        direction_hit=direction_hit,
        score=score,
        scoring_state="scored" if not blockers else "blocked_forecast_scored",
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def _avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 6) if values else None


def _score_by_family(records: Tuple[ForecastOutcomeRecord, ...]) -> Dict[str, float | None]:
    families = tuple(dict.fromkeys(record.family for record in records))
    out: Dict[str, float | None] = {}
    for family in families:
        scores = [float(record.score) for record in records if record.family == family and record.score is not None]
        out[family] = _avg(scores)
    return out


def build_forecast_outcome_records(
    forecast_batch: ForecastLedgerBatch | None,
    realized_outcomes: Mapping[str, RealizedOutcome] | Tuple[RealizedOutcome, ...] | None,
    *,
    now: datetime | None = None,
) -> ForecastOutcomeBatch:
    generated_at = _generated_at(now)
    blockers: list[str] = []
    warnings: list[str] = []
    if forecast_batch is None:
        blockers.append("forecast_batch_missing")
        return ForecastOutcomeBatch(
            batch_id=f"{LOGIC_VERSION}:{generated_at}:missing_forecast_batch",
            forecast_batch_id=None,
            generated_at=generated_at,
            blockers=tuple(blockers),
        )
    realized_by_key = _normalize_realized(realized_outcomes)
    records = tuple(
        _score_record(record, realized_by_key.get(_outcome_key(record.family, record.horizon_sec)) or realized_by_key.get(record.prediction_id))
        for record in forecast_batch.records
    )
    if not records:
        blockers.append("forecast_records_missing")
    if not realized_by_key:
        blockers.append("realized_outcomes_missing")
    warnings.extend(forecast_batch.warnings)
    scores = [float(record.score) for record in records if record.score is not None]
    return ForecastOutcomeBatch(
        batch_id=f"{LOGIC_VERSION}:{generated_at}:{forecast_batch.batch_id}",
        forecast_batch_id=forecast_batch.batch_id,
        generated_at=generated_at,
        records=records,
        record_count=len(records),
        scored_record_count=len(scores),
        label_hit_count=sum(1 for record in records if record.label_hit is True),
        direction_hit_count=sum(1 for record in records if record.direction_hit is True),
        average_score=_avg(scores),
        score_by_family=_score_by_family(records),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
