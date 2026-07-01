# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27T_WARROOM_MARKET_REGIME_STATUS_DENSITY_REDUCTION_2026-07-02.md
# desc: PS-Q27T WarRoom market-regime status density reduction. Removes redundant preview/caption copy without changing preview gating, card specs, or runtime behavior.
# PS-Q27T WarRoom market-regime status density reduction

Updated: 2026-07-02 JST
Base: PS-Q27S WarRoom market-regime small visual polish copy reduction
Mode: small production UI copy deletion / no card geometry change / no runtime artifact write / no scheduler or producer enablement / no trading guidance.

```text
ps_q27t_warroom_market_regime_status_density_reduction=true
base_reentry=PS_Q27S_MARKET_REGIME_ENGINE_WARROOM_SMALL_VISUAL_POLISH_COPY_REDUCTION_DONE
selected_lane=MARKET_REGIME_WARROOM_STATUS_DENSITY_REDUCTION
production_ui_code_changed=true
runtime_code_changed=false
market_regime_only=true
redundant_status_copy_removed=true
preview_checkbox_label_compacted=true
preview_default_explainer_caption_removed=true
panel_caption_removed=true
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

This slice continues the correction from PS-Q27S: reduce visible status text instead of explaining obvious behavior.

The visual change is limited to removing redundant status/caption text around the market-regime card area:

```text
checkbox_label_before=地合いカード preview を明示有効化（D-hot read-only / 実行系なし）
checkbox_label_after=地合い preview
default_explainer_caption_removed=true
panel_sample_preview_caption_removed=true
```

The preview gate and safety flags remain in code/tests, but they do not need to occupy visual space in the WarRoom tab.

## Preserved invariants

```text
preview_default_off=true
operator_checkbox_required=true
explicit_source_root_required=true
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
