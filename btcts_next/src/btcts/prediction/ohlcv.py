# path: ./btcts_next/src/btcts/prediction/ohlcv.py
# desc: Non-executing OHLCV/candle contracts and deterministic aggregation from already-provided rows.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping, Tuple

TIMEFRAME_SECONDS: Tuple[int, ...] = (60, 300, 900, 1800, 3600, 14400, 86400)
LOGIC_VERSION = "prediction_ohlcv.s124.v1"


@dataclass(frozen=True)
class Timeframe:
    timeframe_sec: int
    label: str
    role: str

    @property
    def timeframe_key(self) -> str:
        return f"{int(self.timeframe_sec)}s"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timeframe_key"] = self.timeframe_key
        return data


@dataclass(frozen=True)
class OHLCVCandle:
    timeframe: Timeframe
    start_ts: str
    end_ts: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    trade_count: int = 0
    vwap: float | None = None
    source_family: str = "provided_rows"
    source_symbol: str | None = None
    source_venue: str | None = None
    row_count: int = 0
    gap: bool = False
    stale: bool = False
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timeframe"] = self.timeframe.to_dict()
        data["warnings"] = list(self.warnings)
        return data


@dataclass(frozen=True)
class OHLCVAggregationDiagnostics:
    logic_version: str = LOGIC_VERSION
    requested_timeframes_sec: Tuple[int, ...] = TIMEFRAME_SECONDS
    input_row_count: int = 0
    usable_row_count: int = 0
    candle_count: int = 0
    blocked_by: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    @property
    def usable(self) -> bool:
        return not self.blocked_by

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["requested_timeframes_sec"] = list(self.requested_timeframes_sec)
        data["blocked_by"] = list(self.blocked_by)
        data["warnings"] = list(self.warnings)
        data["usable"] = self.usable
        return data


def _label(seconds: int) -> str:
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds == 86400:
        return "1d"
    if seconds % 3600 == 0:
        return f"{seconds // 3600}h"
    return f"{seconds}s"


def _role(seconds: int) -> str:
    if seconds in (60, 300):
        return "short_technical_structure"
    if seconds in (900, 1800):
        return "primary_trade_structure"
    return "higher_timeframe_context"


def build_default_timeframes() -> Tuple[Timeframe, ...]:
    return tuple(Timeframe(seconds, _label(seconds), _role(seconds)) for seconds in TIMEFRAME_SECONDS)


def timeframe_by_seconds(seconds: int) -> Timeframe:
    for timeframe in build_default_timeframes():
        if timeframe.timeframe_sec == int(seconds):
            return timeframe
    raise KeyError(f"unsupported ohlcv timeframe: {seconds}")


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


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _bucket_start(dt: datetime, timeframe_sec: int) -> datetime:
    seconds = int(dt.timestamp())
    bucket = seconds - (seconds % int(timeframe_sec))
    return datetime.fromtimestamp(bucket, tz=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _row_ts(row: Mapping[str, Any]) -> datetime | None:
    return _parse_ts(row.get("event_ts") or row.get("exchange_ts") or row.get("collector_ts") or row.get("ts"))


def _row_price(row: Mapping[str, Any]) -> float | None:
    return _float_or_none(row.get("price") or row.get("close") or row.get("mid_price") or row.get("mid") or row.get("last_price"))


def _row_size(row: Mapping[str, Any]) -> float:
    return float(_float_or_none(row.get("size") or row.get("volume") or row.get("amount")) or 0.0)


def _normalize_rows(rows: Iterable[Mapping[str, Any]]) -> list[tuple[datetime, float, float, Mapping[str, Any]]]:
    out: list[tuple[datetime, float, float, Mapping[str, Any]]] = []
    for row in rows:
        ts = _row_ts(row)
        price = _row_price(row)
        if ts is None or price is None:
            continue
        out.append((ts, price, _row_size(row), row))
    out.sort(key=lambda item: item[0])
    return out


def aggregate_ohlcv_from_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    timeframes_sec: Tuple[int, ...] = TIMEFRAME_SECONDS,
    now: datetime | None = None,
    max_latest_age_sec: int | None = None,
    source_family: str = "provided_rows",
    source_symbol: str | None = None,
    source_venue: str | None = None,
) -> tuple[Tuple[OHLCVCandle, ...], OHLCVAggregationDiagnostics]:
    requested = tuple(int(item) for item in timeframes_sec)
    normalized = _normalize_rows(rows)
    blocked: list[str] = []
    warnings: list[str] = []
    candles: list[OHLCVCandle] = []

    if not requested:
        blocked.append("timeframes_missing")
    if any(item not in TIMEFRAME_SECONDS for item in requested):
        blocked.append("unsupported_timeframe")
    if not normalized:
        blocked.append("ohlcv_rows_missing_or_unusable")
        return tuple(), OHLCVAggregationDiagnostics(
            requested_timeframes_sec=requested,
            input_row_count=0,
            usable_row_count=0,
            candle_count=0,
            blocked_by=tuple(dict.fromkeys(blocked)),
            warnings=tuple(warnings),
        )

    now_dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    latest_age = max((now_dt - normalized[-1][0]).total_seconds(), 0.0)
    stale = bool(max_latest_age_sec is not None and latest_age > float(max_latest_age_sec))
    if stale:
        warnings.append("latest_row_stale_for_ohlcv")

    for timeframe_sec in requested:
        if timeframe_sec not in TIMEFRAME_SECONDS:
            continue
        timeframe = timeframe_by_seconds(timeframe_sec)
        grouped: dict[datetime, list[tuple[datetime, float, float, Mapping[str, Any]]]] = {}
        for item in normalized:
            start = _bucket_start(item[0], timeframe_sec)
            grouped.setdefault(start, []).append(item)
        for start in sorted(grouped):
            items = grouped[start]
            prices = [item[1] for item in items]
            volume = sum(item[2] for item in items)
            trade_count = len(items)
            vwap = (sum(item[1] * item[2] for item in items) / volume) if volume > 0 else None
            end = datetime.fromtimestamp(start.timestamp() + timeframe_sec, tz=timezone.utc)
            expected_min_points = 2 if timeframe_sec <= 300 else 1
            gap = trade_count < expected_min_points
            candle_warnings = ("sparse_candle",) if gap else ()
            candles.append(
                OHLCVCandle(
                    timeframe=timeframe,
                    start_ts=_iso(start),
                    end_ts=_iso(end),
                    open=prices[0],
                    high=max(prices),
                    low=min(prices),
                    close=prices[-1],
                    volume=volume,
                    trade_count=trade_count,
                    vwap=vwap,
                    source_family=source_family,
                    source_symbol=source_symbol,
                    source_venue=source_venue,
                    row_count=trade_count,
                    gap=gap,
                    stale=stale,
                    warnings=candle_warnings,
                )
            )

    return tuple(candles), OHLCVAggregationDiagnostics(
        requested_timeframes_sec=requested,
        input_row_count=len(list(rows)) if isinstance(rows, list) else len(normalized),
        usable_row_count=len(normalized),
        candle_count=len(candles),
        blocked_by=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
