# path: ./tools/test_prediction_system_ps_q1_full_remaining_implementation_roadmap_guard.py
# desc: Guard for PS-Q1 full remaining Prediction System implementation roadmap and next-thread start gate.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_Q1_FULL_REMAINING_IMPLEMENTATION_ROADMAP_2026-06-19.md"
STANDALONE = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_STANDALONE_DESIGN_AND_ROADMAP_BTC_BITFLYER_2026-06-19.md"
GAP = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_CURRENT_CODE_GAP_INDEX_BTC_BITFLYER_2026-06-19.md"
P12 = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P12_STOP_REVIEW_CHECKPOINT_2026-06-19.md"
P12_GUARD = ROOT / "tools" / "test_prediction_system_ps_p12_stop_review_checkpoint_guard.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
SYSTEM_CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
SOURCE_QUALITY = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "source_quality.py"
FEATURE_DEPTH = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "feature_depth.py"
CAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "calibration_review.py"
EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"


def test_ps_q1_doc_corrects_remaining_roadmap_scope() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "PS-Q1 corrects and closes the current thread context",
        "WarRoom tab read-only prediction display.",
        "Prediction outputs that are high quality enough to become future AutoTrade trigger candidates.",
        "Other information-source acquisition / ingestion coverage",
        "Scenario Prediction Core strengthening beyond lite/basic behavior.",
        "The phrase \"Prediction System roadmap remaining tasks\" means the remaining work required to reach a usable Prediction System",
        "Trigger candidate quality\" does not mean enabling AutoTrade triggers now.",
        "TriggerEligibility remains blocked until a separate human-reviewed AutoTrade return gate.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_q1_doc_lists_remaining_work_packages_and_next_start() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = [
        "PS-Q2: source / artifact input coverage start",
        "PS-Q3: provider reliability and source quality hardening",
        "PS-Q4: feature construction from provided artifacts",
        "PS-Q5: Scenario Prediction Core strengthening",
        "PS-Q6: replay-data quality guard / evidence quality gate",
        "PS-Q7: WarRoom prediction tab read-only display path",
        "PS-Q8: AutoTrade trigger-candidate contract readiness",
        "PS-Q9: explicit AutoTrade return gate / trigger integration design",
        "Start next thread from:",
        "PS-Q2: source / artifact input coverage start",
        "docs/strategy/PREDICTION_SYSTEM_STANDALONE_DESIGN_AND_ROADMAP_BTC_BITFLYER_2026-06-19.md",
        "btcts_next/src/btcts/prediction/source_quality.py",
        "btcts_next/src/btcts/prediction/feature_depth.py",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_q1_doc_preserves_hard_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = [
        "No score changes unless explicitly designed and human-reviewed later.",
        "No confidence behavior changes unless explicitly designed and human-reviewed later.",
        "No caution behavior changes unless explicitly designed and human-reviewed later.",
        "No family label changes unless explicitly designed and human-reviewed later.",
        "No TriggerEligibility enablement.",
        "No AutoTrade trigger enablement in PS-Q2.",
        "No live trading.",
        "No broker/private API import.",
        "No AutoTrade decision append.",
        "No command ledger append.",
        "No mode/grant behavior.",
        "No Collector runtime import into Prediction core.",
        "No Prediction core ownership of collection loops.",
        "No runtime artifact writes from the Prediction System runner.",
        "No production code changed.",
        "This slice is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_q1_anchors_existing_roadmap_and_compiles() -> None:
    for path in (STANDALONE, GAP, P12, P12_GUARD, SYSTEM, SYSTEM_CONTRACT, SOURCE_QUALITY, FEATURE_DEPTH, CAL, EVAL):
        assert path.exists(), path
    assert "WarRoom and human reports" in STANDALONE.read_text(encoding="utf-8")
    assert "Provider reliability registry is mandatory" in STANDALONE.read_text(encoding="utf-8")
    assert "Prediction System itself is still mostly foundation-level" in GAP.read_text(encoding="utf-8")
    assert "Stop before production calibration behavior change." in P12.read_text(encoding="utf-8")
    assert "test_ps_p12_checkpoint_doc_records_stop_review_decision" in P12_GUARD.read_text(encoding="utf-8")
    for path in (SYSTEM, SYSTEM_CONTRACT, SOURCE_QUALITY, FEATURE_DEPTH, CAL, EVAL, P12_GUARD, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def test_ps_q1_static_boundaries_still_hold() -> None:
    reviewed_text = "\n".join(path.read_text(encoding="utf-8") for path in (SYSTEM, SYSTEM_CONTRACT, SOURCE_QUALITY, FEATURE_DEPTH, CAL, EVAL))
    forbidden = [
        "btcts.autotrade",
        "btcts.collector_vnext",
        "append_decision_jsonl",
        "send_order",
        "place_order",
        "private_api",
        "requests.get",
        "urllib.request",
        "would_enable_trigger_eligibility: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in reviewed_text]
    assert not hits, hits


def main() -> int:
    test_ps_q1_doc_corrects_remaining_roadmap_scope()
    test_ps_q1_doc_lists_remaining_work_packages_and_next_start()
    test_ps_q1_doc_preserves_hard_boundaries()
    test_ps_q1_anchors_existing_roadmap_and_compiles()
    test_ps_q1_static_boundaries_still_hold()
    print("[OK] Prediction System PS-Q1 full remaining implementation roadmap guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
