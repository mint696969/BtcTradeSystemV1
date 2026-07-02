# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29P_WARROOM_V2_ROW_LEVEL_DETAIL_OVERLAY_2026-07-02.md
# desc: PS-Q29P WarRoom v2 row-level detail overlay policy.

# PS-Q29P WarRoom v2 row-level detail overlay

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29O_WARROOM_V2_PLACEHOLDER_UI_SIGNOFF_DONE
Slice: PS-Q29P_WARROOM_V2_ROW_LEVEL_DETAIL_OVERLAY

## Decision

`詳細` is not a card-internal expansion. It is a readability-first overlay panel for the prediction item row.

```text
detail_disclosure_mode=row_level_overlay_panel
card_width_constrained=false
close_button_required=true
outside_click_close_enabled=true
backdrop_close_layer=true
layout_pushdown_avoided=true
bottom_row_visibility_guard=true
matrix_bottom_padding_px=96
row_horizontal_scroll_preserved=true
readability_first=true
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
