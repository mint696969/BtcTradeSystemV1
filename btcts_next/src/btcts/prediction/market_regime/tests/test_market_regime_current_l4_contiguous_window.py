# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_current_l4_contiguous_window.py
# desc: MR-F9.18A10 guards for latest contiguous 60-candle selection without interpolation.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from btcts.prediction.market_regime.features.current_l4_candle_window import (
    current_l4_candle_rows,
    future_origin_l4_candle_rows,
    select_latest_contiguous_l4_candle_window,
)
from types import SimpleNamespace


def _rows(count: int, *, start_minute: int = 0):
    base = datetime(2026, 7, 16, 8, 0, tzinfo=timezone.utc) + timedelta(minutes=start_minute)
    return tuple(
        {
            "time_utc": (base + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
        }
        for index in range(count)
    )


def test_selects_latest_exact_contiguous_window() -> None:
    rows = _rows(80)
    selected = select_latest_contiguous_l4_candle_window(rows, window_size=60)
    assert len(selected) == 60
    assert selected[0]["time_utc"] == rows[20]["time_utc"]
    assert selected[-1]["time_utc"] == rows[-1]["time_utc"]


def test_skips_recent_gap_and_selects_previous_contiguous_window() -> None:
    early = _rows(70)
    late = _rows(20, start_minute=71)
    rows = (*early, *late)
    selected = select_latest_contiguous_l4_candle_window(rows, window_size=60)
    assert len(selected) == 60
    assert selected[-1]["time_utc"] == early[-1]["time_utc"]
    assert selected[-1]["time_utc"] != rows[-1]["time_utc"]


def test_does_not_interpolate_or_cross_gap() -> None:
    rows = list(_rows(60))
    del rows[12]
    selected = select_latest_contiguous_l4_candle_window(tuple(rows), window_size=60)
    assert selected == ()


def test_rejects_duplicate_or_reverse_time() -> None:
    rows = list(_rows(61))
    rows[30] = dict(rows[29])
    assert select_latest_contiguous_l4_candle_window(tuple(rows), window_size=60) == ()

def test_current_window_remains_tail_limited_and_allows_short_history() -> None:
    rows = _rows(3)
    snapshot = SimpleNamespace(warroom_candles=SimpleNamespace(closed_candles=rows))
    assert current_l4_candle_rows(snapshot) == rows


def test_future_origin_window_requires_latest_contiguous_sixty() -> None:
    early = _rows(70)
    late = _rows(20, start_minute=71)
    snapshot = SimpleNamespace(
        warroom_candles=SimpleNamespace(
            closed_candles=(*early, *late),
            timeframe_sec=60,
        )
    )
    selected = future_origin_l4_candle_rows(snapshot)
    assert len(selected) == 60
    assert selected[-1]["time_utc"] == early[-1]["time_utc"]
