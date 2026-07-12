# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_shadow_source_batch.py
# desc: MR-F5.14 exact source-batch producer and observation-window tests.

from __future__ import annotations

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import FutureBaselineEvidence, forecast_future_market_regime_baseline
from btcts.prediction.market_regime.future_shadow_outcome import FutureShadowOutcomeEvidence
from btcts.prediction.market_regime.future_shadow_source_batch import (
    FutureShadowObservationWindow,
    build_market_regime_future_shadow_source_batch,
)
from btcts.prediction.market_regime.future_trace_identity import build_market_regime_future_trace_identity


def _trace(horizon: int = 300):
    forecast = forecast_future_market_regime_baseline(FutureBaselineEvidence(
        origin_timestamp="2026-07-12T00:00:00Z",
        origin_current_state=MarketRegimeCode.LOW_VOL_COMPRESSION,
        target_horizon_sec=horizon,
        feature_snapshot_ref="snapshot:mr-f5.14",
        regime_scores={MarketRegimeCode.BREAKOUT: 0.8, MarketRegimeCode.RANGE: 0.2},
        available_feature_families=(
            "price_structure", "volatility", "liquidity", "microprice",
            "source_quality", "session_context",
        ),
        source_timestamp_epoch_sec=100.0,
        origin_timestamp_epoch_sec=100.0,
    ))
    return build_market_regime_future_trace_identity(forecast)


def _window(minimum: int = 1):
    return FutureShadowObservationWindow(
        window_id="window:mr-f5.14:test",
        opened_at="2026-07-12T00:00:00Z",
        evaluated_at="2026-07-12T07:00:00Z",
        source_role="hot_data_root",
        source_refs=("prediction/market_regime/future_shadow/source",),
        minimum_resolved_rows=minimum,
    )


def _evidence(trace, *, observed=MarketRegimeCode.BREAKOUT, available=True, resolved_at=None, observed_at=None):
    return FutureShadowOutcomeEvidence(
        resolved_at=resolved_at or trace.expiry_at,
        observation_available=available,
        observed_at=(observed_at or trace.expiry_at) if available else "",
        observed_future_state=observed if available else MarketRegimeCode.UNKNOWN,
        observation_source_ref="derived:closed-candle" if available else "",
    )


def test_exact_rows_are_produced_in_deterministic_trace_order() -> None:
    traces = (_trace(900), _trace(300))
    evidence = {item.trace_id: _evidence(item) for item in traces}
    result = build_market_regime_future_shadow_source_batch(
        traces=traces, evidence_by_trace_id=evidence, observation_window=_window(minimum=2)
    )
    assert result["observation_window_ready"] is True
    assert result["write_approval_candidate"] is True
    assert result["exact_row_count"] == 2
    assert tuple(row["trace_id"] for row in result["rows"]) == tuple(sorted(item.trace_id for item in traces))
    assert all(row["schema_version"] == "prediction.market_regime.future_shadow_outcome.mr_f5_6.v1" for row in result["rows"])


def test_missing_evidence_blocks_write_approval_candidate() -> None:
    trace = _trace()
    result = build_market_regime_future_shadow_source_batch(
        traces=(trace,), evidence_by_trace_id={}, observation_window=_window()
    )
    assert result["write_approval_candidate"] is False
    assert "trace_evidence_missing" in result["blockers"]


def test_unexpired_or_unavailable_observation_is_not_emitted() -> None:
    trace = _trace()
    unexpired = _evidence(
        trace,
        resolved_at="2026-07-12T00:04:59Z",
        observed_at="2026-07-12T00:04:59Z",
    )
    result = build_market_regime_future_shadow_source_batch(
        traces=(trace,), evidence_by_trace_id={trace.trace_id: unexpired}, observation_window=_window()
    )
    assert result["exact_row_count"] == 0
    assert result["status_counts"]["UNRESOLVED"] == 1
    unavailable = build_market_regime_future_shadow_source_batch(
        traces=(trace,), evidence_by_trace_id={trace.trace_id: _evidence(trace, available=False)}, observation_window=_window()
    )
    assert unavailable["exact_row_count"] == 0


def test_incorrect_outcome_is_still_exact_evidence_row() -> None:
    trace = _trace()
    result = build_market_regime_future_shadow_source_batch(
        traces=(trace,),
        evidence_by_trace_id={trace.trace_id: _evidence(trace, observed=MarketRegimeCode.PANIC_SPIKE)},
        observation_window=_window(),
    )
    assert result["exact_row_count"] == 1
    assert result["rows"][0]["outcome_status"] == "INCORRECT"


def test_unknown_evidence_trace_and_duplicate_trace_fail_closed() -> None:
    trace = _trace()
    with pytest.raises(ValueError, match="future_shadow_source_batch_unknown_evidence_trace"):
        build_market_regime_future_shadow_source_batch(
            traces=(trace,), evidence_by_trace_id={"unknown": _evidence(trace)}, observation_window=_window()
        )
    with pytest.raises(ValueError, match="future_shadow_source_batch_trace_duplicate"):
        build_market_regime_future_shadow_source_batch(
            traces=(trace, trace), evidence_by_trace_id={trace.trace_id: _evidence(trace)}, observation_window=_window()
        )


def test_observation_window_validates_role_time_and_threshold() -> None:
    with pytest.raises(ValueError, match="future_shadow_source_window_role_invalid"):
        FutureShadowObservationWindow(
            window_id="x", opened_at="2026-07-12T00:00:00Z", evaluated_at="2026-07-12T01:00:00Z",
            source_role="D:/btc_ts_hot", source_refs=("x",), minimum_resolved_rows=1,
        )
    with pytest.raises(ValueError, match="future_shadow_source_window_time_order_invalid"):
        FutureShadowObservationWindow(
            window_id="x", opened_at="2026-07-12T02:00:00Z", evaluated_at="2026-07-12T01:00:00Z",
            source_role="hot_data_root", source_refs=("x",), minimum_resolved_rows=1,
        )


def test_trace_and_evidence_must_be_inside_observation_window() -> None:
    trace = _trace()
    late_window = FutureShadowObservationWindow(
        window_id="late", opened_at="2026-07-12T01:00:00Z",
        evaluated_at="2026-07-12T07:00:00Z", source_role="hot_data_root",
        source_refs=("x",), minimum_resolved_rows=1,
    )
    with pytest.raises(ValueError, match="future_shadow_source_trace_outside_window"):
        build_market_regime_future_shadow_source_batch(
            traces=(trace,), evidence_by_trace_id={trace.trace_id: _evidence(trace)},
            observation_window=late_window,
        )
    early_window = FutureShadowObservationWindow(
        window_id="early", opened_at="2026-07-12T00:00:00Z",
        evaluated_at="2026-07-12T00:04:59Z", source_role="hot_data_root",
        source_refs=("x",), minimum_resolved_rows=1,
    )
    with pytest.raises(ValueError, match="future_shadow_source_evidence_after_window"):
        build_market_regime_future_shadow_source_batch(
            traces=(trace,), evidence_by_trace_id={trace.trace_id: _evidence(trace)},
            observation_window=early_window,
        )


def test_result_is_immutable_and_never_performs_io() -> None:
    trace = _trace()
    result = build_market_regime_future_shadow_source_batch(
        traces=(trace,), evidence_by_trace_id={trace.trace_id: _evidence(trace)}, observation_window=_window()
    )
    assert result["safety"]["writes_dhot"] is False
    with pytest.raises(TypeError): result["write_approval_candidate"] = False
    with pytest.raises(TypeError): result["safety"]["writes_dhot"] = True
