# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_calibration_summary_cp13.py
# desc: CP13 tests for market-regime calibration summary MVP. Tmp outcome rows only; no raw market read, scheduler, broker, AutoTrade, or parameter auto-promotion.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.calibration_summary import (  # noqa: E402
    MARKET_REGIME_CALIBRATION_SUMMARY_VERSION,
    build_market_regime_calibration_summary,
    build_market_regime_calibration_table,
    calibration_daily_summary_relpath,
    calibration_table_relpath,
    read_market_regime_outcome_rows,
    validate_market_regime_calibration_summary,
    write_market_regime_calibration_artifacts,
)


def _row(label: str, *, horizon_key: str = "900s", regime: str = "RANGE", parameter_set_id: str = "ps.v1", confidence: int = 70) -> dict:
    return {
        "schema_version": "market_regime_outcome.2026_07_08.v1",
        "artifact_kind": "outcome_row",
        "prediction_family_id": "market_regime",
        "outcome_id": f"run:{horizon_key}:{label}",
        "run_id": "run",
        "generated_at": "2026-07-08T12:00:00Z",
        "resolved_at": "2026-07-08T12:16:00Z",
        "horizon_key": horizon_key,
        "horizon_sec": 900 if horizon_key == "900s" else 300,
        "predicted_regime_code": regime,
        "observed_regime_code": regime if label == "hit" else "UP_TREND",
        "outcome_label": label,
        "confidence_percent": confidence,
        "parameter_set_id": parameter_set_id,
        "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl",
    }


def test_cp13_calibration_relpaths_are_stable() -> None:
    assert calibration_daily_summary_relpath("2026-07-08") == "prediction/market_regime/calibration/date=2026-07-08/daily_summary.json"
    assert calibration_table_relpath("2026-07") == "prediction/market_regime/calibration/month=2026-07/calibration_table.json"


def test_cp13_build_daily_summary_aggregates_outcomes() -> None:
    rows = [
        _row("hit", horizon_key="900s", regime="RANGE", parameter_set_id="ps.v1", confidence=70),
        _row("partial", horizon_key="900s", regime="RANGE", parameter_set_id="ps.v1", confidence=60),
        _row("miss", horizon_key="300s", regime="UP_TREND", parameter_set_id="ps.v2", confidence=80),
        _row("unknown", horizon_key="300s", regime="UP_TREND", parameter_set_id="ps.v2", confidence=50),
    ]
    summary = build_market_regime_calibration_summary(rows=rows, date="2026-07-08")
    assert summary["calibration_summary_version"] == MARKET_REGIME_CALIBRATION_SUMMARY_VERSION
    assert summary["row_count"] == 4
    assert summary["overall"]["known_total"] == 3
    assert summary["overall"]["calibration_score"] == 0.5
    by_horizon = {row["key"]: row for row in summary["by_horizon"]}
    assert by_horizon["900s"]["counts"]["hit"] == 1
    assert by_horizon["900s"]["counts"]["partial"] == 1
    assert by_horizon["300s"]["counts"]["miss"] == 1
    assert validate_market_regime_calibration_summary(summary)["ok"] is True
    assert summary["safety"]["parameter_auto_promotion_allowed"] is False


def test_cp13_build_calibration_table_from_daily_summary() -> None:
    summary = build_market_regime_calibration_summary(rows=[_row("hit"), _row("partial")], date="2026-07-08")
    table = build_market_regime_calibration_table(daily_summaries=[summary], month="2026-07")
    assert table["artifact_kind"] == "calibration_table"
    assert table["month"] == "2026-07"
    assert table["daily_summary_count"] == 1
    assert table["row_count"] >= 1
    assert table["safety"]["broker_private_api_allowed"] is False


def test_cp13_write_calibration_artifacts_from_outcome_rows(tmp_path: Path) -> None:
    part = tmp_path / "prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl"
    part.parent.mkdir(parents=True, exist_ok=True)
    rows = [_row("hit"), _row("miss")]
    part.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    read_rows = read_market_regime_outcome_rows(tmp_path, date="2026-07-08")
    assert len(read_rows) == 2
    result = write_market_regime_calibration_artifacts(tmp_path, date="2026-07-08")
    assert result["ok"] is True
    assert result["outcome_row_count"] == 2
    assert (tmp_path / result["daily_summary_json"]).exists()
    assert (tmp_path / result["calibration_table_json"]).exists()
    payload = json.loads((tmp_path / result["daily_summary_json"]).read_text(encoding="utf-8"))
    assert payload["overall"]["known_total"] == 2
    assert payload["safety"]["raw_market_data_duplicated"] is False


def test_cp13_summary_rejects_raw_payload_and_disables_auto_promotion() -> None:
    summary = build_market_regime_calibration_summary(rows=[_row("hit"), {"raw_candles": [{"close": 1}]}], date="2026-07-08")
    assert summary["row_count"] == 1
    assert summary["input_failure_count"] == 1
    assert "forbidden_raw_payload_key_present" in summary["input_failures"][0]
    bad = dict(summary)
    bad["safety"] = dict(summary["safety"])
    bad["safety"]["parameter_auto_promotion_allowed"] = True
    result = validate_market_regime_calibration_summary(bad)
    assert result["ok"] is False
    assert "safety_parameter_auto_promotion_allowed_not_false" in result["failures"]
