# path: ./tools/test_prediction_system_ps_o2_whole_surface_cc_guard.py
# desc: Guard for PS-O2 review-only whole-surface Code Check pass for the current standalone Prediction System.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_O2_WHOLE_SURFACE_CC_2026-06-19.md"
PRODUCTION_FILES = (
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "feature_depth.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "source_quality.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "bundle_assembly.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "contracts.py",
    ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "__init__.py",
)
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"
N2 = ROOT / "tools" / "test_prediction_system_ps_n2_scenario_review_summary_guard.py"
N3 = ROOT / "tools" / "test_prediction_system_ps_n3_scenario_review_summary_cc_guard.py"
N4 = ROOT / "tools" / "test_prediction_system_ps_n4_narrative_line_close_checkpoint_guard.py"
O1 = ROOT / "tools" / "test_prediction_system_ps_o1_roadmap_checkpoint_guard.py"


def test_ps_o2_doc_records_whole_surface_cc_findings() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_O2_WHOLE_SURFACE_CC_2026-06-19.md",
        "PS-O2 is a review-only whole-surface Code Check pass after PS-O1.",
        "✅ OK: standalone boundary remains intact",
        "✅ OK: top-level contracts remain compatible with current runner",
        "✅ OK: runner assembly is layered and deterministic",
        "✅ OK: rule family coverage remains 11 families",
        "✅ OK: feature-depth remains context-only and non-owner",
        "✅ OK: scenario_review_summary is review-only",
        "✅ OK: forecast ledger is in-memory and non-append",
        "✅ OK: provider reliability remains conservative/context-only",
        "⚠️ Risk: whole-surface guard overlap is growing",
        "⚠️ Risk: evaluation/calibration remains unimplemented",
        "No production code changes in PS-O2.",
        "PS-O3: no-code close checkpoint for the whole-surface CC line.",
        "This pass is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_o2_production_static_boundaries() -> None:
    production_text = "\n".join(path.read_text(encoding="utf-8") for path in PRODUCTION_FILES)
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
        "PredictionSystemResult",
        "ScenarioCoreOutput",
        "INITIAL_FAMILIES",
        "build_rule_based_v0_outputs",
        "build_feature_depth_snapshot",
        "build_provider_reliability_registry",
        "build_forecast_ledger_records_from_bundle",
        "build_inference_bundle_from_outputs",
        "scenario_trace_detail",
        "scenario_review_summary",
        "trigger_eligibility_state=\"blocked\"",
        "liquidity_feature_depth_context_version",
        "orderbook_breakout_algo_context_version",
        "opportunity_tradeflow_context_version",
    ]
    missing = [item for item in required_markers if item not in production_text]
    assert not missing, missing


def test_ps_o2_existing_guard_anchors_present() -> None:
    for path in (PS_G, F12, N2, N3, N4, O1):
        assert path.exists(), path
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in F12.read_text(encoding="utf-8")
    assert "test_ps_n2_scenario_review_summary_shape_with_feature_depth" in N2.read_text(encoding="utf-8")
    assert "test_ps_n3_review_doc_records_findings" in N3.read_text(encoding="utf-8")
    assert "test_ps_n4_close_doc_records_stop_decision_and_next_direction" in N4.read_text(encoding="utf-8")
    assert "test_ps_o1_roadmap_doc_records_current_surface_and_next_recommendation" in O1.read_text(encoding="utf-8")


def test_ps_o2_files_compile() -> None:
    for path in (*PRODUCTION_FILES, PS_G, F12, N2, N3, N4, O1, Path(__file__)):
        assert path.exists(), path
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_o2_doc_records_whole_surface_cc_findings()
    test_ps_o2_production_static_boundaries()
    test_ps_o2_existing_guard_anchors_present()
    test_ps_o2_files_compile()
    print("[OK] Prediction System PS-O2 whole-surface CC guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
