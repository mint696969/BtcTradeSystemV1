# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29K_WARROOM_V2_MATRIX_RAW_HTML_RENDER_FIX_2026-07-02.md
# desc: PS-Q29K WarRoom v2 matrix raw HTML render fix policy.

# PS-Q29K WarRoom v2 matrix raw HTML render fix

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29J_WARROOM_V2_TOP_BAR_PLACEHOLDER_STATUS_POLISH_DONE
Slice: PS-Q29K_WARROOM_V2_MATRIX_RAW_HTML_RENDER_FIX

## Problem

The operator UI showed raw HTML fragments such as `<div class='wv2-card ...'>` inside the WarRoom v2 prediction matrix.

## Decision

Render the WarRoom v2 prediction matrix with `streamlit.components.v1.html()` instead of Markdown unsafe HTML, and generate card HTML without leading Markdown-code indentation.

```text
streamlit_components_html_used=true
markdown_unsafe_html_used=false
raw_html_visible_guard=true
cards_do_not_shrink=true
horizontal_scroll_required=true
visual_semantics_from_payload=true
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
