# path: ./tools/test_prediction_system_ps_n1_scenario_narrative_plan_guard.py
# desc: Guard for PS-N1 scenario narrative / UX digest plan. No production behavior changes.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_N1_SCENARIO_NARRATIVE_UX_DIGEST_PLAN_2026-06-19.md"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"
F15 = ROOT / "tools" / "test_prediction_system_ps_f15_next_slice_checkpoint_guard.py"
F14 = ROOT / "tools" / "test_prediction_system_ps_f14_cc_pass_guard.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"


def test_ps_n1_plan_doc_records_target_and_boundaries() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_N1_SCENARIO_NARRATIVE_UX_DIGEST_PLAN_2026-06-19.md",
        "scenario_review_summary",
        "version: ps_n1.v1",
        "review_only: true",
        "evidence_support",
        "evidence_conflicts",
        "watch_next",
        "refresh_or_rewrite",
        "context_versions",
        "PS-N2: implement scenario_review_summary as top-level review-only digest field",
        "No production code changed.",
        "This plan is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_n1_production_has_existing_review_inputs_and_boundaries() -> None:
    production_text = "\n".join(path.read_text(encoding="utf-8") for path in (SYSTEM, CONTRACT, RULE))
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
        "scenario_lite",
        "scenario_trace_detail",
        "evidence_refs",
        "human_narrative_ja",
        "gpt_review_digest",
        "what_to_watch_next",
        "refresh_required",
        "liquidity_feature_depth_context_version",
        "orderbook_breakout_algo_context_version",
        "opportunity_tradeflow_context_version",
        "trigger_eligibility_state=\"blocked\"",
    ]
    missing = [item for item in required_markers if item not in production_text]
    assert not missing, missing


def test_ps_n1_existing_guard_anchors_present() -> None:
    for path in (PS_G, F15, F14, F12):
        assert path.exists(), path
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")
    assert "test_ps_f15_checkpoint_doc_records_next_direction" in F15.read_text(encoding="utf-8")
    assert "test_ps_f14_production_static_boundaries_and_version_markers" in F14.read_text(encoding="utf-8")
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in F12.read_text(encoding="utf-8")


def test_ps_n1_files_compile() -> None:
    for path in (SYSTEM, CONTRACT, RULE, PS_G, F15, F14, F12, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_n1_plan_doc_records_target_and_boundaries()
    test_ps_n1_production_has_existing_review_inputs_and_boundaries()
    test_ps_n1_existing_guard_anchors_present()
    test_ps_n1_files_compile()
    print("[OK] Prediction System PS-N1 scenario narrative plan guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
