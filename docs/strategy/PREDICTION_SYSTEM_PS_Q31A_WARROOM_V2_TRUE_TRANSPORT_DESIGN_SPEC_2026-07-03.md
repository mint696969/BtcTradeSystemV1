# path: ./docs/strategy/PREDICTION_SYSTEM_PS_Q31A_WARROOM_V2_TRUE_TRANSPORT_DESIGN_SPEC_2026-07-03.md
# desc: PS-Q31A WarRoom v2 true transport design/spec for low-latency independent widget updates.

# PS-Q31A WarRoom v2 true transport design/spec

Date: 2026-07-03
Profile: BtcTradeSystem
Base gate: PS_Q30G_WARROOM_V2_DISABLED_TRANSPORT_ADAPTER_DONE
Slice: PS-Q31A_WARROOM_V2_TRUE_TRANSPORT_DESIGN_SPEC

## Decision

PS-Q31A defines the WarRoom v2 true transport architecture before any WebSocket/SSE implementation.
The operator goal is manual daytrade support: WarRoom v2 should become a low-latency information board where the human watches market, chart, prediction, and safety information while making manual decisions. Each information area should be able to update independently so one slow or noisy widget does not force a full-page reload or delay other widgets.

```text
true_transport_design_spec_only=true
manual_daytrade_support=true
low_latency_information_board=true
independent_widget_updates=true
operator_decision_human_only=true
transport_enabled_default=false
websocket_enabled=false
sse_enabled=false
push_connected=false
runtime_connected=false
read_only=true
display_only=true
would_send_to_broker=false
not_adding_ui_decoration=true
not_touching_autotrade_broker_ledger_mode_parameter=true
```

## Current foundation

The current Q30C-Q30G foundation is accepted and must remain the input to this design.

```text
transport_owner=external_read_model_event_bridge
ui_role=read_model_event_consumer_only
event_unit=widget_topic
patch_unit=widget_dom_region
broad_page_reload_required=false
q30g_payload_contract=disabled_outbound_transport_payload_adapter
q30g_message_unit=widget_update_event_envelope
current_ui_refresh=streamlit_fragment_polling
metrics_default_refresh=market_snapshot_strip
chart_refresh_opt_in_available=true
```

Current contract stack:

```text
D-hot read-only panel builders
-> panel event bridge
-> read-model event bridge
-> local event queue
-> disabled outbound payload adapter
-> future true transport
```

## Product requirement: manual trading information board

WarRoom v2 is not an execution system. It is a manual trading decision-support surface.
Design priorities:

```text
1. low perceived latency for high-value market facts
2. independent widget update cadence by topic
3. no broad page reload for routine updates
4. visible data freshness in existing widgets without new decoration in this slice
5. deterministic event ordering per widget topic
6. safe stale/missing data behavior
7. human-only decision and execution boundary
```

Manual daytrade update tiers:

```text
market_snapshot_strip:
  role: high-frequency trade reference
  preferred_update_class: fastest_safe
  stale_policy: show latest read model with freshness/staleness fields
chart_review_panel:
  role: review/calibration/GPT consultation
  preferred_update_class: opt_in_or_medium_frequency
  stale_policy: avoid noisy redraw by default; update only when opted in or explicitly requested
prediction_cards:
  role: slower prediction/support context
  preferred_update_class: evidence_change_or_moderate_frequency
  stale_policy: preserve last known read model and expose generated_at/fingerprint through existing payloads
safety/current_state/alerts:
  role: critical operator context
  preferred_update_class: high_priority_when_changed
  stale_policy: never hide missing or stale state behind neutral-looking values
```

## Transport ownership and process boundaries

True transport must not move source ownership into Streamlit widgets.

```text
producer_owner=external_read_model_event_bridge
ui_owner=read_model_event_consumer_only
streamlit_page_owns_transport_source=false
widget_owns_artifact_scanning=false
widget_owns_classifier_invocation=false
widget_owns_runtime_execution=false
widget_owns_broker_or_order_path=false
transport_process_reads_dhot=false_for_q31a
transport_process_writes_runtime_artifact=false_for_q31a
```

Q31A defines a future owner boundary, not a running process. A later slice may add a disabled simulator or skeleton, but this slice must remain doc/spec plus guard only.

## Responsibility-separated future folder layout

Future implementation slices must keep true transport responsibilities split by folder and module. Do not place transport lifecycle, schema, replay, gate, and UI rendering in one file.
Target layout for later Q31 slices:

```text
btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/
  topics.py                       # existing topic catalog
  transport_ownership.py          # existing ownership contract
  read_model_event_bridge.py      # existing read-model event envelope builder
  local_event_queue.py            # existing bounded event state
  disabled_transport_adapter.py   # existing Q30G outbound payload contract
  transport/
    __init__.py
    schema.py                     # message schema and validation helpers only
    topic_policy.py               # cadence, priority, freshness, stale policy
    consumer_state.py             # sequence/fingerprint/dedup state only
    replay.py                     # reconnect cursor, replay, backfill helpers only
    simulator.py                  # disabled in-process simulator only; no socket
    gates.py                      # promotion gates and feature flags only
    skeleton.py                   # disabled producer/consumer lifecycle skeleton only
```

UI files under `panels/warroom_v2/` remain renderers and panel packet builders. They must not own transport source scanning, socket lifecycle, replay state, classifier invocation, or execution behavior.

```text
responsibility_separation_required=true
future_transport_folder=btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/transport
one_module_one_responsibility=true
schema_module_no_socket=true
topic_policy_module_no_ui=true
consumer_state_module_no_streamlit=true
replay_module_no_broker_runtime_classifier=true
simulator_module_disabled_by_default=true
gates_module_required_before_transport_enabled=true
ui_renderer_must_not_own_transport_lifecycle=true
```

## Anti-bloat policy for future implementation

Q31 implementation must stay small-slice and split before files become hard to review.

```text
no_monolithic_transport_file=true
no_one_file_bloat=true
prefer_small_modules=true
max_future_transport_module_lines=220
max_renderer_module_lines=120
split_required_when_responsibilities_mix=true
split_required_before_file_becomes_hard_to_review=true
```

If a later implementation needs more than one responsibility, create another focused module and a focused guard rather than growing a large catch-all file.

## Topic model

The transport unit is a widget topic. The UI patch unit remains the widget DOM region.
Primary topics for true transport planning:

```text
warroom.market.snapshot -> widget_id=market_snapshot_strip
warroom.chart.review -> widget_id=chart_review_panel
warroom.current_state -> widget_id=current_state_mini_bar
warroom.alerts -> widget_id=operator_alert_summary
warroom.safety -> widget_id=safety_boundary_summary
warroom.prediction.market_regime -> widget_id=prediction_card.market_regime
warroom.prediction.trend_bias -> widget_id=prediction_card.trend_bias
warroom.prediction.reversal_zone -> widget_id=prediction_card.reversal_zone
warroom.prediction.volatility_risk -> widget_id=prediction_card.volatility_risk
warroom.prediction.scenario_ja -> widget_id=scenario_text_ja
```

Each topic may have its own cadence, dedup state, replay cursor, and freshness policy. A change in one topic must not require re-rendering unrelated widgets.

## Message schema

Future true transport messages must be compatible with the Q30G outbound payload contract.
Required message envelope fields:

```text
message_type=warroom_v2_widget_update
payload_kind=widget_update_event_envelope
adapter_version=prediction_warroom.v2.disabled_transport_adapter.ps_q30g.v1 compatible
transport_kind=websocket_or_sse_after_explicit_gate
topic=<widget topic>
widget_id=<widget dom region id>
sequence=<monotonic per topic sequence>
generated_at=<source read model timestamp>
previous_fingerprint=<previous stable payload fingerprint>
current_fingerprint=<current stable payload fingerprint>
changed=<boolean>
ui_patch_unit=widget_dom_region
broad_page_reload_required=false
read_only=true
display_only=true
would_send_to_broker=false
```

Payload rule:

```text
payload=envelope.event.read_model.payload
json_payload=stable JSON representation of the event envelope
fingerprint_algorithm=sha256_json_sort_keys_24
source_kind=external_read_model_event_bridge_or_disabled_simulator
```

No message is allowed to contain broker order requests, execution commands, parameter application commands, ledger append requests, or mode changes.

## Sequence, fingerprint, dedup, and ordering

The stream must be safe under duplicate delivery, reconnect, and partial widget refresh.

```text
sequence_scope=per_topic
sequence_rule=monotonic_non_decreasing_per_topic
fingerprint_scope=widget_id
dedup_rule=drop_if_current_fingerprint_matches_latest_widget_fingerprint
ordering_rule=apply_only_if_sequence_is_newer_or_equal_with_changed_fingerprint
replay_cursor=last_applied_sequence_per_topic
idempotent_patch_required=true
```

If a lower sequence arrives after a newer event, the consumer should ignore it unless it is explicitly marked as a replay snapshot for initialization and the widget has no current state.

## Reconnect, replay, and backfill

Future true transport needs deterministic recovery behavior.

```text
client_tracks=topic,last_sequence,last_fingerprint,last_received_at
server_or_bridge_replay_input=topic,last_sequence
replay_response=bounded_recent_events_or_latest_snapshot
replay_bound_default=32
initial_connect_behavior=send_latest_snapshot_per_subscribed_topic
reconnect_behavior=request_events_after_last_sequence_then_latest_snapshot_if_gap
large_gap_behavior=send_latest_snapshot_and_gap_marker
```

A reconnect must not trigger broker, order, ledger, runtime, classifier, or parameter behavior.

## WebSocket/SSE strategy

Q31A does not choose an implementation by enabling it. It defines the gate.
Staged strategy:

```text
stage_1_q31a=formal_design_spec_only
stage_2_q31b=disabled_in_process_transport_simulator_contract
stage_3_q31c=disabled_producer_consumer_skeleton_behind_flags
stage_4_q31d=operator_reviewed_local_only_dev_transport_enablement
stage_5_later=real_websocket_or_sse_after_gate
```

Decision guide:

```text
WebSocket:
  strength: bidirectional control and lower interactive latency
  risk: larger server/client lifecycle surface
  allowed_only_after: explicit gate, disabled skeleton guards, reconnect/dedup guards
SSE:
  strength: simpler server-to-browser event stream for read-only updates
  risk: less flexible bidirectional control
  allowed_only_after: explicit gate, disabled skeleton guards, reconnect/dedup guards
Current preference:
  begin with read-only server-to-client event semantics;
  keep the schema transport-neutral so WebSocket and SSE can share message payloads.
```

## Streamlit fragment refresh coexistence and retirement

Current Streamlit fragment refresh remains the accepted fallback until true transport is proven.

```text
streamlit_fragment_refresh_remains_active=true
metrics_default_refresh=market_snapshot_strip
chart_review_refresh=operator_opt_in
true_transport_parallel_shadow_required_before_retirement=true
fragment_refresh_retirement_gate=operator_accepts_true_transport_stability
page_reload_enabled=false
browser_timer_reload_enabled=false
```

Transition rule:

```text
1. keep fragment refresh as fallback
2. add disabled simulator/skeleton without sending messages
3. run shadow comparison between fragment read model and transport event payload
4. enable local-only transport behind explicit reviewed gate
5. retire fragment target only after stability and operator acceptance
```

## Transport promotion gate

No code may set `transport_enabled=true`, `websocket_enabled=true`, `sse_enabled=true`, or `push_connected=true` until all gate items are satisfied and reviewed.

```text
transport_enabled_promotion_gate_required=true
operator_review_required=true
disabled_simulator_guard_passed_required=true
producer_consumer_skeleton_guard_passed_required=true
message_schema_guard_passed_required=true
dedup_reconnect_replay_guard_passed_required=true
no_broker_runtime_classifier_guard_passed_required=true
fragment_fallback_preserved_required=true
```

## Non-goals for Q31A

```text
not_enabling_websocket=true
not_enabling_sse=true
not_opening_socket=true
not_sending_messages=true
not_starting_server=true
not_starting_client=true
not_writing_runtime_artifact=true
not_invoking_classifier=true
not_connecting_autotrade=true
not_connecting_broker=true
not_creating_order=true
not_appending_ledger=true
not_applying_mode=true
not_applying_parameter=true
not_adding_ui_decoration=true
```

## Acceptance criteria

```text
- PS-Q31A design/spec doc exists.
- The doc states manual daytrade support and low-latency independent widget updates as the product goal.
- The doc preserves Q30G disabled transport boundaries.
- The doc defines message schema using Q30G outbound payload shape.
- The doc defines sequence/fingerprint/dedup/reconnect/replay behavior.
- The doc defines Streamlit fragment refresh coexistence and retirement gate.
- The doc defines explicit promotion gates before transport_enabled=true.
- No WebSocket/SSE/socket/runtime/broker/classifier implementation is added in this slice.
```

## Next slice boundary

```text
PS-Q31B: disabled in-process transport simulator contract, transport_enabled=false.
PS-Q31C: disabled producer/consumer skeleton behind flags, no socket open by default.
PS-Q31D: explicit operator-reviewed gate for local-only dev transport enablement.
```
