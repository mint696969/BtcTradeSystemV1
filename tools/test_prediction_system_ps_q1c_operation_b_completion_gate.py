# path: ./tools/test_prediction_system_ps_q1c_operation_b_completion_gate.py
# desc: Guard for PS-Q1C Operation B completion gate and no-overclaim boundary.

from __future__ import annotations

import json
import os
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_Q1C_OPERATION_B_COMPLETION_GATE_2026-06-19.md"
Q1B_DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_Q1B_REPLAY_DATA_QUALITY_GUARD_2026-06-19.md"
Q1_DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_Q1_FULL_REMAINING_IMPLEMENTATION_ROADMAP_2026-06-19.md"
P12_DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P12_STOP_REVIEW_CHECKPOINT_2026-06-19.md"
Q1B_GUARD = ROOT / "tools" / "test_prediction_system_ps_q1b_replay_data_quality_guard.py"
Q1_GUARD = ROOT / "tools" / "test_prediction_system_ps_q1_full_remaining_implementation_roadmap_guard.py"
P12_GUARD = ROOT / "tools" / "test_prediction_system_ps_p12_stop_review_checkpoint_guard.py"
EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"
CAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "calibration_review.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"

COLD_DATA_ROOT = Path(os.environ.get("BTCTS_COLD_DATA_ROOT", r"E:\btc_ts"))
ARCHIVE_DIR = COLD_DATA_ROOT / "replay" / "board_trade_replay_test_20260310T140344Z"
MANIFEST = ARCHIVE_DIR / "manifest.json"
REPORT = ARCHIVE_DIR / "replay_report.json"


def _compile_without_repo_pycache(path: Path) -> None:
    cache_dir = ROOT / "tmp" / "py_compile_cache" / path.parent.relative_to(ROOT)
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_name = path.name.replace(".", "_") + ".pyc"
    py_compile.compile(str(path), cfile=str(cache_dir / safe_name), doraise=True)


def test_ps_q1c_doc_records_operation_b_completion_without_overclaim() -> None:
    assert DOC.exists(), DOC
    text = DOC.read_text(encoding="utf-8")
    required = [
        "PS-Q1C is the close gate for the current-thread Operation B work.",
        "read-only replay-data quality guard only.",
        "It does not mean completing PS-Q2 through PS-Q9.",
        "A committed read-only replay/evaluation/calibration data-quality guard baseline.",
        "A committed read-only available-data inventory gate",
        "A documented no-overclaim boundary",
        "This confirms that a cold archive replay artifact exists",
        "not a full PredictionEvaluationReport/outcome dataset for production calibration.",
        "Therefore PS-Q1C must not claim that full real prediction evaluation/outcome datasets have been analyzed.",
        "That is enough to close Operation B honestly as a read-only guard/inventory baseline",
        "PS-Q2: source / artifact input coverage start",
        "PS-Q6 richer replay-data quality / evidence-quality expansion as real prediction evaluation artifacts become available",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_q1c_available_cold_replay_archive_inventory_when_present() -> None:
    # The guard is read-only. In this project environment E:\btc_ts is expected to exist.
    # If a different machine lacks the cold archive, the doc still records the no-overclaim boundary.
    if not COLD_DATA_ROOT.exists():
        text = DOC.read_text(encoding="utf-8")
        assert "E:\\btc_ts" in text
        assert "No production code changed." in text
        return

    assert MANIFEST.exists(), MANIFEST
    assert REPORT.exists(), REPORT
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    assert manifest["name"] == "board_trade_replay_test"
    assert manifest["created_at_utc"] == "20260310T140344Z"
    assert manifest["result_count"] == 664
    assert str(manifest["results_path"]).endswith("replay_results.jsonl")
    assert str(manifest["report_path"]).endswith("replay_report.json")
    source_paths = "\n".join(str(item) for item in manifest["source_paths"])
    assert "exchange=bitflyer" in source_paths
    assert "symbol=BTC_JPY" in source_paths
    assert "type=market.orderbook.snapshot" in source_paths
    assert "type=market.orderbook.diff" in source_paths
    assert "type=market.trade" in source_paths

    assert report["name"] == "board_trade_replay_test"
    assert report["result_count"] == 664
    assert report["board_count"] == 60
    assert report["trade_count"] == 604
    assert report["signal_count"] == 29
    assert report["microstructure_event_count"] == 1
    assert "pressure_shift" in report["event_name_counts"]


def test_ps_q1c_previous_baseline_and_roadmap_anchors() -> None:
    for path in (Q1B_DOC, Q1_DOC, P12_DOC, Q1B_GUARD, Q1_GUARD, P12_GUARD):
        assert path.exists(), path
    assert "Option B: read-only replay-data quality guard only." in Q1B_DOC.read_text(encoding="utf-8")
    assert "PS-Q6: replay-data quality guard / evidence quality gate" in Q1_DOC.read_text(encoding="utf-8")
    assert "Option B: continue with replay-data quality guards only" in P12_DOC.read_text(encoding="utf-8")
    assert "test_ps_q1b_calibration_review_marks_data_quality_risks_as_advisory_only" in Q1B_GUARD.read_text(encoding="utf-8")
    assert "test_ps_q1_doc_lists_remaining_work_packages_and_next_start" in Q1_GUARD.read_text(encoding="utf-8")
    assert "test_ps_p12_checkpoint_doc_records_stop_review_decision" in P12_GUARD.read_text(encoding="utf-8")


def test_ps_q1c_static_boundaries_and_compile() -> None:
    reviewed_text = "\n".join(path.read_text(encoding="utf-8") for path in (EVAL, CAL, SYSTEM, RULE, FORECAST))
    forbidden = [
        "btcts.autotrade",
        "btcts.collector_vnext",
        "append_decision_jsonl",
        "send_order",
        "place_order",
        "private_api",
        "requests.get",
        "urllib.request",
        "would_change_score_formula: bool = True",
        "would_change_confidence_behavior: bool = True",
        "would_change_caution_behavior: bool = True",
        "would_enable_trigger_eligibility: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in reviewed_text]
    assert not hits, hits

    for path in (EVAL, CAL, SYSTEM, RULE, FORECAST, Q1B_GUARD, Q1_GUARD, P12_GUARD, Path(__file__)):
        _compile_without_repo_pycache(path)


def main() -> int:
    test_ps_q1c_doc_records_operation_b_completion_without_overclaim()
    test_ps_q1c_available_cold_replay_archive_inventory_when_present()
    test_ps_q1c_previous_baseline_and_roadmap_anchors()
    test_ps_q1c_static_boundaries_and_compile()
    print("[OK] Prediction System PS-Q1C Operation B completion gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
