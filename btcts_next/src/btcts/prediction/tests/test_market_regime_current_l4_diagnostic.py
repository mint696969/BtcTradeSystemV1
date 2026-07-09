# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_current_l4_diagnostic.py
# desc: Tests for compact current-L4 diagnostic evidence digest. No raw candle payload emission.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime import FeatureGroup  # noqa: E402
from btcts.prediction.market_regime.features.feature_bundle import FeatureSignal, MarketRegimeFeatureBundle  # noqa: E402
from btcts.prediction.market_regime.inference.current_l4_diagnostic import build_current_l4_candle_evidence_digest  # noqa: E402


def _signal(group: FeatureGroup, name: str, value, *, available: bool = True) -> FeatureSignal:
    return FeatureSignal(
        feature_group=group,
        name=name,
        value=value,
        available=available,
        source_refs=("data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s/closed.jsonl",),
        warnings=("forecast_records_stale",) if group == FeatureGroup.PRICE_STRUCTURE else (),
    )


def test_mr_a3_current_l4_evidence_digest_is_summary_only() -> None:
    bundle = MarketRegimeFeatureBundle(
        generated_at="2026-07-09T01:30:00Z",
        source_snapshot_ok=True,
        signals=(
            _signal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_current_enough", True),
            _signal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_age_sec", 30),
            _signal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_generated_at", "2026-07-09T01:29:30Z"),
            _signal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_window_available", True),
            _signal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_window_candle_count", 60),
            _signal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_window_first_ts", "2026-07-09T00:30:00Z"),
            _signal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_window_last_ts", "2026-07-09T01:29:00Z"),
            _signal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 31.5),
            _signal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_range_bps", 52.0),
            _signal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_close_position", 0.82),
            _signal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "UP_TREND"),
            _signal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_reason", "current_l4_positive_net_change_dominates_window"),
            _signal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 4.2),
            _signal(FeatureGroup.VOLATILITY, "current_l4_candle_average_range_bps", 7.1),
            _signal(FeatureGroup.VOLATILITY, "current_l4_candle_window_range_bps", 52.0),
        ),
        coverage=(),
    )
    digest = build_current_l4_candle_evidence_digest(bundle)
    assert digest["evidence_kind"] == "current_l4_candle_window_summary"
    assert digest["raw_candle_payload_included"] is False
    assert digest["window_current_enough"] is True
    assert digest["regime_hint"] == "UP_TREND"
    assert digest["net_change_bps"] == 31.5
    assert digest["realized_volatility_bps"] == 4.2
    assert digest["source_refs"]
    assert "forecast_records_stale" in digest["warnings"]
    assert "open" not in digest
    assert "high" not in digest
    assert "low" not in digest
    assert "close" not in digest
