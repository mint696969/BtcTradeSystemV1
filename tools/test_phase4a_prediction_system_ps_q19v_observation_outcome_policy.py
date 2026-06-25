# path: ./tools/test_phase4a_prediction_system_ps_q19v_observation_outcome_policy.py
# desc: Focused guard for PS-Q19V read-only bounded observation outcome classifier.

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.classify_prediction_observation_outcome_ps_q19v import classify_prediction_observation_outcome  # noqa: E402

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19V_OBSERVATION_OUTCOME_POLICY_2026-06-25.md"
TOOL = REPO_ROOT / "tools/classify_prediction_observation_outcome_ps_q19v.py"

REQUIRED_MARKERS = (
    "ps_q19v_observation_outcome_policy=true",
    "classifies_bounded_observation_outcome=true",
    "partial_success_with_market_quality_block_supported=true",
    "read_only_classifier=true",
)
FALSE_BOUNDARIES = (
    "runtime_artifact_write_performed_by_classifier=false",
    "status_artifact_write_performed_by_classifier=false",
    "prediction_artifact_write_performed_by_classifier=false",
    "view_artifact_write_performed_by_classifier=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _partial_producer() -> dict:
    return {
        "ok": False,
        "cycle_count": 8,
        "requested_max_cycles": 12,
        "effective_max_cycles": 12,
        "latest_prediction_artifact_written_count": 7,
        "status_artifact_written_count": 8,
        "request_state": "periodic_producer_cycle_blocked",
        "blocked_reasons": [
            "market_overview_trust_state_not_trusted",
            "market_overview_interpretation_bucket_not_allow_structural_use",
            "actual_export_runner_did_not_write_latest_prediction_artifact",
        ],
        "cycle_packets": [
            {"cycle_index": i, "latest_prediction_artifact_written": True, "status_artifact_written": True, "generated_at": f"2026-06-25T11:{29 + i * 5:02d}:13Z", "blocked_reasons": []}
            for i in range(7)
        ] + [
            {"cycle_index": 7, "latest_prediction_artifact_written": False, "status_artifact_written": True, "generated_at": "", "blocked_reasons": ["market_overview_trust_state_not_trusted", "market_overview_interpretation_bucket_not_allow_structural_use"]}
        ],
        "scheduler_enabled": False,
        "warroom_ui_trigger_enabled": False,
        "would_send_to_broker": False,
    }


def _review() -> dict:
    return {
        "ok": True,
        "prediction_generated_at": "2026-06-25T11:59:14Z",
        "review_row_count": 35,
        "actual_available_row_count": 28,
        "actual_by_horizon": {
            "15": {"available": True, "actual_quality_ok": True, "actual_quality_reasons": [], "realized_direction": "flat"},
            "60": {"available": True, "actual_quality_ok": True, "actual_quality_reasons": [], "realized_direction": "up"},
            "300": {"available": False, "actual_quality_ok": False, "actual_quality_reasons": ["market_point_not_trusted", "market_point_not_structural_use", "market_point_negative_spread", "market_point_crossed_book"], "realized_direction": "unavailable"},
            "600": {"available": True, "actual_quality_ok": True, "actual_quality_reasons": [], "realized_direction": "down"},
            "900": {"available": True, "actual_quality_ok": True, "actual_quality_reasons": [], "realized_direction": "down"},
        },
        "warning_reasons": ["actual_market_point_quality_rejected:300:market_point_not_trusted"],
        "read_only_review": True,
        "would_send_to_broker": False,
    }


def _summary() -> dict:
    return {
        "ok": True,
        "source_review_count": 2,
        "review_row_total": 70,
        "actual_available_row_total": 63,
        "actual_available_ratio": 0.9,
        "window_summaries": [
            {"quality_rejected_horizons": [], "warning_reasons": []},
            {"quality_rejected_horizons": ["300"], "warning_reasons": ["actual_market_point_quality_rejected:300:market_point_not_trusted"]},
        ],
        "horizon_direction_summary": {"15": {"flat": 2}, "60": {"flat": 1, "up": 1}, "300": {"down": 1, "unavailable": 1}, "600": {"down": 2}, "900": {"down": 2}},
        "read_only_summary": True,
        "would_send_to_broker": False,
    }


def test_spec_declares_outcome_policy_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_partial_success_with_market_quality_block_is_accepted_for_review() -> None:
    packet = classify_prediction_observation_outcome(producer_packet=_partial_producer(), review_packet=_review(), summary_packet=_summary())
    assert packet["ok"] is True
    assert packet["outcome_class"] == "partial_success_with_market_quality_block"
    assert packet["recommendation"] == "accept_successful_cycles_for_review_and_record_quality_block_separately"
    assert packet["producer_cycle_summary"]["latest_prediction_artifact_written_count"] == 7
    assert packet["producer_block_reason_summary"]["market_overview_quality_block_present"] is True
    assert packet["review_quality_summary"]["review_usable"] is True
    assert packet["review_quality_summary"]["quality_rejected_horizons"] == ["300"]
    assert packet["multi_review_summary"]["summary_usable"] is True
    assert packet["policy_decision"]["partial_success_can_be_accepted_for_review"] is True
    assert packet["scheduler_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_blocked_without_success_is_not_usable_observation() -> None:
    producer = _partial_producer()
    producer["latest_prediction_artifact_written_count"] = 0
    producer["cycle_packets"] = [{"cycle_index": 0, "latest_prediction_artifact_written": False, "blocked_reasons": ["market_overview_trust_state_not_trusted"]}]
    packet = classify_prediction_observation_outcome(producer_packet=producer)
    assert packet["outcome_class"] == "blocked_without_success"
    assert packet["policy_decision"]["partial_success_can_be_accepted_for_review"] is False


def test_missing_packets_blocks_classifier() -> None:
    packet = classify_prediction_observation_outcome()
    assert packet["ok"] is False
    assert "observation_packets_missing" in packet["blocked_reasons"]


def test_tool_has_no_write_or_execution_behavior() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "append_jsonl(",
        "write_canonical(",
        "write_raw(",
        "place_order(",
        "send_order(",
        "build_ps_q19k_periodic_producer_packet(",
        "build_prediction_warroom_bounded_manual_refresh_runner(",
        "would_send_to_broker: bool = True",
    )
    for token in forbidden:
        assert token not in text, token
    assert "read_only_classifier" in text
    assert "runtime_artifact_write_performed_by_classifier" in text


if __name__ == "__main__":
    test_spec_declares_outcome_policy_boundaries()
    test_partial_success_with_market_quality_block_is_accepted_for_review()
    test_blocked_without_success_is_not_usable_observation()
    test_missing_packets_blocks_classifier()
    test_tool_has_no_write_or_execution_behavior()
    print('{"ok": true}')
