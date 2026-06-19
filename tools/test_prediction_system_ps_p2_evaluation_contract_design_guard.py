# path: ./tools/test_prediction_system_ps_p2_evaluation_contract_design_guard.py
# desc: Guard for PS-P2 no-code evaluation contract design for standalone Prediction System replay evaluation.

from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P2_EVALUATION_CONTRACT_DESIGN_2026-06-19.md"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
CONTRACT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system_contract.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
P1 = ROOT / "tools" / "test_prediction_system_ps_p1_evaluation_replay_roadmap_guard.py"
O3 = ROOT / "tools" / "test_prediction_system_ps_o3_whole_surface_cc_close_guard.py"
O2 = ROOT / "tools" / "test_prediction_system_ps_o2_whole_surface_cc_guard.py"
N2 = ROOT / "tools" / "test_prediction_system_ps_n2_scenario_review_summary_guard.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"


def test_ps_p2_design_doc_records_evaluation_contract_shapes() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "# path: ./docs/strategy/PREDICTION_SYSTEM_PS_P2_EVALUATION_CONTRACT_DESIGN_2026-06-19.md",
        "PS-P2 is a no-code design slice for future offline/replay-only evaluation contracts.",
        "PredictionEvaluationRecord intended shape",
        "PredictionEvaluationReport intended shape",
        "Future evaluation contracts should live in a separate prediction evaluation/replay module.",
        "Do not mutate PredictionSystemResult to store evaluation outcomes.",
        "prediction_run_id: str",
        "source_forecast_record_ref: str | None",
        "predicted_trigger_eligibility_state: str",
        "outcome_available: bool",
        "not_evaluable_reason: str | None",
        "autotrade_decision_append_requested: bool = False",
        "PredictionEvaluationReport required summaries",
        "scenario_switch_watch_follow_through_rate",
        "refresh_required_follow_through_rate",
        "Missing outcome window -> not_evaluable with not_evaluable_reason=outcome_window_missing.",
        "The builder should never require AutoTrade objects.",
        "Use D:\\btc_ts_hot only for latest/runtime/current state checks when explicitly needed.",
        "Use E:\\btc_ts only for cold/archive/copy validation or long-term retained replay datasets.",
        "Choose PS-P3: in-memory evaluation contract/builder skeleton.",
        "No production code changed.",
        "This design is documentation and guard only.",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p2_production_static_boundaries_still_hold() -> None:
    production_text = "\n".join(path.read_text(encoding="utf-8") for path in (SYSTEM, CONTRACT, FORECAST, RULE))
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
        "PredictionSystemResult",
        "ForecastLedgerRecord",
        "ForecastLedgerBatch",
        "would_append_ledger: bool = False",
        "build_prediction_system_result",
        "scenario_review_summary",
        "trigger_eligibility_state=\"blocked\"",
    ]
    missing = [item for item in required_markers if item not in production_text]
    assert not missing, missing


def test_ps_p2_existing_guard_anchors_present() -> None:
    for path in (P1, O3, O2, N2, PS_G):
        assert path.exists(), path
    assert "test_ps_p1_roadmap_doc_records_evaluation_boundaries" in P1.read_text(encoding="utf-8")
    assert "test_ps_o3_close_doc_records_stable_findings_and_next_direction" in O3.read_text(encoding="utf-8")
    assert "test_ps_o2_doc_records_whole_surface_cc_findings" in O2.read_text(encoding="utf-8")
    assert "test_ps_n2_scenario_review_summary_shape_with_feature_depth" in N2.read_text(encoding="utf-8")
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")


def test_ps_p2_files_compile() -> None:
    for path in (SYSTEM, CONTRACT, FORECAST, RULE, P1, O3, O2, N2, PS_G, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_p2_design_doc_records_evaluation_contract_shapes()
    test_ps_p2_production_static_boundaries_still_hold()
    test_ps_p2_existing_guard_anchors_present()
    test_ps_p2_files_compile()
    print("[OK] Prediction System PS-P2 evaluation contract design guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
