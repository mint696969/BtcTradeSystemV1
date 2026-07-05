# path: ./docs/strategy/PREDICTION_SYSTEM_WARROOM_V2_RT_WIDGET_IMPLEMENTATION_SPEC_2026-07-05.md
# desc: WarRoom v2 realtime widget implementation specification and thread handoff.

# WarRoom v2 realtime widget implementation specification

Date: 2026-07-05
Profile: BtcTradeSystem
Branch: docs/phase2-handoff-sync
Reference HEAD at handoff: 036cad77
Gate: PS-WARROOM_V2_RT_SECTION_FRAGMENTS_DONE

## 1. Current achievement

WarRoom v2 has reached the intended live observation shape:

```text
Collector bitFlyer WebSocket push
  -> D-hot unified market state
  -> WarRoom D-hot read-only source
  -> RT live receiver bridge
  -> receive-only router
  -> per-widget state store
  -> render packets
  -> section-fragment refreshed cockpit lanes
```

Observed result:

```text
page_reload_enabled=false
transport=streamlit_section_fragment_refresh
display_source=live
fallback_sample_suppressed=true
rt_section_fragment_refresh_ready=true
websocket_send_enabled=false
broker_send_enabled=false
order_intent_submitted=false
prediction_invoked=false
classifier_invoked=false
```

Important precision: WarRoom v2 does not directly subscribe to bitFlyer WebSocket by default. The Collector owns the external WebSocket. WarRoom reads Collector's D-hot output and renders it with section fragments.

## 2. Runtime ownership and safety boundary

### Collector responsibilities

- Opens and maintains external market WebSocket subscriptions.
- Writes current market state under `D:\btc_ts_hot\state`.
- Updates `state/collector_vnext/unified_market_state_status.json`.

### WarRoom responsibilities

- Reads D-hot status/state read-only.
- Converts D-hot state into receive-only messages.
- Routes messages into per-widget state.
- Renders cockpit lanes.
- Never sends to broker, order layer, ledger, prediction engine, classifier, or external network from the UI path.

Required safety markers for any new widget lane:

```text
read_only=true
websocket_send_enabled=false
broker_send_enabled=false
order_intent_submitted=false
ledger_append_allowed=false
auto_trading_enabled=false
prediction_invoked=false
classifier_invoked=false
```

## 3. Core files

### Page orchestration

```text
btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py
```

This file must remain orchestration-only. It should:

- create `auto_refresh_packet`
- build cockpit snapshots
- mount section fragments
- delegate rendering to `rt_ui/*_view.py`

Avoid putting widget-specific business logic into this page file.

### Auto refresh metadata

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/auto_refresh_tick_view.py
```

Current transport:

```text
streamlit_section_fragment_refresh
```

This intentionally avoids browser reload. Do not reintroduce browser-level JavaScript page reloads, component-injected reload timers, or full-page auto-refresh for WarRoom v2 cockpit auto-update unless explicitly approved.

### D-hot live source and bridge

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/push_widgets/rt_live_receiver_bridge.py
```

Important behavior:

- default endpoint: `dhot://unified_market_state`
- default source: `dhot_unified_market_state_provider`
- D-hot source is synchronously read and drained in the same render cycle
- per-widget messages are routed receive-only

### UI lane modules

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/market_strip_view.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/trade_strip_view.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/inference_guidance_view.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/prediction_cards_view.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/chart_view.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/copy_packet_view.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/debug_view.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/live_packets.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/status_view.py
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/top_widgets_view.py
```

Keep each module small and role-specific.

## 4. Widget implementation pattern

For a new realtime widget, use this pattern.

### Step A: Define topic and route

Add or reuse a `topic_key` such as:

```text
market.depth
market.spread
market.liquidity
receiver.lifecycle
warroom.summary
warroom.alerts
trade.orders
trade.position
trade.pnl_after_fill
scenario.guidance
```

Route it in the receive-only router / registry path. The topic must map to one widget id. The route must stay receive-only.

### Step B: Produce or adapt a D-hot read-only message

Message shape:

```python
{
    "topic_key": "market.depth",
    "value": {...},
    "received_at_ms": int,
    "sequence": int,
    "receive_only": True,
}
```

Do not pass raw secrets, endpoints, tokens, or callable values into render packets.

### Step C: Update per-widget state store

The store should keep:

- latest snapshot
- sequence
- last update timestamp
- health/freshness
- bounded buffer

Buffers must remain bounded. Raw payload retention should stay disabled unless explicitly approved.

### Step D: Build render packet

Each widget lane should expose a compact render packet. Render packets should contain only values needed by the UI and GPT review copy packet.

### Step E: Add an `rt_ui` view module

Preferred shape:

```python
def build_<lane>_packet(source_packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "packet_kind": "warroom_v2_rt_<lane>_packet",
        "read_only": True,
        "broker_send_enabled": False,
        "order_intent_submitted": False,
        "prediction_invoked": False,
        "classifier_invoked": False,
    }


def render_<lane>(packet: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    ...
    return {"ok": True, "read_only": True}
```

Do not import Streamlit in the lane modules unless already accepted for that module family. Prefer `st_api` injection.

### Step F: Mount as a section fragment

In `warroom_v2_page.py`, mount through `_render_section_fragment(...)`. Keep static headings outside the dynamic body if possible.

Example:

```python
st.subheader("N. New lane")
_render_section_fragment(
    "new_lane",
    auto_refresh_packet,
    lambda snapshot: render_new_lane(snapshot["new_lane_packet"], st),
)
```

## 5. Current cockpit lane order

The intended lane order is:

```text
1. Market strip
2. Trade strip / orders, position, PnL
3. Inference scenario guidance
4. Prediction cards / important context
5. Bottom chart / realtime context
```

Design intent:

- The top must become a manual-trade cockpit that can be read without scrolling.
- Trade strip is reserved for current orders, position, and after-fill PnL, but remains read-only.
- Scenario guidance is observational only, not prophecy and not an order signal.
- Prediction cards are important context cards, not direct execution triggers.
- Bottom chart is mainly for visual review and GPT copy-packet analysis.

## 6. Auto-refresh behavior

Current setting source:

```text
ui_auto_refresh=true
ui_refresh_interval=3
```

Expected runtime markers:

```text
cockpit_auto_refresh=on
interval_ms=3000
transport=streamlit_section_fragment_refresh
page_reload_enabled=false
```

Expected observation:

- No full page browser reload.
- No forced scroll-to-top jump.
- Numeric values update naturally in visible sections.
- `Drained` / `Applied` counts continue to update.

Latency model:

```text
Collector WebSocket receive -> D-hot write: normally near-immediate
WarRoom D-hot read/apply: milliseconds to tens of milliseconds
Visible UI update: bounded mainly by fragment interval
```

With 3-second interval:

```text
average visual lag ~= 1.5s + Collector/D-hot write time
maximum visual lag ~= 3s + Collector/D-hot write time
```

## 7. GPT review copy packet

The GPT review copy packet is built in:

```text
rt_ui/copy_packet_view.py
```

Current schema marker:

```text
warroom_gpt_review_packet.v1
```

It should stay compact and safe:

- market snapshot
- scenario guidance
- recent chart rows
- prediction cards
- safety markers

Large historical analysis should use D-hot data tools / bounded slices rather than dumping large UI text.

## 8. Current known gaps

Known gaps to address after thread handoff:

```text
market.trades remains not_started in current D-hot WarRoom source
trade strip is reserved but not yet connected to read-only order/position/PnL state
prediction cards are still context cards, not real prediction-engine outputs
scenario guidance is heuristic/observational only
chart history is still shallow; useful GPT review needs range/window selection later
section fragment refresh works, but section-specific cadences may be refined
```

Recommended next small slices:

```text
WR-Next1: Market strip polish and cockpit density
WR-Next2: Bottom chart history/window/copy packet improvements
WR-Next3: Read-only trade strip source connection
WR-Next4: Prediction scenario card refinement
WR-Next5: Section-specific refresh cadence
```

## 9. Thread handoff summary

Start next thread from this state:

```text
branch=docs/phase2-handoff-sync
head=036cad77
status=clean
latest accepted gate=PS-WARROOM_V2_RT_SECTION_FRAGMENTS_DONE
operational mode=WarRoom v2 realtime cockpit observation
refresh transport=streamlit_section_fragment_refresh
source=dhot://unified_market_state
source_owner=Collector
WarRoom role=read-only observation UI
```

Do not regress to:

```text
browser page reload auto refresh
WarRoom direct bitFlyer WebSocket default source
sample fallback displayed as live
large monolithic warroom_v2_page.py business logic
broker/order/prediction/classifier invocation from UI render path
```
