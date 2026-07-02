# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29M_WARROOM_V2_DETAIL_OVERLAY_CLICK_POLISH_2026-07-02.md
# desc: PS-Q29M WarRoom v2 detail overlay click polish policy.

# PS-Q29M WarRoom v2 detail overlay click polish

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29L_WARROOM_V2_COMPONENT_VIEWPORT_TUNE_DONE
Slice: PS-Q29M_WARROOM_V2_DETAIL_OVERLAY_CLICK_POLISH

## Decision

Move card detail overlay HTML/CSS out of `prediction_cards.py` into a dedicated helper and polish the click detail overlay.

```text
detail_disclosure_mode=card_overlay
summary_button_label=詳細
aria_labels_present=true
overlay_max_height_px=230
prediction_cards_line_budget_preserved=true
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
