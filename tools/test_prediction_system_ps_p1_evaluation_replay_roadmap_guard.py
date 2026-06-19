# path: ./tools/test_prediction_system_ps_p1_evaluation_replay_roadmap_guard.py
# desc: Guard for PS-P1 no-code evaluation / replay-feedback roadmap for standalone Prediction System outputs.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P1_EVALUATION_REPLAY_ROADMAP_2026-06-19.md"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"
F12 = ROOT / "tools" / "test_prediction_system_ps_f12_feature_depth_integration_close_guard.py"
N2 = ROOT / "tools" / "test_prediction_system_ps_n2_scenario_review_summary_guard.py"
O2 = ROOT / "tools" / "test_prediction_system_ps_o2_whole_surface_cc_guard.py"
O3 = ROOT / "tools" / "test_prediction_system_ps_o3_whole_surface_cc_close_guard.py"


def test_ps_p1_roadmap_doc_records_evaluation_boundaries() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P1_EVALUATION_REPLAY_ROADMAP_2026-06-19.md",
        "PS-P1 is a no-code roadmap slice for offline/replay-only evaluation",
        "Prediction System is standalone, read-only, non-executing, and AutoTrade/Collector separated.",
        "Previously emitted PredictionSystemResult dictionaries or serialized snapshots.",
        "Later observed market outcome windows from offline/replay datasets.",
        "Use D:\\btc_ts_hot only for latest/runtime/current state checks when explicitly needed.",
        "Use E:\\btc_ts only for cold/archive/copy validation or long-term retained replay datasets.",
        "No live collection.",
        "No Collector runtime import.",
        "No AutoTrade import.",
        "No broker/private API import.",
        "No AutoTrade decision append.",
        "No command ledger append.",
        "PredictionEvaluationRecord:",
        "PredictionEvaluationReport:",
        "directional_hit_rate_by_horizon",
        "scenario_switch_watch_follow_through_rate",
        "PS-P2: no-code evaluation contract design.",
        "No production code changed.",
        "This roadmap is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p1_production_static_boundaries_still_hold() -> None:
    production_text = "\n".join(path.read_text(encoding="utf-8") for path in (SYSTEM, RULE, CONTRACT, FORECAST))
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
        "ForecastLedgerRecord",
        "ForecastLedgerBatch",
        "would_append_ledger: bool = False",
        "scenario_review_summary",
        "trigger_eligibility_state=\"blocked\"",
    ]
    missing = [item for item in required_markers if item not in production_text]
    assert not missing, missing


def test_ps_p1_existing_guard_anchors_present() -> None:
    for path in (PS_G, F12, N2, O2, O3):
        assert path.exists(), path
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")
    assert "test_ps_f12_prediction_system_digest_and_boundaries" in F12.read_text(encoding="utf-8")
    assert "test_ps_n2_scenario_review_summary_shape_with_feature_depth" in N2.read_text(encoding="utf-8")
    assert "test_ps_o2_doc_records_whole_surface_cc_findings" in O2.read_text(encoding="utf-8")
    assert "test_ps_o3_close_doc_records_stable_findings_and_next_direction" in O3.read_text(encoding="utf-8")


def test_ps_p1_files_compile() -> None:
    for path in (SYSTEM, RULE, CONTRACT, FORECAST, PS_G, F12, N2, O2, O3, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_p1_roadmap_doc_records_evaluation_boundaries()
    test_ps_p1_production_static_boundaries_still_hold()
    test_ps_p1_existing_guard_anchors_present()
    test_ps_p1_files_compile()
    print("[OK] Prediction System PS-P1 evaluation / replay-feedback roadmap guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
