# path: ./btcts_next/src/btcts/replay/tests/test_replay_prediction_artifacts.py
# desc: Verify ReplayPredictionArtifactBuilder emits a prediction evaluation entry from two sequential replay results.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.replay.replay_prediction_artifacts import (  # noqa: E402
    ReplayPredictionArtifactBuilder,
)


def main() -> int:
    builder = ReplayPredictionArtifactBuilder()

    first = {
        "record_id": "row_1",
        "record_type": "market.orderbook.snapshot",
        "event_ts": "2026-04-17T04:20:00Z",
        "events": [
            {"event_name": "support_candidate"},
        ],
        "best_bid": 100.0,
        "best_ask": 102.0,
    }
    second = {
        "record_id": "row_2",
        "record_type": "market.orderbook.diff",
        "event_ts": "2026-04-17T04:25:00Z",
        "events": [
            {"event_name": "resistance_candidate"},
        ],
        "best_bid": 101.0,
        "best_ask": 103.0,
    }

    first_artifacts = builder.consume_result_artifacts(first)
    assert first_artifacts["evaluation_entry"] is None
    assert first_artifacts["calibration_review"] is None
    assert first_artifacts["tactic_proposal_output"] is None
    assert first_artifacts["tactic_review_record"] is None
    assert first_artifacts["tactic_operation_record"] is None
    assert first_artifacts["prediction_direction_snapshot"] is None

    artifacts = builder.consume_result_artifacts(second)

    entry = artifacts["evaluation_entry"]
    assert entry is not None
    assert entry["entry_type"] == "prediction_evaluation_entry"
    assert entry["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert entry["realized_horizon"] == "5m"
    assert entry["regime_alignment"] == "matched"
    assert entry["realized_return_bp"] == 99.01
    assert entry["realized_max_adverse_bp"] == 0.0
    assert entry["realized_max_favorable_bp"] == 198.02
    assert entry["diagnostics"]["caller"] == "replay_prediction_artifact_builder"
    assert entry["diagnostics"]["realized_outcome_source"] == "next_step_proxy"

    review = artifacts["calibration_review"]
    assert review is not None
    assert review["review_type"] == "prediction_calibration_review"
    assert review["review_priority"] == "normal"
    assert review["primary_focus"] == "stability_review"
    assert review["invalidation_review"] == "keep_slow_invalidation"
    assert review["followup_actions"] == ("keep_slow_invalidation",)
    assert review["diagnostics"]["caller"] == "replay_prediction_artifact_builder"
    assert review["diagnostics"]["review_source"] == "cumulative_evaluation_entries"

    tactic_proposal = artifacts["tactic_proposal_output"]
    assert tactic_proposal is not None
    assert tactic_proposal["proposal_type"] == "scenario_tactic_proposal_output"
    assert tactic_proposal["source_kind"] == "prediction_scenario_output"
    assert tactic_proposal["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert tactic_proposal["scenario_regime"] == "continuation"
    assert tactic_proposal["primary_tactic_key"] in {
        "observe_only",
        "cautious_probe",
        "continuation_follow",
        "tighten_entry_gate",
        "defensive_reduce_risk",
        "maintain_no_trade",
        "reversal_prepare",
    }

    tactic_review = artifacts["tactic_review_record"]
    assert tactic_review is not None
    assert tactic_review["review_type"] == "tactic_review_record"
    assert tactic_review["selected_tactic_key"] == tactic_proposal["primary_tactic_key"]
    assert tactic_review["decision_state"] == "proposed"
    assert tactic_review["decision_reason"] == "replay_compare_capture"
    assert tactic_review["diagnostics"]["caller"] == "replay_prediction_artifact_builder"
    assert tactic_review["diagnostics"]["review_source"] == (
        "pending_tactic_proposal_output"
    )

    direction_snapshot = artifacts["prediction_direction_snapshot"]
    assert direction_snapshot is not None
    assert direction_snapshot["prediction_type"] == "direction"
    assert direction_snapshot["source_kind"] == "replay_artifact_only"
    assert direction_snapshot["read_only_contract"] is True
    assert direction_snapshot["not_runtime_wiring"] is True
    assert direction_snapshot["not_ui_wiring"] is True
    assert direction_snapshot["diagnostics"]["artifact_only"] is True
    assert "position_size" not in direction_snapshot
    assert "order_size" not in direction_snapshot
    assert "broker_account" not in direction_snapshot

    tactic_operation = artifacts["tactic_operation_record"]
    assert tactic_operation is not None
    assert tactic_operation["operation_type"] == "tactic_operation_record"
    assert tactic_operation["operation_state"] == "propose"
    assert tactic_operation["selected_tactic_key"] == tactic_proposal["primary_tactic_key"]
    assert tactic_operation["review_ref"] == tactic_review["review_id"]
    assert tactic_operation["operation_reason"] == "replay_compare_capture"
    assert tactic_operation["diagnostics"]["caller"] == (
        "replay_prediction_artifact_builder"
    )
    assert tactic_operation["diagnostics"]["operation_source"] == (
        "pending_tactic_review_record"
    )

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())