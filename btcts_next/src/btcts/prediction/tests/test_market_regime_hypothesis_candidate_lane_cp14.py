# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_hypothesis_candidate_lane_cp14.py
# desc: CP14 tests for market-regime AI/GPT hypothesis candidate lane. No GPT/API call, classifier auto-apply, scheduler, broker, AutoTrade, or parameter auto-promotion.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.hypothesis_lane import (  # noqa: E402
    MARKET_REGIME_HYPOTHESIS_LANE_VERSION,
    append_market_regime_hypothesis_candidate_once,
    build_market_regime_hypothesis_candidate,
    build_market_regime_hypothesis_trust_snapshot,
    hypothesis_candidate_part_relpath,
    hypothesis_trust_latest_relpath,
    validate_market_regime_hypothesis_candidate,
    write_market_regime_hypothesis_trust_snapshot,
)


def test_cp14_hypothesis_relpaths_are_stable() -> None:
    assert hypothesis_candidate_part_relpath("2026-07-08T13:30:00Z") == "prediction/market_regime/hypotheses/candidates/date=2026-07-08/part-00001.jsonl"
    assert hypothesis_trust_latest_relpath() == "prediction/market_regime/hypotheses/trust/latest.json"


def test_cp14_build_gpt_origin_candidate_is_evidence_only() -> None:
    candidate = build_market_regime_hypothesis_candidate(
        created_at="2026-07-08T13:30:00Z",
        origin="gpt",
        title="Absorption near range edge may precede reversal watch",
        hypothesis_text="When absorption_score is high near a range boundary, mark reversal watch as a candidate instead of pure range.",
        target_regimes=["RANGE", "REVERSAL_WATCH"],
        target_horizons=["300s", "900s"],
        evidence_refs=["prediction/market_regime/calibration/date=2026-07-08/daily_summary.json"],
        proposed_signal_changes={"absorption_score": {"supports": ["RANGE", "REVERSAL_WATCH"]}},
        trust_rank=7,
    )
    assert candidate["hypothesis_lane_version"] == MARKET_REGIME_HYPOTHESIS_LANE_VERSION
    assert candidate["origin"] == "gpt"
    assert candidate["trust_state"] == "candidate"
    assert candidate["trust_rank"] == 7
    assert candidate["safety"]["evidence_only"] is True
    assert candidate["safety"]["gpt_api_call_allowed"] is False
    assert candidate["safety"]["classifier_auto_apply_allowed"] is False
    assert candidate["safety"]["parameter_auto_promotion_allowed"] is False
    assert validate_market_regime_hypothesis_candidate(candidate)["ok"] is True


def test_cp14_append_candidate_and_write_trust_snapshot(tmp_path: Path) -> None:
    candidate = build_market_regime_hypothesis_candidate(
        created_at="2026-07-08T13:31:00Z",
        origin="operator",
        title="Range confidence should be capped when source quality is weak",
        hypothesis_text="If source_quality_score is below 0.5, cap RANGE confidence even if price structure says range.",
        target_regimes=["RANGE"],
        target_horizons=["900s"],
        evidence_refs=["prediction/market_regime/outcomes/date=2026-07-08/part-00001.jsonl"],
        trust_rank=3,
    )
    result = append_market_regime_hypothesis_candidate_once(tmp_path, candidate)
    assert result["ok"] is True
    part = tmp_path / result["candidate_part_jsonl"]
    assert part.exists()
    rows = [json.loads(line) for line in part.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) == 1
    snapshot = build_market_regime_hypothesis_trust_snapshot(
        candidates=rows,
        calibration_summary={"date": "2026-07-08", "overall": {"calibration_score": 0.72}},
        generated_at="2026-07-08T13:32:00Z",
    )
    assert snapshot["candidate_count"] == 1
    assert snapshot["candidates"][0]["adjusted_trust_rank"] > snapshot["candidates"][0]["base_trust_rank"]
    assert snapshot["candidates"][0]["auto_apply_allowed"] is False
    write_result = write_market_regime_hypothesis_trust_snapshot(tmp_path, snapshot)
    assert write_result["ok"] is True
    assert (tmp_path / write_result["trust_latest_json"]).exists()


def test_cp14_trust_snapshot_downranks_when_calibration_is_weak() -> None:
    candidate = build_market_regime_hypothesis_candidate(
        created_at="2026-07-08T13:33:00Z",
        origin="model_assisted",
        title="Breakout watch from disappearing liquidity",
        hypothesis_text="Disappearing liquidity can support breakout watch when price is near range edge.",
        target_regimes=["BREAKOUT"],
        target_horizons=["300s"],
        trust_rank=10,
    )
    snapshot = build_market_regime_hypothesis_trust_snapshot(
        candidates=[candidate],
        calibration_summary={"overall": {"calibration_score": 0.2}},
        generated_at="2026-07-08T13:34:00Z",
    )
    assert snapshot["candidates"][0]["adjusted_trust_rank"] < 10
    assert snapshot["safety"]["human_gate_required_for_apply"] is True


def test_cp14_candidate_rejects_raw_payload_and_invalid_origin() -> None:
    try:
        build_market_regime_hypothesis_candidate(
            created_at="2026-07-08T13:35:00Z",
            origin="web_api",
            title="bad",
            hypothesis_text="bad",
        )
    except ValueError as exc:
        assert "unsupported hypothesis origin" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("invalid origin should fail")

    try:
        build_market_regime_hypothesis_candidate(
            created_at="2026-07-08T13:35:00Z",
            origin="gpt",
            title="bad raw",
            hypothesis_text="bad raw",
            proposed_signal_changes={"raw_orderbook": {"bids": []}},
        )
    except ValueError as exc:
        assert "forbidden raw market payload" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("raw payload should fail")


def test_cp14_validation_rejects_unsafe_flags() -> None:
    candidate = build_market_regime_hypothesis_candidate(
        created_at="2026-07-08T13:36:00Z",
        origin="manual_rule",
        title="manual candidate",
        hypothesis_text="manual candidate text",
    )
    bad = dict(candidate)
    bad["safety"] = dict(candidate["safety"])
    bad["safety"]["classifier_auto_apply_allowed"] = True
    result = validate_market_regime_hypothesis_candidate(bad)
    assert result["ok"] is False
    assert "safety_classifier_auto_apply_allowed_not_false" in result["failures"]
