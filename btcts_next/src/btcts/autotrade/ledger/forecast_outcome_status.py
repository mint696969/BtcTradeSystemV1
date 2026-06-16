# path: ./btcts_next/src/btcts/autotrade/ledger/forecast_outcome_status.py
# desc: Read-only status/read-model helpers for AutoTrade forecast outcome ledger.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict

from btcts.autotrade.ledger.forecast_calibration import (
    ForecastCalibrationSummary,
    ForecastOutcomeLinkRecord,
    count_divergence_reasons,
    group_forecast_by_confidence,
    group_forecast_by_driver,
    group_forecast_by_parameter_set,
    summarize_forecast_links,
)
from btcts.autotrade.ledger.forecast_resolution import default_forecast_outcome_ledger_path, read_forecast_outcome_links


@dataclass(frozen=True)
class ForecastOutcomeLedgerSummary:
    path: Path
    exists: bool
    total_rows: int
    calibration: ForecastCalibrationSummary
    by_confidence: Dict[str, ForecastCalibrationSummary] = field(default_factory=dict)
    by_driver: Dict[str, ForecastCalibrationSummary] = field(default_factory=dict)
    by_parameter_set: Dict[str, ForecastCalibrationSummary] = field(default_factory=dict)
    divergence_reason_counts: Dict[str, int] = field(default_factory=dict)
    latest_forecast_id: str | None = None
    latest_result: str | None = None
    latest_forecast_direction: str | None = None
    latest_forecast_confidence: str | None = None
    latest_actual_snapshot_id: str | None = None
    latest_divergence_reasons: tuple[str, ...] = ()
    would_send_to_broker: bool = False
    read_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["path"] = str(self.path)
        data["calibration"] = self.calibration.to_dict()
        data["by_confidence"] = {key: value.to_dict() for key, value in self.by_confidence.items()}
        data["by_driver"] = {key: value.to_dict() for key, value in self.by_driver.items()}
        data["by_parameter_set"] = {key: value.to_dict() for key, value in self.by_parameter_set.items()}
        return data


def summarize_forecast_outcome_ledger(path: Path | None = None, *, max_lines: int | None = 1000) -> ForecastOutcomeLedgerSummary:
    target = path or default_forecast_outcome_ledger_path(ensure=False)
    records = read_forecast_outcome_links(target, max_lines=max_lines)
    latest: ForecastOutcomeLinkRecord | None = records[-1] if records else None
    return ForecastOutcomeLedgerSummary(
        path=target,
        exists=target.exists(),
        total_rows=len(records),
        calibration=summarize_forecast_links(records),
        by_confidence=group_forecast_by_confidence(records),
        by_driver=group_forecast_by_driver(records),
        by_parameter_set=group_forecast_by_parameter_set(records),
        divergence_reason_counts=count_divergence_reasons(records),
        latest_forecast_id=latest.forecast_id if latest is not None else None,
        latest_result=latest.result if latest is not None else None,
        latest_forecast_direction=latest.forecast_direction if latest is not None else None,
        latest_forecast_confidence=latest.forecast_confidence if latest is not None else None,
        latest_actual_snapshot_id=latest.actual_snapshot_id if latest is not None else None,
        latest_divergence_reasons=latest.divergence_reasons if latest is not None else (),
        would_send_to_broker=False,
        read_only=True,
    )
