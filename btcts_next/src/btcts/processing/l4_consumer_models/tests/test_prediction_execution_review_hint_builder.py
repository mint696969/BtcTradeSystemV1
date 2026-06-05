# path: ./btcts_next/src/btcts/processing/l4_consumer_models/tests/test_prediction_execution_review_hint_builder.py
# desc: Tests for read-only Execution review hint thin helper.

from __future__ import annotations

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[6]
_SRC_ROOT = _REPO_ROOT / "btcts_next" / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.processing.l4_consumer_models.shared.prediction_execution_review_hint_builder import (
    ExecutionReviewHintBuildInput,
    make_execution_review_hint,
    execution_review_hint_to_snapshot,
)


def test_execution_review_hint_helper_minimal_output() -> None:
    hint = make_execution_review_hint(
        ExecutionReviewHintBuildInput(
            scenario_ref="scenario.test",
            direction_ref="direction.test",
            position_ref="position_review_hint.test",
            market_uid="btc_jpy",
            event_ts="2026-06-05T00:00:00Z",
            evidence_trace_refs=("position:test",),
        )
    )

    assert hint.prediction_type == "execution_review_hint"
    assert hint.prediction_version == "phase4a.execution_review_hint.v1"
    assert hint.scenario_ref == "scenario.test"
    assert hint.direction_ref == "direction.test"
    assert hint.position_ref == "position_review_hint.test"
    assert hint.review_needed is True
    assert hint.diagnostics["read_only_contract"] is True
    assert hint.diagnostics["execution_side_effect_free"] is True
    assert hint.diagnostics["not_execution_instruction"] is True
    assert hint.diagnostics["broker_link_free"] is True
    assert hint.diagnostics["account_side_effect_free"] is True


def test_execution_review_hint_snapshot_is_read_only_and_layout_free() -> None:
    hint = make_execution_review_hint(
        ExecutionReviewHintBuildInput(
            scenario_ref="scenario.test",
            direction_ref="direction.test",
            position_ref="position_review_hint.test",
            execution_context_ref="execution_context.review_only.test",
            timing_hint="review_only_wait_for_confirmation",
            urgency_hint="low",
            passive_aggressive_hint="passive_review_only",
            feasibility_hint="feasible_for_review_only",
        )
    )

    snapshot = execution_review_hint_to_snapshot(hint)

    assert snapshot["prediction_type"] == "execution_review_hint"
    assert snapshot["execution_context_ref"] == "execution_context.review_only.test"
    assert snapshot["timing_hint"] == "review_only_wait_for_confirmation"
    assert snapshot["read_only_contract"] is True
    assert snapshot["not_runtime_wiring"] is True
    assert snapshot["not_replay_wiring"] is True
    assert snapshot["not_ui_wiring"] is True

    forbidden_keys = {
        "_".join(("order", "size")),
        "_".join(("order", "price")),
        "".join(("lever", "age")),
        "_".join(("broker", "account")),
        "_".join(("place", "order")),
        "_".join(("broker", "order")),
        "_".join(("live", "order", "placement")),
        "_".join(("auto", "trade")),
        "_".join(("account", "mutation")),
        "_".join(("broker", "adapter", "operation")),
        "streamlit",
        "widget",
    }
    assert forbidden_keys.isdisjoint(snapshot)


if __name__ == "__main__":
    test_execution_review_hint_helper_minimal_output()
    test_execution_review_hint_snapshot_is_read_only_and_layout_free()
    print("ok")
