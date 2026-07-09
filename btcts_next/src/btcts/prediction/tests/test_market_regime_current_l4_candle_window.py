# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_current_l4_candle_window.py
# desc: Tests for pure current L4 candle-window summary helpers. No reads, writes, UI, broker, scheduler, or AutoTrade.

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.features.current_l4_candle_window import (  # noqa: E402
    CURRENT_L4_CANDLE_WINDOW_MAX_ROWS,
    current_l4_candle_regime_hint,
    current_l4_candle_rows,
    summarize_current_l4_candle_rows,
)


def _row(ts: str, open_: float, high: float, low: float, close: float) -> dict:
    return {"time_utc": ts, "open": open_, "high": high, "low": low, "close": close}


def test_mr_a2_current_l4_candle_rows_are_tail_limited() -> None:
    rows = [_row(f"2026-07-09T00:{index:02d}:00Z", 100.0, 101.0, 99.0, 100.0) for index in range(65)]
    snapshot = SimpleNamespace(warroom_candles=SimpleNamespace(closed_candles=tuple(rows)))
    selected = current_l4_candle_rows(snapshot)  # type: ignore[arg-type]
    assert len(selected) == CURRENT_L4_CANDLE_WINDOW_MAX_ROWS
    assert selected[0]["time_utc"] == "2026-07-09T00:05:00Z"


def test_mr_a2_summarizes_current_l4_window_without_raw_payloads() -> None:
    summary = summarize_current_l4_candle_rows((
        _row("2026-07-09T00:00:00Z", 100.0, 101.0, 99.5, 100.5),
        _row("2026-07-09T00:01:00Z", 100.5, 103.0, 100.0, 102.5),
    ))
    assert summary["ok"] is True
    assert summary["candle_count"] == 2
    assert summary["net_change_bps"] > 0
    assert summary["range_bps"] > 0
    assert "raw" not in str(summary).lower()


def test_mr_a2_current_l4_regime_hint_basic_cases() -> None:
    up = summarize_current_l4_candle_rows((
        _row("2026-07-09T00:00:00Z", 100.0, 101.0, 99.8, 100.5),
        _row("2026-07-09T00:01:00Z", 100.5, 105.0, 100.4, 104.9),
    ))
    chop = summarize_current_l4_candle_rows((
        _row("2026-07-09T00:00:00Z", 100.0, 110.0, 90.0, 100.0),
        _row("2026-07-09T00:01:00Z", 100.0, 109.0, 91.0, 99.8),
    ))
    low_vol = summarize_current_l4_candle_rows((
        _row("2026-07-09T00:00:00Z", 100.0, 100.05, 99.95, 100.01),
        _row("2026-07-09T00:01:00Z", 100.01, 100.06, 99.96, 100.02),
    ))
    assert current_l4_candle_regime_hint(up)[0] == "UP_TREND"
    assert current_l4_candle_regime_hint(chop)[0] == "HIGH_VOL_CHOP"
    assert current_l4_candle_regime_hint(low_vol)[0] == "LOW_VOL_COMPRESSION"
