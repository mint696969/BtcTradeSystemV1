# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_conditioned_pairing.py
# desc: MR-F9.18A12B guards for candidate-specific sequential conditioning in paired bridge output.

from __future__ import annotations

from pathlib import Path


def test_pair_builder_accepts_precomputed_forecasts_without_changing_slot_contract() -> None:
    source = Path(__file__).parents[1] / "future_shadow_candidate_pairing.py"
    text = source.read_text(encoding="utf-8")
    assert "precomputed_forecasts" in text
    assert "future_shadow_candidate_pair_precomputed_count_mismatch" in text
    assert '"precomputed_forecasts_used": precomputed_forecasts is not None' in text
    assert "future_shadow_candidate_pair_slot_identity_mismatch" in text
    assert "future_shadow_candidate_pair_parameter_identity_mismatch" in text


def test_runtime_bridge_keeps_candidate_specific_predecessor_state() -> None:
    source = Path(__file__).parents[1] / "future_shadow_runtime_preflight_bridge.py"
    text = source.read_text(encoding="utf-8")
    assert "predecessor_scores_by_candidate" in text
    assert "predecessor_forecast_by_candidate" in text
    assert "candidate.transition_prior_fraction_of_top" in text
    assert "precomputed_forecasts=tuple(conditioned_forecasts)" in text
    assert '"horizon_conditioning": dict(conditioning)' in text


def test_runtime_bridge_remains_read_only_and_non_promoting() -> None:
    source = Path(__file__).parents[1] / "future_shadow_runtime_preflight_bridge.py"
    text = source.read_text(encoding="utf-8")
    for marker in (
        '"writer_invoked": False',
        '"writes_dhot": False',
        '"scheduler_enabled": False',
        '"auto_promotion_allowed": False',
        '"live_parameter_apply_allowed": False',
        '"canonical_replacement_allowed": False',
    ):
        assert marker in text
