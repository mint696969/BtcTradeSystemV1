# path: ./tools/test_prediction_system_ps_p10_confidence_caution_candidate_guard.py
# desc: Focused guard for PS-P10 PredictionCalibrationReview confidence/caution advisory candidates and missing-summary behavior.

from __future__ import annotations

import copy
import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
P9 = ROOT / "tools" / "test_prediction_system_ps_p9_calibration_review_builder_skeleton_guard.py"
P8 = ROOT / "tools" / "test_prediction_system_ps_p8_calibration_review_contract_design_guard.py"
P7 = ROOT / "tools" / "test_prediction_system_ps_p7_expected_result_matrix_metamorphic_guard.py"
P6 = ROOT / "tools" / "test_prediction_system_ps_p6_calibration_confidence_roadmap_guard.py"

NOW = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)


def _base_report() -> dict[str, Any]:
    return {
        "evaluation_report_id": "eval:ps_p10",
        "evaluation_version": "prediction_evaluation.ps_p3.v1",
        "market_uid": "BTC_JPY:bitFlyer",
        "source_ref": "ps_p10_fixture",
        "evaluation_window_start": "2026-06-19T00:00:00Z",
        "evaluation_window_end": "2026-06-19T00:05:00Z",
        "records": [{"hit_label": "correct_direction"}, {"hit_label": "wrong_direction"}],
        "evaluated_record_count": 2,
        "not_evaluable_count": 0,
        "skipped_record_count": 0,
        "confidence_summary": {
            "confidence_bucket_hit_rate": {"high": 0.9, "medium": 0.6, "low": 0.3},
            "confidence_bucket_average_return_bps": {"high": 8.0, "medium": 4.0, "low": -1.0},
            "confidence_bucket_not_evaluable_count": {"high": 0, "medium": 0, "low": 0},
        },
        "caution_summary": {
            "caution_bucket_adverse_excursion": {"low": -3.0, "medium": -6.0, "high": -10.0},
            "caution_bucket_wrong_direction_rate": {"low": 0.1, "medium": 0.3, "high": 0.6},
            "caution_bucket_not_evaluable_count": {"low": 0, "medium": 0, "high": 0},
        },
        "family_summary": {
            "directional_hit_rate_by_family": {"trend_bias": 0.75},
            "average_return_bps_by_family": {"trend_bias": 5.0},
            "adverse_excursion_bps_by_family": {"trend_bias": -5.0},
            "not_evaluable_count_by_family": {"trend_bias": 0},
        },
        "horizon_summary": {
            "directional_hit_rate_by_horizon": {"300": 0.75},
            "average_return_bps_by_horizon": {"300": 5.0},
            "adverse_excursion_bps_by_horizon": {"300": -5.0},
            "not_evaluable_count_by_horizon": {"300": 0},
        },
        "scenario_switch_summary": {
            "scenario_switch_watch_follow_through_rate": 0.5,
            "scenario_switch_watch_wrong_direction_rate": 0.2,
        },
        "refresh_required_summary": {
            "refresh_required_follow_through_rate": 0.4,
            "refresh_required_not_evaluable_count": 0,
        },
        "data_quality_notes": [],
    }


def _assert_non_behavior_change_flags(data: dict[str, Any]) -> None:
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
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False
    assert data["autotrade_decision_append_requested"] is False


def test_ps_p10_confidence_ordering_candidate_is_advisory_only_and_does_not_mutate_input() -> None:
    from btcts.prediction import build_prediction_calibration_review

    report = _base_report()
    report["confidence_summary"]["confidence_bucket_hit_rate"] = {"high": 0.25, "medium": 0.5, "low": 0.75}
    original = copy.deepcopy(report)
    data = build_prediction_calibration_review(evaluation_report=report, now=NOW).to_dict()
    assert report == original
    assert data["confidence_bucket_review"]["confidence_ordering_suspect"] is True
    assert set(data["confidence_bucket_review"]["ordering_notes"]) == {"high_below_medium", "high_below_low"}
    assert "confidence_ordering_suspect" in data["calibration_candidate_notes"]
    assert "overconfidence_review_required" in data["calibration_candidate_notes"]
    assert "overconfidence" in data["risk_catalog_hits"]
    assert "caution_bucket_not_discriminative" not in data["calibration_candidate_notes"]
    assert data["blockers"] == []
    _assert_non_behavior_change_flags(data)


def test_ps_p10_caution_not_discriminative_candidate_is_advisory_only() -> None:
    from btcts.prediction import build_prediction_calibration_review

    report = _base_report()
    report["caution_summary"]["caution_bucket_wrong_direction_rate"] = {"low": 0.4, "medium": 0.35, "high": 0.4}
    data = build_prediction_calibration_review(evaluation_report=report, now=NOW).to_dict()
    assert data["caution_bucket_review"]["caution_bucket_not_discriminative"] is True
    assert "high_not_above_low_wrong_direction_rate" in data["caution_bucket_review"]["discrimination_notes"]
    assert "medium_not_above_low_wrong_direction_rate" in data["caution_bucket_review"]["discrimination_notes"]
    assert "caution_bucket_not_discriminative" in data["calibration_candidate_notes"]
    assert "metric_mismatch" in data["risk_catalog_hits"]
    assert "confidence_ordering_suspect" not in data["calibration_candidate_notes"]
    assert data["blockers"] == []
    _assert_non_behavior_change_flags(data)


def test_ps_p10_healthy_confidence_and_caution_do_not_emit_candidates() -> None:
    from btcts.prediction import build_prediction_calibration_review

    data = build_prediction_calibration_review(evaluation_report=_base_report(), now=NOW).to_dict()
    assert data["confidence_bucket_review"]["confidence_ordering_suspect"] is False
    assert tuple(data["confidence_bucket_review"]["ordering_notes"]) == ()
    assert data["caution_bucket_review"]["caution_bucket_not_discriminative"] is False
    assert "confidence_ordering_suspect" not in data["calibration_candidate_notes"]
    assert "overconfidence_review_required" not in data["calibration_candidate_notes"]
    assert "caution_bucket_not_discriminative" not in data["calibration_candidate_notes"]
    assert "overconfidence" not in data["risk_catalog_hits"]
    assert "metric_mismatch" not in data["risk_catalog_hits"]
    assert data["warnings"] == []
    assert data["blockers"] == []
    _assert_non_behavior_change_flags(data)


def test_ps_p10_missing_summaries_warn_without_execution_or_score_change() -> None:
    from btcts.prediction import build_prediction_calibration_review

    report = _base_report()
    for key in ("confidence_summary", "caution_summary", "family_summary", "horizon_summary"):
        report.pop(key)
    data = build_prediction_calibration_review(evaluation_report=report, now=NOW).to_dict()
    assert data["blockers"] == []
    assert "confidence_summary_missing" in data["warnings"]
    assert "caution_summary_missing" in data["warnings"]
    assert "family_summary_missing" in data["warnings"]
    assert "horizon_summary_missing" in data["warnings"]
    assert "schema_drift_suspect" in data["calibration_candidate_notes"]
    assert "schema_drift" in data["risk_catalog_hits"]
    assert data["confidence_bucket_review"]["confidence_ordering_suspect"] is None
    assert data["caution_bucket_review"]["caution_bucket_not_discriminative"] is None
    assert tuple(data["family_review"]["family_underperformance_candidates"]) == ()
    assert tuple(data["horizon_review"]["horizon_underperformance_candidates"]) == ()
    _assert_non_behavior_change_flags(data)


def test_ps_p10_static_boundaries_previous_guard_anchors_and_compile() -> None:
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
        "would_change_confidence_behavior: bool = True",
        "would_change_caution_behavior: bool = True",
        "would_enable_trigger_eligibility: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in text]
    assert not hits, hits
    required = [
        "confidence_ordering_suspect",
        "overconfidence_review_required",
        "caution_bucket_not_discriminative",
        "metric_mismatch",
        "confidence_summary_missing",
        "caution_summary_missing",
        "would_change_score_formula: bool = False",
        "would_change_confidence_behavior: bool = False",
        "would_change_caution_behavior: bool = False",
        "would_enable_trigger_eligibility: bool = False",
        "autotrade_decision_append_requested: bool = False",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing
    for path in (CAL, EVAL, INIT, SYSTEM, RULE, FORECAST, P9, P8, P7, P6, Path(__file__)):
        assert path.exists(), path
        py_compile.compile(str(path), doraise=True)
    assert "test_ps_p9_advisory_notes_are_generated_without_behavior_change" in P9.read_text(encoding="utf-8")
    assert "test_ps_p8_design_doc_records_advisory_vocab_and_missing_input_behavior" in P8.read_text(encoding="utf-8")
    assert "test_ps_p7_expected_result_matrix_long_short_and_flat_outcomes" in P7.read_text(encoding="utf-8")
    assert "test_ps_p6_roadmap_doc_records_calibration_confidence_boundaries" in P6.read_text(encoding="utf-8")


def main() -> int:
    test_ps_p10_confidence_ordering_candidate_is_advisory_only_and_does_not_mutate_input()
    test_ps_p10_caution_not_discriminative_candidate_is_advisory_only()
    test_ps_p10_healthy_confidence_and_caution_do_not_emit_candidates()
    test_ps_p10_missing_summaries_warn_without_execution_or_score_change()
    test_ps_p10_static_boundaries_previous_guard_anchors_and_compile()
    print("[OK] Prediction System PS-P10 confidence/caution candidate guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
