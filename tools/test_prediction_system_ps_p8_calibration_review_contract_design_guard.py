# path: ./tools/test_prediction_system_ps_p8_calibration_review_contract_design_guard.py
# desc: Guard for PS-P8 no-code PredictionCalibrationReview contract design.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P8_CALIBRATION_REVIEW_CONTRACT_DESIGN_2026-06-19.md"
P6_DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P6_CALIBRATION_CONFIDENCE_ROADMAP_2026-06-19.md"
EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
P7 = ROOT / "tools" / "test_prediction_system_ps_p7_expected_result_matrix_metamorphic_guard.py"
P6 = ROOT / "tools" / "test_prediction_system_ps_p6_calibration_confidence_roadmap_guard.py"
P5 = ROOT / "tools" / "test_prediction_system_ps_p5_evaluation_report_summary_guard.py"
P4 = ROOT / "tools" / "test_prediction_system_ps_p4_evaluation_not_evaluable_guard.py"


def test_ps_p8_design_doc_records_calibration_review_contract_shape() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P8_CALIBRATION_REVIEW_CONTRACT_DESIGN_2026-06-19.md",
        "PS-P8 is a no-code contract design slice for a future `PredictionCalibrationReview` object.",
        "Evaluation outputs are evidence, not authority.",
        "Future calibration review contracts should live in a separate prediction calibration/review module.",
        "Do not place calibration review logic inside build_prediction_system_result.",
        "PredictionEvaluationReport is an input snapshot to calibration review, not the owner of review state.",
        "PredictionCalibrationReview:",
        "review_id: str",
        "source_evaluation_report_id: str | None",
        "confidence_bucket_review: dict[str, object]",
        "caution_bucket_review: dict[str, object]",
        "family_review: dict[str, object]",
        "horizon_review: dict[str, object]",
        "risk_catalog_hits: tuple[str, ...]",
        "calibration_candidate_notes: tuple[str, ...]",
        "would_change_score_formula: bool = False",
        "would_change_confidence_behavior: bool = False",
        "would_change_caution_behavior: bool = False",
        "would_change_family_labels: bool = False",
        "would_enable_trigger_eligibility: bool = False",
        "would_collect_public_source: bool = False",
        "would_write_runtime_artifact: bool = False",
        "would_send_to_broker: bool = False",
        "command_ledger_append_requested: bool = False",
        "autotrade_decision_append_requested: bool = False",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p8_design_doc_records_advisory_vocab_and_missing_input_behavior() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = [
        "confidence_ordering_suspect",
        "caution_bucket_not_discriminative",
        "family_underperformance_candidate",
        "horizon_underperformance_candidate",
        "not_evaluable_skew",
        "missing_outcome_skew",
        "schema_drift_suspect",
        "silent_fallback_suspect",
        "lookahead_bias_review_required",
        "overconfidence_review_required",
        "aggregation_hiding_review_required",
        "scenario_switch_review_not_ready",
        "refresh_required_review_not_ready",
        "evaluation_report_missing",
        "evaluation_records_missing",
        "calibration_review_in_memory_only",
        "Missing evaluation report -> blockers include evaluation_report_missing.",
        "Missing confidence_summary -> warnings include confidence_summary_missing.",
        "Missing caution_summary -> warnings include caution_summary_missing.",
        "Scenario switch placeholders are allowed but must mark scenario_switch_review_not_ready.",
        "Refresh-required placeholders are allowed but must mark refresh_required_review_not_ready.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p8_design_doc_preserves_no_behavior_change_and_validation_cap_policy() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = [
        "No production code changed.",
        "No tests alter production behavior.",
        "This design is documentation and guard only.",
        "No score formula changes.",
        "No confidence behavior changes.",
        "No caution behavior changes.",
        "No rule_based_v0 label changes.",
        "No TriggerEligibility enablement.",
        "No command ledger append.",
        "No AutoTrade decision append.",
        "No broker/private API import.",
        "Focused verification should normally complete within about 3 validation cycles.",
        "More than about 3 cycles requires an explicit safety, trading-boundary, data-loss, or hard-to-localize failure reason.",
        "Use D:\\btc_ts_hot only for latest/runtime/current state checks when explicitly needed.",
        "Use E:\\btc_ts only for cold/archive/copy validation or long-term retained replay datasets.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p8_static_boundaries_and_previous_guard_anchors() -> None:
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
    required_production = [
        "class PredictionEvaluationReport",
        "def build_prediction_evaluation_report",
        "confidence_bucket_hit_rate",
        "caution_bucket_wrong_direction_rate",
        "would_write_runtime_artifact: bool = False",
        "autotrade_decision_append_requested: bool = False",
    ]
    missing_production = [item for item in required_production if item not in production_text]
    assert not missing_production, missing_production
    for path in (P7, P6, P5, P4, P6_DOC):
        assert path.exists(), path
    assert "test_ps_p7_expected_result_matrix_long_short_and_flat_outcomes" in P7.read_text(encoding="utf-8")
    assert "PredictionCalibrationReview:" in P6_DOC.read_text(encoding="utf-8")
    assert "test_ps_p6_roadmap_doc_records_calibration_confidence_boundaries" in P6.read_text(encoding="utf-8")
    assert "test_ps_p5_summary_keys_match_ps_p2_design" in P5.read_text(encoding="utf-8")
    assert "test_ps_p4_invalid_outcome_prices_are_not_evaluable" in P4.read_text(encoding="utf-8")


def test_ps_p8_files_compile() -> None:
    for path in (EVAL, SYSTEM, RULE, FORECAST, P7, P6, P5, P4, Path(__file__)):
        assert path.exists(), path
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_p8_design_doc_records_calibration_review_contract_shape()
    test_ps_p8_design_doc_records_advisory_vocab_and_missing_input_behavior()
    test_ps_p8_design_doc_preserves_no_behavior_change_and_validation_cap_policy()
    test_ps_p8_static_boundaries_and_previous_guard_anchors()
    test_ps_p8_files_compile()
    print("[OK] Prediction System PS-P8 calibration review contract design guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
