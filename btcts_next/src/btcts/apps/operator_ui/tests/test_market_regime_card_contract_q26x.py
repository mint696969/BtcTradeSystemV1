# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_contract_q26x.py
# desc: PS-Q26X tests for market regime card pure-data contract helpers. No UI/runtime changes.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.contracts.market_regime_card_contract import (  # noqa: E402
    BackgroundTone,
    EvidenceQuality,
    FreshnessBadge,
    MarketRegimeCode,
    RegimeDiagnosticReason,
    ShortTag,
    build_market_regime_card_contract_report,
    build_market_regime_card_spec,
    build_unknown_market_regime_diagnostic_record,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q26x_contract_report_matches_q26w_spec() -> None:
    report = build_market_regime_card_contract_report()
    assert report["ok"] is True
    assert report["regime_codes"] == [
        "UP_TREND",
        "DOWN_TREND",
        "RANGE",
        "LOW_VOL_COMPRESSION",
        "HIGH_VOL_CHOP",
        "BREAKOUT",
        "PANIC_SPIKE",
        "REVERSAL_WATCH",
        "UNKNOWN",
    ]
    assert report["default_horizons"] == ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]
    assert report["freshness_encoded_by_badge_only"] is True
    assert report["border_meaning"] == "evidence_quality"
    assert report["confidence_max_percent"] == 99
    assert report["confidence_meaning"] == "market_regime_classification_certainty_not_win_rate"
    assert report["unknown_regime_available"] is True
    assert report["diagnostic_record_required_for_unknown_and_low_confidence"] is True
    assert report["pure_data_contract_only"] is True
    assert report["production_ui_code_changed"] is False
    assert report["warroom_page_changed"] is False
    assert report["streamlit_render_allowed"] is False
    assert report["runtime_read_allowed"] is False
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        assert report[key] is False


def test_q26x_card_spec_uses_three_lines_badge_and_evidence_border() -> None:
    card = build_market_regime_card_spec(
        horizon="現在",
        regime_code=MarketRegimeCode.UP_TREND,
        confidence_percent=101,
        background_tone=BackgroundTone.CAUTION,
        freshness_badge=FreshnessBadge.LIVE,
        evidence_quality=EvidenceQuality.STRONG,
        short_tag=ShortTag.HIGH_ZONE,
    ).to_dict()
    assert card["regime_label"] == "上昇トレンド"
    assert card["confidence_percent"] == 99
    assert card["card_lines"] == ["上昇トレンド", "99%", "高値圏"]
    assert card["background_style"]["background"] == "#FEF7C3"
    assert card["background_style"]["text"] == "#101828"
    assert card["freshness_badge"] == "LIVE"
    assert card["freshness_encoded_by_badge_only"] is True
    assert card["border_meaning"] == "evidence_quality"
    assert card["evidence_quality_style"]["label"] == "根拠良好"
    assert card["detail"]["regime_label"] == "上昇トレンド"


def test_q26x_unknown_record_preserves_improvement_reasons() -> None:
    record = build_unknown_market_regime_diagnostic_record(
        record_id="mr-unknown-1",
        created_at_utc="2026-07-01T00:00:00Z",
        horizon="15分後",
        confidence_percent="83",
        unknown_reason_codes=[RegimeDiagnosticReason.SIGNAL_CONFLICT, RegimeDiagnosticReason.WIDE_SPREAD],
        used_sources=["board", "executions"],
        missing_sources=["liquidity_context"],
        conflicting_sources=["short_term_flow", "mid_term_regime"],
        freshness_state="LIVE",
        spread_state="WIDE",
        liquidity_state="LOW",
        board_state="LIVE",
        executions_state="LIVE",
        input_snapshot_ref="snapshot://example",
    )
    card = build_market_regime_card_spec(
        horizon="15分後",
        regime_code=MarketRegimeCode.UNKNOWN,
        confidence_percent=83,
        background_tone=BackgroundTone.UNKNOWN,
        freshness_badge=FreshnessBadge.LIVE,
        evidence_quality=EvidenceQuality.CONFLICTED,
        short_tag=ShortTag.SIGNAL_CONFLICT,
        diagnostic_record=record,
    ).to_dict()
    diag = card["diagnostic_record"]
    assert card["regime_label"] == "予測不能"
    assert card["card_lines"] == ["予測不能", "83%", "シグナル割れ"]
    assert card["background_style"]["background"] == "#F2F4F7"
    assert card["evidence_quality_style"]["border_style"] == "dashed"
    assert diag["is_unknown"] is True
    assert diag["is_low_confidence"] is True
    assert diag["unknown_reason_codes"] == ["SIGNAL_CONFLICT", "WIDE_SPREAD"]
    assert diag["low_confidence_reason_codes"] == ["LOW_CONFIDENCE"]
    assert diag["missing_sources"] == ["liquidity_context"]
    assert diag["input_snapshot_ref"] == "snapshot://example"


def test_q26x_does_not_touch_warroom_page() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    assert "MARKET_REGIME_CARD_CONTRACT_VERSION" not in page_text
    assert "build_market_regime_card_spec" not in page_text
