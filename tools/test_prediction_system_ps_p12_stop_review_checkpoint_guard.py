# path: ./tools/test_prediction_system_ps_p12_stop_review_checkpoint_guard.py
# desc: Guard for PS-P12 stop/review checkpoint before production calibration behavior change.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P12_STOP_REVIEW_CHECKPOINT_2026-06-19.md"
P11_DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P11_EVALUATION_CALIBRATION_CC_PASS_2026-06-19.md"
EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"
CAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "calibration_review.py"
INIT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "__init__.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
P11 = ROOT / "tools" / "test_prediction_system_ps_p11_evaluation_calibration_cc_pass_guard.py"
P10 = ROOT / "tools" / "test_prediction_system_ps_p10_confidence_caution_candidate_guard.py"
P9 = ROOT / "tools" / "test_prediction_system_ps_p9_calibration_review_builder_skeleton_guard.py"
P8 = ROOT / "tools" / "test_prediction_system_ps_p8_calibration_review_contract_design_guard.py"


def test_ps_p12_checkpoint_doc_records_stop_review_decision() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P12_STOP_REVIEW_CHECKPOINT_2026-06-19.md",
        "PS-P12 is a stop/review checkpoint before any production calibration behavior change.",
        "Stop before production calibration behavior change.",
        "Do not apply evaluation/calibration outputs to production score, confidence, caution, family labels, TriggerEligibility, or AutoTrade.",
        "Require a separate explicit human-reviewed design before any behavior-changing calibration work.",
        "Option A: stop this line and return to another mainline",
        "Option B: continue with replay-data quality guards only",
        "Option C: design future production calibration behavior",
        "Explicit human approval.",
        "Rollback plan.",
        "No production code changed.",
        "This checkpoint is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p12_checkpoint_doc_preserves_hard_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = [
        "No score changes.",
        "No confidence behavior changes.",
        "No caution behavior changes.",
        "No family label changes.",
        "No scenario_review_summary behavior changes.",
        "No TriggerEligibility enablement.",
        "No live collection.",
        "No Collector runtime import.",
        "No AutoTrade import.",
        "No broker/private API import.",
        "No external API call.",
        "No artifact writes from Prediction System runner.",
        "No AutoTrade decision append.",
        "No command ledger append.",
        "No mode/grant behavior.",
        "About 3 validation cycles is a guideline, not a hard cap.",
        "Cut off validation when checks provide diminishing returns, or ask for stop/review.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p12_static_boundaries_still_hold() -> None:
    reviewed_text = "\n".join(path.read_text(encoding="utf-8") for path in (EVAL, CAL, INIT, SYSTEM, RULE, FORECAST))
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


def test_ps_p12_previous_guard_anchors_and_compile() -> None:
    for path in (P11_DOC, P11, P10, P9, P8):
        assert path.exists(), path
    assert "PS-P12: stop/review checkpoint before any production calibration behavior change." in P11_DOC.read_text(encoding="utf-8")
    assert "test_ps_p11_cc_report_records_findings_and_no_change_decision" in P11.read_text(encoding="utf-8")
    assert "test_ps_p10_confidence_ordering_candidate_is_advisory_only_and_does_not_mutate_input" in P10.read_text(encoding="utf-8")
    assert "test_ps_p9_advisory_notes_are_generated_without_behavior_change" in P9.read_text(encoding="utf-8")
    assert "test_ps_p8_design_doc_records_calibration_review_contract_shape" in P8.read_text(encoding="utf-8")
    for path in (EVAL, CAL, INIT, SYSTEM, RULE, FORECAST, P11, P10, P9, P8, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_p12_checkpoint_doc_records_stop_review_decision()
    test_ps_p12_checkpoint_doc_preserves_hard_boundaries()
    test_ps_p12_static_boundaries_still_hold()
    test_ps_p12_previous_guard_anchors_and_compile()
    print("[OK] Prediction System PS-P12 stop/review checkpoint guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
