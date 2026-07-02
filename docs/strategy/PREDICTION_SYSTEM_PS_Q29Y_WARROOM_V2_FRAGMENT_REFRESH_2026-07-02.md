# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29Y_WARROOM_V2_FRAGMENT_REFRESH_2026-07-02.md
# desc: PS-Q29Y WarRoom v2 fragment refresh without whole-page reload.

# PS-Q29Y WarRoom v2 fragment refresh

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29X_WARROOM_V2_AUTO_REFRESH_OBSERVABILITY_DONE
Slice: PS-Q29Y_WARROOM_V2_FRAGMENT_REFRESH

## Decision

Q29Y replaces WarRoom v2 effective auto-refresh behavior with Streamlit fragment polling for the live read-only sections.

```text
streamlit_fragment_refresh=true
effective_transport_kind=streamlit_fragment_polling
fragment_targets=market_snapshot_strip,chart_review_panel
page_reload_enabled=false
browser_timer_reload_enabled=false
read_only=true
display_only=true
runtime_connected=false
push_connected=false
websocket_enabled=false
sse_enabled=false
would_send_to_broker=false
```

## Boundary

This is not true WebSocket/SSE push. It avoids whole-page reload and reruns only the target Streamlit fragments when the sidebar auto-refresh setting is ON.

## Non-goals

```text
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_invoking_classifier=true
not_touching_autotrade_broker_ledger_mode_parameter=true
would_send_to_broker=false
```
