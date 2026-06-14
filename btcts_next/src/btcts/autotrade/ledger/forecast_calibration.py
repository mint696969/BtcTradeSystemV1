# path: ./btcts_next/src/btcts/autotrade/ledger/forecast_calibration.py
# desc: Forecast outcome linking and calibration summaries for AutoTrade.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, Tuple

from btcts.autotrade.read_model.models import Forecast5m, ForecastOutcome, ForecastOutcomeResult


@dataclass(frozen=True)
class ForecastOutcomeLinkRecord:
    forecast_id: str
    parameter_set_id: str
    logic_version: str
    source_snapshot_id: str
    target_ts: str
    actual_snapshot_id: str | None
    forecast_direction: str
    forecast_confidence: str
    expected_change: str
    drivers: Tuple[str, ...]
    blocked_by: Tuple[str, ...]
    result: str
    direction_hit: bool
    change_type_hit: bool
    divergence_reasons: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ForecastCalibrationSummary:
    group_key: str
    total_forecast_count: int
    scorable_forecast_count: int
    hit_count: int
    partial_count: int
    miss_count: int
    unscorable_count: int
    hit_rate: float | None
    partial_rate: float | None
    miss_rate: float | None
    unscorable_rate: float | None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def link_forecast_outcome(forecast: Forecast5m, outcome: ForecastOutcome) -> ForecastOutcomeLinkRecord:
    return ForecastOutcomeLinkRecord(
        forecast_id=forecast.forecast_id,
        parameter_set_id=forecast.parameter_set_id,
        logic_version=forecast.logic_version,
        source_snapshot_id=forecast.source_snapshot_id,
        target_ts=forecast.target_ts,
        actual_snapshot_id=outcome.actual_snapshot_id,
        forecast_direction=forecast.forecast_direction.value,
        forecast_confidence=forecast.confidence.value,
        expected_change=forecast.expected_change.value,
        drivers=forecast.drivers,
        blocked_by=forecast.blocked_by,
        result=outcome.score.result.value,
        direction_hit=outcome.score.direction_hit,
        change_type_hit=outcome.score.change_type_hit,
        divergence_reasons=outcome.divergence_reasons,
    )


def summarize_forecast_links(records: Iterable[ForecastOutcomeLinkRecord], *, group_key: str = "all") -> ForecastCalibrationSummary:
    rows = list(records)
    total = len(rows)
    hit = sum(1 for r in rows if r.result == ForecastOutcomeResult.HIT.value)
    partial = sum(1 for r in rows if r.result == ForecastOutcomeResult.PARTIAL.value)
    miss = sum(1 for r in rows if r.result == ForecastOutcomeResult.MISS.value)
    unscorable = sum(1 for r in rows if r.result == ForecastOutcomeResult.UNSCORABLE.value)
    scorable = hit + partial + miss
    return ForecastCalibrationSummary(
        group_key=group_key,
        total_forecast_count=total,
        scorable_forecast_count=scorable,
        hit_count=hit,
        partial_count=partial,
        miss_count=miss,
        unscorable_count=unscorable,
        hit_rate=(hit / scorable) if scorable else None,
        partial_rate=(partial / scorable) if scorable else None,
        miss_rate=(miss / scorable) if scorable else None,
        unscorable_rate=(unscorable / total) if total else None,
    )


def group_forecast_by_parameter_set(records: Iterable[ForecastOutcomeLinkRecord]) -> Dict[str, ForecastCalibrationSummary]:
    groups: dict[str, list[ForecastOutcomeLinkRecord]] = {}
    for record in records:
        groups.setdefault(record.parameter_set_id, []).append(record)
    return {key: summarize_forecast_links(value, group_key=f"parameter_set:{key}") for key, value in groups.items()}


def group_forecast_by_confidence(records: Iterable[ForecastOutcomeLinkRecord]) -> Dict[str, ForecastCalibrationSummary]:
    groups: dict[str, list[ForecastOutcomeLinkRecord]] = {}
    for record in records:
        key = record.forecast_confidence
        groups.setdefault(key, []).append(record)
    return {key: summarize_forecast_links(value, group_key=f"confidence:{key}") for key, value in groups.items()}


def group_forecast_by_driver(records: Iterable[ForecastOutcomeLinkRecord]) -> Dict[str, ForecastCalibrationSummary]:
    groups: dict[str, list[ForecastOutcomeLinkRecord]] = {}
    for record in records:
        drivers = record.drivers or ("no_driver",)
        for driver in drivers:
            groups.setdefault(driver, []).append(record)
    return {key: summarize_forecast_links(value, group_key=f"driver:{key}") for key, value in groups.items()}


def count_divergence_reasons(records: Iterable[ForecastOutcomeLinkRecord]) -> Dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        for reason in record.divergence_reasons:
            counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
