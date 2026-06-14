# path: ./btcts_next/src/btcts/autotrade/read_model/temporal_flow_adapter.py
# desc: Temporal flow feature adapter for AutoTrade. Read-only row-window calculations.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Tuple

from btcts.autotrade.config.models import ParameterSet
from btcts.autotrade.read_model.models import TemporalFlowFeatures


@dataclass(frozen=True)
class TemporalFlowAdapterDiagnostics:
    row_count: int
    usable_row_count: int
    windows_sec: Tuple[int, ...]
    usable: bool
    max_feature_age_sec: float | None
    blocked_by: Tuple[str, ...]
    warnings: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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


def _event_ts(row: dict[str, Any]) -> datetime | None:
    return _parse_ts(row.get("collector_ts") or row.get("exchange_ts") or row.get("event_ts"))


def _event_ts_str(row: dict[str, Any]) -> str | None:
    dt = _event_ts(row)
    if dt is None:
        return None
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sort_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched: list[tuple[datetime, dict[str, Any]]] = []
    for row in rows:
        dt = _event_ts(row)
        if dt is not None:
            enriched.append((dt, row))
    enriched.sort(key=lambda item: item[0])
    return [row for _, row in enriched]


def _latest_value(rows: list[dict[str, Any]], key: str) -> float | None:
    for row in reversed(rows):
        value = _float_or_none(row.get(key))
        if value is not None:
            return value
    return None


def _oldest_value(rows: list[dict[str, Any]], key: str) -> float | None:
    for row in rows:
        value = _float_or_none(row.get(key))
        if value is not None:
            return value
    return None


def _change(rows: list[dict[str, Any]], key: str) -> float | None:
    old = _oldest_value(rows, key)
    new = _latest_value(rows, key)
    if old is None or new is None:
        return None
    return new - old


def _return(rows: list[dict[str, Any]], key: str) -> float | None:
    old = _oldest_value(rows, key)
    new = _latest_value(rows, key)
    if old is None or new is None or old == 0:
        return None
    return (new - old) / old


def _window_rows(sorted_rows: list[dict[str, Any]], *, anchor: datetime, window_sec: int) -> list[dict[str, Any]]:
    start = anchor.timestamp() - int(window_sec)
    return [row for row in sorted_rows if (_event_ts(row) is not None and _event_ts(row).timestamp() >= start and _event_ts(row).timestamp() <= anchor.timestamp())]


def _pressure_direction(value: float | None, *, threshold: float = 0.02) -> str:
    if value is None:
        return "unknown"
    if value > threshold:
        return "buy"
    if value < -threshold:
        return "sell"
    return "flat"


def _pattern_flags(*, spread_change: float | None, imbalance_change: float | None, wall_ratio_change: float | None, mid_return_300s: float | None) -> dict[str, Any]:
    return {
        "liquidity_vacuum_candidate": bool(spread_change is not None and spread_change > 3000),
        "breakout_attempt": bool(mid_return_300s is not None and abs(mid_return_300s) >= 0.0015),
        "range_chop_candidate": bool(mid_return_300s is not None and abs(mid_return_300s) < 0.0005 and spread_change is not None and abs(spread_change) < 1000),
        "board_trade_divergence": bool(imbalance_change is not None and wall_ratio_change is not None and (imbalance_change * wall_ratio_change) < 0),
    }


def build_temporal_flow_features_from_rows(
    rows: Iterable[dict[str, Any]],
    *,
    parameter_set: ParameterSet,
    now: datetime | None = None,
    min_points_per_window: int | None = None,
    max_feature_age_sec: float | None = None,
) -> tuple[TemporalFlowFeatures, TemporalFlowAdapterDiagnostics]:
    sorted_rows = _sort_rows(rows)
    windows = tuple(parameter_set.temporal_flow.windows_sec)
    min_points = int(min_points_per_window if min_points_per_window is not None else parameter_set.temporal_flow.min_points_per_window)
    max_age = float(max_feature_age_sec if max_feature_age_sec is not None else parameter_set.freshness.max_temporal_feature_age_sec)
    blocked: list[str] = []

    if not sorted_rows:
        blocked.append("temporal_rows_missing")
        generated_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        features = TemporalFlowFeatures(windows_sec=windows, generated_at=generated_at, usable=False, blocked_by=tuple(blocked))
        return features, TemporalFlowAdapterDiagnostics(0, 0, windows, False, None, tuple(blocked))

    anchor = _event_ts(sorted_rows[-1]) or (now or datetime.now(timezone.utc))
    now_dt = now or datetime.now(timezone.utc)
    age = max((now_dt.astimezone(timezone.utc) - anchor).total_seconds(), 0.0)
    if age > max_age:
        blocked.append("temporal_feature_stale")

    window_sets = {window: _window_rows(sorted_rows, anchor=anchor, window_sec=window) for window in windows}
    if any(len(items) < min_points for items in window_sets.values()):
        blocked.append("temporal_window_insufficient_points")

    w15 = window_sets.get(15, [])
    w30 = window_sets.get(30, [])
    w60 = window_sets.get(60, [])
    w180 = window_sets.get(180, [])
    w300 = window_sets.get(300, [])

    spread_change_60 = _change(w60, "spread")
    spread_change_300 = _change(w300, "spread")
    imbalance_change_60 = _change(w60, "imbalance")
    imbalance_change_300 = _change(w300, "imbalance")
    wall_ratio_change_60 = _change(w60, "wall_ratio")
    wall_ratio_change_300 = _change(w300, "wall_ratio")
    trade_delta_change_60 = _change(w60, "trade_delta")
    trade_delta_change_300 = _change(w300, "trade_delta")
    mid_return_15 = _return(w15, "mid_price")
    mid_return_30 = _return(w30, "mid_price")
    mid_return_60 = _return(w60, "mid_price")
    mid_return_180 = _return(w180, "mid_price")
    mid_return_300 = _return(w300, "mid_price")

    pressure_base = imbalance_change_60 if imbalance_change_60 is not None else wall_ratio_change_60
    pressure_300 = imbalance_change_300 if imbalance_change_300 is not None else wall_ratio_change_300
    pressure_acceleration = _pressure_direction(pressure_base)
    pressure_decay = bool(pressure_base is not None and pressure_300 is not None and abs(pressure_base) < abs(pressure_300))

    generated_at = anchor.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    features = TemporalFlowFeatures(
        windows_sec=windows,
        generated_at=generated_at,
        source_snapshot_ids=tuple(str(row.get("snapshot_id") or row.get("source_series_id") or _event_ts_str(row) or "") for row in sorted_rows[-min(len(sorted_rows), 8):]),
        max_feature_age_sec=age,
        usable=not blocked,
        blocked_by=tuple(dict.fromkeys(blocked)),
        temporal_liquidity_flow={
            "spread_change_60s": spread_change_60,
            "spread_change_300s": spread_change_300,
            "wall_ratio_change_60s": wall_ratio_change_60,
            "wall_ratio_change_300s": wall_ratio_change_300,
        },
        temporal_price_flow={
            "mid_return_15s": mid_return_15,
            "mid_return_30s": mid_return_30,
            "mid_return_60s": mid_return_60,
            "mid_return_180s": mid_return_180,
            "mid_return_300s": mid_return_300,
        },
        temporal_pressure_flow={
            "imbalance_change_60s": imbalance_change_60,
            "imbalance_change_300s": imbalance_change_300,
            "wall_ratio_change_60s": wall_ratio_change_60,
            "wall_ratio_change_300s": wall_ratio_change_300,
            "trade_delta_change_60s": trade_delta_change_60,
            "trade_delta_change_300s": trade_delta_change_300,
            "pressure_acceleration": pressure_acceleration,
            "pressure_decay": pressure_decay,
        },
        temporal_pattern_flags=_pattern_flags(
            spread_change=spread_change_300,
            imbalance_change=imbalance_change_300,
            wall_ratio_change=wall_ratio_change_300,
            mid_return_300s=mid_return_300,
        ),
    )
    return features, TemporalFlowAdapterDiagnostics(
        row_count=len(sorted_rows),
        usable_row_count=sum(len(items) for items in window_sets.values()),
        windows_sec=windows,
        usable=features.usable,
        max_feature_age_sec=age,
        blocked_by=features.blocked_by,
    )
