# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_trace_ledger_outcomes_cp18.py
# desc: CP18 tests for resolving historical market-regime trace ledger predictions into outcomes. Artifact-only; no raw market reads, scheduler, broker, AutoTrade, or parameter auto-promotion.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.tools.resolve_outcomes import (  # noqa: E402
    build_market_regime_trace_outcome_once_plan,
    resolve_market_regime_trace_outcomes_once,
)


def _write_latest_cards(root: Path) -> None:
    path = root / "prediction/market_regime/latest_cards.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_kind": "latest_cards",
        "run_id": "latest_current_run",
        "generated_at": "2026-07-08T12:20:00Z",
        "cards": [
            {"horizon": "現在", "horizon_key": "current", "horizon_sec": 0, "regime_code": "RANGE", "confidence_percent": 70, "detail": {"trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"}},
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _trace_row(run_id: str, generated_at: str) -> dict:
    return {
        "artifact_kind": "trace_row",
        "prediction_family_id": "market_regime",
        "run_id": run_id,
        "generated_at": generated_at,
        "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl",
        "active_parameter_set_id": "market_regime_engine_parameter_set.v1",
        "prediction_summary": {
            "generated_at": generated_at,
            "horizons": [
                {"horizon": "現在", "horizon_key": "current", "horizon_sec": 0, "regime_code": "RANGE", "confidence_percent": 70, "evidence_quality": "PARTIAL", "freshness_state": "LIVE", "parameter_set_id": "market_regime_engine_parameter_set.v1"},
                {"horizon": "5分後", "horizon_key": "300s", "horizon_sec": 300, "regime_code": "RANGE", "confidence_percent": 70, "evidence_quality": "PARTIAL", "freshness_state": "LIVE", "parameter_set_id": "market_regime_engine_parameter_set.v1"},
                {"horizon": "15分後", "horizon_key": "900s", "horizon_sec": 900, "regime_code": "UP_TREND", "confidence_percent": 80, "evidence_quality": "PARTIAL", "freshness_state": "LIVE", "parameter_set_id": "market_regime_engine_parameter_set.v1"},
            ],
        },
        "safety": {"raw_market_data_duplicated": False, "broker_private_api_allowed": False, "autotrade_trigger_allowed": False, "would_send_to_broker": False},
    }


def _write_trace(root: Path) -> None:
    part = root / "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"
    part.parent.mkdir(parents=True, exist_ok=True)
    part.write_text(json.dumps(_trace_row("trace_run_1", "2026-07-08T12:00:00Z"), ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def test_cp18_trace_ledger_preflight_finds_expired_historical_predictions(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    _write_trace(tmp_path)
    result = build_market_regime_trace_outcome_once_plan(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert result["source"] == "trace_ledger"
    assert result["trace_row_count"] == 1
    assert result["trace_prediction_count"] == 2
    assert result["skipped_current_count"] == 1
    assert result["expired_prediction_count"] == 2
    assert result["candidate_outcome_count"] == 2
    assert result["observed_regime_code"] == "RANGE"
    assert result["would_write"] is False


def test_cp18_trace_ledger_once_appends_outcomes_and_calibration(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    _write_trace(tmp_path)
    result = resolve_market_regime_trace_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert result["ok"] is True
    assert result["source"] == "trace_ledger"
    assert result["appended_outcome_count"] == 2
    part = tmp_path / "prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl"
    rows = [json.loads(line) for line in part.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_horizon = {row["horizon_key"]: row for row in rows}
    assert by_horizon["300s"]["outcome_label"] == "hit"
    assert by_horizon["900s"]["outcome_label"] == "miss"
    assert result["calibration_results"][0]["ok"] is True


def test_cp18_trace_ledger_once_is_duplicate_safe(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    _write_trace(tmp_path)
    first = resolve_market_regime_trace_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    second = resolve_market_regime_trace_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert first["appended_outcome_count"] == 2
    assert second["appended_outcome_count"] == 0
    assert second["duplicate_outcome_count"] == 2






def test_cp18_trace_ledger_max_rows_prefers_latest_trace_rows(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    old_part = tmp_path / "prediction/market_regime/ledgers/date=2026-07-08/hour=11/part-00001.jsonl"
    new_part = tmp_path / "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"
    old_part.parent.mkdir(parents=True, exist_ok=True)
    new_part.parent.mkdir(parents=True, exist_ok=True)
    old_part.write_text(json.dumps(_trace_row("trace_run_old", "2026-07-08T11:00:00Z"), ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    new_part.write_text(json.dumps(_trace_row("trace_run_new", "2026-07-08T12:00:00Z"), ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    result = build_market_regime_trace_outcome_once_plan(
        hot_root=tmp_path,
        resolved_at="2026-07-08T12:20:00Z",
        max_trace_rows=1,
    )

    assert result["trace_row_count"] == 1
    assert result["trace_prediction_count"] == 2
    assert {row["run_id"] for row in result["candidate_rows"]} == {"trace_run_new"}


def test_cp18_trace_outcome_identity_keeps_parameter_sets_distinct(tmp_path: Path) -> None:
    _write_latest_cards(tmp_path)
    part = tmp_path / "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl"
    part.parent.mkdir(parents=True, exist_ok=True)

    def row(parameter_set_id: str, regime: str) -> dict:
        return {
            "artifact_kind": "trace_row",
            "prediction_family_id": "market_regime",
            "run_id": "trace_run_compare",
            "generated_at": "2026-07-08T12:00:00Z",
            "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl",
            "active_parameter_set_id": parameter_set_id,
            "prediction_summary": {
                "generated_at": "2026-07-08T12:00:00Z",
                "horizons": [
                    {"horizon": "現在", "horizon_key": "current", "horizon_sec": 0, "regime_code": regime, "confidence_percent": 70, "evidence_quality": "PARTIAL", "freshness_state": "LIVE", "parameter_set_id": parameter_set_id},
                    {"horizon": "5分後", "horizon_key": "300s", "horizon_sec": 300, "regime_code": regime, "confidence_percent": 70, "evidence_quality": "PARTIAL", "freshness_state": "LIVE", "parameter_set_id": parameter_set_id},
                ],
            },
            "safety": {"raw_market_data_duplicated": False, "broker_private_api_allowed": False, "autotrade_trigger_allowed": False, "would_send_to_broker": False},
        }

    rows = [
        row("market_regime_engine_parameter_set.v1", "RANGE"),
        row("market_regime_engine_parameter_set.shadow", "UP_TREND"),
    ]
    part.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in rows), encoding="utf-8")

    preflight = build_market_regime_trace_outcome_once_plan(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert preflight["candidate_outcome_count"] == 2
    outcome_ids = [row["outcome_id"] for row in preflight["candidate_rows"]]
    assert len(set(outcome_ids)) == 2
    assert all(":300s:market_regime_engine_parameter_set." in outcome_id for outcome_id in outcome_ids)
    assert {row["parameter_set_id"] for row in preflight["candidate_rows"]} == {"market_regime_engine_parameter_set.v1", "market_regime_engine_parameter_set.shadow"}

    first = resolve_market_regime_trace_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    second = resolve_market_regime_trace_outcomes_once(hot_root=tmp_path, resolved_at="2026-07-08T12:20:00Z")
    assert first["appended_outcome_count"] == 2
    assert second["appended_outcome_count"] == 0
    assert second["duplicate_outcome_count"] == 2


def test_cp18_trace_ledger_tool_source_is_artifact_only() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/tools/resolve_outcomes.py"
    text = path.read_text(encoding="utf-8")
    required = [
        "--source",
        "trace_ledger",
        "build_market_regime_trace_outcome_once_plan",
        "resolve_market_regime_trace_outcomes_once",
        "prediction/market_regime/ledgers",
        "reverse=True",
        "for raw in reversed(raw_lines)",
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
