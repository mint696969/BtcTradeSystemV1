# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_parameter_set_review_packet.py
# desc: PS_PARAMETER_SET_REVIEW_PACKET_V1 tests. Verifies human/GPT parameter-set review packet is evidence-only and cannot apply parameters.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.parameter_set_comparison_read_model import build_market_regime_parameter_set_comparison_read_model_from_outcome_rows  # noqa: E402
from btcts.prediction.market_regime.parameter_set_review_packet import (  # noqa: E402
    MARKET_REGIME_PARAMETER_SET_REVIEW_PACKET_VERSION,
    build_market_regime_parameter_set_review_packet,
    validate_market_regime_parameter_set_review_packet,
)


def _row(parameter_set_id: str, label: str, *, source: str = "candle_summary", confidence: int = 70, observed: str = "RANGE") -> dict[str, object]:
    return {
        "outcome_id": f"run:300s:{parameter_set_id}:{label}",
        "run_id": "run",
        "generated_at": "2026-07-08T12:00:00Z",
        "resolved_at": "2026-07-08T12:05:00Z",
        "horizon_key": "300s",
        "horizon_sec": 300,
        "predicted_regime_code": "RANGE",
        "observed_regime_code": observed,
        "outcome_label": label,
        "observation_source": source,
        "confidence_percent": confidence,
        "parameter_set_id": parameter_set_id,
        "trace_part_jsonl": "prediction/market_regime/ledgers/date=2026-07-08/hour=12/part-00001.jsonl",
    }


def test_ps_parameter_set_review_packet_marks_single_set_not_comparable_without_autopromotion() -> None:
    comparison = build_market_regime_parameter_set_comparison_read_model_from_outcome_rows(
        rows=[_row("market_regime_engine_parameter_set.v1", "hit"), _row("market_regime_engine_parameter_set.v1", "miss", observed="DOWN_TREND")],
        active_parameter_set_id="market_regime_engine_parameter_set.v1",
        min_trusted_samples=1,
    )

    packet = build_market_regime_parameter_set_review_packet(comparison)

    assert packet["review_packet_version"] == MARKET_REGIME_PARAMETER_SET_REVIEW_PACKET_VERSION
    assert packet["artifact_kind"] == "parameter_set_review_packet"
    assert packet["reviewer_lane"] == "human_gpt_review_loop"
    assert packet["review_state"] == "not_comparable_single_trusted_parameter_set"
    assert packet["comparison_ready"] is False
    assert packet["evidence_summary"]["trusted_row_count"] == 2
    assert packet["evidence_summary"]["trusted_parameter_set_count"] == 1
    assert packet["evidence_summary"]["promotion_candidate_count"] == 0
    assert packet["promotion_candidates"] == []
    assert packet["decision_options"][-1]["decision"] == "open_promotion_or_rollback_review"
    assert packet["decision_options"][-1]["enabled"] is False
    assert packet["safety"]["writes_dhot"] is False
    assert packet["safety"]["parameter_auto_promotion_allowed"] is False
    assert packet["safety"]["live_parameter_apply_allowed"] is False
    assert validate_market_regime_parameter_set_review_packet(packet)["ok"] is True


def test_ps_parameter_set_review_packet_keeps_ready_review_human_gated() -> None:
    comparison = build_market_regime_parameter_set_comparison_read_model_from_outcome_rows(
        rows=[
            _row("active.v1", "miss", observed="DOWN_TREND"),
            _row("active.v1", "hit"),
            _row("shadow.v2", "hit"),
            _row("shadow.v2", "hit"),
        ],
        active_parameter_set_id="active.v1",
        min_trusted_samples=2,
    )

    packet = build_market_regime_parameter_set_review_packet(comparison)

    assert packet["review_state"] == "comparison_ready_for_human_review"
    assert packet["comparison_ready"] is True
    assert packet["evidence_summary"]["comparable_parameter_set_count"] == 2
    assert packet["evidence_summary"]["best_visible_parameter_set"]["parameter_set_id"] == "shadow.v2"
    assert len(packet["parameter_set_evidence"]) == 2
    assert all(item["human_gate_required"] is True for item in packet["recommendations"])
    assert all(item["auto_apply_allowed"] is False for item in packet["recommendations"])
    assert all(option["auto_apply_allowed"] is False for option in packet["decision_options"])
    assert packet["decision_options"][-1]["enabled"] is True
    assert packet["safety"]["broker_private_api_allowed"] is False
    assert packet["safety"]["autotrade_trigger_allowed"] is False
    assert validate_market_regime_parameter_set_review_packet(packet)["ok"] is True


def test_ps_parameter_set_review_packet_validator_rejects_mutating_flags() -> None:
    packet = build_market_regime_parameter_set_review_packet({
        "artifact_kind": "parameter_set_comparison_read_model",
        "comparison_read_model_version": "test",
        "prediction_family_id": "market_regime",
        "comparison_ready": False,
        "comparison_blockers": ["fewer_than_two_parameter_sets_with_minimum_trusted_samples"],
        "calibration_trust": {"trusted_row_count": 0, "reference_only_row_count": 0},
        "parameter_sets": [],
        "recommendations": [],
        "promotion_candidates": [],
    })
    packet["safety"]["parameter_auto_promotion_allowed"] = True
    packet["decision_options"][0]["auto_apply_allowed"] = True
    validation = validate_market_regime_parameter_set_review_packet(packet)
    assert validation["ok"] is False
    assert "safety_parameter_auto_promotion_allowed_not_false" in validation["failures"]
    assert "decision_option_auto_apply_not_false" in validation["failures"]


def test_ps_parameter_set_review_packet_validator_rejects_raw_payload_keys() -> None:
    packet = build_market_regime_parameter_set_review_packet({
        "artifact_kind": "parameter_set_comparison_read_model",
        "comparison_read_model_version": "test",
        "prediction_family_id": "market_regime",
        "comparison_ready": False,
        "comparison_blockers": ["fewer_than_two_parameter_sets_with_minimum_trusted_samples"],
        "calibration_trust": {"trusted_row_count": 0, "reference_only_row_count": 0},
        "parameter_sets": [],
        "recommendations": [],
        "promotion_candidates": [],
    })
    packet["evidence_summary"]["raw_candles"] = []
    validation = validate_market_regime_parameter_set_review_packet(packet)
    assert validation["ok"] is False
    assert "forbidden_raw_payload_key_present" in validation["failures"]


def test_ps_parameter_set_review_packet_source_has_no_writer_or_execution_path() -> None:
    path = Path(__file__).resolve().parents[1] / "market_regime/parameter_set_review_packet.py"
    text = path.read_text(encoding="utf-8")
    required = [
        "build_market_regime_parameter_set_review_packet",
        "validate_market_regime_parameter_set_review_packet",
        "human_gpt_review_loop",
        "display_review_packet_only",
        "parameter_auto_promotion_allowed",
        "live_parameter_apply_allowed",
    ]
    assert [token for token in required if token not in text] == []
    forbidden = [
        "write_text(",
        "open(\"a",
        "write_market_regime_parameter_set_comparison_read_model(",
        "classify_market_regime_feature_bundle(",
        "build_market_regime_source_snapshot(",
        "build_market_regime_feature_bundle(",
        "subprocess.Popen",
        "broker_private_api_allowed: bool = True",
        "autotrade_trigger_allowed: bool = True",
        "order_intent_submitted: bool = True",
        "parameter_auto_promotion_allowed: bool = True",
        "live_parameter_apply_allowed: bool = True",
    ]
    assert [token for token in forbidden if token in text] == []
