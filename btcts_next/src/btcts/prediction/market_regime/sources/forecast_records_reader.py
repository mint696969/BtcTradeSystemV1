# path: ./btcts_next/src/btcts/prediction/market_regime/sources/forecast_records_reader.py
# desc: Read-only JSONL forecast-record reader for market-regime records.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ..source_snapshot import ForecastRecordsSnapshot
from .json_io import resolve_under_root

DEFAULT_FORECAST_RECORDS_MAX_BYTES = 6_000_000
DEFAULT_FORECAST_RECORDS_MAX_LINES = 2_000


def _horizon_sec(record: Mapping[str, Any]) -> int | None:
    value = record.get("horizon_sec")
    try:
        return int(value)
    except Exception:
        return None


def load_forecast_records_snapshot(
    hot_root: str | Path,
    relative_path: str | None,
    *,
    family: str = "market_regime",
    max_bytes: int = DEFAULT_FORECAST_RECORDS_MAX_BYTES,
    max_lines: int = DEFAULT_FORECAST_RECORDS_MAX_LINES,
) -> ForecastRecordsSnapshot:
    if not relative_path:
        return ForecastRecordsSnapshot(relative_path="", ok=False, record_count=0, market_regime_record_count=0, warnings=("forecast_records_path_missing",))
    rel = str(relative_path).replace("\\", "/")
    try:
        path = resolve_under_root(hot_root, rel)
    except Exception as exc:
        return ForecastRecordsSnapshot(relative_path=rel, ok=False, record_count=0, market_regime_record_count=0, warnings=(str(exc),))
    if not path.exists():
        return ForecastRecordsSnapshot(relative_path=rel, ok=False, record_count=0, market_regime_record_count=0, warnings=("forecast_records_missing",))

    warnings: list[str] = []
    records: list[Mapping[str, Any]] = []
    total_records = 0
    scanned = 0
    bytes_seen = 0
    truncated = False
    try:
        with path.open("rb") as handle:
            for raw_line in handle:
                scanned += 1
                bytes_seen += len(raw_line)
                if scanned > max_lines or bytes_seen > max_bytes:
                    truncated = True
                    break
                line = raw_line.decode("utf-8-sig").strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except Exception:
                    warnings.append(f"invalid_jsonl_line:{scanned}")
                    continue
                if not isinstance(record, dict):
                    warnings.append(f"jsonl_line_not_object:{scanned}")
                    continue
                total_records += 1
                if record.get("family") == family:
                    records.append(record)
    except Exception as exc:
        return ForecastRecordsSnapshot(relative_path=rel, ok=False, record_count=total_records, market_regime_record_count=len(records), scanned_lines=scanned, truncated=truncated, warnings=(str(exc),))

    horizons = tuple(sorted({sec for sec in (_horizon_sec(record) for record in records) if sec is not None}))
    return ForecastRecordsSnapshot(
        relative_path=rel,
        ok=True,
        record_count=total_records,
        market_regime_record_count=len(records),
        market_regime_horizons_sec=horizons,
        market_regime_records=tuple(records),
        scanned_lines=scanned,
        truncated=truncated,
        warnings=tuple(dict.fromkeys(warnings)),
    )
