# path: ./btcts_next/src/btcts/autotrade/ledger/forecast_resolution.py
# desc: Resolve due shadow forecasts against target-time market_state actual rows and append outcome links.

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from btcts.autotrade.config import initial_parameter_set_v0_1
from btcts.autotrade.config.models import ParameterSet
from btcts.autotrade.ledger.decision_status import read_shadow_decision_rows
from btcts.autotrade.ledger.forecast_calibration import ForecastOutcomeLinkRecord, summarize_forecast_links
from btcts.autotrade.read_model.live_input_adapter import latest_market_state_part_file
from btcts.autotrade.read_model.models import GroundDirection
from btcts.autotrade.runtime_paths import decision_ledger_path

DEFAULT_MAX_ACTUAL_MATCH_AGE_SEC = 45.0


@dataclass(frozen=True)
class ActualMatch:
    snapshot_id: str | None
    event_ts: str | None
    ground_direction: str | None
    age_delta_sec: float | None
    blocked_by: Tuple[str, ...]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ForecastOutcomeResolutionResult:
    shadow_decision_path: Path
    outcome_ledger_path: Path
    actual_snapshot_id: str | None
    actual_ground_direction: str | None
    due_count: int
    appended_count: int
    duplicate_skipped_count: int
    unresolved_count: int
    blocked_by: Tuple[str, ...]
    records: Tuple[ForecastOutcomeLinkRecord, ...]
    actual_match_max_age_sec: float = DEFAULT_MAX_ACTUAL_MATCH_AGE_SEC
    actual_match_count: int = 0
    actual_match_miss_count: int = 0
    would_send_to_broker: bool = False
    read_only_inputs: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["shadow_decision_path"] = str(self.shadow_decision_path)
        data["outcome_ledger_path"] = str(self.outcome_ledger_path)
        data["records"] = [record.to_dict() for record in self.records]
        data["summary"] = summarize_forecast_links(self.records).to_dict()
        return data


def default_forecast_outcome_ledger_path(*, ensure: bool = True) -> Path:
    return decision_ledger_path("forecast_outcomes.jsonl", ensure=ensure)


def _parse_ts(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _event_ts(row: Dict[str, Any]) -> datetime | None:
    return _parse_ts(row.get("collector_ts") or row.get("exchange_ts") or row.get("event_ts"))


def _event_ts_str(row: Dict[str, Any]) -> str | None:
    dt = _event_ts(row)
    if dt is None:
        return None
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _actual_snapshot_id(row: Dict[str, Any]) -> str | None:
    explicit = row.get("snapshot_id") or row.get("source_snapshot_id")
    if explicit:
        return str(explicit)
    ts = _event_ts_str(row)
    market_uid = str(row.get("market_uid") or f"{row.get('exchange') or 'bitflyer'}:{row.get('symbol_raw') or 'BTC_JPY'}")
    if not ts:
        return None
    safe = "".join(ch if ch.isalnum() else "" for ch in f"{market_uid}_{ts}")[-32:]
    return f"actual_{safe}"


def _ground_direction_from_row(row: Dict[str, Any]) -> str:
    text = " ".join(str(row.get(key) or "").lower() for key in ("interpretation_reason", "market_bias", "pressure_bias"))
    if "sell" in text or "ask" in text or "resistance" in text:
        return GroundDirection.SELL_LEANING.value
    if "buy" in text or "bid" in text or "support" in text:
        return GroundDirection.BUY_LEANING.value
    if str(row.get("interpretation_bucket") or "") == "allow_structural_use":
        return GroundDirection.MIXED.value
    return GroundDirection.UNKNOWN.value


def _read_market_state_rows(*, exchange: str, symbol_raw: str, state_type: str) -> tuple[Path | None, tuple[Dict[str, Any], ...]]:
    path = latest_market_state_part_file(exchange=exchange, symbol_raw=symbol_raw, state_type=state_type)
    if path is None or not path.exists() or not path.is_file():
        return path, ()
    rows: list[Dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return path, ()
    for line in lines:
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    rows.sort(key=lambda row: _event_ts(row) or datetime.min.replace(tzinfo=timezone.utc))
    return path, tuple(rows)


def find_actual_match_for_target(
    rows: Iterable[Dict[str, Any]],
    *,
    target_ts: str,
    max_actual_match_age_sec: float = DEFAULT_MAX_ACTUAL_MATCH_AGE_SEC,
) -> ActualMatch:
    target = _parse_ts(target_ts)
    if target is None:
        return ActualMatch(None, None, None, None, ("forecast_target_ts_missing",))
    best_row: Dict[str, Any] | None = None
    best_delta: float | None = None
    for row in rows:
        ts = _event_ts(row)
        if ts is None:
            continue
        delta = abs((ts - target).total_seconds())
        if best_delta is None or delta < best_delta:
            best_delta = delta
            best_row = row
    if best_row is None or best_delta is None:
        return ActualMatch(None, None, None, None, ("actual_market_state_rows_missing",))
    if best_delta > max_actual_match_age_sec:
        return ActualMatch(
            _actual_snapshot_id(best_row),
            _event_ts_str(best_row),
            None,
            best_delta,
            ("actual_snapshot_too_far",),
        )
    return ActualMatch(
        _actual_snapshot_id(best_row),
        _event_ts_str(best_row),
        _ground_direction_from_row(best_row),
        best_delta,
        (),
    )


def _read_existing_forecast_ids(path: Path) -> set[str]:
    if not path.exists() or not path.is_file():
        return set()
    out: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return out
    for line in lines:
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("forecast_id"):
            out.add(str(obj.get("forecast_id")))
    return out


def append_forecast_outcome_link(path: Path, record: ForecastOutcomeLinkRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")


def read_forecast_outcome_links(path: Path | None = None, *, max_lines: int | None = 1000) -> tuple[ForecastOutcomeLinkRecord, ...]:
    target = path or default_forecast_outcome_ledger_path(ensure=False)
    if not target.exists() or not target.is_file():
        return ()
    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except Exception:
        return ()
    if max_lines is not None and max_lines >= 0:
        lines = lines[-max_lines:]
    rows: list[ForecastOutcomeLinkRecord] = []
    fields = ForecastOutcomeLinkRecord.__dataclass_fields__
    for line in lines:
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        try:
            data = {key: obj.get(key) for key in fields}
            data["drivers"] = tuple(data.get("drivers") or ())
            data["blocked_by"] = tuple(data.get("blocked_by") or ())
            data["divergence_reasons"] = tuple(data.get("divergence_reasons") or ())
            rows.append(ForecastOutcomeLinkRecord(**data))
        except Exception:
            continue
    return tuple(rows)


def _expected_actual_direction(forecast_direction: str) -> str | None:
    mapping = {
        "up": GroundDirection.BUY_LEANING.value,
        "down": GroundDirection.SELL_LEANING.value,
        "range": GroundDirection.MIXED.value,
    }
    return mapping.get(str(forecast_direction or ""))


def _score_forecast_row(*, row: Dict[str, Any], actual_match: ActualMatch) -> tuple[str, bool, bool, tuple[str, ...]]:
    forecast = row.get("forecast_5m") or {}
    forecast_direction = str(forecast.get("forecast_direction") or "unknown")
    if actual_match.blocked_by:
        return "unscorable", False, False, actual_match.blocked_by
    if actual_match.snapshot_id is None or actual_match.ground_direction is None:
        return "unscorable", False, False, ("actual_snapshot_missing",)
    expected = _expected_actual_direction(forecast_direction)
    if expected is None:
        if forecast_direction == "unknown":
            return "unscorable", False, False, ("forecast_direction_unknown",)
        return "partial", False, False, ("forecast_direction_not_directly_scorable",)
    hit = actual_match.ground_direction == expected
    return ("hit" if hit else "miss"), hit, hit, () if hit else ("direction_mismatch",)


def _record_from_shadow_row(*, row: Dict[str, Any], actual_match: ActualMatch) -> ForecastOutcomeLinkRecord:
    forecast = row.get("forecast_5m") or {}
    result, direction_hit, change_type_hit, divergence = _score_forecast_row(
        row=row,
        actual_match=actual_match,
    )
    blocked = list(forecast.get("blocked_by") or row.get("blocked_by") or ())
    if actual_match.blocked_by:
        blocked.extend(actual_match.blocked_by)
    return ForecastOutcomeLinkRecord(
        forecast_id=str(forecast.get("forecast_id") or row.get("forecast_id") or ""),
        parameter_set_id=str(forecast.get("parameter_set_id") or row.get("parameter_set_id") or ""),
        logic_version=str(forecast.get("logic_version") or row.get("logic_version") or ""),
        source_snapshot_id=str(forecast.get("source_snapshot_id") or row.get("snapshot_id") or ""),
        target_ts=str(forecast.get("target_ts") or ""),
        actual_snapshot_id=actual_match.snapshot_id,
        forecast_direction=str(forecast.get("forecast_direction") or "unknown"),
        forecast_confidence=str(forecast.get("confidence") or "unknown"),
        expected_change=str(forecast.get("expected_change") or "unknown"),
        drivers=tuple(str(item) for item in (forecast.get("drivers") or ())),
        blocked_by=tuple(dict.fromkeys(str(item) for item in blocked)),
        result=result,
        direction_hit=direction_hit,
        change_type_hit=change_type_hit,
        divergence_reasons=divergence,
    )


def _due_shadow_rows(rows: Iterable[Dict[str, Any]], *, actual_event_ts: datetime | None, now: datetime | None = None) -> list[Dict[str, Any]]:
    anchor = actual_event_ts or now or datetime.now(timezone.utc)
    due: list[Dict[str, Any]] = []
    for row in rows:
        forecast = row.get("forecast_5m") or {}
        target = _parse_ts(forecast.get("target_ts"))
        forecast_id = forecast.get("forecast_id") or row.get("forecast_id")
        if target is None or not forecast_id:
            continue
        if target <= anchor:
            due.append(row)
    return due


def resolve_due_shadow_forecast_outcomes(
    *,
    parameter_set: ParameterSet | None = None,
    shadow_decision_path: Path | None = None,
    outcome_ledger_path: Path | None = None,
    exchange: str = "bitflyer",
    symbol_raw: str = "BTC_JPY",
    state_type: str = "market.overview",
    persist: bool = True,
    max_decision_lines: int | None = 1000,
    max_actual_match_age_sec: float = DEFAULT_MAX_ACTUAL_MATCH_AGE_SEC,
) -> ForecastOutcomeResolutionResult:
    _ps = parameter_set or initial_parameter_set_v0_1()
    outcome_path = outcome_ledger_path or default_forecast_outcome_ledger_path(ensure=persist)
    read = read_shadow_decision_rows(shadow_decision_path, max_lines=max_decision_lines)
    _actual_part, actual_rows = _read_market_state_rows(exchange=exchange, symbol_raw=symbol_raw, state_type=state_type)
    blocked: list[str] = []
    if not actual_rows:
        blocked.append("actual_market_state_rows_missing")
    actual_event_ts = _event_ts(actual_rows[-1]) if actual_rows else None
    due = _due_shadow_rows(read.rows, actual_event_ts=actual_event_ts)
    existing = _read_existing_forecast_ids(outcome_path)

    records: list[ForecastOutcomeLinkRecord] = []
    appended = 0
    duplicate = 0
    unresolved = 0
    actual_match_count = 0
    actual_match_miss_count = 0
    latest_actual_snapshot_id: str | None = None
    latest_actual_ground_direction: str | None = None

    for row in due:
        forecast = row.get("forecast_5m") or {}
        match = find_actual_match_for_target(
            actual_rows,
            target_ts=str(forecast.get("target_ts") or ""),
            max_actual_match_age_sec=max_actual_match_age_sec,
        )
        if not match.blocked_by:
            actual_match_count += 1
            latest_actual_snapshot_id = match.snapshot_id
            latest_actual_ground_direction = match.ground_direction
        else:
            actual_match_miss_count += 1
        record = _record_from_shadow_row(row=row, actual_match=match)
        if not record.forecast_id:
            unresolved += 1
            continue
        if record.forecast_id in existing:
            duplicate += 1
            continue
        records.append(record)
        if record.result == "unscorable":
            unresolved += 1
        if persist:
            append_forecast_outcome_link(outcome_path, record)
            existing.add(record.forecast_id)
            appended += 1

    return ForecastOutcomeResolutionResult(
        shadow_decision_path=read.path,
        outcome_ledger_path=outcome_path,
        actual_snapshot_id=latest_actual_snapshot_id,
        actual_ground_direction=latest_actual_ground_direction,
        due_count=len(due),
        appended_count=appended,
        duplicate_skipped_count=duplicate,
        unresolved_count=unresolved,
        blocked_by=tuple(dict.fromkeys(blocked)),
        records=tuple(records),
        actual_match_max_age_sec=float(max_actual_match_age_sec),
        actual_match_count=actual_match_count,
        actual_match_miss_count=actual_match_miss_count,
        would_send_to_broker=False,
        read_only_inputs=True,
    )
