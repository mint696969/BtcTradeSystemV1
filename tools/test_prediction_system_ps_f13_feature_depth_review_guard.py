# path: ./tools/test_prediction_system_ps_f13_feature_depth_review_guard.py
# desc: Guard for PS-F13 review/planning artifact. No production behavior changes.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_F13_FEATURE_DEPTH_REVIEW_2026-06-19.md"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"


def test_ps_f13_review_doc_exists_and_records_stop_decision() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "Do not add another feature-depth family behavior immediately.",
        "Do not expand feature-depth into primary direction ownership.",
        "Do not make opportunity_participation an execution gate or grant source.",
        "FeatureDepthSnapshot remains context-only.",
        "TriggerEligibility remains blocked.",
        "liquidity_feature_depth_context_version = ps_e2.v1",
        "orderbook_breakout_algo_context_version = ps_e3.v1",
        "opportunity_tradeflow_context_version = ps_e4.v1",
        "Default recommendation:",
        "Choose Option C first.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_f13_static_boundaries_and_existing_guard_anchor() -> None:
    production_and_review_text = "\n".join(path.read_text(encoding="utf-8") for path in (DOC, RULE, SYSTEM))
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
    hits = [item for item in forbidden if item in production_and_review_text]
    assert not hits, hits
    assert F12.exists(), F12
    f12_text = F12.read_text(encoding="utf-8")
    assert "test_ps_f12_rule_based_feature_depth_context_versions" in f12_text
    assert "forbidden = [" in f12_text


def test_ps_f13_files_compile() -> None:
    for path in (RULE, SYSTEM, F12, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_f13_review_doc_exists_and_records_stop_decision()
    test_ps_f13_static_boundaries_and_existing_guard_anchor()
    test_ps_f13_files_compile()
    print("[OK] Prediction System PS-F13 feature-depth review guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
