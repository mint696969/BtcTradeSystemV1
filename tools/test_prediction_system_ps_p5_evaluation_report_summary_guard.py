# path: ./tools/test_prediction_system_ps_p5_evaluation_report_summary_guard.py
# desc: Guard for PS-P5 Prediction System evaluation report aggregate summary keys and boundaries.

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
P4 = ROOT / "tools" / "test_prediction_system_ps_p4_evaluation_not_evaluable_guard.py"
P3 = ROOT / "tools" / "test_prediction_system_ps_p3_evaluation_builder_skeleton_guard.py"
P2 = ROOT / "tools" / "test_prediction_system_ps_p2_evaluation_contract_design_guard.py"
PS_G = ROOT / "tools" / "test_prediction_system_ps_g_lite_runner_guard.py"


def _record(record_id: str, family: str, horizon_sec: int, label: str, confidence: str, caution: str) -> dict[str, object]:
    return {
        "record_id": record_id,
        "bundle_id": "bundle:summary",
        "generated_at": "2026-06-19T00:00:00Z",
        "prediction_id": f"prediction:{record_id}",
        "family": family,
        "horizon_sec": horizon_sec,
        "horizon_label": f"{horizon_sec}s",
        "horizon_key": f"{horizon_sec}s",
        "primary_label": label,
        "confidence": confidence,
        "score": 0.5,
        "values_snapshot": {"trigger_eligibility_state": "blocked", "caution_level": caution},
        "blockers": [],
        "warnings": [],
    }


def _outcome(family: str, horizon_sec: int, start: float, end: float, min_price: float | None = None, max_price: float | None = None) -> dict[str, object]:
    return {
        "family": family,
        "horizon_sec": horizon_sec,
        "evaluation_window_start": "2026-06-19T00:00:00Z",
        "evaluation_window_end": "2026-06-19T00:05:00Z",
        "start_price": start,
        "end_price": end,
        "min_price": min_price if min_price is not None else min(start, end),
        "max_price": max_price if max_price is not None else max(start, end),
        "source_ref": "offline_replay_fixture",
    }


def test_ps_p5_summary_keys_match_ps_p2_design() -> None:
    from btcts.prediction import build_prediction_evaluation_report

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    report = build_prediction_evaluation_report(
        forecast_batch={
            "records": [
                _record("r1", "trend_bias", 300, "long_bias", "high", "low"),
                _record("r2", "trend_bias", 600, "short_bias", "low", "medium"),
                _record("r3", "market_regime", 300, "long_bias", "high", "low"),
            ]
        },
        outcome_windows={
            "trend_bias:300": _outcome("trend_bias", 300, 10_000_000, 10_010_000, 9_990_000, 10_012_000),
            "trend_bias:600": _outcome("trend_bias", 600, 10_000_000, 10_020_000, 9_995_000, 10_025_000),
            "market_regime:300": _outcome("market_regime", 300, 10_000_000, 9_990_000, 9_985_000, 10_002_000),
        },
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:summary", "generated_at": "2026-06-19T00:00:00Z"}},
        now=now,
        source_ref="summary_fixture",
    )
    data = report.to_dict()
    assert set(data["family_summary"].keys()) == {
        "directional_hit_rate_by_family",
        "average_return_bps_by_family",
        "adverse_excursion_bps_by_family",
        "not_evaluable_count_by_family",
    }
    assert set(data["horizon_summary"].keys()) == {
        "directional_hit_rate_by_horizon",
        "average_return_bps_by_horizon",
        "adverse_excursion_bps_by_horizon",
        "not_evaluable_count_by_horizon",
    }
    assert set(data["confidence_summary"].keys()) == {
        "confidence_bucket_hit_rate",
        "confidence_bucket_average_return_bps",
        "confidence_bucket_not_evaluable_count",
    }
    assert set(data["caution_summary"].keys()) == {
        "caution_bucket_adverse_excursion",
        "caution_bucket_wrong_direction_rate",
        "caution_bucket_not_evaluable_count",
    }
    assert data["confidence_summary"]["confidence_bucket_hit_rate"]["high"] == 0.5
    assert data["confidence_summary"]["confidence_bucket_hit_rate"]["low"] == 0.0
    assert data["confidence_summary"]["confidence_bucket_not_evaluable_count"]["high"] == 0
    assert data["caution_summary"]["caution_bucket_wrong_direction_rate"]["low"] == 0.5
    assert data["caution_summary"]["caution_bucket_wrong_direction_rate"]["medium"] == 1.0
    assert data["caution_summary"]["caution_bucket_not_evaluable_count"]["low"] == 0


def test_ps_p5_missing_outcome_counts_remain_in_summary_maps() -> None:
    from btcts.prediction import build_prediction_evaluation_report

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    report = build_prediction_evaluation_report(
        forecast_batch={"records": [_record("missing", "trend_bias", 300, "long_bias", "medium", "low")]},
        outcome_windows={},
        prediction_snapshot={"run_identity": {"prediction_run_id": "run:summary_missing"}},
        now=now,
    )
    data = report.to_dict()
    assert data["evaluated_record_count"] == 0
    assert data["not_evaluable_count"] == 1
    assert data["family_summary"]["not_evaluable_count_by_family"]["trend_bias"] == 1
    assert data["horizon_summary"]["not_evaluable_count_by_horizon"]["300"] == 1
    assert data["confidence_summary"]["confidence_bucket_not_evaluable_count"]["medium"] == 1
    assert data["caution_summary"]["caution_bucket_not_evaluable_count"]["low"] == 1
    assert data["confidence_summary"]["confidence_bucket_hit_rate"]["medium"] is None
    assert data["caution_summary"]["caution_bucket_wrong_direction_rate"]["low"] is None
    assert "outcome_window_missing" in data["data_quality_notes"]
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_write_runtime_artifact"] is False
    assert data["would_send_to_broker"] is False
    assert data["autotrade_decision_append_requested"] is False


def test_ps_p5_static_boundaries_and_guard_anchors() -> None:
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
        "def _confidence_summary",
        "def _caution_summary",
        "confidence_bucket_hit_rate",
        "confidence_bucket_average_return_bps",
        "confidence_bucket_not_evaluable_count",
        "caution_bucket_adverse_excursion",
        "caution_bucket_wrong_direction_rate",
        "caution_bucket_not_evaluable_count",
        "would_write_runtime_artifact: bool = False",
        "autotrade_decision_append_requested: bool = False",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, missing
    for path in (P4, P3, P2, PS_G):
        assert path.exists(), path
    assert "test_ps_p4_invalid_outcome_prices_are_not_evaluable" in P4.read_text(encoding="utf-8")
    assert "test_ps_p3_builds_in_memory_evaluation_report_with_outcome" in P3.read_text(encoding="utf-8")
    assert "PredictionEvaluationReport required summaries" in (ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_P2_EVALUATION_CONTRACT_DESIGN_2026-06-19.md").read_text(encoding="utf-8")
    assert "test_ps_g_lite_runner_builds_prediction_system_result" in PS_G.read_text(encoding="utf-8")


def test_ps_p5_files_compile() -> None:
    for path in (EVAL, INIT, SYSTEM, RULE, P4, P3, P2, PS_G, Path(__file__)):
        assert path.exists(), path
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    test_ps_p5_summary_keys_match_ps_p2_design()
    test_ps_p5_missing_outcome_counts_remain_in_summary_maps()
    test_ps_p5_static_boundaries_and_guard_anchors()
    test_ps_p5_files_compile()
    print("[OK] Prediction System PS-P5 evaluation report summary guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
