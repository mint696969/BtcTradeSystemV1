# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29C_WARROOM_V2_PAGE_SHELL_MOUNT_2026-07-02.md
# desc: PS-Q29C WarRoom v2 separate page shell mount policy.

# PS-Q29C WarRoom v2 page shell mount

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29B_WARROOM_V2_SHELL_PREVIEW_CONTRACT_DONE
Slice: PS-Q29C_WARROOM_V2_PAGE_SHELL_MOUNT

## Decision

Mount WarRoom v2 as a separate Operator UI route while keeping the current WarRoom as Legacy/reference.

The new page is intentionally thin. It renders the existing shell preview packet through a dedicated panel and does not own D-hot scanning, classifier invocation, cache invalidation, WebSocket/SSE handling, or any execution behavior.

## Added boundary

```text
views/warroom_v2_page.py
  thin Streamlit page shell only

prediction_warroom/panels/warroom_v2_shell_preview_panel.py
  display renderer for shell preview packet

app.py
  adds separate sidebar route: warroom_v2 / WarRoom v2
```

## Non-goals

```text
not_removing_legacy_warroom=true
not_rewriting_legacy_warroom=true
not_connecting_dhot=true
not_invoking_classifier=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_touching_autotrade_broker_ledger_mode_parameter=true
```
