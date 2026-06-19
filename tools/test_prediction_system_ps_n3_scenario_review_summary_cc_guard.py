# path: ./tools/test_prediction_system_ps_n3_scenario_review_summary_cc_guard.py
# desc: Guard for PS-N3 review-only Code Check artifact for scenario_review_summary.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_N3_SCENARIO_REVIEW_SUMMARY_CC_2026-06-19.md"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
N2 = ROOT / "tools" / "test_prediction_system_ps_n2_scenario_review_summary_guard.py"
N1 = ROOT / "tools" / "test_prediction_system_ps_n1_scenario_narrative_plan_guard.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"
F14 = ROOT / "tools" / "test_prediction_system_ps_f14_cc_pass_guard.py"
F15 = ROOT / "tools" / "test_prediction_system_ps_f15_next_slice_checkpoint_guard.py"


def test_ps_n3_review_doc_records_findings() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_N3_SCENARIO_REVIEW_SUMMARY_CC_2026-06-19.md",
        "✅ OK: helper placement is acceptable",
        "✅ OK: review-only boundary is explicit",
        "✅ OK: missing-input behavior is covered",
        "✅ OK: feature-depth context versions remain context-only",
        "✅ OK: output counts are preserved",
        "⚠️ Risk: version marker name remains ps_n1.v1",
        "⚠️ Risk: evidence_support includes turning/switch evidence",
        "No production code changes in PS-N3.",
        "Proceed only with this review artifact and guard.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_n3_production_static_boundaries_and_shape_still_hold() -> None:
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
        '"primary_story"',
        '"scenario_health"',
        '"evidence_support"',
        '"evidence_conflicts"',
        '"watch_next"',
        '"refresh_or_rewrite"',
        '"context_versions"',
        '"output_counts"',
        '"boundaries"',
    ]
    missing = [item for item in required_markers if item not in production_text]
    assert not missing, missing


def test_ps_n3_existing_guard_anchors_present() -> None:
    for path in (N2, N1, PS_G, F12, F14, F15):
        assert path.exists(), path
    assert "test_ps_n2_scenario_review_summary_shape_with_feature_depth" in N2.read_text(encoding="utf-8")
    assert "test_ps_n2_scenario_review_summary_missing_inputs" in N2.read_text(encoding="utf-8")
    assert "test_ps_n1_plan_doc_records_target_and_boundaries" in N1.read_text(encoding="utf-8")
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in F12.read_text(encoding="utf-8")
    assert "test_ps_f14_production_static_boundaries_and_version_markers" in F14.read_text(encoding="utf-8")
    assert "test_ps_f15_checkpoint_doc_records_next_direction" in F15.read_text(encoding="utf-8")


def test_ps_n3_files_compile() -> None:
    for path in (SYSTEM, RULE, CONTRACT, N2, N1, PS_G, F12, F14, F15, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_n3_review_doc_records_findings()
    test_ps_n3_production_static_boundaries_and_shape_still_hold()
    test_ps_n3_existing_guard_anchors_present()
    test_ps_n3_files_compile()
    print("[OK] Prediction System PS-N3 scenario_review_summary CC guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
