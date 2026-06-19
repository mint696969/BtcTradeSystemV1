# path: ./tools/test_prediction_system_ps_p6_calibration_confidence_roadmap_guard.py
# desc: Guard for PS-P6 no-code calibration/confidence roadmap using Prediction System evaluation outputs only.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P6_CALIBRATION_CONFIDENCE_ROADMAP_2026-06-19.md"
EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
P5 = ROOT / "tools" / "test_prediction_system_ps_p5_evaluation_report_summary_guard.py"
P4 = ROOT / "tools" / "test_prediction_system_ps_p4_evaluation_not_evaluable_guard.py"
P3 = ROOT / "tools" / "test_prediction_system_ps_p3_evaluation_builder_skeleton_guard.py"
P2 = ROOT / "tools" / "test_prediction_system_ps_p2_evaluation_contract_design_guard.py"


def test_ps_p6_roadmap_doc_records_calibration_confidence_boundaries() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P6_CALIBRATION_CONFIDENCE_ROADMAP_2026-06-19.md",
        "PS-P6 is a no-code roadmap slice for future calibration and confidence review",
        "Evaluation outputs are evidence, not authority.",
        "Do not directly feed evaluation results into AutoTrade.",
        "Do not enable TriggerEligibility from calibration output.",
        "No score formula changes in PS-P6.",
        "No confidence behavior changes in PS-P6.",
        "No caution behavior changes in PS-P6.",
        "No rule_based_v0 label changes in PS-P6.",
        "Expected-result matrix for future guards",
        "case: long_bias + price up",
        "case: short_bias + price down",
        "case: missing outcome",
        "case: invalid price",
        "case: trigger_eligibility_state not blocked",
        "Metamorphic checks to add before calibration implementation",
        "Price scale invariance",
        "Outcome removal",
        "Execution invariance",
        "Risk catalog for Prediction System evaluation and calibration",
        "schema_drift",
        "silent_fallback",
        "lookahead_bias",
        "overconfidence",
        "missing_data_optimism",
        "aggregation_hiding",
        "PredictionCalibrationReview:",
        "would_change_score_formula = False",
        "would_change_confidence_behavior = False",
        "would_change_caution_behavior = False",
        "would_enable_trigger_eligibility = False",
        "PS-P7: expected-result matrix / metamorphic guard extension for evaluation outputs.",
        "Use D:\\btc_ts_hot only for latest/runtime/current state checks when explicitly needed.",
        "Use E:\\btc_ts only for cold/archive/copy validation or long-term retained replay datasets.",
        "No production code changed.",
        "This roadmap is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p6_evaluation_summary_contract_anchors_still_present() -> None:
    text = EVAL.read_text(encoding="utf-8")
    required = [
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
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p6_static_boundaries_still_hold() -> None:
    production_text = "\n".join(path.read_text(encoding="utf-8") for path in (EVAL, SYSTEM, RULE, FORECAST))
    forbidden = [
        "btcts.autotrade",
        "btcts.collector_vnext",
        "append_decision_jsonl",
        "send_order",
        "place_order",
        "private_api",
        "requests.get",
        "urllib.request",
        "would_apply_mode: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in production_text]
    assert not hits, hits
    required_markers = [
        "build_prediction_system_result",
        "trigger_eligibility_state=\"blocked\"",
        "PredictionEvaluationReport",
        "ForecastLedgerRecord",
        "would_append_ledger: bool = False",
    ]
    missing = [item for item in required_markers if item not in production_text]
    assert not missing, missing


def test_ps_p6_previous_guard_anchors_present_and_compile() -> None:
    for path in (P5, P4, P3, P2):
        assert path.exists(), path
    assert "test_ps_p5_summary_keys_match_ps_p2_design" in P5.read_text(encoding="utf-8")
    assert "test_ps_p4_invalid_outcome_prices_are_not_evaluable" in P4.read_text(encoding="utf-8")
    assert "test_ps_p3_builds_in_memory_evaluation_report_with_outcome" in P3.read_text(encoding="utf-8")
    assert "test_ps_p2_design_doc_records_evaluation_contract_shapes" in P2.read_text(encoding="utf-8")
    for path in (EVAL, SYSTEM, RULE, FORECAST, P5, P4, P3, P2, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_p6_roadmap_doc_records_calibration_confidence_boundaries()
    test_ps_p6_evaluation_summary_contract_anchors_still_present()
    test_ps_p6_static_boundaries_still_hold()
    test_ps_p6_previous_guard_anchors_present_and_compile()
    print("[OK] Prediction System PS-P6 calibration / confidence roadmap guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
