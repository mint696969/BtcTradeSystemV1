# path: ./btcts_next/src/btcts/prediction/tests/test_prediction_inference_bundle_local_blockers.py
# desc: Output-local blockers remain visible without incorrectly blocking the entire Prediction System bundle.

from __future__ import annotations

from datetime import datetime, timezone

from btcts.prediction.bundle_assembly import build_inference_bundle_from_outputs
from btcts.prediction.contracts import (
    ParameterSetIdentity,
    PredictionConfidence,
    PredictionFamily,
    PredictionOutput,
    SourceIdentity,
)
from btcts.prediction.horizons import horizon_by_seconds


def _output(*, blocker: str | None = None, horizon_sec: int = 21600) -> PredictionOutput:
    return PredictionOutput(
        prediction_id=f"test:{horizon_sec}:{blocker or 'ok'}",
        generated_at="2026-07-10T14:34:26Z",
        family=PredictionFamily.MARKET_REGIME,
        horizon=horizon_by_seconds(horizon_sec),
        parameter_set=ParameterSetIdentity(
            parameter_set_id="test-market-regime",
            parameter_family="market_regime",
            version="test",
        ),
        sources=(
            SourceIdentity(
                source_id="ohlcv_6h",
                source_family="ohlcv_technical_evidence",
            ),
        ),
        confidence=PredictionConfidence.UNKNOWN if blocker else PredictionConfidence.MEDIUM,
        primary_label="unknown" if blocker else "range_candidate",
        score=None if blocker else 0.52,
        blockers=(blocker,) if blocker else (),
    )


def test_exact_horizon_history_blocker_is_output_local_not_bundle_fatal() -> None:
    blocked = _output(blocker="insufficient_exact_horizon_candles")
    healthy = _output(horizon_sec=300)

    bundle = build_inference_bundle_from_outputs(
        (blocked, healthy),
        now=datetime(2026, 7, 10, 14, 34, 26, tzinfo=timezone.utc),
    )

    assert blocked.blockers == ("insufficient_exact_horizon_candles",)
    assert bundle.blockers == ()
    assert bundle.blockers == ()
    assert bundle.source_quality_summary["output_local_blocker_count"] == 1
    assert bundle.source_quality_summary["output_local_blockers"] == [
        {
            "family": "market_regime",
            "horizon_sec": 21600,
            "blocker": "insufficient_exact_horizon_candles",
            "scope": "output_local",
        }
    ]
    assert bundle.source_quality_summary["bundle_fatal_output_blockers"] == []


def test_unknown_output_blocker_remains_bundle_fatal() -> None:
    blocked = _output(blocker="unexpected_prediction_input_failure")

    bundle = build_inference_bundle_from_outputs(
        (blocked,),
        now=datetime(2026, 7, 10, 14, 34, 26, tzinfo=timezone.utc),
    )

    assert bundle.blockers == ("unexpected_prediction_input_failure",)
    assert bundle.blockers == ("unexpected_prediction_input_failure",)
    assert bundle.source_quality_summary["output_local_blocker_count"] == 0
    assert bundle.source_quality_summary["bundle_fatal_output_blockers"] == [
        "unexpected_prediction_input_failure"
    ]


def test_empty_bundle_remains_fatal() -> None:
    bundle = build_inference_bundle_from_outputs(
        (),
        now=datetime(2026, 7, 10, 14, 34, 26, tzinfo=timezone.utc),
    )

    assert bundle.blockers == ("prediction_outputs_missing",)
    assert bundle.blockers == ("prediction_outputs_missing",)
