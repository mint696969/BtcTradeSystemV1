# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_ledger_observation.py
# desc: MR-F8.11 tests for canonical point observations resolved from append-only MarketRegime trace-ledger rows.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.future_shadow_ledger_observation import (
    resolve_point_observation_from_ledger_rows,
)


def row(generated_at: str, regime: str = "RANGE", *, read_only: bool = True) -> dict:
    return {
        "artifact_kind": "trace_row",
        "event_type": "market_regime_prediction_trace",
        "generated_at": generated_at,
        "trace_id": f"trace:{generated_at}",
        "prediction_summary": {
            "horizons": [
                {"horizon_sec": 0, "regime_code": regime},
                {"horizon_sec": 300, "regime_code": "RANGE"},
            ]
        },
        "safety": {"read_only_sources": read_only},
    }


def test_selects_first_canonical_row_at_or_after_expiry() -> None:
    result = resolve_point_observation_from_ledger_rows(
        target_horizon_sec=300,
        expiry_at="2026-07-15T09:17:33Z",
        ledger_rows=[
            row("2026-07-15T09:17:20Z", "TREND_UP"),
            row("2026-07-15T09:17:40Z", "RANGE"),
            row("2026-07-15T09:18:00Z", "TREND_DOWN"),
        ],
        source_ref="ledger:09",
    )
    assert result is not None
    assert result.observed_at == "2026-07-15T09:17:40Z"
    assert result.observed_future_state.value == "RANGE"
    assert result.observation_source_ref.endswith("#trace:2026-07-15T09:17:40Z")


def test_returns_none_when_only_before_expiry_or_unknown() -> None:
    assert resolve_point_observation_from_ledger_rows(
        target_horizon_sec=300,
        expiry_at="2026-07-15T09:17:33Z",
        ledger_rows=[row("2026-07-15T09:17:20Z")],
        source_ref="ledger:09",
    ) is None
    assert resolve_point_observation_from_ledger_rows(
        target_horizon_sec=300,
        expiry_at="2026-07-15T09:17:33Z",
        ledger_rows=[row("2026-07-15T09:17:40Z", "UNKNOWN")],
        source_ref="ledger:09",
    ) is None


def test_rejects_noncanonical_safety_row() -> None:
    with pytest.raises(ValueError, match="safety_invalid"):
        resolve_point_observation_from_ledger_rows(
            target_horizon_sec=300,
            expiry_at="2026-07-15T09:17:33Z",
            ledger_rows=[row("2026-07-15T09:17:40Z", read_only=False)],
            source_ref="ledger:09",
        )


def test_current_horizon_zero_is_not_treated_as_missing() -> None:
    result = resolve_point_observation_from_ledger_rows(
        target_horizon_sec=300,
        expiry_at="2026-07-15T09:17:33Z",
        ledger_rows=[row("2026-07-15T09:17:40Z", "RANGE")],
        source_ref="ledger:09",
    )
    assert result is not None
    assert result.observed_future_state.value == "RANGE"
