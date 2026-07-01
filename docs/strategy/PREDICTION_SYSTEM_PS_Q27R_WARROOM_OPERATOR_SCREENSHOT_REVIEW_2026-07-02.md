# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q27R_WARROOM_OPERATOR_SCREENSHOT_REVIEW_2026-07-02.md
# desc: PS-Q27R WarRoom market-regime card operator screenshot review checklist. Documentation-only; no production code/runtime change.
# PS-Q27R WarRoom market-regime operator screenshot review

Updated: 2026-07-02 JST
Base: PS-Q27Q WarRoom market-regime UI smoke preview OFF/ON read-only
Mode: documentation / operator visual review checklist only; no production UI code change; no runtime artifact write; no scheduler or producer enablement; no trading guidance.

```text
ps_q27r_warroom_operator_screenshot_review=true
base_reentry=PS_Q27Q_MARKET_REGIME_ENGINE_WARROOM_UI_SMOKE_PREVIEW_OFF_ON_READ_ONLY_DONE
selected_lane=MARKET_REGIME_WARROOM_OPERATOR_SCREENSHOT_REVIEW
production_code_changed=false
production_ui_code_changed=false
runtime_code_changed=false
warroom_page_changed=false
market_regime_only=true
other_prediction_cards_implemented=false
operator_screenshot_required=true
preview_off_review_required=true
preview_on_review_required=true
q26w_q27e_spec_alignment_required=true
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

Before making further visual or live-binding changes, capture and review the actual WarRoom tab with the market-regime card preview in both states:

```text
OFF=default sample-only card row, no D-hot read
ON=explicit operator checkbox, D-hot read-only preview cards
```

The review is intentionally not a code change gate. It is a visual acceptance and improvement proposal gate. Any visual change after this document must be a separate small slice with before/after review.

## Canonical specs to keep

Use Q26W and Q27E as the visual contract:

```text
spec_foundation=docs/strategy/PREDICTION_SYSTEM_PS_Q26W_MARKET_REGIME_CARD_SPEC_2026-07-01.md
reuse_spec=docs/strategy/PREDICTION_SYSTEM_PS_Q27E_WARROOM_CARD_UI_REUSE_SPEC_2026-07-02.md
```

Required invariants:

```text
card_row_layout=horizontal_time_axis_cards
card_width_px=208
cards_do_not_shrink=true
horizontal_scroll_required=true
card_body_three_lines=true
line_1=primary_classification_label
line_2=confidence_or_card_score
line_3=short_action_or_state_tag
freshness_badge=top_right_badge_only
freshness_encoded_by_badge_only=true
border_meaning=evidence_quality
background_tone=tradability_or_readability_or_risk_temperature
confidence_meaning=classification_certainty_not_win_rate
detail_disclosure_mode=card_overlay
no_vertical_layout_shift_on_detail_open=true
```

## OFF screenshot checklist

For preview OFF, verify:

```text
checkbox_default_off=true
sample_only_caption_visible=true
sample_cards_visible=true
card_count=8
horizons=現在,5分後,15分後,30分後,60分後,6時間後,12時間後,24時間後
no_d_hot_read=true
preview_enabled_effective=false
```

Visual checks:

```text
cards_are_horizontal_not_table=true
cards_are_not_squeezed=true
freshness_badge_top_right=true
background_color_does_not_encode_freshness=true
border_looks_like_evidence_quality=true
primary_label_is_first_read=true
confidence_is_visible_but_not_overpowering=true
short_tag_is_readable=true
detail_button_visible=true
```

## ON screenshot checklist

For preview ON, verify:

```text
operator_checkbox_on=true
read_only_preview_caption_or_signal_visible=true
real_preview_cards_visible=true
sample_data_only=false
source_snapshot_ok_expected=true
card_count=8
horizons=現在,5分後,15分後,30分後,60分後,6時間後,12時間後,24時間後
no_runtime_artifact_write=true
no_scheduler_or_producer=true
no_broker_or_ledger=true
would_send_to_broker=false
```

Expected current D-hot preview from PS-Q27Q smoke:

```text
real_dhot_on_source_snapshot_ok=true
real_dhot_on_card_count=8
real_dhot_on_cards=all_RANGE_78_LIVE_NO_DIRECTION_CAUTION
```

The exact live values may drift as D-hot changes, but these semantic invariants must remain:

```text
all_cards_have_three_body_lines=true
confidence_percent_max_99=true
freshness_badge_values_in=LIVE,WARM,STALE,MISSING
border_meaning=evidence_quality
confidence_not_win_rate=true
card_detail_overlay_available=true
```

## Detail overlay checklist

Open one card detail in OFF and ON screenshots if possible. Verify:

```text
detail_overlay_covers_card_row=true
overlay_close_button_visible=true
overlay_does_not_push_lower_sections=true
long_text_not_inside_card_body=true
summary_reading_reason_source_warning_are_structured=true
```

## Improvement candidates allowed after screenshot review

These are allowed proposals if the screenshot shows they help readability. They must be implemented in later explicit slices, not inside this review slice.

```text
improvement_candidate_1=ON時のcaptionを「実データ preview / read-only / 実行系なし」とより明確化
improvement_candidate_2=detail overlay内の source coverage / missing source / warning を日本語見出しで整理
improvement_candidate_3=confidence lineに「分類信頼度」tooltip_or_detailを追加し勝率誤読を減らす
improvement_candidate_4=ON時にsample-onlyとの違いを小さなstatus lineで示す
improvement_candidate_5=rangeが全horizonに並ぶ場合、detail内に「同一分類の理由」をまとめる
```

Not allowed without a new visual gate:

```text
not_allowed=card_width_change
not_allowed=card_body_more_than_three_lines
not_allowed=freshness_by_background_or_border
not_allowed=confidence_as_win_rate
not_allowed=inline_detail_that_pushes_lower_sections
not_allowed=other_prediction_card_addition
not_allowed=autotrade_or_broker_or_ledger_behavior
```

## Operator screenshot request format

Ask the operator for two screenshots:

```text
1. WarRoom tab with 地合いカード preview checkbox OFF
2. WarRoom tab with 地合いカード preview checkbox ON
```

If the ON screenshot is too wide, include the row from 現在 through 24時間後 or provide a second horizontally scrolled capture. The review should judge both readability and whether the spec still feels right in the real tab.

## Completion criteria

```text
operator_screenshot_review_doc_added=true
production_code_changed=false
focused_guard_passed=true
room_synced_after_commit=true
next_slice_can_review_uploaded_screenshots=true
```
