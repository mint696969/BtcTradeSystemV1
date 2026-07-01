# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27A_MARKET_REGIME_CARD_VISUAL_TUNE_2026-07-01.md
# desc: PS-Q27A visual tune for market regime cards: wider cards and larger horizon labels. No live data changes.
# PS-Q27A Market regime card visual tune

Updated: 2026-07-01 JST
Base: PS-Q26Z Market regime card WarRoom sample-only mount
Mode: visual tune only / sample data remains / no live data connection / no runtime artifact write / no scheduler or producer enablement / no trading guidance

```text
ps_q27a_market_regime_card_visual_tune=true
base_reentry=PS_Q26Z_MARKET_REGIME_CARD_WARROOM_MOUNT_SAMPLE_ONLY_DONE
selected_lane=MARKET_REGIME_CARD_VISUAL_TUNE
visual_tune_only=true
market_regime_first=true
other_prediction_cards_implemented=false
production_ui_code_changed=true
warroom_page_changed=false
warroom_page_mounted_unchanged=true
sample_data_only=true
live_data_connected=false
card_width_px_before=168
card_width_px_after=208
card_width_expanded_by_px=40
horizon_font_size_rem_before=0.82
horizon_font_size_rem_after=0.92
horizon_label_text_unchanged=true
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

Q27A tunes the sample-mounted market-regime cards after visual review. The cards were readable, but slightly too compact. This slice widens each card and increases the time-axis label size while keeping the same label text and the existing horizontal-scroll behavior.

## Boundary

This slice changes only the market-regime card renderer shell styling and directly related guards. It does not connect live data, change D-hot reads, change WarRoom page mounting, add other prediction card types, or alter runtime behavior.
