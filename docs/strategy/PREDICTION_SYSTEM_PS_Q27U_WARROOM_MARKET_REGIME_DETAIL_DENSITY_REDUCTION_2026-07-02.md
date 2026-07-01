# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27U_WARROOM_MARKET_REGIME_DETAIL_DENSITY_REDUCTION_2026-07-02.md
# desc: PS-Q27U WarRoom market-regime detail density reduction. Removes low-value detail rows/fallback copy without changing card specs or runtime behavior.
# PS-Q27U WarRoom market-regime detail density reduction

Updated: 2026-07-02 JST
Base: PS-Q27T WarRoom market-regime status density reduction
Mode: small production UI detail copy deletion / no card geometry change / no runtime artifact write / no scheduler or producer enablement / no trading guidance.

```text
ps_q27u_warroom_market_regime_detail_density_reduction=true
base_reentry=PS_Q27T_MARKET_REGIME_ENGINE_WARROOM_STATUS_DENSITY_REDUCTION_DONE
selected_lane=MARKET_REGIME_WARROOM_DETAIL_DENSITY_REDUCTION
production_ui_code_changed=true
runtime_code_changed=false
market_regime_only=true
detail_density_reduced=true
detail_reading_row_removed=true
detail_evidence_row_removed=true
empty_fallback_copy_removed=true
detail_reason_source_limited=true
warning_row_rendered_only_when_present=true
prefer_deletion_over_explanation=true
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

This slice reduces detail overlay noise. It removes low-value rows and fallback copy rather than adding explanations.

```text
detail_rows_removed=読み方,根拠
fallback_copy_removed=sample shell,Q26X sample card,live data not connected
reason_source_rows_kept=true
reason_source_items_limited=true
warning_row_only_when_present=true
```

## Preserved invariants

```text
preview_default_off=true
operator_checkbox_required=true
card_row_layout=horizontal_time_axis_cards
card_width_px=208
cards_do_not_shrink=true
horizontal_scroll_required=true
card_body_three_lines=true
freshness_badge=top_right_badge_only
freshness_encoded_by_badge_only=true
border_meaning=evidence_quality
detail_disclosure_mode=card_overlay
no_vertical_layout_shift_on_detail_open=true
```

## Non-goals

```text
not_changing_classifier=true
not_changing_card_adapter_semantics=true
not_changing_card_width=true
not_adding_fourth_card_body_line=true
not_adding_more_explanatory_copy=true
not_adding_other_prediction_cards=true
not_adding_autotrade_or_broker_or_ledger_behavior=true
```
