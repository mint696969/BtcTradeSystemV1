# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_candle_observation_evaluator_cp19.py
# desc: CP19 tests for candle-summary observation evaluator MVP. Derived WarRoom candles only; no raw payload duplication, classifier, scheduler, broker, AutoTrade, or parameter promotion.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.observation_evaluator import (  # noqa: E402
    MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION,
    build_market_regime_candle_observation,
    classify_candle_window_regime,
    read_warroom_closed_candles_for_window,
    select_observation_candle_timeframe_sec,
    summarize_candle_window,
    warroom_closed_candle_relpath,
)


def _write_candles(root: Path, timeframe_sec: int, rows: list[dict]) -> None:
    path = root / warroom_closed_candle_relpath(timeframe_sec=timeframe_sec)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def _row(ts: str, open_: float, high: float, low: float, close: float) -> dict:
    return {"time_utc": ts, "open": open_, "high": high, "low": low, "close": close, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60, "raw_trades": "not_written_to_fixture"}


def _prediction(horizon_sec: int = 300) -> dict:
    return {"generated_at": "2026-07-08T12:00:00Z", "horizon_sec": horizon_sec, "horizon_key": f"{horizon_sec}s", "regime_code": "RANGE"}


def test_cp19_candle_relpath_and_timeframe_selection_are_stable() -> None:
    assert warroom_closed_candle_relpath(timeframe_sec=300) == "data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=300s/closed.jsonl"
    assert select_observation_candle_timeframe_sec(300) == 60
    assert select_observation_candle_timeframe_sec(900) == 300
    assert select_observation_candle_timeframe_sec(21600) == 900
    assert select_observation_candle_timeframe_sec(86400) == 3600


def test_cp19_reads_only_window_and_summarizes_compactly(tmp_path: Path) -> None:
    _write_candles(tmp_path, 60, [
        _row("2026-07-08T11:59:00Z", 100, 101, 99, 100),
        _row("2026-07-08T12:00:00Z", 100, 101, 99, 100.1),
        _row("2026-07-08T12:01:00Z", 100.1, 101.0, 99.5, 100.2),
        _row("2026-07-08T12:06:00Z", 100.2, 101, 99, 100),
    ])
    rows = read_warroom_closed_candles_for_window(tmp_path, start_utc="2026-07-08T12:00:00Z", end_utc="2026-07-08T12:05:00Z", timeframe_sec=60)
    assert len(rows) == 2
    summary = summarize_candle_window(rows)
    assert summary["ok"] is True
    assert summary["candle_count"] == 2
    assert "raw_trades" not in json.dumps(summary)


def test_cp19_classifies_basic_range_trend_and_chop_windows() -> None:
    range_summary = summarize_candle_window([
        {"time_utc": "2026-07-08T12:00:00Z", "open": 100, "high": 101, "low": 99, "close": 100.0},
        {"time_utc": "2026-07-08T12:01:00Z", "open": 100, "high": 101, "low": 99, "close": 100.1},
    ])
    up_summary = summarize_candle_window([
        {"time_utc": "2026-07-08T12:00:00Z", "open": 100, "high": 102, "low": 99, "close": 101.5},
        {"time_utc": "2026-07-08T12:01:00Z", "open": 101.5, "high": 106, "low": 101, "close": 105},
    ])
    chop_summary = summarize_candle_window([
        {"time_utc": "2026-07-08T12:00:00Z", "open": 100, "high": 110, "low": 90, "close": 100},
        {"time_utc": "2026-07-08T12:01:00Z", "open": 100, "high": 109, "low": 91, "close": 99.5},
    ])
    assert classify_candle_window_regime(range_summary)[0] == "RANGE"
    assert classify_candle_window_regime(up_summary)[0] == "UP_TREND"
    assert classify_candle_window_regime(chop_summary)[0] == "HIGH_VOL_CHOP"


def test_cp19_builds_outcome_observation_from_derived_candles(tmp_path: Path) -> None:
    _write_candles(tmp_path, 60, [
        _row("2026-07-08T12:00:00Z", 100, 101, 99, 100.0),
        _row("2026-07-08T12:01:00Z", 100, 101, 99, 100.1),
        _row("2026-07-08T12:02:00Z", 100.1, 101, 99, 100.0),
    ])
    observation = build_market_regime_candle_observation(tmp_path, prediction=_prediction(), resolved_at="2026-07-08T12:05:00Z", timeframe_sec=60)
    assert observation["observation_evaluator_version"] == MARKET_REGIME_CANDLE_OBSERVATION_EVALUATOR_VERSION
    assert observation["observation_available"] is True
    assert observation["observed_regime_code"] == "RANGE"
    assert observation["source_refs"][0].endswith("timeframe=60s/closed.jsonl")
    assert observation["safety"]["raw_market_data_duplicated"] is False
    assert observation["safety"]["raw_trades_read"] is False
    assert observation["safety"]["broker_private_api_allowed"] is False
    assert "raw_trades" not in json.dumps(observation["candle_summary"], ensure_ascii=False)
    assert "raw_trades" not in observation["candle_summary"]
    assert "not_written_to_fixture" not in json.dumps(observation, ensure_ascii=False)


def test_cp19_missing_candles_returns_unknown_observation(tmp_path: Path) -> None:
    observation = build_market_regime_candle_observation(tmp_path, prediction=_prediction(), resolved_at="2026-07-08T12:05:00Z", timeframe_sec=60)
    assert observation["observation_available"] is False
    assert observation["observed_regime_code"] == "UNKNOWN"
    assert observation["safety"]["autotrade_trigger_allowed"] is False


def test_cp19_module_has_no_execution_or_classifier_side_effects() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/observation_evaluator.py"
    text = path.read_text(encoding="utf-8")
    forbidden = [
        "import streamlit",
        "from btcts.apps.operator_ui",
        "classify_market_regime_feature_bundle",
        "build_market_regime_source_snapshot",
        "subprocess.Popen",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
