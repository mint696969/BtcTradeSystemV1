# path: ./tools/test_prediction_system_ps_p11_evaluation_calibration_cc_pass_guard.py
# desc: Guard for PS-P11 evaluation/calibration whole-surface CC pass report and boundaries.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P11_EVALUATION_CALIBRATION_CC_PASS_2026-06-19.md"
EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"
CAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "calibration_review.py"
INIT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "__init__.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
P10 = ROOT / "tools" / "test_prediction_system_ps_p10_confidence_caution_candidate_guard.py"
P9 = ROOT / "tools" / "test_prediction_system_ps_p9_calibration_review_builder_skeleton_guard.py"
P8 = ROOT / "tools" / "test_prediction_system_ps_p8_calibration_review_contract_design_guard.py"
P7 = ROOT / "tools" / "test_prediction_system_ps_p7_expected_result_matrix_metamorphic_guard.py"
P6 = ROOT / "tools" / "test_prediction_system_ps_p6_calibration_confidence_roadmap_guard.py"


def test_ps_p11_cc_report_records_findings_and_no_change_decision() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P11_EVALUATION_CALIBRATION_CC_PASS_2026-06-19.md",
        "PS-P11 is a whole-surface code-check pass",
        "No production code changes are required in PS-P11.",
        "✅ OK: evaluation contract remains offline/replay-only",
        "✅ OK: evaluation summary keys align with PS-P2 / PS-P5 contract",
        "✅ OK: calibration review is standalone and advisory-only",
        "✅ OK: public exports are present and localized",
        "✅ OK: confidence/caution candidate checks are advisory, not behavioral",
        "⚠️ Risk: nested review tuple/list representation is intentionally not normalized",
        "⚠️ Risk: calibration review thresholds are skeleton heuristics",
        "✅ OK: hard boundaries remain intact",
        "No score formula changes.",
        "No confidence behavior changes.",
        "No caution behavior changes.",
        "No family label changes.",
        "No TriggerEligibility changes.",
        "PS-P12: stop/review checkpoint before any production calibration behavior change.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p11_evaluation_and_calibration_contract_anchors() -> None:
    eval_text = EVAL.read_text(encoding="utf-8")
    cal_text = CAL.read_text(encoding="utf-8")
    init_text = INIT.read_text(encoding="utf-8")
    eval_required = [
        "class PredictionEvaluationRecord",
        "class PredictionEvaluationReport",
        "def build_prediction_evaluation_report",
        "confidence_bucket_hit_rate",
        "confidence_bucket_average_return_bps",
        "confidence_bucket_not_evaluable_count",
        "caution_bucket_adverse_excursion",
        "caution_bucket_wrong_direction_rate",
        "caution_bucket_not_evaluable_count",
        "would_write_runtime_artifact: bool = False",
        "autotrade_decision_append_requested: bool = False",
    ]
    cal_required = [
        "class PredictionCalibrationReview",
        "def build_prediction_calibration_review",
        "PredictionEvaluationReport | Mapping[str, Any] | None",
        "calibration_review_in_memory_only",
        "confidence_ordering_suspect",
        "caution_bucket_not_discriminative",
        "evaluation_report_missing",
        "confidence_summary_missing",
        "caution_summary_missing",
        "would_change_score_formula: bool = False",
        "would_change_confidence_behavior: bool = False",
        "would_change_caution_behavior: bool = False",
        "would_change_family_labels: bool = False",
        "would_enable_trigger_eligibility: bool = False",
        "would_write_runtime_artifact: bool = False",
        "autotrade_decision_append_requested: bool = False",
    ]
    init_required = [
        "from .calibration_review import PredictionCalibrationReview, build_prediction_calibration_review",
        '"PredictionCalibrationReview"',
        '"build_prediction_calibration_review"',
    ]
    missing = [item for item in eval_required if item not in eval_text]
    missing += [item for item in cal_required if item not in cal_text]
    missing += [item for item in init_required if item not in init_text]
    assert not missing, missing


def test_ps_p11_static_boundaries_still_hold() -> None:
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


def test_ps_p11_previous_guard_anchors_present_and_compile() -> None:
    for path in (P10, P9, P8, P7, P6):
        assert path.exists(), path
    assert "test_ps_p10_confidence_ordering_candidate_is_advisory_only_and_does_not_mutate_input" in P10.read_text(encoding="utf-8")
    assert "test_ps_p9_advisory_notes_are_generated_without_behavior_change" in P9.read_text(encoding="utf-8")
    assert "test_ps_p8_design_doc_records_calibration_review_contract_shape" in P8.read_text(encoding="utf-8")
    assert "test_ps_p7_expected_result_matrix_long_short_and_flat_outcomes" in P7.read_text(encoding="utf-8")
    assert "test_ps_p6_roadmap_doc_records_calibration_confidence_boundaries" in P6.read_text(encoding="utf-8")
    for path in (EVAL, CAL, INIT, SYSTEM, RULE, FORECAST, P10, P9, P8, P7, P6, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_p11_cc_report_records_findings_and_no_change_decision()
    test_ps_p11_evaluation_and_calibration_contract_anchors()
    test_ps_p11_static_boundaries_still_hold()
    test_ps_p11_previous_guard_anchors_present_and_compile()
    print("[OK] Prediction System PS-P11 evaluation/calibration CC pass guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
