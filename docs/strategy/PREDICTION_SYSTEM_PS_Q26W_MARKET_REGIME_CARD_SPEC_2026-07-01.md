# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q26W_MARKET_REGIME_CARD_SPEC_2026-07-01.md
# desc: PS-Q26W market regime card UI specification foundation. Spec-only; reusable card contract for future WarRoom implementations.
# PS-Q26W Market regime card specification

Updated: 2026-07-01 JST
Base: PS-Q26V WarRoom operator focus route table fold
Mode: specification-only / no production UI change / no runtime artifact write / no scheduler or producer enablement / no trading guidance

```text
ps_q26w_market_regime_card_spec=true
base_reentry=PS_Q26V_WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_DONE
selected_lane=WARROOM_UI_MARKET_REGIME_CARD_SPECIFICATION
spec_only_change=true
production_ui_code_changed=false
runtime_code_changed=false
warroom_page_changed=false
warroom_page_slimming_main_goal=false
market_regime_first=true
future_prediction_card_reuse_expected=true
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

Q26W fixes the first version of the WarRoom market-regime card contract before UI implementation. The goal is to make market regime readable as a visual time-axis card row, while keeping the contract generic enough to reuse later for other prediction cards.

The first implementation target is **market regime only**. Other prediction cards must not be added in the same slice.

## Agreed UI intent

```text
full_width_behavior=show_all_horizons_through_24h
narrow_width_behavior=do_not_shrink_cards_show_visible_range_and_allow_horizontal_scroll
card_shape=horizontal_time_axis_cards
primary_goal=visual_understanding_not_text_table
long_text_location=click_detail_or_dialog
```

The card row should represent horizons such as:

```text
現在 / 5分後 / 15分後 / 30分後 / 60分後 / 6時間後 / 12時間後 / 24時間後
```

When the UI window is wide enough, 24h should be visible. When narrower, cards should not be squeezed into unreadable sizes; the visible range should depend on the window width.

## Market regime names v1

Initial registry values:

```text
UP_TREND=上昇トレンド
DOWN_TREND=下落トレンド
RANGE=レンジ
LOW_VOL_COMPRESSION=低ボラ・膠着
HIGH_VOL_CHOP=高ボラ・乱高下
BREAKOUT=ブレイク
PANIC_SPIKE=急変・パニック
REVERSAL_WATCH=転換候補
UNKNOWN=予測不能
```

The registry must be extensible. Future classifications may be added without rewriting the generic card renderer.

## Meaning separation

Do not overload one color with multiple meanings.

```text
regime_name=what_kind_of_market
background_tone=tradability_or_risk_temperature
freshness_badge=input_freshness
border_style=evidence_quality
confidence_percent=certainty_of_this_regime_classification_not_win_rate
```

Important examples:

```text
DOWN_TREND + GOOD background = short-side trend is readable, not necessarily bad
DOWN_TREND + DANGER background = disorderly drop or unsafe new entry condition
UP_TREND + CAUTION background = uptrend but chase risk or high-zone caution
UNKNOWN + UNKNOWN background = cannot classify or classification should be withheld
```

## Card body v1

Card body should stay short.

```text
line_1=market_regime_label
line_2=confidence_percent_max_99
line_3=short_tag
```

Examples:

```text
上昇トレンド
50%
高値圏
```

```text
予測不能
83%
シグナル割れ
```

The percent is capped at 99%. Avoid 100% because the UI should not imply certainty in market reading.

## Confidence meaning

```text
confidence_percent=certainty_of_the_market_regime_classification
max_confidence_percent=99
confidence_is_not_directional_win_rate=true
```

For UNKNOWN:

```text
UNKNOWN 83% = 83% certainty that the correct classification is currently unreadable / no-call
```

## Background tone policy

Card inside color must prioritize readability. Use pale colors and dark text.

```text
background_tone_good=淡い緑 / readable black text
background_tone_caution=淡い黄 / readable black text
background_tone_danger=淡い赤 / readable black text
background_tone_unknown=かなり薄いグレー / readable black text
background_color_never_encodes_freshness=true
```

Recommended palette direction, not final CSS binding:

```text
GOOD.background=#DCFAE6
CAUTION.background=#FEF7C3
DANGER.background=#FEE4E2
UNKNOWN.background=#F2F4F7
TEXT.primary=#101828
```

## Freshness badge policy

Freshness is shown by a small badge, not by the card border.

```text
freshness_badge_required=true
freshness_badge_values=LIVE,WARM,STALE,MISSING
freshness_not_encoded_by_border=true
```

Badge examples:

```text
LIVE
12s
STALE
MISSING
```

Exact time thresholds may be decided later from D-hot data behavior. The v1 spec fixes the vocabulary and meaning only.

## Border style policy

Card border is reserved for evidence quality, not freshness.

```text
border_meaning=evidence_quality
border_not_freshness=true
```

Evidence quality vocabulary:

```text
STRONG=根拠良好
PARTIAL=根拠やや不足
WEAK=根拠不足
CONFLICTED=根拠衝突
MISSING=根拠なし
```

Recommended visual direction:

```text
STRONG=solid blue border
PARTIAL=solid blue-gray or purple border
WEAK=solid gray border
CONFLICTED=dashed border
MISSING=dotted or muted gray border
```

## Short tag vocabulary v1

The third line should use short stable tags. Free text is allowed only inside details.

```text
HIGH_ZONE=高値圏
LOW_ZONE=安値圏
PULLBACK_CANDIDATE=押し目候補
RETURN_SELL_WATCH=戻り売り警戒
NO_DIRECTION=方向感なし
CHOPPY=乱高下
OVERHEATED=過熱
REVERSAL_WATCH=反転警戒
NO_NEW_ENTRY=新規回避
DATA_MISSING=情報不足
STALE_INPUT=鮮度不足
SIGNAL_CONFLICT=シグナル割れ
POST_SPIKE=急変直後
THIN_BOOK=薄板
WIDE_SPREAD=spread広い
```

## Detail payload v1

Long text must not be placed inside the card body. It belongs in a click detail / dialog / popover.

```text
detail_sections=概要,読み方,判定理由,情報源,注意点,鮮度詳細,改善用メモ
```

Minimum detail payload fields:

```text
horizon
regime_code
regime_label
confidence_percent
background_tone
freshness_badge
evidence_quality
short_tag
summary
reading
reason_lines
source_lines
warning_lines
freshness_detail
unknown_or_low_confidence_diagnostic_id
```

## Improvement record for UNKNOWN and low confidence

The UI card does not need to display all diagnostic information, but the system must keep enough structured evidence for later analysis and improvement.

```text
market_regime_diagnostic_record_required=true
unknown_improvement_record_required=true
low_confidence_improvement_record_required=true
```

Diagnostic record fields:

```text
record_id
created_at_utc
horizon
regime_code
confidence_percent
is_unknown
is_low_confidence
unknown_reason_codes
low_confidence_reason_codes
used_sources
missing_sources
conflicting_sources
freshness_state
spread_state
liquidity_state
board_state
executions_state
rule_version
model_version
feature_bundle_hash
input_snapshot_ref
notes
```

UNKNOWN / low-confidence reason codes v1:

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

These reason codes support future improvements, audits, and model/rule tuning without forcing long text into the visual card.

## Reuse boundary

Q26W defines the generic ideas needed for reuse, but it does not implement other prediction types yet.

```text
card_spec_reusable_for_future_prediction_cards=true
implemented_now=market_regime_spec_only
not_implemented_now=direction_prediction_card,volatility_card,liquidity_card,execution_flow_card,shock_risk_card
```

Future cards should reuse the same primitives where possible:

```text
CardSpec
PalettePolicy
FreshnessBadgePolicy
EvidenceQualityPolicy
DetailPayload
DiagnosticRecord
```

## Safety boundary

This slice is specification-only. It does not change production UI code, runtime code, collectors, producers, schedulers, prediction artifacts, status artifacts, view artifacts, AutoTrade, broker access, ledgers, modes, or parameters.
