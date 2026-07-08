# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_outcome_calibration_once_tool_cp17.py
# desc: CP17 tests for market-regime outcome/calibration once tool. Uses latest_cards artifact snapshots only; no raw market reads, scheduler, broker, AutoTrade, or parameter auto-promotion.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.tools.resolve_outcomes import (  # noqa: E402
    MARKET_REGIME_RESOLVE_OUTCOMES_TOOL_VERSION,
    build_market_regime_outcome_once_plan,
    resolve_market_regime_outcomes_once,
)


def _card(horizon_key: str, horizon_sec: int, regime: str = "RANGE") -> dict:
    return {
        "horizon": "現在" if horizon_sec == 0 else horizon_key,
        "horizon_key": horizon_key,
        "horizon_sec": horizon_sec,
        "regime_code": regime,
        "regime_label": "レンジ" if regime == "RANGE" else regime,
        "confidence_percent": 70,
        "evidence_quality": "PARTIAL",
        "freshness_badge": "LIVE",
        "detail": {
            "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
            "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl",
        },
    }


def _write_latest_cards(root: Path, *, generated_at: str = "2026-07-08T12:00:00Z") -> None:
    path = root / "prediction/market_regime/latest_cards.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "market_regime_latest_cards.2026_07_08.v1",
        "artifact_family": "prediction/market_regime",
        "artifact_kind": "latest_cards",
        "prediction_family_id": "market_regime",
        "run_id": "market_regime_cp17_run",
        "prediction_id": "market_regime_cp17_run:latest",
        "generated_at": generated_at,
        "parameter_set_id": "market_regime_engine_parameter_set.v1",
        "cards": [
            _card("current", 0, "RANGE"),
            _card("300s", 300, "RANGE"),
            _card("900s", 900, "UP_TREND"),
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_cp17_preflight_builds_expired_outcome_plan_without_writes(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    result = build_market_regime_outcome_once_plan(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert result["tool_version"] == MARKET_REGIME_RESOLVE_OUTCOMES_TOOL_VERSION
    assert result["expired_prediction_count"] == 2
    assert result["candidate_outcome_count"] == 2
    assert result["unexpired_prediction_count"] == 0
    assert result["observed_regime_code"] == "RANGE"
    assert result["would_write"] is False
    assert result["safety"]["raw_market_data_read"] is False
    assert not (tmp_path / "prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl").exists()


def test_cp17_once_appends_outcomes_and_writes_calibration(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    result = resolve_market_regime_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert result["ok"] is True
    assert result["appended_outcome_count"] == 2
    part = tmp_path / "prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl"
    assert part.exists()
    rows = [json.loads(line) for line in part.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 2
    by_horizon = {row["horizon_key"]: row for row in rows}
    assert by_horizon["300s"]["outcome_label"] == "hit"
    assert by_horizon["900s"]["outcome_label"] == "miss"
    assert by_horizon["300s"]["observation_summary"]["source_refs"][0] == "prediction/market_regime/latest_cards.json"
    calibration = result["calibration_result"]
    assert calibration["ok"] is True
    assert (tmp_path / calibration["daily_summary_json"]).exists()
    assert (tmp_path / calibration["calibration_table_json"]).exists()


def test_cp17_once_is_duplicate_safe(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    first = resolve_market_regime_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    second = resolve_market_regime_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert first["appended_outcome_count"] == 2
    assert second["appended_outcome_count"] == 0
    assert second["duplicate_outcome_count"] == 2
    part = tmp_path / "prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl"
    rows = [line for line in part.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 2


def test_cp17_preflight_skips_unexpired_horizons(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    result = build_market_regime_outcome_once_plan(hot_root=tmp_path, resolved_at="2026-07-08T12:04:00Z")
    assert result["expired_prediction_count"] == 0
    assert result["candidate_outcome_count"] == 0
    assert result["unexpired_prediction_count"] == 2
    assert result["skipped_current_count"] == 1


def test_cp17_tool_source_has_no_raw_or_execution_side_effects() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/tools/resolve_outcomes.py"
    text = path.read_text(encoding="utf-8")
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
        "raw_candles",
        "raw_orderbook",
        "raw_trades",
        "raw_executions",
    ]
    assert [token for token in forbidden if token in text] == []
    required = [
        "--preflight",
        "--once",
        "LATEST_CARDS_RELPATH",
        "write_market_regime_calibration_artifacts",
        "append_market_regime_outcome_row_once",
    ]
    assert [token for token in required if token not in text] == []
