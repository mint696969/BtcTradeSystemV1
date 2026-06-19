# path: ./tools/test_prediction_system_ps_p9_calibration_review_builder_skeleton_guard.py
# desc: Guard for PS-P9 in-memory PredictionCalibrationReview builder skeleton.

from __future__ import annotations

import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

CAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "calibration_review.py"
EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"
INIT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "__init__.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
P8 = ROOT / "tools" / "test_prediction_system_ps_p8_calibration_review_contract_design_guard.py"
P7 = ROOT / "tools" / "test_prediction_system_ps_p7_expected_result_matrix_metamorphic_guard.py"
P6 = ROOT / "tools" / "test_prediction_system_ps_p6_calibration_confidence_roadmap_guard.py"

NOW = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)


def _record(record_id: str, label: str, confidence: str) -> dict[str, object]:
    return {
        "record_id": record_id,
        "bundle_id": "bundle:ps_p9",
        "generated_at": "2026-06-19T00:00:00Z",
        "prediction_id": f"prediction:{record_id}",
        "family": "trend_bias",
        "horizon_sec": 300,
        "horizon_label": "5m",
        "horizon_key": "5m",
        "primary_label": label,
        "confidence": confidence,
        "score": 0.5,
        "values_snapshot": {"trigger_eligibility_state": "blocked", "caution_level": "low"},
        "blockers": [],
        "warnings": [],
    }


def _outcome(end_price: float) -> dict[str, object]:
    return {
        "family": "trend_bias",
        "horizon_sec": 300,
        "evaluation_window_start": "2026-06-19T00:00:00Z",
        "evaluation_window_end": "2026-06-19T00:05:00Z",
        "start_price": 10_000_000,
        "end_price": end_price,
        "min_price": min(10_000_000, end_price),
        "max_price": max(10_000_000, end_price),
        "source_ref": "offline_replay_fixture",
    }


def test_ps_p9_static_boundaries_and_exports() -> None:
    assert CAL.exists(), CAL
    text = "\n".join(path.read_text(encoding="utf-8") for path in (CAL, EVAL, INIT, SYSTEM, RULE, FORECAST))
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
        "would_enable_trigger_eligibility: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in text]
    assert not hits, hits
    required = [
        "class PredictionCalibrationReview",
        "def build_prediction_calibration_review",
        "prediction_calibration_review.ps_p9.v1",
        "PredictionEvaluationReport",
        "calibration_review_in_memory_only",
        "would_change_score_formula: bool = False",
        "would_change_confidence_behavior: bool = False",
        "would_change_caution_behavior: bool = False",
        "would_change_family_labels: bool = False",
        "would_enable_trigger_eligibility: bool = False",
        "would_write_runtime_artifact: bool = False",
        "command_ledger_append_requested: bool = False",
        "autotrade_decision_append_requested: bool = False",
        "PredictionCalibrationReview",
        "build_prediction_calibration_review",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p9_builds_read_only_review_from_evaluation_report() -> None:
    from btcts.prediction import build_prediction_calibration_review, build_prediction_evaluation_report

    evaluation = build_prediction_evaluation_report(
        forecast_batch={"records": [_record("high", "long_bias", "high"), _record("low", "long_bias", "low")]},
        outcome_windows={"trend_bias:300": _outcome(10_010_000)},
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:ps_p9"}},
        now=NOW,
        source_ref="ps_p9_eval_fixture",
    )
    review = build_prediction_calibration_review(evaluation_report=evaluation, now=NOW)
    data = review.to_dict()
    assert data["logic_version"] == "prediction_calibration_review.ps_p9.v1"
    assert data["source_evaluation_report_id"] == evaluation.evaluation_report_id
    assert data["source_evaluation_version"] == evaluation.evaluation_version
    assert data["market_uid"] == evaluation.market_uid
    assert data["evaluated_record_count"] == 2
    assert data["not_evaluable_count"] == 0
    assert data["confidence_bucket_review"]["bucket_hit_rate"]["high"] == 1.0
    assert data["family_review"]["directional_hit_rate_by_family"]["trend_bias"] == 1.0
    assert "calibration_review_in_memory_only" in data["calibration_candidate_notes"]
    assert data["blockers"] == []
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_change_score_formula"] is False
    assert data["would_change_confidence_behavior"] is False
    assert data["would_change_caution_behavior"] is False
    assert data["would_change_family_labels"] is False
    assert data["would_enable_trigger_eligibility"] is False
    assert data["would_collect_public_source"] is False
    assert data["would_write_runtime_artifact"] is False
    assert data["would_send_to_broker"] is False
    assert data["command_ledger_append_requested"] is False
    assert data["autotrade_decision_append_requested"] is False


def test_ps_p9_missing_evaluation_report_is_blocked_and_non_executing() -> None:
    from btcts.prediction import build_prediction_calibration_review

    review = build_prediction_calibration_review(evaluation_report=None, now=NOW)
    data = review.to_dict()
    assert "evaluation_report_missing" in data["blockers"]
    assert "evaluation_report_missing" in data["calibration_candidate_notes"]
    assert data["source_evaluation_report_id"] is None
    assert data["evaluated_record_count"] == 0
    assert data["not_evaluable_count"] == 0
    assert data["usable"] is False
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_change_score_formula"] is False
    assert data["would_enable_trigger_eligibility"] is False
    assert data["would_send_to_broker"] is False
    assert data["autotrade_decision_append_requested"] is False


def test_ps_p9_advisory_notes_are_generated_without_behavior_change() -> None:
    from btcts.prediction import build_prediction_calibration_review

    report = {
        "evaluation_report_id": "eval:advisory",
        "evaluation_version": "prediction_evaluation.fixture",
        "market_uid": "BTC_JPY:bitFlyer",
        "source_ref": "fixture",
        "evaluation_window_start": "2026-06-19T00:00:00Z",
        "evaluation_window_end": "2026-06-19T00:05:00Z",
        "records": [{"hit_label": "not_evaluable", "not_evaluable_reason": "outcome_window_missing"}],
        "evaluated_record_count": 0,
        "not_evaluable_count": 1,
        "skipped_record_count": 0,
        "confidence_summary": {
            "confidence_bucket_hit_rate": {"high": 0.25, "low": 0.75},
            "confidence_bucket_average_return_bps": {"high": -5.0, "low": 3.0},
            "confidence_bucket_not_evaluable_count": {"high": 0, "low": 0},
        },
        "caution_summary": {
            "caution_bucket_adverse_excursion": {"low": -10.0, "high": -5.0},
            "caution_bucket_wrong_direction_rate": {"low": 0.5, "high": 0.4},
            "caution_bucket_not_evaluable_count": {"low": 0, "high": 0},
        },
        "family_summary": {"directional_hit_rate_by_family": {"trend_bias": 0.25}},
        "horizon_summary": {"directional_hit_rate_by_horizon": {"300": 0.25}},
        "scenario_switch_summary": {"scenario_switch_watch_follow_through_rate": None, "scenario_switch_watch_wrong_direction_rate": None},
        "refresh_required_summary": {"refresh_required_follow_through_rate": None, "refresh_required_not_evaluable_count": 1},
        "data_quality_notes": ["outcome_window_missing"],
    }
    data = build_prediction_calibration_review(evaluation_report=report, now=NOW).to_dict()
    assert "confidence_ordering_suspect" in data["calibration_candidate_notes"]
    assert "overconfidence_review_required" in data["calibration_candidate_notes"]
    assert "caution_bucket_not_discriminative" in data["calibration_candidate_notes"]
    assert "family_underperformance_candidate" in data["calibration_candidate_notes"]
    assert "horizon_underperformance_candidate" in data["calibration_candidate_notes"]
    assert "not_evaluable_skew" in data["calibration_candidate_notes"]
    assert "missing_outcome_skew" in data["calibration_candidate_notes"]
    assert "scenario_switch_review_not_ready" in data["calibration_candidate_notes"]
    assert "refresh_required_review_not_ready" in data["calibration_candidate_notes"]
    assert "overconfidence" in data["risk_catalog_hits"]
    assert "aggregation_hiding" in data["risk_catalog_hits"]
    assert data["confidence_bucket_review"]["confidence_ordering_suspect"] is True
    assert data["caution_bucket_review"]["caution_bucket_not_discriminative"] is True
    assert data["data_quality_review"]["not_evaluable_skew"] is True
    assert data["would_change_score_formula"] is False
    assert data["would_change_confidence_behavior"] is False
    assert data["would_change_caution_behavior"] is False
    assert data["would_enable_trigger_eligibility"] is False


def test_ps_p9_previous_guard_anchors_and_compile() -> None:
    for path in (CAL, EVAL, INIT, SYSTEM, RULE, FORECAST, P8, P7, P6, Path(__file__)):
        assert path.exists(), path
        py_compile.compile(str(path), doraise=True)
    assert "test_ps_p8_design_doc_records_calibration_review_contract_shape" in P8.read_text(encoding="utf-8")
    assert "test_ps_p7_expected_result_matrix_long_short_and_flat_outcomes" in P7.read_text(encoding="utf-8")
    assert "test_ps_p6_roadmap_doc_records_calibration_confidence_boundaries" in P6.read_text(encoding="utf-8")


def main() -> int:
    test_ps_p9_static_boundaries_and_exports()
    test_ps_p9_builds_read_only_review_from_evaluation_report()
    test_ps_p9_missing_evaluation_report_is_blocked_and_non_executing()
    test_ps_p9_advisory_notes_are_generated_without_behavior_change()
    test_ps_p9_previous_guard_anchors_and_compile()
    print("[OK] Prediction System PS-P9 calibration review builder skeleton guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
