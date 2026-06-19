# path: ./tools/test_prediction_system_ps_f14_cc_pass_guard.py
# desc: Guard for PS-F14 review-only Code Check artifact. No production behavior changes.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_F14_CC_PASS_2026-06-19.md"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
FEATURE_DEPTH = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "feature_depth.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"
F13 = ROOT / "tools" / "test_prediction_system_ps_f13_feature_depth_review_guard.py"


def test_ps_f14_review_doc_exists_and_records_findings() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_F14_CC_PASS_2026-06-19.md",
        "✅ OK: feature-depth helper ownership is intentional",
        "✅ OK: version markers are stable",
        "✅ OK: context-only / non-executing boundaries remain guarded",
        "✅ OK: guard layering is acceptable",
        "⚠️ Risk: duplicated feature-depth context fields",
        "No production code changes in PS-F14.",
        "No new feature-depth family behavior.",
        "No helper refactor now.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_f14_production_static_boundaries_and_version_markers() -> None:
    production_text = "\n".join(path.read_text(encoding="utf-8") for path in (RULE, SYSTEM, FEATURE_DEPTH))
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

    rule = RULE.read_text(encoding="utf-8")
    liquidity_section = rule.split("def _apply_liquidity_feature_depth_context", 1)[1].split("def _liquidity_execution_quality", 1)[0]
    generic_section = rule.split("def _apply_feature_depth_context_for_family", 1)[1].split("def _breakout_false_break", 1)[0]
    assert "context_version" not in liquidity_section
    assert 'context_version: str = "ps_e3.v1"' in generic_section
    assert '"version": context_version' in generic_section

    for marker in (
        "ps_e2.v1",
        "ps_e3.v1",
        "ps_e4.v1",
        "liquidity_feature_depth_context_version",
        "orderbook_breakout_algo_context_version",
        "opportunity_tradeflow_context_version",
        "liquidity_feature_depth_context_supplied",
        "breakout_false_break_feature_depth_context_supplied",
        "algorithmic_participant_footprint_feature_depth_context_supplied",
        "opportunity_participation_feature_depth_context_supplied",
    ):
        assert marker in production_text, marker


def test_ps_f14_existing_guard_anchors_present() -> None:
    assert F12.exists(), F12
    assert F13.exists(), F13
    f12_text = F12.read_text(encoding="utf-8")
    f13_text = F13.read_text(encoding="utf-8")
    assert "test_ps_f12_rule_based_feature_depth_context_versions" in f12_text
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in f12_text
    assert "test_ps_f13_review_doc_exists_and_records_stop_decision" in f13_text
    assert "production_and_review_text" in f13_text


def test_ps_f14_files_compile() -> None:
    for path in (RULE, SYSTEM, FEATURE_DEPTH, F12, F13, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_f14_review_doc_exists_and_records_findings()
    test_ps_f14_production_static_boundaries_and_version_markers()
    test_ps_f14_existing_guard_anchors_present()
    test_ps_f14_files_compile()
    print("[OK] Prediction System PS-F14 CC pass guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
