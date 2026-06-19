# path: ./tools/test_prediction_system_ps_p4_evaluation_not_evaluable_guard.py
# desc: Focused guard for PS-P4 Prediction System evaluation not_evaluable / missing outcome behavior.

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
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
P3 = ROOT / "tools" / "test_prediction_system_ps_p3_evaluation_builder_skeleton_guard.py"
P2 = ROOT / "tools" / "test_prediction_system_ps_p2_evaluation_contract_design_guard.py"
P1 = ROOT / "tools" / "test_prediction_system_ps_p1_evaluation_replay_roadmap_guard.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"


def _base_record(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
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
    row.update(overrides)
    return row


def _valid_outcome(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
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
    row.update(overrides)
    return row


def test_ps_p4_invalid_outcome_prices_are_not_evaluable() -> None:
    from btcts.prediction import build_prediction_evaluation_report

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    report = build_prediction_evaluation_report(
        forecast_batch={"records": [_base_record()]},
        outcome_windows={"trend_bias:300": _valid_outcome(start_price=0, end_price=10_010_000)},
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:invalid_price"}},
        now=now,
    )
    data = report.to_dict()
    record = data["records"][0]
    assert data["evaluated_record_count"] == 0
    assert data["not_evaluable_count"] == 1
    assert record["hit_label"] == "not_evaluable"
    assert record["timing_label"] == "not_evaluable"
    assert record["not_evaluable_reason"] == "outcome_price_invalid"
    assert record["observed_return_bps"] is None
    assert record["observed_direction"] == "unknown"
    assert "outcome_price_invalid" in record["blockers"]
    assert "outcome_price_invalid" in data["data_quality_notes"]
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_write_runtime_artifact"] is False
    assert data["would_send_to_broker"] is False
    assert data["command_ledger_append_requested"] is False
    assert data["autotrade_decision_append_requested"] is False


def test_ps_p4_missing_prediction_label_is_not_evaluable_with_valid_outcome() -> None:
    from btcts.prediction import build_prediction_evaluation_report

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    record = _base_record(primary_label=None)
    report = build_prediction_evaluation_report(
        forecast_batch={"records": [record]},
        outcome_windows={"trend_bias:300": _valid_outcome()},
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:missing_label"}},
        now=now,
    )
    data = report.to_dict()
    evaluated = data["records"][0]
    assert data["evaluated_record_count"] == 0
    assert data["not_evaluable_count"] == 1
    assert evaluated["predicted_label"] == "unknown"
    assert evaluated["hit_label"] == "not_evaluable"
    assert evaluated["not_evaluable_reason"] == "prediction_label_missing"
    assert "prediction_label_missing" in evaluated["blockers"]
    assert "prediction_label_missing" in data["data_quality_notes"]
    assert evaluated["outcome_available"] is True
    assert evaluated["observed_return_bps"] == 10.0


def test_ps_p4_trigger_state_warning_does_not_enable_execution() -> None:
    from btcts.prediction import build_prediction_evaluation_report

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    record = _base_record(values_snapshot={"trigger_eligibility_state": "candidate", "caution_level": "medium"})
    report = build_prediction_evaluation_report(
        forecast_batch={"records": [record]},
        outcome_windows={"trend_bias:300": _valid_outcome()},
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:trigger_warning"}},
        now=now,
    )
    data = report.to_dict()
    evaluated = data["records"][0]
    assert data["evaluated_record_count"] == 1
    assert evaluated["predicted_trigger_eligibility_state"] == "candidate"
    assert "prediction_trigger_eligibility_state_not_blocked" in evaluated["warnings"]
    assert evaluated["hit_label"] == "correct_direction"
    assert evaluated["read_only"] is True
    assert evaluated["non_executing"] is True
    assert evaluated["would_collect_public_source"] is False
    assert evaluated["would_write_runtime_artifact"] is False
    assert evaluated["would_send_to_broker"] is False
    assert evaluated["broker_execution_requested"] is False
    assert evaluated["mode_apply_requested"] is False
    assert evaluated["command_ledger_append_requested"] is False
    assert evaluated["autotrade_decision_append_requested"] is False
    assert data["would_send_to_broker"] is False
    assert data["autotrade_decision_append_requested"] is False


def test_ps_p4_missing_forecast_batch_is_blocked_in_memory_only() -> None:
    from btcts.prediction import build_prediction_evaluation_report

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    report = build_prediction_evaluation_report(
        forecast_batch=None,
        outcome_windows={"trend_bias:300": _valid_outcome()},
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:missing_forecast"}},
        now=now,
    )
    data = report.to_dict()
    assert data["records"] == []
    assert data["input_forecast_record_count"] == 0
    assert data["evaluated_record_count"] == 0
    assert data["not_evaluable_count"] == 0
    assert "forecast_batch_missing" in data["blockers"]
    assert "forecast_records_missing" in data["blockers"]
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_write_runtime_artifact"] is False
    assert data["would_send_to_broker"] is False
    assert data["command_ledger_append_requested"] is False
    assert data["autotrade_decision_append_requested"] is False


def test_ps_p4_static_boundaries_and_previous_guard_anchors() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in (EVAL, INIT, SYSTEM, RULE, FORECAST))
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
        "def build_prediction_evaluation_report",
        "outcome_window_missing",
        "outcome_price_invalid",
        "prediction_label_missing",
        "prediction_trigger_eligibility_state_not_blocked",
        "autotrade_decision_append_requested: bool = False",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing
    for path in (P3, P2, P1, PS_G):
        assert path.exists(), path
    assert "test_ps_p3_missing_outcome_is_not_evaluable_and_non_executing" in P3.read_text(encoding="utf-8")
    assert "test_ps_p2_design_doc_records_evaluation_contract_shapes" in P2.read_text(encoding="utf-8")
    assert "test_ps_p1_roadmap_doc_records_evaluation_boundaries" in P1.read_text(encoding="utf-8")
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")


def test_ps_p4_files_compile() -> None:
    for path in (EVAL, INIT, SYSTEM, RULE, FORECAST, P3, P2, P1, PS_G, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_p4_invalid_outcome_prices_are_not_evaluable()
    test_ps_p4_missing_prediction_label_is_not_evaluable_with_valid_outcome()
    test_ps_p4_trigger_state_warning_does_not_enable_execution()
    test_ps_p4_missing_forecast_batch_is_blocked_in_memory_only()
    test_ps_p4_static_boundaries_and_previous_guard_anchors()
    test_ps_p4_files_compile()
    print("[OK] Prediction System PS-P4 evaluation not_evaluable guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
