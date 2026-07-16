# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_origin_feature_selected_window_freshness.py
# desc: MR-F9.18A11 guards that selected contiguous-window age is explicit and used as the future source timestamp.

from __future__ import annotations

from pathlib import Path


def test_runtime_bundle_declares_selected_window_freshness_fields() -> None:
    source = Path(__file__).parents[1] / "future_origin_feature_runtime_bundle.py"
    text = source.read_text(encoding="utf-8")
    for marker in (
        "selected_candle_first_timestamp",
        "selected_candle_source_timestamp",
        "selected_candle_source_age_sec",
        "selected_window_is_latest_source",
    ):
        assert marker in text
    assert '"source_timestamp": selected_candle_source_timestamp' in text


def test_preflight_prefers_selected_window_timestamp() -> None:
    source = Path(__file__).parents[1] / "tools" / "shadow_runtime_preflight_once.py"
    text = source.read_text(encoding="utf-8")
    selected = text.index('runtime_bundle.get("selected_candle_source_timestamp")')
    fallback = text.index('_signal_value(feature_bundle, "current_l4_candle_window_generated_at")', selected)
    packet = text.index("build_market_regime_future_shadow_packet", selected)
    assert selected < fallback < packet
