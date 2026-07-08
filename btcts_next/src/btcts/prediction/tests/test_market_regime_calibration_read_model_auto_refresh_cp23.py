# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_calibration_read_model_auto_refresh_cp23.py
# desc: CP23 tests that outcome resolution refreshes calibration/latest_read_model.json after calibration updates. Artifact-only; no raw reads, scheduler, broker, AutoTrade, or parameter promotion.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.calibration_read_model import CALIBRATION_LATEST_READ_MODEL_RELPATH  # noqa: E402
from btcts.prediction.market_regime.observation_evaluator import warroom_closed_candle_relpath  # noqa: E402
from btcts.prediction.market_regime.tools.resolve_outcomes import (  # noqa: E402
    resolve_market_regime_outcomes_once,
    resolve_market_regime_trace_outcomes_once,
)


def _latest_card(horizon_key: str, horizon_sec: int, regime: str) -> dict:
    return {
        "horizon": "現在" if horizon_sec == 0 else horizon_key,
        "horizon_key": horizon_key,
        "horizon_sec": horizon_sec,
        "regime_code": regime,
        "confidence_percent": 70,
        "detail": {"trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"},
    }


def _write_latest_cards(root: Path) -> None:
    path = root / "prediction/market_regime/latest_cards.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_kind": "latest_cards",
        "run_id": "latest_run_cp23",
        "generated_at": "2026-07-08T12:00:00Z",
        "cards": [
            _latest_card("current", 0, "RANGE"),
            _latest_card("300s", 300, "RANGE"),
            _latest_card("900s", 900, "UP_TREND"),
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_trace(root: Path) -> None:
    part = root / "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"
    part.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "artifact_kind": "trace_row",
        "prediction_family_id": "market_regime",
        "run_id": "trace_run_cp23",
        "generated_at": "2026-07-08T12:00:00Z",
        "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl",
        "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
        "prediction_summary": {
            "generated_at": "2026-07-08T12:00:00Z",
            "horizons": [
                {"horizon": "現在", "horizon_key": "current", "horizon_sec": 0, "regime_code": "RANGE", "confidence_percent": 70, "evidence_quality": "PARTIAL", "freshness_state": "LIVE"},
                {"horizon": "5分後", "horizon_key": "300s", "horizon_sec": 300, "regime_code": "RANGE", "confidence_percent": 70, "evidence_quality": "PARTIAL", "freshness_state": "LIVE"},
                {"horizon": "15分後", "horizon_key": "900s", "horizon_sec": 900, "regime_code": "UP_TREND", "confidence_percent": 80, "evidence_quality": "PARTIAL", "freshness_state": "LIVE"},
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


def test_cp23_latest_cards_once_refreshes_calibration_read_model(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    result = resolve_market_regime_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert result["ok"] is True
    assert result["appended_outcome_count"] == 2
    assert result["calibration_read_model_result"]["ok"] is True
    path = tmp_path / CALIBRATION_LATEST_READ_MODEL_RELPATH
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["artifact_kind"] == "calibration_read_model"
    assert payload["primary_observation_source"] == "latest_cards_current"
    assert payload["safety"]["parameter_auto_promotion_allowed"] is False


def test_cp23_trace_candle_once_refreshes_primary_candle_calibration_read_model(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    _write_trace(tmp_path)
    _write_candles(tmp_path)
    result = resolve_market_regime_trace_outcomes_once(
        hot_root=tmp_path,
        resolved_at="2026-07-08T12:20:00Z",
        observation_source="candle_summary",
    )
    assert result["ok"] is True
    assert result["appended_outcome_count"] == 2
    assert result["calibration_read_model_results"][0]["ok"] is True
    assert result["calibration_read_model_results"][0]["primary_observation_source"] == "candle_summary"
    path = tmp_path / CALIBRATION_LATEST_READ_MODEL_RELPATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["primary_observation_source"] == "candle_summary"
    assert payload["primary"]["counts"]["hit"] == 1
    assert payload["primary"]["counts"]["miss"] == 1
    assert "raw_candles" not in json.dumps(payload, ensure_ascii=False)


def test_cp23_no_calibration_does_not_write_read_model(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    result = resolve_market_regime_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z", update_calibration=False)
    assert result["ok"] is True
    assert result["appended_outcome_count"] == 2
    assert result["calibration_result"] == {}
    assert result["calibration_read_model_result"] == {}
    assert not (tmp_path / CALIBRATION_LATEST_READ_MODEL_RELPATH).exists()


def test_cp23_resolve_outcomes_source_mentions_calibration_read_model_and_no_execution_side_effects() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/tools/resolve_outcomes.py"
    text = path.read_text(encoding="utf-8")
    required = [
        "write_market_regime_calibration_read_model",
        "calibration_read_model_result",
        "calibration_read_model_results",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "import streamlit",
        "from btcts.apps.operator_ui",
        "build_market_regime_source_snapshot",
        "build_market_regime_feature_bundle",
        "classify_market_regime_feature_bundle",
        "subprocess.Popen",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
