# path: ./docs/strategy/WARROOM_V2_WEBSOCKET_PUSH_WIDGET_AUTO_UPDATE_SPEC_2026-07-03.md
# desc: WarRoom v2 WebSocket push widget auto-update technical specification for adding new widgets/items safely and consistently.

# WarRoom v2 WebSocket push widget auto-update specification

Date: 2026-07-03
Profile: BtcTradeSystem
Scope: WarRoom v2 widgets, topics, read models, push payloads, receiver-only WebSocket client, lightweight receiver state, Streamlit fragment rendering, and future custom component islands.
Current base head: b1ab1819
Current state: PS_Q33I_WARROOM_V2_WEBSOCKET_RECEIVER_ONLY_CLIENT_LIGHTWEIGHT_STATE_TARGET_WRITE_PREVIEW_DEFAULT_OFF_NO_SOCKET_DONE

## Purpose

This document defines how WarRoom v2 widgets/items must be added so that later GPTs can implement WebSocket push auto-update without broad page reload, without duplicated transport paths, and without accidentally invoking execution, broker, classifier, prediction generation, or unsafe state mutation.

The final product goal is:

```text
WarRoom widgets update independently from WebSocket push.
Each widget is addressed by topic and widget_id.
Only changed widget regions update.
Broad page reload is avoided by default.
Browser timer reload remains legacy fallback only.
The receiver is receive-only and never sends external messages.
```

## Canonical widget/topic model

WarRoom v2 uses topic-level widget update units. A widget must have a stable `widget_id`, a stable `topic`, a zone, an order, and a read-model builder.

Current layout widgets:

```text
current_state_mini_bar -> warroom.current_state -> zone=top
safety_mini_bar -> warroom.safety -> zone=top
alert_summary -> warroom.alerts -> zone=top
prediction_card_market_regime -> warroom.prediction.market_regime -> zone=prediction_cards
prediction_card_trend_bias -> warroom.prediction.trend_bias -> zone=prediction_cards
prediction_card_reversal_zone -> warroom.prediction.reversal_zone -> zone=prediction_cards
prediction_card_volatility_risk -> warroom.prediction.volatility_risk -> zone=prediction_cards
prediction_card_liquidity -> warroom.prediction.liquidity_execution_quality -> zone=prediction_cards
prediction_card_breakout_false_break -> warroom.prediction.breakout_false_break -> zone=prediction_cards
prediction_card_cross_venue -> warroom.prediction.cross_venue_confirmation -> zone=prediction_cards
prediction_card_human_technical -> warroom.prediction.human_technical_structure -> zone=prediction_cards
prediction_scenario_ja -> warroom.prediction.scenario_ja -> zone=scenario
```

Additional push/read-surface targets already present in the topic catalog or current focus:

```text
market_snapshot_strip -> warroom.market.snapshot
chart_review_panel -> warroom.chart.review
```

The topic catalog and layout policy are repository truth. Do not add an ad-hoc widget directly to the WarRoom page without first updating the topic/read-model contract path.

## Required planes

Every WebSocket-updated widget must pass through these planes. Do not skip layers.

```text
source/read-only builder
  -> widget read model
  -> widget update event
  -> transport envelope / WebSocket payload
  -> bounded server queue and replay cursor
  -> receiver-only WebSocket client
  -> bounded receive buffer
  -> lightweight receiver state
  -> session_state target write gate
  -> per-widget read model state
  -> Streamlit fragment render adapter
  -> optional future custom component island
```

### Data/source plane

Allowed:

```text
read-only source inspection
prebuilt payload conversion
existing artifact/read model snapshot consumption
freshness/staleness calculation
fingerprint calculation
```

Forbidden unless a separate explicit gate exists:

```text
prediction_generation_invoked=true
prediction_inference_invoked=true
classifier_invoked=true
runtime_artifact_write=true
prediction_artifact_write=true
broker_private_api_call=true
order_intent_submitted=true
ledger_append=true
mode_apply=true
parameter_apply=true
```

### Read model plane

Every widget read model must include:

```text
widget_id
topic
generated_at
payload
freshness
fingerprint
title
source_kind
read_model_consumer_only=true
future_push_compatible=true
```

The payload must be display-ready. The renderer should not scan D-hot, invoke classifier, compute predictions, or decide trading actions.

### Event plane

Every widget update event must include:

```text
event_id
topic
widget_id
sequence
generated_at
previous_fingerprint
current_fingerprint
changed
read_model
source_kind
```

The `changed` flag must be derived from fingerprint comparison. Rendering should prefer changed-only updates.

### Transport payload plane

Every WebSocket payload must be an envelope around a widget update event. Required payload fields:

```text
ok=true
message_type=widget_update
topic
widget_id
sequence
generated_at
event_id
current_fingerprint
read_model
payload_kind=warroom_v2_widget_update
receiver_only=true
send_required=false
broker_send_enabled=false
prediction_generation_invoked=false
classifier_invoked=false
```

Invalid or unknown topics must be dropped with reason. They must not crash the receiver and must not trigger page reload.

### Server/publisher plane

The server/publisher must be default-off and bounded.

```text
publisher_enabled_default=false
operator_ack_required=true
bounded_queue=true
replay_cursor_required=true
max_replay_events_required=true
dropped_count_tracked=true
invalid_topic_dropped=true
```

The server may publish widget update events. It must not receive commands from the browser that cause execution or broker actions.

### Receiver client plane

The WarRoom receiver client is receive-only.

```text
receiver_only=true
client_sends_messages=false
external_message_send_enabled=false
subscribe_send_disabled_until_explicit_gate=true
socket_opened_only_after_operator_gate=true
bounded_receive_buffer=true
reconnect_policy_bounded=true
replay_cursor_bounded=true
```

If a future WebSocket library requires a protocol-level subscribe message, that must be handled in a separate explicit gate. Do not silently add client sends.

### Lightweight receiver state plane

The receiver state should be small, bounded, and session_state friendly.

Recommended shape:

```text
{
  "state_kind": "warroom_v2_receiver_lightweight_state",
  "updated_at": "...",
  "connection": {
    "transport_state": "connected|disconnected|stale|error",
    "last_message_at": "...",
    "received_message_count": 0,
    "dropped_count": 0,
    "reconnect_count": 0
  },
  "topics": {
    "warroom.market.snapshot": {
      "sequence": 0,
      "generated_at": "...",
      "fingerprint": "...",
      "read_model": {}
    }
  },
  "widgets": {
    "market_snapshot_strip": {
      "topic": "warroom.market.snapshot",
      "sequence": 0,
      "fingerprint": "...",
      "freshness": "live|warm|stale|missing",
      "read_model": {}
    }
  }
}
```

State must be bounded. Do not store unbounded message history in `st.session_state`.

### Session_state write plane

The target session_state write path must remain gated and explicit.

```text
target_session_state_key must be stable and scoped
target write preview before actual write
target write gate before actual write
operator ack before actual write
readback and rollback after actual write
```

Do not write directly from receiver code into arbitrary session_state keys. Write only through the approved lightweight receiver state target key and only after the corresponding gate is complete.

### Render plane

Render must be per-widget or per-fragment, not broad page reload.

```text
broad_page_reload_required=false
browser_timer_reload=legacy_fallback_only
changed_widget_only=true
fragment_render_first=true
custom_component_island_optional_later=true
```

The renderer consumes read models from session_state/lightweight receiver state. It must not own transport, artifact scanning, classifier invocation, or prediction generation.

## Adding a new WarRoom widget/item

When adding a new widget or item, follow this checklist in order.

### 1. Topic and widget identity

Add or confirm:

```text
widget_id: stable snake_case id
topic: stable warroom.* topic
zone: top | prediction_cards | scenario | bottom_chart | debug_collapsed
order: deterministic integer
default_visible: true|false
```

Update the topic catalog and layout policy. Do not add a visible widget without a topic.

### 2. Topic policy

Add policy fields:

```text
surface
update_class
priority
cadence_hint_ms
stale_policy
broad_page_reload_required=false
prediction_generation_invoked=false
classifier_invoked=false
websocket_enabled default false until runtime gate
```

### 3. Read model builder

Create a pure read model builder. It must:

```text
accept prebuilt/read-only payloads
return WidgetReadModel-shaped dict
include freshness and fingerprint
be unit-testable without Streamlit
not read D-hot from WarRoom page
not invoke classifier
not generate predictions
not write artifacts
not send broker orders
```

### 4. Event bridge helper

Create a helper to produce widget update events with sequence and fingerprint. Reuse stable fingerprint logic.

```text
previous_fingerprint + current_fingerprint -> changed
changed=false means no widget repaint needed
```

### 5. Transport payload mapping

Add payload schema coverage and validation. Unknown or invalid fields must fail closed.

```text
known topic required
known widget_id required
sequence int required
generated_at required
payload bounded
read_model bounded
```

### 6. Receiver state mapping

Map topic to widget state:

```text
topics[topic] = latest topic packet
widgets[widget_id] = latest widget read model
```

Do not overwrite unrelated widget state. Do not clear stale widgets unless the stale policy says to mark stale explicitly.

### 7. Fragment/render adapter

Add renderer/fragment adapter only after the read model and state path exist.

Renderer rules:

```text
consume read model only
show freshness/staleness explicitly
show dropped/invalid status where relevant
avoid background color as freshness-only signal
never trigger broker/order/classifier/prediction generation
```

### 8. Tests

Minimum focused tests for each widget/topic addition:

```text
contract_has_widget_id_topic_zone_order
read_model_builder_pure_and_bounded
event_bridge_changed_only_fingerprint
transport_payload_validation_known_topic
renderer_or_fragment_does_not_start_transport_or_invoke_forbidden_paths
```

Close guard should include the current Q33/Q34/Q35/Q36/Q37 chain and existing WarRoom v2 transport ownership tests.

### 9. Docs and handoff

Each slice must add or update:

```text
docs/strategy/PREDICTION_SYSTEM_PS_*.md
tmp/gpt_room/08_STATUS.md
tmp/gpt_room/10_DECISIONS.md
tmp/gpt_room/09_FOCUS.json
tmp/gpt_room/11_STATE.json
```

For major boundary changes, add a closeout/handoff doc before crossing into mutation or runtime.

## Widget rollout order

Do not enable all widgets at once. Recommended rollout:

```text
1. market_snapshot_strip
2. current_state_mini_bar / safety_mini_bar / alert_summary
3. chart_review_panel
4. prediction cards row
5. prediction_scenario_ja
6. all-widget changed-only update closeout
```

Rationale:

```text
market snapshot proves high-frequency push and freshness handling
current/safety/alerts prove top-line operator readability
chart proves medium-frequency optional redraw
prediction cards prove multi-card row update without broad reload
scenario proves larger text payload handling
```

## Future task sequence

Recommended task sequence from the current handoff:

```text
Q33J: target write hidden diagnostic record, no actual target write
Q33K: actual target write gate, no actual write
Q33L: first actual target session_state write, still no socket
Q33M: readback/reset/rollback closeout for state-plane
Q34A: widget source map and read-model ownership spec
Q34B: top widgets read model builders
Q34C: market snapshot and chart review read model builders
Q34D: prediction card read model builders
Q34E: scenario_ja read model builder
Q34F: all-widget event bridge and changed-only fingerprint guard
Q34G: read-model closeout/handoff
Q35A: WebSocket widget update payload schema
Q35B: bounded publisher queue
Q35C: replay cursor and reconnect contract
Q35D: local WebSocket server gate default-off
Q35E: local WebSocket server smoke, no execution
Q35F: producer/server handoff
Q36A: actual receiver client start gate
Q36B: receiver-only WebSocket client implementation
Q36C: actual bounded receive buffer integration
Q36D: topic validation and drop reasons
Q36E: reconnect/replay cursor handling
Q36F: receiver status diagnostics
Q36G: receiver client closeout/handoff
Q37A: market_snapshot_strip auto-update
Q37B: chart_review_panel auto-update
Q37C: top widgets auto-update
Q37D: prediction cards auto-update
Q37E: scenario_ja auto-update
Q37F: all-widget changed-only fragment update contract
Q37G: all-widget fragment handoff
Q38A: end-to-end smoke for market snapshot
Q38B: chart and top widgets smoke
Q38C: prediction cards and scenario smoke
Q38D: reconnect/stale/drop smoke
Q38E: final all-widget WebSocket auto-update handoff
```

## Final acceptance criteria

WarRoom v2 WebSocket widget auto-update is complete only when all of these are true:

```text
websocket_enabled=true behind explicit operator/runtime gate
receiver_only=true
client_started=true behind explicit gate
socket_opened=true behind explicit gate
client_sends_messages=false
external_message_send_enabled=false
broker_send_enabled=false
would_send_to_broker=false
all_registered_topics_validated=true
unknown_topics_dropped_with_reason=true
bounded_receive_buffer=true
bounded_replay=true
lightweight_receiver_state_written=true behind explicit target write gate
all_widget_read_models_present=true
all_widget_fingerprints_present=true
changed_only_update=true
broad_page_reload_required=false
browser_timer_reload=legacy_fallback_only
market_snapshot_strip_updates_from_push=true
current_state_mini_bar_updates_from_push=true
safety_mini_bar_updates_from_push=true
alert_summary_updates_from_push=true
chart_review_panel_updates_from_push=true
prediction_cards_update_from_push=true
prediction_scenario_ja_updates_from_push=true
stale_state_shown_explicitly=true
dropped_count_visible_or_diagnostic=true
prediction_generation_invoked=false
prediction_inference_invoked=false
classifier_invoked=false
order_intent_submitted=false
ledger_append_allowed=false
mode_apply_allowed=false
parameter_apply_allowed=false
```

## Non-negotiable rule

Adding a new item to WarRoom means adding it to the widget/topic/read-model/update-event path first. Do not bolt it directly onto the page as a special-case Streamlit block if it is expected to auto-update from WebSocket push.
