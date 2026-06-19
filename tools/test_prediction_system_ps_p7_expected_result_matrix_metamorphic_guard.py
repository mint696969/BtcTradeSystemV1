# path: ./tools/test_prediction_system_ps_p7_expected_result_matrix_metamorphic_guard.py
# desc: Focused guard for PS-P7 Prediction System evaluation expected-result matrix and metamorphic invariants.

from __future__ import annotations

import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

EVAL = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "evaluation.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
FORECAST = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "forecast_ledger.py"
P6 = ROOT / "tools" / "test_prediction_system_ps_p6_calibration_confidence_roadmap_guard.py"
P5 = ROOT / "tools" / "test_prediction_system_ps_p5_evaluation_report_summary_guard.py"
P4 = ROOT / "tools" / "test_prediction_system_ps_p4_evaluation_not_evaluable_guard.py"
P3 = ROOT / "tools" / "test_prediction_system_ps_p3_evaluation_builder_skeleton_guard.py"

NOW = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)


def _record(record_id: str, label: str, *, confidence: str = "medium", caution: str = "low") -> dict[str, object]:
    return {
        "record_id": record_id,
        "bundle_id": "bundle:ps_p7",
        "generated_at": "2026-06-19T00:00:00Z",
        "prediction_id": f"prediction:{record_id}",
        "family": "trend_bias",
        "horizon_sec": 300,
        "horizon_label": "5m",
        "horizon_key": "5m",
        "primary_label": label,
        "confidence": confidence,
        "score": 0.5,
        "values_snapshot": {"trigger_eligibility_state": "blocked", "caution_level": caution},
        "blockers": [],
        "warnings": [],
    }


def _outcome(start: float, end: float, *, source_ref: str = "offline_replay_fixture") -> dict[str, object]:
    return {
        "family": "trend_bias",
        "horizon_sec": 300,
        "evaluation_window_start": "2026-06-19T00:00:00Z",
        "evaluation_window_end": "2026-06-19T00:05:00Z",
        "start_price": start,
        "end_price": end,
        "min_price": min(start, end),
        "max_price": max(start, end),
        "source_ref": source_ref,
    }


def _build(label: str, outcome: dict[str, object] | None, *, source_ref: str = "ps_p7_fixture") -> dict[str, Any]:
    from btcts.prediction import build_prediction_evaluation_report

    outcomes = {"trend_bias:300": outcome} if outcome is not None else {}
    report = build_prediction_evaluation_report(
        forecast_batch={"records": [_record(f"record:{label}", label)]},
        outcome_windows=outcomes,
        prediction_snapshot={"run_identity": {"prediction_run_id": f"run:{label}"}},
        now=NOW,
        source_ref=source_ref,
    )
    return report.to_dict()


def _single_record(data: dict[str, Any]) -> dict[str, Any]:
    assert len(data["records"]) == 1
    return data["records"][0]


def test_ps_p7_expected_result_matrix_long_short_and_flat_outcomes() -> None:
    cases = [
        ("long_bias", _outcome(10_000_000, 10_010_000), "up", "correct_direction"),
        ("long_bias", _outcome(10_000_000, 9_990_000), "down", "wrong_direction"),
        ("short_bias", _outcome(10_000_000, 9_990_000), "down", "correct_direction"),
        ("short_bias", _outcome(10_000_000, 10_010_000), "up", "wrong_direction"),
        ("long_bias", _outcome(10_000_000, 10_000_500), "flat", "neutral_or_flat"),
    ]
    for label, outcome, expected_direction, expected_hit in cases:
        data = _build(label, outcome)
        record = _single_record(data)
        assert record["observed_direction"] == expected_direction
        assert record["hit_label"] == expected_hit
        assert record["outcome_available"] is True
        assert record["not_evaluable_reason"] is None
        assert data["evaluated_record_count"] == 1
        assert data["not_evaluable_count"] == 0
        assert data["read_only"] is True
        assert data["non_executing"] is True
        assert data["would_send_to_broker"] is False
        assert data["autotrade_decision_append_requested"] is False


def test_ps_p7_price_scale_invariance() -> None:
    base = _build("long_bias", _outcome(10_000_000, 10_010_000))
    scaled = _build("long_bias", _outcome(100_000_000, 100_100_000))
    base_record = _single_record(base)
    scaled_record = _single_record(scaled)
    assert scaled_record["observed_return_bps"] == base_record["observed_return_bps"]
    assert scaled_record["observed_direction"] == base_record["observed_direction"]
    assert scaled_record["hit_label"] == base_record["hit_label"]
    assert scaled["family_summary"] == base["family_summary"]
    assert scaled["horizon_summary"] == base["horizon_summary"]
    assert scaled["confidence_summary"] == base["confidence_summary"]


def test_ps_p7_outcome_removal_and_source_ref_identity() -> None:
    with_outcome = _build("long_bias", _outcome(10_000_000, 10_010_000, source_ref="source:a"))
    source_only_changed = _build("long_bias", _outcome(10_000_000, 10_010_000, source_ref="source:b"))
    removed = _build("long_bias", None)

    with_record = _single_record(with_outcome)
    source_record = _single_record(source_only_changed)
    removed_record = _single_record(removed)

    assert source_record["hit_label"] == with_record["hit_label"]
    assert source_record["observed_return_bps"] == with_record["observed_return_bps"]
    assert source_record["observed_direction"] == with_record["observed_direction"]
    assert source_record["outcome_source_ref"] == "source:b"

    assert removed_record["hit_label"] == "not_evaluable"
    assert removed_record["not_evaluable_reason"] == "outcome_window_missing"
    assert removed_record["outcome_available"] is False
    assert removed["evaluated_record_count"] == 0
    assert removed["not_evaluable_count"] == 1
    assert removed["read_only"] is True
    assert removed["non_executing"] is True
    assert removed["would_write_runtime_artifact"] is False
    assert removed["would_send_to_broker"] is False
    assert removed["command_ledger_append_requested"] is False
    assert removed["autotrade_decision_append_requested"] is False


def test_ps_p7_order_invariance_for_aggregate_counts_and_execution_flags() -> None:
    from btcts.prediction import build_prediction_evaluation_report

    records = [
        _record("a", "long_bias", confidence="high", caution="low"),
        _record("b", "short_bias", confidence="low", caution="medium"),
    ]
    outcomes = {
        "trend_bias:300": _outcome(10_000_000, 10_010_000),
        "prediction:b": _outcome(10_000_000, 9_990_000),
    }
    # This intentionally uses two records with the same family/horizon. The current lookup order
    # prefers family:horizon when present, so this guard only checks aggregate invariants that must
    # not depend on input order, not per-record identity overrides.
    first = build_prediction_evaluation_report(
        forecast_batch={"records": records},
        outcome_windows=outcomes,
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:order:a"}},
        now=NOW,
    ).to_dict()
    second = build_prediction_evaluation_report(
        forecast_batch={"records": list(reversed(records))},
        outcome_windows=outcomes,
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:order:b"}},
        now=NOW,
    ).to_dict()
    for key in ("input_forecast_record_count", "evaluated_record_count", "not_evaluable_count", "skipped_record_count"):
        assert second[key] == first[key]
    for data in (first, second):
        assert data["read_only"] is True
        assert data["non_executing"] is True
        assert data["would_collect_public_source"] is False
        assert data["would_write_runtime_artifact"] is False
        assert data["would_send_to_broker"] is False
        assert data["broker_execution_requested"] is False
        assert data["mode_apply_requested"] is False
        assert data["command_ledger_append_requested"] is False
        assert data["autotrade_decision_append_requested"] is False


def test_ps_p7_static_boundaries_and_previous_guard_anchors() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in (EVAL, SYSTEM, RULE, FORECAST))
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
        "def _hit_label",
        "def _observed_return_bps",
        "def _direction",
        "def _predicted_direction",
        "outcome_window_missing",
        "confidence_bucket_hit_rate",
        "caution_bucket_wrong_direction_rate",
        "autotrade_decision_append_requested: bool = False",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing
    for path in (P6, P5, P4, P3):
        assert path.exists(), path
    assert "Expected-result matrix for future guards" in (ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P6_CALIBRATION_CONFIDENCE_ROADMAP_2026-06-19.md").read_text(encoding="utf-8")
    assert "test_ps_p5_summary_keys_match_ps_p2_design" in P5.read_text(encoding="utf-8")
    assert "test_ps_p4_invalid_outcome_prices_are_not_evaluable" in P4.read_text(encoding="utf-8")
    assert "test_ps_p3_builds_in_memory_evaluation_report_with_outcome" in P3.read_text(encoding="utf-8")


def test_ps_p7_files_compile() -> None:
    for path in (EVAL, SYSTEM, RULE, FORECAST, P6, P5, P4, P3, Path(__file__)):
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_p7_expected_result_matrix_long_short_and_flat_outcomes()
    test_ps_p7_price_scale_invariance()
    test_ps_p7_outcome_removal_and_source_ref_identity()
    test_ps_p7_order_invariance_for_aggregate_counts_and_execution_flags()
    test_ps_p7_static_boundaries_and_previous_guard_anchors()
    test_ps_p7_files_compile()
    print("[OK] Prediction System PS-P7 expected-result matrix / metamorphic guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
