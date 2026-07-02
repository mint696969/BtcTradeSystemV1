# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29F_WARROOM_V2_HORIZON_MATRIX_CONTRACT_2026-07-02.md
# desc: PS-Q29F WarRoom v2 horizon matrix card contract aligned with Q26W/Q27E card specs.

# PS-Q29F WarRoom v2 horizon matrix contract

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29E_WARROOM_V2_DETAIL_BALLOON_PLACEHOLDER_DONE
Slice: PS-Q29F_WARROOM_V2_HORIZON_MATRIX_CONTRACT

## Decision

Align WarRoom v2 placeholder cards with the canonical Q26W/Q27E card specification.

WarRoom v2 prediction cards are not a simple item grid. They are a matrix:

```text
horizontal axis = horizons: 現在,5分後,15分後,30分後,60分後,6時間後,12時間後,24時間後
vertical axis = prediction items: 地合い, 方向感, 反転候補, ボラ警戒, ...
cell = horizontal rectangle card with three body lines and detail overlay
```

The implementation remains placeholder-only and display-only.

## Preserved canonical card spec

```text
card_row_layout=horizontal_time_axis_cards
cards_do_not_shrink=true
horizontal_scroll_required=true
wide_window_goal=show_through_24h_when_space_allows
narrow_window_goal=show_visible_range_and_scroll_do_not_squeeze
card_shape=horizontal_rectangle
card_body_three_lines=true
freshness_badge=top_right_badge_only
freshness_encoded_by_badge_only=true
border_meaning=evidence_quality
detail_disclosure_mode=card_overlay
```

## Non-goals

```text
not_connecting_dhot=true
not_invoking_classifier=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_touching_autotrade_broker_ledger_mode_parameter=true
not_changing_app_route=true
not_changing_legacy_warroom=true
```
