# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27B_MARKET_REGIME_CARD_DETAIL_POPOVER_2026-07-01.md
# desc: PS-Q27B changes market regime card detail from inline vertical expansion to click popover-style overlay. No live data changes.
# PS-Q27B Market regime card detail popover

Updated: 2026-07-01 JST
Base: PS-Q27A Market regime card visual tune
Mode: visual interaction tune only / sample data remains / no live data connection / no runtime artifact write / no scheduler or producer enablement / no trading guidance

```text
ps_q27b_market_regime_card_detail_popover=true
base_reentry=PS_Q27A_MARKET_REGIME_CARD_VISUAL_TUNE_DONE
selected_lane=MARKET_REGIME_CARD_DETAIL_POPOVER
visual_interaction_tune_only=true
market_regime_first=true
other_prediction_cards_implemented=false
production_ui_code_changed=true
warroom_page_changed=false
warroom_page_mounted_unchanged=true
sample_data_only=true
live_data_connected=false
detail_disclosure_mode=popover
detail_popover_enabled=true
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

Q27B keeps the readable Q27A card width and horizon label sizing, but changes the detail interaction. Inline vertical details made the selected card taller and pushed the lower WarRoom sections down. Q27B turns the detail block into a click popover-style overlay so details can be read without changing the surrounding page layout.

## Boundary

This slice only changes the market-regime card detail display behavior and directly related guards. It does not connect live data, change WarRoom page mount structure, add other prediction card types, or alter runtime behavior.
