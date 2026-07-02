# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29J_WARROOM_V2_TOP_BAR_PLACEHOLDER_STATUS_POLISH_2026-07-02.md
# desc: PS-Q29J WarRoom v2 top-bar placeholder status polish policy.

# PS-Q29J WarRoom v2 top-bar placeholder status polish

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29I_WARROOM_V2_MATRIX_PLACEHOLDER_VISUAL_SEMANTICS_DONE
Slice: PS-Q29J_WARROOM_V2_TOP_BAR_PLACEHOLDER_STATUS_POLISH

## Decision

Make the WarRoom v2 top bar readable as placeholder status widgets.

The top zone remains display-only:

```text
top_widgets=現在状態,安全境界,アラート
status_source=placeholder_read_model
status_badge=NO_DATA
runtime_connected=false
push_connected=false
scenario_and_matrix_unchanged=true
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
