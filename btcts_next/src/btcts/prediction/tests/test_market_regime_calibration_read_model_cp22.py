# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_calibration_read_model_cp22.py
# desc: CP22 tests for market-regime calibration read model. Keeps candle_summary and latest_cards_current calibration views separated; no raw market reads or execution side effects.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.calibration_read_model import (  # noqa: E402
    CALIBRATION_LATEST_READ_MODEL_RELPATH,
    MARKET_REGIME_CALIBRATION_READ_MODEL_VERSION,
    build_market_regime_calibration_read_model,
    calibration_latest_read_model_relpath,
    write_market_regime_calibration_read_model,
)
from btcts.prediction.market_regime.calibration_summary import calibration_daily_summary_relpath, calibration_table_relpath  # noqa: E402


def _bucket(key: str, *, total: int, hit: int, partial: int, miss: int, score: float) -> dict:
    return {
        "key": key,
        "total": total,
        "known_total": total,
        "counts": {"hit": hit, "partial": partial, "miss": miss, "unknown": 0, "invalidated": 0},
        "hit_rate": round(hit / total, 4),
        "partial_rate": round(partial / total, 4),
        "miss_rate": round(miss / total, 4),
        "calibration_score": score,
        "avg_confidence_percent": 68.5,
        "sample_trace_refs": ["prediction/market_regime/ledgers/date=2026-07-08/hour=14/part-00001.jsonl"],
    }


def _daily() -> dict:
    return {
        "artifact_kind": "calibration_daily_summary",
        "prediction_family_id": "market_regime",
        "date": "2026-07-08",
        "row_count": 1145,
        "overall": _bucket("overall", total=1145, hit=993, partial=71, miss=81, score=0.8983),
        "by_observation_source": [
            _bucket("candle_summary", total=341, hit=189, partial=71, miss=81, score=0.6584),
            _bucket("latest_cards_current", total=804, hit=804, partial=0, miss=0, score=1.0),
        ],
        "by_observation_source_horizon": [
            _bucket("candle_summary|300s", total=80, hit=41, partial=20, miss=19, score=0.6375),
            _bucket("latest_cards_current|300s", total=246, hit=246, partial=0, miss=0, score=1.0),
        ],
    }


def _table() -> dict:
    return {
        "artifact_kind": "calibration_table",
        "prediction_family_id": "market_regime",
        "month": "2026-07",
        "observation_source_row_count": 2,
        "observation_source_rows": [
            dict(_bucket("candle_summary|300s", total=80, hit=41, partial=20, miss=19, score=0.6375), date="2026-07-08"),
            dict(_bucket("latest_cards_current|300s", total=246, hit=246, partial=0, miss=0, score=1.0), date="2026-07-08"),
        ],
    }


def test_cp22_build_calibration_read_model_prefers_candle_summary() -> None:
    model = build_market_regime_calibration_read_model(daily_summary=_daily(), calibration_table=_table())
    assert model["calibration_read_model_version"] == MARKET_REGIME_CALIBRATION_READ_MODEL_VERSION
    assert model["artifact_kind"] == "calibration_read_model"
    assert model["primary_observation_source"] == "candle_summary"
    assert model["primary"]["calibration_score"] == 0.6584
    assert model["latest_cards_current_reference"]["calibration_score"] == 1.0
    assert model["table_observation_source_row_count"] == 2
    assert model["source_refs"]["daily_summary_json"] == calibration_daily_summary_relpath("2026-07-08")
    assert model["safety"]["parameter_auto_promotion_allowed"] is False
    assert "raw_candles" not in json.dumps(model, ensure_ascii=False)


def test_cp22_build_calibration_read_model_falls_back_to_latest_cards_current() -> None:
    daily = _daily()
    daily["by_observation_source"] = [_bucket("latest_cards_current", total=804, hit=804, partial=0, miss=0, score=1.0)]
    daily["by_observation_source_horizon"] = [_bucket("latest_cards_current|300s", total=246, hit=246, partial=0, miss=0, score=1.0)]
    model = build_market_regime_calibration_read_model(daily_summary=daily, calibration_table={})
    assert model["primary_observation_source"] == "latest_cards_current"
    assert model["primary"]["known_total"] == 804


def test_cp22_write_calibration_read_model_artifact(tmp_path: Path) -> None:
    daily_path = tmp_path / calibration_daily_summary_relpath("2026-07-08")
    table_path = tmp_path / calibration_table_relpath("2026-07")
    daily_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    daily_path.write_text(json.dumps(_daily(), ensure_ascii=False), encoding="utf-8")
    table_path.write_text(json.dumps(_table(), ensure_ascii=False), encoding="utf-8")
    result = write_market_regime_calibration_read_model(tmp_path, date="2026-07-08")
    assert result["ok"] is True
    assert result["primary_observation_source"] == "candle_summary"
    assert result["calibration_read_model_json"] == CALIBRATION_LATEST_READ_MODEL_RELPATH == calibration_latest_read_model_relpath()
    payload = json.loads((tmp_path / result["calibration_read_model_json"]).read_text(encoding="utf-8"))
    assert payload["primary"]["counts"]["miss"] == 81
    assert payload["safety"]["broker_private_api_allowed"] is False
