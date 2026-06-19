# path: ./tools/test_prediction_system_ps_n4_narrative_line_close_checkpoint_guard.py
# desc: Guard for PS-N4 no-code close checkpoint for the scenario narrative / UX digest line.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_N4_NARRATIVE_LINE_CLOSE_CHECKPOINT_2026-06-19.md"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"
N2 = ROOT / "tools" / "test_prediction_system_ps_n2_scenario_review_summary_guard.py"
N3 = ROOT / "tools" / "test_prediction_system_ps_n3_scenario_review_summary_cc_guard.py"


def test_ps_n4_close_doc_records_stop_decision_and_next_direction() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_N4_NARRATIVE_LINE_CLOSE_CHECKPOINT_2026-06-19.md",
        "PS-N4 closes the current scenario narrative / UX digest line after PS-N3.",
        "Do not add more scenario narrative / UX digest production behavior immediately.",
        "Do not rename scenario_review_summary fields immediately.",
        "Do not refactor scenario_review_summary helper immediately.",
        "Do not change ps_n1.v1 schema marker immediately.",
        "Do not expand feature-depth family wiring.",
        "Default recommendation:",
        "Choose Option A first.",
        "No production code changed.",
        "This checkpoint is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_n4_production_static_boundaries_and_summary_shape_still_hold() -> None:
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
        "def _scenario_review_summary",
        '"scenario_review_summary": _scenario_review_summary(',
        '"version": "ps_n1.v1"',
        '"review_only": True',
        '"trigger_eligibility_state": scenario.trigger_eligibility_state',
        '"feature_depth_primary_direction_owner"',
    ]
    missing = [item for item in required_markers if item not in production_text]
    assert not missing, missing


def test_ps_n4_existing_guard_anchors_present() -> None:
    for path in (PS_G, F12, N2, N3):
        assert path.exists(), path
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in F12.read_text(encoding="utf-8")
    assert "test_ps_n2_scenario_review_summary_shape_with_feature_depth" in N2.read_text(encoding="utf-8")
    assert "test_ps_n3_review_doc_records_findings" in N3.read_text(encoding="utf-8")


def test_ps_n4_files_compile() -> None:
    for path in (SYSTEM, RULE, CONTRACT, PS_G, F12, N2, N3, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_n4_close_doc_records_stop_decision_and_next_direction()
    test_ps_n4_production_static_boundaries_and_summary_shape_still_hold()
    test_ps_n4_existing_guard_anchors_present()
    test_ps_n4_files_compile()
    print("[OK] Prediction System PS-N4 narrative line close checkpoint guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
