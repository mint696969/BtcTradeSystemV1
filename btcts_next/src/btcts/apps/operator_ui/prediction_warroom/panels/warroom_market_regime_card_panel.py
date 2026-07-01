# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py
# desc: PS-Q26Y market regime card renderer shell. Static/sample UI shell only; no live data read, WarRoom page mount, runtime writes, producer/scheduler, AutoTrade, broker, ledger, mode, or parameter behavior.

from __future__ import annotations

from html import escape
from typing import Any, Iterable, Mapping

import streamlit as st

from btcts.apps.operator_ui.prediction_warroom.contracts.market_regime_card_contract import (
    BackgroundTone,
    EvidenceQuality,
    FreshnessBadge,
    MarketRegimeCode,
    ShortTag,
    build_market_regime_card_spec,
)

WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION = "prediction_warroom.market_regime_card_renderer.ps_q26y.v1"
WARROOM_MARKET_REGIME_CARD_PREVIEW_SWITCH_VERSION = "prediction_warroom.market_regime_card_preview_switch.ps_q27o.v1"
WARROOM_MARKET_REGIME_CARD_RENDERER_ACK = "PS_Q26Y_MARKET_REGIME_CARD_RENDERER_SHELL_UI_ONLY"
WARROOM_MARKET_REGIME_CARD_VISUAL_TUNE_VERSION = "prediction_warroom.market_regime_card_visual_tune.ps_q27a.v1"
MARKET_REGIME_CARD_WIDTH_PX = 208
MARKET_REGIME_CARD_HORIZON_FONT_SIZE_REM = "0.92rem"
WARROOM_MARKET_REGIME_CARD_DETAIL_POPOVER_VERSION = "prediction_warroom.market_regime_card_detail_popover.ps_q27b.v1"
WARROOM_MARKET_REGIME_CARD_SELECTED_DETAIL_PANEL_VERSION = "prediction_warroom.market_regime_card_selected_detail_panel.ps_q27c.v1"
WARROOM_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_VERSION = "prediction_warroom.market_regime_card_typography_badge_tune.ps_q27d.v1"
WARROOM_MARKET_REGIME_CARD_SMALL_VISUAL_POLISH_VERSION = "prediction_warroom.market_regime_card_small_visual_polish.ps_q27s.v1"
MARKET_REGIME_CARD_REGIME_FONT_SIZE_REM = "1.14rem"
MARKET_REGIME_CARD_CONFIDENCE_FONT_SIZE_REM = "1.60rem"
MARKET_REGIME_CARD_TAG_FONT_SIZE_REM = "1.04rem"
MARKET_REGIME_CARD_FRESHNESS_BADGE_FONT_SIZE_REM = "0.78rem"
MARKET_REGIME_CARD_FRESHNESS_BADGE_MIN_WIDTH_PX = 42
MARKET_REGIME_CARD_UNKNOWN_BACKGROUND = "#F2F4F7"


def build_sample_market_regime_cards() -> list[dict[str, Any]]:
    """Build static sample market-regime cards for renderer validation.

    This intentionally does not read D-hot/latest/runtime artifacts. It gives the
    UI shell stable examples covering GOOD/CAUTION/DANGER/UNKNOWN, freshness
    badges, and evidence border styles.
    """
    sample_specs = [
        ("現在", MarketRegimeCode.UP_TREND, 72, BackgroundTone.GOOD, FreshnessBadge.LIVE, EvidenceQuality.STRONG, ShortTag.PULLBACK_CANDIDATE),
        ("5分後", MarketRegimeCode.UP_TREND, 64, BackgroundTone.CAUTION, FreshnessBadge.LIVE, EvidenceQuality.PARTIAL, ShortTag.HIGH_ZONE),
        ("15分後", MarketRegimeCode.UNKNOWN, 83, BackgroundTone.UNKNOWN, FreshnessBadge.WARM, EvidenceQuality.CONFLICTED, ShortTag.SIGNAL_CONFLICT),
        ("30分後", MarketRegimeCode.RANGE, 58, BackgroundTone.CAUTION, FreshnessBadge.WARM, EvidenceQuality.PARTIAL, ShortTag.NO_DIRECTION),
        ("60分後", MarketRegimeCode.BREAKOUT, 61, BackgroundTone.GOOD, FreshnessBadge.WARM, EvidenceQuality.WEAK, ShortTag.PULLBACK_CANDIDATE),
        ("6時間後", MarketRegimeCode.HIGH_VOL_CHOP, 70, BackgroundTone.DANGER, FreshnessBadge.STALE, EvidenceQuality.CONFLICTED, ShortTag.NO_NEW_ENTRY),
        ("12時間後", MarketRegimeCode.REVERSAL_WATCH, 49, BackgroundTone.CAUTION, FreshnessBadge.STALE, EvidenceQuality.WEAK, ShortTag.REVERSAL_WATCH),
        ("24時間後", MarketRegimeCode.UNKNOWN, 55, BackgroundTone.UNKNOWN, FreshnessBadge.MISSING, EvidenceQuality.MISSING, ShortTag.DATA_MISSING),
    ]
    return [
        build_market_regime_card_spec(
            horizon=horizon,
            regime_code=regime,
            confidence_percent=confidence,
            background_tone=tone,
            freshness_badge=freshness,
            evidence_quality=evidence,
            short_tag=tag,
            extra={"sample_only": True},
        ).to_dict()
        for horizon, regime, confidence, tone, freshness, evidence, tag in sample_specs
    ]


def build_warroom_market_regime_card_renderer_packet(cards: Iterable[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    card_rows = [dict(card) for card in (cards or build_sample_market_regime_cards())]
    return {
        "ok": True,
        "renderer_version": WARROOM_MARKET_REGIME_CARD_RENDERER_VERSION,
        "renderer_ack": WARROOM_MARKET_REGIME_CARD_RENDERER_ACK,
        "market_regime_first": True,
        "sample_data_only": cards is None,
        "live_data_connected": False,
        "warroom_page_changed": False,
        "warroom_page_mounted": False,
        "other_prediction_cards_implemented": False,
        "streamlit_render_function_declared": True,
        "streamlit_render_invoked_by_page": False,
        "horizontal_scroll_required": True,
        "cards_do_not_shrink": True,
        "visual_tune_version": WARROOM_MARKET_REGIME_CARD_VISUAL_TUNE_VERSION,
        "card_width_px": MARKET_REGIME_CARD_WIDTH_PX,
        "card_width_px_before_q27a": 168,
        "card_width_expanded_by_px": MARKET_REGIME_CARD_WIDTH_PX - 168,
        "horizon_font_size_rem": MARKET_REGIME_CARD_HORIZON_FONT_SIZE_REM,
        "horizon_font_size_rem_before_q27a": "0.82rem",
        "horizon_label_text_unchanged": True,
        "typography_badge_tune_version": WARROOM_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_VERSION,
        "time_axis_font_size_unchanged": True,
        "regime_font_size_rem": MARKET_REGIME_CARD_REGIME_FONT_SIZE_REM,
        "confidence_font_size_rem": MARKET_REGIME_CARD_CONFIDENCE_FONT_SIZE_REM,
        "tag_font_size_rem": MARKET_REGIME_CARD_TAG_FONT_SIZE_REM,
        "freshness_badge_visibility_tuned": True,
        "freshness_badge_font_size_rem": MARKET_REGIME_CARD_FRESHNESS_BADGE_FONT_SIZE_REM,
        "freshness_badge_font_weight": 900,
        "freshness_badge_min_width_px": MARKET_REGIME_CARD_FRESHNESS_BADGE_MIN_WIDTH_PX,
        "detail_overlay_background": MARKET_REGIME_CARD_UNKNOWN_BACKGROUND,
        "detail_overlay_background_matches_unknown": True,
        "full_width_target_horizon": "24時間後",
        "detail_disclosure_available": True,
        "dialog_popup_planned_later": False,
        "detail_popover_version": WARROOM_MARKET_REGIME_CARD_DETAIL_POPOVER_VERSION,
        "selected_detail_panel_version": WARROOM_MARKET_REGIME_CARD_SELECTED_DETAIL_PANEL_VERSION,
        "detail_disclosure_mode": "card_overlay",
        "detail_popover_enabled": False,
        "selected_detail_panel_enabled": False,
        "card_detail_overlay_enabled": True,
        "overlay_covers_card_row": True,
        "overlay_close_button_enabled": True,
        "inline_detail_expansion_enabled": False,
        "fixed_detail_panel_reserved": False,
        "no_vertical_layout_shift_on_detail_open": True,
        "no_vertical_layout_shift_on_detail_select": False,
        "freshness_encoded_by_badge_only": True,
        "border_meaning": "evidence_quality",
        "background_tone_is_readability_first": True,
        "confidence_meaning": "market_regime_classification_certainty_not_win_rate",
        "card_count": len(card_rows),
        "horizons": [str(card.get("horizon", "")) for card in card_rows],
        "cards": card_rows,
        "production_ui_code_changed": True,
        "layout_only_change": True,
        "read_only": True,
        "display_only": True,
        "non_executing": True,
        "runtime_read_allowed": False,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "prediction_artifact_write_allowed": False,
        "view_artifact_write_allowed": False,
        "scheduler_enabled": False,
        "producer_enabled": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "ledger_append_allowed": False,
        "mode_apply_allowed": False,
        "parameter_apply_allowed": False,
        "would_send_to_broker": False,
    }



def build_warroom_market_regime_card_preview_switch_packet(
    *,
    preview_enabled: bool = False,
    hot_root: str | Any | None = None,
    generated_at: str = "",
) -> dict[str, Any]:
    """Build renderer packet using sample cards by default, or gated preview cards when explicitly enabled."""
    preview_cards: list[dict[str, Any]] | None = None
    binding_packet: dict[str, Any] | None = None
    preview_disabled_reason = "preview_enabled_false" if not preview_enabled else ""

    if preview_enabled and hot_root is not None and str(hot_root) != "":
        from btcts.apps.operator_ui.prediction_warroom.market_regime import build_market_regime_warroom_preview_binding_packet

        binding_packet = build_market_regime_warroom_preview_binding_packet(
            preview_enabled=True,
            hot_root=hot_root,
            generated_at=generated_at,
        )
        candidate_cards = binding_packet.get("cards") if isinstance(binding_packet, Mapping) else None
        if bool(binding_packet.get("ok")) and isinstance(candidate_cards, list) and candidate_cards:
            preview_cards = [dict(card) for card in candidate_cards if isinstance(card, Mapping)]
        if preview_cards is None:
            preview_disabled_reason = str(binding_packet.get("disabled_reason") or "preview_cards_unavailable")
    elif preview_enabled:
        preview_disabled_reason = "explicit_hot_root_required"

    renderer_packet = build_warroom_market_regime_card_renderer_packet(preview_cards)
    renderer_packet.update(
        {
            "preview_switch_version": WARROOM_MARKET_REGIME_CARD_PREVIEW_SWITCH_VERSION,
            "preview_switch_added": True,
            "preview_enabled": bool(preview_enabled),
            "preview_cards_used": preview_cards is not None,
            "preview_disabled_reason": preview_disabled_reason,
            "default_sample_only_when_disabled": True,
            "explicit_source_root_required": True,
            "explicit_source_root_read_performed": bool(binding_packet.get("explicit_source_root_read_performed")) if isinstance(binding_packet, Mapping) else False,
            "dry_run_invoked": bool(binding_packet.get("dry_run_invoked")) if isinstance(binding_packet, Mapping) else False,
            "source_snapshot_ok": bool(binding_packet.get("source_snapshot_ok")) if isinstance(binding_packet, Mapping) and "source_snapshot_ok" in binding_packet else None,
            "live_data_connected": False,
            "warroom_page_changed": False,
            "warroom_page_mounted": False,
            "streamlit_render_invoked_by_page": False,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        }
    )
    return renderer_packet

def _text(value: Any) -> str:
    return escape("" if value is None else str(value))


def _detail_lines(card: Mapping[str, Any]) -> str:
    detail = card.get("detail") if isinstance(card.get("detail"), Mapping) else {}
    reason_lines = detail.get("reason_lines") if isinstance(detail.get("reason_lines"), list) else []
    source_lines = detail.get("source_lines") if isinstance(detail.get("source_lines"), list) else []
    warning_lines = detail.get("warning_lines") if isinstance(detail.get("warning_lines"), list) else []
    reason = " / ".join(_text(item) for item in reason_lines) or "sample shell"
    source = " / ".join(_text(item) for item in source_lines) or "Q26X sample card"
    warning = " / ".join(_text(item) for item in warning_lines) or "live data not connected"
    evidence = card.get("evidence_quality_style") if isinstance(card.get("evidence_quality_style"), Mapping) else {}
    return (
        f"<div class='mr-detail-title'>概要</div>"
        f"<div class='mr-detail-line'><b>読み方:</b> {_text(detail.get('reading') or detail.get('summary') or '詳細は後続sliceで実データ接続後に拡張')}</div>"
        f"<div class='mr-detail-line'><b>理由:</b> {reason}</div>"
        f"<div class='mr-detail-line'><b>情報源:</b> {source}</div>"
        f"<div class='mr-detail-line'><b>注意:</b> {warning}</div>"
        f"<div class='mr-detail-line'><b>根拠:</b> {_text(evidence.get('label'))}</div>"
    )


def market_regime_cards_html(cards: Iterable[Mapping[str, Any]]) -> str:
    card_rows = [dict(card) for card in cards]
    card_html: list[str] = []
    detail_inputs: list[str] = [
        "<input class='mr-detail-radio' type='radio' id='mr-detail-close' name='mr-detail-selected-card' checked>"
    ]
    overlay_panels: list[str] = []
    select_css: list[str] = []

    for idx, card in enumerate(card_rows):
        detail_id = f"mr-detail-select-{idx}"
        detail_class = f"mr-overlay-content-{idx}"
        detail_inputs.append(
            f"<input class='mr-detail-radio' type='radio' id='{detail_id}' name='mr-detail-selected-card'>"
        )
        select_css.append(
            f"#mr-detail-select-{idx}:checked ~ .market-regime-card-stage .mr-card-detail-overlay {{ display: block; }}"
        )
        select_css.append(
            f"#mr-detail-select-{idx}:checked ~ .market-regime-card-stage .{detail_class} {{ display: block; }}"
        )
        bg = card.get("background_style") if isinstance(card.get("background_style"), Mapping) else {}
        evidence = card.get("evidence_quality_style") if isinstance(card.get("evidence_quality_style"), Mapping) else {}
        card_lines = card.get("card_lines") if isinstance(card.get("card_lines"), list) else []
        line1 = card_lines[0] if len(card_lines) > 0 else card.get("regime_label", "")
        line2 = card_lines[1] if len(card_lines) > 1 else f"{card.get('confidence_percent', '')}%"
        line3 = card_lines[2] if len(card_lines) > 2 else card.get("short_tag_label", "")
        style = (
            f"background:{_text(bg.get('background') or '#F2F4F7')};"
            f"color:{_text(bg.get('text') or '#101828')};"
            f"border:3px {_text(evidence.get('border_style') or 'solid')} {_text(evidence.get('border_color') or '#98A2B3')};"
        )
        card_html.append(
            "<section class='mr-card' style='" + style + "'>"
            "<div class='mr-topline'>"
            f"<span class='mr-horizon'>{_text(card.get('horizon'))}</span>"
            f"<span class='mr-badge'>{_text(card.get('freshness_badge'))}</span>"
            "</div>"
            f"<div class='mr-regime'>{_text(line1)}</div>"
            f"<div class='mr-confidence'>{_text(line2)}</div>"
            f"<div class='mr-tag'>{_text(line3)}</div>"
            f"<label class='mr-detail-selector-button' for='{detail_id}'>詳細</label>"
            "</section>"
        )
        overlay_panels.append(
            f"<section class='mr-overlay-detail-content {detail_class}'>"
            f"<div class='mr-overlay-detail-kicker'>{_text(card.get('horizon'))} / {_text(line1)} / {_text(line2)}</div>"
            + _detail_lines(card)
            + "</section>"
        )

    css = """
<style>
.market-regime-card-root {
  width: 100%;
}
.market-regime-card-root .mr-detail-radio {
  display: none;
}
.market-regime-card-stage {
  position: relative;
  width: 100%;
}
.market-regime-card-shell {
  display: flex;
  flex-wrap: nowrap;
  gap: 12px;
  overflow-x: auto;
  padding: 4px 2px 12px 2px;
  scroll-snap-type: x proximity;
}
.market-regime-card-shell .mr-card {
  min-width: """ + str(MARKET_REGIME_CARD_WIDTH_PX) + """px;
  max-width: """ + str(MARKET_REGIME_CARD_WIDTH_PX) + """px;
  flex: 0 0 """ + str(MARKET_REGIME_CARD_WIDTH_PX) + """px;
  border-radius: 16px;
  padding: 10px 10px 9px 10px;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.10);
  scroll-snap-align: start;
}
.market-regime-card-shell .mr-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}
.market-regime-card-shell .mr-horizon { font-size: """ + MARKET_REGIME_CARD_HORIZON_FONT_SIZE_REM + """; font-weight: 700; }
.market-regime-card-shell .mr-badge {
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(16, 24, 40, 0.22);
  padding: 3px 8px;
  min-width: """ + str(MARKET_REGIME_CARD_FRESHNESS_BADGE_MIN_WIDTH_PX) + """px;
  text-align: center;
  letter-spacing: 0.02em;
  font-size: """ + MARKET_REGIME_CARD_FRESHNESS_BADGE_FONT_SIZE_REM + """;
  font-weight: 900;
}
.market-regime-card-shell .mr-regime { font-size: """ + MARKET_REGIME_CARD_REGIME_FONT_SIZE_REM + """; font-weight: 800; line-height: 1.22; min-height: 2.42em; }
.market-regime-card-shell .mr-confidence { font-size: """ + MARKET_REGIME_CARD_CONFIDENCE_FONT_SIZE_REM + """; font-weight: 900; line-height: 1.08; margin-top: 5px; }
.market-regime-card-shell .mr-tag { font-size: """ + MARKET_REGIME_CARD_TAG_FONT_SIZE_REM + """; font-weight: 800; margin-top: 4px; }
.market-regime-card-shell .mr-detail-selector-button {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  margin-top: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(16, 24, 40, 0.14);
  padding: 3px 9px;
  font-size: 0.75rem;
  font-weight: 900;
}
.market-regime-card-shell .mr-detail-selector-button:hover {
  background: rgba(255, 255, 255, 0.96);
  border-color: rgba(16, 24, 40, 0.28);
}
.mr-card-detail-overlay {
  display: none;
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 40;
  border-radius: 16px;
  border: 1px solid rgba(16, 24, 40, 0.18);
  background: """ + MARKET_REGIME_CARD_UNKNOWN_BACKGROUND + """;
  box-shadow: 0 14px 32px rgba(16, 24, 40, 0.18);
  color: #101828;
  padding: 14px 16px;
  overflow-y: auto;
}
.mr-card-detail-overlay .mr-overlay-close {
  cursor: pointer;
  position: absolute;
  left: 12px;
  top: 10px;
  width: 24px;
  height: 24px;
  border-radius: 999px;
  border: 1px solid rgba(16, 24, 40, 0.18);
  background: #FFFFFF;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 0.92rem;
}
.mr-card-detail-overlay .mr-overlay-title {
  padding-left: 34px;
  font-size: 0.9rem;
  font-weight: 900;
  color: #344054;
  margin-bottom: 8px;
}
.mr-overlay-detail-content {
  display: none;
  padding-left: 34px;
  max-width: 760px;
  font-size: 0.9rem;
  line-height: 1.46;
}
.mr-overlay-detail-kicker {
  font-size: 0.88rem;
  font-weight: 900;
  color: #344054;
  margin-bottom: 6px;
}
.market-regime-card-root .mr-detail-title { font-weight: 900; font-size: 0.96rem; margin-bottom: 6px; }
.market-regime-card-root .mr-detail-line { margin-top: 4px; line-height: 1.38; }
""" + "\n".join(select_css) + """
</style>
<div class='market-regime-card-root'>
"""
    return (
        css
        + "\n".join(detail_inputs)
        + "\n<div class='market-regime-card-stage'>\n"
        + "<div class='market-regime-card-shell'>\n"
        + "\n".join(card_html)
        + "\n</div>\n"
        + "<div class='mr-card-detail-overlay'>\n"
        + "<label class='mr-overlay-close' for='mr-detail-close'>×</label>\n"
        + "<div class='mr-overlay-title'>地合いカード詳細</div>\n"
        + "\n".join(overlay_panels)
        + "\n</div>\n</div>\n</div>"
    )

def render_warroom_market_regime_card_shell(
    cards: Iterable[Mapping[str, Any]] | None = None,
    *,
    preview_enabled: bool = False,
    hot_root: str | Any | None = None,
    generated_at: str = "",
) -> None:
    """Render market-regime cards. Default remains sample-only; preview requires explicit args."""
    if cards is not None:
        packet = build_warroom_market_regime_card_renderer_packet(cards)
    else:
        packet = build_warroom_market_regime_card_preview_switch_packet(
            preview_enabled=preview_enabled,
            hot_root=hot_root,
            generated_at=generated_at,
        )
    st.session_state["warroom_market_regime_card_renderer"] = dict(packet)
    st.markdown(market_regime_cards_html(packet["cards"]), unsafe_allow_html=True)
