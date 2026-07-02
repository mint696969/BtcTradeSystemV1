# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29L_WARROOM_V2_COMPONENT_VIEWPORT_TUNE_2026-07-02.md
# desc: PS-Q29L WarRoom v2 component viewport tune policy.

# PS-Q29L WarRoom v2 component viewport tune

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29K_WARROOM_V2_MATRIX_RAW_HTML_RENDER_FIX_DONE
Slice: PS-Q29L_WARROOM_V2_COMPONENT_VIEWPORT_TUNE

## Problem

After Q29K fixed raw HTML rendering, the prediction matrix rendered correctly but the components iframe showed an internal vertical scrollbar.

## Decision

Let the page own vertical scrolling and keep horizontal scrolling inside each horizon row.

```text
streamlit_components_html_used=true
component_scrolling_enabled=false
page_scroll_owns_vertical_flow=true
internal_vertical_scroll_avoided=true
row_horizontal_scroll_preserved=true
cards_do_not_shrink=true
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
