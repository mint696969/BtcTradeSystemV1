# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_transition_persistence_sequence.py
# desc: MR-F4 regression for persisted previous-state sequences across continued, held, transitioned, and invalid-transition decisions.
from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.current_state_persistence import (  # noqa: E402
    build_persisted_current_state,
    read_persisted_current_state,
    write_persisted_current_state,
)
from btcts.prediction.market_regime.parameter_set import (  # noqa: E402
    build_default_market_regime_parameter_set,
)
from btcts.prediction.market_regime.transition_policy import (  # noqa: E402
    evaluate_market_regime_transition,
)


def _persist_range_sequence(tmp_path: Path) -> tuple[dict, dict]:
    started = build_persisted_current_state(
        previous={},
        regime_code="RANGE",
        observed_at="2026-07-12T04:00:00Z",
        estimator_version="mr_f4_test",
        source_cutoff_time="2026-07-12T04:00:00Z",
    )
    first_write = write_persisted_current_state(tmp_path, started)
    assert first_write["ok"] is True
    first = read_persisted_current_state(tmp_path)

    continued = build_persisted_current_state(
        previous=first,
        regime_code="RANGE",
        observed_at="2026-07-12T04:10:00Z",
        estimator_version="mr_f4_test",
        source_cutoff_time="2026-07-12T04:10:00Z",
    )
    second_write = write_persisted_current_state(tmp_path, continued)
    assert second_write["ok"] is True
    second = read_persisted_current_state(tmp_path)
    return first, second


def test_mr_f4_persisted_same_state_preserves_start_and_age(tmp_path: Path) -> None:
    first, second = _persist_range_sequence(tmp_path)
    assert first["persistence_status"] == "started"
    assert first["state_age_sec"] == 0
    assert second["persistence_status"] == "continued"
    assert second["state_started_at"] == first["state_started_at"]
    assert second["state_age_sec"] == 600
    assert second["transition_detected"] is False
    assert second["would_send_to_broker"] is False


def test_mr_f4_policy_continues_same_persisted_state(tmp_path: Path) -> None:
    _, previous = _persist_range_sequence(tmp_path)
    result = evaluate_market_regime_transition(
        previous_regime=previous["regime_code"],
        candidate_regime="RANGE",
        previous_state_age_sec=previous["state_age_sec"],
        candidate_score=0.72,
        runner_up_score=0.69,
        change_point_evidence_score=0.10,
        parameter_set=build_default_market_regime_parameter_set(),
    )
    assert result["decision"] == "continued"
    assert result["accepted_regime"] == "RANGE"
    assert result["blockers"] == []
    assert result["label_selection_applied"] is False


def test_mr_f4_policy_holds_for_dwell_and_hysteresis(tmp_path: Path) -> None:
    _, previous = _persist_range_sequence(tmp_path)
    result = evaluate_market_regime_transition(
        previous_regime=previous["regime_code"],
        candidate_regime="LOW_VOL_COMPRESSION",
        previous_state_age_sec=120,
        candidate_score=0.74,
        runner_up_score=0.70,
        change_point_evidence_score=0.20,
        parameter_set=build_default_market_regime_parameter_set(),
    )
    assert result["decision"] == "held"
    assert result["accepted_regime"] == "RANGE"
    assert "minimum_dwell_not_satisfied" in result["blockers"]
    assert "hysteresis_margin_not_satisfied" in result["blockers"]
    assert result["label_selection_applied"] is False


def test_mr_f4_policy_transitions_after_dwell_and_margin(tmp_path: Path) -> None:
    _, previous = _persist_range_sequence(tmp_path)
    result = evaluate_market_regime_transition(
        previous_regime=previous["regime_code"],
        candidate_regime="LOW_VOL_COMPRESSION",
        previous_state_age_sec=previous["state_age_sec"],
        candidate_score=0.82,
        runner_up_score=0.66,
        change_point_evidence_score=0.20,
        parameter_set=build_default_market_regime_parameter_set(),
    )
    assert result["decision"] == "transitioned"
    assert result["accepted_regime"] == "LOW_VOL_COMPRESSION"
    assert result["transition_allowed"] is True
    assert result["dwell_satisfied"] is True
    assert result["hysteresis_satisfied"] is True
    assert result["blockers"] == []
    assert result["label_selection_applied"] is False


def test_mr_f4_invalid_transition_remains_held_with_change_point(tmp_path: Path) -> None:
    _, previous = _persist_range_sequence(tmp_path)
    result = evaluate_market_regime_transition(
        previous_regime=previous["regime_code"],
        candidate_regime="PANIC_SPIKE",
        previous_state_age_sec=previous["state_age_sec"],
        candidate_score=0.95,
        runner_up_score=0.50,
        change_point_evidence_score=0.99,
        parameter_set=build_default_market_regime_parameter_set(),
    )
    assert result["decision"] == "held"
    assert result["accepted_regime"] == "RANGE"
    assert result["transition_allowed"] is False
    assert result["change_point_override_applied"] is True
    assert "invalid_transition" in result["blockers"]
    assert result["would_send_to_broker"] is False
