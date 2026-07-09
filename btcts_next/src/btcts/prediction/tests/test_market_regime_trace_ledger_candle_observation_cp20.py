# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_trace_ledger_candle_observation_cp20.py
# desc: CP20 tests for trace-ledger outcome resolution using candle-summary observations. Explicit option only; default CP18 latest-current behavior remains compatible.

from __future__ import annotations

import json
import sys

import pytest
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.observation_evaluator import warroom_closed_candle_relpath  # noqa: E402
from btcts.prediction.market_regime.tools.resolve_outcomes import (  # noqa: E402
    build_market_regime_trace_outcome_once_plan,
    main,
    resolve_market_regime_trace_outcomes_once,
)


def _write_latest_cards(root: Path) -> None:
    path = root / "prediction/market_regime/latest_cards.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_kind": "latest_cards",
        "run_id": "latest_current_range_run",
        "generated_at": "2026-07-08T12:20:00Z",
        "cards": [
            {"horizon": "現在", "horizon_key": "current", "horizon_sec": 0, "regime_code": "RANGE", "confidence_percent": 70, "detail": {"trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"}},
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_trace(root: Path) -> None:
    part = root / "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"
    part.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "artifact_kind": "trace_row",
        "prediction_family_id": "market_regime",
        "run_id": "trace_run_candle_cp20",
        "generated_at": "2026-07-08T12:00:00Z",
        "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl",
        "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
        "prediction_summary": {
            "generated_at": "2026-07-08T12:00:00Z",
            "horizons": [
                {"horizon": "現在", "horizon_key": "current", "horizon_sec": 0, "regime_code": "RANGE", "confidence_percent": 70, "evidence_quality": "PARTIAL", "freshness_state": "LIVE", "parameter_set_id": "market_regime_engine_parameter_set.v1"},
                {"horizon": "5分後", "horizon_key": "300s", "horizon_sec": 300, "regime_code": "RANGE", "confidence_percent": 70, "evidence_quality": "PARTIAL", "freshness_state": "LIVE", "parameter_set_id": "market_regime_engine_parameter_set.v1"},
                {"horizon": "15分後", "horizon_key": "900s", "horizon_sec": 900, "regime_code": "UP_TREND", "confidence_percent": 80, "evidence_quality": "PARTIAL", "freshness_state": "LIVE", "parameter_set_id": "market_regime_engine_parameter_set.v1"},
            ],
        },
        "safety": {"raw_market_data_duplicated": False, "broker_private_api_allowed": False, "autotrade_trigger_allowed": False, "would_send_to_broker": False},
    }
    part.write_text(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def _write_candles(root: Path) -> None:
    rows_60 = [
        {"time_utc": "2026-07-08T12:00:00Z", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60},
        {"time_utc": "2026-07-08T12:01:00Z", "open": 100.0, "high": 102.0, "low": 99.5, "close": 101.5, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60},
        {"time_utc": "2026-07-08T12:02:00Z", "open": 101.5, "high": 104.0, "low": 101.0, "close": 103.5, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60},
        {"time_utc": "2026-07-08T12:03:00Z", "open": 103.5, "high": 106.0, "low": 103.0, "close": 105.0, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60},
        {"time_utc": "2026-07-08T12:04:00Z", "open": 105.0, "high": 106.5, "low": 104.0, "close": 106.0, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60},
        {"time_utc": "2026-07-08T12:05:00Z", "open": 106.0, "high": 107.0, "low": 105.5, "close": 106.5, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60},
    ]
    rows_300 = [
        {"time_utc": "2026-07-08T12:00:00Z", "open": 100.0, "high": 105.0, "low": 99.0, "close": 103.0, "volume": 10.0, "trade_count": 100, "timeframe_sec": 300},
        {"time_utc": "2026-07-08T12:05:00Z", "open": 103.0, "high": 110.0, "low": 102.0, "close": 108.0, "volume": 10.0, "trade_count": 100, "timeframe_sec": 300},
        {"time_utc": "2026-07-08T12:10:00Z", "open": 108.0, "high": 113.0, "low": 107.0, "close": 112.0, "volume": 10.0, "trade_count": 100, "timeframe_sec": 300},
        {"time_utc": "2026-07-08T12:15:00Z", "open": 112.0, "high": 116.0, "low": 111.0, "close": 115.0, "volume": 10.0, "trade_count": 100, "timeframe_sec": 300},
    ]
    for timeframe, rows in ((60, rows_60), (300, rows_300)):
        path = root / warroom_closed_candle_relpath(timeframe_sec=timeframe)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def _fixture(root: Path) -> None:
    _write_latest_cards(root)
    _write_trace(root)
    _write_candles(root)


def test_cp20_default_trace_outcomes_keep_latest_current_observation(tmp_path: Path) -> None:
    _fixture(tmp_path)
    result = build_market_regime_trace_outcome_once_plan(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert result["observation_source"] == "latest_cards_current"
    rows = {row["horizon_key"]: row for row in result["candidate_rows"]}
    assert rows["300s"]["observed_regime_code"] == "RANGE"
    assert rows["300s"]["outcome_label"] == "hit"
    assert rows["900s"]["outcome_label"] == "miss"


def test_cp20_trace_outcomes_can_use_candle_summary_observation(tmp_path: Path) -> None:
    _fixture(tmp_path)
    result = build_market_regime_trace_outcome_once_plan(
        hot_root=tmp_path,
        resolved_at="2026-07-08T12:20:00Z",
        observation_source="candle_summary",
    )
    assert result["observation_source"] == "candle_summary"
    assert result["safety"]["reads_derived_warroom_candles_only"] is True
    rows = {row["horizon_key"]: row for row in result["candidate_rows"]}
    assert rows["300s"]["observed_regime_code"] == "UP_TREND"
    assert rows["300s"]["outcome_label"] == "miss"
    assert rows["900s"]["observed_regime_code"] == "UP_TREND"
    assert rows["900s"]["outcome_label"] == "hit"
    assert rows["300s"]["observation_summary"]["source_refs"][0].endswith("timeframe=60s/closed.jsonl")
    assert rows["900s"]["observation_summary"]["source_refs"][0].endswith("timeframe=300s/closed.jsonl")


def test_cp20_trace_once_with_candle_summary_appends_and_calibrates(tmp_path: Path) -> None:
    _fixture(tmp_path)
    result = resolve_market_regime_trace_outcomes_once(
        hot_root=tmp_path,
        resolved_at="2026-07-08T12:20:00Z",
        observation_source="candle_summary",
    )
    assert result["ok"] is True
    assert result["observation_source"] == "candle_summary"
    assert result["appended_outcome_count"] == 2
    part = tmp_path / "prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl"
    rows = [json.loads(line) for line in part.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_horizon = {row["horizon_key"]: row for row in rows}
    assert by_horizon["300s"]["outcome_label"] == "miss"
    assert by_horizon["900s"]["outcome_label"] == "hit"
    assert result["calibration_results"][0]["ok"] is True




def test_cp20_trace_ledger_cli_requires_explicit_observation_source(tmp_path: Path) -> None:
    _fixture(tmp_path)
    with pytest.raises(SystemExit) as raised:
        main([
            "--hot-root",
            str(tmp_path),
            "--source",
            "trace_ledger",
            "--preflight",
            "--resolved-at",
            "2026-07-08T12:20:00Z",
        ])
    assert raised.value.code == 2

    ok = main([
        "--hot-root",
        str(tmp_path),
        "--source",
        "trace_ledger",
        "--preflight",
        "--observation-source",
        "candle_summary",
        "--resolved-at",
        "2026-07-08T12:20:00Z",
    ])
    assert ok == 0


def test_cp20_resolve_outcomes_cli_exposes_observation_source_and_is_safe() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/tools/resolve_outcomes.py"
    text = path.read_text(encoding="utf-8")
    required = [
        "--observation-source",
        "Required when --source trace_ledger",
        "latest_cards_current",
        "candle_summary",
        "build_market_regime_candle_observation",
        "observation_source=",
    ]
    assert [token for token in required if token not in text] == []
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
