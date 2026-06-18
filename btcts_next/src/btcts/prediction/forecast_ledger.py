# path: ./btcts_next/src/btcts/prediction/forecast_ledger.py
# desc: Non-executing forecast ledger record contracts. Builds in-memory records from InferenceBundle only; no append/write behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple

from .contracts import InferenceBundle, PredictionOutput

LOGIC_VERSION = "prediction_forecast_ledger.s130.v1"


@dataclass(frozen=True)
class ForecastLedgerRecord:
    record_id: str
    bundle_id: str
    generated_at: str
    prediction_id: str
    family: str
    horizon_sec: int
    horizon_label: str
    horizon_key: str
    primary_label: str
    confidence: str
    score: float | None = None
    parameter_set_id: str | None = None
    drivers: Tuple[str, ...] = ()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    values_snapshot: Mapping[str, Any] = field(default_factory=dict)
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
        data["drivers"] = list(self.drivers)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["values_snapshot"] = dict(self.values_snapshot)
        data["usable"] = self.usable
        data["logic_version"] = LOGIC_VERSION
        return data


@dataclass(frozen=True)
class ForecastLedgerBatch:
    batch_id: str
    bundle_id: str | None
    generated_at: str
    records: Tuple[ForecastLedgerRecord, ...] = ()
    family_count: int = 0
    horizon_count: int = 0
    record_count: int = 0
    blocked_record_count: int = 0
    warning_count: int = 0
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
            "bundle_id": self.bundle_id,
            "generated_at": self.generated_at,
            "records": [record.to_dict() for record in self.records],
            "family_count": self.family_count,
            "horizon_count": self.horizon_count,
            "record_count": self.record_count,
            "blocked_record_count": self.blocked_record_count,
            "warning_count": self.warning_count,
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


def _record_id(bundle_id: str, output: PredictionOutput) -> str:
    return f"{LOGIC_VERSION}:{bundle_id}:{output.family.value}:{int(output.horizon.horizon_sec)}s:{output.prediction_id}"


def _values_snapshot(values: Mapping[str, Any], max_keys: int) -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {}
    for key in sorted(values.keys())[:max_keys]:
        value = values[key]
        if isinstance(value, (str, int, float, bool)) or value is None:
            snapshot[key] = value
        else:
            snapshot[key] = str(type(value).__name__)
    return snapshot


def _record_from_output(bundle_id: str, output: PredictionOutput, max_value_keys: int) -> ForecastLedgerRecord:
    horizon = output.horizon
    return ForecastLedgerRecord(
        record_id=_record_id(bundle_id, output),
        bundle_id=bundle_id,
        generated_at=output.generated_at,
        prediction_id=output.prediction_id,
        family=output.family.value,
        horizon_sec=int(horizon.horizon_sec),
        horizon_label=horizon.label,
        horizon_key=horizon.horizon_key,
        primary_label=output.primary_label,
        confidence=output.confidence.value,
        score=output.score,
        parameter_set_id=output.parameter_set.parameter_set_id,
        drivers=tuple(output.drivers),
        blockers=tuple(output.blockers),
        warnings=tuple(output.warnings),
        values_snapshot=_values_snapshot(output.values, max_value_keys),
    )


def build_forecast_ledger_records_from_bundle(
    bundle: InferenceBundle | None,
    *,
    now: datetime | None = None,
    max_value_keys: int = 12,
) -> ForecastLedgerBatch:
    generated_at = _generated_at(now)
    blockers: list[str] = []
    warnings: list[str] = []
    if bundle is None:
        blockers.append("inference_bundle_missing")
        return ForecastLedgerBatch(
            batch_id=f"{LOGIC_VERSION}:{generated_at}:missing_bundle",
            bundle_id=None,
            generated_at=generated_at,
            blockers=tuple(blockers),
        )
    records = tuple(_record_from_output(bundle.bundle_id, output, max_value_keys) for output in bundle.outputs)
    if not records:
        blockers.append("forecast_outputs_missing")
    warnings.extend(bundle.warnings)
    families = tuple(dict.fromkeys(record.family for record in records))
    horizons = tuple(dict.fromkeys(record.horizon_sec for record in records))
    blocked_count = sum(1 for record in records if record.blockers)
    warning_count = sum(len(record.warnings) for record in records) + len(bundle.warnings)
    return ForecastLedgerBatch(
        batch_id=f"{LOGIC_VERSION}:{generated_at}:{bundle.bundle_id}",
        bundle_id=bundle.bundle_id,
        generated_at=generated_at,
        records=records,
        family_count=len(families),
        horizon_count=len(horizons),
        record_count=len(records),
        blocked_record_count=blocked_count,
        warning_count=warning_count,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
