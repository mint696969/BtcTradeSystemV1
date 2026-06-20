# path: ./tools/test_prediction_system_ps_q1b_replay_data_quality_guard.py
# desc: Guard for PS-Q1B read-only replay/evaluation data quality baseline. No production behavior changes.

from __future__ import annotations

import copy
import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BTCTS_SRC = ROOT / "btcts_next" / "src"
if str(BTCTS_SRC) not in sys.path:
    sys.path.insert(0, str(BTCTS_SRC))

from btcts.prediction.calibration_review import build_prediction_calibration_review
from btcts.prediction.evaluation import build_prediction_evaluation_report

DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_Q1B_REPLAY_DATA_QUALITY_GUARD_2026-06-19.md"
Q1_DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_Q1_FULL_REMAINING_IMPLEMENTATION_ROADMAP_2026-06-19.md"
P12_DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P12_STOP_REVIEW_CHECKPOINT_2026-06-19.md"
EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"
CAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "calibration_review.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
Q1_GUARD = ROOT / "tools" / "test_prediction_system_ps_q1_full_remaining_implementation_roadmap_guard.py"
P12_GUARD = ROOT / "tools" / "test_prediction_system_ps_p12_stop_review_checkpoint_guard.py"
P11_GUARD = ROOT / "tools" / "test_prediction_system_ps_p11_evaluation_calibration_cc_pass_guard.py"

NOW = datetime(2026, 6, 19, 0, 0, tzinfo=timezone.utc)


def _prediction_snapshot() -> dict[str, object]:
    return {
        "run_identity": {
            "prediction_run_id": "ps_q1b_replay_quality_fixture",
            "generated_at": "2026-06-19T00:00:00Z",
            "market_uid": "BTC_JPY:bitFlyer",
        },
        "system_input": {"market_uid": "BTC_JPY:bitFlyer"},
    }


def _forecast_records() -> list[dict[str, object]]:
    return [
        {
            "record_id": "ps_q1b_eval_available_trend_300",
            "family": "trend_bias",
            "horizon_sec": 300,
            "horizon_label": "5m",
            "horizon_key": "5m",
            "primary_label": "long_bias",
            "score": 0.72,
            "confidence": "high",
            "values_snapshot": {
                "caution_level": "low",
                "trigger_eligibility_state": "blocked",
                "refresh_required": False,
            },
        },
        {
            "record_id": "ps_q1b_missing_breakout_600",
            "family": "breakout_false_break",
            "horizon_sec": 600,
            "horizon_label": "10m",
            "horizon_key": "10m",
            "primary_label": "breakout_candidate",
            "score": 0.61,
            "confidence": "medium",
            "values_snapshot": {
                "caution_level": "high",
                "trigger_eligibility_state": "blocked",
                "refresh_required": True,
            },
        },
        {
            "record_id": "ps_q1b_missing_liquidity_900",
            "family": "liquidity_execution_quality",
            "horizon_sec": 900,
            "horizon_label": "15m",
            "horizon_key": "15m",
            "primary_label": "no_edge",
            "score": 0.2,
            "confidence": "low",
            "values_snapshot": {
                "caution_level": "medium",
                "trigger_eligibility_state": "blocked",
                "refresh_required": False,
            },
        },
    ]


def _outcome_windows() -> dict[str, dict[str, object]]:
    return {
        "ps_q1b_eval_available_trend_300": {
            "record_id": "ps_q1b_eval_available_trend_300",
            "family": "trend_bias",
            "horizon_sec": 300,
            "start_price": 10_000_000,
            "end_price": 10_020_000,
            "min_price": 9_995_000,
            "max_price": 10_030_000,
            "window_start": "2026-06-19T00:00:00Z",
            "window_end": "2026-06-19T00:05:00Z",
            "outcome_source_ref": "ps_q1b_fixture_outcome",
        }
    }


def _report():
    return build_prediction_evaluation_report(
        forecast_batch=_forecast_records(),
        outcome_windows=_outcome_windows(),
        prediction_snapshot=_prediction_snapshot(),
        now=NOW,
        source_ref="ps_q1b_replay_quality_fixture",
    )


def _assert_safety_flags_false(data: dict[str, object]) -> None:
    assert data["read_only"] is True
    assert data["non_executing"] is True
    for key in (
        "would_collect_public_source",
        "would_write_runtime_artifact",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "autotrade_decision_append_requested",
    ):
        assert data[key] is False, key
    for key in (
        "would_change_score_formula",
        "would_change_confidence_behavior",
        "would_change_caution_behavior",
        "would_change_family_labels",
        "would_enable_trigger_eligibility",
    ):
        if key in data:
            assert data[key] is False, key


def _compile_without_repo_pycache(path: Path) -> None:
    cache_dir = ROOT / "tmp" / "py_compile_cache" / path.parent.relative_to(ROOT)
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_name = path.name.replace(".", "_") + ".pyc"
    py_compile.compile(str(path), cfile=str(cache_dir / safe_name), doraise=True)


def test_ps_q1b_doc_records_option_b_completion_boundary() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "Option B: read-only replay-data quality guard only.",
        "Option B is considered complete in this thread when a committed guard verifies",
        "PredictionEvaluationReport preserves not_evaluable evidence by family.",
        "PredictionEvaluationReport preserves not_evaluable evidence by horizon.",
        "PredictionEvaluationReport preserves not_evaluable evidence by confidence bucket.",
        "PredictionEvaluationReport preserves not_evaluable evidence by caution bucket.",
        "PredictionCalibrationReview turns not_evaluable skew into advisory data-quality risk.",
        "PredictionCalibrationReview turns missing outcome skew into advisory data-quality risk.",
        "It does not mean production calibration is enabled.",
        "Next thread remains:",
        "PS-Q2: source / artifact input coverage start",
        "No production code changed.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_q1b_evaluation_preserves_replay_data_quality_skew_axes() -> None:
    report = _report()
    data = report.to_dict()

    assert data["input_forecast_record_count"] == 3
    assert data["evaluated_record_count"] == 1
    assert data["not_evaluable_count"] == 2
    assert data["data_quality_notes"] == ["outcome_window_missing"]
    assert "evaluation_records_with_missing_outcome_window" in data["warnings"]

    family_missing = data["family_summary"]["not_evaluable_count_by_family"]
    assert family_missing["trend_bias"] == 0
    assert family_missing["breakout_false_break"] == 1
    assert family_missing["liquidity_execution_quality"] == 1

    horizon_missing = data["horizon_summary"]["not_evaluable_count_by_horizon"]
    assert horizon_missing["300"] == 0
    assert horizon_missing["600"] == 1
    assert horizon_missing["900"] == 1

    confidence_missing = data["confidence_summary"]["confidence_bucket_not_evaluable_count"]
    assert confidence_missing["high"] == 0
    assert confidence_missing["medium"] == 1
    assert confidence_missing["low"] == 1

    caution_missing = data["caution_summary"]["caution_bucket_not_evaluable_count"]
    assert caution_missing["low"] == 0
    assert caution_missing["high"] == 1
    assert caution_missing["medium"] == 1

    _assert_safety_flags_false(data)
    for record in data["records"]:
        _assert_safety_flags_false(record)
        assert record["predicted_trigger_eligibility_state"] == "blocked"


def test_ps_q1b_calibration_review_marks_data_quality_risks_as_advisory_only() -> None:
    review = build_prediction_calibration_review(evaluation_report=_report(), now=NOW)
    data = review.to_dict()

    dq = data["data_quality_review"]
    assert dq["not_evaluable_count"] == 2
    assert dq["record_count"] == 3
    assert dq["not_evaluable_ratio"] == 0.666667
    assert dq["not_evaluable_skew"] is True
    assert dq["missing_outcome_skew"] is True
    assert tuple(dq["data_quality_notes"]) == ("outcome_window_missing",)

    assert "not_evaluable_skew" in data["risk_catalog_hits"]
    assert "missing_data_optimism" in data["risk_catalog_hits"]
    assert "not_evaluable_skew" in data["calibration_candidate_notes"]
    assert "missing_outcome_skew" in data["calibration_candidate_notes"]
    assert data["blockers"] == []
    _assert_safety_flags_false(data)


def test_ps_q1b_schema_drift_and_missing_summaries_are_advisory_only_and_do_not_mutate_input() -> None:
    report_data = _report().to_dict()
    for key in ("confidence_summary", "caution_summary", "family_summary", "horizon_summary"):
        report_data[key] = {}
    before = copy.deepcopy(report_data)

    review = build_prediction_calibration_review(evaluation_report=report_data, now=NOW)
    data = review.to_dict()

    assert report_data == before
    assert "confidence_summary_missing" in data["warnings"]
    assert "caution_summary_missing" in data["warnings"]
    assert "family_summary_missing" in data["warnings"]
    assert "horizon_summary_missing" in data["warnings"]
    assert "schema_drift" in data["risk_catalog_hits"]
    assert "schema_drift_suspect" in data["calibration_candidate_notes"]
    assert data["blockers"] == []
    _assert_safety_flags_false(data)


def test_ps_q1b_previous_anchors_static_boundaries_and_compile() -> None:
    for path in (Q1_DOC, P12_DOC, Q1_GUARD, P12_GUARD, P11_GUARD, EVAL, CAL, SYSTEM, RULE, FORECAST):
        assert path.exists(), path
    assert "PS-Q6: replay-data quality guard / evidence quality gate" in Q1_DOC.read_text(encoding="utf-8")
    assert "Option B: continue with replay-data quality guards only" in P12_DOC.read_text(encoding="utf-8")
    assert "test_ps_q1_doc_lists_remaining_work_packages_and_next_start" in Q1_GUARD.read_text(encoding="utf-8")
    assert "test_ps_p12_checkpoint_doc_records_stop_review_decision" in P12_GUARD.read_text(encoding="utf-8")

    reviewed_text = "\n".join(path.read_text(encoding="utf-8") for path in (EVAL, CAL, SYSTEM, RULE, FORECAST))
    forbidden = [
        "btcts.autotrade",
        "btcts.collector_vnext",
        "append_decision_jsonl",
        "send_order",
        "place_order",
        "private_api",
        "requests.get",
        "urllib.request",
        "would_change_score_formula: bool = True",
        "would_change_confidence_behavior: bool = True",
        "would_change_caution_behavior: bool = True",
        "would_enable_trigger_eligibility: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in reviewed_text]
    assert not hits, hits

    for path in (EVAL, CAL, SYSTEM, RULE, FORECAST, Q1_GUARD, P12_GUARD, P11_GUARD, Path(__file__)):
        _compile_without_repo_pycache(path)


def main() -> int:
    test_ps_q1b_doc_records_option_b_completion_boundary()
    test_ps_q1b_evaluation_preserves_replay_data_quality_skew_axes()
    test_ps_q1b_calibration_review_marks_data_quality_risks_as_advisory_only()
    test_ps_q1b_schema_drift_and_missing_summaries_are_advisory_only_and_do_not_mutate_input()
    test_ps_q1b_previous_anchors_static_boundaries_and_compile()
    print("[OK] Prediction System PS-Q1B replay-data quality guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
