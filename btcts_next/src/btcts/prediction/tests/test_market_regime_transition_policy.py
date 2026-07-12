# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_transition_policy.py
# desc: MR-F4 guards minimum dwell, hysteresis, transition matrix, change-point override, invalid transition, and persistence probability semantics.
from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime.parameter_set import (  # noqa: E402
    build_default_market_regime_parameter_set,
)
from btcts.prediction.market_regime.transition_policy import (  # noqa: E402
    evaluate_market_regime_transition,
)


def _evaluate(**overrides):
    values = {
        "previous_regime": "RANGE",
        "candidate_regime": "LOW_VOL_COMPRESSION",
        "previous_state_age_sec": 600,
        "candidate_score": 0.80,
        "runner_up_score": 0.60,
        "change_point_evidence_score": 0.20,
        "parameter_set": build_default_market_regime_parameter_set(),
    }
    values.update(overrides)
    return evaluate_market_regime_transition(**values)


def test_same_state_continues_without_transition_penalty() -> None:
    result = _evaluate(candidate_regime="RANGE", candidate_score=0.70, runner_up_score=0.69)
    assert result["decision"] == "continued"
    assert result["accepted_regime"] == "RANGE"
    assert result["same_state"] is True
    assert result["blockers"] == []
    assert result["label_selection_applied"] is False


def test_valid_transition_requires_dwell_and_hysteresis() -> None:
    result = _evaluate()
    assert result["decision"] == "transitioned"
    assert result["accepted_regime"] == "LOW_VOL_COMPRESSION"
    assert result["transition_allowed"] is True
    assert result["dwell_satisfied"] is True
    assert result["hysteresis_satisfied"] is True
    assert result["blockers"] == []


def test_minimum_dwell_holds_previous_state() -> None:
    result = _evaluate(previous_state_age_sec=120)
    assert result["decision"] == "held"
    assert result["accepted_regime"] == "RANGE"
    assert "minimum_dwell_not_satisfied" in result["blockers"]


def test_hysteresis_holds_narrow_margin() -> None:
    result = _evaluate(candidate_score=0.70, runner_up_score=0.66)
    assert result["decision"] == "held"
    assert result["accepted_regime"] == "RANGE"
    assert "hysteresis_margin_not_satisfied" in result["blockers"]


def test_change_point_override_can_bypass_dwell_and_hysteresis() -> None:
    result = _evaluate(
        previous_state_age_sec=30,
        candidate_score=0.70,
        runner_up_score=0.68,
        change_point_evidence_score=0.95,
    )
    assert result["decision"] == "transitioned"
    assert result["change_point_override_applied"] is True
    assert result["blockers"] == []


def test_invalid_transition_is_blocked_even_with_change_point() -> None:
    result = _evaluate(
        previous_regime="RANGE",
        candidate_regime="PANIC_SPIKE",
        change_point_evidence_score=0.99,
    )
    assert result["decision"] == "held"
    assert result["accepted_regime"] == "RANGE"
    assert "invalid_transition" in result["blockers"]


def test_unknown_candidate_fails_closed() -> None:
    result = _evaluate(candidate_regime="UNKNOWN")
    assert result["decision"] == "unknown"
    assert result["accepted_regime"] == "UNKNOWN"
    assert "candidate_regime_unknown" in result["blockers"]


def test_persistence_probability_is_bounded_and_uncalibrated() -> None:
    result = _evaluate()
    assert 0.0 <= result["persistence_probability"] <= 1.0
    assert result["persistence_probability_calibrated"] is False
    assert result["would_send_to_broker"] is False
