# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27E_WARROOM_CARD_UI_REUSE_SPEC_2026-07-02.md
# desc: PS-Q27E WarRoom prediction card UI reuse specification. Documents the final Q27D card UI for reuse by future prediction cards. Spec-only; no runtime/UI code change.
# PS-Q27E WarRoom card UI reuse specification

Updated: 2026-07-02 JST
Base: PS-Q27D Market regime card typography and freshness badge tune
Mode: specification-only / no production UI code change / no runtime artifact write / no scheduler or producer enablement / no trading guidance

```text
ps_q27e_warroom_card_ui_reuse_spec=true
base_reentry=PS_Q27D_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_DONE
selected_lane=WARROOM_CARD_UI_REUSE_SPECIFICATION
spec_only_change=true
production_ui_code_changed=false
runtime_code_changed=false
warroom_page_changed=false
sample_data_only_unchanged=true
live_data_connected=false
market_regime_card_ui_is_canonical_reference=true
future_prediction_card_reuse_expected=true
next_thread_ready_for_market_regime_live_data_binding_design=true
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

Q27E freezes the final WarRoom card UI style from Q27D as the common reference for future prediction cards. Later cards should not invent a separate visual language unless a new explicit design gate changes this document.

The current implemented card is **market regime**. Future cards may reuse the same shell for direction, volatility, shock risk, liquidity, execution flow, or other prediction views, but those cards are not implemented by this slice.

## Canonical source chain

```text
Q26W=market_regime_card_spec_foundation
Q26X=pure_data_contract_helpers
Q26Y=sample_renderer_shell
Q26Z=WarRoom_sample_mount
Q27A=card_width_and_horizon_visual_tune
Q27B=detail_popover_experiment
Q27C=card_row_overlay_detail_behavior
Q27D=typography_badge_tune_and_overlay_unknown_gray
Q27E=this_reuse_spec
```

Implementation source for the current market-regime sample card:

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/market_regime_card_contract.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py
```

## Reusable card shell

Future WarRoom prediction cards should reuse this shape:

```text
card_row_layout=horizontal_time_axis_cards
card_width_px=208
cards_do_not_shrink=true
horizontal_scroll_required=true
wide_window_goal=show_through_24h_when_space_allows
narrow_window_goal=show_visible_range_and_scroll_do_not_squeeze
card_border_radius_px=16
card_padding=10px 10px 9px 10px
card_gap_px=12
scroll_snap=x_proximity
```

## Reusable card body hierarchy

The card body has exactly three main text lines plus a freshness badge and detail action.

```text
line_1=primary_classification_label
line_2=confidence_or_card_score
line_3=short_action_or_state_tag
freshness_badge=top_right_badge_only
detail_action=small_detail_button
```

For market regime:

```text
line_1=上昇トレンド / レンジ / 予測不能など
line_2=72%などの分類信頼度
line_3=押し目候補 / 高値圏 / シグナル割れなど
```

For future prediction cards, the same visual slots may be reused, but the semantics must be explicit in that card's contract. Do not silently reuse `%` as a win rate unless the card contract says so.

## Final typography values

These are the Q27D visual defaults.

```text
time_axis_font_size_unchanged=true
horizon_font_size_rem=0.92rem
primary_label_font_size_rem=1.14rem
confidence_font_size_rem=1.60rem
short_tag_font_size_rem=1.04rem
freshness_badge_font_size_rem=0.78rem
freshness_badge_font_weight=900
freshness_badge_min_width_px=42
freshness_badge_padding=3px 8px
freshness_badge_border=1px solid rgba(16, 24, 40, 0.22)
freshness_badge_letter_spacing=0.02em
```

Rationale:

```text
primary_label_should_be_first_read=true
confidence_should_be_visible_but_not_overpower_primary_label=true
short_tag_should_be_readable_for_operator_action_context=true
time_axis_size_currently_good_do_not_change_without_new_visual_review=true
freshness_badge_visibility_should_be_higher_than_q27c=true
```

## Color meaning separation

Do not overload colors.

```text
background_tone=tradability_or_readability_or_risk_temperature
freshness=badge_only
border=evidence_quality
confidence=classification_certainty_or_card_specific_certainty_not_implicit_win_rate
```

Market-regime background palette:

```text
GOOD.background=#DCFAE6
CAUTION.background=#FEF7C3
DANGER.background=#FEE4E2
UNKNOWN.background=#F2F4F7
TEXT.primary=#101828
```

Important rule:

```text
background_color_never_encodes_freshness=true
freshness_not_encoded_by_border=true
```

## Freshness badge policy

```text
freshness_encoded_by_badge_only=true
freshness_badge_values=LIVE,WARM,STALE,MISSING
badge_position=top_right
badge_background=rgba(255,255,255,0.82)
badge_border=1px solid rgba(16,24,40,0.22)
badge_font_size=0.78rem
badge_font_weight=900
badge_min_width=42px
```

Future cards should use the same badge vocabulary unless they define a compatible extension.

## Evidence border policy

For market regime, border means evidence quality. Future prediction cards should either reuse this meaning or explicitly rename the border concept in their own card contract.

```text
border_meaning=evidence_quality
STRONG=solid blue border / 根拠良好
PARTIAL=solid purple or blue-gray border / 根拠やや不足
WEAK=solid gray border / 根拠不足
CONFLICTED=dashed purple border / 根拠衝突
MISSING=dotted muted gray border / 根拠なし
```

## Detail behavior

Q27C/Q27D final behavior is canonical.

```text
detail_disclosure_mode=card_overlay
card_detail_overlay_enabled=true
overlay_covers_card_row=true
overlay_close_button_enabled=true
overlay_close_button_position=left_top
overlay_close_button_label=×
inline_detail_expansion_enabled=false
detail_popover_enabled=false
selected_detail_panel_enabled=false
fixed_detail_panel_reserved=false
no_vertical_layout_shift_on_detail_open=true
detail_overlay_background=#F2F4F7
detail_overlay_background_matches_unknown=true
```

Rationale:

```text
inline_detail_pushes_lower_warroom_sections_down=bad
pseudo_popover_inside_horizontal_scroll_can_be_clipped=bad
selected_detail_panel_uses_vertical_space_and_hurts_future_scanability=not_preferred
card_overlay_preserves_overall_scanability=true
card_overlay_can_cover_cards_while_reading_details=true
```

## Detail content sections

Use concise, structured detail text. Do not put long text inside the card body.

```text
detail_sections=概要,読み方,理由,情報源,注意,根拠
```

Future live-data binding should fill details from structured payload fields, not ad-hoc text.

## Generic card reuse contract

Future prediction cards should define a contract equivalent to:

```text
CardSpec.card_id
CardSpec.card_type
CardSpec.horizon
CardSpec.primary_label
CardSpec.confidence_or_score
CardSpec.confidence_meaning
CardSpec.short_tag
CardSpec.background_tone
CardSpec.freshness_badge
CardSpec.border_style_name
CardSpec.detail_payload
CardSpec.diagnostic_record_ref
```

If a future card uses a numeric value, it must define what the value means:

```text
number_is_classification_confidence
number_is_direction_probability
number_is_risk_score
number_is_volatility_score
number_is_liquidity_score
```

Do not let the UI imply trade probability, win rate, or trade instruction by default.

## Diagnostic and improvement records

For UNKNOWN, low-confidence, stale, conflicted, or missing states, card details may be short, but diagnostic records must preserve improvement context.

```text
diagnostic_record_required_for_unknown_and_low_confidence=true
reason_codes_should_be_stable=true
record_raw_large_payloads_by_reference_not_inline=true
```

Existing market-regime reason codes remain reusable examples:

```text
DATA_MISSING
STALE_INPUT
SIGNAL_CONFLICT
LOW_LIQUIDITY
WIDE_SPREAD
POST_SPIKE_UNSTABLE
MODEL_DISAGREEMENT
LOW_CONFIDENCE
INSUFFICIENT_HISTORY
NO_CLEAR_REGIME
```

## Safety and non-goals

Q27E is documentation only.

```text
production_ui_code_changed=false
runtime_code_changed=false
warroom_page_changed=false
live_data_connected=false
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

## Next-thread recommended start

The next thread can start with:

```text
Start from PS_Q27E_WARROOM_CARD_UI_REUSE_SPEC_DONE.
Next target: MARKET_REGIME_CARD_LIVE_DATA_BINDING_DESIGN.
Do not connect live data until D-hot/latest artifact source shape is inspected.
Do not add other prediction card types before market-regime binding is designed.
Keep Q27D/Q27E card UI spec unchanged unless a new visual review gate explicitly changes it.
```
