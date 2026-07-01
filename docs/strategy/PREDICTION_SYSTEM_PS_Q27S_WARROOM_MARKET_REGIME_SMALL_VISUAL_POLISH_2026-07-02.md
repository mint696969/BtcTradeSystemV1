# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27S_WARROOM_MARKET_REGIME_SMALL_VISUAL_POLISH_2026-07-02.md
# desc: PS-Q27S small WarRoom market-regime visual polish. Reduces redundant captions/copy without changing card geometry or runtime behavior.
# PS-Q27S WarRoom market-regime small visual polish

Updated: 2026-07-02 JST
Base: PS-Q27R WarRoom operator screenshot review checklist
Mode: small production UI text polish / no card geometry change / no runtime artifact write / no scheduler or producer enablement / no trading guidance.

```text
ps_q27s_warroom_market_regime_small_visual_polish=true
base_reentry=PS_Q27R_MARKET_REGIME_ENGINE_WARROOM_OPERATOR_SCREENSHOT_REVIEW_DONE
selected_lane=MARKET_REGIME_WARROOM_SMALL_VISUAL_POLISH_COPY_REDUCTION
production_ui_code_changed=true
runtime_code_changed=false
market_regime_only=true
redundant_copy_reduced=true
caption_compacted=true
preview_off_status_compact=true
preview_on_status_compact=true
confidence_explainer_added=false
operator_already_understands_confidence_not_win_rate=true
detail_overlay_japanese_headings_preserved=true
card_width_changed=false
card_body_three_lines_unchanged=true
freshness_encoded_by_badge_only=true
border_meaning=evidence_quality
detail_disclosure_mode=card_overlay
read_only=true
display_only=true
non_executing=true
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

This slice corrects the PS-Q27S direction: do not add obvious explanatory copy. The operator already understands that confidence is not a win rate. The UI should stay compact.

The polish is intentionally small:

```text
OFF caption=地合いカード: sample
ON caption=地合いカード: preview / read-only
extra_confidence_explainer_removed=true
```

## Preserved Q26W/Q27E invariants

```text
card_row_layout=horizontal_time_axis_cards
card_width_px=208
cards_do_not_shrink=true
horizontal_scroll_required=true
card_body_three_lines=true
freshness_badge=top_right_badge_only
freshness_encoded_by_badge_only=true
border_meaning=evidence_quality
background_tone=tradability_or_readability_or_risk_temperature
confidence_meaning=classification_certainty_not_win_rate
detail_disclosure_mode=card_overlay
no_vertical_layout_shift_on_detail_open=true
```

## Non-goals

```text
not_changing_card_width=true
not_adding_fourth_card_body_line=true
not_encoding_freshness_by_background_or_border=true
not_adding_confidence_explainer=true
not_adding_other_prediction_cards=true
not_adding_autotrade_or_broker_or_ledger_behavior=true
```

## Next visual review preference

Use screenshots first. When something is visually noisy, prefer deletion or shorter labels before adding explanatory text.
