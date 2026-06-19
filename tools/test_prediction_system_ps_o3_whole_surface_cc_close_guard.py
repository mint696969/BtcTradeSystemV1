# path: ./tools/test_prediction_system_ps_o3_whole_surface_cc_close_guard.py
# desc: Guard for PS-O3 no-code close checkpoint for the Prediction System whole-surface CC line.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_O3_WHOLE_SURFACE_CC_CLOSE_2026-06-19.md"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"
N2 = ROOT / "tools" / "test_prediction_system_ps_n2_scenario_review_summary_guard.py"
O1 = ROOT / "tools" / "test_prediction_system_ps_o1_roadmap_checkpoint_guard.py"
O2 = ROOT / "tools" / "test_prediction_system_ps_o2_whole_surface_cc_guard.py"


def test_ps_o3_close_doc_records_stable_findings_and_next_direction() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_O3_WHOLE_SURFACE_CC_CLOSE_2026-06-19.md",
        "PS-O3 closes the whole-surface Code Check line after PS-O2.",
        "OK: standalone boundary remains intact.",
        "OK: rule family coverage remains 11 families.",
        "OK: scenario_review_summary is review-only.",
        "Guard overlap is a future maintainability note, not a current behavior or safety defect.",
        "Evaluation/calibration being unimplemented is a roadmap/quality gap, not an execution risk.",
        "No trading path is enabled from Prediction System outputs.",
        "Do not refactor guard overlap immediately.",
        "Do not add evaluation/calibration behavior directly after PS-O3 without a roadmap slice.",
        "Choose Option A first: evaluation / replay-feedback roadmap.",
        "No production code changed.",
        "This checkpoint is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_o3_production_static_boundaries_still_hold() -> None:
    production_text = "\n".join(path.read_text(encoding="utf-8") for path in (SYSTEM, RULE, CONTRACT))
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
        "INITIAL_FAMILIES",
        "scenario_review_summary",
        "trigger_eligibility_state=\"blocked\"",
        "liquidity_feature_depth_context_version",
        "orderbook_breakout_algo_context_version",
        "opportunity_tradeflow_context_version",
    ]
    missing = [item for item in required_markers if item not in production_text]
    assert not missing, missing


def test_ps_o3_existing_guard_anchors_present() -> None:
    for path in (PS_G, F12, N2, O1, O2):
        assert path.exists(), path
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in F12.read_text(encoding="utf-8")
    assert "test_ps_n2_scenario_review_summary_shape_with_feature_depth" in N2.read_text(encoding="utf-8")
    assert "test_ps_o1_roadmap_doc_records_current_surface_and_next_recommendation" in O1.read_text(encoding="utf-8")
    assert "test_ps_o2_doc_records_whole_surface_cc_findings" in O2.read_text(encoding="utf-8")


def test_ps_o3_files_compile() -> None:
    for path in (SYSTEM, RULE, CONTRACT, PS_G, F12, N2, O1, O2, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_o3_close_doc_records_stable_findings_and_next_direction()
    test_ps_o3_production_static_boundaries_still_hold()
    test_ps_o3_existing_guard_anchors_present()
    test_ps_o3_files_compile()
    print("[OK] Prediction System PS-O3 whole-surface CC close guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
