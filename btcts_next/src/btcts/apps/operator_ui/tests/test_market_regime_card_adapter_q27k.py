# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_adapter_q27k.py
# desc: PS-Q27K tests for pure WarRoom card adapter from market-regime prediction packet. No UI mount or runtime reads.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.market_regime import (  # noqa: E402
    WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION,
    adapt_market_regime_prediction_packet_to_cards,
    build_warroom_market_regime_card_adapter_packet,
)
from btcts.prediction.market_regime import (  # noqa: E402
    EvidenceQuality,
    FreshnessState,
    MarketRegimeCode,
    MarketRegimePrediction,
    MarketRegimePredictionPacket,
    TacticalHint,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
RENDERER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
ADAPTER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/market_regime"


def _prediction(label: str, horizon: int, regime: MarketRegimeCode, confidence: int, *, missing: tuple[str, ...] = (), warnings: tuple[str, ...] = (), tactical: TacticalHint = TacticalHint.RANGE_TACTIC) -> MarketRegimePrediction:
    return MarketRegimePrediction(
        horizon_label=label,
        horizon_sec=horizon,
        regime_code=regime,
        confidence_percent=confidence,
        evidence_quality=EvidenceQuality.PARTIAL,
        freshness_state=FreshnessState.LIVE if not missing else FreshnessState.MISSING,
        tactical_hint=tactical,
        drivers=("forecast_label:range_candidate", "forecast_horizons:300,21600", "classified_regime:" + regime.value),
        warnings=warnings,
        missing_sources=missing,
        invalidation_hints=("source_quality_drops", "spread_widens_or_crosses"),
        diagnostic_record={"classifier_version": "prediction.market_regime.regime_classifier.ps_q27j.v1"},
    )


def _packet() -> MarketRegimePredictionPacket:
    return MarketRegimePredictionPacket(
        generated_at="2026-07-01T17:30:00Z",
        logic_version="prediction.market_regime.regime_classifier.ps_q27j.v1",
        predictions=(
            _prediction("現在", 0, MarketRegimeCode.RANGE, 68, warnings=("negative_spread_seen",), tactical=TacticalHint.NO_NEW_ENTRY),
            _prediction("5分後", 300, MarketRegimeCode.UP_TREND, 72, tactical=TacticalHint.TREND_FOLLOW_WATCH),
            _prediction("15分後", 900, MarketRegimeCode.UNKNOWN, 15, missing=("latest_manifest",), tactical=TacticalHint.UNKNOWN_HOLD),
        ),
    )


def test_q27k_adapter_maps_prediction_packet_to_card_contract_dicts() -> None:
    cards = adapt_market_regime_prediction_packet_to_cards(_packet())
    assert len(cards) == 3
    assert cards[0]["horizon"] == "現在"
    assert cards[0]["regime_code"] == "RANGE"
    assert cards[0]["freshness_badge"] == "LIVE"
    assert cards[0]["short_tag"] == "NO_NEW_ENTRY"
    assert cards[0]["background_tone"] == "CAUTION"
    assert cards[0]["card_lines"] == ["レンジ", "68%", "新規回避"]
    assert cards[0]["confidence_meaning"] == "market_regime_classification_certainty_not_win_rate"
    assert cards[0]["freshness_encoded_by_badge_only"] is True
    assert cards[0]["border_meaning"] == "evidence_quality"
    assert cards[0]["extra"]["adapter_version"] == WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION
    assert cards[0]["extra"]["would_send_to_broker"] is False


def test_q27k_unknown_or_missing_prediction_gets_diagnostic_record() -> None:
    cards = adapt_market_regime_prediction_packet_to_cards(_packet())
    unknown = cards[2]
    assert unknown["regime_code"] == "UNKNOWN"
    assert unknown["short_tag"] == "DATA_MISSING"
    assert unknown["freshness_badge"] == "MISSING"
    assert unknown["diagnostic_record"] is not None
    assert unknown["diagnostic_record"]["is_unknown"] is True
    assert "DATA_MISSING" in unknown["diagnostic_record"]["unknown_reason_codes"]
    assert unknown["diagnostic_record"]["missing_sources"] == ["latest_manifest"]
    assert unknown["detail"]["unknown_or_low_confidence_diagnostic_id"] == "q27k-900"


def test_q27k_adapter_packet_is_display_only_and_not_mounted() -> None:
    packet = build_warroom_market_regime_card_adapter_packet(_packet())
    assert packet["ok"] is True
    assert packet["adapter_version"] == WARROOM_MARKET_REGIME_CARD_ADAPTER_VERSION
    assert packet["card_count"] == 3
    assert packet["horizons"] == ["現在", "5分後", "15分後"]
    assert packet["market_regime_only"] is True
    assert packet["adapter_prep_only"] is True
    assert packet["display_adapter_only"] is True
    assert packet["live_data_connected"] is False
    assert packet["warroom_page_changed"] is False
    assert packet["warroom_page_mounted"] is False
    assert packet["renderer_changed"] is False
    assert packet["streamlit_render_invoked_by_page"] is False
    for key in ("runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert packet[key] is False


def test_q27k_does_not_change_page_or_renderer_mount() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    renderer_text = RENDERER.read_text(encoding="utf-8-sig")
    assert "build_warroom_market_regime_card_adapter_packet" not in page_text
    assert "adapt_market_regime_prediction_packet_to_cards" not in page_text
    assert "build_warroom_market_regime_card_adapter_packet" not in renderer_text
    assert "adapt_market_regime_prediction_packet_to_cards" not in renderer_text


def test_q27k_adapter_modules_do_not_import_streamlit_or_runtime_paths() -> None:
    forbidden = ("import streamlit", "from streamlit", "runtime_root(", "send_to_broker(", "append_ledger(", "ledger.append(", "open(\"D:")
    for path in ADAPTER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"
