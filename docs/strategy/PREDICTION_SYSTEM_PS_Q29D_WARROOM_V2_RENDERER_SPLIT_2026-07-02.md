# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q29D_WARROOM_V2_RENDERER_SPLIT_2026-07-02.md
# desc: PS-Q29D WarRoom v2 renderer responsibility split policy.

# PS-Q29D WarRoom v2 renderer split

Date: 2026-07-02
Profile: BtcTradeSystem
Base gate: PS_Q29C_WARROOM_V2_PAGE_SHELL_MOUNT_DONE
Slice: PS-Q29D_WARROOM_V2_RENDERER_SPLIT

## Decision

Split the WarRoom v2 shell-preview panel into small responsibility-specific renderer modules before adding richer card detail, scenario, or future push behavior.

The existing `warroom_v2_shell_preview_panel.py` remains as a thin orchestrator. It delegates top bar, prediction cards, Japanese scenario area, debug preview, and zone selection to small modules under `prediction_warroom/panels/warroom_v2/`.

## Added boundary

```text
prediction_warroom/panels/warroom_v2/model_views.py
  zone selection helpers only

prediction_warroom/panels/warroom_v2/top_bar.py
  top mini-bar renderer only

prediction_warroom/panels/warroom_v2/prediction_cards.py
  prediction card grid renderer only

prediction_warroom/panels/warroom_v2/scenario_area.py
  Japanese scenario area renderer only

prediction_warroom/panels/warroom_v2/debug_preview.py
  collapsed debug preview renderer only
```

## Non-goals

```text
not_changing_app_route=true
not_changing_warroom_v2_page_route=true
not_changing_legacy_warroom=true
not_connecting_dhot=true
not_invoking_classifier=true
not_enabling_websocket=true
not_enabling_sse=true
not_enabling_scheduler_or_producer=true
not_touching_autotrade_broker_ledger_mode_parameter=true
```
