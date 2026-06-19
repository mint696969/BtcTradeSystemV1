# path: ./tools/test_prediction_system_standalone_design_roadmap_guard.py
# desc: Guard for the standalone Prediction System design and roadmap document.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_STANDALONE_DESIGN_AND_ROADMAP_BTC_BITFLYER_2026-06-19.md"

REQUIRED = [
    "Prediction System must be treated as a standalone system",
    "Prediction System does not trade",
    "unknown",
    "no_edge",
    "flat",
    "no_change",
    "status_quo",
    "valid_from",
    "valid_until",
    "refresh_required",
    "bitFlyer Spot BTC_JPY board",
    "Provider reliability registry",
    "11 prediction families",
    "Scenario Prediction Core",
    "invalidation_condition",
    "rewrite_condition",
    "scenario_switch_condition",
    "parameter_set_id",
    "change_hypothesis",
    "rollback_condition",
    "hit_reason_candidates",
    "miss_reason_candidates",
    "7B-class dedicated AI",
    "GPT-readable artifacts",
    "WarRoom is a consumer only",
    "trigger_eligibility_state",
    "PS-A design and roadmap closure",
    "PS-N standalone completion gate",
    "no AutoTrade dependency",
    "separate PCs",
    "Prediction System and Collector should be movable to separate PCs",
    "no Collector runtime import",
    "btcts.collector_vnext",
    "Prediction System code must remain portable",
]

FORBIDDEN_AS_ALLOWED = [
    "This document authorizes broker execution",
    "This roadmap permits real orders",
    "AutoTrade mode apply is allowed",
    "append_decision_jsonl integration is allowed",
]


def main() -> int:
    if not DOC.exists():
        raise AssertionError(f"missing roadmap document: {DOC}")
    text = DOC.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED if item not in text]
    if missing:
        raise AssertionError(f"missing required roadmap anchors: {missing}")
    forbidden = [item for item in FORBIDDEN_AS_ALLOWED if item in text]
    if forbidden:
        raise AssertionError(f"forbidden authorization language found: {forbidden}")
    print("[OK] Prediction System standalone design/roadmap guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
