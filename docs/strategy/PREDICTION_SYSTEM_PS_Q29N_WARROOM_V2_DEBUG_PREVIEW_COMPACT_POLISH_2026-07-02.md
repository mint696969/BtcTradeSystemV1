# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29N_WARROOM_V2_DEBUG_PREVIEW_COMPACT_POLISH_2026-07-02.md
# desc: PS-Q29N WarRoom v2 debug preview compact polish policy.

# PS-Q29N WarRoom v2 debug preview compact polish

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29M_WARROOM_V2_DETAIL_OVERLAY_CLICK_POLISH_DONE
Slice: PS-Q29N_WARROOM_V2_DEBUG_PREVIEW_COMPACT_POLISH

## Decision

Make the WarRoom v2 debug preview compact and explicit about placeholder/display-only state.

```text
compact_debug_preview=true
expanded_by_default=false
display_only=true
placeholder_only=true
model_count_visible=true
zone_counts_visible=true
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
