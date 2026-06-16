# path: ./btcts_next/src/btcts/replay/tests/test_prediction_realized_outcome.py
# desc: Verify realized-outcome contract stays compact and replay-oriented.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.replay.prediction_realized_outcome import (  # noqa: E402
    PredictionRealizedOutcomeBuildInput,
    build_prediction_realized_outcome,
)


def main() -> int:
    built = build_prediction_realized_outcome(
        PredictionRealizedOutcomeBuildInput(
            market_uid="bitflyer.spot.BTC_JPY",
            event_ts="2026-04-17T04:40:00Z",
            realized_horizon="10m",
            realized_regime_state="transition",
            realized_confidence=1.2,
            realized_caution_level="high",
            realized_return_bp=-18.456,
            realized_max_adverse_bp=-22.112,
            realized_max_favorable_bp=6.889,
            diagnostics={"caller": "unit_test"},
        )
    )

    assert built["outcome_type"] == "prediction_realized_outcome"
    assert built["outcome_version"] == "phase3.v1alpha1"
    assert built["market_uid"] == "bitflyer.spot.BTC_JPY"
    assert built["event_ts"] == "2026-04-17T04:40:00Z"
    assert built["realized_horizon"] == "10m"
    assert built["realized_regime_state"] == "transition"
    assert built["realized_confidence"] == 1.0
    assert built["realized_caution_level"] == "high"
    assert built["realized_return_bp"] == -18.46
    assert built["realized_max_adverse_bp"] == -22.11
    assert built["realized_max_favorable_bp"] == 6.89
    assert built["diagnostics"]["builder_type"] == "prediction_realized_outcome"
    assert built["diagnostics"]["caller"] == "unit_test"

    empty = build_prediction_realized_outcome(
        PredictionRealizedOutcomeBuildInput()
    )
    assert empty["market_uid"] is None
    assert empty["event_ts"] is None
    assert empty["realized_horizon"] is None
    assert empty["realized_regime_state"] is None
    assert empty["realized_confidence"] is None
    assert empty["realized_caution_level"] is None
    assert empty["realized_return_bp"] is None
    assert empty["realized_max_adverse_bp"] is None
    assert empty["realized_max_favorable_bp"] is None

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())