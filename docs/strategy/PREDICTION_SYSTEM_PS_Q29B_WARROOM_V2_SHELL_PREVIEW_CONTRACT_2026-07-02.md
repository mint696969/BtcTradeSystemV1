# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29B_WARROOM_V2_SHELL_PREVIEW_CONTRACT_2026-07-02.md
# desc: PS-Q29B WarRoom v2 shell preview contract policy.

# PS-Q29B WarRoom v2 shell preview contract

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29A_WARROOM_V2_PUSH_READY_WIDGET_READ_MODEL_CONTRACT_DONE
Slice: PS-Q29B_WARROOM_V2_SHELL_PREVIEW_CONTRACT

## Decision

Add a WarRoom v2 shell preview contract before mounting any new page or transport.

This slice intentionally does not change `app.py` or `views/warroom_page.py`. The current WarRoom stays Legacy/reference. WarRoom v2 remains a contract-only preview with placeholder read models.

## Added boundary

```text
prediction_warroom/v2/placeholder_read_models.py
  placeholder WidgetReadModel packets for every planned widget

prediction_warroom/v2/shell_preview.py
  complete shell preview packet combining layout, topics, zones, and placeholders
```

## Non-goals

```text
not_mounting_warroom_v2_page=true
not_adding_sidebar_route=true
not_changing_legacy_warroom=true
not_connecting_dhot=true
not_connecting_classifier=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_touching_autotrade_broker_ledger_mode_parameter=true
```

## Acceptance criteria

```text
- shell preview packet contains top / prediction_cards / scenario zones
- placeholder read models exist for every planned widget
- prediction card placeholders expose detail availability
- Japanese scenario placeholder remains below prediction cards
- app.py and warroom_page.py are not changed or imported by v2 shell
- all v2 files remain small and side-effect free
```
