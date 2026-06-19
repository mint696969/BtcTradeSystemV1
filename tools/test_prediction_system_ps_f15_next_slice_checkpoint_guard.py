# path: ./tools/test_prediction_system_ps_f15_next_slice_checkpoint_guard.py
# desc: Guard for PS-F15 no-code checkpoint selecting the next Prediction System slice.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_F15_NEXT_SLICE_CHECKPOINT_2026-06-19.md"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
F14 = ROOT / "tools" / "test_prediction_system_ps_f14_cc_pass_guard.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"


def test_ps_f15_checkpoint_doc_records_next_direction() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_F15_NEXT_SLICE_CHECKPOINT_2026-06-19.md",
        "Stop feature-depth expansion for now.",
        "Next recommended direction is scenario narrative / UX digest refinement.",
        "PS-N1: scenario narrative / UX digest refinement plan",
        "Do not change prediction scores, family labels, trigger eligibility, execution behavior, or data collection.",
        "No production code changed.",
        "This checkpoint is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_f15_production_static_boundaries_still_hold() -> None:
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
    assert "trigger_eligibility_state=\"blocked\"" in SYSTEM.read_text(encoding="utf-8")
    assert "ScenarioCoreOutput" in SYSTEM.read_text(encoding="utf-8")
    assert "scenario_trace_detail" in SYSTEM.read_text(encoding="utf-8")


def test_ps_f15_existing_review_guard_anchors_present() -> None:
    assert F14.exists(), F14
    assert F12.exists(), F12
    f14_text = F14.read_text(encoding="utf-8")
    f12_text = F12.read_text(encoding="utf-8")
    assert "test_ps_f14_production_static_boundaries_and_version_markers" in f14_text
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in f12_text


def test_ps_f15_files_compile() -> None:
    for path in (SYSTEM, RULE, CONTRACT, F14, F12, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_f15_checkpoint_doc_records_next_direction()
    test_ps_f15_production_static_boundaries_still_hold()
    test_ps_f15_existing_review_guard_anchors_present()
    test_ps_f15_files_compile()
    print("[OK] Prediction System PS-F15 next slice checkpoint guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
