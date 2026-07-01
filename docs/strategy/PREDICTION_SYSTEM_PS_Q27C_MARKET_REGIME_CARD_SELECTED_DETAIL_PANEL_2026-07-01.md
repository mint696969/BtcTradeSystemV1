# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27C_MARKET_REGIME_CARD_SELECTED_DETAIL_PANEL_2026-07-01.md
# desc: PS-Q27C changes market regime card details from clipped pseudo-popover to a card-row overlay with close button. No live data changes.
# PS-Q27C Market regime card detail overlay

Updated: 2026-07-01 JST
Base: PS-Q27B Market regime card detail popover
Mode: visual interaction tune only / sample data remains / no live data connection / no runtime artifact write / no scheduler or producer enablement / no trading guidance

```text
ps_q27c_market_regime_card_detail_overlay=true
base_reentry=PS_Q27B_MARKET_REGIME_CARD_DETAIL_POPOVER_DONE
selected_lane=MARKET_REGIME_CARD_DETAIL_OVERLAY
visual_interaction_tune_only=true
market_regime_first=true
other_prediction_cards_implemented=false
production_ui_code_changed=true
warroom_page_changed=false
warroom_page_mounted_unchanged=true
sample_data_only=true
live_data_connected=false
detail_disclosure_mode=card_overlay
card_detail_overlay_enabled=true
overlay_covers_card_row=true
overlay_close_button_enabled=true
selected_detail_panel_enabled=false
detail_popover_enabled=false
inline_detail_expansion_enabled=false
no_vertical_layout_shift_on_detail_open=true
card_width_px=208
horizon_font_size_rem=0.92rem
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

Q27B improved detail readability, but the pseudo-popover was clipped by the card-row scroll container. The initial Q27C selected-detail panel was stable, but it consumed vertical space and reduced future scanability when more cards are added. Q27C now uses a detail overlay on top of the card row. Clicking a card's detail button covers the visible card row with a readable detail layer, and the operator can close it with the left-top × button.

## Boundary

This slice only changes the market-regime card detail display behavior and directly related historical guards. It does not connect live data, change WarRoom page mount structure, add other prediction card types, or alter runtime behavior.
