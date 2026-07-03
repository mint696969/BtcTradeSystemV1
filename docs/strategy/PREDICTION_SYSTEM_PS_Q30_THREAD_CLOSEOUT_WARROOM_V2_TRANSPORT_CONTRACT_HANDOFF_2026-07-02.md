# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q30_THREAD_CLOSEOUT_WARROOM_V2_TRANSPORT_CONTRACT_HANDOFF_2026-07-02.md
# desc: WarRoom v2 Q30C-Q30G transport contract closeout and next-thread handoff.

# PS-Q30 WarRoom v2 transport contract closeout and next-thread handoff

Updated: 2026-07-03T01:32:30Z
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync
Base handoff head before closeout doc commit: c4360c7b
Current gate before next thread: PS_Q30G_WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_DONE
Next planned slice: PS-Q31A_WARROOM_V2_TRUE_TRANSPORT_DESIGN_SPEC

## Human intent

The operator wants to continue without drifting and complete the WarRoom v2 natural widget update path. The next work must start from the current contract stack and move into true transport design/spec first, not direct socket implementation.

## Current accepted behavior

WarRoom v2 currently has natural-feeling auto update through Streamlit fragment refresh. Market Snapshot updates naturally, and Chart Review can be explicitly opted in for refresh. This is accepted as current UI behavior, but it is not true WebSocket/SSE push.

```text
current_ui_refresh=streamlit_fragment_polling
metrics_default_refresh=market_snapshot_strip
chart_refresh_opt_in_available=true
page_reload_enabled=false
browser_timer_reload_enabled=false
push_connected=false
websocket_enabled=false
sse_enabled=false
runtime_connected=false
would_send_to_broker=false
```

## Completed contract stack

```text
PS-Q30C commit=2e5c4d25 Define WarRoom v2 transport ownership
- transport_owner=external_read_model_event_bridge
- ui_role=read_model_event_consumer_only
- event_unit=widget_topic
- patch_unit=widget_dom_region
- topics include warroom.market.snapshot and warroom.chart.review

PS-Q30D commit=ff03a555 Add WarRoom v2 read-model event bridge
- prebuilt read-model payload -> stable fingerprint -> WidgetUpdateEvent -> transport envelope
- no D-hot read, no socket, no runtime write, no classifier, no broker

PS-Q30E commit=3440a02b Adapt WarRoom v2 panel packets to event bridge
- existing read-only panel packets -> event payloads -> Q30D bridge packet
- shell preview packet carries read_model_event_bridge contract data
- no UI decoration added

PS-Q30F commit=2d13450b Add WarRoom v2 local event queue contract
- changed event extraction
- bounded local event queue/state holder
- latest fingerprint state by widget_id
- disabled/pure state helper only

PS-Q30G commit=c4360c7b Add WarRoom v2 disabled transport adapter
- local queue event -> outbound message payload contract
- future WebSocket/SSE compatible shape
- no socket open, no send, no D-hot read, no runtime write
```

## Canonical files for next GPT to read first

```text
tmp/gpt_room/08_STATUS.md
tmp/gpt_room/10_DECISIONS.md
tmp/gpt_room/NEXT_THREAD_PS_Q31_WARROOM_V2_TRUE_TRANSPORT_DESIGN_START_HERE.md

docs/strategy/PREDICTION_SYSTEM_PS_Q30_THREAD_CLOSEOUT_WARROOM_V2_TRANSPORT_CONTRACT_HANDOFF_2026-07-02.md
docs/strategy/PREDICTION_SYSTEM_PS_Q30C_WARROOM_V2_TRANSPORT_OWNERSHIP_2026-07-02.md
docs/strategy/PREDICTION_SYSTEM_PS_Q30D_WARROOM_V2_READ_MODEL_EVENT_BRIDGE_2026-07-02.md
docs/strategy/PREDICTION_SYSTEM_PS_Q30E_WARROOM_V2_PANEL_EVENT_BRIDGE_2026-07-02.md
docs/strategy/PREDICTION_SYSTEM_PS_Q30F_WARROOM_V2_LOCAL_EVENT_QUEUE_2026-07-02.md
docs/strategy/PREDICTION_SYSTEM_PS_Q30G_WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_2026-07-02.md

btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport_ownership.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/read_model_event_bridge.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/local_event_queue.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/disabled_transport_adapter.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/panel_event_bridge.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/fragment_refresh.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/auto_refresh_control.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py
```

## Next thread start instruction

```text
Start from PS_Q30G_WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_DONE.
Use project_bootstrap first.
Read tmp/gpt_room/08_STATUS.md, tmp/gpt_room/10_DECISIONS.md, and tmp/gpt_room/NEXT_THREAD_PS_Q31_WARROOM_V2_TRUE_TRANSPORT_DESIGN_START_HERE.md.
Then begin PS-Q31A WarRoom v2 true transport design/spec for natural widget updates.
Do not enable WebSocket/SSE yet.
Do not add UI decoration unless explicitly requested.
Keep AutoTrade, broker, order, ledger, mode, and parameter disconnected.
```

## PS-Q31A recommended boundary

Do:

```text
- define true transport architecture/spec
- decide producer/bridge/consumer responsibility boundaries
- define WebSocket vs SSE decision gate, or staged support plan
- define message schema using Q30G outbound payload contract
- define sequence/fingerprint/dedup/reconnect/replay behavior
- define Streamlit fragment refresh coexistence and retirement gate
- define transport_enabled=false default and promotion gate to true
- define focused guards before any socket is enabled
```

Do not:

```text
- open a socket
- start WebSocket/SSE server/client
- add UI status decoration
- connect runtime execution
- invoke classifier
- call AutoTrade, broker, order, ledger, mode, or parameter paths
- write runtime/prediction/status artifacts from WarRoom v2 transport contracts
```

## Non-negotiable safety invariants

```text
transport_enabled_default=false
websocket_enabled=false until explicit implementation gate
sse_enabled=false until explicit implementation gate
page_reload_required=false
ui_role=read_model_event_consumer_only
transport_owner=external_read_model_event_bridge
patch_unit=widget_dom_region
read_only=true
display_only=true
runtime_connected=false
push_connected=false
would_send_to_broker=false
classifier_invoked=false
autotrade_allowed=false
broker_allowed=false
ledger_append=false
mode_apply=false
parameter_apply=false
```

## Suggested next implementation sequence

```text
PS-Q31A: formal true transport design/spec only, no runtime behavior.
PS-Q31B: disabled in-process transport simulator contract with transport_enabled=false.
PS-Q31C: disabled producer/consumer skeleton behind flags, no socket open by default.
PS-Q31D: operator-reviewed gate for enabling local-only transport in dev, still no broker/runtime.
```

## Guard posture

Continue the existing close guard style. At minimum, include Q30G-Q30C plus Q29/Q30 refresh tests when changing transport-adjacent code.

```text
focused guard for next slice: new Q31A spec/contract test if code is added
close guard baseline: Q30G, Q30F, Q30E, Q30D, Q30C, Q30A, Q29Z, Q29Y, Q29X, Q29W, Q29V, Q29U, Q29T, Q29S, Q29R, Q29Q, Q29P, Q29O
py_compile target: changed v2/panel modules only
```
