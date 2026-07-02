# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29G_WARROOM_V2_MATRIX_VISUAL_SCROLL_POLISH_2026-07-02.md
# desc: PS-Q29G WarRoom v2 matrix visual scroll polish policy.

# PS-Q29G WarRoom v2 matrix visual scroll polish

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29F_WARROOM_V2_HORIZON_MATRIX_CONTRACT_DONE
Slice: PS-Q29G_WARROOM_V2_MATRIX_VISUAL_SCROLL_POLISH

## Decision

Render the WarRoom v2 placeholder matrix with HTML/CSS instead of Streamlit columns so Q26W/Q27E card invariants are respected.

The matrix remains placeholder-only:

```text
row_axis=prediction_item
column_axis=horizon
horizontal_scroll_required=true
cards_do_not_shrink=true
card_width_px=208
card_shape=horizontal_rectangle
card_body_three_lines=true
freshness_badge=top_right_badge_only
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
not_changing_warroom_v2_page=true
not_changing_legacy_warroom=true
```
