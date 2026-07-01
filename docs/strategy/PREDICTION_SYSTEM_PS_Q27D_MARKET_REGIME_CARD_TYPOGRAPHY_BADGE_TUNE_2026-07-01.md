# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27D_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_2026-07-01.md
# desc: PS-Q27D market regime card typography and freshness badge visual tune. No live data changes.
# PS-Q27D Market regime card typography and freshness badge tune

Updated: 2026-07-01 JST
Base: PS-Q27C Market regime card detail overlay
Mode: visual typography tune only / sample data remains / no live data connection / no runtime artifact write / no scheduler or producer enablement / no trading guidance

```text
ps_q27d_market_regime_card_typography_badge_tune=true
base_reentry=PS_Q27C_MARKET_REGIME_CARD_DETAIL_OVERLAY_DONE
selected_lane=MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE
visual_typography_tune_only=true
market_regime_first=true
other_prediction_cards_implemented=false
production_ui_code_changed=true
warroom_page_changed=false
warroom_page_mounted_unchanged=true
sample_data_only=true
live_data_connected=false
time_axis_font_size_unchanged=true
horizon_font_size_rem=0.92rem
regime_font_size_before=1.02rem
regime_font_size_after=1.14rem
confidence_font_size_before=1.72rem
confidence_font_size_after=1.60rem
tag_font_size_before=0.88rem
tag_font_size_after=1.04rem
freshness_badge_visibility_tuned=true
freshness_badge_font_size_before=0.72rem
freshness_badge_font_size_after=0.78rem
freshness_badge_font_weight_after=900
freshness_badge_padding_after=3px 8px
freshness_badge_min_width_after=42px
freshness_badge_border_after=1px solid rgba(16, 24, 40, 0.22)
detail_overlay_background=#F2F4F7
detail_overlay_background_matches_unknown=true
detail_disclosure_mode=card_overlay
card_detail_overlay_enabled=true
overlay_close_button_enabled=true
card_width_px=208
horizontal_scroll_required=true
cards_do_not_shrink=true
freshness_encoded_by_badge_only=true
border_meaning=evidence_quality
background_tone_is_readability_first=true
confidence_meaning=market_regime_classification_certainty_not_win_rate
read_only=true
display_only=true
non_executing=true
runtime_read_allowed=false
runtime_artifact_write_allowed=false
status_artifact_write_allowed=false
prediction_artifact_write_allowed=false
view_artifact_write_allowed=false
scheduler_enabled=false
producer_enabled=false
autotrade_trigger_allowed=false
broker_private_api_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
would_send_to_broker=false
```

## Purpose

Q27D tunes the card typography after visual review. The time-axis label is already readable and remains unchanged. The regime label becomes the main first-read text, the confidence percent is made less dominant, the short tag becomes easier to scan, and the freshness badge gains visibility without changing its meaning. The card-row detail overlay uses the same gray as the UNKNOWN card background to avoid blending into the surrounding white page.

## Boundary

This slice only changes market-regime card typography and badge visual styling. It does not connect live data, change WarRoom page mount structure, add other prediction card types, or alter runtime behavior.
