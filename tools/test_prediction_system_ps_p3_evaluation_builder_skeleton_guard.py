# path: ./tools/test_prediction_system_ps_p3_evaluation_builder_skeleton_guard.py
# desc: Guard for PS-P3 in-memory Prediction System evaluation contract/builder skeleton.

from __future__ import annotations

import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"
INIT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "__init__.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
P2 = ROOT / "tools" / "test_prediction_system_ps_p2_evaluation_contract_design_guard.py"
P1 = ROOT / "tools" / "test_prediction_system_ps_p1_evaluation_replay_roadmap_guard.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"


def _forecast_record() -> dict[str, object]:
    return {
        "record_id": "forecast:trend:300",
        "bundle_id": "bundle:1",
        "generated_at": "2026-06-19T00:00:00Z",
        "prediction_id": "prediction:trend:300",
        "family": "trend_bias",
        "horizon_sec": 300,
        "horizon_label": "5m",
        "horizon_key": "5m",
        "primary_label": "long_bias",
        "confidence": "medium",
        "score": 0.66,
        "values_snapshot": {"trigger_eligibility_state": "blocked", "caution_level": "low"},
        "blockers": [],
        "warnings": [],
    }


def test_ps_p3_static_boundaries_and_exports() -> None:
    assert EVAL.exists(), EVAL
    text = "\n".join(path.read_text(encoding="utf-8") for path in (EVAL, INIT, SYSTEM, RULE))
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
    hits = [item for item in forbidden if item in text]
    assert not hits, hits
    required = [
        "class PredictionEvaluationRecord",
        "class PredictionEvaluationReport",
        "def build_prediction_evaluation_records",
        "def build_prediction_evaluation_report",
        "prediction_evaluation.ps_p3.v1",
        "would_write_runtime_artifact: bool = False",
        "autotrade_decision_append_requested: bool = False",
        "PredictionEvaluationRecord",
        "build_prediction_evaluation_report",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing


def test_ps_p3_builds_in_memory_evaluation_report_with_outcome() -> None:
    from btcts.prediction import build_prediction_evaluation_report

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    report = build_prediction_evaluation_report(
        forecast_batch={"records": [_forecast_record()]},
        outcome_windows={
            "trend_bias:300": {
                "family": "trend_bias",
                "horizon_sec": 300,
                "evaluation_window_start": "2026-06-19T00:00:00Z",
                "evaluation_window_end": "2026-06-19T00:05:00Z",
                "start_price": 10_000_000,
                "end_price": 10_010_000,
                "min_price": 9_995_000,
                "max_price": 10_012_000,
                "source_ref": "offline_replay_fixture",
            }
        },
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:1", "generated_at": "2026-06-19T00:00:00Z"}},
        now=now,
        source_ref="prediction_snapshot_fixture",
    )
    data = report.to_dict()
    assert data["logic_version"] == "prediction_evaluation.ps_p3.v1"
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_write_runtime_artifact"] is False
    assert data["would_send_to_broker"] is False
    assert data["command_ledger_append_requested"] is False
    assert data["autotrade_decision_append_requested"] is False
    assert data["evaluated_record_count"] == 1
    assert data["not_evaluable_count"] == 0
    record = data["records"][0]
    assert record["hit_label"] == "correct_direction"
    assert record["observed_direction"] == "up"
    assert record["observed_return_bps"] == 10.0
    assert record["predicted_trigger_eligibility_state"] == "blocked"
    assert record["outcome_available"] is True
    assert data["family_summary"]["directional_hit_rate_by_family"]["trend_bias"] == 1.0


def test_ps_p3_missing_outcome_is_not_evaluable_and_non_executing() -> None:
    from btcts.prediction import build_prediction_evaluation_report

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    report = build_prediction_evaluation_report(
        forecast_batch={"records": [_forecast_record()]},
        outcome_windows={},
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:missing"}},
        now=now,
    )
    data = report.to_dict()
    assert data["evaluated_record_count"] == 0
    assert data["not_evaluable_count"] == 1
    assert data["records"][0]["hit_label"] == "not_evaluable"
    assert data["records"][0]["not_evaluable_reason"] == "outcome_window_missing"
    assert data["records"][0]["outcome_available"] is False
    assert "outcome_window_missing" in data["data_quality_notes"]
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False


def test_ps_p3_existing_guard_anchors_and_compile() -> None:
    for path in (EVAL, INIT, SYSTEM, RULE, P2, P1, PS_G, Path(__file__)):
        assert path.exists(), path
        py_compile.compile(str(path), doraise=True)
    assert "test_ps_p2_design_doc_records_evaluation_contract_shapes" in P2.read_text(encoding="utf-8")
    assert "test_ps_p1_roadmap_doc_records_evaluation_boundaries" in P1.read_text(encoding="utf-8")
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")


def main() -> int:
    test_ps_p3_static_boundaries_and_exports()
    test_ps_p3_builds_in_memory_evaluation_report_with_outcome()
    test_ps_p3_missing_outcome_is_not_evaluable_and_non_executing()
    test_ps_p3_existing_guard_anchors_and_compile()
    print("[OK] Prediction System PS-P3 evaluation builder skeleton guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
