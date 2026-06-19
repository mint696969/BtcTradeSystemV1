# path: ./tools/test_prediction_system_ps_o1_roadmap_checkpoint_guard.py
# desc: Guard for PS-O1 no-code roadmap checkpoint for current Prediction System state and next candidate work.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_O1_ROADMAP_CHECKPOINT_2026-06-19.md"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"
N2 = ROOT / "tools" / "test_prediction_system_ps_n2_scenario_review_summary_guard.py"
N3 = ROOT / "tools" / "test_prediction_system_ps_n3_scenario_review_summary_cc_guard.py"
N4 = ROOT / "tools" / "test_prediction_system_ps_n4_narrative_line_close_checkpoint_guard.py"


def test_ps_o1_roadmap_doc_records_current_surface_and_next_recommendation() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_O1_ROADMAP_CHECKPOINT_2026-06-19.md",
        "PS-O1 is a no-code roadmap checkpoint after PS-N4.",
        "All 11 rule_based_v0 families emit outputs.",
        "scenario_review_summary is emitted as a top-level review-only digest.",
        "Do not expand feature-depth family wiring immediately.",
        "Do not resume AutoTrade automatically.",
        "Option A: whole-surface Code Check pass",
        "Option B: evaluation / replay-feedback roadmap",
        "Option C: calibration / confidence roadmap",
        "Option D: UX documentation only",
        "Choose Option A first: PS-O2 whole-surface Code Check pass.",
        "No production code changed.",
        "This checkpoint is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_o1_production_static_boundaries_still_hold() -> None:
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
        "ScenarioCoreOutput",
        "scenario_trace_detail",
        "scenario_review_summary",
        "trigger_eligibility_state=\"blocked\"",
        "liquidity_feature_depth_context_version",
        "orderbook_breakout_algo_context_version",
        "opportunity_tradeflow_context_version",
    ]
    missing = [item for item in required_markers if item not in production_text]
    assert not missing, missing


def test_ps_o1_existing_guard_anchors_present() -> None:
    for path in (PS_G, F12, N2, N3, N4):
        assert path.exists(), path
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in F12.read_text(encoding="utf-8")
    assert "test_ps_n2_scenario_review_summary_shape_with_feature_depth" in N2.read_text(encoding="utf-8")
    assert "test_ps_n3_review_doc_records_findings" in N3.read_text(encoding="utf-8")
    assert "test_ps_n4_close_doc_records_stop_decision_and_next_direction" in N4.read_text(encoding="utf-8")


def test_ps_o1_files_compile() -> None:
    for path in (SYSTEM, RULE, CONTRACT, PS_G, F12, N2, N3, N4, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_o1_roadmap_doc_records_current_surface_and_next_recommendation()
    test_ps_o1_production_static_boundaries_still_hold()
    test_ps_o1_existing_guard_anchors_present()
    test_ps_o1_files_compile()
    print("[OK] Prediction System PS-O1 roadmap checkpoint guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
